from __future__ import annotations

import re
from pathlib import Path
import pandas as pd


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

    return data


def apply_manual_corrections(df: pd.DataFrame, corrections_path: str) -> pd.DataFrame:
    corrections = pd.read_csv(corrections_path)
    corrections = build_session_id(corrections)

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
             "parse_status",
             "needs_review",
             "review_reason"
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


def _normalize_name_for_match(value: object) -> str | None:
    """Lightweight normalization for host/attendee matching only."""
    if pd.isna(value):
        return None
    s = str(value).strip()
    if not s:
        return None

    # collapse spaces
    s = re.sub(r"\s+", " ", s)

    # strip trailing punctuation
    s = re.sub(r"[.,;:]+$", "", s)

    return s.title()


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
        "parse_status",
        "needs_review",
        "review_reason",
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
        "parse_status",
        "needs_review",
        "review_reason"
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
    df_long["host_match_key"] = df_long["host"].map(_normalize_name_for_match)
    df_long["attendee_match_key"] = df_long["attendee_raw"].map(_normalize_name_for_match)

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
    session_status["host_present"] = session_status["host_present"].fillna(False)

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
                "parse_status": row["parse_status"],
                "needs_review": row["needs_review"],
                "review_reason": row["review_reason"],
                "attendee_slot": slot,
                "attendee_raw": row["host"],
                "attendance_source": source,
                "is_host": True,
                "host_match_key": _normalize_name_for_match(row["host"]),
                "attendee_match_key": _normalize_name_for_match(row["host"]),
            }
        )

    if rows_to_add:
        df_added = pd.DataFrame(rows_to_add)
        df_long = pd.concat([df_long, df_added], ignore_index=True)

    # Mark listed rows that are actually host rows
    df_long["is_host"] = df_long["host_match_key"] == df_long["attendee_match_key"]

    # Final sort
    df_long = df_long.sort_values(
        ["date_clean", "datetime", "session_id", "attendance_source", "attendee_slot"],
        na_position="last",
    ).reset_index(drop=True)

    return df_long
    
    
def normalize_person_name(value: object) -> str | None:
    if pd.isna(value):
        return None

    s = str(value).strip()
    if not s:
        return None

    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[.,;:]+$", "", s)
    s = re.sub(r"\s*-\s*", "-", s)

    s = s.title()

    return s


