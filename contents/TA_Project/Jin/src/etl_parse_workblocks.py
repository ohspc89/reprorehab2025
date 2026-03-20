"""
Read the google spreadsheet and parse texts
Please provide the url at the bottom of this script.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Iterable

import pandas as pd

LOGPATH = Path('./log')
DATAPATH = Path('../data')
POSTPARSE_PATH = DATAPATH / 'interim/post_parse'


def setup_logger() -> logging.Logger:
    LOGPATH.mkdir(parents=True, exist_ok=True)

    # Logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        filename=str(LOGPATH / "etl_parse_workblocks.log"),
        filemode="w"
    )
    return logging.getLogger(__name__)

logger = setup_logger()

# -------------------------
# Configuration
# -------------------------
TZ_MAP = {
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
    "CEST": "Europe/Berlin",
}

# Fall-back timezone if a row has no timezone token.
# Set to None if you prefer to leave datetime as NaT unless tz is explicit.
DEFAULT_TIMEZONE = None

# Used only when dates omit the year.
# ReproRehab2025: 2025/09 - 2026/04
DEFAULT_YEAR_BY_MONTH = {
    1: 2026,
    2: 2026,
    3: 2026,
    4: 2026,
    5: 2026,
    9: 2025,
    10: 2025,
    11: 2025,
    12: 2025
}

# Hi Devin, fancy emojis! But we don't need them.
EMOJI_RE = re.compile(
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
    flags=re.UNICODE,
)

UNICODE_TRANSLATION = str.maketrans({
    "\u2010": "-",  # hyphen
    "\u2011": "-",  # non-breaking hyphen
    "\u2012": "-",  # figure dash
    "\u2013": "-",  # en dash
    "\u2014": "-",  # em dash
    "\u2015": "-",  # horizontal bar
    "\u2212": "-",  # minus sign
    "\u00A0": " ",  # non-breaking space
})

# Y, m, d are separated by '.', '/', or '-'.
DATE_RE = re.compile(r"(?<!\d)(\d{1,2}[./-]\d{1,2}(?:[./-]\d{2,4})?)(?!\d)")

# Timezone pattern
TZ_RE = re.compile(r"\b(?:P(?:S|D)?T|M(?:S|D)?T|C(?:S|D)?T|E(?:S|D)?T|CEST)\b", re.I)

RANGE_RE = re.compile(
    r"(?<![:\d])"
    r"(?P<start>\d{1,2}(?::\d{2})?|\d{3,4})"
    r"\s*(?:-|to)\s*"
    r"(?P<end>\d{1,2}(?::\d{2})?|\d{3,4})"
    r"\s*(?P<suffix>[AaPp](?:[Mm])?)?"
)

SINGLE_TIME_RE = re.compile(
    r"\b(?P<time>\d{1,2}(?::\d{2})?|\d{3,4})\s*(?P<suffix>[AaPp](?:[Mm])?)?\b",
    re.I
)

# -------------------------
# Loading / basic cleaning
# -------------------------
def load_attendance(source: str | Path) -> pd.DataFrame:
    """source can be a URL or a filepath"""
    src = str(source)
    if src.startswith(("http://", "https://")):
        if "format=csv" in src or src.endswith(".csv"):
            return pd.read_csv(src)
        return pd.read_excel(src)

    path = Path(src)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path)


def rename_attendance_columns(df: pd.DataFrame) -> pd.DataFrame:
    new_names = ["ID"] + [f"Attendee_{i}" for i in range(1, len(df.columns))]
    return df.rename(columns=dict(zip(df.columns, new_names))).copy()


def normalize_session_text(text: object) -> str:
    """Normalize the free-text session column before parsing."""
    if pd.isna(text):
        return text

    s = str(text)

    # Remove EMOJI
    s = EMOJI_RE.sub("", s)

    # remove unicode whitespace (zero-width chars)
    s = re.sub(r"[\u200B-\u200D\uFEFF]", "", s)

    # normalize punctuation
    s = s.translate(UNICODE_TRANSLATION)

    # normalize am/pm
    s = re.sub(r"\ba\.?\s*m\.?\b", "am", s, flags=re.I)
    s = re.sub(r"\bp\.?\s*m\.?\b", "pm", s, flags=re.I)

    # normalize separators
    s = re.sub(r"\s*@\s*", " ", s)
    s = re.sub(r"\bat\b", " ", s, flags=re.I)

    # collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()

    return s

# --------------------
# Parsing helpers
# --------------------
def normalize_date(date_raw: str | pd.NA) -> tuple[str | pd.NA, bool]:
    if pd.isna(date_raw):
        return pd.NA, False

    token = str(date_raw).replace(".", "/").replace("-", "/")
    parts = token.split("/")
    if len(parts) == 2:
        month = int(parts[0])
        year = DEFAULT_YEAR_BY_MONTH.get(month, None)
        if year is None:
            return pd.NA, False
        return f"{int(parts[0])}/{int(parts[1])}/{year}", True

    if len(parts) == 3:
        month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
        if year < 100:
            year += 2000
        return f"{month}/{day}/{year}", False

    return pd.NA, False


def infer_ampm_from_hour(hour: int) -> str:
    # Conservative default for this workbook
    return "am" if 6 <= hour < 12 else "pm"


def normalize_time_token(token: str, suffix: str | None) -> tuple[str, bool]:
    token = token.strip()
    suffix = "" if suffix is None else suffix.strip().lower()

    if re.fullmatch(r"\d{3,4}", token):
        if len(token) == 3:
            token = f"{token[0]}:{token[1:]}"
        else:
            token = f"{token[:2]}:{token[2:]}"

    inferred = False
    if suffix in {"a", "p"}:
        suffix += "m"
    if suffix not in {"am", "pm"}:
        hour = int(token.split(":")[0])
        suffix = infer_ampm_from_hour(hour)
        inferred = True
    return f"{token}{suffix}", inferred

def localize_datetime(date_clean: str | pd.NA,
                      time_clean: str | pd.NA,
                      tz_full: str | pd.NA) -> pd.Timestamp | pd.NaT:
    if pd.isna(date_clean) or pd.isna(time_clean) or pd.isna(tz_full):
        return pd.NaT

    naive = pd.to_datetime(f"{date_clean} {time_clean}", errors="coerce")
    if pd.isna(naive):
        return pd.NaT
    return naive.tz_localize(tz_full)


def parse_session_text(text: str) -> dict:
    s = normalize_session_text(text)

    date_match = DATE_RE.search(s)
    date_raw = date_match.group(1) if date_match else pd.NA
    date_clean, year_inferred = normalize_date(date_raw)

    tz_match = TZ_RE.search(s)
    timezone_raw = tz_match.group(0).upper() if tz_match else pd.NA
    timezone_inferred = False
    if pd.isna(timezone_raw) and DEFAULT_TIMEZONE is not None:
        timezone_raw = DEFAULT_TIMEZONE
        timezone_inferred = True
    tz_full = TZ_MAP.get(str(timezone_raw), pd.NA) if not pd.isna(timezone_raw) else pd.NA

    if date_match:
        host = s[:date_match.start()].strip(" -") or pd.NA
        tail = s[date_match.end():]
    else:
        host = pd.NA
        tail = s

    time_raw = pd.NA
    time_clean = pd.NA
    time_inferred_ampm = False

    range_match = RANGE_RE.search(tail)
    if range_match:
        time_raw = range_match.group("start")
        time_clean, time_inferred_ampm = normalize_time_token(
            range_match.group("start"),
            range_match.group("suffix"),
        )
    else:
        single_match = SINGLE_TIME_RE.search(tail)
        if single_match:
            time_raw = single_match.group("time")
            time_clean, time_inferred_ampm = normalize_time_token(
                single_match.group("time"),
                single_match.group("suffix"),
            )

    dt = localize_datetime(date_clean, time_clean, tz_full)

    reasons: list[str] = []
    if pd.isna(date_raw):
        reasons.append("missing_date")
    if pd.isna(time_raw):
        reasons.append("missing_time")
    if pd.isna(timezone_raw):
        reasons.append("missing_timezone")
    if year_inferred:
        reasons.append("year_inferred")
    if time_inferred_ampm:
        reasons.append("ampm_inferred")
    if not pd.isna(timezone_raw) and pd.isna(tz_full):
        reasons.append("unknown_timezone")
    if not pd.isna(date_clean) and not pd.isna(time_clean) and not pd.isna(tz_full) and pd.isna(dt):
        reasons.append("datetime_parse_failed")

    if not reasons:
        parse_status = "OK"
    elif any(r in reasons for r in ["missing_date", "missing_time", "unknown_timezone",
                                    "datetime_parse_failed"]):
        parse_status = "ERROR"
    else:
        parse_status = "REVIEW"

    return {
        "host"      :         host,
        "date_raw"  :         date_raw,
        "date_clean":         date_clean,
        "year_inferred":      year_inferred,
        "time_raw":           time_raw,
        "time_clean":         time_clean,
        "time_inferred_ampm": time_inferred_ampm,
        "timezone_raw":       timezone_raw,
        "tz_full":            tz_full,
        "timezone_inferred":  timezone_inferred,
        "datetime":           dt,
        "parse_status":       parse_status,
        "needs_review":       parse_status != "OK",
        "review_reason":     ";".join(reasons),
    }


# ---------------
# Main ETL
# ---------------
def transform_workblock_attendance(source: str | Path) -> pd.DataFrame:
    df = load_attendance(source)
    df = rename_attendance_columns(df)
    df = df.loc[~df.isna().all(axis=1)].copy()

    # Keep banner rows like "(CSM Week)" out of the parsed session dataset.
    df["ID_original"] = df["ID"]
    df["ID_clean"] = df["ID"].map(normalize_session_text)
    df = df.loc[~df["ID_clean"].str.fullmatch(r"\([^)]*\)", na=False)].copy()

    parsed = df["ID_clean"].map(parse_session_text)
    parsed_df = pd.DataFrame(parsed.tolist(), index=df.index)

    logger.info(parsed_df["parse_status"].value_counts().to_dict())
    logger.info(parsed_df["review_reason"].value_counts().head(10).to_dict())
    logger.info(f"Rows needing review: {parsed_df['needs_review'].sum()}")

    attendee_cols = [c for c in df.columns if c.startswith("Attendee_")]
    out = pd.concat([df[["ID_original", "ID_clean"] + attendee_cols], parsed_df], axis=1)

    ordered_cols = [
        "ID_original",
        "ID_clean",
        "host",
        "date_raw",
        "date_clean",
        "year_inferred",
        "time_raw",
        "time_clean",
        "time_inferred_ampm",
        "timezone_raw",
        "tz_full",
        "timezone_inferred",
        "datetime",
        "parse_status",
        "needs_review",
        "review_reason",
    ] + attendee_cols

    return out[ordered_cols].sort_values(["date_clean", "time_clean", "host"], na_position="last")


def save_outputs(df: pd.DataFrame, out_dir: str | Path = ".") -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(out_dir / "cleaned_workblocks.csv", index=False)
    df.loc[df["needs_review"]].to_csv(out_dir / "workblocks_needing_review.csv", index=False)


if __name__ == "__main__":
    # Example local file.
    SOURCE = "https://docs.google.com/spreadsheets/d/1reeteJsj4_DjMMyLbgeQQ0_HjLEkHDONV0tHII0TmwI/export?format=csv&gid=0"
    result = transform_workblock_attendance(SOURCE)
    save_outputs(result, POSTPARSE_PATH)
    print(f"[INFO] Interim file saved at: {(POSTPARSE_PATH / 'cleaned_workblocks.csv').resolve()}")
