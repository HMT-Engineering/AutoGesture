import time
import leap
import numpy as np
import cv2

from leapmotion import Pose, decode_pose

from leap.events import Event

class HandAngles():
    
    def __init__(self, parameters):
        self.thumb = parameters["thumb"]
        self.index = parameters["index"]
        self.middle = parameters["middle"]
        self.ring = parameters["ring"]
        self.pinky = parameters["pinky"]
        self.handRot = parameters["handRot"]
        self.pinchDistance = parameters["pinchDistance"]
        self.pinchStrength = parameters["pinchStrength"]
class Canvas:
    def __init__(self):
        self.name = "Hand Visualizer"
        self.screen_size = [500, 500]
        self.hands_colour = (255, 255, 255)
        self.font_colour = (0, 255, 44)
        self.recording_font_colour = (0, 0, 255)
        self.hands_format = "Skeleton"
        self.output_image = np.zeros((self.screen_size[0], self.screen_size[1], 3), np.uint8)

    def get_joint_position(self, bone):
        if bone:
            return int(bone.x + (self.screen_size[1] / 2)), int(bone.z + (self.screen_size[0] / 2))
        else:
            return None
        
    def save_to_file(self, filename):
        cv2.imwrite(filename, self.output_image)

    def render_timestamp(self,time):
        cv2.putText(
            self.output_image,
            time,
            (self.screen_size[1] - 140, self.screen_size[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )

    def render_instructions(self,instructions, recording=False):
        cv2.putText(
            self.output_image,
            instructions,
            (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.recording_font_colour if recording else self.font_colour,
            1,
        )
    def render_hand_angles(self, hand: HandAngles): 
        cv2.putText(
            self.output_image,
            f"Thumb: {hand.thumb["base"],hand.thumb["tip"]}",
            (10, self.screen_size[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        cv2.putText(
            self.output_image,
            f"Index: {hand.index["base"],hand.index["middle"],hand.index["tip"]}",
            (10, self.screen_size[0] - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        cv2.putText(
            self.output_image,
            f"Middle: {hand.middle["base"],hand.middle["middle"],hand.middle["tip"]}",
            (10, self.screen_size[0] - 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        cv2.putText(
            self.output_image,
            f"Ring: {hand.ring["base"],hand.ring["middle"],hand.ring["tip"]}",
            (10, self.screen_size[0] - 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        cv2.putText(
            self.output_image,
            f"Pinky: {hand.pinky["base"],hand.pinky["middle"],hand.pinky["tip"]}",
            (10, self.screen_size[0] - 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        cv2.putText(
            self.output_image,
            f"Hand Rotation: {hand.handRot}",
            (10, self.screen_size[0] - 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        cv2.putText(
            self.output_image,
            f"Pinch Distance: {hand.pinchDistance}",
            (10, self.screen_size[0] - 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        cv2.putText(
            self.output_image,
            f"Pinch Strength: {hand.pinchStrength}",
            (10, self.screen_size[0] - 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        
    def render_pose(self, motion:Pose):
         cv2.putText(
            self.output_image,
            f"Detected Motion: {motion}",
            (10, self.screen_size[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
         
    def render_hands(self, event:Event):
        # Clear the previous image
        self.output_image[:, :] = 0

        if len(event.hands) == 0:
            return

        for i in range(0, len(event.hands)):
            hand = event.hands[i]
            for index_digit in range(0, 5):
                digit = hand.digits[index_digit]
                for index_bone in range(0, 4):
                    bone = digit.bones[index_bone]
                    wrist = self.get_joint_position(hand.arm.next_joint)
                    elbow = self.get_joint_position(hand.arm.prev_joint)
                    if wrist:
                        cv2.circle(self.output_image, wrist, 3, self.hands_colour, -1)

                    if elbow:
                        cv2.circle(self.output_image, elbow, 3, self.hands_colour, -1)

                    if wrist and elbow:
                        cv2.line(self.output_image, wrist, elbow, self.hands_colour, 2)

                    bone_start = self.get_joint_position(bone.prev_joint)
                    bone_end = self.get_joint_position(bone.next_joint)

                    if bone_start:
                        cv2.circle(self.output_image, bone_start, 3, self.hands_colour, -1)

                    if bone_end:
                        cv2.circle(self.output_image, bone_end, 3, self.hands_colour, -1)

                    if bone_start and bone_end:
                        cv2.line(self.output_image, bone_start, bone_end, self.hands_colour, 2)

                    if ((index_digit == 0) and (index_bone == 0)) or (
                        (index_digit > 0) and (index_digit < 4) and (index_bone < 2)
                    ):
                        index_digit_next = index_digit + 1
                        digit_next = hand.digits[index_digit_next]
                        bone_next = digit_next.bones[index_bone]
                        bone_next_start = self.get_joint_position(bone_next.prev_joint)
                        if bone_start and bone_next_start:
                            cv2.line(
                                self.output_image,
                                bone_start,
                                bone_next_start,
                                self.hands_colour,
                                2,
                            )

                    if index_bone == 0 and bone_start and wrist:
                        cv2.line(self.output_image, bone_start, wrist, self.hands_colour, 2)


class TrackingListener(leap.Listener):
    def __init__(self, canvas):
        self.poses = []
        self.canvas : Canvas = canvas
        self.pose = "No Hands Detected"
        self.restingRotation = 0
        self.restingRotations = [0]

    def on_connection_event(self, event):
        pass

    def on_device_event(self, event):
        try:
            with event.device.open():
                info = event.device.get_info()
        except leap.LeapCannotOpenDeviceError:
            info = event.device.get_info()

        print(f"Found device {info.serial}")

    def on_tracking_event(self, event):
        if len(event.hands) != 0:
            hand = event.hands[0]
            hand_type = "Left" if str(hand.type) == "HandType.Left" else "Right"

            tmppose = decode_pose(hand, self.restingRotation)
            self.poses.append(tmppose.decodedPose.value)

            if(tmppose.decodedPose == Pose.Resting or tmppose.decodedPose == Pose.WristFlickOut):
                self.restingRotations.append(tmppose.handRot[1])
                #print(self.restingRotations)
                if(len(self.restingRotations) > 40):
                    self.restingRotations.pop(0)
                    self.restingRotation = np.average(self.restingRotations)

            if(len(self.poses) > 5):
                self.poses.pop(0)
                self.pose = Pose(np.median(self.poses))
                print(f"Hand pose: {self.pose.name}")
        self.canvas.render_hands(event,self.pose)


def main():
    canvas = Canvas()

    print(canvas.name)

    tracking_listener = TrackingListener(canvas)

    connection = leap.Connection()
    connection.add_listener(tracking_listener)

    running = True

    with connection.open():
        connection.set_tracking_mode(leap.TrackingMode.Desktop)

        while running:
            cv2.imshow(canvas.name, canvas.output_image)
            
            key = cv2.waitKey(1)

            if key == ord("x"):
                running = False
            
if __name__ == "__main__":
    main()
