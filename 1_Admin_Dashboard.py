from pathlib import Path

import pandas as pd
import streamlit as st

from auth import initialize_session, logout, require_access
from utils import (
    apply_custom_style,
    compute_compliance,
    load_json,
    read_audit_log,
    render_alerts,
    render_findings_cards,
    render_hero,
    render_kpi_card,
    render_progress_bar,
    render_section_header,
    render_sidebar,
    render_system_overview,
)

st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")
apply_custom_style()
initialize_session()
require_access("admin")

BASE_DIR = Path(__file__).resolve().parent.parent
CONTROL_FILE = BASE_DIR / "control_bank.json"
SYSTEM_FILE = BASE_DIR / "system_data.json"

controls = load_json(CONTROL_FILE)
system = load_json(SYSTEM_FILE)
summary = compute_compliance(controls, system)
user = st.session_state.user

render_sidebar(user, summary, system)

render_hero(
    "Admin Security Dashboard",
    "Executive view of healthcare security posture, control performance, alerts, and recent audit activity.",
    "Administrator Access",
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Compliance Score", f"{summary['percent']:.2f}%", "Overall compliance posture", "info")
with c2:
    render_kpi_card("Risk Level", summary["overall"], "Calculated from control results", "warning")
with c3:
    render_kpi_card("Passed Controls", str(summary["passed"]), "Controls meeting expectations", "success")
with c4:
    render_kpi_card("Failed Controls", str(summary["failed"]), "Controls needing remediation", "danger")

render_section_header("Control Performance", "Breakdown of compliance status across evaluated controls.", "▣")
total_controls = summary["passed"] + summary["failed"] + summary["insufficient"]

if total_controls > 0:
    render_progress_bar("Passed", (summary["passed"] / total_controls) * 100, "success")
    render_progress_bar("Failed", (summary["failed"] / total_controls) * 100, "danger")
    render_progress_bar("Insufficient Data", (summary["insufficient"] / total_controls) * 100, "warning")

render_section_header("Security Alerts", "Detected issues based on current system posture.", "⚠")
render_alerts(summary["alerts"])

render_section_header("System Overview", "Key live configuration and monitoring indicators.", "◆")
render_system_overview(system)

render_section_header("Recent Audit Activity", "Latest login and access activity from the audit log.", "📝")
audit_lines = read_audit_log(limit=10)
if audit_lines:
    df = pd.DataFrame({"Recent Events": audit_lines})
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No audit log entries found yet.")

render_section_header("Compliance Findings", "Detailed findings with evidence and recommended action.", "✓")
render_findings_cards(summary["results"])

st.markdown("---")
if st.button("Logout"):
    logout()
    st.rerun()