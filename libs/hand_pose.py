from __future__ import annotations

import json
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


def get_canonical_direction_from_bone_stable(bone, coordinates_system, origin):
    p_local_prev = np.array([bone.prev_joint.x, bone.prev_joint.y, bone.prev_joint.z]) - origin
    p_local_next = np.array([bone.next_joint.x, bone.next_joint.y, bone.next_joint.z]) - origin
    return coordinates_system.T @ (p_local_next - p_local_prev)


def get_canonical_direction_from_bone(bone: ldt.Bone, coordinates_system: np.ndarray, palm_position: np.ndarray):
    p_local_prev = np.array(
        [bone.prev_joint.x, bone.prev_joint.y, bone.prev_joint.z]) - palm_position
    p_canon_prev = coordinates_system.T @ p_local_prev
    p_local_next = np.array(
        [bone.next_joint.x, bone.next_joint.y, bone.next_joint.z]) - palm_position
    p_canon_next = coordinates_system.T @ p_local_next

    return p_canon_next - p_canon_prev


def normalize(v):
    return v / np.linalg.norm(v)


def get_hand_coordinate_system_stable(hand: ldt.Hand):
    wrist = np.array([hand.arm.next_joint.x, hand.arm.next_joint.y, hand.arm.next_joint.z])
    index_mcp = np.array([hand.index.metacarpal.prev_joint.x,
                          hand.index.metacarpal.prev_joint.y,
                          hand.index.metacarpal.prev_joint.z])
    pinky_mcp = np.array([hand.pinky.metacarpal.prev_joint.x,
                          hand.pinky.metacarpal.prev_joint.y,
                          hand.pinky.metacarpal.prev_joint.z])

    # X axis: across palm (index -> pinky)
    x = normalize(pinky_mcp - index_mcp)

    # Forward vector: wrist -> palm center
    palm_center = 0.5 * (index_mcp + pinky_mcp)
    forward = normalize(palm_center - wrist)

    # Z axis: palm normal
    z = normalize(np.cross(x, forward))

    # Y axis: orthogonal to X and Z
    y = normalize(np.cross(z, x))

    R = np.stack([x, y, z], axis=1)  # Columns are axes
    return R, wrist


def get_hand_coordinate_system(hand: ldt.Hand):
    palm_dir = np.array([hand.palm.direction.x, hand.palm.direction.y, hand.palm.direction.z])
    palm_normal = np.array([hand.palm.normal.x, hand.palm.normal.y, hand.palm.normal.z])

    # Build hand basis
    z = normalize(palm_dir)
    y = normalize(palm_normal)
    x = normalize(np.cross(y, z))
    y = normalize(np.cross(z, x))

    R = np.stack([x, y, z], axis=1)
    return R


def json_to_hand_pose(json_data: Any):
    pose = HandPose()
    pose.pinch_distance = json_data["pinch_distance"]
    pose.pinch_strength = json_data["pinch_strength"]
    pose.palm_orientation = np.array(json_data["palm_orientation"])
    pose.palm_position = np.array(json_data["palm_position"])
    pose.pose_vector = np.array(json_data["pose_vector"])
    return pose


class HandPose:
    def __init__(self):
        # Each fingers pose is represented by a vector from its base
        # This matrix represents the hands pose
        # It can be flattened in order to have a one dimensional vector
        # Then, cosine similarity can be applied
        self.pose_vector = np.array([
            0, 0, 0, 0, 0, 0, 0, 0, 0,  # Thumb
            0, 0, 0, 0, 0, 0, 0, 0, 0,  # Index
            0, 0, 0, 0, 0, 0, 0, 0, 0,  # Middle
            0, 0, 0, 0, 0, 0, 0, 0, 0,  # Ring
            0, 0, 0, 0, 0, 0, 0, 0, 0,  # Pinky
        ])
        self.pinch_distance = 0
        self.pinch_strength = 0
        self.palm_orientation = np.array([0, 0, 0, 0])
        self.palm_position = np.array([0, 0, 0])

    def as_dict(self):
        return {
            "pinch_distance": self.pinch_distance,
            "pinch_strength": self.pinch_strength,
            "palm_orientation": self.palm_orientation.tolist(),
            "palm_position": self.palm_position.tolist(),
            "pose_vector": self.pose_vector.tolist()
        }

    def set_pose_from_hand(self, hand: ldt.Hand):
        self.pinch_distance = hand.pinch_distance
        self.pinch_strength = hand.pinch_strength
        self.palm_orientation = np.array(
            [hand.palm.orientation.x, hand.palm.orientation.y, hand.palm.orientation.z, hand.palm.orientation.w])
        self.palm_position = np.array([hand.palm.position.x, hand.palm.position.y, hand.palm.position.z])

        hand_coordinates = get_hand_coordinate_system(hand)
        palm_pos = self.palm_position

        self.pose_vector = np.array([
            get_canonical_direction_from_bone(hand.thumb.proximal, hand_coordinates, palm_pos),
            get_canonical_direction_from_bone(hand.thumb.intermediate, hand_coordinates, palm_pos),
            get_canonical_direction_from_bone(hand.thumb.distal, hand_coordinates, palm_pos),
            get_canonical_direction_from_bone(hand.index.proximal, hand_coordinates, palm_pos),
            get_canonical_direction_from_bone(hand.index.intermediate, hand_coordinates, palm_pos),
            get_canonical_direction_from_bone(hand.index.distal, hand_coordinates, palm_pos),
            get_canonical_direction_from_bone(hand.middle.proximal, hand_coordinates, palm_pos),
            get_canonical_direction_from_bone(hand.middle.intermediate, hand_coordinates, palm_pos),
            get_canonical_direction_from_bone(hand.middle.distal, hand_coordinates, palm_pos),
            get_canonical_direction_from_bone(hand.ring.proximal, hand_coordinates, palm_pos),
            get_canonical_direction_from_bone(hand.ring.intermediate, hand_coordinates, palm_pos),
            get_canonical_direction_from_bone(hand.ring.distal, hand_coordinates, palm_pos),
            get_canonical_direction_from_bone(hand.pinky.proximal, hand_coordinates, palm_pos),
            get_canonical_direction_from_bone(hand.pinky.intermediate, hand_coordinates, palm_pos),
            get_canonical_direction_from_bone(hand.pinky.distal, hand_coordinates, palm_pos)
        ]).flatten()

    def compare_to_pose(self, target_pose: HandPose):
        return calculate_similarity(self.pose_vector, target_pose.pose_vector)


def get_most_similar_pose(hand_pose : HandPose, poses: dict[str,HandPose]) -> HandPose:
    # if self.handRot[0] < -30:
    #     self.decodedPose = Pose.WristFlickDown
    # elif self.handRot[0] > 50:
    #     self.decodedPose = Pose.WristFlickUp
    # elif (self.handRot[1] - restingRotation) > 15:
    #     self.decodedPose = Pose.WristFlickOut
    # elif self.handRot[1] < -15: ##UNATURAL MOVEMENT
    #     self.decodedPose = Pose.WristFlickIn
    highestSimilarity = 0
    decodedPose = ""
    for pose in poses.keys():
        similarity = hand_pose.compare_to_pose(poses[pose])
        if similarity > highestSimilarity:
            decodedPose = pose
            highestSimilarity = similarity
    if highestSimilarity < 0.9:
        decodedPose = "unknown"
    return decodedPose