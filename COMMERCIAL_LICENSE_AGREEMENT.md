# Commercial License Agreement

**sethir-marketplace — Claude Code Plugin Marketplace**

**Version:** 1.0 | **Effective Template Date:** April 2026

---

> **IMPORTANT:** This document is a template agreement. To enter into a binding commercial
> license, both parties must complete the fields marked [LICENSEE: ...], sign below, and
> receive countersignature from the Licensor. An unsigned copy of this agreement confers
> no rights beyond those already granted by the Elastic License 2.0.

---

## Parties

**Licensor:**
Rahul Sethi
GitHub: https://github.com/rahulsethi
Contact: rahulsethi@github
("Licensor")

**Licensee:**
Company Name: [LICENSEE: Full legal entity name]
Address: [LICENSEE: Registered address]
Contact Name: [LICENSEE: Signatory name and title]
Contact Email: [LICENSEE: Email]
("Licensee")

---

## Recitals

WHEREAS, Licensor has developed the sethir-marketplace, a collection of Claude Code
plugins for SAP enterprise data platforms, including the sap-hana-cloud and
sap-datasphere plugins, together with associated skills, agents, hooks, workflows,
ontology pipelines, and documentation (collectively, the "Software");

WHEREAS, the Software is made publicly available under the Elastic License 2.0
("ELv2"), which restricts certain commercial uses including provision as a managed
or hosted service to third parties;

WHEREAS, Licensee wishes to use the Software in a manner that requires rights
beyond those granted by ELv2;

NOW THEREFORE, in consideration of the mutual covenants herein and the License
Fee paid or agreed to be paid by Licensee, the parties agree as follows:

---

## 1. Definitions

1.1 **"Software"** means the sethir-marketplace repository and all plugins contained
therein, including but not limited to sap-hana-cloud and sap-datasphere, together with
all skill files, agent definitions, hook scripts, workflow logic, example code, and
documentation, as made available at https://github.com/rahulsethi/claude_plugins and
any successor location.

1.2 **"Derivative Works"** means any work that is based on or derived from the Software,
including modifications, adaptations, translations, and works that incorporate the
Software in whole or in part.

1.3 **"Commercial Use"** means use of the Software in a production environment for
business purposes, including but not limited to provision as a service to end users,
embedding in commercial products, or redistribution to customers.

1.4 **"Managed Service"** means providing access to the Software's functionality to
third parties via a hosted platform, API, SaaS product, or any other mechanism where
end users consume the Software's features without receiving a direct copy.

1.5 **"License Type"** means the specific tier of commercial rights purchased by
Licensee, as set out in Section 3.

1.6 **"License Fee"** means the fee agreed between the parties for the License Type,
as set out in Schedule A.

---

## 2. Grant of Rights — Beyond ELv2

Subject to the terms of this Agreement and payment of the License Fee, Licensor
grants Licensee a non-exclusive, non-transferable (except as set out in Section 9.2),
worldwide license to use the Software under the License Type selected in Section 3,
in addition to the rights already granted by ELv2.

This Agreement does not supersede ELv2 for uses already permitted thereunder. It
supplements ELv2 by removing specific restrictions for Licensee's chosen License Type.

---

## 3. License Types

Select one License Type. The selected type determines the scope of rights granted
and the applicable License Fee in Schedule A.

### 3A. Enterprise Internal Use License

**Permitted:**
- Deploy and operate the Software across Licensee's entire organization, including
  all subsidiaries and affiliates under common control, without restriction on the
  number of users, environments, or seats.
- Modify the Software for Licensee's internal purposes without the obligation to
  open-source or publish modifications.
- Sub-distribute the Software internally to Licensee's employees and contractors
  working on Licensee's behalf.

**Not permitted under this tier:**
- Providing the Software or Derivative Works as a service to third parties outside
  Licensee's organization.
- Resale, sublicensing, or redistribution to customers or partners.
- White-labeling or OEM embedding in products sold to others.

Selected: [ ] YES / [ ] NO

### 3B. Managed Service / SaaS License

