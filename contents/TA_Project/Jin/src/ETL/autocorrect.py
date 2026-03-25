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

LOGPATH = Path('../log')
DATAPATH = Path('../../data')
REFERENCE_PATH = DATAPATH / 'reference'
POSTPARSE_PATH = DATAPATH / 'interim/post_parse'


def setup_logger() -> logging.Logger:
    LOGPATH.mkdir(parents=True, exist_ok=True)

    # Logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        filename=str(LOGPATH / "autocorrect.log"),
        filemode="w"
    )
    return logging.getLogger(__name__)

logger = setup_logger()


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

    pool = [n for n in names if n and n[0] == host[0]]
    return pool if pool else names


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(POSTPARSE_PATH / "cleaned_workblocks.csv")
    metadata = pd.read_csv(REFERENCE_PATH / "person_master.csv")
    return df, metadata


def correct_timezones(
    df: pd.DataFrame,
    metadata: pd.DataFrame,
    logger: logging.Logger,
) -> pd.DataFrame:
    df = df.copy()
    metadata = metadata.copy()

    # Only rows needing timezone correction
    timezone_mask = df["review_reason"].str.contains("missing_timezone", na=False)

    # Prepare metadata
    metadata["First_name_norm"] = metadata["First_name"].map(normalize_name)

    # Normalized name -> timezone
    name_to_timezone = dict(
        zip(metadata["First_name_norm"], metadata["Timezone"])
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
        # If the fuzzy score is lower than 75,
        # review the correction.
        if score < 75:
            logger.warning("[WARN] Low-confidence match for host=%s candidate=%s score=%s",
                           host,
                           candidate_name,
                           score)
            continue

        matched_timezone = name_to_timezone.get(candidate_name)
        if pd.isna(matched_timezone):
            logger.warning(
                "No timezone found for candidate=%s (host=%s)",
                candidate_name,
                host,
            )
            continue

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
            continue

        try:
            df.at[k, "datetime"] = naive.tz_localize(matched_timezone)
        except Exception as e:
            logger.warning(
                "Failed to localize datetime for host=%s timezone=%s error=%s",
                host,
                matched_timezone,
                e,
            )
            df.at[k, "datetime"] = pd.NaT
            continue

    return df


def save_outputs(df: pd.DataFrame, logger: logging.Logger) -> None:
    out_path = POSTPARSE_PATH / "timezone_corrected.csv"
    df.to_csv(out_path, index=False)
    logger.info("Timezone corrected file: %s", out_path)


def main() -> None:
    df, metadata = load_inputs()
    corrected = correct_timezones(df, metadata, logger)
    save_outputs(corrected, logger)


if __name__ == "__main__":
    main()
