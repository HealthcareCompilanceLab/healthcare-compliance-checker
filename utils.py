import json
from datetime import datetime
from pathlib import Path

import streamlit as st

RISK_WEIGHTS = {"High": 3, "Medium": 2, "Low": 1}
AUDIT_DIR = Path(__file__).resolve().parent / "audit_logs"
AUDIT_FILE = AUDIT_DIR / "login_audit_log.txt"


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_compliance(controls, system):
    results = []
    alerts = []
    score = 0
    max_score = 0
    passed = failed = insufficient = 0

    for control in controls:
        field = control["field"]
        risk = control["risk"]
        weight = RISK_WEIGHTS[risk]
        max_score += weight

        if field not in system:
            status = "INSUFFICIENT"
            insufficient += 1
            value = "Not Found"
        else:
            value = system[field]

            if control.get("comparison") == "min":
                status = "COMPLIANT" if value >= control["expected"] else "NON-COMPLIANT"
            else:
                status = "COMPLIANT" if value == control["expected"] else "NON-COMPLIANT"

            if status == "COMPLIANT":
                score += weight
                passed += 1
            else:
                failed += 1

        results.append(
            {
                "id": control.get("id", "N/A"),
                "category": control.get("category", "Uncategorized"),
                "desc": control["description"],
                "status": status,
                "risk": risk,
                "remediation": control["remediation"],
                "evidence": f"{field} = {value}",
            }
        )

    failed_logins = system.get("login_attempts", []).count("failed")

    if failed_logins >= 3:
        alerts.append("Multiple failed login attempts detected")

    if system.get("suspicious_ip_detected"):
        alerts.append("Suspicious IP detected")

    percent = (score / max_score) * 100 if max_score else 0

    if percent >= 80:
        overall = "LOW RISK"
    elif percent >= 50:
        overall = "MEDIUM RISK"
    else:
        overall = "HIGH RISK"

    return {
        "results": results,
        "alerts": alerts,
        "score": score,
        "max_score": max_score,
        "percent": percent,
        "overall": overall,
        "passed": passed,
        "failed": failed,
        "insufficient": insufficient,
    }


def append_audit_log(event_type, status, user=None, attempted_job_id=None, note=""):
    AUDIT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user:
        job_id = user.get("job_id", "N/A")
        name = user.get("name", "Unknown")
        role = user.get("role", "Unknown")
        department = user.get("department", "Unknown")
    else:
        job_id = attempted_job_id or "N/A"
        name = "Unknown"
        role = "Unknown"
        department = "Unknown"

    line = (
        f"[{timestamp}] "
        f"EVENT={event_type} | "
        f"STATUS={status} | "
        f"JOB_ID={job_id} | "
        f"NAME={name} | "
        f"ROLE={role} | "
        f"DEPARTMENT={department}"
    )

    if note:
        line += f" | NOTE={note}"

    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def read_audit_log(limit=None):
    if not AUDIT_FILE.exists():
        return []

    with open(AUDIT_FILE, "r", encoding="utf-8") as f:
        lines = [line.rstrip() for line in f if line.strip()]

    lines = list(reversed(lines))
    return lines[:limit] if limit else lines


