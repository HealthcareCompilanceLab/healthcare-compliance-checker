from pathlib import Path
import streamlit as st
from auth import initialize_session, logout, require_any_access
from utils import (
    apply_custom_style,
    compute_compliance,
    load_json,
    render_alerts,
    render_category_bar,
    render_compliance_donut,
    render_divider,
    render_findings_cards,
    render_hero,
    render_kpi_card,
    render_score_gauge,
    render_section_header,
    render_severity_chart,
    render_sidebar,
)

st.set_page_config(page_title="Compliance Officer", page_icon="📋", layout="wide")
apply_custom_style()
initialize_session()
require_any_access(["admin", "compliance"])

BASE_DIR = Path(__file__).resolve().parent.parent
controls = load_json(BASE_DIR / "control_bank.json")
system = load_json(BASE_DIR / "system_data.json")
summary = compute_compliance(controls, system)
user = st.session_state.user

render_sidebar(user, summary, system)
render_hero(
    "Compliance Oversight",
    "Audit readiness view focused on control status, evidence quality, remediation needs, and risk tracking.",
    "Compliance View",
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Compliance Score", f"{summary['percent']:.2f}%", "Overall control effectiveness", "success" if summary["percent"] >= 85 else "warning" if summary["percent"] >= 60 else "danger", "🎯")
with c2:
    render_kpi_card("Risk Level", summary["overall"], "Current compliance risk", "danger" if summary["overall"] == "HIGH RISK" else "warning" if summary["overall"] == "MEDIUM RISK" else "success", "🛰️")
with c3:
    render_kpi_card("Insufficient Data", str(summary["insufficient"]), "Controls missing evidence or data", "warning", "❔")
with c4:
    render_kpi_card("Failed Controls", str(summary["failed"]), "Controls requiring remediation", "danger", "⛔")

render_divider()
render_section_header("Audit Readiness", "Visual breakdown of control outcomes and remaining risk.", "🧭")
g1, g2 = st.columns(2)
with g1:
    render_score_gauge(summary, title="Readiness Score")
with g2:
    render_compliance_donut(summary, title="Status Breakdown")

render_section_header("Compliance by Category", "Pass rate across every control category, weakest first.", "📊")
render_category_bar(summary["results"])

render_section_header("Failed-Control Risk Exposure", "Severity distribution of controls that still need remediation.", "📛")
render_severity_chart(summary["results"])

render_divider()
render_section_header("Compliance Alerts", "Conditions that may affect policy adherence or audit readiness.", "⚠")
render_alerts(summary["alerts"])

render_section_header("Control Findings", "Detailed compliance findings with severity, evidence, explanations, remediation, and references.", "✓")
render_findings_cards(summary["results"], limit=6)

render_divider()
if st.button("Logout"):
    logout()
    st.rerun()
