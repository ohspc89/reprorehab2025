import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from zoneinfo import ZoneInfo

filename = "cleaned.csv"
df_raw = pd.read_csv(filename)

# Exporting for further analysis
attendee_cols = df_raw.columns[df_raw.columns.str.match('Attendee')]
df = (
    df_raw.melt(id_vars=['host', 'datetime', 'date_clean'],
                value_vars=list(attendee_cols),
                value_name='attendee')
                .sort_values(by=['date_clean', 'host'])
                .drop('variable', axis=1)
)

# If there's no attendee, fill the host name
# Host should also be the attendee of that workblock.
missing_rows = []
groups = df.groupby(["host", "datetime"])
for _, group in groups:
    if all(group['attendee'].isna()):
        row = group.iloc[0].copy()
        row['attendee'] = row['host']
        missing_rows.append(row)

if missing_rows:
    df = pd.concat((df, pd.DataFrame(missing_rows)),
                   ignore_index=True)

# Drop NA rows
df = df.dropna(subset=['attendee'])

# timezones of individuals
with open("timezones.json") as f:
    tzmap = json.load(f)

# full names of individuals
with open("namemap.json") as g:
    namemap = json.load(g)

def normalize_names(series: pd.Series):
    """
    Remove 1) whitespace, 2) '.' or ',' at the end,
    3) whitespace after '-', 4) multiple whitespace,
    5) '.' after middle names AND capitalize 
    First and the last name.
    """
    return (series
            .str.strip()
            .str.replace(r"[\,\.]+$", "", regex=True)
            .str.replace(r"[-]\s", "-", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.replace(r"\b([A-Za-z])\.\b", r"\1", regex=True)
            .str.title())

# normalized names
df['host_norm'] = normalize_names(df['host'])
df['attendee_norm'] = normalize_names(df['attendee'])

# Use the full name for consistency
# attendee_fullname - if NaN, no participant
df['host_fullname'] = df['host_norm'].map(namemap)
df['attendee_fullname'] = df['attendee_norm'].map(namemap)

# If attendee_fullname is NA, that means there was no attendee
# Paste the host_fullname value here.
df['attendee_fullname'] = df['attendee_fullname'].fillna(df['host_fullname'])

# Make sure the host is also the attendee of the workblock.
rows_missing_host = []
groups = df.groupby(["host_fullname", "datetime"])
for _, group in groups:
    if group['host_fullname'] not in group['attendee_fullname'].values:
        row = group.iloc[0].copy()
        row['attendee_fullname'] = row['host_fullname']
        row['attendee'] = row['host']
        row['attendee_norm'] = row['host_norm']
        rows_missing_host.append(row)

if rows_missing_host:
    df = pd.concat((df, pd.DataFrame(rows_missing_host)),
                   ignore_index=True)

df.sort_values(by=['host_fullname', 'date_clean']).to_csv("jemma_in.csv")

# Timezones
# This is not 100% accurate,
# because values are based on the locations of
# their affiliated institutions. 
df["host_tz"] = df["host_fullname"].map(tzmap)
df["attendee_tz"] = df["attendee_fullname"].map(tzmap)

# Ensure datetime format
df["datetime_utc"] = pd.to_datetime(df["datetime"], utc=True)


def local_hour(row):
    tz = row["attendee_tz"]
    dt = row["datetime_utc"]
    if pd.isna(tz) or pd.isna(dt):
        return np.nan
    dt_local = dt.tz_convert(ZoneInfo(tz))
    return dt_local.hour


def local_weekday(row):
    tz = row["attendee_tz"]
    dt = row["datetime_utc"]
    if pd.isna(tz) or pd.isna(dt):
        return np.nan
    dt_local = dt.tz_convert(ZoneInfo(tz))
    # 0=Monday, ..., 6=Sunday
    return dt_local.weekday()

df["local_hour"] = df.apply(local_hour, axis=1)
df["local_weekday"] = df.apply(local_weekday, axis=1)

# Timezone-specific numbers
# When analyzing these, strictly focus on 'learners'
tas = ["Alexandra Reed", "Amanda Gahlot", "Andrew Hooyman",
       "Becky Molinini", "Devin Austin", "Duncan Tulimieri",
       "Jinseok Oh", "Johanna Bayer", "Rini Varghese",
       "Rachel Mazorow", "Ashley Catchpole"]
learners = df.loc[~df["attendee_fullname"].isin(tas)]

# When did learners attend workblocks?
hour_dist = (
    learners.groupby(["attendee_fullname", "local_hour"])
    .size()
    .reset_index(name="n_sessions")
)
hour_dist.to_csv("hour_distribution.csv", index=False)

# peak hour
peak_hour = (
    hour_dist.sort_values(["attendee_fullname", "n_sessions"],
                          ascending=[True, False])
                          .groupby("attendee_fullname")
                          .head(1)
)
peak_hour.to_csv('peak_hour.csv', index=False)

# plot peak hours
peak_hour_agg = (
    peak_hour.groupby('local_hour')
    .agg("count")
)
fig, ax = plt.subplots(constrained_layout=True)
sns.barplot(peak_hour_agg, x='local_hour',
            y='n_sessions', ax=ax)
ax.set_ylabel("Count")
ax.set_xlabel("Local Hour")
ax.set_xticks(labels=['8am', '9am', '10am', '11am', '12pm',
                      '1pm', '2pm', '3pm', '4pm', '5pm'], 
           ticks=plt.gca().get_xticks())
ax.spines[['top', 'right']].set_visible(False)
fig.suptitle("Learners' Most Frequent Workblock Start Times"
             "\n(9/30/25 - 11/14/25)")
fig.savefig("individual_peak_hours.png",
            bbox_inches='tight',
            dpi=300)

heat = (
    learners.dropna(subset=["local_hour"])
    .pivot_table(
        index="attendee_fullname",
        columns="local_hour",
        values="datetime_utc",
        aggfunc="count",
        fill_value=0
    )
)

# Exclude columns where all values are 0.0
# heat = heat.iloc[:, 1:]

fig, ax = plt.subplots(figsize=(14, 10))
sns.heatmap(heat, cmap='mako', ax=ax)
ax.set_title("Attendance Heatmap (Local Hour by Attendee)"
             "\n(9/30/25 - 11/14/25)")
ax.set_xlabel("Local Hour")
ax.set_ylabel("Count")
ax.set_xticks(labels=['8am', '9am', '10am', '11am', '12pm',
                      '1pm', '2pm', '3pm', '4pm', '5pm', '6pm'], 
           ticks=plt.gca().get_xticks())
fig.savefig("Heatmap.png", bbox_inches='tight', dpi=300)

# Hour preference patterns
global_hour_pref = learners["local_hour"].value_counts().sort_index()
global_hour_pref.to_csv("global_hour_pref.csv")

# plotting
fig, ax = plt.subplots(constrained_layout=True)
sns.barplot(pd.DataFrame(global_hour_pref), x='local_hour',
             y='count',
             ax=ax)
sns.despine()
fig.suptitle("Workblock Attendance by Local Hour"
             "\n(9/30/25 - 11/14/25)")
ax.set_xticks(labels=['8am', '9am', '10am', '11am', '12pm',
                      '1pm', '2pm', '3pm', '4pm', '5pm', '6pm'],
                      ticks=plt.gca().get_xticks())
fig.savefig('global_hour_pref.png', dpi=300, bbox_inches='tight')

# Per learner attendance
attendance_counts_learners = (
    learners.groupby('attendee_fullname')
    .size()
    .reset_index(name='n_attendances')
    .sort_values('n_attendances', ascending=False)
    .sort_values('attendee_fullname')
)
attendance_counts_learners.to_csv(
    "Learner_attendance_counts.csv", index=False)


# --- 2b. Workblock weekday distribution (host local time) ---

def host_local_weekday(row):
    tz = row["host_tz"]
    dt = row["datetime_utc"]
    if pd.isna(tz) or pd.isna(dt):
        return np.nan
    dt_local = dt.tz_convert(ZoneInfo(tz))
    # 0=Monday, ..., 6=Sunday
    return dt_local.weekday()

df["host_weekday"] = df.apply(host_local_weekday, axis=1)

# host_fullname + datetime 조합으로 unique workblock 정의
blocks = df[["host_fullname", "datetime", "host_weekday"]].drop_duplicates()

# 월(0)~금(4)만 필터링
weekday_counts = (
    blocks[blocks["host_weekday"] < 5]["host_weekday"]
    .value_counts()
    .sort_index()
)
print(f"Weekday_counts: {weekday_counts}")

# 비율도 보고 싶으면:
weekday_prop = weekday_counts / weekday_counts.sum()
print(f"Weekday_prop: {weekday_prop}")


df.sort_values(by='host_fullname').to_csv("processed.csv", index=False)