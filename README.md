<p align="center">
  <img src="https://www.news-medical.net/image-handler/ts/20240308012538/ri/750/src/images/Article_Images/ImageForArticle_24645_17099223367073417.jpg" alt="Healthcare Compliance Checker" width="850">
</p>

<h1 align="center">🏥 Healthcare Compliance Lab</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Project-Healthcare%20Data%20Security-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Focus-Cybersecurity%20%26%20Compliance-teal?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Frameworks-HIPAA%20%7C%20PHIPA%20%7C%20NIST-purple?style=for-the-badge" />
</p>

<p align="center">
  <em>Transforming healthcare security through compliance automation, risk assessment, and data protection.</em>
</p>

<p align="center">
  <a href="#about-this-project">About</a> •
  <a href="#project-overview">Overview</a> •
  <a href="#project-status">Status</a> •
  <a href="#phase-1-completion">Phase 1</a> •
  <a href="#phase-2-direction">Phase 2</a> •
  <a href="#weekly-milestones">Milestones</a> •
  <a href="#group-roles-and-responsibilities">Team</a> •
  <a href="#links-and-resources">Resources</a>
</p>

---

## About This Project
<img align="right" alt="Coding" width="400" src="https://media.tenor.com/1S7bWTL8VWMAAAAi/abster-coded.gif">

We are fourth-year Information Sciences students at **Sheridan College** with a strong interest in cybersecurity, compliance, and healthcare data protection. As part of our capstone project, we are developing the **Healthcare Data Security Compliance Checker** to connect academic learning with a practical healthcare security challenge.

The project is designed as a proof-of-concept that helps evaluate whether important security safeguards are in place in healthcare environments. It does not process or store live patient health information. Instead, it focuses on security-related indicators, compliance validation, and evidence-based reporting.

### Team Members
- **Hartej Singh Dhanjal** — Project Manager
- **Carleen Gyamfi** — Research & Compliance Lead
- **Kasinadhan Udayakumar** — Technical Lead

---

## Project Overview

The Healthcare Data Security Compliance Checker is a cybersecurity and compliance support tool developed to help healthcare organizations evaluate whether important technical safeguards are properly implemented. The tool focuses on healthcare data security requirements and does not process or store live patient health information.

Instead, it checks whether selected system configurations and security practices align with healthcare security expectations.

Our intention is for the tool to run as a lightweight background monitoring and compliance support system while healthcare professionals access PHI systems. It collects security-related metadata such as:

- Login attempts
- MFA status
- Role-based access status
- Audit log availability
- Encryption status
- Backup protection
- Suspicious access indicators

It then evaluates these signals against healthcare security control requirements and generates plain-language and technical reports showing:

- Risk level
- Compliance gaps
- Supporting evidence
- Remediation recommendations

### Main safeguard areas
- Access control
- Encryption and transmission security
- Logging and audit controls
- Backup and contingency planning

---

## Project Status

The project is currently in the refinement stage. Phase 1 is complete, and Phase 2 is focused on improving the prototype’s usability, documentation, mapping accuracy, and reporting quality.

The goal for Phase 2 is to improve the existing prototype into a more complete and evidence-based compliance checker that is also practical for smaller and privately funded healthcare organizations that may not have access to expensive enterprise compliance platforms.

---
## user repository roles

## Phase 1 Completion

During Phase 1, we completed the original project idea, proposal, research, prototype concept, and early implementation. The project proposal identified the gap between regulatory requirements and real-world technical implementation in healthcare cybersecurity.

We also outlined how frameworks such as **HIPAA**, **PHIPA**, **ISO/IEC 27001**, and **NIST SP 800-53A** support structured evaluation of healthcare security controls.

Our group also developed an initial Python-based prototype. The prototype already evaluates selected controls including:

- MFA
- TLS/HTTPS
- Audit logging
- Encrypted backups
- Password policy strength

The current code uses:

- A control bank
- System data
- Weighted risk scoring
- Attack detection logic
- HTML report generation

