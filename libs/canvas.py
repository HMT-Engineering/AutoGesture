import numpy as np
import cv2

from handAngles import HandAngles
from leapmotion import Pose

from leap.events import Event

from hand_pose import HandPose


class Canvas:
    def __init__(self):
        self.name = "Hand Visualizer"
        self.screen_size = [600, 1500]
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

    def render_timestamp(self, time):
        cv2.putText(
            self.output_image,
            time,
            (self.screen_size[1] - 140, self.screen_size[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )

    def render_instructions(self, instructions, recording=False):
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
            f"Thumb: {hand.thumb['base'], hand.thumb['tip']}",
            (10, self.screen_size[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        cv2.putText(
            self.output_image,
            f"Index: {hand.index['base'], hand.index['middle'], hand.index['tip']}",
            (10, self.screen_size[0] - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        cv2.putText(
            self.output_image,
            f"Middle: {hand.middle['base'], hand.middle['middle'], hand.middle['tip']}",
            (10, self.screen_size[0] - 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        cv2.putText(
            self.output_image,
            f"Ring: {hand.ring['base'], hand.ring['middle'], hand.ring['tip']}",
            (10, self.screen_size[0] - 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        cv2.putText(
            self.output_image,
            f"Pinky: {hand.pinky['base'], hand.pinky['middle'], hand.pinky['tip']}",
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

    def render_hand_canonical_pose(self, hand: HandPose):
        cv2.putText(
            self.output_image,
            f"Thumb: {hand.pose_vector[0:9]}",
            (10, self.screen_size[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        cv2.putText(
            self.output_image,
            f"Index: {hand.pose_vector[9:18]}",
            (10, self.screen_size[0] - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        cv2.putText(
            self.output_image,
            f"Middle: {hand.pose_vector[18:27]}",
            (10, self.screen_size[0] - 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        cv2.putText(
            self.output_image,
            f"Ring: {hand.pose_vector[27:36]}",
            (10, self.screen_size[0] - 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        cv2.putText(
            self.output_image,
            f"Pinky: {hand.pose_vector[36:45]}",
            (10, self.screen_size[0] - 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        cv2.putText(
            self.output_image,
            f"Hand Rotation: {hand.palm_orientation}",
            (10, self.screen_size[0] - 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        cv2.putText(
            self.output_image,
            f"Pinch Distance: {hand.pinch_distance}",
            (10, self.screen_size[0] - 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )
        cv2.putText(
            self.output_image,
            f"Pinch Strength: {hand.pinch_strength}",
            (10, self.screen_size[0] - 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )

    def render_pose(self, motion: str, similarity: float = 0.0):
        cv2.putText(
            self.output_image,
            f"Detected Motion: {motion} (Similarity: {similarity:.2f})",
            (10, self.screen_size[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.font_colour,
            1,
        )

    def render_hands(self, event: Event):
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

