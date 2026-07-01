from pathlib import Path

import pandas as pd
import streamlit as st

from auth import initialize_session, logout, require_any_access
from utils import (
    apply_custom_style,
    compute_compliance,
    load_json,
    read_audit_log,
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
CONTROL_FILE = BASE_DIR / "control_bank.json"
SYSTEM_FILE = BASE_DIR / "system_data.json"

controls = load_json(CONTROL_FILE)
system = load_json(SYSTEM_FILE)
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

c1, c2, c3 = st.columns(3)
with c1:
    render_kpi_card("Total Events", str(total_events), "Number of recorded audit entries", "info")
with c2:
    render_kpi_card("Successful Events", str(success_events), "Successful login/logout activity", "success")
with c3:
    render_kpi_card("Failed Events", str(failed_events), "Failed login attempts or errors", "danger")

render_section_header("Audit Entries", "Most recent application audit entries appear first.", "🗂")

if audit_lines:
    df = pd.DataFrame({"Audit Log Entry": audit_lines})
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No audit entries found.")

st.markdown("---")
if st.button("Logout"):
    logout()
    st.rerun()