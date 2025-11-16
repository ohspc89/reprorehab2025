#%% Reading data
import re  # Regular expression(regex)
import numpy as np
import pandas as pd
# Google spreadsheet - link should be replaced
# every year.
URL = "https://docs.google.com/spreadsheets/d/1reeteJsj4_DjMMyLbgeQQ0_HjLEkHDONV0tHII0TmwI/export?format=csv&gid=0"
out = pd.read_csv(URL)

#################
# Data cleaning #
#################
#%% 1. Rename columns
# The first column name is too long,
# and from the third column names are non-existent.
out.rename(
        columns=dict(zip(out.columns,
                         ['ID']+[f'Attendee_{i}' for i in range(len(out.columns)-1)])),
           inplace=True)

# There are 'blank' rows to separate weeks. Drop them.
out = out.loc[~out.isna().all(axis=1)]
out = out.copy()

# Hi Devin, fancy emojis! But we don't need them.
emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002700-\U000027BF"  # dingbats
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA70-\U0001FAFF"  # more emojis
        "\U00002600-\U000026FF"  # misc symbols
        "]+",
        flags=re.UNICODE)
out["ID_clean"] = out["ID"].apply(lambda x: emoji_pattern.sub("", str(x))).str.strip()

# Clean ID_clean one more time
out["ID_clean"] = (
        out["ID_clean"]
        .str.replace(",", " ", regex=False)
        # Dates like "10/25.25" -> "10/25/25"
        .str.replace(r'(\d{1,2})\.(\d{2})', r'\1/\2', regex=True)
        # Times like "2pmet" -> "2pm et"
        .str.replace(r'(\d{1,2}(?::\d{2})?\s*[AaPp][Mm]?)([A-Za-z]{1,3}[Tt])',
                     r'\1 \2', regex=True)
        )
#%% 2. Extract time and timezone strings
"""
Date formats to be matched:
  - mm/dd
  - mm-dd
  - mm/dd/yy
  - mm/dd/yyyy
  - mm-dd-yy
  - mm-dd-yyyy
"""
DATE_RE = re.compile(
    r'(?<!\d)(\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b)')
"""
Timezone formats to be matched (lower case allowed):
  - ET/EST/EDT
  - PT/PST/PDT
  - CT/CST/CDT
  - MT/MST/MDT
"""
TZ_RE   = re.compile(r'\b(E|e|P|p|C|c|M|m)(S|s|D|d)?[Tt]\b')


def extract_time_and_tz(text: str):
    """extract time and timezone(tz) from strings"""
    if pd.isna(text):
        return pd.Series([pd.NA, pd.NA])
    s = str(text)

    # Find the date first and only look AFTER it
    m_date = DATE_RE.search(s)
    tail = s[m_date.end():] if m_date else s

    # Range First: 2-3pm, 1-2 pm, 4 to 5 pm
    m = re.search(
        # don't count if it starts with ':'
            r'(?<![:\d])'
            r'\b(\d{1,2}(?::\d{2})?)'
            r'\s*(?:-|to)\s*'
            r'\d{1,2}(?::\d{2})?'
            r'\s*([AaPp](?:[Mm])?)?',
            tail)
    # timezone string extracted
    m_tz = TZ_RE.search(s)
    tz_str = m_tz.group(0).upper() if m_tz else pd.NA

    if m:
        hour = m.group(1)
        suffix = m.group(2) or ""
        # not sure if this is the right behavior... but '11-12pm', then '11am' 
        if hour=="11":
            time_str = f"{hour}am"
        else:
            time_str = f"{hour}{suffix}".strip()

        # normalize "4p" -> "4pm"
        if re.search(r'[AaPp]$', time_str) and not re.search(r'[Mm]$', time_str):
            time_str = time_str + "m"

        return pd.Series([time_str, tz_str])

    # Try hh:mm (e.g., "3:30 - 4:30")
    m = re.search(r'\b(\d{1,2}:\d{2})\b', tail)
    if m:
        time_str = m.group(1)
        return pd.Series([time_str, tz_str])

    # Try explicit am/pm
    m = re.search(r'\b(\d{1,2}(?::\d{2})?\s*[AaPp][Mm]?)\b', tail)
    if m:
        time_str = m.group(1).strip()
        # Normalize "5p" -> "5pm"
        if re.search(r'[AaPp]$', time_str) and not re.search(r'[Mm]$', time_str):
            time_str = time_str + 'm'

        return pd.Series([time_str, tz_str])

    # Nothing time-like found, but try to find timezone one last time
    # (timezone strings are typically at the end)
    return pd.Series([pd.NA, tz_str])

