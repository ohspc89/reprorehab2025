"""
This will update person_alias.csv
and make ensure_host_long.csv.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
import pandas as pd
from rapidfuzz import process, fuzz


LOGPATH = Path('./log')
INTERIM_PATH = Path("../data/interim")
REFERENCE_PATH = Path("../data/reference")


def setup_logger() -> logging.Logger:
    LOGPATH.mkdir(parents=True, exist_ok=True)

    # Logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        filename=str(LOGPATH / "etl_enrich_workblocks_pt1.log"),
        filemode="w"
    )
    return logging.getLogger(__name__)

logger = setup_logger()


def load_parsed_workblocks(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if path.suffix == ".csv":
        data = pd.read_csv(path)
    elif path.suffix == ".parquet":
        data = pd.read_parquet(path)
    else:
        raise ValueError(f"Neither a parquet nor a csv: {path}")

    required_cols = {
        "host",
        "date_clean",
        "datetime",
        "parse_status",
        "needs_review"
    }
    missing = required_cols - set(data.columns)
    if missing:
        raise ValueError(f"Required columns are missing: {sorted(missing)}")

    data["date_clean"] = pd.to_datetime(data["date_clean"], errors="coerce")
    data["datetime"]   = pd.to_datetime(data["datetime"], errors="coerce")

    return data.sort_values(by=["host", "date_clean"])


def apply_manual_corrections(df: pd.DataFrame, corrections: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    for _, row in corrections.iterrows():
        sid = row["session_id"]

        for col in corrections.columns:
            if col == "session_id":
                continue

            value = row[col]

            if pd.notna(value):
                df.loc[df["session_id"] == sid, col] = value

    return df


def build_session_id(df: pd.DataFrame) -> pd.DataFrame:
    df = (
        df.sort_values(["date_clean", "host", "datetime"],
                       na_position="last")
        .reset_index(drop=True).copy()
    )
    df["session_id"] = "WB" + (df.index + 1).astype(str).str.zfill(5)

    return df


def reshape_attendance_long(df_sessions: pd.DataFrame) -> pd.DataFrame:
    attendee_cols = [c for c in df_sessions.columns if c.startswith("Attendee")]

    if not attendee_cols:
        raise ValueError("No attendee columns found.")

    id_vars=["session_id",
             "host",
             "datetime",
             "date_clean",
             ]

    missing = set(id_vars) - set(df_sessions.columns)
    if missing:
        raise ValueError(f"Missing required session columns for melt: {sorted(missing)}")

    df_long = (
        df_sessions.melt(
            id_vars=id_vars,
            value_vars=attendee_cols,
            var_name="attendee_slot",
    value_name="attendee_raw",
        )
        .copy()
    )

    df_long["attendee_raw"] = df_long["attendee_raw"].astype("string").str.strip()
    df_long = df_long[df_long["attendee_raw"].notna() & (df_long["attendee_raw"] != "")]

    df_long = df_long.sort_values(
        ["date_clean", "host", "session_id", "attendee_slot"],
        na_position="last",
    ).reset_index(drop=True)

    return df_long

    
def _normalize_name(value: object) -> str | None:
    if pd.isna(value):
        return None

    s = str(value).strip()
    if not s:
        return None

    # Remove notes inside parentheses:
    s = re.sub(r"\s*\(.*?\)\s*", " ", s)

    s = re.sub(r"[!.,;:]+", "", s)
    s = re.sub(r"\s*-\s*", "-", s)

    # Leave only one whitespace
    s = re.sub(r"\s+", " ", s)

    return s.title().strip()


def ensure_host_attendance(df_long: pd.DataFrame,
                           df_sessions: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure each session has the host represented in the attendance long table.

    Rules:
      - If host already appears among attendee rows for that session, do nothing.
      - If host is missing, append one host row with attendance_source='host_added_missing'.
      - If a session had no attendee rows at all after melt/dropna, create one host-only row
        with attendance source='host_only_session.'
    """
    required_long_cols = {
        "session_id",
        "host",
        "datetime",
        "date_clean",
        "attendee_slot",
        "attendee_raw"
    }
    missing_long = required_long_cols - set(df_long.columns)
    if missing_long:
        raise ValueError(f"Missing required columns in df_long: {sorted(missing_long)}")

    required_session_cols = {
        "session_id",
        "host",
        "datetime",
        "date_clean",
    }

    missing_sessions = required_session_cols - set(df_sessions.columns)
    if missing_sessions:
        raise ValueError(f"Missing required columns in df_sessions: {sorted(missing_sessions)}")

    # Work on copies
    df_long = df_long.copy()
    df_sessions = df_sessions.copy()

    # Mark existing long rows
    df_long["attendance_source"] = "listed_attendee"
    df_long["is_host"] = False

    # Build normalized comparison keys
    df_long["host_match_key"] = df_long["host"].map(_normalize_name)
    df_long["attendee_match_key"] = df_long["attendee_raw"].map(_normalize_name)

    # Existing host-as-attendee rows
    host_present_by_session = (
        df_long.groupby("session_id")
        .apply(lambda g: (g["host_match_key"] == g["attendee_match_key"]).any(),
               include_groups=False)
        .rename("host_present")
        .reset_index()
    )

    # Join host-present flag back to session table
    session_status = df_sessions.merge(host_present_by_session, on="session_id",
                                       how="left")
    session_status["host_present"] = (
        session_status["host_present"]
        .fillna(False)
        .astype(bool)
    )

    # Sessions that disappeared entirely after dropping black attendees
    sessions_with_rows = set(df_long["session_id"].unique())
    session_status["has_any_attendee_rows"] = session_status["session_id"].isin(sessions_with_rows)

    rows_to_add = []

    for _, row in session_status.iterrows():
        if row["host_present"]:
            continue

        host_raw = row["host"]
        if pd.isna(host_raw) or str(host_raw).strip() == "":
        # No usable host, so skip adding anything
            continue

        if row["has_any_attendee_rows"]:
            source = "host_added_missing"
            slot = "host_added"
        else:
            source = "host_only_session"
            slot = "host_only"

        rows_to_add.append(
            {
                "session_id": row["session_id"],
                "host": row["host"],
                "datetime": row["datetime"],
                "date_clean": row["date_clean"],
                "attendee_slot": slot,
                "attendee_raw": row["host"],
                "attendance_source": source,
                "is_host": True,
                "host_match_key": _normalize_name(row["host"]),
                "attendee_match_key": _normalize_name(row["host"]),
            }
        )

    logger.info(f"Host rows added: {len(rows_to_add)}")

    if rows_to_add:
        df_added = pd.DataFrame(rows_to_add)
        df_long = pd.concat([df_long, df_added], ignore_index=True)

    # Mark listed rows that are actually host rows
    df_long["is_host"] = df_long["host_match_key"] == df_long["attendee_match_key"]

    # Final sort
    df_long = df_long.sort_values(
        ["date_clean", "datetime", "session_id", "attendance_source", "attendee_slot"],
        na_position="last",
    )

    # Clean up... if '-' is causing 

    return df_long


