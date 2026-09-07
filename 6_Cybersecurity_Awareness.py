from datetime import datetime

import streamlit as st

from auth import initialize_session, logout, require_any_access, user_has_access
from utils import (
    apply_custom_style,
    get_awareness_role_keys,
    get_max_widgets_for_session,
    get_session_hours,
    initialize_awareness_session,
    prioritize_awareness_widgets,
    render_awareness_widget,
    render_divider,
    render_hero,
    render_kpi_card,
    render_section_header,
    render_sidebar,
    render_smart_awareness_nudge,
)

st.set_page_config(page_title="Cybersecurity Awareness", page_icon="🧠", layout="wide")
apply_custom_style()
initialize_session()
require_any_access(["admin", "it", "staff", "compliance"])

user = st.session_state.user
initialize_awareness_session(user)
render_sidebar(user, None, None)

render_hero(
    "Cybersecurity Awareness Widgets",
    "Role-based security guidance for healthcare staff, IT administrators, and compliance officers.",
    "Awareness Mode",
)

AWARENESS_WIDGETS = {
    "staff": {
        "label": "Healthcare Staff",
        "description": "Plain-language reminders for protecting patient information during daily clinical work.",
        "widgets": [
            {"title": "Phishing Awareness", "status": "Warning", "message": "Be careful with urgent emails, unknown links, fake login pages, and unexpected attachments.", "action": "Do not click suspicious links. Report suspicious emails or messages to IT.", "compliance_area": "Security Awareness / Incident Reporting"},
            {"title": "Strong Passwords & MFA", "status": "Important", "message": "Strong passwords and multi-factor authentication help protect patient records if a password is stolen.", "action": "Use unique passwords and approve MFA prompts only when you started the login.", "compliance_area": "Access Control / Authentication"},
            {"title": "Secure PHI Handling", "status": "Critical", "message": "Patient information should only be accessed and shared for approved work purposes.", "action": "Use approved systems only. Do not send PHI through personal email, texts, or unauthorized apps.", "compliance_area": "PHI Protection / Privacy"},
            {"title": "Device Protection", "status": "Reminder", "message": "Unlocked workstations, shared accounts, and lost devices can expose patient information.", "action": "Lock screens when stepping away and report lost or suspicious devices immediately.", "compliance_area": "Workstation Security / Device Safeguards"},
            {"title": "Incident Reporting", "status": "Action Required", "message": "Early reporting helps IT contain phishing, malware, account misuse, and privacy incidents.", "action": "Report strange pop-ups, suspicious access, missing files, or accidental PHI exposure right away.", "compliance_area": "Incident Response / Breach Prevention"},
            {"title": "Ransomware Awareness", "status": "Critical", "message": "Ransomware often spreads through a clicked link or infected attachment, then encrypts patient records and clinical systems.", "action": "If files won't open or a ransom note appears, disconnect the device from the network and notify IT immediately.", "compliance_area": "Incident Response / Malware Containment", "mitre_id": "T1486"},
            {"title": "Social Engineering & Vishing", "status": "Warning", "message": "Attackers impersonate IT support or coworkers by phone or text to pressure staff into resetting passwords or approving MFA prompts.", "action": "Verify unexpected credential or MFA requests through a known internal channel before acting.", "compliance_area": "Security Awareness / Social Engineering Defense", "mitre_id": "T1566"},
            {"title": "Telehealth & Video Visit Security", "status": "Important", "message": "Telehealth sessions can expose PHI if joined from unapproved apps, public Wi-Fi, or shared devices.", "action": "Use only approved telehealth platforms and confirm patient identity before discussing records.", "compliance_area": "PHI Protection / Remote Care Delivery"},
            {"title": "Physical Security & Badge Tailgating", "status": "Reminder", "message": "Letting someone follow you into a restricted area without their own badge can expose patient records or systems.", "action": "Do not hold secure doors for unbadged individuals; direct them to reception or security.", "compliance_area": "Physical Safeguards / Facility Access Control"},
        ],
    },
    "it": {
        "label": "IT Administrator",
        "description": "Technical security awareness and evidence-based findings for remediation work.",
        "widgets": [
            {"title": "MFA Enforcement Status", "status": "Critical", "message": "Privileged and remote-access accounts should have MFA enforced.", "action": "Review accounts without MFA and apply conditional access or equivalent enforcement policies.", "compliance_area": "Access Control / Authentication Evidence"},
            {"title": "Privileged Account Risk", "status": "Warning", "message": "Admin accounts create higher risk if they are inactive, shared, over-permissioned, or missing MFA.", "action": "Review admin accounts, remove unnecessary privileges, and disable inactive accounts.", "compliance_area": "Least Privilege / Identity Governance"},
            {"title": "Suspicious Access Alerts", "status": "Monitor", "message": "Repeated failed logins, unusual locations, and unfamiliar devices may indicate account compromise.", "action": "Investigate abnormal logins and document evidence for incident response.", "compliance_area": "Monitoring / Audit Controls"},
            {"title": "Audit Log Retention", "status": "Evidence Needed", "message": "Audit logs support investigations, access reviews, and compliance reporting.", "action": "Confirm logging is enabled and retention settings meet organizational policy.", "compliance_area": "Audit Controls / Evidence Retention"},
            {"title": "Backup Integrity", "status": "Warning", "message": "Backups must be protected, encrypted, recent, and tested to reduce ransomware impact.", "action": "Validate backup encryption, restore testing, and backup schedule evidence.", "compliance_area": "Contingency Planning / Data Recovery"},
            {"title": "Configuration Gaps", "status": "Review", "message": "Weak password rules, disabled logging, missing TLS, and unpatched systems increase healthcare risk.", "action": "Prioritize configuration gaps by severity and document remediation actions.", "compliance_area": "Technical Safeguards / Risk Management"},
            {"title": "Vulnerability & Patch Management", "status": "Critical", "message": "Unpatched internet-facing systems and outdated software are among the most common entry points into healthcare networks.", "action": "Maintain a patch cadence for critical CVEs and prioritize internet-facing and EHR-adjacent systems.", "compliance_area": "Vulnerability Management / Technical Safeguards", "mitre_id": "T1190"},
            {"title": "Ransomware Containment Readiness", "status": "Critical", "message": "Recovery depends on network segmentation, offline/immutable backups, and a tested isolation procedure.", "action": "Validate backup isolation, confirm network segmentation, and rehearse the containment runbook.", "compliance_area": "Contingency Planning / Ransomware Resilience", "mitre_id": "T1486"},
            {"title": "Medical Device / IoT Segmentation", "status": "Warning", "message": "Connected medical devices often run outdated firmware and cannot be patched like standard endpoints.", "action": "Place clinical IoT and medical devices on segmented VLANs with restricted traffic and anomaly monitoring.", "compliance_area": "Network Security / Medical Device Risk", "mitre_id": "T1200"},
            {"title": "Cloud / SaaS Shadow IT Risk", "status": "Review", "message": "Unapproved cloud storage or messaging apps used to move patient data create untracked, unencrypted copies of PHI.", "action": "Inventory sanctioned cloud services and route data-sharing needs through approved platforms.", "compliance_area": "Cloud Security / Data Governance", "mitre_id": "T1567"},
            {"title": "Zero Trust Access Review", "status": "Monitor", "message": "Standing, always-on privileged access increases blast radius if a credential is compromised.", "action": "Move toward just-in-time privileged access and default-deny network policies where feasible.", "compliance_area": "Access Control / Identity Governance"},
        ],
    },
    "compliance": {
        "label": "Compliance Officer",
        "description": "Summary-level awareness for training, evidence collection, and audit readiness.",
        "widgets": [
            {"title": "Training Completion", "status": "Track", "message": "Cybersecurity awareness training should be completed and documented for all workforce members.", "action": "Follow up with incomplete users or departments and keep completion records.", "compliance_area": "Security Awareness Training"},
            {"title": "Missing Evidence", "status": "Warning", "message": "Controls are harder to defend during an audit when evidence is missing or outdated.", "action": "Collect evidence for MFA, access reviews, logging, backup testing, and policy acknowledgements.", "compliance_area": "Audit Evidence / Control Validation"},
            {"title": "Audit Readiness", "status": "Review", "message": "Audit readiness depends on control status, evidence quality, policy review, and remediation progress.", "action": "Review failed controls and confirm each risk has an owner, deadline, and remediation note.", "compliance_area": "Compliance Reporting / Governance"},
            {"title": "Overall Compliance Posture", "status": "Monitor", "message": "A single score helps summarize risk, but failed high-risk controls should be reviewed separately.", "action": "Use the compliance score with detailed findings to prioritize remediation.", "compliance_area": "Risk Management / Executive Reporting"},
            {"title": "Policy Review Status", "status": "Reminder", "message": "Security and privacy policies should be reviewed regularly and updated when workflows change.", "action": "Check the last policy review date and document updates or approvals.", "compliance_area": "Policy Governance / Documentation"},
            {"title": "Vendor & Business Associate Risk", "status": "Warning", "message": "Third-party vendors with access to PHI extend the organization's attack surface and must be covered by signed BAAs.", "action": "Maintain a vendor inventory, confirm signed BAAs are on file, and schedule reviews for high-risk vendors.", "compliance_area": "Third-Party Risk / Business Associate Management"},
            {"title": "Breach Notification Timeliness", "status": "Critical", "message": "Breach notification obligations are time-bound, and missed deadlines create regulatory exposure.", "action": "Confirm the breach-notification workflow, owners, and required timelines are documented and rehearsed.", "compliance_area": "Breach Notification / Regulatory Reporting"},
            {"title": "Third-Party Risk Assessments", "status": "Review", "message": "Point-in-time vendor onboarding checks lose accuracy as vendor environments change.", "action": "Re-assess high-risk vendors on a recurring schedule and document findings.", "compliance_area": "Vendor Governance / Risk Management"},
            {"title": "Regulatory Change Tracking", "status": "Track", "message": "HIPAA, state privacy laws, and payer requirements evolve, and outdated policies can fall out of alignment.", "action": "Assign ownership for monitoring regulatory updates and log policy revisions with review dates.", "compliance_area": "Policy Governance / Regulatory Alignment"},
        ],
    },
}

