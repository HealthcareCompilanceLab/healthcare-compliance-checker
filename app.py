from pathlib import Path

import streamlit as st

from auth import authenticate_user, initialize_session, logout, user_has_access
from utils import (
    append_audit_log,
    apply_custom_style,
    compute_compliance,
    get_awareness_role_keys,
    get_max_widgets_for_session,
    get_session_hours,
    initialize_awareness_session,
    load_json,
    prioritize_awareness_widgets,
    render_alerts,
    render_awareness_widget,
    render_hero,
    render_sidebar,
    render_smart_awareness_nudge,
    render_system_overview,
)

st.set_page_config(page_title="Healthcare Compliance App", page_icon="🏥", layout="wide")
apply_custom_style()

BASE_DIR = Path(__file__).resolve().parent
EMPLOYEE_FILE = BASE_DIR / "employees.json"
CONTROL_FILE = BASE_DIR / "control_bank.json"
SYSTEM_FILE = BASE_DIR / "system_data.json"

initialize_session()
employees = load_json(EMPLOYEE_FILE)
controls = load_json(CONTROL_FILE)
system = load_json(SYSTEM_FILE)
summary = compute_compliance(controls, system)

render_sidebar(st.session_state.user if st.session_state.user else None, summary, system)

render_hero(
    "Healthcare Security Command Center",
    "Real-time compliance visibility, workforce security posture, and infrastructure risk monitoring for healthcare environments.",
    "Secure Monitoring Active",
)

AWARENESS_WIDGETS = {
    "staff": {
        "label": "Healthcare Staff",
        "widgets": [
            {
                "title": "Phishing Awareness",
                "status": "Warning",
                "message": "Be careful with urgent emails, unknown links, fake login pages, and unexpected attachments.",
                "action": "Do not click suspicious links. Report suspicious emails or messages to IT.",
                "compliance_area": "Security Awareness / Incident Reporting",
            },
            {
                "title": "Strong Passwords & MFA",
                "status": "Important",
                "message": "Strong passwords and multi-factor authentication help protect patient records if a password is stolen.",
                "action": "Use unique passwords and approve MFA prompts only when you started the login.",
                "compliance_area": "Access Control / Authentication",
            },
            {
                "title": "Secure PHI Handling",
                "status": "Critical",
                "message": "Patient information should only be accessed and shared for approved work purposes.",
                "action": "Use approved systems only. Do not send PHI through personal email, texts, or unauthorized apps.",
                "compliance_area": "PHI Protection / Privacy",
            },
            {
                "title": "Incident Reporting",
                "status": "Action Required",
                "message": "Early reporting helps IT contain phishing, malware, account misuse, and privacy incidents.",
                "action": "Report strange pop-ups, suspicious access, missing files, or accidental PHI exposure right away.",
                "compliance_area": "Incident Response / Breach Prevention",
            },
        ],
    },
    "it": {
        "label": "IT Administrator",
        "widgets": [
            {
                "title": "MFA Enforcement Status",
                "status": "Critical",
                "message": "Privileged and remote-access accounts should have MFA enforced.",
                "action": "Review accounts without MFA and apply conditional access or equivalent enforcement policies.",
                "compliance_area": "Access Control / Authentication Evidence",
            },
            {
                "title": "Privileged Account Risk",
                "status": "Warning",
                "message": "Admin accounts create higher risk if they are inactive, shared, over-permissioned, or missing MFA.",
                "action": "Review admin accounts, remove unnecessary privileges, and disable inactive accounts.",
                "compliance_area": "Least Privilege / Identity Governance",
            },
            {
                "title": "Suspicious Access Alerts",
                "status": "Monitor",
                "message": "Repeated failed logins, unusual locations, and unfamiliar devices may indicate account compromise.",
                "action": "Investigate abnormal logins and document evidence for incident response.",
                "compliance_area": "Monitoring / Audit Controls",
            },
            {
                "title": "Configuration Gaps",
                "status": "Review",
                "message": "Weak password rules, disabled logging, missing TLS, and unpatched systems increase healthcare risk.",
                "action": "Prioritize configuration gaps by severity and document remediation actions.",
                "compliance_area": "Technical Safeguards / Risk Management",
            },
        ],
    },
    "compliance": {
        "label": "Compliance Officer",
        "widgets": [
            {
                "title": "Training Completion",
                "status": "Track",
                "message": "Cybersecurity awareness training should be completed and documented for all workforce members.",
                "action": "Follow up with incomplete users or departments and keep completion records.",
                "compliance_area": "Security Awareness Training",
            },
            {
                "title": "Missing Evidence",
                "status": "Warning",
                "message": "Controls are harder to defend during an audit when evidence is missing or outdated.",
                "action": "Collect evidence for MFA, access reviews, logging, backup testing, and policy acknowledgements.",
                "compliance_area": "Audit Evidence / Control Validation",
            },
            {
                "title": "Audit Readiness",
                "status": "Review",
                "message": "Audit readiness depends on control status, evidence quality, policy review, and remediation progress.",
                "action": "Review failed controls and confirm each risk has an owner, deadline, and remediation note.",
                "compliance_area": "Compliance Reporting / Governance",
            },
        ],
    },
}


