import os
import csv
import json

def csv_to_json(csv_file_path, json_file_path):
    data = []
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
    
    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)

def convert_all_csv_to_json(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            csv_file_path = os.path.join(folder_path, filename)
            json_file_path = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}.json")
            csv_to_json(csv_file_path, json_file_path)
            print(f"Converted {csv_file_path} to {json_file_path}")

if __name__ == "__main__":
    folder_path = input("Enter the folder path containing CSV files: ")
    convert_all_csv_to_json(folder_path)