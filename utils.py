# %%
import glob
import os

import pandas as pd


def get_last_csv_file(download_path):
    # Get list of all CSV files in the current directory
    csv_files = glob.glob(f"{download_path}/*.csv")

    # Sort files by creation time
    csv_files_sorted = sorted(csv_files, key=os.path.getctime)
    return csv_files_sorted[-1]


def load_data(filename, use_last_file, download_path):
    if use_last_file:
        last_file = get_last_csv_file(download_path)
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
    return df
