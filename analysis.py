"""
WhatsApp Group Chat Analysis Backend
=====================================
Parses WhatsApp chat export and generates:
  - Parsed DataFrame (messages.csv)
  - Summary statistics (summary.json)
  - All charts as PNG files
"""

import re
import json
import os
import warnings
from collections import Counter, defaultdict
from datetime import datetime

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
CHAT_FILE  = os.path.join(BASE_DIR, "data", "chat.txt")
CHART_DIR  = os.path.join(BASE_DIR, "charts")
OUTPUT_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(CHART_DIR,  exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Colour palette ─────────────────────────────────────────────────────────────
PALETTE    = ["#25D366", "#128C7E", "#075E54", "#34B7F1", "#ECE5DD", "#FF6B6B", "#FFA07A"]
SENDER_CLR = {"#25D366": "Sender A", "#128C7E": "Sender B"}

plt.rcParams.update({
    "figure.facecolor": "#0d1117",
    "axes.facecolor":   "#161b22",
    "axes.edgecolor":   "#30363d",
    "axes.labelcolor":  "#c9d1d9",
    "xtick.color":      "#8b949e",
    "ytick.color":      "#8b949e",
    "text.color":       "#c9d1d9",
    "grid.color":       "#21262d",
    "grid.linestyle":   "--",
    "grid.alpha":       0.5,
    "font.family":      "DejaVu Sans",
})


# ══════════════════════════════════════════════════════════════════════════════
# 1.  PARSING
# ══════════════════════════════════════════════════════════════════════════════

MSG_RE  = re.compile(r'^(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}) - (.+?): (.+)$')
SYS_RE  = re.compile(r'^(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}) - (.+)$')


def parse_chat(filepath: str) -> tuple[pd.DataFrame, list[str]]:
    """Return (messages_df, system_events list)."""
    records, system_events = [], []

    with open(filepath, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            m = MSG_RE.match(line)
            if m:
                date_s, time_s, sender, content = m.groups()
                dt = datetime.strptime(f"{date_s} {time_s}", "%d/%m/%Y %H:%M")
                records.append({
                    "datetime":  dt,
                    "date":      dt.date(),
                    "hour":      dt.hour,
                    "day_name":  dt.strftime("%A"),
                    "month":     dt.strftime("%Y-%m"),
                    "week":      dt.strftime("%Y-W%U"),
                    "sender":    sender.strip(),
                    "content":   content.strip(),
                    "word_count": len(content.split()),
                    "char_count": len(content),
                    "is_media":  content.strip() == "<Media omitted>",
                })
            else:
                s = SYS_RE.match(line)
                if s:
                    system_events.append(line)

    df = pd.DataFrame(records)
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df, system_events


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Add keyword, category and response-time columns."""
    keyword_map = {
        "Scholarship":  r'\bscholarship\b',
        "Fully Funded": r'fully funded',
        "Fellowship":   r'\bfellowship\b',
        "Internship":   r'\binternship\b',
        "Visa / Jobs":  r'\b(visa|job|work permit)\b',
        "PhD / Masters":r'\b(phd|masters|msc|mba)\b',
        "University":   r'\buniversity\b',
    }
    for label, pattern in keyword_map.items():
        df[f"kw_{label}"] = df["content"].str.lower().str.contains(pattern, regex=True, na=False)

    # Simple country detection
    countries = {
        "USA": r'\b(usa|united states|america)\b',
        "UK":  r'\b(uk|united kingdom|britain)\b',
        "Germany": r'\bgermany\b',
        "Japan":   r'\bjapan\b',
        "Canada":  r'\bcanada\b',
        "Australia": r'\baustralia\b',
        "Singapore": r'\bsingapore\b',
        "France":  r'\bfrance\b',
        "Netherlands": r'\b(netherlands|holland)\b',
        "Italy":   r'\bitaly\b',
        "South Korea": r'\b(south korea|korea)\b',
        "China":   r'\bchina\b',
        "Taiwan":  r'\btaiwan\b',
        "Malaysia": r'\bmalaysia\b',
        "Turkey":  r'\bturkey\b',
    }
    for cname, pat in countries.items():
        df[f"country_{cname}"] = df["content"].str.lower().str.contains(pat, regex=True, na=False)

    return df


# ══════════════════════════════════════════════════════════════════════════════
# 2.  CHART HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def save(fig, name: str) -> str:
    path = os.path.join(CHART_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  [OK] {name}")
    return path


def sender_label(sender: str, mapping: dict) -> str:
    return mapping.get(sender, sender[-8:])


# ══════════════════════════════════════════════════════════════════════════════
# 3.  INDIVIDUAL CHART FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def chart_messages_over_time(df, mapping):
    monthly = df.groupby(["month", "sender"]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(13, 5))
    colors = PALETTE[:len(monthly.columns)]
    monthly.plot(kind="bar", ax=ax, color=colors, width=0.7, edgecolor="none")
    ax.set_title("📅 Messages Per Month by Sender", fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("Month")
    ax.set_ylabel("Message Count")
    ax.legend([mapping.get(c, c[-8:]) for c in monthly.columns], title="Sender")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y")
    fig.tight_layout()
    return save(fig, "01_messages_over_time.png")


def chart_hourly_heatmap(df, mapping):
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heat_data  = df.groupby(["day_name", "hour"]).size().unstack(fill_value=0)
    heat_data  = heat_data.reindex(dow_order, fill_value=0)

    fig, ax = plt.subplots(figsize=(14, 5))
    sns.heatmap(heat_data, cmap="YlGn", linewidths=0.3, linecolor="#0d1117",
                ax=ax, cbar_kws={"label": "Messages"})
    ax.set_title("🕐 Activity Heatmap — Day of Week × Hour", fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("Hour of Day (0–23)")
    ax.set_ylabel("")
    fig.tight_layout()
    return save(fig, "02_activity_heatmap.png")


def chart_sender_share(df, mapping):
    counts = df["sender"].value_counts()
    labels = [mapping.get(s, s[-8:]) for s in counts.index]
    colors = PALETTE[:len(counts)]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Pie
    wedges, texts, autotexts = axes[0].pie(
        counts, labels=labels, colors=colors,
        autopct="%1.1f%%", startangle=140,
        wedgeprops={"edgecolor": "#0d1117", "linewidth": 2}
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(11)
    axes[0].set_title("Message Share", fontsize=13, fontweight="bold")

    # Bar – word count
    wc = df.groupby("sender")["word_count"].sum()
    wc.index = [mapping.get(s, s[-8:]) for s in wc.index]
    axes[1].barh(wc.index, wc.values, color=colors[:len(wc)], edgecolor="none", height=0.5)
    axes[1].set_title("Total Words Contributed", fontsize=13, fontweight="bold")
    axes[1].set_xlabel("Words")
    axes[1].grid(axis="x")

    fig.suptitle("👥 Sender Comparison", fontsize=15, fontweight="bold", y=1.01)
    fig.tight_layout()
    return save(fig, "03_sender_share.png")


def chart_keyword_frequency(df):
    kw_cols = [c for c in df.columns if c.startswith("kw_")]
    kw_totals = {c.replace("kw_", ""): df[c].sum() for c in kw_cols}
    kw_sorted = dict(sorted(kw_totals.items(), key=lambda x: x[1], reverse=True))

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(kw_sorted.keys(), kw_sorted.values(),
                  color=PALETTE[:len(kw_sorted)], edgecolor="none")
    ax.set_title("🔑 Keyword Frequency in Messages", fontsize=15, fontweight="bold", pad=14)
    ax.set_ylabel("Number of Messages")
    ax.tick_params(axis="x", rotation=20)
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                str(int(bar.get_height())), ha="center", va="bottom", fontsize=10)
    ax.grid(axis="y")
    fig.tight_layout()
    return save(fig, "04_keyword_frequency.png")


def chart_country_mentions(df):
    country_cols = [c for c in df.columns if c.startswith("country_")]
    totals = {c.replace("country_", ""): df[c].sum() for c in country_cols}
    totals = {k: v for k, v in totals.items() if v > 0}
    totals = dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))

    fig, ax = plt.subplots(figsize=(11, 5))
    colors = plt.cm.Set2(np.linspace(0, 1, len(totals)))
    bars = ax.barh(list(totals.keys()), list(totals.values()), color=colors, edgecolor="none")
    ax.set_title("🌍 Countries Mentioned in Scholarships", fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("Message Count")
    ax.invert_yaxis()
    for bar in bars:
        ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                str(int(bar.get_width())), va="center", fontsize=10)
    ax.grid(axis="x")
    fig.tight_layout()
    return save(fig, "05_country_mentions.png")


def chart_daily_trend(df):
    daily = df.groupby("date").size().reset_index(name="count")
    daily["date"] = pd.to_datetime(daily["date"])
    rolling = daily.set_index("date")["count"].rolling(7).mean()

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.fill_between(daily["date"], daily["count"], alpha=0.3, color=PALETTE[0])
    ax.plot(daily["date"], daily["count"], color=PALETTE[0], linewidth=1, alpha=0.6)
    ax.plot(rolling.index, rolling.values, color=PALETTE[1], linewidth=2.5, label="7-day rolling avg")
    ax.set_title("📈 Daily Message Volume (with 7-day Rolling Average)", fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Messages")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30)
    ax.legend()
    ax.grid(axis="y")
    fig.tight_layout()
    return save(fig, "06_daily_trend.png")


def chart_word_length_dist(df, mapping):
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, (sender, grp) in enumerate(df.groupby("sender")):
        label = mapping.get(sender, sender[-8:])
        ax.hist(grp["word_count"].clip(upper=100), bins=40,
                alpha=0.7, color=PALETTE[i], label=label, edgecolor="none")
    ax.set_title("📝 Distribution of Message Length (Words)", fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("Word Count per Message")
    ax.set_ylabel("Frequency")
    ax.legend()
    ax.grid(axis="y")
    fig.tight_layout()
    return save(fig, "07_word_length_dist.png")


def chart_hourly_line(df, mapping):
    hourly = df.groupby(["hour", "sender"]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(12, 5))
    for i, col in enumerate(hourly.columns):
        label = mapping.get(col, col[-8:])
        ax.plot(hourly.index, hourly[col], marker="o", color=PALETTE[i],
                linewidth=2.5, markersize=5, label=label)
    ax.set_title("⏰ Hourly Messaging Pattern", fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Messages")
    ax.set_xticks(range(0, 24))
    ax.legend()
    ax.grid()
    fig.tight_layout()
    return save(fig, "08_hourly_pattern.png")


def chart_top_words(df):
    import string
    STOPWORDS = set("""the a an and or of to in is are was were be been being
        have has had do does did will would could should may might shall
        this that these those it its with for from by at on about into
        your our their his her my we i you he she they what how when
        which if not no but so as up more out can all also just
        get got there here than then after before over under through
        omitted media ll ve re don didn hasn isn wasn weren won
        couldn wouldn shouldn im youre hes shes were theyre ive
        youve weve theyve id youd hed shed wed theyd let s t""".split())

    words = []
    for content in df["content"]:
        for w in content.lower().split():
            w = w.strip(string.punctuation + "*_~")
            if len(w) > 3 and w not in STOPWORDS and not w.startswith("+"):
                words.append(w)

    top40 = Counter(words).most_common(25)
    labels, counts = zip(*top40)

    fig, ax = plt.subplots(figsize=(12, 6))
    y_pos = range(len(labels))
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(labels)))
    ax.barh(list(y_pos), list(counts), color=colors, edgecolor="none")
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(list(labels), fontsize=11)
    ax.invert_yaxis()
    ax.set_title("🔠 Top 25 Most Frequent Words", fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("Frequency")
    ax.grid(axis="x")
    fig.tight_layout()
    return save(fig, "09_top_words.png")


def chart_monthly_keyword_trend(df):
    kw_cols = [c for c in df.columns if c.startswith("kw_")]
    monthly_kw = df.groupby("month")[kw_cols].sum()
    monthly_kw.columns = [c.replace("kw_", "") for c in monthly_kw.columns]

    fig, ax = plt.subplots(figsize=(14, 6))
    for i, col in enumerate(monthly_kw.columns):
        ax.plot(monthly_kw.index, monthly_kw[col], marker="o",
                color=PALETTE[i % len(PALETTE)], linewidth=2, label=col, markersize=4)
    ax.set_title("📊 Monthly Keyword Trends", fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("Month")
    ax.set_ylabel("Message Count")
    ax.tick_params(axis="x", rotation=45)
    ax.legend(ncol=2, fontsize=9)
    ax.grid()
    fig.tight_layout()
    return save(fig, "10_monthly_keyword_trend.png")


# ══════════════════════════════════════════════════════════════════════════════
# 4.  SUMMARY STATISTICS
# ══════════════════════════════════════════════════════════════════════════════

def build_summary(df: pd.DataFrame, mapping: dict) -> dict:
    sender_stats = {}
    for sender, grp in df.groupby("sender"):
        label = mapping.get(sender, sender[-8:])
        sender_stats[label] = {
            "messages":    int(len(grp)),
            "words":       int(grp["word_count"].sum()),
            "avg_words":   round(grp["word_count"].mean(), 2),
            "media":       int(grp["is_media"].sum()),
        }

    kw_cols = [c for c in df.columns if c.startswith("kw_")]
    keyword_totals = {c.replace("kw_", ""): int(df[c].sum()) for c in kw_cols}

    country_cols = [c for c in df.columns if c.startswith("country_")]
    country_totals = {c.replace("country_", ""): int(df[c].sum()) for c in country_cols}
    country_totals = {k: v for k, v in sorted(country_totals.items(), key=lambda x: -x[1]) if v > 0}

    peak_hour  = int(df["hour"].value_counts().idxmax())
    peak_day   = df["day_name"].value_counts().idxmax()
    peak_month = df["month"].value_counts().idxmax()
    busiest_date = str(df["date"].value_counts().idxmax())

    summary = {
        "group_name": "Bright Scholarship 146",
        "date_range": {
            "start": str(df["datetime"].min().date()),
            "end":   str(df["datetime"].max().date()),
        },
        "total_messages":  int(len(df)),
        "total_senders":   int(df["sender"].nunique()),
        "total_words":     int(df["word_count"].sum()),
        "avg_msg_per_day": round(len(df) / df["date"].nunique(), 2),
        "media_messages":  int(df["is_media"].sum()),
        "peak_hour":       peak_hour,
        "peak_day":        peak_day,
        "peak_month":      peak_month,
        "busiest_date":    busiest_date,
        "sender_stats":    sender_stats,
        "keyword_totals":  keyword_totals,
        "country_mentions": country_totals,
    }
    return summary


# ══════════════════════════════════════════════════════════════════════════════
# 5.  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def run():
    print("=" * 60)
    print("  WhatsApp Chat Analysis — Bright Scholarship 146")
    print("=" * 60)

    print("\n[1/4] Parsing chat file …")
    df, sys_events = parse_chat(CHAT_FILE)
    df = enrich(df)
    print(f"      {len(df):,} messages | {df['sender'].nunique()} senders | "
          f"{df['date'].nunique()} active days")

    # Friendly sender labels
    senders = df["sender"].value_counts().index.tolist()
    mapping = {senders[0]: "Admin A", senders[1]: "Admin B"}
    if len(senders) > 2:
        for i, s in enumerate(senders[2:], 3):
            mapping[s] = f"Member {i}"

    print("\n[2/4] Generating charts …")
    chart_messages_over_time(df, mapping)
    chart_hourly_heatmap(df, mapping)
    chart_sender_share(df, mapping)
    chart_keyword_frequency(df)
    chart_country_mentions(df)
    chart_daily_trend(df)
    chart_word_length_dist(df, mapping)
    chart_hourly_line(df, mapping)
    chart_top_words(df)
    chart_monthly_keyword_trend(df)

    print("\n[3/4] Building summary JSON …")
    summary = build_summary(df, mapping)
    summary_path = os.path.join(OUTPUT_DIR, "summary.json")
    with open(summary_path, "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"      Saved → {summary_path}")

    print("\n[4/4] Saving parsed CSV …")
    csv_cols = ["datetime", "date", "hour", "day_name", "month", "sender",
                "content", "word_count", "char_count", "is_media"]
    csv_path = os.path.join(OUTPUT_DIR, "messages.csv")
    df[csv_cols].to_csv(csv_path, index=False)
    print(f"      Saved → {csv_path}")

    print("\n✅  Analysis complete!")
    print(f"    Charts  → {CHART_DIR}")
    print(f"    Outputs → {OUTPUT_DIR}")
    return df, summary


if __name__ == "__main__":
    run()