import pandas as pd
import tkinter as tk
from tkinter import filedialog
gesture_classes = {
    "Pose.Pinch": "0",
    "Pose.Fist": "1",
    "Pose.Flat": "2",
    "Pose.IndexTap": "3",
    "Pose.AllFingerTap": "4",
    "Pose.WristFlickUp": "5",
    "Pose.WristFlickDown": "6",
    "Pose.WristFlickIn": "7",
    "Pose.WristFlickOut": "8",
    "Pose.PinkyPinch": "9",
    "Pose.Resting": "98",
    "Pose.Unknown": "99",
    "":"99"
}

def merge_data(gesture_data, sensor_data):
    # Read CSV files
    files = []
    for file in sensor_data:
        files.append(pd.read_csv(file))
    action_annotations_df = pd.read_csv(gesture_data)

    # Apply gesture class mapping to the 'Gesture' column
    action_annotations_df['Gesture'] = action_annotations_df['Pose'].map(gesture_classes)


    # Merge dataframes on 'Timestamp' column using outer join
    merged_df = action_annotations_df
    for file in files:
        merged_df = pd.merge(merged_df, file, on='Timestamp', how='outer')

    # Sort by 'Timestamp' and fill missing values with the previous value
    merged_df.sort_values('Timestamp', inplace=True)
    merged_df.fillna(method='ffill', inplace=True)

    return merged_df

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    gesture_data = filedialog.askopenfilename(title="Select Gesture Data CSV", filetypes=[("CSV files", "*.csv")])
    sensor_data = filedialog.askopenfilenames(title="Select Sensor Data CSVs", filetypes=[("CSV files", "*.csv")])

    if gesture_data and sensor_data:
        merged_data = merge_data(gesture_data, sensor_data)
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if save_path:
            merged_data.to_csv(save_path, index=False)
            print(f"Merged data saved to {save_path}")
        else:
            print("Save operation cancelled.")
    else:
        print("No files selected.")