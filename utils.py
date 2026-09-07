import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ====================== VISUAL THEME CONSTANTS ======================
CHART_FONT = dict(family="JetBrains Mono, monospace", color="#EAF2FF")
CHART_COLORS = {
    "pass": "#12E8C6",
    "fail": "#FF4D6A",
    "insufficient": "#FFB833",
    "high": "#FF4D6A",
    "medium": "#FFB833",
    "low": "#2FE6A0",
    "secondary": "#8B7CFF",
    "accent": "#FF2F9E",
    "grid": "rgba(120,180,220,0.10)",
}

# ====================== PROFESSIONAL CONFIG ======================
RISK_WEIGHTS = {"High": 3, "Medium": 2, "Low": 1}
STATUS_TO_LABEL = {"COMPLIANT": "PASS", "NON-COMPLIANT": "FAIL", "INSUFFICIENT": "FAIL"}

AUDIT_DIR = Path(__file__).resolve().parent / "audit_logs"
AUDIT_FILE = AUDIT_DIR / "login_audit_log.txt"


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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
        f"[{timestamp}] EVENT={event_type} | STATUS={status} | JOB_ID={job_id} | "
        f"NAME={name} | ROLE={role} | DEPARTMENT={department}"
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


def _value_meets_expectation(control, value):
    if control.get("comparison") == "min":
        return value >= control["expected"]
    if control.get("comparison") == "contains_all":
        return all(item in value for item in control["expected"])
    return value == control["expected"]


def _safe_get(system, field, default="Not Found"):
    return system[field] if field in system else default


def _format_evidence(control, system):
    field = control["field"]
    actual = _safe_get(system, field)

    evidence_map = system.get("evidence_inventory", {})
    mapped_evidence = evidence_map.get(field)

    if mapped_evidence:
        return f"{field} = {actual}; evidence: {mapped_evidence}"
    return f"{field} = {actual}"


def _build_finding(control, system):
    field = control["field"]
    if field not in system:
        status = "INSUFFICIENT"
        actual_value = "Not Found"
    else:
        actual_value = system[field]
        status = "COMPLIANT" if _value_meets_expectation(control, actual_value) else "NON-COMPLIANT"

    severity = control.get("risk", "Medium")
    return {
        "id": control.get("id", "N/A"),
        "category": control.get("category", "Uncategorized"),
        "control_name": control.get("control_name", control.get("description", "Control")),
        "desc": control.get("description", "No description provided."),
        "status": status,
        "pass_fail": STATUS_TO_LABEL.get(status, "FAIL"),
        "severity": severity,
        "risk": severity,
        "field": field,
        "expected": control.get("expected", "N/A"),
        "actual": actual_value,
        "evidence": _format_evidence(control, system),
        "plain_language_explanation": control.get(
            "plain_language_feedback",
            "This control explains whether a healthcare safeguard is working in a way that staff can understand.",
        ),
        "technical_explanation": control.get(
            "technical_feedback",
            "This control checks a technical or administrative safeguard against the expected state.",
        ),
        "remediation": control.get("remediation", "Review and correct the failed safeguard."),
        "reference": control.get("reference", "NIST SP 800-53"),
        "nist_family": control.get("nist_family", "General"),
        "related_framework": control.get("related_framework", ["NIST SP 800-53"]),
        "section": control.get("section", "General"),
    }


def generate_alerts(system):
    alerts = []

    failed_logins = system.get("failed_login_count", 0)
    if failed_logins >= 3:
        alerts.append("Multiple failed login attempts detected.")

    if system.get("suspicious_ip_detected"):
        alerts.append("Suspicious IP or unusual source detected.")

    if system.get("after_hours_access"):
        alerts.append("After-hours record access detected.")

    if system.get("unusual_location_access"):
        alerts.append("Unusual location or geolocation mismatch detected.")

    if system.get("excessive_record_access"):
        alerts.append("A user accessed too many PHI records in a short period.")

    if system.get("role_mismatch_detected"):
        alerts.append("Role-based access mismatch detected.")

    if not system.get("tamper_evident_logging", True):
        alerts.append("Tamper-evident logging is disabled.")

    if not system.get("unauthorized_modification_detection", True):
        alerts.append("Unauthorized modification detection is disabled.")

    return alerts


def compute_compliance(controls, system):
    results = []
    score = 0
    max_score = 0
    passed = 0
    failed = 0
    insufficient = 0

    for control in controls:
        finding = _build_finding(control, system)
        weight = RISK_WEIGHTS.get(finding["severity"], 2)
        max_score += weight

        if finding["status"] == "COMPLIANT":
            score += weight
            passed += 1
        elif finding["status"] == "INSUFFICIENT":
            insufficient += 1
            failed += 1
        else:
            failed += 1

        results.append(finding)

    percent = (score / max_score) * 100 if max_score else 0
    if percent >= 85:
        overall = "LOW RISK"
    elif percent >= 60:
        overall = "MEDIUM RISK"
    else:
        overall = "HIGH RISK"

    return {
        "results": results,
        "alerts": generate_alerts(system),
        "score": score,
        "max_score": max_score,
        "percent": percent,
        "overall": overall,
        "passed": passed,
        "failed": failed,
        "insufficient": insufficient,
    }


def apply_custom_style():
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --void: #040914;
    --panel: rgba(9, 17, 32, 0.66);
    --panel-solid: #0a1526;
    --line: rgba(120, 180, 220, 0.14);
    --primary: #12E8C6;
    --primary-dim: rgba(18, 232, 198, 0.16);
    --secondary: #8B7CFF;
    --secondary-dim: rgba(139, 124, 255, 0.16);
    --pulse: #ff2f9e;
    --success: #2fe6a0;
    --warning: #ffb833;
    --danger: #ff4d6a;
    --text: #eaf4ff;
    --text-dim: #7e93ad;
    --grid: rgba(18, 232, 198, 0.05);
}

/* ================= BASE / ATMOSPHERE ================= */
.stApp {
    background:
        repeating-linear-gradient(0deg, var(--grid) 0px, transparent 1px, transparent 42px, var(--grid) 43px),
        repeating-linear-gradient(90deg, var(--grid) 0px, transparent 1px, transparent 42px, var(--grid) 43px),
        radial-gradient(circle at 12% 8%, rgba(18, 232, 198, 0.12), transparent 30%),
        radial-gradient(circle at 88% 4%, rgba(139, 124, 255, 0.10), transparent 32%),
        radial-gradient(circle at 50% 100%, rgba(255, 47, 158, 0.05), transparent 40%),
        linear-gradient(160deg, #030711 0%, #050c1a 45%, #070f1e 100%);
    color: var(--text);
    font-family: 'Inter', sans-serif;
}
.block-container { padding-top: 1.6rem; padding-bottom: 2.5rem; max-width: 1300px; }
h1, h2, h3, h4 { color: var(--text) !important; font-family: 'Inter', sans-serif; }
::selection { background: var(--primary-dim); color: var(--primary); }

/* Thin animated top accent across the whole app */
.stApp::before {
    content: "";
    position: fixed; top: 0; left: 0; right: 0; height: 2px; z-index: 999999;
    background: linear-gradient(90deg, transparent, var(--primary), var(--secondary), var(--pulse), transparent);
    background-size: 200% 100%;
    animation: hc-topline 7s linear infinite;
    opacity: 0.85;
}
@keyframes hc-topline { 0% { background-position: 0% 0; } 100% { background-position: 200% 0; } }

/* ================= PANELS ================= */
.hc-hero, .hc-card, .hc-kpi-card, .hc-finding-card {
    background: var(--panel);
    border: 1px solid var(--line);
    backdrop-filter: blur(20px);
    border-radius: 14px;
    box-shadow: 0 18px 44px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255,255,255,0.03);
    position: relative;
}
.hc-hero { padding: 28px 30px; margin-bottom: 22px; overflow: hidden; }
.hc-card { padding: 20px 22px; margin-bottom: 16px; }

