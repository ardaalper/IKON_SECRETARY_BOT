import streamlit as st
from ultralytics import YOLO
from PIL import Image
import tempfile

# Load model
model = YOLO("best.pt")

st.title("YOLO Object Detection Demo")
st.write("Upload an image and see the detections.")

# Upload image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Open image
    image = Image.open(uploaded_file).convert("RGB")

    # Save to temp file for YOLO
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        image.save(tmp_file.name)
        results = model(tmp_file.name)

    # Show original image
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Show detection result (YOLO saves plots automatically in results[0].plot())
    res_img = results[0].plot()
    st.image(res_img, caption="Detection Result", use_column_width=True)
