# debug.py
import traceback
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(__file__))

from utils.sheets import init_google_sheets
import gspread

def debug_sheets():
    print("=== Debugging Google Sheets Connection ===")
    
    # 1. Test credentials loading
    print("1. Testing credentials...")
    try:
        client = init_google_sheets('credentials.json')
        if client:
            print("✓ Credentials loaded successfully")
        else:
            print("✗ Failed to load credentials")
            return
    except Exception as e:
        print(f"✗ Credentials error: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        return
    
    # 2. Test sheet access
    print("\n2. Testing sheet access...")
    sheet_url = "https://docs.google.com/spreadsheets/d/1iHuQpPtutue1rHdQ0S7wl13Lm7qy6uiPRnD8Y5N1LoQ/edit?usp=sharing"
    
    try:
        sheet = client.open_by_url(sheet_url)
        print("✓ Sheet accessed successfully")
        print(f"✓ Sheet title: {sheet.title}")
    except gspread.exceptions.SpreadsheetNotFound:
        print("✗ Spreadsheet not found - check URL and sharing permissions")
        return
    except gspread.exceptions.APIError as e:
        print(f"✗ Google API Error: {e}")
        print(f"Error details: {e.response.text if hasattr(e, 'response') else 'No response details'}")
        return
    except Exception as e:
        print(f"✗ Sheet access error: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Full traceback: {traceback.format_exc()}")
        return
    
    # 3. Test worksheet access
    print("\n3. Testing worksheet access...")
    try:
        worksheet = sheet.get_worksheet(0)  # First sheet
        print(f"✓ Worksheet accessed: {worksheet.title}")
    except Exception as e:
        print(f"✗ Worksheet error: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        return
    
    # 4. Test writing data
    print("\n4. Testing data writing...")
    try:
        test_data = ["Test Name", "25", "Test Feedback"]
        worksheet.append_row(test_data)
        print("✓ Data written successfully!")
        print(f"✓ Test data: {test_data}")
    except Exception as e:
        print(f"✗ Write error: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        return
    
    print("\n=== All tests passed! ===")

if __name__ == "__main__":
    debug_sheets()