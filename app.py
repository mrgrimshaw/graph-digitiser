#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

st.set_page_config(layout="wide")
st.title("🧭 Graph Photo Digitiser")

uploaded_file = st.file_uploader("📷 Upload a graph photo", type=["jpg", "jpeg", "png"])
Xmax = st.number_input("Grid X max", value=10)
Ymax = st.number_input("Grid Y max", value=10)

if uploaded_file:
    img = Image.open(uploaded_file)
    img_array = np.array(img)
    st.image(img_array, caption="Original Image", use_column_width=True)

    st.markdown("### 🖱️ Click 3 points: bottom-left (0,0), top-left (0,Ymax), bottom-right (Xmax,0)")

    if "clicked" not in st.session_state:
        st.session_state.clicked = []
        st.session_state.labels = []

    fig, ax = plt.subplots()
    ax.imshow(img_array)

    if len(st.session_state.clicked) == 3:
        bl = np.array(st.session_state.clicked[0])
        tl = np.array(st.session_state.clicked[1])
        br = np.array(st.session_state.clicked[2])

        x_vec = br - bl
        y_vec = tl - bl

        def xy_to_pixel(x, y):
            return bl + x * (x_vec / Xmax) + y * (y_vec / Ymax)

        grid_x = np.linspace(0, Xmax, Xmax + 1)
        grid_y = np.linspace(0, Ymax, Ymax + 1)

        for x in grid_x:
            p1, p2 = xy_to_pixel(x, 0), xy_to_pixel(x, Ymax)
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'w--', linewidth=0.5)

        for y in grid_y:
            p1, p2 = xy_to_pixel(0, y), xy_to_pixel(Xmax, y)
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'w--', linewidth=0.5)

        for pt, label in zip(st.session_state.labels, st.session_state.clicked[3:]):
            ax.plot(pt[0], pt[1], 'ro')
            ax.text(pt[0], pt[1], label, color='red', fontsize=8)

    click = st.pyplot(fig)

    st.markdown("Click on the image above (use Streamlit rerun workaround by refreshing)")

    if st.button("🔁 Reset"):
        st.session_state.clicked = []
        st.session_state.labels = []

    st.write("**Clicked Points:**", st.session_state.clicked)

    if len(st.session_state.clicked) > 3:
        df = pd.DataFrame(
            [(x, y, l) for (x, y), l in zip(st.session_state.clicked[3:], st.session_state.labels)],
            columns=["X", "Y", "Label"]
        )
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "digitised_points.csv", "text/csv")

    label = st.text_input("Label for next point")
    if label and st.button("💾 Add Label"):
        st.session_state.labels.append(label)

