import asyncio
import json
import time
from pathlib import Path
import cv2
from bleak import BleakGATTCharacteristic
import csv

import argparse

import leap

from  leapmotion import GestureListener, HandPose
from  canvas import Canvas
from bluetooth import disconnectFromWatch, searchAndConnectToWatch, startRecording, stopRecording, subscribeToData

class FingerTracking:
    def __init__(self):
        self.client = None       
        self.running = False 
        self.recording = False
        self.recorded_hands = {}
        self.recorded_poses = {}
        self.manual_poses = {}
        self.recorded_frames = {}
        self.recorded_ppg = {}
        self.recorded_gyro = {}
        self.recorded_acc = {}
        self.start_timestamp = "0"
        self._manual_label = "Pose.Resting"
        self.canvas = Canvas()
        self.framerate = 30
        self.last_frame_time = time.time()


    def on_pose_detected(self, event,pose:HandPose):
        self.canvas.render_hands(event)
        timestamp = str(int(1000*(time.time())))
        self.canvas.render_timestamp(timestamp)
        if(self.recording):
            if(self.last_frame_time + 1/self.framerate < time.time()):
                self.last_frame_time = time.time()
                self.recorded_frames[timestamp] = self.canvas.output_image.copy()
        self.canvas.render_pose(pose.decodedPose)
        self.canvas.render_instructions("x: Exit, r: Start Rec, s: Stop Rec, c: Connect watch", self.recording)
        if(self.recording):
            self.recorded_hands[timestamp] = pose
            self.recorded_poses[timestamp] = pose.decodedPose
            if(self._manual_label != ""):
                self.manual_poses[timestamp] = self._manual_label
        
    def save_recorded_data(self):
        Path(f"./recordings/{self.start_timestamp}").mkdir(exist_ok=True)
        fps = self.framerate
        out = cv2.VideoWriter(f'recordings/{self.start_timestamp}/recording.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (self.canvas.screen_size[1], self.canvas.screen_size[0]))
        for frame in self.recorded_frames.keys():
            data = self.recorded_frames[frame]
            out.write(data)
        out.release()
        with open(f"./recordings/{self.start_timestamp}/acc.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Acc X", "Acc Y", "Acc Z"])
            for time in self.recorded_acc.keys():
                writer.writerow([time,self.recorded_acc[time][0],self.recorded_acc[time][1],self.recorded_acc[time][2]])
        with open(f"./recordings/{self.start_timestamp}/gyro.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Gyro X", "Gyro Y", "Gyro Z"])
            for time in self.recorded_gyro.keys():
                writer.writerow([time,self.recorded_gyro[time][0],self.recorded_gyro[time][1],self.recorded_gyro[time][2]])
        with open(f"./recordings/{self.start_timestamp}/ppg.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "PPG Green", "PPG IR", "PPG Red"])
            for time in self.recorded_ppg.keys():
                writer.writerow([time,self.recorded_ppg[time][0],self.recorded_ppg[time][1],self.recorded_ppg[time][2]])
        with open(f"./recordings/{self.start_timestamp}/poses.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Pose"])
            for time in self.recorded_poses.keys():
                writer.writerow([time,self.recorded_poses[time]])
        with open(f"./recordings/{self.start_timestamp}/manual_poses.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Pose"])
            for time in self.manual_poses.keys():
                writer.writerow([time,self.manual_poses[time]])
        # with open(f"./recordings/{self.start_timestamp}/raw_hands.json", 'w') as f:
        #     json.dump(self.recorded_hands,f,default=lambda o: o.__dict__)
 
    def process_watch_data(self,sender: BleakGATTCharacteristic, data: bytearray):
        dataString = data.decode('utf-8')
        messageParts = dataString.split("_")
        if(len(messageParts) != 2):
            return
        sensor_data = messageParts[1].split(";")
        for set in sensor_data:
            time = set.split(",")[0]
            values = set.split(",")[1:]
            if(len(values) == 3):
                match messageParts[0][0]:
                    case 'A':
                        self.recorded_acc[time] = values
                    case 'G':
                        self.recorded_gyro[time] = values
                    case 'P':
                        self.recorded_ppg[time] = values
        
    async def mainloop(self, poses: list[dict] = None):
        tracking_listener = GestureListener(self.on_pose_detected, customposes=poses)
        connection = leap.Connection()
        connection.add_listener(tracking_listener)
        with connection.open():
            connection.set_tracking_mode(leap.TrackingMode.Desktop)
            self.running = True
            while self.running:
                cv2.imshow(self.canvas.name, self.canvas.output_image)
                key = cv2.waitKey(1)
                if key == ord("x"):
                    print("Exiting")
                    self.running = False
                    if(self.client is not None):
                        await disconnectFromWatch(self.client)
                elif key == ord("r"):
                    print("Recording")
                    self.start_timestamp = str(int(1000*time.time()))
                    if(self.client is not None):
                        await startRecording(self.client, self.start_timestamp)
                    self.recording = True
                elif key == ord("s"):
                    print("Stop Recording")
                    self.recording = False
                    if(self.client is not None):
                        await stopRecording(self.client, str(int(1000*time.time())))
                    self.save_recorded_data()
                    self.recorded_hands = {}
                    self.recorded_poses = {}
                    self.manual_poses = {}
                    self.recorded_frames = {}
                    self.recorded_ppg = {}
                    self.recorded_gyro = {}
                    self.recorded_acc = {}
                    self.start_timestamp = "0"
                elif key == ord("c"):
                    self.client = await searchAndConnectToWatch()
                    if(self.client is not None):
                        print("Connected to watch")
                        await subscribeToData(self.client, self.process_watch_data)
                    else:
                        print("Could not connect to watch")
                elif key == ord("j"):
                    self._manual_label = "Pose.Fist"
                    print(f"Manual label set to Fist")
                elif key == ord("k"):
                    self._manual_label = "Pose.Pinch"
                    print(f"Manual label set to Pinch")
                elif key == ord("l"):
                    self._manual_label = "Pose.IndexTap"
                    print(f"Manual label set to IndexTap")
                elif key == ord(" "):
                    print(f"Manual label set to Resting")
                    self._manual_label = "Pose.Resting"

async def start_window(poses: list[dict] = None):
    fingertracker = FingerTracking()
    await fingertracker.mainloop(poses)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pose Recording Tool")
    parser.add_argument("--path", type=str , help="Path to poses.json file")
    args = parser.parse_args()
    print(args)
    if args.path:
        try:
            with open(args.path, 'r') as f:
                poses = json.load(f)
        except FileNotFoundError:
            print(f"File {args.path} not found.")
            poses = None
    else:
        poses = None
    asyncio.run(start_window(poses))
