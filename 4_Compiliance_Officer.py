from pathlib import Path

import streamlit as st

from auth import initialize_session, logout, require_any_access
from utils import (
    apply_custom_style,
    compute_compliance,
    evaluate_contingency_controls,
    load_json,
    render_alerts,
    render_contingency_section,
    render_findings_cards,
    render_hero,
    render_kpi_card,
    render_progress_bar,
    render_section_header,
    render_sidebar,
    summarize_contingency_findings,
)

st.set_page_config(page_title="Compliance Officer", page_icon="📋", layout="wide")
apply_custom_style()
initialize_session()
require_any_access(["admin", "compliance"])

BASE_DIR = Path(__file__).resolve().parent.parent
CONTROL_FILE = BASE_DIR / "control_bank.json"
SYSTEM_FILE = BASE_DIR / "system_data.json"

controls = load_json(CONTROL_FILE)
system = load_json(SYSTEM_FILE)
summary = compute_compliance(controls, system)
contingency_findings = evaluate_contingency_controls(controls, system)
contingency_summary = summarize_contingency_findings(contingency_findings)
user = st.session_state.user

render_sidebar(user, summary, system)

render_hero(
    "Compliance Oversight",
    "Audit readiness view focused on control status, evidence quality, remediation needs, risk tracking, and recovery preparedness.",
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

render_contingency_section(contingency_findings, contingency_summary)

compliance_keywords = [
    "policy",
    "audit",
    "logging",
    "backup",
    "mfa",
    "password",
    "privacy",
    "access",
    "recovery",
    "downtime",
    "ransomware",
    "evidence",
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