**Permitted:**
Everything in 3A, plus:
- Host and operate the Software (or Derivative Works based on it) as a managed
  service accessible to Licensee's customers, including as a SaaS product, API,
  or embedded analytical service.
- Offer the Software's capabilities to end users under Licensee's own brand,
  provided that Licensee's documentation attributes the underlying technology to
  sethir-marketplace by Rahul Sethi.

**Required:**
- Attribution statement in Licensee's product documentation and application "About"
  or "Legal" page: *"Powered by sethir-marketplace by Rahul Sethi
  (https://github.com/rahulsethi/claude_plugins), licensed under a commercial license."*

**Not permitted under this tier:**
- Sublicensing the Software to customers for their own redistribution.
- Removing or obscuring the required attribution statement.

Selected: [ ] YES / [ ] NO

### 3C. OEM / Embedding License

**Permitted:**
Everything in 3B, plus:
- Embed the Software or Derivative Works within Licensee's commercial software
  products for redistribution to Licensee's customers ("End Products").
- Distribute the Software as a component of End Products under Licensee's
  product name, without displaying the attribution required under 3B, subject
  to inclusion of attribution in the End Product's license documentation.

**Required:**
- Licensee must include the following notice in the End Product's license
  documentation or credits file: *"This product includes technology from
  sethir-marketplace by Rahul Sethi, licensed under a commercial license."*
- Licensee must not represent to customers that Licensee is the original author
  of the embedded technology.

Selected: [ ] YES / [ ] NO

---

## 4. Restrictions Applicable to All License Types

4.1 Licensee shall not sublicense, sell, rent, lease, transfer, or assign this
Agreement or any rights hereunder to any third party, except as expressly permitted
by the selected License Type or as set out in Section 9.2.

4.2 Licensee shall not remove, alter, or obscure any copyright notice, trademark
notice, or attribution notice appearing in the Software.

4.3 Licensee shall not use Licensor's name, trademark, or likeness to suggest
endorsement of Licensee's products or services without Licensor's prior written consent.

4.4 Licensee shall not use the Software to train, fine-tune, or create derivative
machine learning models for commercial redistribution without a separate written
agreement with Licensor.

4.5 Licensee acknowledges that the Software connects at runtime to third-party MCP
server packages (hana-mcp-server, mcp-sap-datasphere-server). Those packages are
independently licensed under MIT and are not covered by this Agreement. Licensee is
responsible for compliance with those packages' license terms.

---

## 5. Intellectual Property Ownership

5.1 The Software and all Derivative Works authored by Licensor remain the exclusive
property of Licensor. This Agreement transfers no ownership interest.

5.2 Licensee retains ownership of Derivative Works authored solely by Licensee,
subject to Licensor's underlying ownership of the original Software elements embedded
therein. Licensee's Derivative Works may not be distributed in a way that removes
obligations under this Agreement or ELv2 from third parties who receive them.

5.3 Licensor reserves all rights not expressly granted herein.

---

## 6. License Fee and Payment

6.1 Licensee shall pay the License Fee set out in Schedule A within 30 days of the
Effective Date of this Agreement or as otherwise specified in Schedule A.

6.2 All fees are non-refundable except as expressly stated in Schedule A.

6.3 Late payments shall accrue interest at 1.5% per month or the maximum rate
permitted by applicable law, whichever is lower.

6.4 License Fees may be renegotiated annually. Licensor will provide 60 days' written
notice of any fee change. Continued use following fee change notice constitutes
acceptance of the new fee schedule.

---

## 7. Warranties and Disclaimer

7.1 Licensor warrants that, to the best of Licensor's knowledge, Licensor has the
right to grant the licenses herein, and the Software does not knowingly infringe any
third-party intellectual property rights.

7.2 EXCEPT AS SET OUT IN SECTION 7.1, THE SOFTWARE IS PROVIDED "AS IS" WITHOUT
WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.

7.3 Licensor does not warrant that the Software will be error-free, uninterrupted,
or compatible with any specific third-party system, including SAP HANA, SAP
Datasphere, or Claude Code, which are independent products subject to change.

---

## 8. Limitation of Liability

8.1 IN NO EVENT SHALL LICENSOR BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING LOST PROFITS, BUSINESS INTERRUPTION,
OR LOSS OF DATA), ARISING OUT OF OR IN CONNECTION WITH THIS AGREEMENT, EVEN IF
LICENSOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

