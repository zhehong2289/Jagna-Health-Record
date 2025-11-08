# test_sheet_access.py
import gspread
from google.oauth2.service_account import Credentials
import traceback

def test_sheet_access():
    print("=== Testing Sheet Access ===")
    
    # Authenticate
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
    client = gspread.authorize(creds)
    print("✓ Authentication successful")
    
    # Try to access the specific sheet
    sheet_url = "https://docs.google.com/spreadsheets/d/1iHuQpPtutue1rHdQ0S7wl13Lm7qy6uiPRnD8Y5N1LoQ/edit?usp=sharing"
    
    try:
        print(f"Attempting to open: {sheet_url}")
        sheet = client.open_by_url(sheet_url)
        print(f"✓ Sheet opened: {sheet.title}")
        
        # Try to get worksheets
        worksheets = sheet.worksheets()
        print(f"✓ Worksheets found: {len(worksheets)}")
        for i, ws in enumerate(worksheets):
            print(f"  Worksheet {i}: {ws.title}")
        
        # Try to access the first worksheet
        worksheet = sheet.get_worksheet(0)
        print(f"✓ First worksheet: {worksheet.title}")
        
        # Try to read some data
        print("Reading existing data...")
        existing_data = worksheet.get_all_records()
        print(f"✓ Existing records: {len(existing_data)}")
        if existing_data:
            print("Sample data:", existing_data[0])
        
        # Try to write test data
        print("Writing test data...")
        test_data = ["Test Name", "25", "Test Feedback"]
        worksheet.append_row(test_data)
        print(f"✓ Data written successfully: {test_data}")
        
        return True
        
    except gspread.exceptions.APIError as e:
        print(f"✗ Google API Error: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_sheet_access()