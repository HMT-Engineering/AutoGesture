import asyncio
import json
import time
from tkinter import Tk, filedialog
import cv2
import leap
from leap import datatypes as ldt
import numpy as np
import leap
from leapmotion import euler_from_quaternion
from visualizer import Canvas, HandAngles
import argparse

def decode_pose(hand: ldt.Hand):
    pinchDistance = hand.pinch_distance
    pinchStrength = hand.pinch_strength
    thumb = hand.digits[0]
    thumbBaseAngle = get_angle(thumb.proximal, thumb.intermediate)
    thumbTipAngle = get_angle(thumb.intermediate, thumb.distal)
    index = hand.digits[1]
    indexBaseAngle = get_angle(index.metacarpal, index.proximal)
    indexMiddleAngle = get_angle(index.proximal, index.intermediate)
    indexTipAngle = get_angle(index.intermediate, index.distal)
    middle = hand.digits[2]
    middleBaseAngle = get_angle(middle.metacarpal, middle.proximal)
    middleMiddleAngle = get_angle(middle.proximal, middle.intermediate)
    middleTipAngle = get_angle(middle.intermediate, middle.distal)
    ring = hand.digits[3]
    ringBaseAngle = get_angle(ring.metacarpal, ring.proximal)
    ringMiddleAngle = get_angle(ring.proximal, ring.intermediate)
    ringTipAngle = get_angle(ring.intermediate, ring.distal)
    pinky = hand.digits[4]
    pinkyBaseAngle = get_angle(pinky.metacarpal, pinky.proximal)
    pinkyMiddleAngle = get_angle(pinky.proximal, pinky.intermediate)
    pinkyTipAngle = get_angle(pinky.intermediate, pinky.distal)
    handRot = np.rad2deg(euler_from_quaternion(hand.palm.orientation))
    if handRot[2] < 0:
        handRot[2] = handRot[2] + 360
    return HandAngles(
        {
            "pinchDistance": int(pinchDistance),
            "pinchStrength": int(pinchStrength),
            "thumb": {"base": thumbBaseAngle, "tip": thumbTipAngle},
            "index": {
                "base": indexBaseAngle,
                "middle": indexMiddleAngle,
                "tip": indexTipAngle,
            },
            "middle": {
                "base": middleBaseAngle,
                "middle": middleMiddleAngle,
                "tip": middleTipAngle,
            },
            "ring": {
                "base": ringBaseAngle,
                "middle": ringMiddleAngle,
                "tip": ringTipAngle,
            },
            "pinky": {
                "base": pinkyBaseAngle,
                "middle": pinkyMiddleAngle,
                "tip": pinkyTipAngle,
            },
            "handRot": {
                "x": int(handRot[0]),
                "y": int(handRot[1]),
            }
        }
    )


def get_angle(bone1: ldt.Bone, bone2: ldt.Bone):
    bone_1_direction = np.array(
        [bone1.next_joint.x, bone1.next_joint.y, bone1.next_joint.z]
    ) - np.array([bone1.prev_joint.x, bone1.prev_joint.y, bone1.prev_joint.z])
    bone_2_direction = np.array(
        [bone2.next_joint.x, bone2.next_joint.y, bone2.next_joint.z]
    ) - np.array([bone2.prev_joint.x, bone2.prev_joint.y, bone2.prev_joint.z])
    dotProduct = np.vecdot(bone_1_direction, bone_2_direction)
    norm = np.linalg.norm(bone_1_direction) * np.linalg.norm(bone_2_direction)
    CosTheta = np.maximum(np.minimum(dotProduct / norm, 1), -1)
    angle = np.real(np.arccos(CosTheta))
    return int(np.degrees(angle))


class PoseCalibration(leap.Listener):
    def __init__(self):
        self.client = None
        self.running = False
        self.canvas = Canvas()
        self.framerate = 30
        self.last_frame_time = time.time()

    def on_tracking_event(self, event):
        if len(event.hands) != 0:
            hand = event.hands[0]
            self.handAngles = decode_pose(hand)
            self.canvas.render_hands(event)
            timestamp = str(int(1000 * (time.time())))
            self.canvas.render_timestamp(timestamp)
            self.canvas.render_hand_angles(self.handAngles)
            self.canvas.render_instructions("x: Exit, s: Capture Pose")

    async def mainloop(self):
        connection = leap.Connection()
        connection.add_listener(self)
        with connection.open():
            connection.set_tracking_mode(leap.TrackingMode.Desktop)
            self.running = True
            while self.running:
                cv2.imshow(self.canvas.name, self.canvas.output_image)
                key = cv2.waitKey(1)
                if key == ord("x"):
                    print("Exiting")
                    self.running = False
                elif key == ord("s"):
                    print("Save Grasp Position")
                    pose = self.handAngles
                    save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
                    if save_path:
                        with open(save_path, "w") as f:
                            json.dump(pose.__dict__, f)
                        print(f"Pose saved to {save_path}")
                    print(
                        f'[{pose.thumb["base"]},{pose.thumb["tip"]},{pose.index["base"]},{pose.index["middle"]},{pose.index["tip"]},{pose.middle["base"]},{pose.middle["middle"]},{pose.middle["tip"]},{pose.ring["base"]},{pose.ring["middle"]},{pose.ring["tip"]},{pose.pinky["base"]},{pose.pinky["middle"]},{pose.pinky["tip"]}]'
                    )

    async def record_single_pose(self):
        connection = leap.Connection()
        connection.add_listener(self)
        with connection.open():
            connection.set_tracking_mode(leap.TrackingMode.Desktop)
            self.running = True
            while self.running:
                cv2.imshow(self.canvas.name, self.canvas.output_image)
                key = cv2.waitKey(1)
                if key == ord("x"):
                    print("CANCELLED")
                    self.running = False
                elif key == ord("s"):
                    pose = self.handAngles
                    self.running = False
                    return pose

async def calibrate_pose():
    fingertracker = PoseCalibration()
    pose = await fingertracker.record_single_pose()
    return pose

async def start_window():
    fingertracker = PoseCalibration()
    root = Tk()
    await fingertracker.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pose Calibration Tool")
    parser.add_argument("--single", action="store_true", help="Record a single pose")
    args = parser.parse_args()

    if args.single:
        pose = asyncio.run(calibrate_pose())
        print(json.dumps(pose.__dict__))
    else: 
        asyncio.run(start_window())