/* corner-bracket "HUD" styling on hero + cards */
.hc-hero::after, .hc-card::after {
    content: ""; position: absolute; top: 10px; right: 10px; width: 14px; height: 14px;
    border-top: 2px solid rgba(18, 232, 198, 0.45); border-right: 2px solid rgba(18, 232, 198, 0.45);
    opacity: 0.7; pointer-events: none;
}

.hc-title {
    font-family: 'Orbitron', sans-serif;
    font-weight: 700;
    font-size: 28px;
    color: var(--text) !important;
    letter-spacing: 0.02em;
    margin-bottom: 8px;
    text-shadow: 0 0 24px rgba(18, 232, 198, 0.25);
}
.hc-subtitle { color: var(--text-dim) !important; font-size: 13.5px; line-height: 1.65; }

.hc-pill {
    display: inline-flex; align-items: center; gap: 8px;
    margin-top: 16px;
    padding: 8px 16px;
    border-radius: 999px;
    background: var(--primary-dim);
    color: var(--primary) !important;
    border: 1px solid rgba(18, 232, 198, 0.35);
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.hc-pill::before {
    content: ""; width: 7px; height: 7px; border-radius: 50%;
    background: var(--primary); box-shadow: 0 0 10px var(--primary);
    animation: hc-dot-pulse 1.6s ease-in-out infinite;
}
@keyframes hc-dot-pulse { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.7); } }

.hc-card-title {
    color: var(--text-dim) !important;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 12px;
    font-weight: 600;
}
.hc-low { color: var(--success) !important; font-weight: 800; }
.hc-medium { color: var(--warning) !important; font-weight: 800; }
.hc-high { color: var(--danger) !important; font-weight: 800; }

.hc-alert {
    background: linear-gradient(90deg, rgba(255, 77, 106, 0.14), rgba(255, 77, 106, 0.04));
    color: #ffc7d1 !important;
    padding: 14px 16px;
    border: 1px solid rgba(255, 77, 106, 0.28);
    border-left: 3px solid var(--danger);
    border-radius: 10px;
    margin-bottom: 10px;
    font-size: 13.5px;
}
.hc-success {
    background: linear-gradient(90deg, rgba(47, 230, 160, 0.14), rgba(47, 230, 160, 0.04));
    color: #b9f8dd !important;
    border: 1px solid rgba(47, 230, 160, 0.26);
    border-left: 3px solid var(--success);
    padding: 14px 16px;
    border-radius: 10px;
    margin-bottom: 10px;
    font-size: 13.5px;
}
.hc-info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 14px;
    margin-top: 8px;
    margin-bottom: 12px;
}
.hc-mini-card {
    background: rgba(4, 10, 20, 0.75);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 16px;
    transition: border-color 0.2s ease, transform 0.2s ease;
}
.hc-mini-card:hover { border-color: rgba(18, 232, 198, 0.4); transform: translateY(-2px); }
.hc-mini-label {
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-dim) !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
    font-weight: 600;
}
.hc-mini-value { font-size: 22px; font-weight: 700; color: var(--text) !important; font-family: 'JetBrains Mono', monospace; }
.hc-widget-ref {
    margin-top: 12px;
    padding: 10px 12px;
    border-radius: 10px;
    background: rgba(4, 10, 20, 0.7);
    border: 1px solid var(--line);
    border-left: 2px solid var(--secondary);
}

/* ================= BRAND / STATUS ================= */
.hc-brand {
    display: flex; align-items: center; gap: 10px; margin-bottom: 4px;
}
.hc-brand-mark {
    width: 34px; height: 34px; border-radius: 9px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    display: flex; align-items: center; justify-content: center;
    font-size: 17px; box-shadow: 0 0 18px rgba(18, 232, 198, 0.35);
}
.hc-brand-name {
    font-family: 'Orbitron', sans-serif; font-weight: 700; font-size: 16px;
    letter-spacing: 0.05em; color: var(--text) !important; line-height: 1.1;
}
.hc-brand-sub { font-family: 'JetBrains Mono', monospace; font-size: 9.5px; color: var(--text-dim) !important; letter-spacing: 0.14em; text-transform: uppercase; }

.hc-status-row { display: flex; align-items: center; gap: 8px; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-dim); margin-top: 10px; }
.hc-status-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--success); box-shadow: 0 0 8px var(--success); animation: hc-dot-pulse 1.8s ease-in-out infinite; flex-shrink: 0; }
.hc-status-dot.warn { background: var(--warning); box-shadow: 0 0 8px var(--warning); }
.hc-status-dot.crit { background: var(--danger); box-shadow: 0 0 8px var(--danger); }

/* ================= KPI / SCAN ================= */
.hc-hero { position: relative; overflow: hidden; }
.hc-hero::before {
    content: "";
    position: absolute;
    top: 0; left: -140%;
    width: 140%; height: 2px;
    background: linear-gradient(90deg, transparent, var(--primary), transparent);
    animation: hc-scan 5s linear infinite;
    opacity: 0.7;
}
@keyframes hc-scan { 0% { left: -140%; } 100% { left: 100%; } }

.hc-kpi-card {
    transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
    border-top: 2px solid rgba(18, 232, 198, 0.3) !important;
}
.hc-kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 22px 48px rgba(18, 232, 198, 0.14);
    border-color: rgba(18, 232, 198, 0.4) !important;
}
.hc-kpi-icon {
    font-size: 22px;
    margin-bottom: 6px;
    filter: drop-shadow(0 0 8px rgba(18, 232, 198, 0.5));
}

