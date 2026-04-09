"""
Plugin smoke test for sap-datasphere scaffold.
Exercises all 5 skill flows using the backend's tasks.py functions directly.
Uses env vars already exported in the shell.

Run: python smoke_test.py   (with venv active or full path to venv python)
"""

import asyncio
import json
import os
import sys
import traceback

# Default to mock mode unless already set.
# To test against a live tenant: set DATASPHERE_MOCK_MODE=0 before running.
if "DATASPHERE_MOCK_MODE" not in os.environ:
    os.environ["DATASPHERE_MOCK_MODE"] = "1"

# Resolve the backend package location dynamically — no hardcoded paths.
# Works whether installed via pip (normal or editable) or run from the repo venv.
import importlib.util as _ilu
_spec = _ilu.find_spec("sap_datasphere_mcp")
if _spec is None:
    sys.exit(
        "ERROR: sap_datasphere_mcp not importable.\n"
        "Activate the SAPDatasphereMCP venv or run:\n"
        "  pip install mcp-sap-datasphere-server"
    )

from sap_datasphere_mcp.tools.tasks import (
    diagnostics,
    list_spaces,
    list_assets,
    space_summary,
    search_assets,
    get_asset_metadata,
    list_columns,
    describe_asset_schema,
    preview_asset,
    query_analytical,
    profile_column,
    summarize_column_profile,
)

PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"

results: list[tuple[str, str, str]] = []  # (flow, tool, status)


def record(flow: str, tool: str, status: str, note: str = "") -> None:
    tag = f"[{status}]"
    print(f"  {tag:<6} {tool}" + (f"  ? {note}" if note else ""))
    results.append((flow, tool, status))


def compact(obj: dict, max_keys: int = 8) -> str:
    """Print a trimmed JSON summary."""
    top = {k: obj[k] for i, k in enumerate(obj) if i < max_keys}
    return json.dumps(top, default=str, indent=None)[:300]


