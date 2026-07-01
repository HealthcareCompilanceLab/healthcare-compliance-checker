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
    render_system_overview,
    summarize_contingency_findings,
)

st.set_page_config(page_title="IT Security", page_icon="💻", layout="wide")
apply_custom_style()
initialize_session()
require_any_access(["admin", "it"])

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
    "IT Security Operations",
    "Technical review of authentication, monitoring, infrastructure hardening, encryption, operational risk, and recovery readiness.",
    "IT Security View",
)

failed_logins = system.get("login_attempts", []).count("failed")
mfa_status = "Enabled" if system.get("mfa_enabled") else "Disabled"
tls_status = "Enabled" if system.get("tls_enabled") else "Disabled"
logging_status = "Enabled" if system.get("logging_enabled") else "Disabled"

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card(
        "MFA",
        mfa_status,
        "Privileged and user account protection",
        "success" if mfa_status == "Enabled" else "danger",
    )
with c2:
    render_kpi_card(
        "TLS / HTTPS",
        tls_status,
        "Encrypted communications status",
        "success" if tls_status == "Enabled" else "danger",
    )
with c3:
    render_kpi_card(
        "Audit Logging",
        logging_status,
        "Visibility into activity and events",
        "success" if logging_status == "Enabled" else "danger",
    )
with c4:
    render_kpi_card(
        "Failed Logins",
        str(failed_logins),
        "Authentication anomalies detected",
        "danger" if failed_logins >= 3 else "info",
    )

render_section_header("Technical Posture", "Current system configuration and live control indicators.", "◆")
render_system_overview(system)

render_section_header("Operational Risk", "Visual summary of IT-facing compliance results.", "▣")
render_progress_bar("Compliance Score", summary["percent"], "info")
render_progress_bar(
    "Failed Controls Ratio",
    (summary["failed"] / len(summary["results"])) * 100 if summary["results"] else 0,
    "danger",
)
render_progress_bar(
    "Passed Controls Ratio",
    (summary["passed"] / len(summary["results"])) * 100 if summary["results"] else 0,
    "success",
)

render_section_header("Security Alerts", "Events and patterns needing technical review.", "⚠")
render_alerts(summary["alerts"])

render_contingency_section(contingency_findings, contingency_summary)

it_keywords = [
    "mfa",
    "tls",
    "audit",
    "logging",
    "backup",
    "password",
    "endpoint",
    "access",
    "recovery",
    "ransomware",
    "downtime",
]
it_results = [
    item for item in summary["results"]
    if any(
        keyword in item.get("desc", "").lower() or keyword in item.get("evidence", "").lower()
        for keyword in it_keywords
    )
]

render_section_header(
    "IT Findings",
    "Technical findings most relevant to infrastructure, monitoring, encryption, backup, and recovery operations.",
    "🛡",
)
render_findings_cards(it_results if it_results else summary["results"])

st.markdown("---")
if st.button("Logout"):
    logout()
    st.rerun()