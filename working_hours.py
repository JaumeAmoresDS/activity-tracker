# %%
import pandas as pd
from IPython.display import display
import os
import glob


# %% [markdown]
# ## Parameters


# %%
use_last_file = True
filename = "working_hours.csv"


# %%
def get_last_csv_file(path="/mnt/c/Users/jaum/Downloads"):
    # Get list of all CSV files in the current directory
    csv_files = glob.glob(f"{path}/*.csv")

    # Sort files by creation time
    csv_files_sorted = sorted(csv_files, key=os.path.getctime)
    return csv_files_sorted[-1]


if use_last_file:
    last_file = get_last_csv_file()
    if not os.path.exists(last_file):
        last_file = filename
    print(f"Using {last_file} as the last file")
    df = pd.read_csv(last_file)
    df.to_csv(filename, index=False)
    os.remove(last_file)
else:
    df = pd.read_csv(filename)
df.head()

# %%
df["time started"] = pd.to_datetime(df["time started"])
df["time ended"] = pd.to_datetime(df["time ended"])

# %%
df.head()

# %%
df["date"] = pd.to_datetime(df["time started"].dt.date)

# %%
df["day_of_week"] = df["date"].dt.dayofweek
df["weekend"] = df["day_of_week"] >= 5
df["week_number"] = df["date"].dt.isocalendar().week
df["corrected_date"] = df["date"]
df.loc[df["weekend"], "corrected_date"] -= pd.offsets.Day(2)
df["corrected_day_of_week"] = df["corrected_date"].dt.dayofweek
display(
    df.loc[df.weekend],
    ["date", "corrected_date", "day_of_week", "corrected_day_of_week"],
)

print(f"total original records: {len(df)}")
df = df[df["time ended"].dt.day == df["time started"].dt.day]
print(f"total records after removing incomplete records: {len(df)}")


# %%
df["activity name"] = df["activity name"].str.strip()
df = df[df["activity name"] == "Jaume trabajo"]
hours_per_day = df.groupby(by="corrected_date")["duration minutes"].sum()
print("Total days: ", len(hours_per_day))

# %%
hours_per_day = hours_per_day[hours_per_day > 0]
hours_per_day = hours_per_day / 60
print("Total working days: ", len(hours_per_day))
hours_per_day = hours_per_day.reset_index()
hours_per_day.columns = ["corrected_date", "hours"]
hours_per_day.describe()

# %%
min_hours = 2
max_hours = 12

# %%
low_hours = hours_per_day[hours_per_day["hours"] < min_hours]
low_hours

# %%
high_hours = hours_per_day[hours_per_day["hours"] > max_hours]
high_hours

# %%
df = df.set_index("corrected_date")
print("Low hours")
display(df.loc[low_hours["corrected_date"]])

# %%
print("High hours")
display(df.loc[high_hours["corrected_date"]])

# %%
hours_per_day["corrected_date"] = pd.to_datetime(hours_per_day["corrected_date"])
display(hours_per_day.describe())

# %%
hours_per_day = hours_per_day[hours_per_day["hours"] > min_hours]
print("Total working days after removing low hours: ", len(hours_per_day))

# %%
import matplotlib.pyplot as plt

weekly_hours = hours_per_day.groupby(
    hours_per_day["corrected_date"].dt.isocalendar().week
).agg({"hours": ["sum", "count"], "corrected_date": ["min", "max"]})
weekly_hours.columns = ["actual hours", "working days", "start date", "end date"]
required_hours = weekly_hours["working days"] * 8
# Add half hour per day for the first 4 weeks
required_hours.iloc[:4] = weekly_hours["working days"].iloc[:4] * 8.5
weekly_hours["required hours"] = required_hours
weekly_hours["difference"] = (
    weekly_hours["actual hours"] - weekly_hours["required hours"]
)
weekly_hours["cumulative difference"] = weekly_hours["difference"].cumsum()
weekly_hours = weekly_hours[
    [
        "working days",
        "actual hours",
        "required hours",
        "difference",
        "cumulative difference",
        "start date",
        "end date",
    ]
]

# %%
import calendar

tostring = lambda col: [
    f"{calendar.month_abbr[x]}{y}"
    for x, y in zip(weekly_hours[col].dt.month, weekly_hours[col].dt.day)
]
weekly_hours.index = [
    f"{x} - {y}" for x, y in zip(tostring("start date"), tostring("end date"))
]

# %%
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Plot the difference in hours per week
ax1.plot(
    weekly_hours.index, weekly_hours["difference"], "b.-", label="Difference in hours"
)
ax1.axhline(0, color="r", linestyle="--")
ax1.set_xlabel("Week")
ax1.set_ylabel("Difference in hours")
ax1.set_title("Difference in hours per week")
ax1.set_xticklabels(weekly_hours.index, rotation=90)

# Plot the cumulative difference in hours
ax2.plot(
    weekly_hours.index,
    weekly_hours["cumulative difference"],
    "r.-",
    label="Cumulative difference in hours",
)
ax2.axhline(0, color="b", linestyle="--")
ax2.set_xlabel("Week")
ax2.set_ylabel("Cumulative difference in hours")
ax2.set_title("Cumulative difference in hours")
ax2.set_xticklabels(weekly_hours.index, rotation=90)

plt.tight_layout()
plt.show()

# %%
print(
    "Total hours minus working hours: ", weekly_hours["cumulative difference"].iloc[-1]
)


# %%
import os

os.makedirs("working_hours_analysis", exist_ok=True)
weekly_hours.to_csv("working_hours_analysis/weekly_hours.csv")
hours_per_day.to_csv("working_hours_analysis/hours_per_day.csv")
df.to_csv("working_hours_analysis/processed_working_hours.csv")