def load_reference_data(
    alias_path: str | Path,
    master_path: str | Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    alias_df = pd.read_csv(alias_path)
    master_df = pd.read_csv(master_path)

    alias_required = {"alias_raw", "alias_norm", "person_name"}
    master_required = {"person_name", "timezone", "pod_assignment", "role"}

    alias_missing = alias_required - set(alias_df.columns)
    master_missing = master_required - set(master_df.columns)

    if alias_missing:
        raise ValueError(f"Missing required alias columns: {sorted(alias_missing)}")
    if master_missing:
        raise ValueError(f"Missing required master columns: {sorted(master_missing)}")

    alias_df = alias_df.copy()
    master_df = master_df.copy()

    alias_df["alias_norm"] = alias_df["alias_norm"].map(normalize_person_name)
    alias_df["person_name"] = alias_df["person_name"].map(normalize_person_name)
    master_df["person_name"] = master_df["person_name"].map(normalize_person_name)

    return alias_df, master_df
    
    
def apply_person_mapping(df_long: pd.DataFrame, alias_df: pd.DataFrame) -> pd.DataFrame:
    df = df_long.copy()

    df["host_norm"] = df["host"].map(normalize_person_name)
    df["attendee_norm"] = df["attendee_raw"].map(normalize_person_name)

    alias_lookup = (
        alias_df[["alias_norm", "person_name"]]
        .dropna()
        .drop_duplicates(subset=["alias_norm"])
        .rename(columns={"person_name": "mapped_person_name"})
    )

    df = df.merge(
        alias_lookup,
        how="left",
        left_on="attendee_norm",
        right_on="alias_norm",
    )
    df = df.rename(columns={"mapped_person_name": "attendee_name"})
    df = df.drop(columns=["alias_norm"])

    host_lookup = (
        alias_df[["alias_norm", "person_name"]]
        .dropna()
        .drop_duplicates(subset=["alias_norm"])
        .rename(columns={"alias_norm": "host_norm", "person_name": "host_name"})
    )

    df = df.merge(host_lookup, how="left", on="host_norm")

    df["attendee_name"] = df["attendee_name"].fillna(df["attendee_norm"])
    df["host_name"] = df["host_name"].fillna(df["host_norm"])

    df["attendee_match_status"] = pd.Series("mapped", index=df.index)
    df.loc[df["attendee_name"] == df["attendee_norm"], "attendee_match_status"] = "unmapped"

    df["host_match_status"] = pd.Series("mapped", index=df.index)
    df.loc[df["host_name"] == df["host_norm"], "host_match_status"] = "unmapped"

    return df


def attach_person_attributes(df_long: pd.DataFrame, master_df: pd.DataFrame) -> pd.DataFrame:
    df = df_long.copy()

    attendee_master = master_df.rename(
        columns={
            "person_name": "attendee_name",
            "timezone": "attendee_timezone",
            "pod_assignment": "pod_assignment",
            "role": "role",
        }
    )

    df = df.merge(attendee_master, how="left", on="attendee_name")

    host_master = master_df.rename(
        columns={
            "person_name": "host_name",
            "timezone": "host_timezone",
        }
    )[["host_name", "host_timezone"]]

    df = df.merge(host_master, how="left", on="host_name")

    return df


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

    df["session_datetime_utc"] = pd.to_datetime(df["datetime"], errors="coerce", utc=True)

    df["attendee_local_datetime"] = [
        _safe_localize_timestamp(ts, tz)
        for ts, tz in zip(df["session_datetime_utc"], df["attendee_timezone"])
    ]
    df["host_local_datetime"] = [
        _safe_localize_timestamp(ts, tz)
        for ts, tz in zip(df["session_datetime_utc"], df["host_timezone"])
    ]

    df["attendee_local_date"] = pd.to_datetime(df["attendee_local_datetime"], errors="coerce").dt.date
    df["attendee_local_hour"] = pd.to_datetime(df["attendee_local_datetime"], errors="coerce").dt.hour
    df["attendee_local_weekday"] = pd.to_datetime(df["attendee_local_datetime"], errors="coerce").dt.day_name()

    df["host_local_date"] = pd.to_datetime(df["host_local_datetime"], errors="coerce").dt.date
    df["host_local_hour"] = pd.to_datetime(df["host_local_datetime"], errors="coerce").dt.hour
    df["host_local_weekday"] = pd.to_datetime(df["host_local_datetime"], errors="coerce").dt.day_name()

    return df
  
  
def extract_unknown_names(df_long: pd.DataFrame) -> pd.DataFrame:
    attendee_unknown = (
        df_long.loc[df_long["attendee_match_status"] == "unmapped", ["attendee_raw", "attendee_norm", "session_id"]]
        .copy()
        .assign(appears_as="attendee")
        .rename(columns={"attendee_raw": "raw_name", "attendee_norm": "normalized_name"})
    )

    host_unknown = (
        df_long.loc[df_long["host_match_status"] == "unmapped", ["host", "host_norm", "session_id"]]
        .copy()
        .assign(appears_as="host")
        .rename(columns={"host": "raw_name", "host_norm": "normalized_name"})
    )

    unknown = pd.concat([attendee_unknown, host_unknown], ignore_index=True)

    if unknown.empty:
        return pd.DataFrame(columns=["raw_name", "normalized_name", "appears_as", "n_rows", "n_sessions"])

    summary = (
        unknown.groupby(["raw_name", "normalized_name", "appears_as"], dropna=False)
        .agg(
            n_rows=("session_id", "size"),
            n_sessions=("session_id", "nunique"),
        )
        .reset_index()
        .sort_values(["n_rows", "normalized_name"], ascending=[False, True])
        .reset_index(drop=True)
    )

    return summary
 
 
def build_sessions_table(df_sessions: pd.DataFrame) -> pd.DataFrame:
    keep_cols = [
        "session_id",
        "ID_original",
        "ID_clean",
        "host",
        "date_raw",
        "date_clean",
        "time_raw",
        "time_clean",
        "timezone_raw",
        "tz_full",
        "datetime",
        "year_inferred",
        "time_inferred_ampm",
        "parse_status",
        "needs_review",
        "review_reason",
    ]

    existing = [c for c in keep_cols if c in df_sessions.columns]
    return df_sessions[existing].copy()


def build_attendance_enriched(df_long: pd.DataFrame) -> pd.DataFrame:
    df = df_long.copy()

    ordered_cols = [
        "session_id",
        "session_datetime_utc",
        "date_clean",
        "host",
        "host_norm",
        "host_name",
        "host_timezone",
        "host_local_datetime",
        "host_local_date",
        "host_local_hour",
        "host_local_weekday",
        "attendee_slot",
        "attendee_raw",
        "attendee_norm",
        "attendee_name",
        "attendee_timezone",
        "attendee_local_datetime",
        "attendee_local_date",
        "attendee_local_hour",
        "attendee_local_weekday",
        "pod_assignment",
        "role",
        "is_host",
        "attendance_source",
        "parse_status",
        "needs_review",
        "review_reason",
        "attendee_match_status",
        "host_match_status",
    ]

    existing = [c for c in ordered_cols if c in df.columns]
    df = df[existing].copy()

    df = df.sort_values(
        ["session_datetime_utc", "session_id", "attendee_name", "attendee_slot"],
        na_position="last",
    ).reset_index(drop=True)

    return df
    
    
def save_outputs(
    sessions: pd.DataFrame,
    attendance_long: pd.DataFrame,
    attendance_enriched: pd.DataFrame,
    unknown_names: pd.DataFrame,
    out_dir: str | Path,
) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    sessions.to_csv(out_dir / "workblock_sessions.csv", index=False)
    attendance_long.to_csv(out_dir / "workblock_attendance_long.csv", index=False)
    attendance_enriched.to_csv(out_dir / "workblock_attendance_enriched.csv", index=False)
    unknown_names.to_csv(out_dir / "unknown_names.csv", index=False)


def main():
    sessions = load_parsed_workblocks("../data/interim/cleaned_workblocks.csv")
    print("Loaded parsed workblocks")

    sessions = build_session_id(sessions)
    print("Sessions built")

    sessions = apply_manual_corrections(
        sessions,
        "../data/interim/corrected_workblocks.csv"
    )

    sessions = build_session_id(sessions)

    attendance_long = reshape_attendance_long(sessions)
    attendance_long = ensure_host_attendance(attendance_long, sessions)

    attendance_long.to_csv("long.csv", index=False)

    # alias_df, person_master = load_reference_data(
    #     "../data/reference/person_alias.csv",
    #     "../data/reference/person_master.csv",
    # )

    # attendance_long = apply_person_mapping(attendance_long, alias_df)
    # attendance_enriched = attach_person_attributes(attendance_long, person_master)
    # attendance_enriched = add_local_time_features(attendance_enriched)

    # unknown_names = extract_unknown_names(attendance_enriched)
    # 
    # sessions_out = build_sessions_table(sessions)
    # attendance_enriched = build_attendance_enriched(attendance_enriched)

    # save_outputs(
    #     sessions=sessions_out,
    #     attendance_long=attendance_long,
    #     attendance_enriched=attendance_enriched,
    #     unknown_names=unknown_names,
    #     out_dir="../data/processed",
    # )

if __name__ == "__main__":
    main()