.hc-chip {
    display: inline-block;
    padding: 4px 11px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-left: 6px;
    white-space: nowrap;
}
.hc-chip-high { background: rgba(255, 77, 106, 0.14); color: #ffb0c0; border: 1px solid rgba(255, 77, 106, 0.36); }
.hc-chip-medium { background: rgba(255, 184, 51, 0.13); color: #ffd98a; border: 1px solid rgba(255, 184, 51, 0.32); }
.hc-chip-low { background: rgba(47, 230, 160, 0.13); color: #a8f5d6; border: 1px solid rgba(47, 230, 160, 0.32); }
.hc-chip-neutral { background: rgba(139, 124, 255, 0.13); color: #cabfff; border: 1px solid rgba(139, 124, 255, 0.32); }
.hc-chip-mitre { background: rgba(255, 47, 158, 0.12); color: #ff9ccb; border: 1px solid rgba(255, 47, 158, 0.32); }

.hc-finding-card { border-left: 3px solid rgba(120, 150, 180, 0.3); padding: 18px 20px; }
.hc-finding-high { border-left-color: var(--danger); }
.hc-finding-medium { border-left-color: var(--warning); }
.hc-finding-low { border-left-color: var(--success); }

.hc-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(18, 232, 198, 0.5), rgba(139, 124, 255, 0.3), transparent);
    margin: 28px 0;
    border: none;
}

.hc-badge-row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }

/* ================= EKG / HERO DECORATION ================= */
.hc-ekg-wrap { position: absolute; right: 0; top: 0; bottom: 0; width: 42%; opacity: 0.35; pointer-events: none; }
.hc-ekg-path {
    stroke: var(--primary); stroke-width: 2; fill: none;
    stroke-dasharray: 1000; stroke-dashoffset: 1000;
    animation: hc-ekg-draw 3.4s ease-in-out infinite;
    filter: drop-shadow(0 0 6px rgba(18, 232, 198, 0.6));
}
@keyframes hc-ekg-draw {
    0% { stroke-dashoffset: 1000; }
    60% { stroke-dashoffset: 0; }
    100% { stroke-dashoffset: -1000; }
}

/* ================= BOOT / LOADING SCREEN ================= */
.hc-boot-overlay {
    position: fixed; inset: 0; z-index: 999999;
    background:
        repeating-linear-gradient(0deg, rgba(18,232,198,0.04) 0px, transparent 1px, transparent 40px, rgba(18,232,198,0.04) 41px),
        radial-gradient(circle at 50% 40%, rgba(18, 232, 198, 0.10), transparent 55%),
        #03060d;
    display: flex; align-items: center; justify-content: center; flex-direction: column;
    animation: hc-boot-fade 0.7s ease-out 2.6s forwards;
}
.hc-boot-overlay * { box-sizing: border-box; }
.hc-boot-logo {
    font-family: 'Orbitron', sans-serif; font-weight: 800; font-size: 30px; letter-spacing: 0.12em;
    color: #eaf4ff; text-shadow: 0 0 30px rgba(18, 232, 198, 0.6);
    display: flex; align-items: center; gap: 14px;
}
.hc-boot-logo .hc-boot-cross { color: var(--primary); font-size: 30px; animation: hc-dot-pulse 1.4s ease-in-out infinite; }
.hc-boot-sub { font-family: 'JetBrains Mono', monospace; color: var(--text-dim); font-size: 11.5px; letter-spacing: 0.24em; text-transform: uppercase; margin-top: 10px; }
.hc-boot-bar-track { width: 340px; max-width: 70vw; height: 3px; background: rgba(120,180,220,0.14); border-radius: 999px; margin-top: 28px; overflow: hidden; }
.hc-boot-bar-fill { height: 100%; width: 0%; background: linear-gradient(90deg, var(--primary), var(--secondary)); animation: hc-boot-fill 2.3s ease-in-out forwards; box-shadow: 0 0 12px rgba(18, 232, 198, 0.7); }
@keyframes hc-boot-fill { 0% { width: 0%; } 100% { width: 100%; } }
.hc-boot-lines { margin-top: 18px; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: rgba(18, 232, 198, 0.75); text-align: left; width: 340px; max-width: 70vw; min-height: 90px; }
.hc-boot-lines div { opacity: 0; animation: hc-boot-line-in 0.4s ease forwards; }
.hc-boot-lines div:nth-child(1) { animation-delay: 0.15s; }
.hc-boot-lines div:nth-child(2) { animation-delay: 0.75s; }
.hc-boot-lines div:nth-child(3) { animation-delay: 1.35s; }
.hc-boot-lines div:nth-child(4) { animation-delay: 1.95s; color: #a8f5d6; }
@keyframes hc-boot-line-in { from { opacity: 0; transform: translateY(3px); } to { opacity: 1; transform: translateY(0); } }
@keyframes hc-boot-fade { 0% { opacity: 1; visibility: visible; } 100% { opacity: 0; visibility: hidden; } }

@media (prefers-reduced-motion: reduce) {
    .hc-hero::before, .hc-pill::before, .hc-status-dot, .stApp::before, .hc-ekg-path,
    .hc-boot-bar-fill, .hc-boot-lines div, .hc-boot-logo .hc-boot-cross { animation: none; }
}

[data-testid="stMetric"] {
    background: rgba(6, 12, 22, 0.6);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 14px 16px;
}

/* Streamlit primary buttons -> brand accent */
.stButton > button {
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.04em;
    border-radius: 8px !important;
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_boot_sequence(app_name="SENTINEL-HC", tagline="Healthcare Compliance & Security Operations Platform"):
    """Full-screen animated boot/loading overlay shown once at the start of a session.
    Pure CSS-driven: it paints over the page for ~2.6s while content renders underneath,
    then fades itself out. Safe to call multiple times per session; only render before
    the rest of the page body for the intended effect."""
    st.markdown(
        f"""
<div class="hc-boot-overlay">
    <div class="hc-boot-logo"><span class="hc-boot-cross">▲</span>{app_name}</div>
    <div class="hc-boot-sub">{tagline}</div>
    <div class="hc-boot-bar-track"><div class="hc-boot-bar-fill"></div></div>
    <div class="hc-boot-lines">
        <div>&gt; establishing secure session...</div>
        <div>&gt; loading control framework (HIPAA / NIST 800-53)...</div>
        <div>&gt; verifying encryption &amp; audit modules...</div>
        <div>&gt; compliance engine ready.</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_status_strip(items):
    """items: list of (label, state) where state in {'ok','warn','crit'} maps to dot color."""
    dots_html = ""
    for label, state in items:
        cls = {"ok": "", "warn": "warn", "crit": "crit"}.get(state, "")
        dots_html += f'<div class="hc-status-row"><span class="hc-status-dot {cls}"></span>{label}</div>'
    st.markdown(f'<div>{dots_html}</div>', unsafe_allow_html=True)


def render_hero(title, subtitle, pill_text):
    st.markdown(
        f"""
<div class="hc-hero">
    <div class="hc-ekg-wrap">
        <svg viewBox="0 0 400 120" preserveAspectRatio="none" width="100%" height="100%">
            <polyline class="hc-ekg-path" points="0,60 40,60 55,60 65,20 80,100 95,60 130,60 145,40 160,80 175,60 220,60 235,30 250,90 265,60 400,60" />
        </svg>
    </div>
    <div class="hc-title">{title}</div>
    <div class="hc-subtitle">{subtitle}</div>
    <div class="hc-pill">{pill_text}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_alerts(alerts):
    if alerts:
        for alert in alerts:
            st.markdown(f'<div class="hc-alert">{alert}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="hc-success">No active security alerts detected.</div>', unsafe_allow_html=True)


def render_sidebar(user=None, summary=None, system=None):
    with st.sidebar:
        st.markdown(
            """
<div class="hc-card">
    <div class="hc-brand">
        <div class="hc-brand-mark">🛡️</div>
        <div>
            <div class="hc-brand-name">SENTINEL-HC</div>
            <div class="hc-brand-sub">Compliance Ops Console</div>
        </div>
    </div>
    <div class="hc-subtitle" style="margin-top:10px;">Real-time healthcare security posture, safeguard review, and workforce awareness.</div>
    <div class="hc-status-row"><span class="hc-status-dot"></span>PLATFORM ONLINE · SESSION ENCRYPTED</div>
</div>
""",
            unsafe_allow_html=True,
        )

        if user:
            st.markdown(
                f"""
<div class="hc-card">
    <div class="hc-card-title">Authenticated User</div>
    <div class="hc-subtitle" style="font-size:14px;color:#eaf4ff !important;font-weight:600;">{user.get('name', 'Unknown')}</div>
    <div class="hc-subtitle">{user.get('role', 'Unknown')} · {user.get('department', 'Unknown')}</div>
    <div class="hc-status-row"><span class="hc-status-dot"></span>ACCESS VERIFIED</div>
</div>
""",
                unsafe_allow_html=True,
            )

        if summary:
            risk_state = "ok" if summary["overall"] == "LOW RISK" else "warn" if summary["overall"] == "MEDIUM RISK" else "crit"
            st.markdown(
                f"""
<div class="hc-card">
    <div class="hc-card-title">Compliance Snapshot</div>
    <div class="hc-mini-value" style="font-size:26px;">{summary['percent']:.1f}%</div>
    <div class="hc-status-row"><span class="hc-status-dot {risk_state}"></span>{summary['overall']}</div>
    <div class="hc-subtitle" style="margin-top:10px;">
        Passed: <strong style="color:#a8f5d6;">{summary['passed']}</strong> &nbsp;·&nbsp;
        Failed: <strong style="color:#ffb0c0;">{summary['failed']}</strong>
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

        if system:
            ip_state = "crit" if system.get("suspicious_ip_detected") else "ok"
            mfa_state = "ok" if system.get("mfa_enabled") else "crit"
            audit_state = "ok" if system.get("audit_logging") else "warn"
            st.markdown(
                f"""
<div class="hc-card">
    <div class="hc-card-title">System Watch</div>
    <div class="hc-status-row"><span class="hc-status-dot {ip_state}"></span>Suspicious IP: {'Detected' if system.get('suspicious_ip_detected') else 'Clear'}</div>
    <div class="hc-status-row"><span class="hc-status-dot {mfa_state}"></span>MFA: {'Enabled' if system.get('mfa_enabled') else 'Disabled'}</div>
    <div class="hc-status-row"><span class="hc-status-dot {audit_state}"></span>Audit Logging: {'Enabled' if system.get('audit_logging') else 'Disabled'}</div>
    <div class="hc-status-row"><span class="hc-status-dot {'warn' if system.get('failed_login_count', 0) >= 3 else 'ok'}"></span>Failed Logins: {system.get('failed_login_count', 0)}</div>
</div>
""",
                unsafe_allow_html=True,
            )


def render_system_overview(system):
    cards = [
        ("Encryption at Rest", system.get("encryption_at_rest")),
        ("Encrypted Backups", system.get("encrypted_backups")),
        ("Firewall", system.get("firewall_protection")),
        ("Endpoint Protection", system.get("antivirus_endpoint_protection")),
        ("Audit Logging", system.get("audit_logging")),
        ("Integrity Detection", system.get("unauthorized_modification_detection")),
    ]

    st.markdown('<div class="hc-card"><div class="hc-card-title">System Intelligence</div><div class="hc-info-grid">', unsafe_allow_html=True)
    for label, enabled in cards:
        css = "hc-low" if enabled else "hc-high"
        value = "Enabled" if enabled else "Disabled"
        st.markdown(
            f"""
<div class="hc-mini-card">
    <div class="hc-mini-label">{label}</div>
    <div class="hc-mini-value {css}">{value}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_score_summary(summary):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Compliance Score", f"{summary['percent']:.1f}%")
    c2.metric("Risk Level", summary["overall"])
    c3.metric("Passed Controls", summary["passed"])
    c4.metric("Failed Controls", summary["failed"])


# ====================== DATA BREAKDOWN HELPERS ======================
def get_category_breakdown(results):
    """Pass/fail counts and pass-rate per control category, sorted weakest first."""
    columns = ["category", "passed", "failed", "total", "pass_rate"]
    if not results:
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(results)
    total = df.groupby("category").size().rename("total")
    passed = df[df["pass_fail"] == "PASS"].groupby("category").size().rename("passed")
    out = pd.concat([total, passed], axis=1).fillna(0)
    out["passed"] = out["passed"].astype(int)
    out["failed"] = (out["total"] - out["passed"]).astype(int)
    out["pass_rate"] = (out["passed"] / out["total"] * 100).round(1)
    return out.reset_index().rename(columns={"index": "category"}).sort_values("pass_rate")


def get_severity_breakdown(results):
    """Failed/passed counts per severity tier (High, Medium, Low)."""
    order = ["High", "Medium", "Low"]
    columns = ["severity", "total", "failed", "passed"]
    if not results:
        return pd.DataFrame({"severity": order, "total": [0, 0, 0], "failed": [0, 0, 0], "passed": [0, 0, 0]})

    df = pd.DataFrame(results)
    total = df.groupby("severity").size().rename("total")
    failed = df[df["pass_fail"] == "FAIL"].groupby("severity").size().rename("failed")
    out = pd.concat([total, failed], axis=1).reindex(order).fillna(0)
    out["failed"] = out["failed"].astype(int)
    out["total"] = out["total"].astype(int)
    out["passed"] = (out["total"] - out["failed"]).astype(int)
    return out.reset_index().rename(columns={"index": "severity"})[columns]


# ====================== PLOTLY CHART BUILDERS ======================
def render_chart_panel(fig, title=None, subtitle=None, icon="📊"):
    """Wrap a plotly figure in the app's card header style for a consistent, presentable layout."""
    if title:
        render_section_header(title, subtitle or "", icon)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_score_gauge(summary, title="Compliance Score", icon="🎯"):
    percent = summary.get("percent", 0)
    risk = summary.get("overall", "MEDIUM RISK")
    bar_color = CHART_COLORS["low"] if risk == "LOW RISK" else CHART_COLORS["medium"] if risk == "MEDIUM RISK" else CHART_COLORS["high"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percent,
        number={"suffix": "%", "font": {"size": 34, "color": "#f8fbff", "family": "Orbitron, sans-serif"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#9fb3c8", "tickfont": {"color": "#9fb3c8", "size": 10}},
            "bar": {"color": bar_color, "thickness": 0.28},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 60], "color": "rgba(239,68,68,0.16)"},
                {"range": [60, 85], "color": "rgba(250,204,21,0.16)"},
                {"range": [85, 100], "color": "rgba(34,197,94,0.16)"},
            ],
            "threshold": {"line": {"color": "#f8fbff", "width": 3}, "thickness": 0.85, "value": percent},
        },
    ))
    fig.update_layout(
        template="plotly_dark", height=280, margin=dict(l=25, r=25, t=35, b=10),
        paper_bgcolor="rgba(0,0,0,0)", font=CHART_FONT,
    )
    render_chart_panel(fig, title, f"Overall risk level: {risk}", icon)


def render_compliance_donut(summary, title="Control Status Breakdown", icon="🧬"):
    true_fail = max(summary.get("failed", 0) - summary.get("insufficient", 0), 0)
    labels = ["Passed", "Failed", "Insufficient Evidence"]
    values = [summary.get("passed", 0), true_fail, summary.get("insufficient", 0)]
    colors = [CHART_COLORS["pass"], CHART_COLORS["fail"], CHART_COLORS["insufficient"]]

    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.68, sort=False,
        marker=dict(colors=colors, line=dict(color="#07111f", width=2)),
        textinfo="value+percent", textfont=dict(size=12, color="#EAF2FF"),
    )])
    fig.add_annotation(
        text=f"{summary.get('percent', 0):.0f}%<br><span style='font-size:11px;color:#9fb3c8'>Compliant</span>",
        x=0.5, y=0.5, showarrow=False, font=dict(size=24, color="#f8fbff", family="Orbitron, sans-serif"),
    )
    fig.update_layout(
        template="plotly_dark", height=320, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", font=CHART_FONT,
        legend=dict(orientation="h", yanchor="bottom", y=-0.18, x=0.08, font=dict(color="#9fb3c8", size=11)),
    )
    render_chart_panel(fig, title, "Live snapshot of pass/fail outcomes across all evaluated controls.", icon)