Phase 1 also included testing different scenarios. In Week 14, the prototype was tested by changing user responses across access control, encryption, audit logging, backup protection, and suspicious activity indicators to evaluate how the system behaved under stronger and weaker compliance conditions.

---

## Research-Informed Improvements

Recent healthcare cybersecurity research emphasizes that healthcare organizations must protect sensitive patient data while still allowing efficient and appropriate access to patient information. One article reviewed for this project highlights the importance of cybersecurity, encrypted computation, real-time monitoring, secure data sharing, privacy-preserving methods, and protection of sensitive patient data in healthcare environments.

As IT professionals and cybersecurity students, we also understand the importance of developing tools with UI-centered design, ethical oversight, and regulatory alignment. These ideas are relevant to our compliance checker because the tool is intended for healthcare environments where usability, trust, privacy, and clear reporting are important.

For Phase 2, instead of implementing complex machine learning or full electronic health record integration, the tool will use a more practical rule-based approach focused on evidence collection, configuration checks, and control mapping.

---

## Feedback Received

As we move forward in the Spring/Summer 2026 semester, we are focusing on improving the project's technical and compliance alignment.

The main feedback provided to our group by Professor Syed Tanbeer was to:

- Explain how configurations would be evaluated against HIPAA and NIST.
- Map configurations to real standards.
- Make the system accessible to medical staff.
- Include awareness of common cyberattacks.
- Create an overall system diagram.
- Implement User Reporsitories for login redirections.

### How we will address it
- Expand the control bank so each check includes a control ID, category, expected value, risk level, remediation, and regulatory mapping.
- Map each technical check to related healthcare security areas such as access control, transmission security, audit controls, and contingency planning.
- Improve the questionnaire so the tool can be used by non-technical healthcare staff as well as IT and security users.
- Add a section that explains common cybersecurity risks such as weak passwords, missing MFA, failed login attempts, suspicious IP activity, missing audit logs, and unencrypted backups.
- Update GitHub weekly.

---
## Phase 2 Direction

As we move into Phase 2, the goal is to improve the prototype into a more complete and evidence-based compliance checker.

Planned improvements include:

- Expanding the control bank with more detailed fields such as control ID, category, expected value, evidence, risk level, and remediation.
- Mapping each technical check to healthcare security areas in a more structured way.
- Improving the questionnaire so it can be used by both healthcare staff and technical users.
- Adding explanations for common cyber risks such as weak passwords, missing MFA, failed logins, suspicious IP activity, missing logs, and unencrypted backups.
- Strengthening the system diagram and documentation.
- Updating GitHub on a weekly basis.

---

## Standards and Control Mapping

The project uses healthcare security frameworks as reference points for mapping technical checks to regulatory expectations. These include **HIPAA**, **PHIPA**, **ISO/IEC 27001**, and **NIST SP 800-53A**.

A key design goal in Phase 2 is to map each technical control to an understandable compliance category.

### Example control map

| Tool Check | Category | Related Standard | Evidence Needed | Risk |
|---|---|---|---|---|
| MFA enabled for admin accounts | Access Control | HIPAA Technical Safeguards / NIST Access Control | Screenshot or configuration showing MFA enabled | High |
| Audit logging enabled | Audit Controls | HIPAA Audit Controls / NIST logging controls | Log settings, sample audit log | Medium / High |
| TLS/HTTPS enabled | Transmission Security | HIPAA Transmission Security | HTTPS certificate, TLS settings | High |
| Backups encrypted | Contingency Planning | HIPAA backup/security practices | Backup policy or configuration | High |
| Failed login detection | Detect / Respond | NIST CSF Detect / Respond | Login logs or alert records | Medium / High |

---

## Features Completed

- Initial project proposal and scope definition.
- Prototype concept and control bank design.
- Basic Python compliance logic.
- Checks for MFA, TLS/HTTPS, audit logging, encrypted backups, and password strength.
- Weighted risk scoring.
- HTML reporting.
- Scenario-based testing.

---

## Features Still in Progress

