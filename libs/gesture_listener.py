
import json
import time
from typing import Callable
import leap
from leap.events import Event

from hand_pose import HandPose, get_most_similar_pose


class GestureListener(leap.Listener):
    def __init__(self, poseDetectedCallback: Callable[[Event,str], None], customposes: dict[str, HandPose] = None):
        self.restingRotation = 0
        self.restingRotations = [0]
        self.poseDetectedCallback = poseDetectedCallback
        if customposes is not None:
            self.poses = customposes

    def on_tracking_event(self, event):
        if len(event.hands) != 0:
            hand = event.hands[0]
            pose = HandPose()
            pose.set_pose_from_hand(hand)
            similar_pose = get_most_similar_pose(pose, self.poses)
            # if(pose.decodedPose == Pose.Resting or pose.decodedPose == Pose.WristFlickOut):
            #     self.restingRotations.append(pose.handRot[1])
            #     if(len(self.restingRotations) > 40):
            #         self.restingRotations.pop(0)
            #         self.restingRotation = np.average(self.restingRotations)

            self.poseDetectedCallback(event,similar_pose)