# Map your timezone abbreviations -> IANA names
tz_map = {
        "PT": "America/Los_Angeles",
        "PST": "America/Los_Angeles",
        "PDT": "America/Los_Angeles",
        "ET": "America/New_York",
        "EST": "America/New_York",
        "EDT": "America/New_York",
        "CT": "America/Chicago",
        "CST": "America/Chicago",
        "CDT": "America/Chicago",
        "MT": "America/Denver",
        "MST": "America/Denver",
        "MDT": "America/Denver",
        }

# ex. 'Andrew - 10/7/25 3-4pm pst' -> '3am' & 'pst'
out[["time", "timezone"]] = out["ID_clean"].apply(extract_time_and_tz)
# 'pst' -> 'PST'
out["timezone"] = out["timezone"].str.upper()
# 'PST' -> 'America/Los_Angeles'
out["tz_full"] = out["timezone"].map(tz_map)

# --- host ---
host_pattern = rf'^\s*(.*?)(?:\s*-\s*)?\s*{DATE_RE.pattern}'
out["host"] = (
        out["ID_clean"]
        .str.extract(host_pattern)[0]
        .str.strip()
        )

# --- time: specify am/pm if missing ---
def add_ampm(time: str):
    """add 'am' or 'pm' at the end"""
    if pd.isna(time):
        return pd.NA
    if 'am' in time.lower() or 'pm' in time.lower():
        return time
    if ':' in time:
        hour_min = time.split(':')
        hour = hour_min[0]
        # This is a PURE guess - not stable
        if int(hour) >= 9 and int(hour) < 12:
            return time+"am"
        return time+"pm"
    if int(time) >= 9 and int(time) < 12:
        return time+"am"
    return time+"pm"


# --- time (am/pm) --- 
out["time"] = out["time"].apply(add_ampm)

# --- date ---
out["date"] = (
    out["ID_clean"]
    .str
    .extract(DATE_RE.pattern, expand=False)
)
out["date_clean"] = (
    out["date"]
    .str
    .replace(r"[-\.]", "/", regex=True)
)

# M/D -> M/D/2025
mask_no_year = out["date_clean"].str.count("/") == 1
out.loc[mask_no_year, "date_clean"] = (
        out.loc[mask_no_year, "date_clean"] + "/2025"
        )

# Build datetime string
date_str = out["date_clean"].astype("string")
time_str = out["time"].astype("string")

dt_str = (date_str.fillna("") + " " + time_str)

# I must be missing something,
# but vectorization doesn't work.
dt_naive = []
for i, dst in enumerate(dt_str):
    dt_naive.append(pd.to_datetime(dst, errors="coerce"))


def localize_row(d, tz):
    if pd.isna(d) or pd.isna(tz):
        return pd.NaT
    # If already timezone-aware, just return it
    if d.tz is not None:
        return d
    return d.tz_localize(tz)


# Localize explicitly
out["datetime"] = [
        localize_row(d, tz)
        for d, tz in zip(dt_naive, out["tz_full"])
        ]

attendee_cols = out.columns[out.columns.str.match('Attendee')]
new_col_order = ['ID_clean', 'time', 'timezone',
                 'tz_full', 'host', 'datetime',
                 'date_clean'] + list(attendee_cols)

# Save processed output
out_new = out[new_col_order]
out_new.to_csv('cleaned.csv', index=False)