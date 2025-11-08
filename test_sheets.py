# test_sheets.py
import requests
import json

def test_sheets_integration():
    print("Testing OCR with Google Sheets integration...")
    
    # Your actual sheet URL
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1iHuQpPtutue1rHdQ0S7wl13Lm7qy6uiPRnD8Y5N1LoQ/edit?usp=sharing"
    
    # Test the main endpoint
    with open('reference_form.png', 'rb') as f:
        files = {'image': f}
        response = requests.post(
            "http://127.0.0.1:8000/process-form/",
            files=files,
            params={'save_to_sheets': True, 'sheet_url': SHEET_URL}
        )
    
    result = response.json()
    print("\nOCR + Sheets Result:")
    print(json.dumps(result, indent=2))
    
    if result.get('saved_to_sheets'):
        print("✅ SUCCESS! Form data saved to Google Sheets!")
    else:
        print("❌ Data not saved to Google Sheets")

if __name__ == "__main__":
    test_sheets_integration()