def render_category_bar(results, title="Compliance by Category", icon="📊", categories=None):
    data = get_category_breakdown(results)
    if categories:
        data = data[data["category"].isin(categories)]
    if data.empty:
        st.info("No category data available.")
        return

    colors = [CHART_COLORS["high"] if v < 60 else CHART_COLORS["medium"] if v < 85 else CHART_COLORS["pass"] for v in data["pass_rate"]]
    fig = go.Figure(go.Bar(
        x=data["pass_rate"], y=data["category"], orientation="h",
        marker=dict(color=colors, line=dict(color="rgba(255,255,255,0.08)", width=1)),
        text=[f"{v:.0f}%" for v in data["pass_rate"]], textposition="outside",
        hovertemplate="%{y}: %{x:.1f}%% passing<extra></extra>",
    ))
    fig.update_layout(
        template="plotly_dark", height=max(280, 42 * len(data) + 60),
        margin=dict(l=10, r=40, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[0, 112], showgrid=True, gridcolor=CHART_COLORS["grid"], ticksuffix="%"),
        yaxis=dict(showgrid=False), font=CHART_FONT,
    )
    render_chart_panel(fig, title, "Pass rate for each control category — weakest areas surface first.", icon)


def render_severity_chart(results, title="Risk Exposure by Severity", icon="⚠️"):
    data = get_severity_breakdown(results)
    fig = go.Figure(go.Bar(
        x=data["severity"], y=data["failed"],
        marker=dict(color=[CHART_COLORS["high"], CHART_COLORS["medium"], CHART_COLORS["low"]]),
        text=data["failed"], textposition="outside",
        hovertemplate="%{x} severity: %{y} failed control(s)<extra></extra>",
    ))
    fig.update_layout(
        template="plotly_dark", height=300, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=True, gridcolor=CHART_COLORS["grid"], title="Failed Controls"),
        xaxis=dict(showgrid=False), font=CHART_FONT,
    )
    render_chart_panel(fig, title, "Failed or insufficient-evidence controls grouped by risk severity.", icon)


