
import streamlit as st
from pathlib import Path
from auth import authenticate_user, initialize_session, logout, user_has_access
from utils import (
    append_audit_log,
    apply_custom_style,
    compute_compliance,
    evaluate_scenarios,
    get_awareness_role_keys,
    get_max_widgets_for_session,
    get_session_hours,
    initialize_awareness_session,
    load_json,
    prioritize_awareness_widgets,
    render_alerts,
    render_awareness_widget,
    render_boot_sequence,
    render_category_bar,
    render_compliance_donut,
    render_divider,
    render_hero,
    render_results_table,
    render_scenario_results,
    render_score_gauge,
    render_score_summary,
    render_section_header,
    render_severity_chart,
    render_sidebar,
    render_smart_awareness_nudge,
    render_system_overview,
)

st.set_page_config(page_title="SENTINEL-HC | Compliance Console", page_icon="🛡️", layout="wide")
apply_custom_style()

if "boot_sequence_shown" not in st.session_state:
    render_boot_sequence()
    st.session_state.boot_sequence_shown = True

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
    "Security Command Center",
    "Live posture for EHR safeguards, incident response, backup recovery, data-integrity testing, and citation-backed awareness guidance.",
    "All Systems Monitored",
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
                "source": "HIPAA Security Rule 45 CFR 164.308(a)(5); NIST SP 800-53 AT-2, AT-3, IR-6",
                "nist_family": "AT – Awareness and Training; IR – Incident Response",
                "reference_note": "Matches advice on phishing awareness and prompt reporting.",
            },
            {
                "title": "Strong Passwords & MFA",
                "status": "Important",
                "message": "Strong passwords and multi-factor authentication help protect patient records if a password is stolen.",
                "action": "Use unique passwords and approve MFA prompts only when you started the login.",
                "compliance_area": "Access Control / Authentication",
                "source": "HIPAA Security Rule 45 CFR 164.312(a); NIST SP 800-53 AC-2, IA-2",
                "nist_family": "AC – Access Control",
                "reference_note": "Matches advice on authentication strength and access protection.",
            },
            {
                "title": "Secure PHI Handling",
                "status": "Critical",
                "message": "Patient information should only be accessed and shared for approved work purposes.",
                "action": "Use approved systems only. Do not send PHI through personal email, texts, or unauthorized apps.",
                "compliance_area": "PHI Protection / Privacy",
                "source": "HIPAA Security Rule 45 CFR 164.312(a), 164.312(e); PHIPA safeguards provisions; NIST SP 800-53 AC-3, SC-8",
                "nist_family": "AC – Access Control; SC – System and Communications Protection",
                "reference_note": "Matches advice on limiting PHI use and approved transmission methods.",
            },
            {
                "title": "Incident Reporting",
                "status": "Action Required",
                "message": "Early reporting helps IT contain phishing, malware, account misuse, and privacy incidents.",
                "action": "Report strange pop-ups, suspicious access, missing files, or accidental PHI exposure right away.",
                "compliance_area": "Incident Response / Breach Prevention",
                "source": "HIPAA Security Rule 45 CFR 164.308(a)(6); NIST SP 800-53 IR-4, IR-6",
                "nist_family": "IR – Incident Response",
                "reference_note": "Matches advice on reporting suspicious events quickly.",
            },
            {
                "title": "Ransomware Awareness",
                "status": "Critical",
                "message": "Ransomware often enters through a clicked link, an infected attachment, or a compromised remote session, then encrypts patient records and clinical systems.",
                "action": "If a screen shows a ransom note or files suddenly won't open, disconnect the device from the network and notify IT immediately — do not restart or try to fix it yourself.",
                "compliance_area": "Incident Response / Malware Containment",
                "source": "HIPAA Security Rule 45 CFR 164.308(a)(6); NIST SP 800-53 IR-4, SI-3",
                "nist_family": "IR – Incident Response; SI – System and Information Integrity",
                "reference_note": "Matches guidance on early containment of ransomware and malware events.",
                "mitre_id": "T1486",
            },
            {
                "title": "Social Engineering & Vishing",
                "status": "Warning",
                "message": "Attackers impersonate IT support, vendors, or coworkers by phone or text to pressure staff into resetting passwords or approving MFA prompts.",
                "action": "Verify any unexpected request for credentials or MFA approval through a known internal channel before acting on it.",
                "compliance_area": "Security Awareness / Social Engineering Defense",
                "source": "HIPAA Security Rule 45 CFR 164.308(a)(5); NIST SP 800-53 AT-2, IA-2",
                "nist_family": "AT – Awareness and Training; IA – Identification and Authentication",
                "reference_note": "Matches advice on verifying identity before granting access or resetting credentials.",
                "mitre_id": "T1566",
            },
            {
                "title": "Telehealth & Video Visit Security",
                "status": "Important",
                "message": "Telehealth sessions can expose PHI if joined from unapproved apps, public Wi-Fi, or shared/unlocked devices.",
                "action": "Use only approved telehealth platforms, confirm patient identity before discussing records, and avoid conducting visits over unsecured networks.",
                "compliance_area": "PHI Protection / Remote Care Delivery",
                "source": "HIPAA Security Rule 45 CFR 164.312(e); NIST SP 800-53 SC-8, AC-17",
                "nist_family": "SC – System and Communications Protection; AC – Access Control",
                "reference_note": "Matches advice on securing remote and telehealth communication channels.",
            },
            {
                "title": "Physical Security & Badge Tailgating",
                "status": "Reminder",
                "message": "Allowing someone to follow you into a restricted clinical or IT area without their own badge can let an unauthorized person reach patient records or systems.",
                "action": "Do not hold secure doors open for unbadged individuals; direct them to reception or security instead.",
                "compliance_area": "Physical Safeguards / Facility Access Control",
                "source": "HIPAA Security Rule 45 CFR 164.310(a); NIST SP 800-53 PE-2, PE-3",
                "nist_family": "PE – Physical and Environmental Protection",
                "reference_note": "Matches advice on controlling physical access to facilities holding PHI.",
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
                "source": "HIPAA Security Rule 45 CFR 164.312(a); NIST SP 800-53 AC-2, IA-2",
                "nist_family": "AC – Access Control",
                "reference_note": "Matches advice on privileged access and stronger authentication.",
            },
            {
                "title": "Privileged Account Risk",
                "status": "Warning",
                "message": "Admin accounts create higher risk if they are inactive, shared, over-permissioned, or missing MFA.",
                "action": "Review admin accounts, remove unnecessary privileges, and disable inactive accounts.",
                "compliance_area": "Least Privilege / Identity Governance",
                "source": "HIPAA Security Rule 45 CFR 164.308(a)(3), 164.312(a); NIST SP 800-53 AC-2, AC-6",
                "nist_family": "AC – Access Control",
                "reference_note": "Matches advice on least privilege and privileged-account review.",
            },
            {
                "title": "Suspicious Access Alerts",
                "status": "Monitor",
                "message": "Repeated failed logins, unusual locations, and unfamiliar devices may indicate account compromise.",
                "action": "Investigate abnormal logins and document evidence for incident response.",
                "compliance_area": "Monitoring / Audit Controls",
                "source": "HIPAA Security Rule 45 CFR 164.312(b); NIST SP 800-53 AU-6, SI-4, IR-4",
                "nist_family": "AU – Audit and Accountability; SI – System and Information Integrity; IR – Incident Response",
                "reference_note": "Matches advice on reviewing alerts and suspicious access events.",
            },
            {
                "title": "Configuration Gaps",
                "status": "Review",
                "message": "Weak password rules, disabled logging, missing TLS, and unpatched systems increase healthcare risk.",
                "action": "Prioritize configuration gaps by severity and document remediation actions.",
                "compliance_area": "Technical Safeguards / Risk Management",
                "source": "HIPAA Security Rule 45 CFR 164.308(a)(1), 164.312(b), 164.312(e); NIST SP 800-53 RA-5, AU-2, SC-8",
                "nist_family": "RA – Risk Assessment; AU – Audit and Accountability; SC – System and Communications Protection",
                "reference_note": "Matches advice on technical safeguards and risk reduction.",
            },
            {
                "title": "Vulnerability & Patch Management",
                "status": "Critical",
                "message": "Unpatched internet-facing systems and outdated software are among the most common entry points into healthcare networks.",
                "action": "Maintain a patch cadence for critical CVEs, prioritize internet-facing and EHR-adjacent systems, and track exceptions with compensating controls.",
                "compliance_area": "Vulnerability Management / Technical Safeguards",
                "source": "HIPAA Security Rule 45 CFR 164.308(a)(1); NIST SP 800-53 RA-5, SI-2",
                "nist_family": "RA – Risk Assessment; SI – System and Information Integrity",
                "reference_note": "Matches advice on identifying and remediating exploitable vulnerabilities.",
                "mitre_id": "T1190",
            },
            {
                "title": "Ransomware Containment Readiness",
                "status": "Critical",
                "message": "Ransomware recovery depends on network segmentation, offline/immutable backups, and a tested isolation procedure so one compromised host cannot encrypt shared clinical storage.",
                "action": "Validate backup isolation, confirm segmentation between clinical and administrative networks, and rehearse the containment runbook.",
                "compliance_area": "Contingency Planning / Ransomware Resilience",
                "source": "HIPAA Security Rule 45 CFR 164.308(a)(7); NIST SP 800-53 CP-9, CP-10, IR-4",
                "nist_family": "CP – Contingency Planning; IR – Incident Response",
                "reference_note": "Matches advice on backup integrity, testing, and rapid containment.",
                "mitre_id": "T1486",
            },
            {
                "title": "Medical Device / IoT Segmentation",
                "status": "Warning",
                "message": "Connected medical devices and IoT equipment often run outdated firmware and cannot be patched like standard endpoints, so they need network isolation instead.",
                "action": "Place clinical IoT and medical devices on segmented VLANs with restricted east-west traffic and monitor for anomalous device behavior.",
                "compliance_area": "Network Security / Medical Device Risk",
                "source": "NIST SP 800-53 SC-7, CM-8; FDA premarket cybersecurity guidance (informative)",
                "nist_family": "SC – System and Communications Protection; CM – Configuration Management",
                "reference_note": "Matches advice on isolating hard-to-patch clinical and IoT devices.",
                "mitre_id": "T1200",
            },
            {
                "title": "Cloud / SaaS Shadow IT Risk",
                "status": "Review",
                "message": "Unapproved cloud storage, messaging apps, or SaaS tools used to move patient data create untracked, unencrypted copies of PHI outside organizational control.",
                "action": "Inventory sanctioned cloud services, block or flag unsanctioned SaaS in use, and route data-sharing needs through approved platforms.",
                "compliance_area": "Cloud Security / Data Governance",
                "source": "HIPAA Security Rule 45 CFR 164.308(a)(1); NIST SP 800-53 CA-3, SC-7",
                "nist_family": "CA – Assessment, Authorization, and Monitoring; SC – System and Communications Protection",
                "reference_note": "Matches advice on tracking and controlling third-party data flows.",
                "mitre_id": "T1567",
            },
            {
                "title": "Zero Trust Access Review",
                "status": "Monitor",
                "message": "Standing, always-on privileged access increases blast radius if any single credential is compromised.",
                "action": "Move toward just-in-time privileged access, continuous verification, and default-deny network policies where feasible.",
                "compliance_area": "Access Control / Identity Governance",
                "source": "NIST SP 800-207 (Zero Trust Architecture); NIST SP 800-53 AC-2, AC-6",
                "nist_family": "AC – Access Control",
                "reference_note": "Matches advice on minimizing standing privilege and continuous verification.",
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
                "source": "HIPAA Security Rule 45 CFR 164.308(a)(5); NIST SP 800-53 AT-2",
                "nist_family": "AT – Awareness and Training",
                "reference_note": "Matches advice on documenting workforce training.",
            },
            {
                "title": "Missing Evidence",
                "status": "Warning",
                "message": "Controls are harder to defend during an audit when evidence is missing or outdated.",
                "action": "Collect evidence for MFA, access reviews, logging, backup testing, and policy acknowledgements.",
                "compliance_area": "Audit Evidence / Control Validation",
                "source": "HIPAA Security Rule 45 CFR 164.308(a)(1), 164.312(b); NIST SP 800-53 AU-2, AU-6, CA-7",
                "nist_family": "AU – Audit and Accountability; CA – Assessment, Authorization, and Monitoring",
                "reference_note": "Matches advice on retaining control evidence and review records.",
            },
            {
                "title": "Audit Readiness",
                "status": "Review",
                "message": "Audit readiness depends on control status, evidence quality, policy review, and remediation progress.",
                "action": "Review failed controls and confirm each risk has an owner, deadline, and remediation note.",
                "compliance_area": "Compliance Reporting / Governance",
                "source": "HIPAA Security Rule 45 CFR 164.308(a)(1); PHIPA safeguards provisions; NIST SP 800-53 CA-7, PM-9",
                "nist_family": "CA – Assessment, Authorization, and Monitoring",
                "reference_note": "Matches advice on governance, tracking, and documented remediation.",
            },
            {
                "title": "Vendor & Business Associate Risk",
                "status": "Warning",
                "message": "Third-party vendors and business associates with access to PHI extend the organization's attack surface and must be covered by signed BAAs and periodic risk review.",
                "action": "Maintain a current vendor inventory, confirm signed BAAs are on file, and schedule periodic security reviews for high-risk vendors.",
                "compliance_area": "Third-Party Risk / Business Associate Management",
                "source": "HIPAA Security Rule 45 CFR 164.308(b); NIST SP 800-53 SA-9, CA-3",
                "nist_family": "SA – System and Services Acquisition; CA – Assessment, Authorization, and Monitoring",
                "reference_note": "Matches advice on managing vendor and business-associate risk.",
            },
            {
                "title": "Breach Notification Timeliness",
                "status": "Critical",
                "message": "Breach notification obligations are time-bound, and missed deadlines create regulatory exposure on top of the underlying incident.",
                "action": "Confirm the breach-notification workflow, owners, and required timelines are documented and rehearsed before an incident occurs.",
                "compliance_area": "Breach Notification / Regulatory Reporting",
                "source": "HIPAA Breach Notification Rule 45 CFR 164.400-414; NIST SP 800-53 IR-6, IR-8",
                "nist_family": "IR – Incident Response",
                "reference_note": "Matches advice on timely, well-documented breach reporting.",
            },
            {
                "title": "Third-Party Risk Assessments",
                "status": "Review",
                "message": "Point-in-time vendor onboarding checks lose accuracy over time as vendor environments and subprocessors change.",
                "action": "Re-assess high-risk vendors on a recurring schedule and document findings alongside the original onboarding review.",
                "compliance_area": "Vendor Governance / Risk Management",
                "source": "HIPAA Security Rule 45 CFR 164.308(a)(1); NIST SP 800-53 CA-7, RA-3",
                "nist_family": "CA – Assessment, Authorization, and Monitoring; RA – Risk Assessment",
                "reference_note": "Matches advice on recurring, documented third-party risk review.",
            },
            {
                "title": "Regulatory Change Tracking",
                "status": "Track",
                "message": "HIPAA, state privacy laws, and payer requirements evolve, and outdated policies can fall out of alignment with current obligations.",
                "action": "Assign ownership for monitoring regulatory updates and confirm policy revisions are logged with review dates.",
                "compliance_area": "Policy Governance / Regulatory Alignment",
                "source": "HIPAA Security Rule 45 CFR 164.316; NIST SP 800-53 PM-1, PM-9",
                "nist_family": "PM – Program Management",
                "reference_note": "Matches advice on keeping policy documentation current with regulatory change.",
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
            popup_widget, st.session_state.get("awareness_widgets_shown", 0), max_widgets
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
    <div class="hc-title" style="font-size:24px;">Secure Employee Access</div>
    <div class="hc-subtitle">Authenticate with your Job ID and password to enter the SENTINEL-HC compliance console.</div>
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

    st.markdown('<div class="hc-card"><div class="hc-card-title">Demo Accounts</div><div class="hc-info-grid">', unsafe_allow_html=True)
    demo_accounts = [
        ("🛡️", "EMP001 / admin123", "Admin"),
        ("💻", "EMP002 / itsecure123", "IT Security"),
        ("🩺", "EMP003 / staff123", "Healthcare Staff"),
        ("📋", "EMP004 / compliance123", "Compliance Officer"),
    ]
    for icon, creds, role in demo_accounts:
        st.markdown(
            f"""
<div class="hc-mini-card">
    <div class="hc-kpi-icon">{icon}</div>
    <div class="hc-mini-label">{role}</div>
    <div class="hc-subtitle" style="margin-top:4px;"><strong>{creds}</strong></div>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown("</div></div>", unsafe_allow_html=True)
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

    render_score_summary(summary)
    render_system_overview(system)

    render_divider()
    render_section_header("Executive Risk Overview", "A live, at-a-glance read on organizational compliance health.", "🧭")
    g1, g2 = st.columns(2)
    with g1:
        render_score_gauge(summary, title="")
    with g2:
        render_compliance_donut(summary, title="")

    render_category_bar(summary["results"], title="Compliance by Category")
    render_severity_chart(summary["results"], title="Risk Exposure by Severity")

    render_divider()
    st.markdown("## Security Alerts")
    render_alerts(summary["alerts"])

    st.markdown("## Access and Visibility")
    if user_has_access(user, "admin"):
        st.markdown(
            '<div class="hc-success">Full access to compliance results, scenarios, awareness widgets, employee views, and system details.</div>',
            unsafe_allow_html=True,
        )
    elif user_has_access(user, "it"):
        st.markdown(
            '<div class="hc-success">Access to technical safeguards, suspicious activity alerts, backup and recovery findings, and remediation guidance.</div>',
            unsafe_allow_html=True,
        )
    elif user_has_access(user, "staff"):
        st.markdown(
            '<div class="hc-success">Access to workforce-facing awareness content, suspicious activity results, and a limited compliance overview.</div>',
            unsafe_allow_html=True,
        )
    elif user_has_access(user, "compliance"):
        st.markdown(
            '<div class="hc-success">Access to control mappings, evidence review, control status, remediation notes, and scenario testing summaries.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("## Compliance Findings")
    render_results_table(summary["results"])

    st.markdown("## Scenario Simulation Lab")
    scenario_results = evaluate_scenarios(controls)
    render_scenario_results(scenario_results)

    with st.expander("Awareness widget library", expanded=False):
        st.caption(
            "Each awareness widget below includes a visible citation block with source, related NIST family, and a short reference note."
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