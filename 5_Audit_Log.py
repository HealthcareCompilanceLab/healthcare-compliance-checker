from pathlib import Path
import pandas as pd
import streamlit as st
from auth import initialize_session, logout, require_any_access
from utils import (
    apply_custom_style,
    compute_compliance,
    load_json,
    read_audit_log,
    render_alerts,
    render_divider,
    render_event_outcome_chart,
    render_findings_cards,
    render_hero,
    render_kpi_card,
    render_section_header,
    render_sidebar,
)

st.set_page_config(page_title="Audit Log", page_icon="📝", layout="wide")
apply_custom_style()
initialize_session()
require_any_access(["admin", "compliance", "it"])

BASE_DIR = Path(__file__).resolve().parent.parent
controls = load_json(BASE_DIR / "control_bank.json")
system = load_json(BASE_DIR / "system_data.json")
summary = compute_compliance(controls, system)
user = st.session_state.user

render_sidebar(user, summary, system)
render_hero(
    "Audit Log Review",
    "Track recent login attempts, user activity, and operational events recorded by the application.",
    "Audit Monitoring",
)

audit_lines = read_audit_log()
total_events = len(audit_lines)
failed_events = len([line for line in audit_lines if "STATUS=FAILED" in line])
success_events = len([line for line in audit_lines if "STATUS=SUCCESS" in line])
other_events = max(total_events - success_events - failed_events, 0)
unique_users = len(set([line.split("JOB_ID=")[1].split(" |")[0] for line in audit_lines if "JOB_ID=" in line])) if audit_lines else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Total Events", str(total_events), "Number of recorded audit entries", "info", "🗃️")
with c2:
    render_kpi_card("Successful Events", str(success_events), "Successful login/logout activity", "success", "✅")
with c3:
    render_kpi_card("Failed Events", str(failed_events), "Failed login attempts or errors", "danger" if failed_events else "success", "⛔")
with c4:
    render_kpi_card("Active Users", str(unique_users), "Distinct users in the log", "info", "👥")

render_divider()
render_section_header("Log Health", "Conditions flagged by current system telemetry.", "🩺")
render_alerts(summary["alerts"])

left, right = st.columns([1.15, 0.85])
with left:
    render_section_header("Audit Entries", "Most recent application audit entries appear first.", "🗂")
    if audit_lines:
        df = pd.DataFrame({"Audit Log Entry": audit_lines})
        st.dataframe(df, use_container_width=True, hide_index=True, height=420)
    else:
        st.info("No audit entries found.")
with right:
    if total_events:
        render_event_outcome_chart(success_events, failed_events, other_events, title="Activity Snapshot")
    else:
        render_section_header("Activity Snapshot", "A compact summary of event volume and outcomes.", "▣")
        st.info("No audit entries recorded yet — outcomes will appear here once logins occur.")
    st.markdown("<div class='hc-card'>", unsafe_allow_html=True)
    st.markdown('<div class="hc-card-title">Top Audit Signals</div>', unsafe_allow_html=True)
    for signal in ["Repeated failed logins", "Unexpected user switches", "Access outside normal hours", "Missing evidence trails"]:
        st.markdown(f'<div class="hc-subtitle">• {signal}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

render_divider()
render_section_header("Integrity Findings", "Logging, tamper-evidence, and integrity-related findings.", "🔐")
audit_results = [r for r in summary["results"] if r["category"] in ["Logging", "Audit Logging", "Audit Controls", "Data Integrity"]]
render_findings_cards(audit_results if audit_results else summary["results"], limit=6)

render_divider()
if st.button("Logout"):
    logout()
    st.rerun()