8.2 LICENSOR'S TOTAL CUMULATIVE LIABILITY ARISING OUT OF OR RELATED TO THIS
AGREEMENT SHALL NOT EXCEED THE LICENSE FEE PAID BY LICENSEE IN THE TWELVE MONTHS
PRECEDING THE CLAIM.

---

## 9. Term and Termination

9.1 **Term.** This Agreement begins on the Effective Date and continues for the initial
term set in Schedule A, unless earlier terminated.

9.2 **Renewal.** Unless either party provides written notice of non-renewal at least
30 days before the end of the then-current term, this Agreement renews automatically
for successive one-year terms.

9.3 **Termination for Cause.** Either party may terminate this Agreement immediately
upon written notice if the other party materially breaches this Agreement and fails
to cure such breach within 30 days after receiving written notice thereof.

9.4 **Effect of Termination.** Upon termination: (a) all licenses granted hereunder
terminate immediately; (b) Licensee shall cease all use of the Software under the
rights granted by this Agreement (ELv2 rights remain in effect for uses permitted
thereby); (c) Licensee shall destroy or return all copies of the Software that are
not permitted to be retained under ELv2.

9.5 **Survival.** Sections 4, 5, 7, 8, and 10 survive termination.

---

## 10. General Provisions

10.1 **Governing Law.** This Agreement is governed by the laws of [LICENSOR: specify
jurisdiction, e.g., England and Wales / State of Delaware / Republic of India] without
regard to conflict of law principles.

10.2 **Dispute Resolution.** The parties shall first attempt to resolve any dispute
through good-faith negotiation. If unresolved after 30 days, disputes shall be
submitted to binding arbitration under the rules of [LICENSOR: specify body].

10.3 **Entire Agreement.** This Agreement, together with Schedule A, constitutes
the entire agreement between the parties with respect to its subject matter and
supersedes all prior negotiations, representations, and understandings.

10.4 **Amendment.** No amendment to this Agreement is effective unless in writing
and signed by both parties.

10.5 **Waiver.** Failure to enforce any provision does not constitute a waiver of
future enforcement of that provision or any other provision.

10.6 **Severability.** If any provision of this Agreement is held unenforceable,
the remaining provisions continue in full force.

10.7 **Assignment.** Licensee may not assign this Agreement without Licensor's prior
written consent, except in connection with a merger, acquisition, or sale of all or
substantially all of Licensee's assets, provided the assignee agrees in writing to
be bound by all terms hereof.

---

## Schedule A — License Fee and Term

| Item | Value |
|------|-------|
| License Type | [LICENSEE: Select 3A / 3B / 3C] |
| Initial Term | [e.g., 12 months from Effective Date] |
| Annual License Fee | [LICENSOR/LICENSEE: Agreed fee in agreed currency] |
| Payment Schedule | [e.g., Upfront / Quarterly] |
| Effective Date | [Date both parties have signed] |
| Renewal | Automatic annual renewal unless terminated per Section 9.2 |

*Suggested fee guidance (adjust based on use case scope):*
- *3A Enterprise Internal: from £5,000 / $6,000 / €5,500 per year*
- *3B Managed Service / SaaS: from £15,000 / $18,000 / €16,000 per year*
- *3C OEM / Embedding: negotiated based on end-product reach and revenue share*

---

## Signatures

By signing below, each party represents that the signatory has authority to enter into
this Agreement on behalf of the named party.

**LICENSOR:**

Signature: ______________________________
Name: Rahul Sethi
Date: ______________________________

---

**LICENSEE:**

Signature: ______________________________
Name: [LICENSEE: Full name]
Title: [LICENSEE: Title]
Company: [LICENSEE: Legal entity name]
Date: ______________________________

---

*This document is a template. Consult a qualified solicitor or attorney before entering
into binding commitments. This template is provided for informational purposes and does
not constitute legal advice.*
