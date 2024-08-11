# %%
import pandas as pd
import numpy as np
import glob
import os

# %% [markdown]
# ## Parameters

# %%
filename = "pilates.csv"
date_col = "date"
program_col = "back-and-superman"
use_last_file = False
first_date = "2024-06-27"


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
        x = os.path.getctime(filename)
        print(
            f"{last_file} not found - using {filename}, created at {pd.to_datetime(x, unit='s')} as the last file"
        )
        last_file = filename
    else:
        x = os.path.getctime(last_file)
        print(
            f"{last_file} created at {pd.to_datetime(x, unit='s')} found - using it as the last file"
        )
    df = pd.read_csv(last_file)
    df.to_csv(filename, index=False)
    os.remove(last_file)
else:
    df = pd.read_csv(filename)


# Convert the date column to datetime
df[date_col] = pd.to_datetime(df[date_col])

# Set the "Date" column as the index
df.set_index(date_col, inplace=True)

# Define the start date
start_date = pd.to_datetime(first_date)

# Define the period length in days
two_weeks = pd.DateOffset(weeks=2)
two_weeks_data = pd.DataFrame(columns=["start_date", "end_date", "percentage"])

# Iterate over the two weeks periods
while start_date < df.index.max():
    end_date = start_date + two_weeks
    period_df = df.loc[start_date:end_date]
    period_sum = period_df[program_col].sum()

    # Calculate the percentage with respect to a total of 48
    period_percentage = period_sum / 48 * 100

    # Save the result
    two_weeks_data.loc[len(two_weeks_data)] = [start_date, end_date, period_percentage]

    # Move to the next period
    start_date = end_date + pd.DateOffset(days=1)

# Define the start date
start_date = pd.to_datetime(first_date)

# Define the period length in days
one_week = pd.DateOffset(weeks=1)
number_days = 3
one_week_data = pd.DataFrame(
    columns=[
        "start_date",
        "end_date",
        "total remaining to date (caped)",
        "last considered day",
        "total this week / to date",
        "total pilates days this week",
        "required this week",
        "remaining this week",
        "percentage for this week",
        "ideal this weeek / to date",
        "difference with respect to ideal",
        "percentage to date",
        "total remaining to date",
    ]
)

capped_total_remaining_to_date = 0
total_remaining_to_date = 0

while start_date < df.index.max():
    end_date = start_date + one_week - pd.DateOffset(days=1)
    period_df = df.loc[start_date:end_date]
    period_sum = period_df[program_col].sum()

    # Calculate the percentage with respect to a total of 24
    total_per_week = 7 * (number_days - 1) + 6 if number_days == 4 else 7 * number_days
    period_percentage = period_sum / total_per_week * 100

    last_day = min(end_date, df.index.max())
    # on weekly periods that have 3 days of exercises,
    # the first pilates day starts on the second day of the period,
    # so we count one less on those days to calculate days_from_start
    actual_start_date = (
        start_date + pd.DateOffset(days=1) if number_days == 3 else start_date
    )
    days_from_start = (last_day - actual_start_date).days + 1

    # we require to do pilates one every other day:
    # - if we run the script on a day that is a pilates day:
    #       days_from_start will be odd, so that days_from_start / 2
    #       is a fraction and we use np.ceil to round up to the next
    # - if we run the script on a day that is not a pilates day:
    #       days_from_start will be even, so that days_from_start / 2
    #       is an integer and using np.ceil will not change the value
    number_pilates_days = np.ceil(days_from_start / 2)

    if df.index.max() < end_date:
        required_aggregate = 7 * number_pilates_days
    else:
        required_aggregate = total_per_week

    percentage_to_date = period_sum / required_aggregate * 100

    capped_total_remaining_to_date = max(capped_total_remaining_to_date, -12) + (
        total_per_week - period_sum
    )
    capped_total_remaining_to_date = max(-12, capped_total_remaining_to_date)
    total_remaining_to_date += total_per_week - period_sum

    # Save the result
    one_week_data.loc[len(one_week_data)] = [
        start_date,  # start date
        end_date,  # end date
        capped_total_remaining_to_date,  # total remaining to date, capped at 12
        df.index.max(),  # last considered day
        period_sum,  # total this week / to date
        number_days,  # total pilates days this week
        total_per_week,  # required this week
        total_per_week - period_sum,  # remaining this week
        round(period_percentage, ndigits=1),  # percentage for this week
        required_aggregate,  # ideal this week / to date
        required_aggregate - period_sum,  # difference with respect to ideal
        round(percentage_to_date, ndigits=1),  # percentage to date
        total_remaining_to_date,  # total remaining to date
    ]

    number_days = 3 if number_days == 4 else 4

    # Move to the next period
    start_date = end_date + pd.DateOffset(days=1)

# Save the results to a CSV file
import os

os.makedirs("date_numbers", exist_ok=True)
two_weeks_data.to_csv("date_numbers/two_weeks_data.csv")
one_week_data.to_csv("date_numbers/one_week_data.csv")

# %%
display(one_week_data)
print(
    "Total remaining to date: ",
    one_week_data["total remaining to date (caped)"].values[-1],
)

# %%
