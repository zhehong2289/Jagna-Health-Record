# app.py
import streamlit as st
import cv2
import numpy as np
import json
import tempfile
import os
from utils.ocr import extract_fields
from utils.sheets import init_google_sheets, write_to_sheet

# Page configuration
st.set_page_config(
    page_title="Form OCR Processor",
    page_icon="📄",
    layout="wide"
)

# Initialize Google Sheets
@st.cache_resource
def init_sheets():
    return init_google_sheets('credentials.json')

# Load field configuration
with open('field_config.json', 'r') as f:
    FIELD_CONFIG = json.load(f)

# Google Sheet URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1iHuQpPtutue1rHdQ0S7wl13Lm7qy6uiPRnD8Y5N1LoQ/edit?usp=sharing"

# App title and description
st.title("📄 Form OCR Processor")
st.markdown("Upload a form image to extract data and save to Google Sheets")

# File upload section
st.header("1. Upload Form Image")
uploaded_file = st.file_uploader(
    "Choose a form image", 
    type=['png', 'jpg', 'jpeg'],
    help="Upload a clear image of the form"
)

if uploaded_file is not None:
    # Display the uploaded image
    st.subheader("Uploaded Form")
    st.image(uploaded_file, caption="Uploaded Form", use_column_width=True)
    
    # Process the image
    with st.spinner("Processing form..."):
        # Convert uploaded file to OpenCV image
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # Extract fields
        results = extract_fields(image, FIELD_CONFIG)
    
    # Display extracted data for review
    st.header("2. Review Extracted Data")
    st.info("Please review the extracted data before saving to Google Sheets")
    
    # Create a nice display of extracted data
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("👤 Name")
        name_value = st.text_input("Name", value=results.get('name', ''), key="name_review")
    
    with col2:
        st.subheader("🔢 Age") 
        age_value = st.text_input("Age", value=results.get('age', ''), key="age_review")
    
    with col3:
        st.subheader("💬 Feedback")
        feedback_value = st.text_area("Feedback", value=results.get('feedback', ''), key="feedback_review", height=100)
    
    # Save to Google Sheets section
    st.header("3. Save to Google Sheets")
    
    if st.button("💾 Save to Google Sheets", type="primary", use_container_width=True):
        with st.spinner("Saving to Google Sheets..."):
            try:
                # Initialize sheets client
                sheets_client = init_sheets()
                
                if sheets_client:
                    # Prepare data for sheet
                    sheet_data = [name_value, age_value, feedback_value]
                    
                    # Write to sheet
                    success, sheet_msg = write_to_sheet(sheets_client, SHEET_URL, sheet_data)

                    if success:
                        st.success(f"✅ Data successfully saved to Google Sheets! ({sheet_msg})")
                        st.balloons()

                        # Show what was saved
                        st.subheader("Saved Data:")
                        st.json({
                            "Name": name_value,
                            "Age": age_value,
                            "Feedback": feedback_value
                        })
                    else:
                        st.error(f"❌ Failed to save data to Google Sheets: {sheet_msg}")
                        st.info("Please check the sheet permissions, sheet name 'Health Records', and try again.")
                else:
                    st.error("❌ Google Sheets connection not available.")
                    
            except Exception as e:
                st.error(f"❌ Error saving to Google Sheets: {str(e)}")
    
    # Alternative: Download as CSV
    st.header("Alternative: Download Data")
    
    # Create downloadable data
    csv_data = f"Name,Age,Feedback\n{name_value},{age_value},{feedback_value.replace(chr(10), ' ')}"
    
    st.download_button(
        label="📥 Download as CSV",
        data=csv_data,
        file_name="form_data.csv",
        mime="text/csv",
        use_container_width=True
    )

else:
    # Show instructions when no file is uploaded
    st.info("👆 Please upload a form image to get started")
    
    # Show sample field configuration
    with st.expander("📋 Expected Form Fields"):
        st.json(FIELD_CONFIG)
    
    # Show tips for better OCR
    with st.expander("💡 Tips for Better OCR Results"):
        st.markdown("""
        - Use clear, high-resolution images
        - Ensure good lighting and contrast
        - Position the form straight and flat
        - Avoid shadows and glares
        - Use standard fonts if possible
        """)

# Footer
st.markdown("---")
st.markdown("Form OCR Processor • Built with Streamlit")