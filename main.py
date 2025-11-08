# main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import cv2
import numpy as np
import json
import os
from utils.ocr import extract_fields
from utils.sheets import init_google_sheets, write_to_sheet

app = FastAPI(title="Form OCR Backend")

# Load field configuration
try:
    with open('field_config.json', 'r') as f:
        FIELD_CONFIG = json.load(f)
    print("Field configuration loaded successfully")
except Exception as e:
    print(f"Error loading field config: {e}")
    FIELD_CONFIG = {}

# Initialize Google Sheets client
try:
    SHEETS_CLIENT = init_google_sheets('credentials.json')
    if SHEETS_CLIENT:
        print("Google Sheets client ready")
    else:
        print("Google Sheets client not available")
except Exception as e:
    print(f"Error initializing Google Sheets: {e}")
    SHEETS_CLIENT = None

# Google Sheets configuration (you'll need to set this)
# Get this from your Google Sheet URL: https://docs.google.com/spreadsheets/d/[THIS_IS_YOUR_SHEET_ID]/edit...
SHEET_URL = "https://docs.google.com/spreadsheets/d/1iHuQpPtutue1rHdQ0S7wl13Lm7qy6uiPRnD8Y5N1LoQ/edit?usp=sharing"

@app.get("/")
async def root():
    return {"message": "Form OCR API is running"}

@app.get("/config")
async def get_config():
    """Endpoint to check loaded configuration"""
    return {
        "field_config": FIELD_CONFIG,
        "sheets_available": SHEETS_CLIENT is not None
    }

@app.post("/process-form/")
async def process_form(
    image: UploadFile = File(...),
    save_to_sheets: bool = True,
    sheet_url: str = None
):
    try:
        if not FIELD_CONFIG:
            raise HTTPException(status_code=500, detail="Field configuration not loaded")
        
        # Read uploaded image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Extract fields
        results = extract_fields(img, FIELD_CONFIG)
        
        # Prepare response
        response = {
            "status": "success", 
            "filename": image.filename,
            "extracted_data": results,
            "saved_to_sheets": False
        }
        
        # Save to Google Sheets if requested and available
        if save_to_sheets and SHEETS_CLIENT:
            # Use provided sheet URL or default
            target_sheet_url = sheet_url or SHEET_URL
            
            if target_sheet_url != "YOUR_GOOGLE_SHEET_URL_HERE":
                # Prepare data for sheet (convert dict to list maintaining order)
                sheet_data = [
                    results.get('name', ''),
                    results.get('age', ''),
                    results.get('blood_sugar', ''),
                    results.get('systolic', ''),
                    results.get('diastolic', ''),
                    results.get('feedback', '')
                ]
                
                # Write to sheet
                success, sheet_msg = write_to_sheet(SHEETS_CLIENT, target_sheet_url, sheet_data)
                response["saved_to_sheets"] = success
                response["sheet_url"] = target_sheet_url
                response["sheet_message"] = sheet_msg
            else:
                response["sheets_message"] = "Please set your Google Sheet URL in the code"
        
        return JSONResponse(response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/test-sheets/")
async def test_sheets(sheet_url: str = None):
    """Test endpoint to verify Google Sheets connection"""
    if not SHEETS_CLIENT:
        raise HTTPException(status_code=500, detail="Google Sheets client not available")
    
    try:
        target_url = sheet_url or SHEET_URL
        if target_url == "YOUR_GOOGLE_SHEET_URL_HERE":
            return {"error": "Please set your Google Sheet URL first"}
        
        # Test by writing a simple row
        test_data = ["Test Entry", "25", "120", "120", "80", "This is a test from OCR API"]
        success, msg = write_to_sheet(SHEETS_CLIENT, target_url, test_data)

        return {
            "status": "success" if success else "failed",
            "message": msg,
            "sheet_url": target_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sheets test error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