role_keys = get_awareness_role_keys(user, user_has_access)
visible_widgets = [w for key in role_keys for w in AWARENESS_WIDGETS[key]["widgets"]]

c1, c2, c3 = st.columns(3)
with c1:
    render_kpi_card("User Role", user.get("role", "Unknown"), "Dashboard guidance is role-based", "info", "🧑‍⚕️")
with c2:
    render_kpi_card("Widgets Available", str(len(visible_widgets)), "Awareness items shown to this user", "success", "🧠")
with c3:
    render_kpi_card("Primary Focus", ", ".join([AWARENESS_WIDGETS[k]["label"] for k in role_keys]), "Based on access permissions", "warning", "🎯")

render_divider()

if len(role_keys) > 1:
    selected_label = st.selectbox("Select awareness view", [AWARENESS_WIDGETS[k]["label"] for k in role_keys])
    selected_key = next(k for k in role_keys if AWARENESS_WIDGETS[k]["label"] == selected_label)
else:
    selected_key = role_keys[0]

with st.expander("Smart widget frequency controls", expanded=False):
    st.markdown("These controls demonstrate how the app avoids annoying pop-ups by limiting reminders based on role, session length, risk level, audit-log concerns, and repeated security mistakes.")
    risk_level = st.selectbox("Current risk level", ["LOW RISK", "MEDIUM RISK", "HIGH RISK"], index=0)
    common_mistakes = st.slider("Common security mistakes detected this session", 0, 5, st.session_state.get("common_security_mistakes", 0))
    audit_log_issues = st.slider("Audit-log or evidence issues detected", 0, 5, st.session_state.get("audit_log_issues", 0))
    session_hours = get_session_hours()
    manual_hours = st.number_input("Session length override for demo/testing", min_value=0.0, max_value=12.0, value=float(round(session_hours, 2)), step=0.5)
    st.session_state.common_security_mistakes = common_mistakes
    st.session_state.audit_log_issues = audit_log_issues
    if st.button("Reset awareness reminders for this session"):
        st.session_state.awareness_session_started = datetime.now()
        st.session_state.awareness_widgets_shown = 0
        st.session_state.dismissed_awareness_widgets = []
        st.rerun()

