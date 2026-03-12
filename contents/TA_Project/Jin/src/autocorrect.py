"""
Take `cleaned_workblocks.csv` generated from the execution of
`etl_parse_workblocks.py` and fill in timezones to fill in
as many missing datetimes as possible
"""
import logging
import re
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz, process

DATAPATH = Path('../data')
REFERENCE_PATH = DATAPATH / 'reference'
INTERIM_PATH = DATAPATH / 'interim'

df = pd.read_csv(INTERIM_PATH / 'cleaned_workblocks.csv')
metadata = pd.read_csv(REFERENCE_PATH / 'person_master.csv')

# Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filename=str(INTERIM_PATH / "autocorrect.log"),
    filemode="w"
)
logger = logging.getLogger(__name__)


def normalize_name(s: str) -> str:
    """Normalize person name for fuzzy matching."""
    if pd.isna(s):
        return ""
    return str(s).replace(".", "").replace(",", "").strip()


def extract_time_token(s: str) -> str|None:
    """
    Extract time token like 9AM, 10pm, 3P, 7a from a string.
    Returns None if not found.
    """
    if pd.isna(s):
        return None
    match = re.search(r"\d{1,2}[ap]m?", str(s), flags=re.I)
    return match.group(0) if match else None


def get_candidate_pool(host: str, names: list[str]) -> list[str]:
    if not host:
        return []

    pool = [
        n for n in names
        if n
        and n[0] == host[0]
    ]
    return pool if pool else names


# Only rows needing timezone correction
timezone_mask = df["review_reason"].str.contains("missing_timezone", na=False)

# Prepare metadata
metadata = metadata.copy()
metadata["First_name_norm"] = metadata["First_name"].map(normalize_name)


# Normalized name -> timezone
name_to_timezone = dict(zip(
    metadata["First_name_norm"],
    metadata["Timezone"]
    )
)

# Candidate names for rapidfuzz
all_names_norm = metadata["First_name_norm"].tolist()

# Work on subset only
target_idx = df.index[timezone_mask]

for k in target_idx:
    host = df.at[k, "host"]
    host_norm = normalize_name(host)
    pool = get_candidate_pool(host_norm, all_names_norm)

    # best fuzzy match
    match = process.extractOne(host_norm,
                               pool,
                               scorer=fuzz.WRatio)

    if match is None:
        logger.warning("[WARN] No name match found for host=%s",
                       host)
        continue

    candidate_name, score, _ = match
    if score < 75:
        logger.warning("[WARN] Low-confidence match for host=%s candidate=%s score=%s",
                       host,
                       candidate_name,
                       score)
        continue

    matched_timezone = name_to_timezone[candidate_name]

    logger.info(
        "name given=%s matched=%s score=%s",
        host,
        candidate_name,
        score
    )

    df.at[k, "tz_full"] = matched_timezone

    date_clean = df.at[k, "date_clean"]
    time_clean = df.at[k, "time_clean"]

    # if date is missing, cannot construct datetime
    if pd.isna(date_clean):
        df.at[k, "datetime"] = pd.NaT
        continue

    # if time missing, try recovering it from ID_clean
    if pd.isna(time_clean):
        recovered_time = extract_time_token(df.at[k, "ID_clean"])
        if recovered_time is not None:
            time_clean = recovered_time
            df.at[k, "time_clean"] = recovered_time
        else:
            df.at[k, "datetime"] = pd.NaT
            continue

    naive = pd.to_datetime(f"{date_clean} {time_clean}", errors="coerce")

    if pd.isna(naive):
        df.at[k, "datetime"] = pd.NaT
    else:
        df.at[k, "datetime"] = naive.tz_localize(matched_timezone)

df.to_csv(INTERIM_PATH / "timezone_corrected.csv", index=False)
logger.info("Timezone corrected file: %s",
            INTERIM_PATH / 'timezone_corrected.csv')
