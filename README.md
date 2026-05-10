# Healthcare Data Security Compliance Checker

## Overview

The Healthcare Data Security Compliance Checker is a cybersecurity proof-of-concept tool designed to evaluate healthcare system security configurations against industry compliance frameworks such as:

- HIPAA
- PHIPA
- NIST SP 800-53

The project demonstrates how healthcare compliance requirements can be translated into automated technical validation and security assessment processes.

The system analyzes simulated configuration data and security evidence to identify compliance gaps, calculate risk scores, detect suspicious activity, and generate a professional dashboard-style HTML report.

---

# Features

## Compliance Validation
The system evaluates security controls related to:

- Access Control
- Encryption
- Audit Logging
- Backup Protection
- Password Policies

---

## Evidence-Based Assessment
The tool analyzes simulated system evidence including:

- Configuration settings
- Authentication settings
- Logs
- Security indicators

---

## Risk Scoring
The checker calculates a weighted compliance score based on the severity of failed controls.

Risk Levels:
- Low Risk
- Medium Risk
- High Risk

---

## Security Monitoring
The system includes basic attack detection capabilities such as:

- Multiple failed login detection
- Suspicious access alerts
- Security alert generation

---

## Dashboard Report
Results are displayed through a professional HTML dashboard containing:

- Compliance score
- Security alerts
- Evidence tracking
- Remediation recommendations
- Risk assessment summary

---

# Project Structure

```bash
Healthcare-Compliance-Checker/
│
├── checker.py
├── control_bank.json
├── system_data.json
├── report.html
└── README.md