max_widgets_this_session = get_max_widgets_for_session(role_keys, risk_level, manual_hours, common_mistakes, audit_log_issues)
widgets = prioritize_awareness_widgets(AWARENESS_WIDGETS[selected_key]["widgets"], selected_key, risk_level, common_mistakes, audit_log_issues)
available_nudges = [widget for widget in widgets if widget["title"] not in st.session_state.dismissed_awareness_widgets]

render_section_header("Smart Session Awareness Nudge", "Shows only one targeted reminder at a time, with a session limit to prevent pop-up fatigue.", "✦")

if st.session_state.awareness_widgets_shown < max_widgets_this_session and available_nudges:
    current_nudge = available_nudges[0]
    render_smart_awareness_nudge(current_nudge, st.session_state.awareness_widgets_shown, max_widgets_this_session)
    n1, n2 = st.columns([1, 4])
    with n1:
        if st.button("Got it", key=f"dismiss_{current_nudge['title']}"):
            st.session_state.dismissed_awareness_widgets.append(current_nudge["title"])
            st.session_state.awareness_widgets_shown += 1
            st.rerun()
    with n2:
        st.caption("Once dismissed, this reminder will not appear again during the current session.")
else:
    st.markdown('<div class="hc-success">No more awareness nudges are needed for this session. Users can still review the full widget library below.</div>', unsafe_allow_html=True)

render_section_header(f"{AWARENESS_WIDGETS[selected_key]['label']} Awareness Widget Library", AWARENESS_WIDGETS[selected_key]["description"], "▣")
st.caption("The full library is always available for review, but only the smart nudge above appears automatically. This keeps the interface helpful without spamming the user.")

for i in range(0, len(widgets), 2):
    cols = st.columns(2)
    for col, widget in zip(cols, widgets[i:i + 2]):
        with col:
            render_awareness_widget(widget)

render_divider()
if st.button("Logout"):
    logout()
    st.rerun()