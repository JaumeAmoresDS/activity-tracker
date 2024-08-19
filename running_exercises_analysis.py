import pandas as pd
import numpy as np
import os

from utils import get_last_csv_file, load_data


def prepare_data(date_col, df):
    df[date_col] = pd.to_datetime(df[date_col])
    df.set_index(date_col, inplace=True)


def window_analysis(
    program_col: str,
    df: pd.DataFrame,
    number_program_exercises: int,
    start_date: str,
    window_size: int = 7,
    rounding_method: str = "round",
    last_day_has_different_number_of_exercises: bool = True,
    number_program_repetitions_per_window: int = 2,
):
    print("Analyzing", program_col)
    print("start date", start_date)
    print("number_program_exercises", number_program_exercises)
    print("rounding_method", rounding_method)
    print("window_size", window_size)

    start_date = pd.to_datetime(start_date)

    window = pd.DateOffset(days=window_size)
    number_days = 3
    window_data = pd.DataFrame(
        columns=[
            "start_date",
            "end_date",
            "last considered day",
            "total this window / to date",
            "total pilates days this window",
            "required this window",
            "remaining this window",
            "percentage for this window",
            "ideal this window / to date",
            "difference with respect to ideal",
            "percentage to date",
            "total remaining to date",
        ]
    )

    number_of_exercises_per_window = (
        number_program_exercises * number_program_repetitions_per_window
    )
    number_of_exercises_per_two_windows = number_of_exercises_per_window * 2
    rounding_op = getattr(np, rounding_method)
    number_of_exercises_all_but_last_day = rounding_op(
        number_of_exercises_per_two_windows / window_size
    )
    if last_day_has_different_number_of_exercises:
        number_of_exercises_last_day = (
            number_of_exercises_per_two_windows
            - number_of_exercises_all_but_last_day * (window_size - 1)
        )
    else:
        number_of_exercises_last_day = number_of_exercises_all_but_last_day
    print(
        f"number_of_exercises_all_but_last_day: {number_of_exercises_all_but_last_day}"
    )
    print(f"number_of_exercises_last_day: {number_of_exercises_last_day}")
    print(
        f"total number of exercises every two windows: {number_of_exercises_all_but_last_day*(window_size-1) + number_of_exercises_last_day}"
    )

    total_remaining_to_date = 0

    while start_date < df.index.max():
        end_date = start_date + window - pd.DateOffset(days=1)
        window_df = df.loc[start_date:end_date]
        window_sum = window_df[program_col].sum()

        total_per_window = (
            number_of_exercises_all_but_last_day * (number_days - 1)
            + number_of_exercises_last_day
            if number_days == 4
            else number_of_exercises_all_but_last_day * number_days
        )
        window_percentage = window_sum / total_per_window * 100

        last_day = min(end_date, df.index.max())
        actual_start_date = (
            start_date + pd.DateOffset(days=1) if number_days == 3 else start_date
        )
        days_from_start = (last_day - actual_start_date).days + 1

        number_pilates_days = np.ceil(days_from_start / 2)

        if df.index.max() < end_date:
            required_aggregate = (
                number_of_exercises_all_but_last_day * number_pilates_days
            )
        else:
            required_aggregate = total_per_window

        percentage_to_date = window_sum / required_aggregate * 100

        total_remaining_to_date += total_per_window - window_sum

        window_data.loc[len(window_data)] = [
            start_date,
            end_date,
            df.index.max(),
            window_sum,
            number_days,
            total_per_window,
            total_per_window - window_sum,
            round(window_percentage, ndigits=1),
            required_aggregate,
            required_aggregate - window_sum,
            round(percentage_to_date, ndigits=1),
            total_remaining_to_date,
        ]

        number_days = 3 if number_days == 4 else 4

        start_date = start_date + pd.DateOffset(days=1)

    os.makedirs("exercise_analysis", exist_ok=True)
    window_data.to_csv(f"exercise_analysis/{program_col}_sliding_window_data.csv")

    display(window_data)
    print(
        "Total remaining to date: ",
        window_data["total remaining to date"].values[-1],
    )
    return window_data


def main(
    filename,
    date_col,
    program_col,
    use_last_file,
    download_path,
    number_program_exercises,
    start_date,
    window_size: int = 7,
    rounding_method: str = "round",
    last_day_has_different_number_of_exercises: bool = True,
    number_program_repetitions_per_window: int = 2,
):
    df = load_data(filename, use_last_file, download_path)
    prepare_data(date_col, df)
    window_data = window_analysis(
        program_col,
        df,
        number_program_exercises,
        start_date,
        window_size,
        rounding_method,
        last_day_has_different_number_of_exercises,
        number_program_repetitions_per_window,
    )
    return window_data


print("-" * 80)
filename = "pilates.csv"
date_col = "date"
download_path = "/mnt/c/Users/jaum/Downloads"
rounding_method = "round"
last_day_has_different_number_of_exercises = True
number_program_repetitions_per_window = 2
window_size = 7  # Default window size

program_col = "back-and-superman"
number_program_exercises = 12
start_date = "2024-06-27"
use_last_file = False

_ = main(
    filename,
    date_col,
    program_col,
    use_last_file,
    download_path,
    number_program_exercises,
    start_date,
    window_size,
    rounding_method,
    last_day_has_different_number_of_exercises,
    number_program_repetitions_per_window,
)

print()
print("-" * 80)
program_col = "ankle-arms"
number_program_exercises = 18
start_date = "2024-08-06"
use_last_file = False

_ = main(
    filename,
    date_col,
    program_col,
    use_last_file,
    download_path,
    number_program_exercises,
    start_date,
    window_size,
    rounding_method,
    last_day_has_different_number_of_exercises,
    number_program_repetitions_per_window,
)
