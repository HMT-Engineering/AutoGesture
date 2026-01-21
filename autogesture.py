import asyncio
import tkinter as tk
import subprocess
from tkinter import filedialog
from PIL import Image, ImageTk
import json

from pose_calibration import calibrate_pose
from visualizer import HandAngles
poses = {}
recorded_pose = None

def start_pose_calibration():
    try:
        res = subprocess.run(["python3", "pose_calibration.py", "--single"], check=True,
            capture_output = True, # Python >= 3.7 only
            text = True # Python >= 3.7 only)
        )
        pose_json = str(res.stdout)
        if (pose_json != "CANCELLED"):
            pose = json.loads(pose_json)
            hand_angle = HandAngles(pose)
            print("Pose loaded:", hand_angle.__dict__)
            return hand_angle
        else:
            print("Pose calibration cancelled.")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error running script1.py: {e}")

def start_pose_recorder():
    try:
        poses = filedialog.askopenfilename(title="Select Poses", filetypes=[("JSON files", "*.json")])
        res = subprocess.run(["python3", "finger_tracking.py", "--path", poses])
        # pose_json = str(res.stdout)
        # if (pose_json != "CANCELLED"):
        #     pose = json.loads(pose_json)
        #     hand_angle = HandAngles(pose)
        #     print("Pose loaded:", hand_angle.__dict__)
        #     return hand_angle
        # else:
        #     print("Pose calibration cancelled.")
        #     return None
    except subprocess.CalledProcessError as e:
        print(f"Error running script1.py: {e}")


# Update the label whenever poses are loaded
def update_hand_angles_count():
    hand_angles_count_label.config(text=f"Loaded Poses: {len(poses)}")
    for widget in hand_angles_frame.winfo_children():
        widget.destroy()  # Clear the frame
    for key in poses.keys():
        label = tk.Label(hand_angles_frame, text=key)
        label.pack(anchor="w")

def save_poses_to_files():
    #poses[pose_name] = { 
            #     "pose": pose_value,
            #     "poseVector": f'[{pose.handRot["x"]},{pose.handRot["y"]},{pose.thumb["base"]},{pose.thumb["tip"]},{pose.index["base"]},{pose.index["middle"]},{pose.index["tip"]},{pose.middle["base"]},{pose.middle["middle"]},{pose.middle["tip"]},{pose.ring["base"]},{pose.ring["middle"]},{pose.ring["tip"]},{pose.pinky["base"]},{pose.pinky["middle"]},{pose.pinky["tip"]}]'
            # }
    save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if save_path:
        try:
            with open(save_path, 'w') as file:
                json.dump(poses, file, indent=4)  # Save poses as JSON
            print(f"Poses saved to {save_path}")
        except Exception as e:
            print(f"Error saving poses: {e}")

def load_poses_from_files():
    poses = filedialog.askopenfilenames(title="Select Poses", filetypes=[("JSON files", "*.json")])
    for pose_file in poses:
        try:
            with open(pose_file, 'r') as file:
                data = json.load(file)  # Parse JSON data       
                #poses[pose_name] = { 
                #     "pose": pose_value,
                #     "poseVector": f'[{pose.handRot["x"]},{pose.handRot["y"]},{pose.thumb["base"]},{pose.thumb["tip"]},{pose.index["base"]},{pose.index["middle"]},{pose.index["tip"]},{pose.middle["base"]},{pose.middle["middle"]},{pose.middle["tip"]},{pose.ring["base"]},{pose.ring["middle"]},{pose.ring["tip"]},{pose.pinky["base"]},{pose.pinky["middle"]},{pose.pinky["tip"]}]'
                # }
                for pose_name, pose_data in data.items():
                    poses[pose_name] = {
                        "pose": pose_data["pose"],
                        "poseVector": pose_data["poseVector"]
                    }
        except Exception as e:
            print(f"Error reading {pose_file}: {e}")
    print("Loaded HandAngles:", [ha for ha in poses.keys()])
    update_hand_angles_count()


def open_add_pose_dialog():
    dialog = tk.Toplevel(root)
    dialog.title("Add Pose")

    tk.Label(dialog, text="Pose Name:").grid(row=0, column=0, padx=10, pady=5)
    pose_name_entry = tk.Entry(dialog)
    pose_name_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(dialog, text="Pose Value:").grid(row=1, column=0, padx=10, pady=5)
    pose_value_entry = tk.Entry(dialog)
    pose_value_entry.grid(row=1, column=1, padx=10, pady=5)

    def add_pose():
        print("Adding pose...")
        pose_name = pose_name_entry.get()
        try:
            pose = start_pose_calibration()
            if pose is None:
                tk.messagebox.showerror("Error", "Pose calibration cancelled.")
                dialog.destroy()
                return
            print("Pose:", pose)
            pose_value = int(pose_value_entry.get())
            poses[pose_name] = { 
                "pose": pose_value,
                "poseVector": f'[{pose.handRot["x"]},{pose.handRot["y"]},{pose.thumb["base"]},{pose.thumb["tip"]},{pose.index["base"]},{pose.index["middle"]},{pose.index["tip"]},{pose.middle["base"]},{pose.middle["middle"]},{pose.middle["tip"]},{pose.ring["base"]},{pose.ring["middle"]},{pose.ring["tip"]},{pose.pinky["base"]},{pose.pinky["middle"]},{pose.pinky["tip"]}]'
            }
            update_hand_angles_count()
            dialog.destroy()
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Pose value must be a number.")
    add_button = tk.Button(dialog, text="Add", command=add_pose)
    add_button.grid(row=3, column=0, columnspan=2, pady=10)


def toggle_hand_angles_display():
    if hand_angles_frame.winfo_ismapped():
        hand_angles_frame.pack_forget()
        toggle_button.config(text="Show Poses")
    else:
        hand_angles_frame.pack(pady=5)
        toggle_button.config(text="Hide Poses")
        update_hand_angles_count()


# Create the main window
root = tk.Tk()
root.title("AutoGesture")
# Set the window size
root.geometry("512x400")

# Add a logo at the top left corner
image = Image.open("logo.png")
image = image.resize((64, 64))
logo = ImageTk.PhotoImage(image)
logo_label = tk.Label(root, image=logo)
logo_label.image = logo  # Keep a reference to avoid garbage collection
logo_label.pack(anchor="nw", padx=10, pady=10)


frame = tk.Frame(root, borderwidth=2, relief="groove")
frame.pack(pady=10)
# Label to show the number of loaded hand angles
hand_angles_count_label = tk.Label(frame, text=f"Loaded Poses: {len(poses)}") 
hand_angles_count_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

# Add a collapsible frame to display the keys of the hand_angles dictionary

toggle_button = tk.Button(frame, text="Show Poses", command=toggle_hand_angles_display)
toggle_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")

button2 = tk.Button(frame, text="Load Poses From File", command=load_poses_from_files)
button2.grid(row=1, column=0, padx=5, pady=5, sticky="w")

button3 = tk.Button(frame, text="Save Poses to File", command=save_poses_to_files)
button3.grid(row=1, column=1, padx=5, pady=5, sticky="w")


hand_angles_frame = tk.Frame(root)


add_pose_button = tk.Button(frame, text="Add Pose", command=open_add_pose_dialog)
add_pose_button.grid(row=2, column=0, padx=5, pady=5, sticky="w")
add_pose_button = tk.Button(frame, text="Start Recorder", command=start_pose_recorder)
add_pose_button.grid(row=2, column=1, padx=5, pady=5, sticky="w")



# Start the Tkinter event loop
root.mainloop()