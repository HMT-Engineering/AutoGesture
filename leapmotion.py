"""Prints which hand is pinching every 50 frames, both hands can be tracked. 
The difference between the location of the distal of the index and the distal 
of the thumb is calculated and we check it against a threshold of 20 in each 
axis. If any one axis is off by more than 20, we say the finger and thumb are 
not pinching.
"""

import json
import time
from typing import Callable
import leap
from leap import datatypes as ldt
from enum import Enum
import math
from scipy.spatial.transform import Rotation as R
import numpy as np
from leap.events import Event
# Function to compute the angle between two vectors
def angle_between_vectors(v1, v2):
    # Normalize the vectors
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)
    
    # Compute the dot product
    dot_product = np.dot(v1, v2)
    
    # Ensure the value is within the valid range for acos due to floating-point errors
    dot_product = np.clip(dot_product, -1.0, 1.0)
    
    # Compute the angle in radians
    angle = np.arccos(dot_product)
    
    # Convert to degrees if you want
    angle_degrees = np.degrees(angle)
    
    return angle, angle_degrees

# Function to compute the angle around the Y-axis
def angle_around_y(v1, v2):
    # Project the vectors onto the XZ-plane (set Y component to 0)
    v1_xz = np.array([v1[0], 0, v1[2]])  # Set Y to 0
    v2_xz = np.array([v2[0], 0, v2[2]])  # Set Y to 0
    
    # Normalize the projected vectors
    v1_xz = v1_xz / np.linalg.norm(v1_xz)
    v2_xz = v2_xz / np.linalg.norm(v2_xz)
    
    # Compute the angle between the projected vectors in the XZ-plane
    angle_rad, angle_deg = angle_between_vectors(v1_xz, v2_xz)
    
    # To determine if it's clockwise or counterclockwise, calculate the cross product in the XZ-plane
    cross_product = np.cross(v1_xz, v2_xz)
    
    # The Z component of the cross product will tell us the direction:
    # - Positive Z component means counterclockwise (left-hand rule)
    # - Negative Z component means clockwise
    if cross_product[1] < 0:
        angle_rad = -angle_rad
        angle_deg = -angle_deg
    
    return angle_rad, angle_deg

 
def euler_from_quaternion(quat:ldt.Quaternion):
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
     
        return np.array([roll_x, pitch_y, yaw_z]) # in radians

    

class Pose(Enum):
    Pinch = 0
    Fist = 1
    Flat = 2
    IndexTap = 3
    AllFingerTap = 4
    WristFlickUp = 5
    WristFlickDown = 6
    WristFlickIn = 7
    WristFlickOut = 8
    PinkyPinch = 9
    Resting = 98
    Unknown = 99

