from pathlib import Path

import streamlit as st

from auth import initialize_session, logout, require_any_access
from utils import (
    apply_custom_style,
    compute_compliance,
    load_json,
    render_alerts,
    render_findings_cards,
    render_hero,
    render_kpi_card,
    render_progress_bar,
    render_section_header,
    render_sidebar,
)

st.set_page_config(page_title="Compliance Officer", page_icon="📋", layout="wide")
apply_custom_style()
initialize_session()
require_any_access(["admin", "compliance"])

BASE_DIR = Path(__file__).resolve().parent.parent
CONTROL_FILE = BASE_DIR / "control_bank.json"
SYSTEM_FILE = BASE_DIR / "system_data.json"


def evaluate_ehr_safeguards(system):
    return [
        {
            "control_id": "EHR-001",
            "name": "TLS/HTTPS enabled",
            "status": "PASS" if system.get("tls_https_enabled") else "FAIL",
            "severity": "High",
            "evidence": f"tls_https_enabled = {system.get('tls_https_enabled', 'Not Found')}",
            "remediation": "Enable TLS/HTTPS for systems that transmit healthcare or authentication data.",
        },
        {
            "control_id": "EHR-002",
            "name": "Data encryption at rest",
            "status": "PASS" if system.get("data_encryption_at_rest") else "FAIL",
            "severity": "High",
            "evidence": f"data_encryption_at_rest = {system.get('data_encryption_at_rest', 'Not Found')}",
            "remediation": "Encrypt stored healthcare and operational data at rest.",
        },
        {
            "control_id": "EHR-003",
            "name": "Encrypted backups",
            "status": "PASS" if system.get("encrypted_backups") else "FAIL",
            "severity": "High",
            "evidence": f"encrypted_backups = {system.get('encrypted_backups', 'Not Found')}",
            "remediation": "Encrypt backup media and backup storage containing sensitive information.",
        },
        {
            "control_id": "EHR-004",
            "name": "Firewall enabled",
            "status": "PASS" if system.get("firewall_enabled") else "FAIL",
            "severity": "High",
            "evidence": f"firewall_enabled = {system.get('firewall_enabled', 'Not Found')}",
            "remediation": "Enable and maintain firewall protection for healthcare systems and supporting infrastructure.",
        },
        {
            "control_id": "EHR-005",
            "name": "Firewall monitored / reviewed",
            "status": "PASS" if system.get("firewall_monitored") else "FAIL",
            "severity": "Medium",
            "evidence": f"firewall_monitored = {system.get('firewall_monitored', 'Not Found')}",
            "remediation": "Review firewall rules and logs regularly to support secure network access.",
        },
        {
            "control_id": "EHR-006",
            "name": "Antivirus enabled",
            "status": "PASS" if system.get("antivirus_enabled") else "FAIL",
            "severity": "Medium",
            "evidence": f"antivirus_enabled = {system.get('antivirus_enabled', 'Not Found')}",
            "remediation": "Enable antivirus protection on healthcare workstations and supported systems.",
        },
        {
            "control_id": "EHR-007",
            "name": "Endpoint protection enabled",
            "status": "PASS" if system.get("endpoint_protection_enabled") else "FAIL",
            "severity": "Medium",
            "evidence": f"endpoint_protection_enabled = {system.get('endpoint_protection_enabled', 'Not Found')}",
            "remediation": "Implement endpoint protection or managed device security controls.",
        },
        {
            "control_id": "EHR-008",
            "name": "Workstation security controls",
            "status": "PASS" if system.get("workstation_security_controls") else "FAIL",
            "severity": "Medium",
            "evidence": f"workstation_security_controls = {system.get('workstation_security_controls', 'Not Found')}",
            "remediation": "Apply workstation hardening and device security controls for systems handling PHI.",
        },
        {
            "control_id": "EHR-009",
            "name": "Role-based access control",
            "status": "PASS" if system.get("role_based_access_control") else "FAIL",
            "severity": "High",
            "evidence": f"role_based_access_control = {system.get('role_based_access_control', 'Not Found')}",
            "remediation": "Restrict access using role-based permissions aligned to job responsibilities.",
        },
        {
            "control_id": "EHR-010",
            "name": "Secure remote access",
            "status": "PASS" if system.get("remote_access_secured") else "FAIL",
            "severity": "Medium",
            "evidence": f"remote_access_secured = {system.get('remote_access_secured', 'Not Found')}",
            "remediation": "Protect remote access using approved secure access controls and authentication safeguards.",
        },
    ]


