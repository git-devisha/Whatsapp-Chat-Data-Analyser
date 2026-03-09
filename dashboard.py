"""
dashboard_generator.py
Builds a fully self-contained HTML dashboard from the analysis outputs.
Run AFTER analysis.py.
"""

import os
import json
import base64

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
CHART_DIR  = os.path.join(BASE_DIR, "charts")
STATIC_DIR = os.path.join(BASE_DIR, "static")
OUT_HTML   = os.path.join(STATIC_DIR, "dashboard.html")


def img_b64(filename: str) -> str:
    path = os.path.join(CHART_DIR, filename)
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode()


def build():
    # Load summary
    with open(os.path.join(STATIC_DIR, "summary.json")) as fh:
        s = json.load(fh)

    charts = sorted(os.listdir(CHART_DIR))
    chart_titles = {
        "01_messages_over_time.png":    "Messages Per Month by Sender",
        "02_activity_heatmap.png":      "Activity Heatmap — Day × Hour",
        "03_sender_share.png":          "Sender Share & Word Count",
        "04_keyword_frequency.png":     "Keyword Frequency",
        "05_country_mentions.png":      "Countries Mentioned",
        "06_daily_trend.png":           "Daily Message Volume Trend",
        "07_word_length_dist.png":      "Message Length Distribution",
        "08_hourly_pattern.png":        "Hourly Messaging Pattern",
        "09_top_words.png":             "Top 25 Most Frequent Words",
        "10_monthly_keyword_trend.png": "Monthly Keyword Trends",
    }

    # Build stat cards
    def stat_card(icon, label, value, color="#25D366"):
        return f"""
        <div class="stat-card">
          <div class="stat-icon" style="color:{color}">{icon}</div>
          <div class="stat-value">{value}</div>
          <div class="stat-label">{label}</div>
        </div>"""

    admin_a = s["sender_stats"].get("Admin A", {})
    admin_b = s["sender_stats"].get("Admin B", {})

    cards_html = (
        stat_card("💬", "Total Messages",   f"{s['total_messages']:,}")
      + stat_card("📅", "Active Days",       f"{s['date_range']['start']} → {s['date_range']['end']}", "#128C7E")
      + stat_card("📝", "Total Words",        f"{s['total_words']:,}", "#34B7F1")
      + stat_card("⚡", "Avg Msgs / Day",     s["avg_msg_per_day"], "#FFA07A")
      + stat_card("🕐", "Peak Hour",          f"{s['peak_hour']}:00", "#FF6B6B")
      + stat_card("📆", "Busiest Day",        s["peak_day"], "#9B59B6")
      + stat_card("🌍", "Top Country",        list(s["country_mentions"].keys())[0], "#E67E22")
      + stat_card("🏆", "Top Keyword",        max(s["keyword_totals"], key=s["keyword_totals"].get), "#1ABC9C")
    )

    # Sender table
    sender_rows = ""
    for name, st in s["sender_stats"].items():
        sender_rows += f"""
        <tr>
          <td>{name}</td>
          <td>{st['messages']:,}</td>
          <td>{st['words']:,}</td>
          <td>{st['avg_words']}</td>
          <td>{st['media']}</td>
        </tr>"""

    # Keyword rows
    kw_rows = "".join(
        f"<tr><td>{k}</td><td>{v:,}</td></tr>"
        for k, v in sorted(s["keyword_totals"].items(), key=lambda x: -x[1])
    )

    # Country rows
    country_rows = "".join(
        f"<tr><td>{k}</td><td>{v:,}</td></tr>"
        for k, v in list(s["country_mentions"].items())[:10]
    )

    # Charts grid
    charts_html = ""
    for filename in charts:
        title = chart_titles.get(filename, filename)
        b64   = img_b64(filename)
        charts_html += f"""
        <div class="chart-card">
          <h3 class="chart-title">{title}</h3>
          <img src="data:image/png;base64,{b64}" alt="{title}" loading="lazy"/>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>WhatsApp Chat Analysis — Bright Scholarship 146</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg:        #0d1117;
    --card:      #161b22;
    --border:    #30363d;
    --text:      #c9d1d9;
    --muted:     #8b949e;
    --green:     #25D366;
    --teal:      #128C7E;
    --accent:    #34B7F1;
  }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Segoe UI', system-ui, sans-serif;
    line-height: 1.6;
  }}

  /* ── Header ── */
  .header {{
    background: linear-gradient(135deg, #075E54 0%, #128C7E 50%, #25D366 100%);
    padding: 40px 32px 36px;
    text-align: center;
  }}
  .header-icon {{ font-size: 52px; }}
  .header h1 {{ font-size: 2rem; font-weight: 800; margin: 8px 0 4px; color: #fff; }}
  .header p  {{ color: rgba(255,255,255,.8); font-size: .95rem; }}
  .badge {{
    display: inline-block;
    background: rgba(255,255,255,.15);
    border: 1px solid rgba(255,255,255,.3);
    border-radius: 20px;
    padding: 3px 14px;
    font-size: .82rem;
    margin-top: 10px;
    color: #fff;
  }}

  /* ── Layout ── */
  .container {{ max-width: 1280px; margin: 0 auto; padding: 32px 20px; }}
  .section-title {{
    font-size: 1.2rem; font-weight: 700;
    border-left: 4px solid var(--green);
    padding-left: 12px;
    margin: 40px 0 18px;
    color: #e6edf3;
  }}

  /* ── Stat cards ── */
  .stats-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 14px;
  }}
  .stat-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
    transition: transform .2s;
  }}
  .stat-card:hover {{ transform: translateY(-3px); }}
  .stat-icon  {{ font-size: 26px; margin-bottom: 6px; }}
  .stat-value {{ font-size: 1.35rem; font-weight: 700; color: #e6edf3; word-break: break-word; }}
  .stat-label {{ font-size: .78rem; color: var(--muted); margin-top: 4px; }}

  /* ── Tables ── */
  .tables-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
  }}
  .table-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
  }}
  .table-card h3 {{
    padding: 14px 18px;
    font-size: .95rem;
    font-weight: 700;
    background: #1c2128;
    border-bottom: 1px solid var(--border);
  }}
  table {{ width: 100%; border-collapse: collapse; font-size: .88rem; }}
  th, td {{ padding: 9px 16px; text-align: left; }}
  th {{ color: var(--muted); font-weight: 600; background: #1c2128; border-bottom: 1px solid var(--border); }}
  tr:not(:last-child) td {{ border-bottom: 1px solid var(--border); }}
  tr:hover td {{ background: #1c2128; }}

  /* ── Charts ── */
  .charts-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(560px, 1fr));
    gap: 20px;
  }}
  .chart-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
  }}
  .chart-title {{
    padding: 14px 18px;
    font-size: .9rem;
    font-weight: 700;
    background: #1c2128;
    border-bottom: 1px solid var(--border);
  }}
  .chart-card img {{
    width: 100%;
    display: block;
  }}

  /* ── Footer ── */
  .footer {{
    text-align: center;
    padding: 30px 16px;
    color: var(--muted);
    font-size: .82rem;
    border-top: 1px solid var(--border);
    margin-top: 60px;
  }}

  @media (max-width: 640px) {{
    .charts-grid {{ grid-template-columns: 1fr; }}
    .header h1   {{ font-size: 1.4rem; }}
  }}
</style>
</head>
<body>

<div class="header">
  <div class="header-icon">💬</div>
  <h1>Bright Scholarship 146</h1>
  <p>WhatsApp Group Chat Analysis Dashboard</p>
  <span class="badge">📅 {s["date_range"]["start"]} → {s["date_range"]["end"]}</span>
  <span class="badge">🗂️ {s["total_messages"]:,} Messages Analysed</span>
</div>

<div class="container">

  <h2 class="section-title">📊 Key Statistics</h2>
  <div class="stats-grid">
    {cards_html}
  </div>

  <h2 class="section-title">👥 Sender & Keyword Breakdown</h2>
  <div class="tables-grid">

    <div class="table-card">
      <h3>👤 Sender Activity</h3>
      <table>
        <thead><tr><th>Sender</th><th>Messages</th><th>Words</th><th>Avg Words</th><th>Media</th></tr></thead>
        <tbody>{sender_rows}</tbody>
      </table>
    </div>

    <div class="table-card">
      <h3>🔑 Keyword Counts</h3>
      <table>
        <thead><tr><th>Keyword</th><th>Mentions</th></tr></thead>
        <tbody>{kw_rows}</tbody>
      </table>
    </div>

    <div class="table-card">
      <h3>🌍 Top Countries Mentioned</h3>
      <table>
        <thead><tr><th>Country</th><th>Mentions</th></tr></thead>
        <tbody>{country_rows}</tbody>
      </table>
    </div>

  </div>

  <h2 class="section-title">📈 Visualisations</h2>
  <div class="charts-grid">
    {charts_html}
  </div>

</div>

<div class="footer">
  Generated by WhatsApp Chat Analyser &nbsp;|&nbsp; Bright Scholarship 146 &nbsp;|&nbsp;
  Data: {s["date_range"]["start"]} – {s["date_range"]["end"]}
</div>

</body>
</html>"""

    with open(OUT_HTML, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"✅  Dashboard saved → {OUT_HTML}  ({os.path.getsize(OUT_HTML)//1024} KB)")


if __name__ == "__main__":
    build()