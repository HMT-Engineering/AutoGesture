import csv
import json
import os

def preprocess(csv_file_path):
    # Read the poses.csv file
    poses = []
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            poses.append((int(row['Timestamp']), row['Pose']))

    # Convert the timeseries to actionAnnotationList format
    window_size = 100
    pre_window_steps = 25
    action_annotation_list = []
    smoothed_list = []
    first_timestamp = poses[0][0]
    last_timestamp = poses[len(poses) - 1][0]   

    for timestamp, pose in poses:
        if(timestamp - first_timestamp > window_size/2 and timestamp < last_timestamp - window_size/2):
            poses_in_window = [p for p in poses if p[0] >= timestamp - window_size/2 and p[0] <= timestamp + window_size/2]
            most_common_pose = max(set([p[1] for p in poses_in_window]), key=[p[1] for p in poses_in_window].count)
            if most_common_pose == "Pose.Unknown":
                most_common_pose = "Pose.Resting"
            action_annotation_list.append({"Timestamp": timestamp, "Pose": most_common_pose})

    #Pre transition smoothing to get the transition itself classified.
    for i in range(0, len(action_annotation_list)):
        smoothed_list.append(action_annotation_list[i])
        if i > pre_window_steps:
            if(smoothed_list[i]["Pose"] != "Pose.Resting"):
                for j in range(i - pre_window_steps, i):
                    smoothed_list[j]["Pose"] = smoothed_list[i]["Pose"]
    # Write the actionAnnotationList to a new CSV file
    output_file_path = os.path.join(os.path.dirname(csv_file_path), 'action_annotations.csv')
    with open(output_file_path, mode='w', newline='') as csvfile:
        fieldnames = ['Timestamp', 'Pose']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for annotation in smoothed_list:
            writer.writerow(annotation)

if __name__ == "__main__":
    folder_path = input("Select the annotations file:")
    preprocess(folder_path)