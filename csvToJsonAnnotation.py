import csv
import json
import os
config_data = json.load(open("config.json"))
annotation_template = json.load(open("annotation_template.json"))

# Create a mapping from pose names to action IDs and colors
pose_to_action = {item["name"]: (item["id"], item["color"]) for item in config_data["actionLabelData"]}

def csv_to_json(csv_file_path):
    json_file_path = f"{os.path.splitext(csv_file_path)[0]}.json"
    # Read the poses.csv file
    poses = []
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            poses.append((int(row['Timestamp']), row['Pose']))

    # Convert the timeseries to actionAnnotationList format
    action_annotation_list = []
    current_action = None
    start_time = None
    offset_timestamp = 0

    for i, (timestamp, pose) in enumerate(poses):
        if i == 0:
            offset_timestamp = timestamp
        if current_action is None:
            current_action = pose
            start_time = timestamp
        elif pose != current_action:
            action_id, color = pose_to_action[current_action.split('.')[1]]
            action_annotation_list.append({
                "start": (start_time - offset_timestamp)/ 1000.0,
                "end": (timestamp - offset_timestamp) / 1000.0,
                "action": action_id,
                "object": 0,
                "color": color,
                "description": ""
            })
            current_action = pose
            start_time = timestamp

    # Add the last action
    if current_action is not None:
        action_id, color = pose_to_action[current_action.split('.')[1]]
        action_annotation_list.append({
            "start": (start_time - offset_timestamp) / 1000.0,
            "end": (poses[-1][0] - offset_timestamp) / 1000.0,
            "action": action_id,
            "object": 0,
            "color": color,
            "description": ""
        })

    # Print the result
    print(json.dumps({"actionAnnotationList": action_annotation_list}, indent=2))
    annotation_template["annotation"]["actionAnnotationList"] = action_annotation_list
    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(annotation_template, json_file, indent=4)

if __name__ == "__main__":
    folder_path = input("Enter the folder path containing CSV files: ")
    csv_to_json(folder_path)