def apply_custom_style():
    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@600;700&display=swap');
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(56, 189, 248, 0.16), transparent 24%),
            radial-gradient(circle at top right, rgba(59, 130, 246, 0.12), transparent 28%),
            radial-gradient(circle at bottom right, rgba(14, 165, 233, 0.08), transparent 24%),
            linear-gradient(135deg, #06101f 0%, #0b1324 45%, #111827 100%);
        color: #e5eefc;
        font-family: 'Inter', sans-serif;
    }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1240px; }
    h1, h2, h3 { color: #f8fbff !important; }
    .hc-hero { background: rgba(15, 23, 42, 0.58); border: 1px solid rgba(148, 163, 184, 0.16); backdrop-filter: blur(18px); border-radius: 22px; padding: 24px; box-shadow: 0 16px 40px rgba(0,0,0,0.22); margin-bottom: 24px; }
    .hc-title { font-family: 'Orbitron', sans-serif; font-size: 30px; color: #f8fbff !important; letter-spacing: 0.03em; margin-bottom: 8px; }
    .hc-subtitle { color: #94a3b8 !important; font-size: 14px; line-height: 1.6; }
    .hc-pill { display: inline-block; margin-top: 14px; padding: 10px 16px; border-radius: 999px; background: rgba(34, 197, 94, 0.12); color: #22c55e !important; border: 1px solid rgba(34, 197, 94, 0.34); font-size: 13px; font-weight: 700; }
    .hc-card { background: rgba(15, 23, 42, 0.58); border: 1px solid rgba(148, 163, 184, 0.16); backdrop-filter: blur(16px); border-radius: 18px; padding: 22px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.22); margin-bottom: 18px; }
    .hc-card-title { color: #94a3b8 !important; font-size: 13px; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px; font-weight: 700; }
    .hc-score { font-size: 30px; font-weight: 800; color: #67e8f9 !important; text-shadow: 0 0 18px rgba(103, 232, 249, 0.12); }
    .hc-low { color: #22c55e !important; font-weight: 800; }
    .hc-medium { color: #facc15 !important; font-weight: 800; }
    .hc-high { color: #ef4444 !important; font-weight: 800; }
    .hc-alert { background: rgba(127, 29, 29, 0.30); color: #fecaca !important; padding: 15px; border: 1px solid rgba(248, 113, 113, 0.18); border-radius: 12px; margin-bottom: 12px; }
    .hc-success { background: rgba(22, 53, 28, 0.40); color: #bbf7d0 !important; border: 1px solid rgba(34, 197, 94, 0.18); padding: 15px; border-radius: 12px; margin-bottom: 12px; }
    .hc-info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; margin-top: 8px; margin-bottom: 12px; }
    .hc-mini-card { background: rgba(8, 17, 32, 0.80); border: 1px solid rgba(148, 163, 184, 0.12); border-radius: 16px; padding: 16px; }
    .hc-mini-label { font-size: 12px; color: #94a3b8 !important; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; font-weight: 700; }
    .hc-mini-value { font-size: 24px; font-weight: 800; color: #f8fbff !important; }
    .hc-chip { display: inline-block; padding: 6px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; margin-right: 8px; margin-bottom: 8px; }
    .hc-chip-ok { background: rgba(34, 197, 94, 0.12); color: #22c55e !important; border: 1px solid rgba(34, 197, 94, 0.28); }
    .hc-chip-warn { background: rgba(250, 204, 21, 0.12); color: #facc15 !important; border: 1px solid rgba(250, 204, 21, 0.28); }
    .hc-chip-danger { background: rgba(239, 68, 68, 0.12); color: #ef4444 !important; border: 1px solid rgba(239, 68, 68, 0.28); }
    div[data-testid="stMetric"] { background: rgba(15, 23, 42, 0.58); border: 1px solid rgba(148, 163, 184, 0.16); border-radius: 18px; padding: 18px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.22); }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #07111f 0%, #0a1729 45%, #0b1d33 100%) !important; border-right: 1px solid rgba(56, 189, 248, 0.14) !important; }
    section[data-testid="stSidebar"] > div, div[data-testid="stSidebarContent"] { background: linear-gradient(180deg, #07111f 0%, #0a1729 45%, #0b1d33 100%) !important; }
    .hc-sidebar-brand { background: linear-gradient(180deg, rgba(14, 23, 42, 0.96), rgba(10, 18, 33, 0.92)); border: 1px solid rgba(103, 232, 249, 0.16); border-radius: 18px; padding: 16px; margin-bottom: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.18), inset 0 1px 0 rgba(255,255,255,0.03); }
    .hc-sidebar-brand h2 { font-family: 'Orbitron', sans-serif; color: #67e8f9 !important; font-size: 20px; margin: 0 0 8px 0; letter-spacing: 0.04em; }
    .hc-sidebar-brand p { color: #8ea7c2 !important; font-size: 12px; line-height: 1.55; margin: 0; }
    .hc-sidebar-box { background: rgba(14, 23, 42, 0.78); border: 1px solid rgba(148, 163, 184, 0.11); border-radius: 16px; padding: 14px; margin-bottom: 12px; }
    .hc-sidebar-label { font-size: 11px; color: #7f94ab !important; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; font-weight: 700; }
    .hc-sidebar-value { font-size: 13px; color: #e5eefc !important; font-weight: 600; line-height: 1.55; margin-bottom: 3px; }
    .hc-section-head { display: flex; align-items: center; gap: 14px; margin: 8px 0 18px 0; padding: 14px 16px; border-radius: 16px; background: rgba(10, 18, 33, 0.58); border: 1px solid rgba(148, 163, 184, 0.12); }
    .hc-section-icon { width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, rgba(8,145,178,0.22), rgba(37,99,235,0.22)); color: #67e8f9; font-size: 18px; font-weight: 800; }
    .hc-section-title { font-size: 18px; font-weight: 800; color: #f8fbff; }
    .hc-section-subtitle { font-size: 13px; color: #8ea7c2; margin-top: 2px; }
    .hc-kpi-card { position: relative; overflow: hidden; border-radius: 18px; padding: 18px; margin-bottom: 16px; background: rgba(15, 23, 42, 0.64); border: 1px solid rgba(148, 163, 184, 0.14); box-shadow: 0 12px 28px rgba(0,0,0,0.22); }
    .hc-kpi-title { color: #8ea7c2; font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; }
    .hc-kpi-value { font-size: 30px; font-weight: 800; color: #f8fbff; margin-top: 10px; margin-bottom: 6px; }
    .hc-kpi-subtitle { font-size: 13px; color: #94a3b8; line-height: 1.5; }
    .hc-kpi-info { border-color: rgba(56, 189, 248, 0.16); }
    .hc-kpi-success { border-color: rgba(34, 197, 94, 0.18); }
    .hc-kpi-warning { border-color: rgba(250, 204, 21, 0.18); }
    .hc-kpi-danger { border-color: rgba(239, 68, 68, 0.18); }
    .hc-progress-wrap { margin-bottom: 14px; }
    .hc-progress-label-row { display: flex; justify-content: space-between; align-items: center; color: #dbeafe; font-size: 13px; margin-bottom: 7px; }
    .hc-progress-track { width: 100%; height: 10px; background: rgba(30, 41, 59, 0.75); border: 1px solid rgba(148, 163, 184, 0.10); border-radius: 999px; overflow: hidden; }
    .hc-progress-fill { height: 100%; border-radius: 999px; box-shadow: 0 0 18px rgba(255,255,255,0.08); }
    .hc-bar-info { background: linear-gradient(90deg, #06b6d4, #3b82f6); }
    .hc-bar-success { background: linear-gradient(90deg, #16a34a, #22c55e); }
    .hc-bar-warning { background: linear-gradient(90deg, #eab308, #facc15); }
    .hc-bar-danger { background: linear-gradient(90deg, #dc2626, #ef4444); }
    .hc-finding-card { background: rgba(15, 23, 42, 0.58); border: 1px solid rgba(148, 163, 184, 0.16); border-radius: 18px; padding: 18px; margin-bottom: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.20); }
    .hc-finding-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 14px; }
    .hc-finding-title { font-size: 18px; font-weight: 800; color: #f8fbff; line-height: 1.45; }
    .hc-finding-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
    .hc-finding-box { background: rgba(8, 17, 32, 0.82); border: 1px solid rgba(148, 163, 184, 0.10); border-radius: 14px; padding: 14px; }
    .stButton > button { width: 100%; border-radius: 14px; padding: 0.8rem 1rem; font-weight: 700; border: 1px solid rgba(56, 189, 248, 0.22); background: linear-gradient(90deg, #0891b2, #2563eb); color: white; box-shadow: 0 0 18px rgba(37, 99, 235, 0.16); }
    .stTextInput input, .stSelectbox select { background: rgba(8, 17, 32, 0.92) !important; color: #f8fbff !important; border-radius: 12px !important; }
    .stDataFrame, .stTable { background: rgba(8, 17, 32, 0.58); border-radius: 16px; }
    </style>
    """,
        unsafe_allow_html=True,
    )


def render_hero(title, subtitle, pill_text):
    st.markdown(f"""<div class="hc-hero"><div class="hc-title">{title}</div><div class="hc-subtitle">{subtitle}</div><div class="hc-pill">{pill_text}</div></div>""", unsafe_allow_html=True)


def render_alerts(alerts):
    if alerts:
        for alert in alerts:
            st.markdown(f'<div class="hc-alert">{alert}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="hc-success">No active security alerts detected.</div>', unsafe_allow_html=True)


def render_sidebar(user=None, summary=None, system=None):
    with st.sidebar:
        st.markdown("""<div class="hc-sidebar-brand"><h2>HC DASHBOARD</h2><p>Healthcare security monitoring for compliance posture, workforce awareness, and infrastructure readiness.</p></div>""", unsafe_allow_html=True)
        if user:
            st.markdown(f"""<div class="hc-sidebar-box"><div class="hc-sidebar-label">User</div><div class="hc-sidebar-value">{user.get('name', 'Unknown')}</div><div class="hc-sidebar-value">{user.get('role', 'Unknown')}</div><div class="hc-sidebar-value">{user.get('department', 'Unknown')}</div></div>""", unsafe_allow_html=True)
        if summary:
            st.markdown(f"""<div class="hc-sidebar-box"><div class="hc-sidebar-label">Compliance Snapshot</div><div class="hc-sidebar-value">Score: {summary['percent']:.2f}%</div><div class="hc-sidebar-value">Risk: {summary['overall']}</div><div class="hc-sidebar-value">Passed: {summary['passed']}</div><div class="hc-sidebar-value">Failed: {summary['failed']}</div></div>""", unsafe_allow_html=True)
        if system:
            failed_logins = system.get("login_attempts", []).count("failed")
            suspicious = "Detected" if system.get("suspicious_ip_detected") else "None"
            st.markdown(f"""<div class="hc-sidebar-box"><div class="hc-sidebar-label">System Watch</div><div class="hc-sidebar-value">Failed Logins: {failed_logins}</div><div class="hc-sidebar-value">Suspicious IP: {suspicious}</div><div class="hc-sidebar-value">MFA: {'Enabled' if system.get('mfa_enabled') else 'Disabled'}</div><div class="hc-sidebar-value">TLS: {'Enabled' if system.get('tls_enabled') else 'Disabled'}</div></div>""", unsafe_allow_html=True)


def render_system_overview(system):
    failed_logins = system.get("login_attempts", []).count("failed")
    suspicious = system.get("suspicious_ip_detected", False)
    st.markdown("""<div class="hc-card"><div class="hc-card-title">System Intelligence</div><div class="hc-subtitle">Live technical posture and security control visibility from current system data.</div><div class="hc-info-grid">""", unsafe_allow_html=True)
    cards = [
        ("MFA", "Enabled" if system.get("mfa_enabled") else "Disabled", "hc-low" if system.get("mfa_enabled") else "hc-high"),
        ("TLS / HTTPS", "Enabled" if system.get("tls_enabled") else "Disabled", "hc-low" if system.get("tls_enabled") else "hc-high"),
        ("Audit Logging", "Enabled" if system.get("logging_enabled") else "Disabled", "hc-low" if system.get("logging_enabled") else "hc-high"),
        ("Backup Encryption", "Enabled" if system.get("backup_encrypted") else "Disabled", "hc-low" if system.get("backup_encrypted") else "hc-high"),
        ("Password Length", str(system.get("password_length", "N/A")), "hc-low" if system.get("password_length", 0) >= 8 else "hc-medium"),
        ("Failed Logins", str(failed_logins), "hc-high" if failed_logins >= 3 else "hc-low"),
    ]
    for label, value, cls in cards:
        st.markdown(f"""<div class="hc-mini-card"><div class="hc-mini-label">{label}</div><div class="hc-mini-value {cls}">{value}</div></div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    chips = []
    chips.append('<span class="hc-chip hc-chip-ok">MFA Active</span>' if system.get("mfa_enabled") else '<span class="hc-chip hc-chip-danger">MFA Missing</span>')
    chips.append('<span class="hc-chip hc-chip-ok">TLS Protected</span>' if system.get("tls_enabled") else '<span class="hc-chip hc-chip-danger">TLS Disabled</span>')
    chips.append('<span class="hc-chip hc-chip-ok">Logging On</span>' if system.get("logging_enabled") else '<span class="hc-chip hc-chip-danger">Logging Off</span>')
    chips.append('<span class="hc-chip hc-chip-ok">Encrypted Backups</span>' if system.get("backup_encrypted") else '<span class="hc-chip hc-chip-danger">Backups Unencrypted</span>')
    chips.append('<span class="hc-chip hc-chip-danger">Suspicious IP Detected</span>' if suspicious else '<span class="hc-chip hc-chip-ok">No Suspicious IP</span>')
    chips.append('<span class="hc-chip hc-chip-warn">Password Policy Weak</span>' if system.get("password_length", 0) < 8 else '<span class="hc-chip hc-chip-ok">Password Policy Good</span>')
    st.markdown("".join(chips), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_kpi_card(title, value, subtitle="", tone="info"):
    tone_class = {"info": "hc-kpi-info", "success": "hc-kpi-success", "warning": "hc-kpi-warning", "danger": "hc-kpi-danger"}.get(tone, "hc-kpi-info")
    st.markdown(f"""<div class="hc-kpi-card {tone_class}"><div class="hc-kpi-title">{title}</div><div class="hc-kpi-value">{value}</div><div class="hc-kpi-subtitle">{subtitle}</div></div>""", unsafe_allow_html=True)


def render_section_header(title, subtitle="", icon="◆"):
    st.markdown(f"""<div class="hc-section-head"><div class="hc-section-icon">{icon}</div><div><div class="hc-section-title">{title}</div><div class="hc-section-subtitle">{subtitle}</div></div></div>""", unsafe_allow_html=True)


def render_progress_bar(label, value, tone="info"):
    tone_class = {"info": "hc-bar-info", "success": "hc-bar-success", "warning": "hc-bar-warning", "danger": "hc-bar-danger"}.get(tone, "hc-bar-info")
    safe_value = max(0, min(100, float(value)))
    st.markdown(f"""<div class="hc-progress-wrap"><div class="hc-progress-label-row"><span>{label}</span><span>{safe_value:.0f}%</span></div><div class="hc-progress-track"><div class="hc-progress-fill {tone_class}" style="width:{safe_value}%;"></div></div></div>""", unsafe_allow_html=True)


def render_finding_card(title, status, risk, evidence, remediation):
    risk_class = "hc-low" if str(risk).lower() == "low" else "hc-medium" if str(risk).lower() == "medium" else "hc-high"
    status_tone = "hc-success" if status == "COMPLIANT" else "hc-alert" if status in ["NON-COMPLIANT", "INSUFFICIENT"] else "hc-card"
    st.markdown(f"""<div class="hc-finding-card"><div class="hc-finding-top"><div class="hc-finding-title">{title}</div><div class="{status_tone}" style="padding:8px 12px; border-radius:12px; margin:0;">{status}</div></div><div class="hc-finding-grid"><div class="hc-finding-box"><div class="hc-card-title">Risk</div><div class="{risk_class}" style="font-size:20px;">{risk}</div></div><div class="hc-finding-box"><div class="hc-card-title">Evidence</div><div class="hc-subtitle">{evidence}</div></div><div class="hc-finding-box"><div class="hc-card-title">Remediation</div><div class="hc-subtitle">{remediation}</div></div></div></div>""", unsafe_allow_html=True)


def render_findings_cards(results):
    if not results:
        st.markdown('<div class="hc-success">No findings available.</div>', unsafe_allow_html=True)
        return
    for item in results:
        render_finding_card(item.get("desc", item.get("title", "Finding")), item.get("status", "UNKNOWN"), item.get("risk", "Unknown"), item.get("evidence", "No evidence provided"), item.get("remediation", "No remediation provided"))


def get_awareness_role_keys(user, user_has_access_fn):
    if user_has_access_fn(user, "admin"):
        return ["staff", "it", "compliance"]
    keys = []
    if user_has_access_fn(user, "staff"):
        keys.append("staff")
    if user_has_access_fn(user, "it"):
        keys.append("it")
    if user_has_access_fn(user, "compliance"):
        keys.append("compliance")
    return keys or ["staff"]


def initialize_awareness_session(user):
    user_id = user.get("job_id", "unknown")
    if st.session_state.get("awareness_user_id") != user_id:
        st.session_state.awareness_user_id = user_id
        st.session_state.awareness_session_started = datetime.now()
        st.session_state.awareness_widgets_shown = 0
        st.session_state.dismissed_awareness_widgets = []
        st.session_state.common_security_mistakes = 0
        st.session_state.audit_log_issues = 0
    if "awareness_session_started" not in st.session_state:
        st.session_state.awareness_session_started = datetime.now()
    if "awareness_widgets_shown" not in st.session_state:
        st.session_state.awareness_widgets_shown = 0
    if "dismissed_awareness_widgets" not in st.session_state:
        st.session_state.dismissed_awareness_widgets = []


def get_session_hours():
    elapsed = datetime.now() - st.session_state.awareness_session_started
    return elapsed.total_seconds() / 3600


def get_max_widgets_for_session(role_keys, risk_level, session_hours, common_mistakes, audit_log_issues):
    max_widgets = 1
    if "staff" in role_keys:
        max_widgets = 2
    if "it" in role_keys and risk_level in ["MEDIUM RISK", "HIGH RISK"]:
        max_widgets = max(max_widgets, 2)
    if "compliance" in role_keys and audit_log_issues > 0:
        max_widgets = max(max_widgets, 2)
    if session_hours >= 2:
        max_widgets += 1
    if common_mistakes >= 2 or audit_log_issues >= 2:
        max_widgets += 1
    return min(max_widgets, 3)


def prioritize_awareness_widgets(widgets, role_key, risk_level, common_mistakes, audit_log_issues):
    priority_titles = []
    if role_key == "staff":
        priority_titles = ["Secure PHI Handling", "Phishing Awareness", "Device Protection"] if common_mistakes >= 2 else ["Phishing Awareness", "Strong Passwords & MFA", "Incident Reporting"]
    elif role_key == "it":
        if risk_level == "HIGH RISK":
            priority_titles = ["MFA Enforcement Status", "Configuration Gaps", "Privileged Account Risk"]
        elif audit_log_issues > 0:
            priority_titles = ["Audit Log Retention", "Suspicious Access Alerts", "Backup Integrity"]
        else:
            priority_titles = ["Privileged Account Risk", "Backup Integrity", "Suspicious Access Alerts"]
    elif role_key == "compliance":
        priority_titles = ["Missing Evidence", "Audit Readiness", "Training Completion"] if audit_log_issues > 0 else ["Training Completion", "Policy Review Status", "Overall Compliance Posture"]
    title_rank = {title: index for index, title in enumerate(priority_titles)}
    return sorted(widgets, key=lambda item: title_rank.get(item["title"], 99))


def render_smart_awareness_nudge(widget, shown_count, max_widgets):
    st.markdown(f"""<div class="hc-card" style="border-left: 5px solid #38bdf8;"><div class="hc-card-title">Smart Awareness Reminder: {widget['title']}</div><div class="hc-subtitle"><strong>Status:</strong> {widget['status']}</div><br><div class="hc-subtitle">{widget['message']}</div><div class="hc-subtitle"><strong>Recommended Action:</strong> {widget['action']}</div><div class="hc-subtitle"><strong>Compliance Area:</strong> {widget['compliance_area']}</div><br><div class="hc-subtitle">Shown {shown_count} of {max_widgets} allowed reminder(s) this session.</div></div>""", unsafe_allow_html=True)


def render_awareness_widget(widget):
    st.markdown(f"""<div class="hc-card"><div class="hc-card-title">{widget['title']}</div><div class="hc-subtitle"><strong>Status:</strong> {widget['status']}</div><br><div class="hc-subtitle"><strong>Explanation:</strong> {widget['message']}</div><div class="hc-subtitle"><strong>Recommended Action:</strong> {widget['action']}</div><div class="hc-subtitle"><strong>Compliance Area:</strong> {widget['compliance_area']}</div></div>""", unsafe_allow_html=True)
    
    
def evaluate_contingency_controls(control_bank, system_data):
    findings = []

    for control in control_bank:
        if control.get("category") != "Backup, Recovery and Contingency Planning":
            continue

        field = control.get("field")
        expected = control.get("expected")
        actual = system_data.get(field, "Not Found")

        if field not in system_data:
            status = "INSUFFICIENT"
        else:
            if control.get("comparison") == "min":
                status = "COMPLIANT" if actual >= expected else "NON-COMPLIANT"
            else:
                status = "COMPLIANT" if actual == expected else "NON-COMPLIANT"

        findings.append(
            {
                "id": control.get("id", "N/A"),
                "category": control.get("category", "Uncategorized"),
                "desc": control.get("description", "Contingency control"),
                "status": status,
                "risk": control.get("risk", "Medium"),
                "expected": expected,
                "actual": actual,
                "remediation": control.get("remediation", "No remediation provided."),
                "evidence": f"{field} = {actual}",
                "cia_impact": control.get("cia_impact", []),
                "related_framework": control.get("related_framework", []),
                "plain_language_feedback": control.get(
                    "plain_language_feedback",
                    "No plain-language feedback provided.",
                ),
                "technical_feedback": control.get(
                    "technical_feedback",
                    "No technical feedback provided.",
                ),
            }
        )

    return findings


def summarize_contingency_findings(findings):
    total = len(findings)
    passed = sum(1 for item in findings if item["status"] == "COMPLIANT")
    failed = sum(1 for item in findings if item["status"] == "NON-COMPLIANT")
    insufficient = sum(1 for item in findings if item["status"] == "INSUFFICIENT")
    score = round((passed / total) * 100, 1) if total else 0

    if score >= 80:
        posture = "STRONG"
    elif score >= 50:
        posture = "NEEDS IMPROVEMENT"
    else:
        posture = "HIGH RISK"

    return {
        "total_controls": total,
        "passed_controls": passed,
        "failed_controls": failed,
        "insufficient_controls": insufficient,
        "contingency_score": score,
        "overall_posture": posture,
    }


def render_contingency_section(contingency_findings, contingency_summary):
    render_section_header(
        "Backup, Recovery, and Contingency Planning",
        "This section evaluates backup protection, restore readiness, downtime planning, ransomware recovery, and recovery evidence using simulated system data.",
        "⟳",
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card(
            "Controls Checked",
            str(contingency_summary["total_controls"]),
            "Contingency controls evaluated",
            "info",
        )
    with c2:
        render_kpi_card(
            "Passed",
            str(contingency_summary["passed_controls"]),
            "Controls currently meeting expectations",
            "success",
        )
    with c3:
        render_kpi_card(
            "Failed",
            str(contingency_summary["failed_controls"]),
            "Controls requiring remediation",
            "danger",
        )
    with c4:
        render_kpi_card(
            "Score",
            f"{contingency_summary['contingency_score']:.1f}%",
            contingency_summary["overall_posture"],
            "warning" if contingency_summary["overall_posture"] != "STRONG" else "success",
        )

    render_progress_bar(
        "Contingency Readiness Score",
        contingency_summary["contingency_score"],
        "info",
    )

    if contingency_summary["overall_posture"] == "STRONG":
        st.markdown(
            '<div class="hc-success">Overall contingency posture is strong based on the current simulated data.</div>',
            unsafe_allow_html=True,
        )
    elif contingency_summary["overall_posture"] == "NEEDS IMPROVEMENT":
        st.markdown(
            '<div class="hc-alert" style="background: rgba(120, 53, 15, 0.32); color: #fde68a;">Overall contingency posture needs improvement. Some recovery safeguards are missing or incomplete.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="hc-alert">Overall contingency posture is high risk. Multiple recovery and continuity safeguards are missing.</div>',
            unsafe_allow_html=True,
        )

    for finding in contingency_findings:
        title = f"{finding['id']} - {finding['desc']}"
        with st.expander(f"{title} ({finding['status']})", expanded=False):
            st.write(f"**Risk Level:** {finding['risk']}")
            st.write(f"**Expected Value:** {finding['expected']}")
            st.write(f"**Actual Value:** {finding['actual']}")
            st.write(f"**Evidence:** {finding['evidence']}")

            if finding.get("cia_impact"):
                st.write(f"**CIA Impact:** {', '.join(finding['cia_impact'])}")

            if finding.get("related_framework"):
                st.write(f"**Related Framework:** {', '.join(finding['related_framework'])}")

            st.write(f"**Plain-language feedback:** {finding['plain_language_feedback']}")
            st.write(f"**Technical feedback:** {finding['technical_feedback']}")
            st.write(f"**Recommended remediation:** {finding['remediation']}")