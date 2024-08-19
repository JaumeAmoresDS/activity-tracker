import pandas as pd
import math

import matplotlib.pyplot as plt

# Read the CSV file into a pandas DataFrame
df = pd.read_csv("your_file.csv")

# Convert the 'date' column to datetime type
df["date"] = pd.to_datetime(df["date"])

# Set the 'date' column as the index
df.set_index("date", inplace=True)

# Define the rolling window size (X)
window_size = 7

# Calculate the rolling sum of exercises using the defined window size
rolling_sum = df["exercises"].rolling(window_size).sum()

# Define the reference total exercises (as a parameter)
reference_total = 100

# Plot the rolling sum and the reference line
plt.plot(df.index, rolling_sum, label="Rolling Sum")
plt.axhline(y=reference_total, color="r", linestyle="--", label="Reference")
plt.xlabel("Date")
plt.ylabel("Total Exercises")
plt.legend()

# Calculate the difference between the rolling sum and the reference
difference = rolling_sum - reference_total

# Create a separate axis for the difference plot
ax2 = plt.twinx()
ax2.plot(df.index, difference, color="g", label="Difference")
ax2.set_ylabel("Difference")
ax2.legend()

# Define the number of days (Y)
num_days = 10

# Calculate the number of exercises needed to reach the reference in the next Y days
exercises_needed = math.ceil(difference[-1] / num_days)

# Print the number of exercises needed
print(f"Number of exercises needed in the next {num_days} days: {exercises_needed}")

# Show the plot
plt.show()
