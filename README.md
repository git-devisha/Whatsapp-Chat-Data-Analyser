# Whatsapp-Chat-Data-Analyser
# 📊 WhatsApp Scholarship Community — Chat Analysis

> **Group:** Bright Scholarship 146  
> **Period Analyzed:** February 2025 – March 2026  
> **Total Messages:** ~1,700+ | **Active Senders:** 3 | **Keywords Tracked:** 7 | **Countries Detected:** 15

---

## 📁 Project Structure

```
whatsapp-scholarship-analysis/
│
├── data/
│   └── chat.txt                  # Raw WhatsApp chat export (.txt)
│
├── charts/                       # All generated chart PNGs
│   ├── 01_messages_over_time.png
│   ├── 02_activity_heatmap.png
│   ├── 03_sender_share.png
│   ├── 04_keyword_frequency.png
│   ├── 05_country_mentions.png
│   ├── 06_daily_trend.png
│   ├── 07_word_length_dist.png
│   ├── 08_hourly_pattern.png
│   ├── 09_top_words.png
│   └── 10_monthly_keyword_trend.png
│
├── static/
│   ├── messages.csv              # Parsed & enriched message data
│   └── summary.json              # Aggregated statistics
│
├── analysis.py                   # Main analysis & chart generation script
└── README.md                     # This file
```

---

## ⚙️ Setup & Usage

### Requirements

```bash
pip install pandas matplotlib seaborn numpy
```

### Export your WhatsApp Chat

1. Open WhatsApp → Group → **⋮ Menu → More → Export Chat**
2. Choose **Without Media**
3. Save as `chat.txt` inside the `data/` folder

### Run the Analysis

```bash
python analysis.py
```

This will:
- Parse the raw chat export
- Enrich messages with keyword & country flags
- Generate all 10 charts in `/charts`
- Save `messages.csv` and `summary.json` in `/static`

---

## 📈 Charts & Insights

### 1. `01_messages_over_time.png` — Messages Per Month by Sender
Tracks the volume of messages sent each month, broken down by Admin A, Admin B, and Member 3. The data shows consistent activity throughout 2025, with a peak in January 2026 (~165 messages). Admin A and Admin B each contribute roughly 50% of all messages, indicating a well-managed, dual-admin operation.

---

### 2. `02_activity_heatmap.png` — Activity Heatmap (Day × Hour)
A heatmap of message frequency across all days of the week and hours of the day. Activity is concentrated between **10 AM – 7 PM**, with notable spikes on **Friday afternoons (14:00–15:00)** and **Monday/Tuesday evenings**. Weekends (Saturday–Sunday) show lower but sustained engagement. Midnight-to-9 AM slots are virtually silent.

---

### 3. `03_sender_share.png` — Sender Comparison
Compares message count share (pie chart) and total words contributed (bar chart) per sender. Admin A holds **50.4%** of messages and Admin B holds **49.5%**, while Member 3 is negligible (0.1%). Both admins contribute ~8,000+ words each, confirming near-equal effort in content delivery.

---

### 4. `04_keyword_frequency.png` — Keyword Frequency in Messages
Counts how many messages contain high-signal keywords relevant to the scholarship domain:

| Keyword | Occurrences |
|---|---|
| Fully Funded | 1,137 |
| Scholarship | 614 |
| University | 605 |
| Internship | 140 |
| Fellowship | 123 |
| PhD / Masters | 72 |
| Visa / Jobs | 39 |

**Fully Funded** dominates, confirming the group's primary focus on no-cost opportunities. Internship and Fellowship content is secondary but present, suggesting audience interest in broader career development.

---

### 5. `05_country_mentions.png` — Countries Mentioned in Scholarship Messages
Identifies which countries appear most often in scholarship-related messages:

| Country | Mentions |
|---|---|
| USA | 148 |
| Canada | 136 |
| China | 128 |
| Germany | 113 |
| Australia | 113 |
| UK | 99 |
| Japan | 96 |

The **USA, Canada, and China** lead by a significant margin. This reflects where the most prominent fully-funded programs (Fulbright, Vanier, CSC) are based and points to the geographic aspirations of the community's audience.

---

### 6. `06_daily_trend.png` — Daily Message Volume (7-day Rolling Average)
Plots raw daily message count alongside a 7-day smoothed average. The rolling average consistently holds between **4–5 messages/day**, indicating a steady, reliable posting cadence. Minor dips appear around early April 2025, and a slight uptick is visible from January 2026 onward — likely reflecting new scholarship cycles opening.

