import pandas as pd
import math
import pandas as pd
import math
from IPython.display import display

import matplotlib.pyplot as plt


def rolling_window_analysis(
    df,
    window_size,
    reference_total,
    num_days,
    padding=None,
    date_col="date",
    exercises_col="exercises",
):
    # Convert the 'date' column to datetime type
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.fillna(0)
    df["future"] = False
    if num_days > 0:
        # Add Y more days to the dataframe with 0 exercises each day
        future_dates = pd.date_range(
            start=df[date_col].values[-1] + pd.DateOffset(1), periods=num_days
        )
        future_df = pd.DataFrame(
            {date_col: future_dates, exercises_col: padding, "future": True}
        )
        df = pd.concat([df, future_df])

    # Set the 'date' column as the index
    df = df.set_index(date_col)
    # Calculate the rolling sum of exercises using the defined window size
    df["rolling_sum"] = df[exercises_col].rolling(window_size).sum()
    df["rolling_median"] = df[exercises_col].rolling(window_size).median()
    df["rolling_mean"] = df[exercises_col].rolling(window_size).mean()
    if num_days > 0 and padding is None:
        df.loc[df.future, exercises_col] = df.loc[~df.future, "rolling_median"].values[
            -1
        ]
        df["rolling_sum"] = df[exercises_col].rolling(window_size).sum()
        df["rolling_median"] = df[exercises_col].rolling(window_size).median()
        df["rolling_mean"] = df[exercises_col].rolling(window_size).mean()

    # Calculate the difference between the reference and the rolling sum
    difference = reference_total - df["rolling_sum"]

    # Create a separate axis for the difference plot
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

    # Plot the rolling sum and the reference line
    ax1.plot(
        df.index[~df.future], df["rolling_sum"][~df.future], "b.-", label="Rolling Sum"
    )
    if num_days > 0:
        ax1.plot(
            df.index[df.future],
            df["rolling_sum"][df.future],
            "b.--",
            label="Rolling Sum (Future)",
        )
    ax1.axhline(y=reference_total, color="r", linestyle="--", label="Reference")
    ax1.set_ylabel("Total Exercises")
    ax1.legend()

    # Calculate the difference between the rolling sum and the reference

    # Plot the difference
    ax2.plot(
        df.index[~df.future],
        difference[~df.future],
        "g.-",
        label="Remaining Exercises",
    )
    if num_days > 0:
        ax2.plot(
            df.index[df.future],
            difference[df.future],
            "g.--",
            label="Remaining Exercises (Future)",
        )
    ax2.set_ylabel("Difference")
    ax2.legend()

    # Rotate the x-axis labels by 90 degrees
    plt.xticks(rotation=90)

    # Calculate the number of exercises needed to reach the reference in the next Y days
    exercises_needed = difference.values[-1]

    # Show the plot
    plt.show()
    # plt.draw()

    df.to_csv(exercises_col + ".csv", index=False, header=True)

    print()
    print("-" * 80)
    print(exercises_col)
    # Print the number of exercises needed
    print(f"Number of exercises needed in the next {num_days} days: {exercises_needed}")
    display(
        df[
            [exercises_col, "future", "rolling_sum", "rolling_median", "rolling_mean"]
        ].tail(window_size + 1)
    )

    # Return the rolling sum dataframe
    return df


def main():

    # Parameters
    file_name = "pilates.csv"

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_name)

    # Define the window size (X)
    window_size = 7

    # Define the number of days (Y)
    num_days = 0

    # ------------------------------------------------
    program_col = "back-and-superman"
    # Define the reference total exercises (as a parameter)
    reference_total = 12 * 2

    # Call the rolling_window_analysis function
    _ = rolling_window_analysis(
        df,
        window_size,
        reference_total,
        num_days,
        padding=0,
        date_col="date",
        exercises_col=program_col,
    )

    # ------------------------------------------------
    program_col = "ankle-arms"
    # Define the reference total exercises (as a parameter)
    reference_total = 18 * 2

    # Call the rolling_window_analysis function
    _ = rolling_window_analysis(
        df,
        window_size,
        reference_total,
        num_days,
        padding=0,
        date_col="date",
        exercises_col=program_col,
    )


def test_rolling_window_analysis():
    # Create a dummy example dataframe
    df = pd.DataFrame(
        {
            "date": pd.date_range(start="2022-01-01", periods=10),
            "exercises": [3, 0, 5, 9, 0, 3, 0, 5, 9, 0],
        }
    )

    # Define the window size (X)
    window_size = 7

    # Define the reference total exercises (as a parameter)
    reference_total = 27

    # Define the number of days (Y)
    num_days = 2

    # Call the rolling_window_analysis function
    df = rolling_window_analysis(df, window_size, reference_total, num_days)

    display(df)


if __name__ == "__main__":
    # main()
    # df = test_rolling_window_analysis()
    main()