def get_popup_widget(user, summary_data):
    role_keys = get_awareness_role_keys(user, user_has_access)
    visible_widgets = [w for key in role_keys for w in AWARENESS_WIDGETS[key]["widgets"]]
    risk_level = summary_data["overall"]
    common_mistakes = st.session_state.get("common_security_mistakes", 0)
    audit_log_issues = st.session_state.get("audit_log_issues", 1 if summary_data["alerts"] else 0)

    max_widgets = get_max_widgets_for_session(
        role_keys,
        risk_level,
        get_session_hours(),
        common_mistakes,
        audit_log_issues,
    )

    prioritized = []
    for key in role_keys:
        prioritized.extend(
            prioritize_awareness_widgets(
                AWARENESS_WIDGETS[key]["widgets"],
                key,
                risk_level,
                common_mistakes,
                audit_log_issues,
            )
        )

    seen = set()
    ordered = []
    for widget in prioritized:
        if (
            widget["title"] not in seen
            and widget["title"] not in st.session_state.get("dismissed_awareness_widgets", [])
        ):
            ordered.append(widget)
            seen.add(widget["title"])

    return role_keys, visible_widgets, max_widgets, ordered[0] if ordered else None


role_keys = []
visible_widgets = []
max_widgets = 0
popup_widget = None

if st.session_state.logged_in and st.session_state.user:
    initialize_awareness_session(st.session_state.user)
    role_keys, visible_widgets, max_widgets, popup_widget = get_popup_widget(
        st.session_state.user, summary
    )

    if (
        st.session_state.get("show_awareness_popup", False)
        and popup_widget
        and st.session_state.get("awareness_widgets_shown", 0) < max_widgets
    ):

        @st.dialog("Cybersecurity Awareness Reminder")
        def awareness_popup():
            st.write(
                "This login-based popup shows one targeted awareness widget based on the user's role, session conditions, and current compliance risk."
            )
            render_smart_awareness_nudge(
                popup_widget,
                st.session_state.get("awareness_widgets_shown", 0),
                max_widgets,
            )
            st.caption(
                f"Visible roles: {', '.join(role_keys)} • Available widgets: {len(visible_widgets)}"
            )

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Acknowledge", key=f"popup_ack_{popup_widget['title']}"):
                    dismissed = st.session_state.get("dismissed_awareness_widgets", [])
                    if popup_widget["title"] not in dismissed:
                        dismissed.append(popup_widget["title"])
                        st.session_state.dismissed_awareness_widgets = dismissed

                    st.session_state.awareness_widgets_shown = (
                        st.session_state.get("awareness_widgets_shown", 0) + 1
                    )
                    st.session_state.show_awareness_popup = False
                    st.rerun()

            with c2:
                if st.button("Dismiss for now", key=f"popup_close_{popup_widget['title']}"):
                    st.session_state.show_awareness_popup = False
                    st.rerun()

        awareness_popup()

