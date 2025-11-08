# test_service_account.py
import gspread
from google.oauth2.service_account import Credentials
import json

def test_service_account():
    print("=== Testing Service Account Access ===")
    
    # 1. Show service account email
    with open('credentials.json', 'r') as f:
        creds_data = json.load(f)
    service_account_email = creds_data['client_email']
    print(f"Service Account Email: {service_account_email}")
    
    # 2. Authenticate
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
        client = gspread.authorize(creds)
        print("✓ Authentication successful")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return
    
    # 3. List available spreadsheets (to verify access)
    try:
        print("\nListing available spreadsheets...")
        spreadsheets = client.list_spreadsheet_files()
        if spreadsheets:
            print("✓ Access to spreadsheets confirmed")
            for sheet in spreadsheets[:3]:  # Show first 3
                print(f"  - {sheet['name']} (ID: {sheet['id']})")
        else:
            print("No spreadsheets found (this might be normal)")
    except Exception as e:
        print(f"✗ Cannot list spreadsheets: {e}")
    
    # 4. Try to access your specific sheet
    try:
        sheet_url = "https://docs.google.com/spreadsheets/d/1iHuQpPtutue1rHdQ0S7wl13Lm7qy6uiPRnD8Y5N1LoQ/edit?usp=sharing"
        sheet = client.open_by_url(sheet_url)
        print(f"✓ Sheet accessed: {sheet.title}")
        return True
    except gspread.exceptions.SpreadsheetNotFound:
        print("✗ Spreadsheet not found. Please check:")
        print("  1. The sheet URL is correct")
        print("  2. The sheet is shared with the service account email above")
        print("  3. The service account has 'Editor' permissions")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_service_account()