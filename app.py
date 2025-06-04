#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📷 Graph Digitiser")

# Upload image
uploaded_file = st.file_uploader("Upload a photo of your graph", type=["png", "jpg", "jpeg"])
Xmax = st.number_input("Grid X max", value=10)
Ymax = st.number_input("Grid Y max", value=10)

# Canvas drawing mode
mode = st.radio("Canvas mode", ["Reference Points", "Label Points"])

if "ref_points" not in st.session_state:
    st.session_state.ref_points = []
if "data_points" not in st.session_state:
    st.session_state.data_points = []

if uploaded_file:
    img = Image.open(uploaded_file)
    width, height = img.size

    st.write(f"Image size: {width} x {height}")

    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=3,
        stroke_color="#FF0000",
        background_image=img,
        update_streamlit=True,
        height=height,
        width=width,
        drawing_mode="point",
        point_display_radius=5,
        key="canvas"
    )

    if canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]
        new_clicks = [(obj["left"], obj["top"]) for obj in objects]

        if mode == "Reference Points":
            if len(new_clicks) != len(st.session_state.ref_points):
                st.session_state.ref_points = new_clicks[:3]
        elif mode == "Label Points":
            if len(new_clicks) > len(st.session_state.ref_points) + len(st.session_state.data_points):
                new_point = new_clicks[-1]
                label = st.text_input("Label for new point", value=f"P{len(st.session_state.data_points)+1}")
                if st.button("Add Label"):
                    st.session_state.data_points.append((new_point[0], new_point[1], label))

    # Once reference points are selected
    if len(st.session_state.ref_points) == 3:
        st.success("3 reference points selected.")
        bl = np.array(st.session_state.ref_points[0])
        tl = np.array(st.session_state.ref_points[1])
        br = np.array(st.session_state.ref_points[2])
        x_vec = br - bl
        y_vec = tl - bl

        def pixel_to_xy(px, py):
            rel = np.array([px, py]) - bl
            x = np.dot(rel, x_vec) / np.dot(x_vec, x_vec) * Xmax
            y = np.dot(rel, y_vec) / np.dot(y_vec, y_vec) * Ymax
            return round(x, 2), round(y, 2)

        if st.session_state.data_points:
            xy_data = [pixel_to_xy(px, py) + (label,) for px, py, label in st.session_state.data_points]
            df = pd.DataFrame(xy_data, columns=["X", "Y", "Label"])
            st.dataframe(df)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV", csv, "digitised_points.csv", "text/csv")

    if st.button("🔁 Reset All"):
        st.session_state.ref_points = []
        st.session_state.data_points = []
