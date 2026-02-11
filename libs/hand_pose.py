from __future__ import annotations

from typing import Any

import numpy as np
from leap import datatypes as ldt
import math


def euler_from_quaternion(quat: ldt.Quaternion):
    """
    Convert a quaternion into euler angles (roll, pitch, yaw)
    roll is rotation around x in radians (counterclockwise)
    pitch is rotation around y in radians (counterclockwise)
    yaw is rotation around z in radians (counterclockwise)
    """
    x = quat.x
    y = quat.y
    z = quat.z
    w = quat.w
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = math.atan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = math.asin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.atan2(t3, t4)

    return np.array([roll_x, pitch_y, yaw_z])  # in radians


def calculate_similarity(input_vector: np.ndarray[tuple[int], Any],
                         target_vector: np.ndarray[tuple[int], Any]) -> float:
    """
    Calculate cosine similarity between two vectors.

    :param input_vector: Array of input pose.
    :param target_vector: Array of target pose.
    :return: Cosine similarity score.
    """
    dot_product = np.dot(input_vector, target_vector)
    norm_input = np.linalg.norm(input_vector)
    norm_target = np.linalg.norm(target_vector)
    return dot_product / (norm_input * norm_target)


def get_vector_between_joints(start_joint: ldt.Vector, end_joint: ldt.Vector):
    direction =  np.array(
        [end_joint.x, end_joint.y, end_joint.z]) - np.array(
        [start_joint.x, start_joint.y, start_joint.z])
    return direction


def get_direction_from_bone(bone: ldt.Bone):
    return get_vector_between_joints(bone.prev_joint, bone.next_joint)


class HandPose:
    def __init__(self, hand: ldt.Hand):
        # Each fingers pose is represented by a vector from its base
        # This matrix represents the hands pose
        # It can be flattened in order to have a one dimensional vector
        # Then, cosine similarity can be applied
        self.poseMatrix = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0],  # Thumb
            [0, 0, 0, 0, 0, 0, 0, 0, 0],  # Index
            [0, 0, 0, 0, 0, 0, 0, 0, 0],  # Middle
            [0, 0, 0, 0, 0, 0, 0, 0, 0],  # Ring
            [0, 0, 0, 0, 0, 0, 0, 0, 0],  # Pinky
        ])
        self.poseVector = self.poseMatrix.flatten()
        self.pinch_distance = 0
        self.pinch_strength = 0
        self.hand_rotation = 0
        self.set_pose_from_hand(hand)

    def set_pose_from_hand(self, hand: ldt.Hand):
        self.pinch_distance = hand.pinch_distance
        self.pinch_strength = hand.pinch_strength
        self.hand_rotation = np.rad2deg(euler_from_quaternion(hand.palm.orientation))
        self.poseMatrix = np.array([
            [get_direction_from_bone(hand.thumb.proximal), get_direction_from_bone(hand.thumb.intermediate),
             get_direction_from_bone(hand.thumb.distal)],
            [get_direction_from_bone(hand.index.proximal), get_direction_from_bone(hand.index.intermediate),
             get_direction_from_bone(hand.index.distal)],
            [get_direction_from_bone(hand.middle.proximal), get_direction_from_bone(hand.middle.intermediate),
             get_direction_from_bone(hand.middle.distal)],
            [get_direction_from_bone(hand.ring.proximal), get_direction_from_bone(hand.ring.intermediate),
             get_direction_from_bone(hand.ring.distal)],
            [get_direction_from_bone(hand.pinky.proximal), get_direction_from_bone(hand.pinky.intermediate),
             get_direction_from_bone(hand.pinky.distal)]
        ])
        self.poseVector = self.poseMatrix.flatten()

    def compare_to_pose(self, target_pose: HandPose):
        return calculate_similarity(self.poseVector, target_pose.poseVector)
