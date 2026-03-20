"""
This maps the alias to the full names of workblock attendees
and merges other metadata.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
import pandas as pd

LOGPATH = Path('./log')
DATAPATH = Path("../data")
INTERIM_PATH = DATAPATH / "interim"
REFERENCE_PATH = DATAPATH / "reference"
OUTPUT_PATH = DATAPATH / "final_output"

def setup_logger() -> logging.Logger:
    LOGPATH.mkdir(parents=True, exist_ok=True)

    # Logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        filename=str(LOGPATH / "etl_enrich_workblocks2.log"),
        filemode="w"
    )
    return logging.getLogger(__name__)

logger = setup_logger()


def load_alias_data(alias_path: str | Path) -> pd.DataFrame:
    alias_path = Path(alias_path)

    if not alias_path.exists():
        raise ValueError(f"{alias_path} does not exist.")

    alias_df = pd.read_csv(alias_path)

    required = {"match_key", "match_value"}
    missing = required - set(alias_df.columns)
    if missing:
        raise ValueError(f"Missing required alias columns: {sorted(missing)}")

    alias_df = alias_df.copy()
    alias_df["match_key"] = alias_df["match_key"].astype("string").str.strip()
    alias_df["match_value"] = alias_df["match_value"].astype("string").str.strip()

    return alias_df


def _normalize_name(value: object) -> str | None:
    if pd.isna(value):
        return None

    s = str(value).strip()
    if not s or s == "-":
        return None

    # Remove notes inside parentheses:
    s = re.sub(r"\s*\(.*?\)\s*", " ", s)

    s = re.sub(r"[!.,;:]+", "", s)
    s = re.sub(r"\s*-\s*", "-", s)

    # Leave only one whitespace
    s = re.sub(r"\s+", " ", s)

    return s.title().strip()


def build_person_master(master_df):
    pm = master_df.copy()

    pm["First_name_norm"] = pm["First_name"].map(_normalize_name)
    pm["Last_name_norm"] = pm["Last_name"].map(_normalize_name)
    pm["person_name"] = (
        pm["First_name"].fillna("").astype(str).str.strip()
        + " "
        + pm["Last_name"].fillna("").astype(str).str.strip()
    ).str.strip()
    pm["person_name_norm"] = pm["person_name"].map(_normalize_name)

    return pm


def load_reference_data(master_path: str | Path) -> pd.DataFrame:
    master_df = pd.read_csv(master_path)

    master_required = {"First_name", "Last_name", "Timezone", "Pod", "Role"}
    master_missing = master_required - set(master_df.columns)
    if master_missing:
        raise ValueError(f"Missing required master columns: {sorted(master_missing)}")

    return master_df

    
def apply_master(df_long: pd.DataFrame,
                 person_master: pd.DataFrame) -> pd.DataFrame:

    # person attributes
    pm_join = person_master[[
        "person_name_norm", "Timezone", "Pod", "Role"
    ]].drop_duplicates()

    out = df_long.merge(
        pm_join.rename(columns={
            "person_name_norm": "host_full_name",
            "Timezone": "host_timezone",
            "Pod": "host_pod",
            "Role": "host_role",
        }),
        on="host_full_name",
        how="left",
    )
    
    out = out.merge(
        pm_join.rename(columns={
            "person_name_norm": "attendee_full_name",
            "Timezone": "attendee_timezone",
            "Pod": "attendee_pod",
            "Role": "attendee_role",
        }),
        on="attendee_full_name",
        how="left",
    )

    return out


def _safe_localize_timestamp(ts: pd.Timestamp, tz_name: object) -> pd.Timestamp | pd.NaT:
    if pd.isna(ts) or pd.isna(tz_name):
        return pd.NaT

    try:
        ts = pd.Timestamp(ts)
        if ts.tzinfo is None:
            # upstream datetime should already be timezone-aware in ideal case,
            # but just in case, interpret as UTC fallback
            ts = ts.tz_localize("UTC")
        return ts.tz_convert(str(tz_name))
    except Exception:
        return pd.NaT
       
       
def add_local_time_features(df_long: pd.DataFrame) -> pd.DataFrame:
    df = df_long.copy()

    df["workblock_datetime_utc"] = pd.to_datetime(df["datetime"], errors="coerce", utc=True)

    df["attendee_local_datetime"] = [
        _safe_localize_timestamp(ts, tz)
        for ts, tz in zip(df["workblock_datetime_utc"], df["attendee_timezone"])
    ]
    df["host_local_datetime"] = [
        _safe_localize_timestamp(ts, tz)
        for ts, tz in zip(df["workblock_datetime_utc"], df["host_timezone"])
    ]

    df["attendee_local_date"] = df["attendee_local_datetime"].apply(
        lambda x: x.date() if pd.notna(x) else pd.NaT
    )
    df["attendee_local_hour"] = df["attendee_local_datetime"].apply(
        lambda x: x.hour if pd.notna(x) else pd.NA
    )
    df["attendee_local_weekday"] = df["attendee_local_datetime"].apply(
        lambda x: x.day_name() if pd.notna(x) else pd.NA
    )

    df["host_local_date"] = df["host_local_datetime"].apply(
        lambda x: x.date() if pd.notna(x) else pd.NaT
    )
    df["host_local_hour"] = df["host_local_datetime"].apply(
        lambda x: x.hour if pd.notna(x) else pd.NA
    )
    df["host_local_weekday"] = df["host_local_datetime"].apply(
        lambda x: x.day_name() if pd.notna(x) else pd.NA
    )

    return df
  

def build_attendance_enriched(df_long: pd.DataFrame) -> pd.DataFrame:
    df = df_long.copy()

    ordered_cols = [
        "workblock_datetime_utc",
        "date_clean",
        "host",
        "host_full_name",
        "host_timezone",
        "host_local_datetime",
        "host_local_date",
        "host_local_hour",
        "host_local_weekday",
        "attendee_raw",
        "attendee_full_name",
        "attendee_timezone",
        "attendee_local_datetime",
        "attendee_local_date",
        "attendee_local_hour",
        "attendee_local_weekday",
        "pod_assignment",
        "role",
        "is_host",
    ]

    existing = [c for c in ordered_cols if c in df.columns]
    df = df[existing].copy()

    df = df.sort_values(
        ["workblock_datetime_utc", "attendee_full_name"],
        na_position="last",
    ).reset_index(drop=True)

    return df
    
    
def save_outputs(
    attendance_enriched: pd.DataFrame,
    out_dir: str | Path,
) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    attendance_enriched.to_csv(out_dir / "workblock_attendance_enriched.csv", index=False)


def main():
    # pt1 should have been executed.
    post_enrich_path = INTERIM_PATH / "post_enrichment_pt1"
    attendance = pd.read_csv(post_enrich_path / "host_ensured_long.csv")
    logger.info(f"Loaded attendance rows: {len(attendance)}")

    # Load master file first
    master = load_reference_data(REFERENCE_PATH / "person_master.csv")

    # Load alias file
    alias = load_alias_data(REFERENCE_PATH / "person_alias.csv")
    alias["match_key"] = alias["match_key"].map(_normalize_name)
    logger.info(f"Unique alias keys: {attendance['attendee_match_key'].nunique()}")

    # map match_values to match_keys
    alias_map = dict(zip(alias["match_key"], alias["match_value"]))

    attendance["host_full_name"] = (
        attendance["host_match_key"].astype("string").str.strip().map(alias_map)
    )

    attendance["attendee_full_name"] = (
        attendance["attendee_match_key"].astype("string").str.strip().map(alias_map)
    )

    # Clear rows with null attendee_full_name
    before = len(attendance)
    attendance = attendance[~attendance["attendee_full_name"].isnull()]
    after = len(attendance)
    logger.warning(f"Rows dropped due to missing attendee_full_name: {before - after}")

    # Map master 
    master = build_person_master(master)
    attendance = apply_master(attendance, master)

    # # Time related measures added
    attendance = add_local_time_features(attendance)

    missing_tz = attendance["attendee_timezone"].isna().sum()
    logger.warning(f"Rows with missing attendee timezone after master join: {missing_tz}")

    # # Tidy up
    attendance = build_attendance_enriched(attendance)
    logger.info(f"Final rows: {len(attendance)}")

    # # Save output
    save_outputs(attendance, OUTPUT_PATH)
    print(f"[INFO] Final output saved at: {OUTPUT_PATH / 'workblock_attendance_enriched.csv'}")


if __name__ == "__main__":
    main()
