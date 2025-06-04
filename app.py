import streamlit as st
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from streamlit_drawable_canvas import st_canvas

st.set_page_config(layout="wide")
st.title("📈 Graph Digitiser (No OpenCV)")

# Upload image
uploaded_file = st.file_uploader("Upload a graph image", type=["jpg", "jpeg", "png"])
if not uploaded_file:
    st.stop()

image = Image.open(uploaded_file).convert("RGB")
img_np = np.array(image)
img_height, img_width = img_np.shape[:2]

# Show image
st.image(image, caption="Uploaded Image", use_container_width=True)

# Select 3 reference points
st.markdown("### Step 1: Select 3 Reference Points")
st.markdown("Click: (1) Bottom-left (0,0), (2) Top-left (0,Ymax), (3) Bottom-right (Xmax,0)")

canvas_result = st_canvas(
    fill_color="rgba(255, 0, 0, 0.3)",
    stroke_width=3,
    stroke_color="#FF0000",
    background_image=image,
    update_streamlit=True,
    height=600,
    drawing_mode="point",
    key="calibration_canvas"
)

if canvas_result.json_data and len(canvas_result.json_data["objects"]) >= 3:
    points = canvas_result.json_data["objects"]
    pts = [np.array([p["left"], p["top"]]) for p in points[:3]]

    bl, tl, br = pts
    tr = br + (tl - bl)  # Approximate top-right

    # Axis settings
    Xmax = st.number_input("X axis max", value=10.0)
    Ymax = st.number_input("Y axis max", value=10.0)

    # Grid overlay
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(img_np)
    ax.set_title("XY Grid Over Image")

    # Approximate coordinate axes using clicked points
    x_axis = np.linspace(bl[0], br[0], int(Xmax) + 1)
    y_axis = np.linspace(bl[1], tl[1], int(Ymax) + 1)

    for x in x_axis:
        ax.axvline(x=x, color='gray', linestyle='--', linewidth=0.7)
    for y in y_axis:
        ax.axhline(y=y, color='gray', linestyle='--', linewidth=0.7)

    ax.set_xlim(0, img_width)
    ax.set_ylim(img_height, 0)
    st.pyplot(fig)
    st.success("Grid overlay complete. You can now digitise points or label them.")
else:
    st.info("Waiting for 3 calibration points...")