def render_section_radar(section_scores, title="Behavior Score by Category", icon="🕸️"):
    labels = list(section_scores.keys())
    if not labels:
        st.info("No section data available.")
        return
    values = [(v["score"] / v["max"] * 100) if v.get("max") else 0 for v in section_scores.values()]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]], theta=labels + [labels[0]], fill="toself",
        fillcolor="rgba(89, 215, 194, 0.25)", line=dict(color=CHART_COLORS["pass"], width=2), name="Score",
    ))
    fig.update_layout(
        template="plotly_dark", height=420, showlegend=False,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=CHART_COLORS["grid"], tickfont=dict(size=9, color="#9fb3c8")),
            angularaxis=dict(gridcolor=CHART_COLORS["grid"], tickfont=dict(size=10.5, color="#EAF2FF")),
        ),
        paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=50, r=50, t=30, b=30), font=CHART_FONT,
    )
    render_chart_panel(fig, title, "Radar view of workforce security behavior across each audit domain.", icon)


def render_event_outcome_chart(success_events, failed_events, other_events=0, title="Event Outcomes", icon="📶"):
    labels = ["Success", "Failed", "Other"]
    values = [success_events, failed_events, other_events]
    colors = [CHART_COLORS["pass"], CHART_COLORS["fail"], "#64748b"]
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.6, sort=False,
        marker=dict(colors=colors, line=dict(color="#07111f", width=2)),
        textinfo="value+percent", textfont=dict(size=12, color="#EAF2FF"),
    )])
    fig.update_layout(
        template="plotly_dark", height=300, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", font=CHART_FONT,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, x=0.12, font=dict(color="#9fb3c8", size=11)),
    )
    render_chart_panel(fig, title, "Distribution of recorded audit-log event outcomes.", icon)


def render_results_table(results):
    if not results:
        st.markdown('<div class="hc-success">No findings available.</div>', unsafe_allow_html=True)
        return

    for item in results:
        status_class = "hc-success" if item["pass_fail"] == "PASS" else "hc-alert"
        risk_class = "hc-low" if item["severity"] == "Low" else "hc-medium" if item["severity"] == "Medium" else "hc-high"

        st.markdown(
            f"""
<div class="hc-finding-card">
    <div class="hc-card-title">{item['id']} - {item['control_name']}</div>
    <div class="{status_class}" style="padding:8px 12px; border-radius:12px; margin-bottom:12px;">{item['pass_fail']}</div>
    <div class="hc-subtitle"><strong>Severity:</strong> <span class="{risk_class}">{item['severity']}</span></div>
    <div class="hc-subtitle"><strong>Evidence Used:</strong> {item['evidence']}</div>
    <div class="hc-subtitle"><strong>Plain-language Explanation:</strong> {item['plain_language_explanation']}</div>
    <div class="hc-subtitle"><strong>Technical Explanation:</strong> {item['technical_explanation']}</div>
    <div class="hc-subtitle"><strong>Remediation Guidance:</strong> {item['remediation']}</div>
    <div class="hc-subtitle"><strong>Reference:</strong> {item['reference']} | {item['nist_family']}</div>
</div>
""",
            unsafe_allow_html=True,
        )


