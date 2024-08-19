import pandas as pd
import math
import pandas as pd
import math

import matplotlib.pyplot as plt


def rolling_window_analysis(df, window_size, reference_total, num_days):
    # Set the 'date' column as the index
    df = df.set_index("date")

    # Calculate the rolling sum of exercises using the defined window size
    rolling_sum = df["exercises"].rolling(window_size).sum()

    # Calculate the difference between the reference and the rolling sum
    difference = reference_total - rolling_sum

    # Create a separate axis for the difference plot
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

    # Plot the rolling sum and the reference line
    ax1.plot(df.index, rolling_sum, "b.-", label="Rolling Sum")
    ax1.axhline(y=reference_total, color="r", linestyle="--", label="Reference")
    ax1.set_ylabel("Total Exercises")
    ax1.legend()

    # Calculate the difference between the rolling sum and the reference
    # Add Y more days to the dataframe with 0 exercises each day
    future_dates = pd.date_range(
        start=df.index[-1] + pd.DateOffset(1), periods=num_days
    )
    future_df = pd.DataFrame({"date": future_dates, "exercises": 0})
    df = pd.concat([df, future_df])

    # Calculate the rolling sum with the updated dataframe
    rolling_sum = df["exercises"].rolling(window_size).sum()

    # Calculate the difference between the reference and the rolling sum
    difference = reference_total - rolling_sum

    # Plot the difference
    ax2.plot(df.index, difference, "g.-", label="Remaining Exercises")
    ax2.set_ylabel("Difference")
    ax2.legend()

    # Rotate the x-axis labels by 90 degrees
    plt.xticks(rotation=90)

    # Calculate the number of exercises needed to reach the reference in the next Y days
    exercises_needed = math.ceil(difference[-1] / num_days)

    # Print the number of exercises needed
    print(f"Number of exercises needed in the next {num_days} days: {exercises_needed}")

    # Show the plot
    plt.show()
    # plt.draw()

    # Return the rolling sum dataframe
    return pd.DataFrame(rolling_sum, columns=["Rolling Sum"])


def main():
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv("your_file.csv")

    # Convert the 'date' column to datetime type
    df["date"] = pd.to_datetime(df["date"])

    # Define the window size (X)
    window_size = 7

    # Define the reference total exercises (as a parameter)
    reference_total = 100

    # Define the number of days (Y)
    num_days = 10

    # Call the rolling_window_analysis function
    rolling_window_analysis(df, window_size, reference_total, num_days)


def test_rolling_window_analysis():
    # Create a dummy example dataframe
    df = pd.DataFrame(
        {
            "date": pd.date_range(start="2022-01-01", periods=10),
            "exercises": [3, 0, 5, 9, 0, 7, 0, 4, 6, 8],
        }
    )

    # Define the window size (X)
    window_size = 7

    # Define the reference total exercises (as a parameter)
    reference_total = 27

    # Define the number of days (Y)
    num_days = 2

    # Call the rolling_window_analysis function
    rolling_window_analysis(df, window_size, reference_total, num_days)


if __name__ == "__main__":
    # main()
    df = test_rolling_window_analysis()
    display(df)
