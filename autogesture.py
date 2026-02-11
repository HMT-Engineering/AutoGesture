import asyncio
import tkinter as tk
import subprocess
from tkinter import filedialog
from PIL import Image, ImageTk
import json

from libs.hand_pose import HandPose, json_to_hand_pose

poses: dict[str, HandPose] = {}
recorded_pose = None

def start_pose_calibration():
    try:
        res = subprocess.run(["python3", "libs/pose_calibration.py", "--single"], check=True,
            capture_output = True, # Python >= 3.7 only
            text = True # Python >= 3.7 only)
        )
        pose_json = str(res.stdout)
        if (pose_json != "CANCELLED"):
            hand_pose = json_to_hand_pose(json.loads(pose_json))
            print("Pose loaded:", hand_pose.as_dict())
            return hand_pose
        else:
            print("Pose calibration cancelled.")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error running script1.py: {e}")

def start_pose_recorder():
    try:
        poses_dict = filedialog.askopenfilename(title="Select Poses", filetypes=[("JSON files", "*.json")])
        res = subprocess.run(["python3", "libs/finger_tracking.py", "--path", poses_dict])
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
    for key, data in poses.items():
        pose_item_frame = tk.Frame(hand_angles_frame)
        pose_item_frame.pack(fill="x", pady=2)

        label_text = f"{key}:\n{data.pose_vector}"
        label = tk.Label(pose_item_frame, text=label_text, anchor="w", justify="left", font=("Courier", 12))
        label.pack(side="left", fill="x", expand=True)
        
        def remove_pose(k=key):
            if k in poses:
                del poses[k]
                update_hand_angles_count()

        remove_btn = tk.Button(pose_item_frame, text="Remove", command=remove_pose, fg="#d32f2f")
        remove_btn.pack(side="right", padx=5)

def save_poses_to_files():
    #poses[pose_name] = { 
            #     "pose": pose_value,
            #     "pose_vector": f'[{pose.handRot["x"]},{pose.handRot["y"]},{pose.thumb["base"]},{pose.thumb["tip"]},{pose.index["base"]},{pose.index["middle"]},{pose.index["tip"]},{pose.middle["base"]},{pose.middle["middle"]},{pose.middle["tip"]},{pose.ring["base"]},{pose.ring["middle"]},{pose.ring["tip"]},{pose.pinky["base"]},{pose.pinky["middle"]},{pose.pinky["tip"]}]'
            # }
    save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if save_path:
        try:
            with open(save_path, 'w') as file:
                poses_dict = {}
                for pose_name, pose in poses.items():
                    poses_dict[pose_name] = pose.as_dict()
                json.dump(poses_dict, file, indent=4)  # Save poses as JSON
            print(f"Poses saved to {save_path}")
        except Exception as e:
            print(f"Error saving poses: {e}")

def load_poses_from_files():
    pose_files = filedialog.askopenfilenames(title="Select Poses", filetypes=[("JSON files", "*.json")])
    for pose_file in pose_files:
        try:
            with open(pose_file, 'r') as file:
                data = json.load(file)  # Parse JSON data       
                #poses[pose_name] = { 
                #     "pose": pose_value,
                #     "pose_vector": f'[{pose.handRot["x"]},{pose.handRot["y"]},{pose.thumb["base"]},{pose.thumb["tip"]},{pose.index["base"]},{pose.index["middle"]},{pose.index["tip"]},{pose.middle["base"]},{pose.middle["middle"]},{pose.middle["tip"]},{pose.ring["base"]},{pose.ring["middle"]},{pose.ring["tip"]},{pose.pinky["base"]},{pose.pinky["middle"]},{pose.pinky["tip"]}]'
                # }
                for pose_name, pose_data in data.items():
                    poses[pose_name] = json_to_hand_pose(pose_data)
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
        if not pose_name:
            tk.messagebox.showerror("Error", "Pose name cannot be empty.")
            return
        try:
            pose_value_str = pose_value_entry.get()
            if not pose_value_str:
                tk.messagebox.showerror("Error", "Pose value cannot be empty.")
                return
            pose_value = int(pose_value_str)
            
            pose = start_pose_calibration()
            if pose is None:
                tk.messagebox.showerror("Error", "Pose calibration cancelled.")
                dialog.destroy()
                return
            print("Pose:", pose)
            poses[pose_name] = pose
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
        hand_angles_frame.pack(fill="x", pady=5, after=management_frame)
        toggle_button.config(text="Hide Poses")
        update_hand_angles_count()


# Create the main window
root = tk.Tk()
root.title("AutoGesture")
# Set the window size
root.geometry("600x600")

# Add a logo at the top left corner
try:
    image = Image.open("logo.png")
    image = image.resize((64, 64))
    logo = ImageTk.PhotoImage(image)
    logo_label = tk.Label(root, image=logo)
    logo_label.image = logo  # Keep a reference to avoid garbage collection
    logo_label.pack(anchor="nw", padx=20, pady=10)
except Exception as e:
    print(f"Could not load logo: {e}")

# Main container for better padding
main_container = tk.Frame(root, padx=20, pady=10)
main_container.pack(fill="both", expand=True)

# --- Management Block ---
management_frame = tk.LabelFrame(main_container, text="Pose Management", padx=10, pady=10, font=("Helvetica", 10, "bold"))
management_frame.pack(fill="x", pady=5)

hand_angles_count_label = tk.Label(management_frame, text=f"Loaded Poses: {len(poses)}") 
hand_angles_count_label.grid(row=0, column=0, sticky="w", pady=5)

toggle_button = tk.Button(management_frame, text="Show Poses", command=toggle_hand_angles_display)
toggle_button.grid(row=0, column=1, padx=10, pady=5)

button2 = tk.Button(management_frame, text="Load Poses From File", command=load_poses_from_files)
button2.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

button3 = tk.Button(management_frame, text="Save Poses to File", command=save_poses_to_files)
button3.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

# Hand angles list (collapsible)
hand_angles_frame = tk.Frame(main_container)

# --- Add Block ---
add_frame = tk.LabelFrame(main_container, text="Add New Pose", padx=10, pady=10, font=("Helvetica", 10, "bold"))
add_frame.pack(fill="x", pady=10)

add_pose_button = tk.Button(add_frame, text="Add Pose", command=open_add_pose_dialog, bg="#e1e1e1")
add_pose_button.pack(fill="x", pady=5)

# --- Recording Block ---
recording_frame = tk.Frame(root)
recording_frame.pack(side="bottom", fill="x", padx=20, pady=20)

start_recorder_button = tk.Button(
    recording_frame, 
    text="Start Recorder", 
    command=start_pose_recorder,
    bg="#4CAF50",
    fg="red",
    font=("Helvetica", 12, "bold"),
    padx=20,
    pady=10,
    relief="raised"
)
start_recorder_button.pack(side="right")

# Start the Tkinter event loop
root.mainloop()