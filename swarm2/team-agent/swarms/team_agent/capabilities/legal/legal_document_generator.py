"""Legal Document Generator Capability.

This capability generates various legal documents including contracts,
NDAs, terms of service, privacy policies, and compliance documents.
"""

from typing import Dict, Any
from swarms.team_agent.capabilities.base_capability import BaseCapability


class LegalDocumentGenerator(BaseCapability):
    """Generate legal documents, contracts, and compliance materials."""

    def __init__(self):
        super().__init__()
        self.name = self.metadata.get("name")
        self.domains = self.metadata.get("domains", [])

    def get_metadata(self) -> Dict[str, Any]:
        """Return metadata for legal document generation capability."""
        return {
            "name": "legal_document_generator",
            "type": "document_generation",
            "domain": "legal",
            "domains": ["legal", "contracts", "compliance", "nda", "terms", "privacy"],
            "description": "Generate legal documents, contracts, NDAs, terms of service, and compliance materials",
            "version": "1.0.0",
            "specialty": "legal_documentation",
            "formats": ["markdown", "plaintext"],
        }

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate legal document based on mission context.

        Args:
            context: Dictionary containing:
                - mission: Description of the legal document needed
                - architecture: Optional architecture/structure guidance

        Returns:
            Dictionary containing:
                - content: Main generated content
                - artifacts: List of artifact dictionaries
                - metadata: Capability metadata
        """
        mission = context.get("mission", "")
        mission_lower = mission.lower()

        # Determine document type from mission keywords
        doc_type = self._determine_document_type(mission_lower)

        # Generate appropriate legal document
        if doc_type == "nda":
            content, artifacts = self._generate_nda(mission)
        elif doc_type == "contract":
            content, artifacts = self._generate_contract(mission)
        elif doc_type == "terms":
            content, artifacts = self._generate_terms_of_service(mission)
        elif doc_type == "privacy":
            content, artifacts = self._generate_privacy_policy(mission)
        elif doc_type == "compliance":
            content, artifacts = self._generate_compliance_document(mission)
        else:
            content, artifacts = self._generate_generic_legal_document(mission)

        return {
            "content": content,
            "artifacts": artifacts,
            "metadata": self.metadata,
        }

    def _determine_document_type(self, mission_lower: str) -> str:
        """Determine the type of legal document from mission text."""
        if any(keyword in mission_lower for keyword in ["nda", "non-disclosure", "confidentiality"]):
            return "nda"
        elif any(keyword in mission_lower for keyword in ["contract", "agreement", "service agreement"]):
            return "contract"
        elif any(keyword in mission_lower for keyword in ["terms of service", "tos", "terms and conditions"]):
            return "terms"
        elif any(keyword in mission_lower for keyword in ["privacy policy", "privacy", "data protection"]):
            return "privacy"
        elif any(keyword in mission_lower for keyword in ["compliance", "regulatory", "gdpr", "hipaa"]):
            return "compliance"
        else:
            return "generic"

    def _generate_nda(self, mission: str) -> tuple[str, list]:
        """Generate a Non-Disclosure Agreement."""
        content = f'''# Non-Disclosure Agreement (NDA)

**Mission Context:** {mission}

## 1. PARTIES

This Non-Disclosure Agreement ("Agreement") is entered into as of [DATE] by and between:

- **Disclosing Party:** [PARTY A NAME]
- **Receiving Party:** [PARTY B NAME]

## 2. DEFINITION OF CONFIDENTIAL INFORMATION

For purposes of this Agreement, "Confidential Information" shall include all information or material that has or could have commercial value or other utility in the business in which Disclosing Party is engaged.

## 3. OBLIGATIONS OF RECEIVING PARTY

Receiving Party agrees to:

a) Hold and maintain the Confidential Information in strict confidence
b) Not disclose the Confidential Information to third parties without prior written consent
c) Use the Confidential Information solely for the purpose of [PURPOSE]
d) Protect the Confidential Information using the same degree of care used to protect its own confidential information

## 4. EXCLUSIONS FROM CONFIDENTIAL INFORMATION

Confidential Information shall not include information that:

a) Was publicly known at the time of disclosure
b) Becomes publicly known through no breach of this Agreement
c) Was rightfully received by Receiving Party from a third party
d) Was independently developed by Receiving Party

## 5. TERM

This Agreement shall remain in effect for a period of [DURATION] from the Effective Date, unless earlier terminated by either party with [NOTICE_PERIOD] written notice.

## 6. RETURN OF MATERIALS

Upon termination or at Disclosing Party's request, Receiving Party shall promptly return or destroy all Confidential Information and certify such destruction in writing.

## 7. REMEDIES

Receiving Party acknowledges that breach of this Agreement may cause irreparable harm for which monetary damages may be inadequate. Disclosing Party shall be entitled to seek equitable relief, including injunction and specific performance.

## 8. GOVERNING LAW

This Agreement shall be governed by the laws of [JURISDICTION].

## 9. ENTIRE AGREEMENT

This Agreement constitutes the entire agreement between the parties concerning the subject matter hereof.

---

**DISCLOSING PARTY:**

Signature: _______________________
Name: [NAME]
Title: [TITLE]
Date: [DATE]

**RECEIVING PARTY:**

Signature: _______________________
Name: [NAME]
Title: [TITLE]
Date: [DATE]

---

*DISCLAIMER: This is a template for informational purposes only. Consult with a qualified attorney before use.*
'''

        artifacts = [
            {
                "type": "markdown",
                "name": "nda",
                "filename": "non_disclosure_agreement.md",
                "content": content,
                "summary": f"Non-Disclosure Agreement template for: {mission}"
            }
        ]

        return content, artifacts

    def _generate_contract(self, mission: str) -> tuple[str, list]:
        """Generate a service or business contract."""
        content = f'''# Service Agreement Contract

**Mission Context:** {mission}

## 1. PARTIES AND EFFECTIVE DATE

This Service Agreement ("Agreement") is made effective as of [EFFECTIVE_DATE] by and between:

- **Service Provider:** [PROVIDER_NAME]
- **Client:** [CLIENT_NAME]

## 2. SERVICES TO BE PROVIDED

Service Provider agrees to provide the following services ("Services"):

[DETAILED_DESCRIPTION_OF_SERVICES]

## 3. COMPENSATION

Client agrees to compensate Service Provider as follows:

- **Payment Amount:** [AMOUNT]
- **Payment Schedule:** [SCHEDULE]
- **Payment Method:** [METHOD]
- **Late Payment:** Interest of [RATE]% per month on overdue amounts

## 4. TERM AND TERMINATION

a) **Term:** This Agreement shall commence on [START_DATE] and continue for [DURATION]
b) **Termination for Cause:** Either party may terminate with [NOTICE] written notice if the other party materially breaches
c) **Termination for Convenience:** Either party may terminate with [NOTICE] written notice

## 5. DELIVERABLES AND TIMELINE

Service Provider shall deliver the following:

| Deliverable | Description | Due Date |
|------------|-------------|----------|
| [ITEM_1]   | [DESC_1]    | [DATE_1] |
| [ITEM_2]   | [DESC_2]    | [DATE_2] |

## 6. INTELLECTUAL PROPERTY RIGHTS

a) **Work Product:** All work product created under this Agreement shall be owned by [OWNER]
b) **Pre-Existing IP:** Each party retains ownership of their pre-existing intellectual property
c) **License Grant:** [LICENSING_TERMS]

## 7. CONFIDENTIALITY

Both parties agree to maintain confidentiality of proprietary information disclosed during the term of this Agreement.

## 8. WARRANTIES AND REPRESENTATIONS

Service Provider warrants that:
- Services will be performed in a professional and workmanlike manner
- Services will conform to industry standards
- Service Provider has the right and authority to enter into this Agreement

## 9. LIMITATION OF LIABILITY

In no event shall either party be liable for indirect, incidental, special, or consequential damages exceeding the total compensation paid under this Agreement.

## 10. INDEMNIFICATION

Each party agrees to indemnify and hold harmless the other party from claims, damages, and expenses arising from their negligence or breach of this Agreement.

## 11. DISPUTE RESOLUTION

a) **Negotiation:** Parties shall first attempt to resolve disputes through good faith negotiation
b) **Mediation:** If negotiation fails, disputes shall be submitted to mediation
c) **Arbitration/Litigation:** [ARBITRATION_OR_COURT_PROVISIONS]

## 12. GENERAL PROVISIONS

- **Governing Law:** [JURISDICTION]
- **Entire Agreement:** This Agreement constitutes the entire agreement between the parties
- **Amendments:** Amendments must be in writing and signed by both parties
- **Severability:** If any provision is invalid, the remainder shall remain in effect
- **Assignment:** Neither party may assign this Agreement without written consent

---

**SERVICE PROVIDER:**

Signature: _______________________
Name: [NAME]
Title: [TITLE]
Date: [DATE]

**CLIENT:**

Signature: _______________________
Name: [NAME]
Title: [TITLE]
Date: [DATE]

---

*DISCLAIMER: This is a template for informational purposes only. Consult with a qualified attorney before use.*
'''

        artifacts = [
            {
                "type": "markdown",
                "name": "service_contract",
                "filename": "service_agreement.md",
                "content": content,
                "summary": f"Service Agreement contract for: {mission}"
            }
        ]

        return content, artifacts

    def _generate_terms_of_service(self, mission: str) -> tuple[str, list]:
        """Generate Terms of Service document."""
        content = f'''# Terms of Service

**Mission Context:** {mission}

**Last Updated:** [DATE]

## 1. ACCEPTANCE OF TERMS

By accessing and using [SERVICE_NAME] ("Service"), you accept and agree to be bound by these Terms of Service ("Terms"). If you do not agree to these Terms, do not use the Service.

## 2. DESCRIPTION OF SERVICE

[SERVICE_NAME] provides [DESCRIPTION_OF_SERVICE].

## 3. USER ACCOUNTS

### 3.1 Account Creation
- You must provide accurate and complete information when creating an account
- You are responsible for maintaining the security of your account credentials
- You must be at least [AGE] years old to use this Service

### 3.2 Account Responsibilities
- You are responsible for all activities under your account
- You must notify us immediately of any unauthorized access
- We reserve the right to suspend or terminate accounts for violations

## 4. USER CONDUCT

You agree NOT to:
- Violate any applicable laws or regulations
- Infringe on intellectual property rights
- Transmit malicious code or malware
- Attempt to gain unauthorized access to the Service
- Harass, abuse, or harm other users
- Use the Service for any illegal or unauthorized purpose

## 5. INTELLECTUAL PROPERTY

### 5.1 Service Content
All content, features, and functionality are owned by [COMPANY_NAME] and protected by copyright, trademark, and other intellectual property laws.

### 5.2 User Content
- You retain ownership of content you submit
- By submitting content, you grant us a license to use, modify, and display such content
- You represent that you have the right to submit such content

## 6. PRIVACY

Your use of the Service is also governed by our Privacy Policy, available at [PRIVACY_POLICY_URL].

## 7. PAYMENT TERMS

### 7.1 Fees
- Certain features may require payment
- All fees are stated in [CURRENCY]
- Fees are non-refundable unless otherwise stated

### 7.2 Subscriptions
- Subscriptions automatically renew unless cancelled
- You may cancel your subscription at any time
- Cancellation takes effect at the end of the current billing period

## 8. DISCLAIMERS

THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO:
- Warranties of merchantability
- Fitness for a particular purpose
- Non-infringement
- Uninterrupted or error-free operation

## 9. LIMITATION OF LIABILITY

TO THE MAXIMUM EXTENT PERMITTED BY LAW, [COMPANY_NAME] SHALL NOT BE LIABLE FOR:
- Indirect, incidental, special, or consequential damages
- Loss of profits, data, or business opportunities
- Damages exceeding the amount paid by you in the past 12 months

## 10. INDEMNIFICATION

You agree to indemnify and hold harmless [COMPANY_NAME] from any claims, damages, losses, and expenses arising from:
- Your use of the Service
- Your violation of these Terms
- Your violation of any third-party rights

## 11. MODIFICATIONS TO SERVICE

We reserve the right to:
- Modify or discontinue the Service at any time
- Change these Terms with notice
- Continued use after changes constitutes acceptance

## 12. TERMINATION

We may terminate or suspend your access immediately for:
- Violation of these Terms
- Fraudulent or illegal activity
- At our sole discretion with or without cause

## 13. GOVERNING LAW AND DISPUTES

### 13.1 Governing Law
These Terms are governed by the laws of [JURISDICTION].

### 13.2 Dispute Resolution
- Disputes shall first be resolved through negotiation
- If unresolved, disputes shall be submitted to [ARBITRATION/COURT]

## 14. CONTACT INFORMATION

For questions about these Terms, contact us at:
- Email: [EMAIL]
- Address: [ADDRESS]
- Phone: [PHONE]

## 15. MISCELLANEOUS

- **Entire Agreement:** These Terms constitute the entire agreement
- **Severability:** Invalid provisions do not affect the remainder
- **Waiver:** Failure to enforce does not constitute a waiver
- **Assignment:** You may not assign these Terms without our consent

---

*DISCLAIMER: This is a template for informational purposes only. Consult with a qualified attorney before use.*
'''

        artifacts = [
            {
                "type": "markdown",
                "name": "terms_of_service",
                "filename": "terms_of_service.md",
                "content": content,
                "summary": f"Terms of Service document for: {mission}"
            }
        ]

        return content, artifacts

    def _generate_privacy_policy(self, mission: str) -> tuple[str, list]:
        """Generate Privacy Policy document."""
        content = f'''# Privacy Policy

**Mission Context:** {mission}

**Effective Date:** [DATE]

## 1. INTRODUCTION

[COMPANY_NAME] ("we," "us," or "our") respects your privacy and is committed to protecting your personal data. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our service [SERVICE_NAME].

## 2. INFORMATION WE COLLECT

### 2.1 Information You Provide
- **Account Information:** Name, email address, username, password
- **Profile Information:** Profile photo, bio, preferences
- **Payment Information:** Billing address, payment card details (processed by third-party payment processors)
- **Communications:** Messages, support tickets, feedback

### 2.2 Automatically Collected Information
- **Device Information:** IP address, browser type, operating system
- **Usage Data:** Pages visited, features used, time spent
- **Cookies and Tracking:** See our Cookie Policy
- **Location Data:** Approximate location based on IP address

### 2.3 Information from Third Parties
- Social media platforms (if you connect your account)
- Authentication services
- Analytics providers

## 3. HOW WE USE YOUR INFORMATION

We use collected information to:
- Provide, operate, and maintain our Service
- Process transactions and send transaction notifications
- Respond to your comments and questions
- Send administrative information and updates
- Improve and personalize user experience
- Monitor usage and analyze trends
- Detect and prevent fraud and abuse
- Comply with legal obligations

## 4. LEGAL BASIS FOR PROCESSING (GDPR)

We process personal data based on:
- **Consent:** You have given consent for specific purposes
- **Contract:** Processing is necessary to perform a contract with you
- **Legal Obligation:** Processing is required by law
- **Legitimate Interests:** Processing is in our legitimate business interests

## 5. SHARING YOUR INFORMATION

We may share your information with:

### 5.1 Service Providers
Third-party vendors who perform services on our behalf:
- Cloud hosting providers
- Payment processors
- Analytics services
- Customer support tools

### 5.2 Business Transfers
In connection with mergers, acquisitions, or asset sales

### 5.3 Legal Requirements
When required by law, court order, or governmental request

### 5.4 With Your Consent
When you explicitly authorize sharing

We do NOT sell your personal information to third parties.

## 6. DATA RETENTION

We retain your personal information for as long as:
- Your account is active
- Necessary to provide services
- Required by law or for legitimate business purposes

After retention period, we securely delete or anonymize your data.

## 7. YOUR PRIVACY RIGHTS

Depending on your location, you may have the following rights:

### 7.1 General Rights
- **Access:** Request copies of your personal data
- **Correction:** Request correction of inaccurate data
- **Deletion:** Request deletion of your data
- **Portability:** Request transfer of your data
- **Objection:** Object to processing of your data
- **Restriction:** Request restriction of processing

### 7.2 GDPR Rights (EU/EEA)
- Right to lodge a complaint with supervisory authority
- Right to withdraw consent at any time

### 7.3 CCPA Rights (California)
- Right to know what data is collected
- Right to delete personal information
- Right to opt-out of sale (we do not sell data)
- Right to non-discrimination

### 7.4 Exercising Your Rights
To exercise these rights, contact us at [PRIVACY_EMAIL]

## 8. DATA SECURITY

We implement appropriate technical and organizational measures to protect your data:
- Encryption in transit and at rest
- Access controls and authentication
- Regular security assessments
- Employee training on data protection

However, no method of transmission over the Internet is 100% secure.

## 9. INTERNATIONAL DATA TRANSFERS

Your information may be transferred to and processed in countries other than your country of residence. We ensure appropriate safeguards are in place:
- Standard Contractual Clauses (SCCs)
- Adequacy decisions
- Privacy Shield (where applicable)

## 10. CHILDREN'S PRIVACY

Our Service is not intended for children under [AGE]. We do not knowingly collect data from children. If we learn we have collected such data, we will delete it immediately.

## 11. COOKIES AND TRACKING TECHNOLOGIES

We use cookies and similar technologies to:
- Remember your preferences
- Understand usage patterns
- Deliver targeted advertising

You can control cookies through your browser settings. See our Cookie Policy for details.

## 12. DO NOT TRACK

We do not respond to Do Not Track signals. You may disable tracking through browser settings and privacy tools.

## 13. THIRD-PARTY LINKS

Our Service may contain links to third-party websites. We are not responsible for the privacy practices of these sites. Please review their privacy policies.

## 14. CHANGES TO THIS POLICY

We may update this Privacy Policy from time to time. Changes will be posted with a new effective date. Material changes will be communicated via:
- Email notification
- Prominent notice on our Service

Continued use after changes constitutes acceptance.

## 15. CONTACT US

For questions or concerns about this Privacy Policy or our data practices:

- **Email:** [PRIVACY_EMAIL]
- **Address:** [PRIVACY_ADDRESS]
- **Data Protection Officer:** [DPO_CONTACT]

## 16. SUPERVISORY AUTHORITY

If you are in the EU/EEA, you have the right to lodge a complaint with your local data protection authority.

---

*Last Updated: [DATE]*

*DISCLAIMER: This is a template for informational purposes only. Consult with a qualified attorney and privacy professional before use.*
'''

        artifacts = [
            {
                "type": "markdown",
                "name": "privacy_policy",
                "filename": "privacy_policy.md",
                "content": content,
                "summary": f"Privacy Policy document for: {mission}"
            }
        ]

        return content, artifacts

    def _generate_compliance_document(self, mission: str) -> tuple[str, list]:
        """Generate a compliance or regulatory document."""
        content = f'''# Compliance Documentation

**Mission Context:** {mission}

**Document Date:** [DATE]

## 1. COMPLIANCE OVERVIEW

This document outlines compliance requirements and procedures for [ORGANIZATION_NAME] to ensure adherence to applicable regulations and standards.

## 2. APPLICABLE REGULATIONS

### 2.1 Data Protection Regulations
- **GDPR** (General Data Protection Regulation) - EU/EEA
- **CCPA** (California Consumer Privacy Act) - California, USA
- **HIPAA** (Health Insurance Portability and Accountability Act) - Healthcare (USA)
- **PIPEDA** (Personal Information Protection and Electronic Documents Act) - Canada

### 2.2 Industry Standards
- **ISO 27001** - Information Security Management
- **SOC 2** - Service Organization Control
- **PCI DSS** - Payment Card Industry Data Security Standard

## 3. DATA PROTECTION COMPLIANCE

### 3.1 GDPR Compliance Measures
- [ ] Lawful basis for processing personal data established
- [ ] Data Processing Agreements (DPAs) in place with processors
- [ ] Privacy Policy updated and accessible
- [ ] Cookie consent mechanism implemented
- [ ] Data Subject Rights procedures established (access, deletion, portability)
- [ ] Data Protection Impact Assessments (DPIAs) conducted for high-risk processing
- [ ] Data breach notification procedures in place (72-hour requirement)
- [ ] Data Protection Officer (DPO) appointed (if required)
- [ ] Records of processing activities maintained

### 3.2 CCPA Compliance Measures
- [ ] Privacy Policy includes CCPA-required disclosures
- [ ] "Do Not Sell My Personal Information" link provided (if applicable)
- [ ] Consumer rights request procedures established
- [ ] Opt-out mechanisms implemented
- [ ] Non-discrimination policy in place
- [ ] Service provider agreements updated

### 3.3 HIPAA Compliance Measures (if applicable)
- [ ] Business Associate Agreements (BAAs) executed
- [ ] Technical safeguards implemented (encryption, access controls)
- [ ] Administrative safeguards in place (policies, training)
- [ ] Physical safeguards implemented (facility security)
- [ ] Breach notification procedures established
- [ ] HIPAA Privacy and Security Rule training completed

## 4. INFORMATION SECURITY COMPLIANCE

### 4.1 ISO 27001 Alignment
- [ ] Information Security Management System (ISMS) established
- [ ] Risk assessment and treatment process implemented
- [ ] Security policies and procedures documented
- [ ] Access control policies enforced
- [ ] Incident management procedures in place
- [ ] Regular security audits conducted

### 4.2 SOC 2 Controls
- [ ] Security controls implemented and documented
- [ ] Availability controls for system uptime
- [ ] Processing integrity controls
- [ ] Confidentiality controls for sensitive data
- [ ] Privacy controls aligned with AICPA Trust Services Criteria

### 4.3 PCI DSS Compliance (if applicable)
- [ ] Firewall configuration to protect cardholder data
- [ ] Default passwords and security parameters changed
- [ ] Cardholder data protection (encryption, masking)
- [ ] Data transmission encryption over public networks
- [ ] Anti-virus software deployed and updated
- [ ] Secure systems and applications maintained
- [ ] Access to cardholder data restricted (need-to-know)
- [ ] Unique IDs assigned to users with computer access
- [ ] Physical access to cardholder data restricted
- [ ] Network and resource access tracked and monitored
- [ ] Security systems and processes regularly tested
- [ ] Information security policy maintained

## 5. COMPLIANCE MONITORING AND REPORTING

### 5.1 Regular Audits
- **Internal Audits:** [FREQUENCY]
- **External Audits:** [FREQUENCY]
- **Penetration Testing:** [FREQUENCY]
- **Vulnerability Scanning:** [FREQUENCY]

### 5.2 Compliance Metrics
| Metric | Target | Frequency | Responsible Party |
|--------|--------|-----------|-------------------|
| Security incidents | <[NUMBER]/month | Monthly | [ROLE] |
| Policy violations | 0 | Monthly | [ROLE] |
| Training completion | 100% | Quarterly | [ROLE] |
| Audit findings | <[NUMBER] critical | Annually | [ROLE] |

### 5.3 Reporting Requirements
- Quarterly compliance reports to management
- Annual compliance certification
- Incident reports within [TIMEFRAME]
- Regulatory filings as required

## 6. EMPLOYEE TRAINING AND AWARENESS

### 6.1 Mandatory Training
- [ ] Data protection and privacy training - All employees, annually
- [ ] Information security awareness - All employees, annually
- [ ] HIPAA training - Healthcare staff, annually (if applicable)
- [ ] PCI DSS training - Payment processing staff, annually (if applicable)

### 6.2 Training Documentation
- Training completion records maintained
- Training materials updated annually
- Quizzes and assessments administered
- Acknowledgment forms signed and retained

## 7. INCIDENT RESPONSE AND BREACH NOTIFICATION

### 7.1 Incident Response Plan
1. **Detection and Reporting:** Incidents reported to [CONTACT] within [TIMEFRAME]
2. **Assessment:** Severity and scope evaluation
3. **Containment:** Immediate actions to limit impact
4. **Investigation:** Root cause analysis
5. **Remediation:** Corrective actions implemented
6. **Documentation:** Incident log maintained
7. **Review:** Post-incident review and lessons learned

### 7.2 Breach Notification
- **GDPR:** Notify supervisory authority within 72 hours if high risk
- **CCPA:** Notify affected individuals without unreasonable delay
- **HIPAA:** Notify HHS and affected individuals within 60 days
- **State Laws:** Comply with applicable state breach notification laws

## 8. THIRD-PARTY VENDOR MANAGEMENT

### 8.1 Vendor Due Diligence
- [ ] Security questionnaires completed
- [ ] Compliance certifications verified (SOC 2, ISO 27001, etc.)
- [ ] Data Processing Agreements / Business Associate Agreements executed
- [ ] Regular vendor risk assessments conducted

### 8.2 Vendor Monitoring
- Annual compliance attestations required
- Periodic security reviews
- Incident notification requirements in contracts

## 9. RECORDS RETENTION

### 9.1 Retention Schedule
| Record Type | Retention Period | Responsible Party |
|-------------|------------------|-------------------|
| Contracts | [YEARS] after expiration | [ROLE] |
| Financial records | [YEARS] | [ROLE] |
| Employee records | [YEARS] after termination | [ROLE] |
| Audit logs | [MONTHS/YEARS] | [ROLE] |
| Privacy requests | [YEARS] | [ROLE] |

### 9.2 Secure Disposal
- Paper records: Shredding or incineration
- Electronic records: Secure deletion or destruction
- Storage media: Physical destruction or degaussing

## 10. CONTINUOUS IMPROVEMENT

### 10.1 Policy Review
- Compliance policies reviewed [FREQUENCY]
- Updates implemented based on regulatory changes
- Stakeholder feedback incorporated

### 10.2 Compliance Committee
- Regular meetings: [FREQUENCY]
- Members: [ROLES]
- Responsibilities: Oversight, risk assessment, policy development

## 11. COMPLIANCE ATTESTATION

I, [NAME], [TITLE], attest that [ORGANIZATION_NAME] has implemented the compliance measures outlined in this document and is committed to maintaining ongoing compliance with applicable regulations and standards.

Signature: _______________________
Name: [NAME]
Title: [TITLE]
Date: [DATE]

---

## APPENDICES

### Appendix A: Compliance Checklist
[Detailed checklist for each regulation]

### Appendix B: Policy References
[Links to related policies]

### Appendix C: Contact Information
[Compliance officer, DPO, legal counsel]

---

*DISCLAIMER: This is a template for informational purposes only. Consult with qualified legal and compliance professionals to ensure adherence to all applicable regulations.*
'''

        artifacts = [
            {
                "type": "markdown",
                "name": "compliance_documentation",
                "filename": "compliance_documentation.md",
                "content": content,
                "summary": f"Compliance documentation for: {mission}"
            }
        ]

        return content, artifacts

    def _generate_generic_legal_document(self, mission: str) -> tuple[str, list]:
        """Generate a generic legal document when specific type is not determined."""
        content = f'''# Legal Document

**Mission Context:** {mission}

## Document Overview

This legal document has been generated based on the mission requirements. Please review and customize as needed for your specific use case.

## 1. INTRODUCTION

[Document introduction and purpose]

## 2. DEFINITIONS

Key terms used in this document:

- **Term 1:** Definition
- **Term 2:** Definition
- **Term 3:** Definition

## 3. MAIN PROVISIONS

### 3.1 Section Title
[Content of section]

### 3.2 Section Title
[Content of section]

### 3.3 Section Title
[Content of section]

## 4. RIGHTS AND RESPONSIBILITIES

### 4.1 Party A
- Responsibility 1
- Responsibility 2
- Responsibility 3

### 4.2 Party B
- Responsibility 1
- Responsibility 2
- Responsibility 3

## 5. TERM AND TERMINATION

- **Effective Date:** [DATE]
- **Term:** [DURATION]
- **Termination Conditions:** [CONDITIONS]

## 6. DISPUTE RESOLUTION

Disputes shall be resolved through:
1. Negotiation
2. Mediation
3. Arbitration / Litigation

## 7. GOVERNING LAW

This document shall be governed by the laws of [JURISDICTION].

## 8. SIGNATURES

**PARTY A:**

Signature: _______________________
Name: [NAME]
Title: [TITLE]
Date: [DATE]

**PARTY B:**

Signature: _______________________
Name: [NAME]
Title: [TITLE]
Date: [DATE]

---

*DISCLAIMER: This is a template for informational purposes only. Consult with a qualified attorney before use.*
'''

        artifacts = [
            {
                "type": "markdown",
                "name": "legal_document",
                "filename": "legal_document.md",
                "content": content,
                "summary": f"Generic legal document for: {mission}"
            }
        ]

        return content, artifacts
