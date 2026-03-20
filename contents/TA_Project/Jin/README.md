# Workblock Attendance ETL Pipeline

A reproducible ETL pipeline for transforming messy, semi-structured attendance data into a clean, analysis-ready dataset.

---

## 📌 Overview

This project processes raw attendance records (from spreadsheets or CSV exports) into a structured dataset with:

* Clean session metadata (date, time, timezone)
* Normalized participant names
* Host-attendance consistency
* Person-level enrichment (timezone, role, pod)
* Local-time features for both hosts and attendees

The pipeline is designed to handle **noisy human-entered data**, including:

* inconsistent formatting (dates, times, punctuation)
* missing or ambiguous timezones
* inconsistent name spellings
* partial or missing attendee lists

---

## 🧠 Pipeline Design

The pipeline follows a staged architecture:

```
Parse → Auto-correct → Enrich (pt1) → Human Review → Enrich (pt2)
```

### 1. `etl_parse_workblocks.py`

* Parses raw session text
* Extracts:

  * host
  * date / time
  * timezone
* Outputs:

  * `cleaned_workblocks.csv`
  * `workblocks_needing_review.csv`

---

### 2. `autocorrect.py`

* Fixes missing or inconsistent timezones
* Uses first-name heuristics for fallback mapping
* Outputs:

  * `timezone_corrected.csv`

---

### 3. `etl_enrich_workblocks_pt1.py`

* Assigns unique `session_id`
* Converts wide attendance → long format
* Ensures host is included in attendance
* Generates `person_alias.csv` for human validation

Outputs:

* `host_ensured_long.csv`
* `person_alias.csv` (requires manual review)

---

### 4. Human-in-the-loop Step

* Review and correct:

  * `person_alias.csv`
* This ensures accurate identity resolution

---

### 5. `etl_enrich_workblocks_pt2.py`

* Maps names → canonical identities
* Joins with `person_master.csv`
* Adds:

  * timezone
  * role
  * pod
* Generates local time features:

  * local datetime
  * hour
  * weekday

Output:

* `workblock_attendance_enriched.csv`

---

## 📂 Project Structure

```
data/
  interim/
  reference/
    person_master.csv
    person_alias.csv
  final_output/

src/
  etl_parse_workblocks.py
  autocorrect.py
  etl_enrich_workblocks_pt1.py
  etl_enrich_workblocks_pt2.py
```

---

## ⚙️ Key Features

### ✔ Robust text parsing

Handles inconsistent formats such as:

* "10/9 9am PT"
* "Oct 9 @ 0900"
* "9-10 AM EST"

---

### ✔ Human-in-the-loop design

Instead of forcing unreliable automation, the pipeline:

* surfaces ambiguity
* requires explicit review
* ensures high data quality

---

### ✔ Identity resolution via alias mapping

Separates:

* raw names (`attendee_raw`)
* normalized keys (`match_key`)
* canonical identities (`match_value`)

---

### ✔ Timezone-aware transformation

All sessions are:

* normalized to UTC
* converted into local time per participant

---

### ✔ Logging for observability

Each stage logs:

* row counts
* dropped rows
* unmatched names
* timezone failures

This enables traceability across the pipeline.

---

## 🚀 How to Run

Run each stage sequentially:

```bash
python etl_parse_workblocks.py
python autocorrect.py
python etl_enrich_workblocks_pt1.py
# manually review person_alias.csv
python etl_enrich_workblocks_pt2.py
```

---

## ⚠️ Known Limitations

* First-name-based timezone inference may fail for duplicates
* Alias mapping requires manual validation
* Free-text parsing may require updates for new formats

---

## 💡 Future Improvements

* Replace heuristic matching with probabilistic entity resolution
* Add Airflow DAG for orchestration
* Introduce automated data validation (Great Expectations)
* Store outputs in a database instead of CSV

---

## 🎯 Why This Matters

This project demonstrates:

* handling of messy real-world data
* modular ETL design
* human-in-the-loop data pipelines
* production-style logging and observability

---

## 👤 Author

Jinseok Oh
Postdoctoral Research Fellow
Interested in data engineering, wearable sensor analytics, and scalable pipelines