STATUS_CHIP_MAP = {
    "Critical": "hc-chip-high", "Action Required": "hc-chip-high",
    "Warning": "hc-chip-medium", "Review": "hc-chip-medium", "Reminder": "hc-chip-medium", "Track": "hc-chip-medium",
    "Important": "hc-chip-medium",
    "Monitor": "hc-chip-neutral", "Evidence Needed": "hc-chip-neutral",
}


def render_awareness_widget(widget):
    status = widget.get("status", "Review")
    chip_class = STATUS_CHIP_MAP.get(status, "hc-chip-neutral")
    mitre = widget.get("mitre_id")
    mitre_html = f'<span class="hc-chip hc-chip-mitre">{mitre}</span>' if mitre else ""
    st.markdown(
        f"""
<div class="hc-card">
    <div class="hc-badge-row" style="justify-content:space-between;">
        <div class="hc-card-title" style="margin-bottom:0;">{widget['title']}</div>
        <div><span class="hc-chip {chip_class}">{status}</span>{mitre_html}</div>
    </div>
    <div class="hc-subtitle" style="margin-top:10px;"><strong>Explanation:</strong> {widget['message']}</div>
    <div class="hc-subtitle"><strong>Recommended Action:</strong> {widget['action']}</div>
    <div class="hc-subtitle"><strong>Compliance Area:</strong> {widget['compliance_area']}</div>
    <div class="hc-widget-ref">
        <div class="hc-subtitle"><strong>Source:</strong> {widget.get('source', 'NIST SP 800-53')}</div>
        <div class="hc-subtitle"><strong>NIST Family:</strong> {widget.get('nist_family', 'General')}</div>
        <div class="hc-subtitle"><strong>Reference Note:</strong> {widget.get('reference_note', 'Source aligns with the advice shown in this widget.')}</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_smart_awareness_nudge(widget, shown_count, max_widgets):
    chip_class = STATUS_CHIP_MAP.get(widget.get("status", "Review"), "hc-chip-neutral")
    st.markdown(
        f"""
<div class="hc-card" style="border-left:3px solid var(--secondary);">
    <div class="hc-badge-row" style="justify-content:space-between;">
        <div class="hc-card-title" style="margin-bottom:0;">⚡ Smart Awareness Reminder — {widget['title']}</div>
        <span class="hc-chip {chip_class}">{widget['status']}</span>
    </div>
    <div class="hc-subtitle" style="margin-top:10px;">{widget['message']}</div>
    <div class="hc-subtitle"><strong>Recommended Action:</strong> {widget['action']}</div>
    <div class="hc-widget-ref">
        <div class="hc-subtitle"><strong>Source:</strong> {widget.get('source', 'NIST SP 800-53')}</div>
        <div class="hc-subtitle"><strong>NIST Family:</strong> {widget.get('nist_family', 'General')}</div>
        <div class="hc-subtitle"><strong>Reference Note:</strong> {widget.get('reference_note', 'Source aligns with the advice shown in this widget.')}</div>
    </div>
    <div class="hc-subtitle" style="margin-top:10px;">Shown {shown_count} of {max_widgets} allowed reminders this session.</div>
</div>
""",
        unsafe_allow_html=True,
    )


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
        st.session_state.show_awareness_popup = True

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
    if session_hours > 2:
        max_widgets += 1
    if common_mistakes >= 2 or audit_log_issues >= 2:
        max_widgets += 1
    return min(max_widgets, 3)


def prioritize_awareness_widgets(widgets, role_key, risk_level, common_mistakes, audit_log_issues):
    if role_key == "staff":
        priority_titles = (
            ["Secure PHI Handling", "Phishing Awareness", "Incident Reporting"]
            if common_mistakes >= 2
            else ["Phishing Awareness", "Strong Passwords & MFA", "Incident Reporting"]
        )
    elif role_key == "it":
        if risk_level == "HIGH RISK":
            priority_titles = ["MFA Enforcement Status", "Configuration Gaps", "Suspicious Access Alerts"]
        elif audit_log_issues > 0:
            priority_titles = ["Suspicious Access Alerts", "Configuration Gaps", "Privileged Account Risk"]
        else:
            priority_titles = ["Privileged Account Risk", "MFA Enforcement Status", "Configuration Gaps"]
    else:
        if audit_log_issues > 0:
            priority_titles = ["Missing Evidence", "Audit Readiness", "Training Completion"]
        else:
            priority_titles = ["Training Completion", "Missing Evidence", "Audit Readiness"]

    title_rank = {title: index for index, title in enumerate(priority_titles)}
    return sorted(widgets, key=lambda item: title_rank.get(item["title"], 99))


SCENARIOS = [
    {
        "name": "Strong Compliance",
        "description": "MFA, encryption, audit logging, secure backups, staff training, and monitoring are enabled.",
        "overrides": {
            "incident_response_plan": True,
            "suspicious_activity_reporting_process": True,
            "post_incident_documentation": True,
            "staff_retraining_after_incidents": True,
            "backup_testing": True,
            "downtime_procedures": True,
            "ransomware_recovery_steps": True,
            "recovery_evidence_documented": True,
            "tamper_evident_logging": True,
            "unauthorized_modification_detection": True,
            "restoration_testing": True,
            "workstation_security": True,
            "failed_login_count": 0,
            "suspicious_ip_detected": False,
            "after_hours_access": False,
            "usb_policy_defined": True,
        }
    },
    {
        "name": "Weak Access Control",
        "description": "MFA is missing, password controls are weak, failed logins occur, and there is a role mismatch.",
        "overrides": {
            "mfa_enabled": False,
            "rbac_enabled": False,
            "password_length": 6,
            "failed_login_count": 5,
            "role_mismatch_detected": True,
        }
    },
    {
        "name": "Suspicious PHI Access",
        "description": "The user accesses too many records, accesses records after hours, or connects from an unusual IP or location.",
        "overrides": {
            "suspicious_ip_detected": True,
            "after_hours_access": True,
            "unusual_location_access": True,
            "excessive_record_access": True,
        }
    },
    {
        "name": "Poor Training or Human Risk",
        "description": "Phishing training is missing, device rules are weak, the USB policy is missing, and staff do not know how to report incidents.",
        "overrides": {
            "phishing_training_enabled": False,
            "staff_training_completed": False,
            "usb_policy_defined": False,
            "suspicious_activity_reporting_process": False,
        }
    },
    {
        "name": "Recovery Failure",
        "description": "Backups exist but are not encrypted or tested, and there is no incident response or disaster recovery plan.",
        "overrides": {
            "encrypted_backups": False,
            "backup_testing": False,
            "incident_response_plan": False,
            "disaster_recovery_plan": False,
            "ransomware_recovery_steps": False,
            "recovery_evidence_documented": False,
        }
    },
    {
        "name": "Data Integrity Risk",
        "description": "Audit logs are missing, modification detection is disabled, and tamper-evident logging is not enabled.",
        "overrides": {
            "audit_logging": False,
            "tamper_evident_logging": False,
            "unauthorized_modification_detection": False,
        }
    },
]


def evaluate_scenarios(controls):
    base_path = Path(__file__).resolve().parent / "system_data.json"
    base_system = load_json(base_path)
    scenario_results = []

    for scenario in SCENARIOS:
        scenario_system = deepcopy(base_system)
        scenario_system.update(scenario["overrides"])
        result = compute_compliance(controls, scenario_system)
        scenario_results.append(
            {
                "name": scenario["name"],
                "description": scenario["description"],
                "summary": result,
            }
        )

    return scenario_results


def render_scenario_results(scenario_results):
    for scenario in scenario_results:
        with st.expander(f"{scenario['name']} — {scenario['summary']['overall']}", expanded=False):
            st.write(scenario["description"])
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Score", f"{scenario['summary']['percent']:.1f}%")
            c2.metric("Risk", scenario["summary"]["overall"])
            c3.metric("Passed", scenario["summary"]["passed"])
            c4.metric("Failed", scenario["summary"]["failed"])
            render_alerts(scenario["summary"]["alerts"])


# === ADDED HELPER FUNCTIONS FOR OTHER DASHBOARDS ===
def render_kpi_card(label, value, help_text="", color="info", icon=""):
    color_map = {"success": "hc-low", "warning": "hc-medium", "danger": "hc-high", "info": ""}
    border_map = {
        "success": "rgba(47, 230, 160, 0.5)",
        "warning": "rgba(255, 184, 51, 0.5)",
        "danger": "rgba(255, 77, 106, 0.5)",
        "info": "rgba(18, 232, 198, 0.3)",
    }
    css_class = color_map.get(color, "")
    border_color = border_map.get(color, border_map["info"])
    icon_html = f'<div class="hc-kpi-icon">{icon}</div>' if icon else ""
    st.markdown(f'''
<div class="hc-card hc-kpi-card" style="text-align:center;padding:20px;border-top:2px solid {border_color} !important;">
    {icon_html}
    <div class="hc-mini-label">{label}</div>
    <div class="hc-mini-value {css_class}">{value}</div>
    <div class="hc-subtitle">{help_text}</div>
</div>
''', unsafe_allow_html=True)


def render_divider():
    st.markdown('<div class="hc-divider"></div>', unsafe_allow_html=True)


def render_progress_bar(label, percent, color="info"):
    colors = {"success": "#22c55e", "danger": "#ef4444", "warning": "#facc15", "info": "#3b82f6"}
    bar_color = colors.get(color, "#3b82f6")
    st.markdown(f"""
<div style="margin-bottom:12px;">
    <div class="hc-subtitle">{label}</div>
    <div style="background:rgba(148,163,184,0.2);height:8px;border-radius:999px;">
        <div style="width:{percent}%;height:100%;background:{bar_color};border-radius:999px;"></div>
    </div>
    <div style="text-align:right;font-size:12px;">{percent:.1f}%</div>
</div>
""", unsafe_allow_html=True)


def render_section_header(title, subtitle="", icon=""):
    st.markdown(f"""
<div class="hc-card">
    <div class="hc-title" style="font-size:22px;">{icon} {title}</div>
    <div class="hc-subtitle">{subtitle}</div>
</div>
""", unsafe_allow_html=True)


def _render_finding_card(item):
    status_class = "hc-success" if item.get("pass_fail") == "PASS" else "hc-alert"
    severity = item.get("severity", "Medium")
    border_class = {"High": "hc-finding-high", "Medium": "hc-finding-medium", "Low": "hc-finding-low"}.get(severity, "")
    chip_class = {"High": "hc-chip-high", "Medium": "hc-chip-medium", "Low": "hc-chip-low"}.get(severity, "hc-chip-medium")
    st.markdown(f"""
<div class="hc-finding-card {border_class}">
    <div class="hc-badge-row" style="justify-content:space-between;">
        <div class="hc-card-title" style="margin-bottom:0;">{item.get('id','')} — {item.get('control_name','Control')}</div>
        <div>
            <span class="hc-chip {chip_class}">{severity}</span>
            <span class="hc-chip hc-chip-neutral">{item.get('category','General')}</span>
        </div>
    </div>
    <div class="{status_class}" style="padding:7px 12px;border-radius:8px;margin-top:10px;display:inline-block;">{item.get('pass_fail','FAIL')}</div>
    <div class="hc-subtitle" style="margin-top:8px;">Remediation: {item.get('remediation','N/A')}</div>
</div>
""", unsafe_allow_html=True)


def render_findings_cards(results, limit=6, show_more=True):
    if not results:
        st.info("No findings.")
        return

    for item in results[:limit]:
        _render_finding_card(item)

    remaining = results[limit:]
    if remaining and show_more:
        with st.expander(f"Show {len(remaining)} more finding(s)"):
            for item in remaining:
                _render_finding_card(item)


def evaluate_contingency_controls(controls, system):
    cont_controls = [c for c in controls if "BR-" in c.get("id", "") or "backup" in str(c).lower()]
    return [_build_finding(c, system) for c in cont_controls]


def summarize_contingency_findings(findings):
    passed = sum(1 for f in findings if f.get("status") == "COMPLIANT")
    return {"passed": passed, "total": len(findings)}


def render_contingency_section(findings, summary):
    st.subheader("Contingency Planning")
    render_findings_cards(findings)


# ====================== THREAT INTELLIGENCE (SOC-STYLE) HELPERS ======================
# Educational mapping from this app's control categories to illustrative MITRE ATT&CK
# tactics/techniques, so failed/insufficient controls can be shown the way a SOC
# console would present exposure. This is a simplified teaching mapping, not a
# full ATT&CK Navigator layer.
MITRE_MAP = {
    "Access Control": ("Credential Access", "T1078", "Valid Accounts"),
    "Encryption": ("Exfiltration", "T1537", "Data Transfer to Cloud Account"),
    "Network Security": ("Command and Control", "T1071", "Application Layer Protocol"),
    "Endpoint Security": ("Execution", "T1204", "User Execution"),
    "Remote Access": ("Initial Access", "T1133", "External Remote Services"),
    "Audit Controls": ("Defense Evasion", "T1070", "Indicator Removal"),
    "Backup and Recovery": ("Impact", "T1486", "Data Encrypted for Impact"),
    "Backup": ("Impact", "T1486", "Data Encrypted for Impact"),
    "Contingency Planning": ("Impact", "T1490", "Inhibit System Recovery"),
    "Data Integrity": ("Defense Evasion", "T1565", "Data Manipulation"),
    "Incident Response": ("Impact", "T1489", "Service Stop"),
    "Risk Management": ("Reconnaissance", "T1590", "Gather Victim Network Information"),
}
DEFAULT_MITRE = ("Discovery", "T1082", "System Information Discovery")


def build_threat_indicators(results, system):
    """Turn failed/insufficient control findings into SOC-style threat indicators
    tagged with an illustrative MITRE ATT&CK tactic and technique."""
    indicators = []
    for item in results:
        if item.get("pass_fail") == "PASS":
            continue
        tactic, technique_id, technique_name = MITRE_MAP.get(item.get("category", ""), DEFAULT_MITRE)
        indicators.append({
            "id": item.get("id", "N/A"),
            "title": item.get("control_name", "Control"),
            "category": item.get("category", "General"),
            "severity": item.get("severity", "Medium"),
            "tactic": tactic,
            "technique_id": technique_id,
            "technique_name": technique_name,
            "remediation": item.get("remediation", "Review and remediate."),
        })

    # live-telemetry indicators sourced directly from system_data.json signals
    if system.get("suspicious_ip_detected"):
        indicators.append({"id": "TEL-01", "title": "Suspicious IP Connection", "category": "Network Security",
                            "severity": "High", "tactic": "Command and Control", "technique_id": "T1071",
                            "technique_name": "Application Layer Protocol", "remediation": "Isolate source and review firewall/VPN logs."})
    if system.get("after_hours_access"):
        indicators.append({"id": "TEL-02", "title": "After-Hours Record Access", "category": "Access Control",
                            "severity": "Medium", "tactic": "Credential Access", "technique_id": "T1078",
                            "technique_name": "Valid Accounts", "remediation": "Confirm business justification with the accessing user's manager."})
    if system.get("excessive_record_access"):
        indicators.append({"id": "TEL-03", "title": "Excessive PHI Record Access", "category": "Access Control",
                            "severity": "High", "tactic": "Collection", "technique_id": "T1213",
                            "technique_name": "Data from Information Repositories", "remediation": "Trigger a privacy access review for the account."})
    if system.get("role_mismatch_detected"):
        indicators.append({"id": "TEL-04", "title": "Role-Based Access Mismatch", "category": "Access Control",
                            "severity": "Medium", "tactic": "Privilege Escalation", "technique_id": "T1078.004",
                            "technique_name": "Valid Accounts: Cloud Accounts", "remediation": "Reconcile role assignment against least-privilege policy."})

    severity_order = {"High": 0, "Medium": 1, "Low": 2}
    indicators.sort(key=lambda i: severity_order.get(i["severity"], 1))
    return indicators


def render_threat_ticker(indicators):
    """Horizontally scrolling SOC-style live ticker of active threat indicators."""
    if not indicators:
        st.markdown('<div class="hc-success">No active threat indicators — telemetry is clean.</div>', unsafe_allow_html=True)
        return

    sev_color = {"High": "#ff4d6a", "Medium": "#ffb833", "Low": "#2fe6a0"}
    items_html = ""
    for ind in indicators:
        c = sev_color.get(ind["severity"], "#ffb833")
        items_html += (
            f'<span style="color:{c};font-weight:700;">●</span>&nbsp;'
            f'<span style="color:#eaf4ff;">{ind["title"]}</span>&nbsp;'
            f'<span style="color:#7e93ad;">[{ind["technique_id"]} · {ind["tactic"]}]</span>'
            f'&nbsp;&nbsp;&nbsp;<span style="color:#334155;">//</span>&nbsp;&nbsp;&nbsp;'
        )
    # duplicate content so the marquee loops seamlessly
    st.markdown(
        f"""
<style>
.hc-ticker-wrap {{
    overflow: hidden; white-space: nowrap; background: rgba(4,10,20,0.75);
    border: 1px solid var(--line); border-radius: 10px; padding: 12px 0; margin-bottom: 16px;
}}
.hc-ticker-track {{
    display: inline-block; padding-left: 100%;
    animation: hc-ticker-scroll 32s linear infinite;
    font-family: 'JetBrains Mono', monospace; font-size: 12.5px;
}}
@keyframes hc-ticker-scroll {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-100%); }} }}
</style>
<div class="hc-ticker-wrap"><div class="hc-ticker-track">{items_html}{items_html}</div></div>
""",
        unsafe_allow_html=True,
    )


def _render_threat_card(ind):
    chip_class = {"High": "hc-chip-high", "Medium": "hc-chip-medium", "Low": "hc-chip-low"}.get(ind["severity"], "hc-chip-medium")
    border_class = {"High": "hc-finding-high", "Medium": "hc-finding-medium", "Low": "hc-finding-low"}.get(ind["severity"], "")
    st.markdown(f"""
