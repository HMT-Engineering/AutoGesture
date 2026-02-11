from typing import Any

import numpy as np
from leap import datatypes as ldt


def calculate_similarity(input_vector: np.ndarray[tuple[int], Any], target_vector: np.ndarray[tuple[int], Any]) -> float:
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


class HandPose:
    def __init__(self):
        # Each fingers pose is represented by a vector from its base
        # This matrix represents the hands pose
        # It can be flattened in order to have a one dimensional vector
        # Then, cosine similarity can be applied
        self.poseMatrix = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0], #Thumb
            [0, 0, 0, 0, 0, 0, 0, 0, 0], #Index
            [0, 0, 0, 0, 0, 0, 0, 0, 0], #Middle
            [0, 0, 0, 0, 0, 0, 0, 0, 0], #Ring
            [0, 0, 0, 0, 0, 0, 0, 0, 0], #Pinky
        ])
        self.poseVector = self.poseMatrix.flatten()

    def set_pose_from_hand(self, hand: ldt.Hand):
        self.poseMatrix = np.array([
            hand.thumb.proximal,hand.thumb.intermediate,hand.thumb.distal,
            hand.index.proximal,hand.index.intermediate,hand.index.distal,
            hand.middle.proximal,hand.middle.intermediate,hand.middle.distal,
            hand.ring.proximal,hand.ring.intermediate,hand.ring.distal,
            hand.pinky.proximal,hand.pinky.intermediate,hand.pinky.distal
        ])
        self.poseVector = self.poseMatrix.flatten()

    def compare_to_pose(self, target_pose: HandPose):
        return calculate_similarity(self.poseVector, target_pose.poseVector)
