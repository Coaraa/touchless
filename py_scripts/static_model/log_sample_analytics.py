import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

df = pd.read_csv("gesture_runtime_log.csv")
df_pipe = pd.read_csv("mediapipe_log.csv")

fig, (ax1, ax2, ax6, ax3, ax4, ax5) = plt.subplots(6, 1, figsize=(12,8), sharex=True)

ax1.scatter(df["timestamp"], df["gesture_name"], s=10)
ax1.set_title("Prediction timeline")
ax1.set_ylabel("Predicted class")

ax2.plot(df["timestamp"], df["model_activated"], label="Model Active")
ax2.set_title("Model Activation")
ax2.set_ylabel("Active (0/1)")
ax2.legend()

ax6.plot(df["timestamp"], df["n_hands"], label="Number of hands")
ax6.set_title("Model Activation")
ax6.set_ylabel("n_hands")
ax6.legend()

sc = ax3.scatter(df_pipe["timestamp"], df_pipe["hand_confidence"],s=8, c=df_pipe["hand_confidence"], cmap="viridis")
ax3.set_title("MediaPipe Hand Confidence Over Time")
ax3.set_ylabel("Confidence (0–1)")

ax4.plot(df["timestamp"], df["palm_x"], label="Palm X")
ax4.plot(df["timestamp"], df["smooth_x"], label="Mouse X")
ax4.set_title("X movement over time")
ax4.set_ylabel("X (normalized or px)")
ax4.legend()

ax5.plot(df["timestamp"], df["palm_y"], label="Palm Y")
ax5.plot(df["timestamp"], df["smooth_y"], label="Mouse Y")
ax5.set_title("Y movement over time")
ax5.set_xlabel("Time")
ax5.set_ylabel("Y (normalized or px)")
ax5.legend()


plt.tight_layout()
plt.show()


df_time = pd.read_csv("gesture_profile.csv")

plt.figure(figsize=(14,8))

plt.plot(df_time["frame"], df_time["t_capture"], label="Capture")
plt.plot(df_time["frame"], df_time["t_mediapipe"], label="Mediapipe")
plt.plot(df_time["frame"], df_time["t_normalize"], label="Normalize")
plt.plot(df_time["frame"], df_time["t_predict"], label="Predict")
plt.plot(df_time["frame"], df_time["t_mouse"], label="Mouse")
plt.plot(df_time["frame"], df_time["t_total"], label="Total frame time", linewidth=2)

plt.title("Frame vs Processing Time")
plt.xlabel("Frame")
plt.ylabel("Time (seconds)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

df = pd.read_csv("gesture_runtime_log.csv")
df_pipe = pd.read_csv("mediapipe_log.csv")

def plot_prediction_timeline(df):
    plt.figure(figsize=(12, 3))
    plt.scatter(df["timestamp"], df["gesture_name"], s=10)
    plt.title("Prediction Timeline")
    plt.ylabel("Predicted Class")
    plt.xlabel("Time")
    plt.tight_layout()
    plt.show()

def plot_model_activation(df):
    plt.figure(figsize=(12, 3))
    plt.plot(df["timestamp"], df["model_activated"], label="Model Active")
    plt.title("Model Activation")
    plt.ylabel("Active (0/1)")
    plt.xlabel("Time")
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_n_hands(df):
    plt.figure(figsize=(12, 3))
    plt.plot(df["timestamp"], df["n_hands"], label="Number of Hands")
    plt.title("Number of Hands Over Time")
    plt.ylabel("n_hands")
    plt.xlabel("Time")
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_hand_confidence(df_pipe):
    plt.figure(figsize=(12, 3))
    sc = plt.scatter(
        df_pipe["timestamp"],
        df_pipe["hand_confidence"],
        s=8,
        c=df_pipe["hand_confidence"],
        cmap="viridis"
    )
    plt.title("MediaPipe Hand Confidence Over Time")
    plt.ylabel("Confidence (0–1)")
    plt.xlabel("Time")
    plt.colorbar(sc, label="Confidence")
    plt.tight_layout()
    plt.show()

def plot_x_movement(df):
    plt.figure(figsize=(12, 3))
    plt.plot(df["timestamp"], df["palm_x"])
    plt.plot(df["timestamp"], df["smooth_x"])
    plt.title("X Movement Over Time")
    plt.ylabel("X")
    plt.xlabel("Time")
    plt.legend(["Palm X", "Mouse X"])
    plt.tight_layout()
    plt.show()

def plot_y_movement(df):
    plt.figure(figsize=(12, 3))
    plt.plot(df["timestamp"], df["palm_y"])
    plt.plot(df["timestamp"], df["smooth_y"])
    plt.title("Y Movement Over Time")
    plt.ylabel("Y")
    plt.xlabel("Time")
    plt.legend(["Palm Y", "Mouse Y"])
    plt.tight_layout()
    plt.show()

def plot_all(df, df_pipe):
    plot_prediction_timeline(df)
    plot_model_activation(df)
    plot_n_hands(df)
    plot_hand_confidence(df_pipe)
    plot_x_movement(df)
    plot_y_movement(df)

plot_all(df, df_pipe)