def first_token(value):
    if value is None or pd.isna(value):
        return None
    parts = str(value).split()
    return parts[0] if parts else None


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


def match_name_to_master(name_raw: str, pm: pd.DataFrame):
    """
    name_raw: name (match_key)
    pm: master CSV file (person_master.csv)
        the first two columns should be 'match_key' & 'match_value'
    """

    name_norm = _normalize_name(name_raw)
    if name_norm is None:
        return {
            "match_key": None,
            "match_value": None,
        }

    # 1) first-name exact
    first_norm = first_token(name_norm)
    exact_first = pm.loc[pm["First_name_norm"] == first_norm]
    if len(exact_first) == 1:
        row = exact_first.iloc[0]
        return {
            "match_key": name_norm,
            "match_value": row["person_name"],
        }

    # 2) fuzzy on first name
    first_name_choices = (
        pm["First_name_norm"].dropna().drop_duplicates().tolist()
    )
    if not first_name_choices:
        return {
            "match_key": name_norm,
            "match_value": None,
        }

    match = process.extractOne(first_norm, first_name_choices,
                               scorer=fuzz.WRatio)
    if match is None:
        return {
            "match_key": name_norm,
            "match_value": None,
        }

    candidate_first, score, _ = match
    # If same first names, make it 'ambiguous'
    candidate_rows = pm.loc[pm["First_name_norm"] == candidate_first]
    if score >= 90 and len(candidate_rows) == 1:
        row = candidate_rows.iloc[0]
        return {
            "match_key": name_norm,
            "match_value": row["person_name"],
        }
    return {
        "match_key": name_norm,
        "match_value": None,
    }


def save_outputs(df: pd.DataFrame, out_dir: str | Path = ".") -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(out_dir / "host_ensured_long.csv", index=False)


def main():
    # 1. Read the claned sheet
    sessions = load_parsed_workblocks(INTERIM_PATH / "post_parse/corrected_workblocks.csv")
    logger.info(f"Loaded sessions: {len(sessions)}")

    # 2. Make a primary key
    sessions = build_session_id(sessions)
    print("Sessions built")

    # 3. Make it a long format
    attendance_long = reshape_attendance_long(sessions)
    logger.info(f"Rows after melt: {len(attendance_long)}")

    # 4. Make sure the host is also 'attending' the workblock
    #    they hosted.
    attendance_long = ensure_host_attendance(attendance_long, sessions)
    logger.info(f"Final rows: {len(attendance_long)}")
    save_outputs(attendance_long,
                 INTERIM_PATH / "post_enrichment_pt1")

    # A person should Make sure the host is also 'attending' the workblock
    print(f"[INFO] Interim output is saved at: {(INTERIM_PATH / 'post_enrichment_pt1/host_ensured_long.csv').resolve()}")
    print("       This is required to run 'etl_enrich_workblocks_pt2.py")

    # 5-1. Load master file first
    person_master = load_reference_data(
        REFERENCE_PATH / "person_master.csv",
    )
    person_master = build_person_master(person_master)

    # 5-2. Export person_alias if there's non existing.
    #      Otherwise, load it and add new rows.
    alias = attendance_long["attendee_match_key"].unique()
    logger.info(f"Unique names: {len(alias)}")
    alias_df = pd.Series(alias).map(lambda x: match_name_to_master(x, person_master))
    alias_df = pd.DataFrame(alias_df.to_list())

    # Remove rows with NULL values first
    alias_df = alias_df[~alias_df["match_key"].isnull()]

    alias_path = REFERENCE_PATH / "person_alias.csv"
    if not alias_path.exists():
        alias_df.to_csv(alias_path, index=False)
    else:
        existing_alias_df = pd.read_csv(alias_path)
        new_names = set(alias_df["match_key"]) - set(existing_alias_df["match_key"])
        rows_to_add = alias_df[alias_df["match_key"].isin(new_names)]
        alias_df = pd.concat((existing_alias_df, rows_to_add),
                             ignore_index=True)
        alias_df.to_csv(alias_path, index=False)

    # A person must review and confirm 'person_alias.csv'.
    print(f"[INFO] Alias file saved at {alias_path.resolve()}")
    print("       Please review the file and confirm.")


if __name__ == "__main__":
    main()