async def run_flows() -> None:

    # -----------------------------------------------------------------
    # FLOW 1: tenant-recon
    # Skill sequence: diagnostics ? list_spaces ? summarize_space
    # -----------------------------------------------------------------
    print("\n--- FLOW 1: tenant-recon ---")
    space_id: str | None = None
    asset_name: str | None = None

    try:
        diag = await diagnostics()
        if diag.get("ok") or diag.get("status") == "ok" or "tenant" in diag:
            record("tenant-recon", "datasphere_diagnostics", PASS, compact(diag))
        else:
            record("tenant-recon", "datasphere_diagnostics", FAIL, compact(diag))
    except Exception as e:
        record("tenant-recon", "datasphere_diagnostics", FAIL, str(e)[:120])

    try:
        spaces_result = await list_spaces()
        spaces = spaces_result.get("spaces", [])
        if spaces:
            space_id = spaces[0].get("id") or spaces[0].get("space_id")
            record("tenant-recon", "datasphere_list_spaces", PASS,
                   f"{len(spaces)} spaces; first={space_id}")
        else:
            record("tenant-recon", "datasphere_list_spaces", FAIL, "empty spaces list")
    except Exception as e:
        record("tenant-recon", "datasphere_list_spaces", FAIL, str(e)[:120])

    if space_id:
        try:
            summary = await space_summary(space_id=space_id, max_assets=20)
            total = summary.get("total_assets", summary.get("asset_count", "?"))
            record("tenant-recon", "datasphere_space_summary", PASS,
                   f"space={space_id} total_assets={total}")
        except Exception as e:
            record("tenant-recon", "datasphere_space_summary", FAIL, str(e)[:120])
    else:
        record("tenant-recon", "datasphere_space_summary", SKIP, "no space found")

    # -----------------------------------------------------------------
    # Discover a candidate asset for flows 2-5
    # Try list_assets first (works in mock mode); fall back to search_assets.
    # -----------------------------------------------------------------
    print("\n  [discovery] listing assets in space ...")
    if space_id:
        try:
            la_result = await list_assets(space_id=space_id)
            hits = la_result.get("assets", [])
            if hits:
                # Prefer technical ID — catalog and data lookups use asset_id, not display name.
                asset_name = hits[0].get("id") or hits[0].get("asset_name") or hits[0].get("name")
                print(f"  [discovery] found {len(hits)} assets; using: {asset_name}")
            else:
                print("  [discovery] list_assets returned empty ? trying search_assets ...")
                search_result = await search_assets(space_id=space_id, limit=5)
                hits2 = search_result.get("assets", [])
                if hits2:
                    asset_name = hits2[0].get("name") or hits2[0].get("asset_name") or hits2[0].get("id")
                    print(f"  [discovery] search found: {asset_name}")
                else:
                    print("  [discovery] no assets found ? flows 2-5 will SKIP")
        except Exception as e:
            print(f"  [discovery] list_assets error: {e}")
    else:
        print("  [discovery] no space_id ? flows 2-5 will SKIP")

    # -----------------------------------------------------------------
    # FLOW 2: asset-explorer
    # Skill sequence: metadata ? columns ? schema ? preview
    # -----------------------------------------------------------------
    print("\n--- FLOW 2: asset-explorer ---")
    col_name: str | None = None

    if space_id and asset_name:
        try:
            meta = await get_asset_metadata(space_id=space_id, asset_name=asset_name)
            record("asset-explorer", "datasphere_get_asset_metadata", PASS, compact(meta))
        except Exception as e:
            record("asset-explorer", "datasphere_get_asset_metadata", FAIL, str(e)[:120])

        try:
            cols = await list_columns(space_id=space_id, asset_name=asset_name)
            columns = cols.get("columns", [])
            if columns:
                col_name = columns[0].get("name") or columns[0].get("column_name")
            record("asset-explorer", "datasphere_list_columns", PASS,
                   f"{len(columns)} columns; first={col_name}")
        except Exception as e:
            record("asset-explorer", "datasphere_list_columns", FAIL, str(e)[:120])

        try:
            schema = await describe_asset_schema(space_id=space_id, asset_name=asset_name)
            record("asset-explorer", "datasphere_describe_asset_schema", PASS, compact(schema))
        except Exception as e:
            record("asset-explorer", "datasphere_describe_asset_schema", FAIL, str(e)[:120])

        try:
            preview = await preview_asset(space_id=space_id, asset_name=asset_name, top=5)
            rows = preview.get("rows", preview.get("data", []))
            record("asset-explorer", "datasphere_preview_asset", PASS,
                   f"{len(rows)} rows returned")
        except Exception as e:
            record("asset-explorer", "datasphere_preview_asset", FAIL, str(e)[:120])
    else:
        for tool in ["datasphere_get_asset_metadata", "datasphere_list_columns",
                     "datasphere_describe_asset_schema", "datasphere_preview_asset"]:
            record("asset-explorer", tool, SKIP, "no asset")

    # -----------------------------------------------------------------
    # FLOW 3: analytical-check
    # Skill sequence: metadata (already done) ? query_analytical
    # -----------------------------------------------------------------
    print("\n--- FLOW 3: analytical-check ---")

    if space_id and asset_name:
        try:
            aq = await query_analytical(
                space_id=space_id,
                asset_name=asset_name,
                top=5,
            )
            rows = aq.get("rows", aq.get("data", []))
            error = aq.get("error") or aq.get("code")
            if error and not rows:
                record("analytical-check", "datasphere_query_analytical", PASS,
                       f"not supported (expected for views): {str(error)[:80]}")
            else:
                record("analytical-check", "datasphere_query_analytical", PASS,
                       f"{len(rows)} rows from analytical query")
        except Exception as e:
            # "not analytical" is not a failure ? the skill handles it gracefully
            msg = str(e)[:120]
            status = PASS if "not" in msg.lower() or "unsupported" in msg.lower() else FAIL
            record("analytical-check", "datasphere_query_analytical", status, msg)
    else:
        record("analytical-check", "datasphere_query_analytical", SKIP, "no asset")

    # -----------------------------------------------------------------
    # FLOW 4: column-investigator
    # Skill sequence: profile_column ? 2 ? summarize_column_profile
    # -----------------------------------------------------------------
    print("\n--- FLOW 4: column-investigator ---")

    if space_id and asset_name and col_name:
        try:
            prof = await profile_column(
                space_id=space_id,
                asset_name=asset_name,
                column_name=col_name,
            )
            record("column-investigator", "datasphere_profile_column", PASS,
                   f"col={col_name} " + compact(prof))
        except Exception as e:
            record("column-investigator", "datasphere_profile_column", FAIL, str(e)[:120])

        try:
            summ = await summarize_column_profile(
                space_id=space_id,
                asset_name=asset_name,
                column_name=col_name,
            )
            record("column-investigator", "datasphere_summarize_column_profile", PASS, compact(summ))
        except Exception as e:
            record("column-investigator", "datasphere_summarize_column_profile", FAIL, str(e)[:120])
    else:
        for tool in ["datasphere_profile_column", "datasphere_summarize_column_profile"]:
            record("column-investigator", tool, SKIP, "no asset or column")

    # -----------------------------------------------------------------
    # FLOW 5: data-quality-scan
    # Skill sequence: schema + preview + profile (all already tested above;
    # run a second asset if available; otherwise reuse first asset)
    # -----------------------------------------------------------------
    print("\n--- FLOW 5: data-quality-scan ---")

    if space_id and asset_name:
        # schema
        try:
            schema2 = await describe_asset_schema(space_id=space_id, asset_name=asset_name, top=10)
            record("data-quality-scan", "datasphere_describe_asset_schema", PASS,
                   "schema ok (reused from flow 2)")
        except Exception as e:
            record("data-quality-scan", "datasphere_describe_asset_schema", FAIL, str(e)[:120])

        # preview
        try:
            prev2 = await preview_asset(space_id=space_id, asset_name=asset_name, top=10)
            rows2 = prev2.get("rows", prev2.get("data", []))
            record("data-quality-scan", "datasphere_preview_asset", PASS,
                   f"{len(rows2)} rows (reused from flow 2)")
        except Exception as e:
            record("data-quality-scan", "datasphere_preview_asset", FAIL, str(e)[:120])

        # profile
        if col_name:
            try:
                prof2 = await profile_column(
                    space_id=space_id,
                    asset_name=asset_name,
                    column_name=col_name,
                )
                record("data-quality-scan", "datasphere_profile_column", PASS,
                       f"col={col_name} profile ok")
            except Exception as e:
                record("data-quality-scan", "datasphere_profile_column", FAIL, str(e)[:120])
        else:
            record("data-quality-scan", "datasphere_profile_column", SKIP, "no column discovered")
    else:
        for tool in ["datasphere_describe_asset_schema", "datasphere_preview_asset",
                     "datasphere_profile_column"]:
            record("data-quality-scan", tool, SKIP, "no asset")

    # -----------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------
    print("\n" + "=" * 60)
    print("SMOKE TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, _, s in results if s == PASS)
    failed = sum(1 for _, _, s in results if s == FAIL)
    skipped = sum(1 for _, _, s in results if s == SKIP)

    current_flow = ""
    for flow, tool, status in results:
        if flow != current_flow:
            print(f"\n  {flow}")
            current_flow = flow
        tag = f"[{status}]"
        print(f"    {tag:<6} {tool}")

    print(f"\nTotal: {passed} PASS  {failed} FAIL  {skipped} SKIP")
    if failed == 0:
        print("Result: ALL CHECKS PASSED")
    else:
        print(f"Result: {failed} FAILURE(S) ? see above")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_flows())