def render_ehr_safeguards(system):
    findings = evaluate_ehr_safeguards(system)
    passed = sum(1 for item in findings if item["status"] == "PASS")
    failed = sum(1 for item in findings if item["status"] == "FAIL")
    score = (passed / len(findings)) * 100 if findings else 0

    render_section_header(
        "EHR Safeguards",
        "Encryption, firewall, endpoint protection, workstation security, access control, and secure remote access checks.",
        "🛡",
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Safeguards Checked", str(len(findings)), "Visible EHR safeguard controls", "info")
    with c2:
        render_kpi_card("Passed", str(passed), "Controls currently meeting expectations", "success")
    with c3:
        render_kpi_card("Failed", str(failed), "Controls requiring remediation", "danger")
    with c4:
        render_kpi_card("EHR Score", f"{score:.1f}%", "Encryption and infrastructure security", "warning")

    render_progress_bar("EHR Safeguards Score", score, "info")

    for item in findings:
        tone = "hc-success" if item["status"] == "PASS" else "hc-alert"
        st.markdown(
            f"""
            <div class="hc-finding-card">
                <div class="hc-finding-top">
                    <div class="hc-finding-title">{item['control_id']} - {item['name']}</div>
                    <div class="{tone}" style="padding:8px 12px; border-radius:12px; margin:0;">{item['status']}</div>
                </div>
                <div class="hc-finding-grid">
                    <div class="hc-finding-box">
                        <div class="hc-card-title">Severity</div>
                        <div class="hc-subtitle">{item['severity']}</div>
                    </div>
                    <div class="hc-finding-box">
                        <div class="hc-card-title">Evidence</div>
                        <div class="hc-subtitle">{item['evidence']}</div>
                    </div>
                    <div class="hc-finding-box">
                        <div class="hc-card-title">Remediation</div>
                        <div class="hc-subtitle">{item['remediation']}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


controls = load_json(CONTROL_FILE)
system = load_json(SYSTEM_FILE)
summary = compute_compliance(controls, system)
user = st.session_state.user

render_sidebar(user, summary, system)

render_hero(
    "Compliance Oversight",
    "Audit readiness view focused on control status, evidence quality, remediation needs, risk tracking, and healthcare infrastructure safeguards.",
    "Compliance View",
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Compliance Score", f"{summary['percent']:.2f}%", "Overall control effectiveness", "info")
with c2:
    render_kpi_card("Risk Level", summary["overall"], "Current compliance risk", "warning")
with c3:
    render_kpi_card("Insufficient Data", str(summary["insufficient"]), "Controls missing evidence or data", "warning")
with c4:
    render_kpi_card("Failed Controls", str(summary["failed"]), "Controls requiring remediation", "danger")

render_section_header("Audit Readiness", "Progress indicators for compliance tracking and evidence coverage.", "▣")
total_controls = len(summary["results"]) if summary["results"] else 1
render_progress_bar("Controls Passed", (summary["passed"] / total_controls) * 100, "success")
render_progress_bar("Controls Failed", (summary["failed"] / total_controls) * 100, "danger")
render_progress_bar("Evidence Gaps", (summary["insufficient"] / total_controls) * 100, "warning")

render_section_header("Compliance Alerts", "Conditions that may affect policy adherence or audit readiness.", "⚠")
render_alerts(summary["alerts"])

render_ehr_safeguards(system)

compliance_keywords = [
    "policy", "audit", "logging", "backup", "mfa", "password", "privacy", "access",
    "tls", "encryption", "firewall", "antivirus", "endpoint", "workstation", "remote"
]
compliance_results = [
    item for item in summary["results"]
    if any(
        keyword in item.get("desc", "").lower() or keyword in item.get("remediation", "").lower()
        for keyword in compliance_keywords
    )
]

render_section_header("Control Findings", "Detailed compliance findings with evidence and remediation notes.", "✓")
render_findings_cards(compliance_results if compliance_results else summary["results"])

st.markdown("---")
if st.button("Logout"):
    logout()
    st.rerun()