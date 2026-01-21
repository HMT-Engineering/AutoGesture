import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from tkinter import filedialog

def compare_pose_files(file1_path, file2_path):
    """
    Compare two pose files and calculate accuracy, confusion matrix, and classification report.

    Args:
        file1_path (str): Path to the first pose CSV file (reference).
        file2_path (str): Path to the second pose CSV file (to compare).

    Returns:
        tuple: Accuracy, confusion matrix, and classification report.
    """
    # Load the two files
    data1 = pd.read_csv(file1_path)
    data2 = pd.read_csv(file2_path)

    # Ensure both files have the same timestamps
    merged_data = pd.merge(data1, data2, on="Timestamp", suffixes=("_file1", "_file2"))

    # Extract the Pose columns for comparison
    y_true = merged_data["Pose_file1"]
    y_pred = merged_data["Pose_file2"]

    # Calculate accuracy
    accuracy = accuracy_score(y_true, y_pred)

    # Calculate confusion matrix
    conf_matrix = confusion_matrix(y_true, y_pred)

    # Generate classification report
    class_report = classification_report(y_true, y_pred)

    return accuracy, conf_matrix, class_report

def main():
    # Prompt the user to select the two files
    file1_path = filedialog.askopenfilename(title="Select First Pose File", filetypes=[("CSV files", "*.csv")])
    file2_path = filedialog.askopenfilename(title="Select Second Pose File", filetypes=[("CSV files", "*.csv")])

    # Compare the files
    try:
        accuracy, conf_matrix, class_report = compare_pose_files(file1_path, file2_path)
        print(f"Accuracy: {accuracy:.2%}")
        print("\nConfusion Matrix:")
        print(conf_matrix)
        print("\nClassification Report:")
        print(class_report)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()