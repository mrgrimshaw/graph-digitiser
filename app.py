import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
import pandas as pd
from streamlit_drawable_canvas import st_canvas

st.set_page_config(layout="wide")
st.title("📈 Graph Digitiser")

# Upload image
uploaded_file = st.file_uploader("Upload a graph image", type=["jpg", "jpeg", "png"])
if not uploaded_file:
    st.stop()

file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Show raw image
st.image(img_rgb, caption="Uploaded Image", use_container_width=True)

st.markdown("### Step 1: Select 3 Reference Points")
st.markdown("Click: (1) Bottom-left (0,0), (2) Top-left (0,Ymax), (3) Bottom-right (Xmax,0)")

canvas_result = st_canvas(
    fill_color="rgba(255, 0, 0, 0.3)",
    stroke_width=3,
    stroke_color="#FF0000",
    background_image=Image.fromarray(img_rgb),
    update_streamlit=True,
    height=600,
    drawing_mode="point",
    key="calibration_canvas"
)

if canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) >= 3:
    points = canvas_result.json_data["objects"]
    pts = [np.array([p["left"], p["top"]]) for p in points[:3]]

    bl, tl, br = pts
    tr = br + (tl - bl)

    Xmax = st.number_input("X axis max", value=10.0)
    Ymax = st.number_input("Y axis max", value=10.0)
    PIXELS_PER_UNIT = 100
    dst = np.array([
        [0, Ymax * PIXELS_PER_UNIT],
        [0, 0],
        [Xmax * PIXELS_PER_UNIT, Ymax * PIXELS_PER_UNIT],
        [Xmax * PIXELS_PER_UNIT, 0]
    ], dtype=np.float32)

    src = np.array([bl, tl, br, tr], dtype=np.float32)
    output_size = (int(Xmax * PIXELS_PER_UNIT), int(Ymax * PIXELS_PER_UNIT))
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img_rgb, M, output_size)

    st.image(warped, caption="Warped Image", use_container_width=True)

    # Overlay grid
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(warped, extent=[0, Xmax, 0, Ymax], aspect='auto', zorder=0)
    ax.set_xlim(0, Xmax)
    ax.set_ylim(0, Ymax)
    ax.set_xlabel("X axis")
    ax.set_ylabel("Y axis")
    ax.set_title("XY Grid Over Aligned Image")
    ax.grid(True, which='both', color='gray', linestyle='--', linewidth=0.5, zorder=1)
    ax.set_xticks(np.arange(0, Xmax + 1, 1))
    ax.set_yticks(np.arange(0, Ymax + 1, 1))
    st.pyplot(fig)

    st.success("Calibration complete. You can now implement point labelling next.")
else:
    st.info("Waiting for 3 calibration points...")