---

### 7. `07_word_length_dist.png` — Distribution of Message Length (Words)
A histogram showing word counts per message for each sender. The distribution peaks at **8–9 words per message**, suggesting Admin A and Admin B favor short, link-and-description style posts rather than long-form narratives. Very few messages exceed 14 words.

---

### 8. `08_hourly_pattern.png` — Hourly Messaging Pattern
Line chart showing aggregate message counts per hour for each sender. Both admins show **synchronized posting patterns**, with peaks at **11 AM, 2 PM, 6 PM, and 11 PM**. Activity is zero between midnight and 9 AM, confirming this is a manually operated community (not a bot) aligned with Indian Standard Time.

---

### 9. `09_top_words.png` — Top 25 Most Frequent Words
After removing stopwords, the most used terms are: `funded`, `fully`, `2026`, `scholarships`, `scholarship`, `2025`, `university`, `program`, `international`, `ielts`, `internship`, `without`, `free`, `canada`, `online`, `china`, `study`, `fellowship`, `australia`, `germany`, `japan`, `summer`, `courses`, `government`.

This vocabulary profile confirms the group's heavy emphasis on **free, fully-funded international study programs**, with IELTS and government-backed programs being recurring themes.

---

### 10. `10_monthly_keyword_trend.png` — Monthly Keyword Trends
Tracks how each keyword category evolved over the 13-month period. **Fully Funded** content spikes sharply in **December 2025**, likely coinciding with deadlines for 2026 intake cycles. **Scholarship** and **University** mentions remain stable throughout. **Fellowship** sees periodic spikes, while **Visa/Jobs** and **PhD/Masters** remain niche but consistent.

---

## 🏭 Industry Applications

This analysis framework has direct applications across multiple sectors:

### 🎓 EdTech & Study Abroad Platforms
- Understand which **destination countries** and **program types** (fully funded vs. fellowship) attract the most interest
- Use keyword trend data to **time scholarship notifications and email campaigns** around peak community engagement
- Align content calendars with the **Friday afternoon / evening peak hours** identified in the heatmap

### 📣 Content & Social Media Marketing
- **Post timing optimization**: Schedule scholarship content between 10 AM–7 PM, with priority slots at 11 AM and 2 PM for maximum reach
- Replicate the **8–10 word message format** that dominates engagement in this community — concise, scannable announcements outperform long posts
- Keyword frequency data helps identify the **exact vocabulary** that resonates with scholarship-seeking audiences

### 🏛️ NGOs, Government & Scholarship Bodies
- Track **geographic demand signals**: USA, Canada, Germany, and Australia dominate mentions — funders can use this to assess where awareness campaigns are needed
- Monitor month-on-month keyword trends to understand **when students are actively searching**, enabling better deadline and information release planning

### 📊 Market Research & Competitive Intelligence
- Community-level chat data provides **organic, unfiltered demand signals** that are more authentic than survey data
- Dual-admin structure and consistent daily volume (~5 msgs/day) can be benchmarked as a **best practice model** for running high-retention Telegram/WhatsApp scholarship channels

### 🤖 AI & Recommendation Systems
- The enriched `messages.csv` can be used to train **scholarship recommendation NLP models**
- Country and keyword co-occurrence data supports building **personalized opportunity matching engines**
- Message timing patterns can inform **push notification scheduling models** for mobile apps

---

## 📌 Key Findings at a Glance

| Metric | Value |
|---|---|
| Most active month | January 2026 |
| Peak posting hour | 11 AM & 2 PM (IST) |
| Peak posting day | Friday |
| Most mentioned country | USA (148) |
| Top keyword | Fully Funded (1,137 msgs) |
| Admin A vs B share | 50.4% vs 49.5% |
| Avg message length | ~8–9 words |
| Daily posting rate | ~5 messages/day |

---

## 🔒 Privacy Note

All sender identities are anonymized as `Admin A`, `Admin B`, and `Member 3`. No phone numbers or personal identifiers are stored or exposed in any output file.

---

## 📄 License

This project is for educational and research purposes. If using community chat data, ensure you have appropriate consent from group members in accordance with applicable data privacy laws (e.g., DPDPA 2023 in India, GDPR in Europe).

---

*Generated by WhatsApp Chat Analysis Pipeline · Bright Scholarship 146 · 2025–2026*
