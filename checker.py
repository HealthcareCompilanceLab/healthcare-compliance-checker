import json
from datetime import datetime
import webbrowser
import os

risk_weights = {"High": 3, "Medium": 2, "Low": 1}

with open("control_bank.json") as f:
    controls = json.load(f)

with open("system_data.json") as f:
    system = json.load(f)

results = []
alerts = []

score = 0
max_score = 0

passed = failed = insufficient = 0

print("\n=== Healthcare Security Scanner ===\n")

# ---------------- COMPLIANCE CHECK ----------------
for control in controls:
    field = control["field"]
    risk = control["risk"]
    weight = risk_weights[risk]
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

    icon = "✔" if status == "COMPLIANT" else "✖" if status == "NON-COMPLIANT" else "⚠"
    print(f"[{icon}] {control['description']} -> {status}")

    results.append({
        "desc": control["description"],
        "status": status,
        "risk": risk,
        "remediation": control["remediation"],
        "evidence": f"{field} = {value}"
    })

# ---------------- ATTACK DETECTION ----------------
failed_logins = system.get("login_attempts", []).count("failed")

if failed_logins >= 3:
    alerts.append("⚠ Multiple failed login attempts detected (possible brute-force attack)")

if system.get("suspicious_ip_detected"):
    alerts.append("🚨 Suspicious IP detected accessing system")

# ---------------- SCORE ----------------
percent = (score / max_score) * 100

if percent >= 80:
    overall = "LOW RISK"
elif percent >= 50:
    overall = "MEDIUM RISK"
else:
    overall = "HIGH RISK"

print(f"\nFinal Score: {percent:.2f}% ({overall})\n")

# ---------------- HTML REPORT ----------------
html = f"""
<html>
<head>
<title>Security Compliance Report</title>
<style>
body {{
    font-family: Arial;
    background-color: #0f172a;
    color: white;
    padding: 20px;
}}
h1 {{ color: #38bdf8; }}
.card {{
    background: #1e293b;
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 8px;
}}
table {{
    width: 100%;
    border-collapse: collapse;
}}
th, td {{
    padding: 10px;
    border-bottom: 1px solid #333;
}}
.compliant {{ color: #22c55e; }}
.noncompliant {{ color: #ef4444; }}
.insufficient {{ color: #facc15; }}
.alert {{ color: #f87171; font-weight: bold; }}
button {{
    padding: 10px;
    background: #38bdf8;
    border: none;
    color: white;
    border-radius: 5px;
    cursor: pointer;
}}
</style>
</head>

<body>

<h1>Healthcare Security Dashboard</h1>

<div class="card">
<h2>Compliance Score: {percent:.2f}%</h2>
<h3>Status: {overall}</h3>
<p>Generated: {datetime.now()}</p>
</div>

<div class="card">
<h3>Summary</h3>
<p>Total Checks: {len(results)}</p>
<p>Passed: {passed}</p>
<p>Failed: {failed}</p>
<p>Insufficient: {insufficient}</p>
</div>

<div class="card">
<h3>Security Alerts</h3>
{"<br>".join(f"<p class='alert'>{a}</p>" for a in alerts) if alerts else "<p>No active threats detected</p>"}
</div>

<div class="card">
<h3>Compliance Results</h3>
<table>
<tr>
<th>Control</th>
<th>Status</th>
<th>Risk</th>
<th>Evidence</th>
<th>Remediation</th>
</tr>
"""

for r in results:
    cls = "compliant" if r["status"] == "COMPLIANT" else "noncompliant" if r["status"] == "NON-COMPLIANT" else "insufficient"

    html += f"""
    <tr>
    <td>{r['desc']}</td>
    <td class="{cls}">{r['status']}</td>
    <td>{r['risk']}</td>
    <td>{r['evidence']}</td>
    <td>{r['remediation']}</td>
    </tr>
    """

html += """
</table>
</div>

<div class="card">
<h3>Actions</h3>
<button onclick="location.reload()">Run Scan Again</button>
</div>

</body>
</html>
"""

with open("report.html", "w", encoding="utf-8") as f:
    f.write(html)

webbrowser.open('file://' + os.path.realpath("report.html"))