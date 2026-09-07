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

st.set_page_config(page_title='Admin Dashboard', page_icon='📊', layout='wide')
apply_custom_style()
initialize_session()
require_access('admin')

BASE_DIR = Path(__file__).resolve().parent.parent
controls = load_json(BASE_DIR / 'control_bank.json')
system = load_json(BASE_DIR / 'system_data.json')
summary = compute_compliance(controls, system)
user = st.session_state.user

render_sidebar(user, summary, system)
render_hero(
    'Admin Security Dashboard',
    'Executive view of healthcare security posture, control performance, alerts, and recent audit activity.',
    'Administrator Access',
)

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    render_kpi_card('Compliance Score', f"{summary['percent']:.1f}%", 'Weighted across all controls', 'info', '🎯')
with c2:
    render_kpi_card('Risk Level', summary['overall'], 'Current organizational risk', 'danger' if summary['overall'] == 'HIGH RISK' else 'warning' if summary['overall'] == 'MEDIUM RISK' else 'success', '🛰️')
with c3:
    render_kpi_card('Passed', summary['passed'], 'Controls fully satisfied', 'success', '✅')
with c4:
    render_kpi_card('Failed', summary['failed'], 'Controls needing remediation', 'danger', '⛔')
with c5:
    render_kpi_card('Insufficient', summary['insufficient'], 'Missing evidence or data', 'warning', '❔')

render_divider()
render_section_header('Executive Risk Overview', 'A real-time read on organizational compliance health.', '🧭')
g1, g2 = st.columns(2)
with g1:
    render_score_gauge(summary)
with g2:
    render_compliance_donut(summary)

render_section_header('Control Performance by Category', 'Where the organization is strong versus exposed.', '📈')
render_category_bar(summary['results'])

render_section_header('Risk Exposure by Severity', 'Failed controls grouped by how much risk they carry.', '📛')
render_severity_chart(summary['results'])

render_divider()
render_section_header('Security Alerts', 'Detected issues based on current system posture.', '🚨')
render_alerts(summary['alerts'])

render_section_header('Recent Audit Activity', 'Latest login and access activity from the audit log.', '📝')
audit_lines = read_audit_log(limit=10)
if audit_lines:
    st.dataframe(pd.DataFrame({'Recent Events': audit_lines}), use_container_width=True, hide_index=True)
else:
    st.info('No audit log activity recorded yet.')

render_divider()
render_section_header('Compliance Findings', 'Detailed findings with evidence and recommended action.', '🔍')
render_findings_cards(summary['results'], limit=6)

render_divider()
if st.button('Logout'):
    logout()
    st.rerun()