<div class="hc-finding-card {border_class}">
    <div class="hc-badge-row" style="justify-content:space-between;">
        <div class="hc-card-title" style="margin-bottom:0;">{ind['id']} — {ind['title']}</div>
        <div>
            <span class="hc-chip {chip_class}">{ind['severity']}</span>
            <span class="hc-chip hc-chip-mitre">{ind['technique_id']}</span>
            <span class="hc-chip hc-chip-neutral">{ind['category']}</span>
        </div>
    </div>
    <div class="hc-subtitle" style="margin-top:8px;"><strong>ATT&amp;CK Tactic:</strong> {ind['tactic']} — {ind['technique_name']}</div>
    <div class="hc-subtitle"><strong>Recommended Response:</strong> {ind['remediation']}</div>
</div>
""", unsafe_allow_html=True)


def render_threat_indicator_cards(indicators, limit=8):
    if not indicators:
        st.markdown('<div class="hc-success">No active threat indicators detected.</div>', unsafe_allow_html=True)
        return
    for ind in indicators[:limit]:
        _render_threat_card(ind)
    remaining = indicators[limit:]
    if remaining:
        with st.expander(f"Show {len(remaining)} more indicator(s)"):
            for ind in remaining:
                _render_threat_card(ind)


def render_tactic_coverage_chart(indicators, title="Exposure by ATT&CK Tactic", icon="🧬"):
    if not indicators:
        st.info("No indicators to chart.")
        return
    df = pd.DataFrame(indicators)
    counts = df.groupby("tactic").size().sort_values(ascending=True)

    fig = go.Figure(go.Bar(
        x=counts.values, y=counts.index, orientation="h",
        marker=dict(color=CHART_COLORS["secondary"], line=dict(color="rgba(255,255,255,0.08)", width=1)),
        text=counts.values, textposition="outside",
        hovertemplate="%{y}: %{x} indicator(s)<extra></extra>",
    ))
    fig.update_layout(
        template="plotly_dark", height=max(260, 42 * len(counts) + 60),
        margin=dict(l=10, r=30, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor=CHART_COLORS["grid"]),
        yaxis=dict(showgrid=False), font=CHART_FONT,
    )
    render_chart_panel(fig, title, "Active indicators grouped by the ATT&CK tactic they map to.", icon)