- Expanded control bank with regulatory mapping.
- More accurate HIPAA, PHIPA, and NIST alignment.
- Background monitoring logic.
- Suspicious activity detection.
- Improved questionnaire for healthcare and non-technical users.
- Plain-language reporting improvements.
- System architecture diagram.
- Weekly GitHub documentation updates.
- User Repository 

---

## Known Issues and Limitations

- The current prototype is still a proof-of-concept and not a production-ready compliance platform.
- The tool does not collect or store live PHI, so it evaluates security posture rather than actual clinical records.
- Some control-to-standard mappings still need refinement.
- Background monitoring may remain limited until Phase 2 is further developed.
- Testing scenarios may not yet represent every real-world healthcare environment.

---

## Weekly Milestones

**Subject to change based on professor feedback and requirements**

| Week | Planned Milestone | Evidence |
|---|---|---|
| 1 | Submit revised project plan and update GitHub README | Revised plan report, README link |
| 2 | Update system architecture diagram and finalize Phase 2 scope | Diagram, GitHub update |
| 3 | Improve questionnaires | UI screenshots |
| 4 | Expand control bank with regulatory mappings | Updated control bank / JSON |
| 5 | HIPAA / PHIPA / NIST mapping to each major control | Mapping table + documentation |
| 6 | Build background monitoring logic for access events | Code commit, test data |
| 7 | Add suspicious activity detection: failed logins, unusual access, missing MFA | Alert screenshots, test results |
| 8 | Improve scoring system by category and severity | Sample reports |
| 9 | Improve plain-language and technical report output | HTML / PDF report screenshots |
| 10 | Test multiple healthcare scenarios | Testing notes, screenshots |
| 11 | Prepare final report, slides, and demo script | Draft report and slides |
| 12 | Finalize project, GitHub, final demo, and submission | Final repository and presentation |

---

## Group Roles and Responsibilities

| Member | Role | Responsibilities |
|---|---|---|
| Carleen | Research & Compliance Lead | HIPAA / PHIPA / NIST mapping, documentation, testing scenarios, report writing |
| Kasi | Technical & Prototype Lead | Code implementation, Streamlit interface, monitoring logic, report generation |
| Hartej | Project Management & Presentation Lead | Weekly coordination, GitHub evidence, slides, diagrams, integration support |

---

## Risks and Challenges

- Difficulty mapping technical checks accurately to HIPAA, NIST, and PHIPA.
- Scope becoming too large.
- Background monitoring feature becoming too complex.
- GitHub not being updated weekly.
- Uneven group contribution.
- Testing scenarios may not be realistic enough.

---

## Links and Resources

- Repository: [healthcare-compliance-checker](https://github.com/HealthcareCompilanceLab/healthcare-compliance-checker)
- ProQuest Computer Science Journals Database: (https://www.proquest.com/compscijour/fromDatabasesLayer)
- CCOHS Academic: Occupational Health and Safety Information: https://www-ccohs-ca.library.sheridanc.on.ca/ccinfoweb/asp
- EBSCOhost: Applied Science & Tech Source: https://research-ebsco-com.library.sheridanc.on.ca/c/uombjt/search/advanced/filters?autocorrect=y&db=awh
- EBSCOhost: Health Source- Consumer Edition: https://research-ebsco-com.library.sheridanc.on.ca/c/uombjt/search/advanced/filters?auth-callid=f6c73317-b31e-418c-bd6a-23ea8ccef0a0&autocorrect=y&db=hch
- CanLII: Canadian Legal Information Institute: https://www.canlii.org/?origLang=en

---

<p align="center">
  <img src="https://img.shields.io/badge/Cyber%20Security-Our%20Passion-red?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Open%20to%20Opportunities-Yes-brightgreen?style=for-the-badge" />
</p>

<p align="center">
  <strong>⭐ If you find our work valuable, please consider giving it a star! ⭐</strong>
</p>

**Last updated:** 2026-05-24

*Building safer, more compliant healthcare systems, one project at a time.*