if not st.session_state.logged_in:
    st.markdown(
        """
    <div class="hc-card">
        <div class="hc-title" style="font-size:24px;">Employee Login</div>
        <div class="hc-subtitle">Access your dashboard using your Job ID and password.</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        job_id = st.text_input("Job ID")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        user = authenticate_user(job_id, password, employees)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            initialize_awareness_session(user)
            st.session_state.show_awareness_popup = True
            append_audit_log("LOGIN", "SUCCESS", user=user)
            st.success(f"Welcome, {user['name']} ({user['role']})")
            st.rerun()
        else:
            append_audit_log(
                "LOGIN",
                "FAILED",
                attempted_job_id=job_id,
                note="Invalid credentials",
            )
            st.error("Invalid Job ID or password.")

    st.markdown(
        """
    <div class="hc-card">
        <div class="hc-card-title">Demo Accounts</div>
        <div class="hc-subtitle">
            <p><strong>EMP001 / admin123</strong> — Admin</p>
            <p><strong>EMP002 / itsecure123</strong> — IT Security</p>
            <p><strong>EMP003 / staff123</strong> — Healthcare Staff</p>
            <p><strong>EMP004 / compliance123</strong> — Compliance Officer</p>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

else:
    user = st.session_state.user
    initialize_awareness_session(user)

    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown(
            f"""
        <div class="hc-card">
            <div class="hc-title" style="font-size:24px;">Welcome, {user['name']}</div>
            <div class="hc-subtitle">
                <strong>Job ID:</strong> {user['job_id']}<br>
                <strong>Role:</strong> {user['role']}<br>
                <strong>Department:</strong> {user['department']}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with c2:
        st.write("")
        st.write("")
        if st.button("Logout"):
            append_audit_log("LOGOUT", "SUCCESS", user=user)
            logout()
            st.rerun()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Compliance Score", f"{summary['percent']:.2f}%")
    col2.metric("Risk Level", summary["overall"])
    col3.metric("Passed Controls", summary["passed"])
    col4.metric("Failed Controls", summary["failed"])

    risk_class = (
        "hc-low"
        if summary["overall"] == "LOW RISK"
        else "hc-medium"
        if summary["overall"] == "MEDIUM RISK"
        else "hc-high"
    )

    st.markdown(
        f"""
    <div class="hc-card">
        <div class="hc-card-title">Role-based Access</div>
        <div class="hc-subtitle">{', '.join(user.get('access', []))}</div>
        <br>
        <div class="hc-card-title">Current Risk Assessment</div>
        <div class="{risk_class}" style="font-size:28px;">{summary['overall']}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_system_overview(system)

    st.markdown("### Security Alerts")
    render_alerts(summary["alerts"])

    st.markdown("### What this role can access")
    if user_has_access(user, "admin"):
        st.markdown(
            '<div class="hc-success">Full access to compliance, alerts, employee views, and system data.</div>',
            unsafe_allow_html=True,
        )
    elif user_has_access(user, "it"):
        st.markdown(
            '<div class="hc-success">Access to security controls, alerts, attack indicators, and remediation data.</div>',
            unsafe_allow_html=True,
        )
    elif user_has_access(user, "staff"):
        st.markdown(
            '<div class="hc-success">Access to staff audit questions and limited dashboard summary.</div>',
            unsafe_allow_html=True,
        )
    elif user_has_access(user, "compliance"):
        st.markdown(
            '<div class="hc-success">Access to compliance mappings, control status, and reporting summaries.</div>',
            unsafe_allow_html=True,
        )

    with st.expander("Awareness widget library", expanded=False):
        st.caption(
            "This section lets users review all awareness widgets without needing the popup to appear again."
        )
        for key in role_keys:
            st.markdown(f"### {AWARENESS_WIDGETS[key]['label']}")
            for widget in prioritize_awareness_widgets(
                AWARENESS_WIDGETS[key]["widgets"],
                key,
                summary["overall"],
                st.session_state.get("common_security_mistakes", 0),
                st.session_state.get("audit_log_issues", 0),
            ):
                render_awareness_widget(widget)