from pathlib import Path
import pandas as pd
import streamlit as st
from auth import initialize_session, logout, require_any_access
from utils import (
    apply_custom_style,
    compute_compliance,
    load_json,
    render_alerts,
    render_category_bar,
    render_divider,
    render_findings_cards,
    render_hero,
    render_kpi_card,
    render_score_gauge,
    render_section_header,
    render_severity_chart,
    render_sidebar,
    render_system_overview,
)

st.set_page_config(page_title="IT Security", page_icon="💻", layout="wide")
apply_custom_style()
initialize_session()
require_any_access(["admin", "it"])

BASE_DIR = Path(__file__).resolve().parent.parent
controls = load_json(BASE_DIR / "control_bank.json")
system = load_json(BASE_DIR / "system_data.json")
summary = compute_compliance(controls, system)
user = st.session_state.user

# IT Security cares about the technical control categories specifically
IT_CATEGORIES = ["Encryption", "Network Security", "Endpoint Security", "Access Control", "Remote Access", "Audit Controls"]
it_results = [r for r in summary["results"] if r["category"] in IT_CATEGORIES]

render_sidebar(user, summary, system)
render_hero(
    "IT Security Operations",
    "Technical review of authentication, monitoring, infrastructure hardening, encryption, and operational risk.",
    "IT Security View",
)

# NOTE: these KPIs now read the *actual* fields present in system_data.json.
# (Previously this page referenced fields such as tls_enabled / logging_enabled /
# login_attempts / firewall_enabled / endpoint_protection_enabled that don't exist
# in the data model, so every card silently showed "Disabled" or "0".)
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("MFA", "Enabled" if system.get("mfa_enabled") else "Disabled",
                     "Privileged and user account protection", "success" if system.get("mfa_enabled") else "danger", "🔐")
with c2:
    render_kpi_card("Secure Remote Access", "Enabled" if system.get("secure_remote_access") else "Disabled",
                     "Encrypted / hardened remote connections", "success" if system.get("secure_remote_access") else "danger", "🌐")
with c3:
    render_kpi_card("Audit Logging", "Enabled" if system.get("audit_logging") else "Disabled",
                     "Visibility into activity and events", "success" if system.get("audit_logging") else "danger", "🗂️")
with c4:
    render_kpi_card("Failed Logins", str(system.get("failed_login_count", 0)),
                     "Authentication anomalies detected", "danger" if system.get("failed_login_count", 0) >= 3 else "info", "⚠️")

render_divider()
left, right = st.columns([1.1, 1])
with left:
    render_section_header("Technical Posture", "Current system configuration and live control indicators.", "◆")
    render_system_overview(system)
with right:
    render_section_header("IT Compliance Score", "Weighted compliance score across all evaluated controls.", "▣")
    render_score_gauge(summary, title="")

render_section_header("Technical Control Performance", "Pass rate for each IT-facing control category.", "📊")
render_category_bar(summary["results"], categories=IT_CATEGORIES, icon="🖥️")

render_section_header("Risk Exposure by Severity", "IT-relevant failed controls grouped by severity.", "📛")
render_severity_chart(it_results if it_results else summary["results"])

render_divider()
render_section_header("Security Alerts", "Conditions flagged by current system telemetry.", "🚨")
render_alerts(summary["alerts"])

render_section_header("IT Findings", "Technical findings with evidence, explanation, remediation, and references.", "🛡")
render_findings_cards(it_results if it_results else summary["results"], limit=6)

render_divider()
if st.button("Logout"):
    logout()
    st.rerun()
