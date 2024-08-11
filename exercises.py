# %%
import pandas as pd
import numpy as np
import os

from utils import get_last_csv_file, load_data


# %%
def prepare_data(date_col, df):
    # Convert the date column to datetime
    df[date_col] = pd.to_datetime(df[date_col])

    # Set the "Date" column as the index
    df.set_index(date_col, inplace=True)


def week_analysis(program_col, df, number_program_exercises, start_date):

    start_date = pd.to_datetime(start_date)

    # Define the week length in days
    week = pd.DateOffset(weeks=1)
    number_days = 3
    week_data = pd.DataFrame(
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

    number_of_exercises_per_week = number_program_exercises * 2
    number_of_exercises_per_two_weeks = number_of_exercises_per_week * 2
    number_of_exercises_first_week = np.ceil(number_of_exercises_per_two_weeks / 7)
    number_of_exercises_last_day = (
        number_of_exercises_per_two_weeks
        - number_of_exercises_first_week
        * np.floor(number_of_exercises_per_two_weeks / 7)
    )

    capped_total_remaining_to_date = 0
    total_remaining_to_date = 0

    while start_date < df.index.max():
        end_date = start_date + week - pd.DateOffset(days=1)
        week_df = df.loc[start_date:end_date]
        week_sum = week_df[program_col].sum()

        # Calculate the percentage with respect to a total of 24
        total_per_week = (
            number_of_exercises_first_week * (number_days - 1)
            + number_of_exercises_last_day
            if number_days == 4
            else number_of_exercises_first_week * number_days
        )
        week_percentage = week_sum / total_per_week * 100

        last_day = min(end_date, df.index.max())
        # on weekly weeks that have 3 days of exercises,
        # the first pilates day starts on the second day of the week,
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
            required_aggregate = number_of_exercises_first_week * number_pilates_days
        else:
            required_aggregate = total_per_week

        percentage_to_date = week_sum / required_aggregate * 100

        capped_total_remaining_to_date = max(
            capped_total_remaining_to_date, -number_program_exercises
        ) + (total_per_week - week_sum)
        capped_total_remaining_to_date = max(-12, capped_total_remaining_to_date)
        total_remaining_to_date += total_per_week - week_sum

        # Save the result
        week_data.loc[len(week_data)] = [
            start_date,  # start date
            end_date,  # end date
            capped_total_remaining_to_date,  # total remaining to date, capped at program_num_exercises
            df.index.max(),  # last considered day
            week_sum,  # total this week / to date
            number_days,  # total pilates days this week
            total_per_week,  # required this week
            total_per_week - week_sum,  # remaining this week
            round(week_percentage, ndigits=1),  # percentage for this week
            required_aggregate,  # ideal this week / to date
            required_aggregate - week_sum,  # difference with respect to ideal
            round(percentage_to_date, ndigits=1),  # percentage to date
            total_remaining_to_date,  # total remaining to date
        ]

        number_days = 3 if number_days == 4 else 4

        # Move to the next week
        start_date = end_date + pd.DateOffset(days=1)

    # Save the results to a CSV file
    os.makedirs("date_numbers", exist_ok=True)
    week_data.to_csv("date_numbers/one_week_data.csv")

    display(week_data)
    print(
        "Total remaining to date: ",
        week_data["total remaining to date (caped)"].values[-1],
    )
    return week_data


# %%
def main(
    filename,
    date_col,
    program_col,
    use_last_file,
    download_path,
    number_program_exercises,
):
    # Load the data
    df = load_data(filename, use_last_file, download_path)
    prepare_data(date_col, df)
    week_data = week_analysis(program_col, df, number_program_exercises)
    return week_data


if __name__ == "__main__":
    filename = "pilates.csv"
    date_col = "date"
    use_last_file = False
    download_path = "/mnt/c/Users/jaum/Downloads"
    program_col = "back-and-superman"
    number_program_exercises = 12
    start_date = "2024-06-27"

    main(
        filename,
        date_col,
        program_col,
        use_last_file,
        download_path,
        number_program_exercises,
        start_date,
    )
