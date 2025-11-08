# mobile_app.py
import streamlit as st
import cv2
import numpy as np
import io
import json
import tempfile
import os
from PIL import Image
from utils.ocr import extract_fields
from utils.sheets import init_google_sheets, write_to_sheet

# Mobile-optimized page config
st.set_page_config(
    page_title="Form Scanner",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load field configuration
with open('field_config.json', 'r') as f:
    FIELD_CONFIG = json.load(f)

# Google Sheet URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1iHuQpPtutue1rHdQ0S7wl13Lm7qy6uiPRnD8Y5N1LoQ/edit?usp=sharing"

# Initialize Sheets (cached)
@st.cache_resource
def get_sheets_client():
    return init_google_sheets('credentials.json')

# App header
st.markdown("""
<div style="text-align: center;">
    <h1>📱 Form Scanner</h1>
    <p>Take a photo of your form and upload it</p>
</div>
""", unsafe_allow_html=True)

# File upload - mobile optimized
st.markdown("### 1. Upload Form Photo")
uploaded_file = st.file_uploader(
    "Choose form image",
    type=['png', 'jpg', 'jpeg'],
    help="Take a clear photo of the form or select from gallery",
    label_visibility="collapsed"
)

if uploaded_file is not None:
    # Display uploaded image
    st.markdown("### 📸 Form Preview")

    # Read uploaded bytes once (so both PIL and OpenCV can use the same buffer)
    uploaded_bytes = uploaded_file.read()

    # Convert for display using PIL from bytes
    try:
        image = Image.open(io.BytesIO(uploaded_bytes))
        st.image(image, use_container_width=True, caption="Uploaded Form")
    except Exception:
        st.error("Unable to open uploaded image for preview. The file may be corrupted or in an unsupported format.")

    # Process image
    with st.spinner("🔄 Scanning form..."):
        # Convert to OpenCV format
        file_bytes = np.frombuffer(uploaded_bytes, dtype=np.uint8)
        cv_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Fail-fast if decoding failed (prevents NoneType slicing in ocr.extract_fields)
        if cv_image is None:
            st.error("Failed to decode uploaded image. Please upload a valid PNG/JPG image taken from the camera or gallery.")
            # stop further execution of this script path
            st.stop()

        # Extract fields
        results = extract_fields(cv_image, FIELD_CONFIG)
    
    # Display extracted data
    st.markdown("### 📋 Extracted Data")
    st.info("Review the data below before saving")
    
    # Create editable fields
    col1, col2 = st.columns(2)
    
    with col1:
        name_value = st.text_input(
            "**Name**",
            value=results.get('name', ''),
            key="name_input"
        )
        
        blood_sugar_value = st.text_input(
            "**Blood Sugar Level (mg/dL)**",
            value=results.get('blood_sugar', ''),
            key="blood_sugar_input",
            help="Scanned value can be edited if needed"
        )
        
        systolic_value = st.text_input(
            "**Systolic Pressure (mmHg)**",
            value=results.get('systolic', ''),
            key="systolic_input",
            help="Upper number of blood pressure reading"
        )
    
    with col2:
        age_value = st.text_input(
            "**Age**", 
            value=results.get('age', ''),
            key="age_input"
        )
        
        diastolic_value = st.text_input(
            "**Diastolic Pressure (mmHg)**",
            value=results.get('diastolic', ''),
            key="diastolic_input",
            help="Lower number of blood pressure reading"
        )
    
    feedback_value = st.text_area(
        "**Feedback**",
        value=results.get('feedback', ''),
        height=100,
        key="feedback_input"
    )
    
    # Save to Google Sheets
    st.markdown("### 💾 Save to Database")
    
    if st.button("✅ Save to Google Sheets", type="primary", use_container_width=True):
        with st.spinner("Saving to database..."):
            try:
                sheets_client = get_sheets_client()
                
                if sheets_client:
                    sheet_data = [
                        name_value,
                        age_value,
                        blood_sugar_value,
                        systolic_value,
                        diastolic_value,
                        feedback_value
                    ]
                    success, sheet_msg = write_to_sheet(sheets_client, SHEET_URL, sheet_data)

                    if success:
                        st.success(f"🎉 Data saved successfully! ({sheet_msg})")
                        st.balloons()

                        # Show confirmation
                        st.markdown("#### Saved Data:")
                        st.json({
                            "Name": name_value,
                            "Age": age_value,
                            "Blood Sugar": blood_sugar_value,
                            "Blood Pressure": f"{systolic_value}/{diastolic_value}",
                            "Feedback": feedback_value
                        })
                    else:
                        st.error(f"❌ Failed to save: {sheet_msg}")
                        st.info("Please verify the sheet exists, the service account has Editor access, and the worksheet is named 'Health Records'.")
                else:
                    st.error("❌ Connection error. Please check internet.")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

else:
    # Instructions when no file uploaded
    st.markdown("---")
    st.markdown("""
    ### 📝 How to Use:
    1. **Take a photo** of your form using the camera
    2. **Make sure** the form is well-lit and flat
    3. **Upload** the photo above
    4. **Review** the extracted data
    5. **Save** to database
    
    ### 💡 Tips for Best Results:
    - 📏 Keep the form flat and straight
    - 💡 Good lighting reduces errors
    - 📱 Hold phone parallel to form
    - 🖊️ Use dark ink on light paper
    """)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Form Scanner App • Mobile Optimized</div>", unsafe_allow_html=True)