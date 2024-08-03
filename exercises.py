# %%
import pandas as pd


# %% [markdown]
# ## Parameters

# %%
filename = "pilates.csv"
date_col = "date"
program_col = "back-and-superman"

# %%


# Read the CSV file
df = pd.read_csv(filename)

# Convert the date column to datetime
df[date_col] = pd.to_datetime(df[date_col])

# Set the "Date" column as the index
df.set_index(date_col, inplace=True)

# Define the start date
start_date = pd.to_datetime("2024-07-25")

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
start_date = pd.to_datetime("2024-07-25")

# Define the period length in days
one_week = pd.DateOffset(weeks=1)
number_days = 3
one_week_data = pd.DataFrame(
    columns=[
        "start_date",
        "end_date",
        "last considered day",
        "total this week / to date",
        "required this week",
        "remaining this week",
        "percentage for this week",
        "ideal this weeek / to date",
        "difference with respect to ideal",
        "percentage to date",
    ]
)

while start_date < df.index.max():
    end_date = start_date + one_week - pd.DateOffset(days=1)
    period_df = df.loc[start_date:end_date]
    period_sum = period_df[program_col].sum()

    # Calculate the percentage with respect to a total of 24
    total_per_week = 7 * (number_days - 1) + 6 if number_days == 4 else 7 * number_days
    period_percentage = period_sum / total_per_week * 100

    # Calculate the ideal aggregate
    days_from_start = (min(end_date, df.index.max()) - start_date).days + 1
    # on weekly periods that have 3 days of exercises, 
    # the first pilates day starts on the second day of the period,
    # so we subtract 1 from days_from_start
    if number_days == 3: 
        days_from_start -= 1

    last_day = min(end_date, df.index.max())

    days_from_start = (
        (last_day - start_date).days
        if number_days == 3
        else (df.index.max() - start_date).days + 1
    )

    if df.index.max() < end_date:
        ideal_aggregate = (
            14 * (days_from_start - 1) / 2
            if number_days == 3
            else 14 * np.floor(days_from_start / 2)
        )
    else:
        ideal_aggregate = (
            14 * (days_from_start - 1) / 2 + 6
            if number_days == 3
            else 14 * days_from_start / 2
        )

    percentage_to_date = period_sum / ideal_aggregate * 100

    number_days = 3 if number_days == 4 else 4

    # Save the result
    one_week_data.loc[len(one_week_data)] = [
        start_date,  # start date
        end_date,  # end date
        df.index.max(),  # last considered day
        period_sum,  # total this week / to date
        total_per_week,  # required this week
        total_per_week - period_sum,  # remaining this week
        round(period_percentage, ndigits=1),  # percentage for this week
        ideal_aggregate,  # ideal this week / to date
        ideal_aggregate - period_sum,  # difference with respect to ideal
        round(percentage_to_date, ndigits=1),  # percentage to date
    ]

    # Move to the next period
    start_date = end_date + pd.DateOffset(days=1)

# Save the results to a CSV file
import os

os.makedirs("date_numbers", exist_ok=True)
two_weeks_data.to_csv("date_numbers/two_weeks_data.csv")
one_week_data.to_csv("date_numbers/one_week_data.csv")

# %%