default_poses = [
    {
        "pose": Pose.Pinch,
        "poseVector": np.array([7,12,46,47,27,11,16,11,10,11,9,11,7,9])
    },
    {
        "pose": Pose.Fist,
        "poseVector": np.array([46,38,77,81,38,87,87,40,88,84,40,83,82,42])
    },
    # {
    #     "pose": Pose.Flat,
    #     "poseVector": np.array([7,6,18,6,12,16,4,10,13,5,9,17,3,9])
    # },
    {
        "pose": Pose.IndexTap,
        "poseVector": np.array([3,4,66,51,28,27,18,9,17,14,7,8,8,8])
    },
    # {
    #     "pose": Pose.AllFingerTap,
    #     "poseVector": np.array([2,7,56,60,29,61,54,26,54,56,32,49,52,31])
    # },
    # {
    #     "pose": Pose.WristFlickUp,
    #     "poseVector": np.array([16,12,29,30,22,26,29,18,18,26,17,3,17,17])
    # },
    # {
    #     "pose": Pose.WristFlickDown,
    #     "poseVector": np.array([3,12,27,46,25,29,50,23,31,52,27,48,53,35])
    # },
    # {
    #     "pose": Pose.WristFlickIn,
    #     "poseVector": np.array([8,9,13,14,11,6,4,9,4,6,6,11,3,8])
    # },
    # {
    #     "pose": Pose.WristFlickOut,
    #     "poseVector": np.array([7,3,27,7,7,25,6,10,20,6,10,22,8,8])
    # },
    # {
    #     "pose": Pose.PinkyPinch,
    #     "poseVector": np.array([18,16,9,30,24,9,21,18,4,23,19,20,40,24])
    # },
    {
        "pose": Pose.Resting,
        "poseVector": np.array([7,3,9,11,8,8,12,7,11,13,8,5,9,7])
    }
]
class HandPose:
    def __init__(self):
        self.pose = Pose.Unknown
        self.poseVector = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0])

    def calculate_similarity(self, target_vector: np.ndarray[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        :param input_angles: Array of input angles.
        :param target_angles: Array of target angles.
        :return: Cosine similarity score.
        """
        dot_product = np.dot(self.poseVector, target_vector)
        norm_input = np.linalg.norm(self.poseVector)
        norm_target = np.linalg.norm(target_vector)
        return dot_product / (norm_input * norm_target)
    
def get_most_similar_pose(poseVector: np.ndarray[float], poses: list[dict]) -> HandPose:
    decodedPose = Pose.Resting
    handPose = HandPose()
    handPose.poseVector = poseVector
    # if self.handRot[0] < -30:
    #     self.decodedPose = Pose.WristFlickDown
    # elif self.handRot[0] > 50:
    #     self.decodedPose = Pose.WristFlickUp
    # elif (self.handRot[1] - restingRotation) > 15:
    #     self.decodedPose = Pose.WristFlickOut
    # elif self.handRot[1] < -15: ##UNATURAL MOVEMENT
    #     self.decodedPose = Pose.WristFlickIn
    highestSimilarity = 0
    for pose in poses:
        similarity = handPose.calculate_similarity(poseVector, pose["poseVector"])
        if similarity > highestSimilarity:
            decodedPose = pose["pose"]
            highestSimilarity = similarity
    if highestSimilarity < 0.9:
        decodedPose = Pose.Unknown
    handPose.pose = decodedPose

   

def decode_pose (hand: ldt.Hand, restingRotation = 0, poses: list[dict] = default_poses) -> HandPose:
    HandPose()
    pinchDistance = hand.pinch_distance
    pinchStrength = hand.pinch_strength
    thumb = hand.digits[0]
    print(thumb)
    thumbBaseAngle = get_angle(thumb.proximal,thumb.intermediate)
    thumbTipAngle = get_angle(thumb.intermediate,thumb.distal)
    index = hand.digits[1]
    indexBaseAngle = get_angle(index.metacarpal,index.proximal)
    indexMiddleAngle = get_angle(index.proximal,index.intermediate)
    indexTipAngle = get_angle(index.intermediate,index.distal)
    middle = hand.digits[2]
    middleBaseAngle = get_angle(middle.metacarpal,middle.proximal)
    middleMiddleAngle = get_angle(middle.proximal,middle.intermediate)
    middleTipAngle = get_angle(middle.intermediate,middle.distal)
    ring = hand.digits[3]
    ringBaseAngle = get_angle(ring.metacarpal,ring.proximal)
    ringMiddleAngle = get_angle(ring.proximal,ring.intermediate)
    ringTipAngle = get_angle(ring.intermediate,ring.distal)
    pinky = hand.digits[4]
    pinkyBaseAngle = get_angle(pinky.metacarpal,pinky.proximal)
    pinkyMiddleAngle = get_angle(pinky.proximal,pinky.intermediate)
    pinkyTipAngle = get_angle(pinky.intermediate,pinky.distal)
    handRot = np.rad2deg(euler_from_quaternion(hand.palm.orientation))
    if(handRot[2] < 0):
        handRot[2] = handRot[2] + 360
    poseVector = np.array([
        thumbBaseAngle,thumbTipAngle,
        indexBaseAngle,indexMiddleAngle,indexTipAngle,
        middleBaseAngle,middleMiddleAngle,middleTipAngle,
        ringBaseAngle,ringMiddleAngle,ringTipAngle,
        pinkyBaseAngle,pinkyMiddleAngle,pinkyTipAngle
    ])
    return get_most_similar_pose(poseVector, poses)
   


def get_angle(metacarpal_bone:ldt.Bone, proximal_phalange_bone:ldt.Bone):
    metacarpal_direction = np.array([metacarpal_bone.next_joint.x, metacarpal_bone.next_joint.y, metacarpal_bone.next_joint.z]) - np.array([metacarpal_bone.prev_joint.x, metacarpal_bone.prev_joint.y, metacarpal_bone.prev_joint.z])
    prox_phal_direction = np.array([proximal_phalange_bone.next_joint.x, proximal_phalange_bone.next_joint.y, proximal_phalange_bone.next_joint.z]) - np.array([proximal_phalange_bone.prev_joint.x, proximal_phalange_bone.prev_joint.y, proximal_phalange_bone.prev_joint.z])
    dotProduct = np.vecdot(metacarpal_direction,prox_phal_direction)
    norm = np.linalg.norm(metacarpal_direction)*np.linalg.norm(prox_phal_direction)
    CosTheta = np.maximum(np.minimum(dotProduct/norm,1),-1)
    angle = np.real(np.arccos(CosTheta))
    return np.degrees(angle)


class GestureListener(leap.Listener):
    def __init__(self, poseDetectedCallback: Callable[[Event,HandPose], None], customposes: dict[str, HandPose] = None):
        self.restingRotation = 0
        self.restingRotations = [0]
        self.poseDetectedCallback = poseDetectedCallback
        if customposes is not None:
            self.poses = customposes
        else:
            self.poses = default_poses

    def on_tracking_event(self, event):
        if len(event.hands) != 0:
            hand = event.hands[0]
            pose = decode_pose(hand, poses=self.poses)
            # if(pose.decodedPose == Pose.Resting or pose.decodedPose == Pose.WristFlickOut):
            #     self.restingRotations.append(pose.handRot[1])
            #     if(len(self.restingRotations) > 40):
            #         self.restingRotations.pop(0)
            #         self.restingRotation = np.average(self.restingRotations)

            self.poseDetectedCallback(event,pose)
