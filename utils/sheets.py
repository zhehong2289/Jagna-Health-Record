# utils/sheets.py
import gspread
from google.oauth2.service_account import Credentials
import traceback

def init_google_sheets(credentials_file='credentials.json'):
    """
    Initialize Google Sheets client
    """
    try:
        print(f"Attempting to load credentials from: {credentials_file}")
        
        # Updated scope - use these specific scopes
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file'
        ]
        
        # Load credentials
        creds = Credentials.from_service_account_file(credentials_file, scopes=scope)
        client = gspread.authorize(creds)
        print("✓ Google Sheets client initialized successfully")
        return client
    except Exception as e:
        print(f"✗ Error initializing Google Sheets: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        return None

def write_to_sheet(client, sheet_url, data, worksheet_name="Health Records"):
    """
    Write data to Google Sheet
    Groups entries by name by inserting new entries after the last occurrence of the same name

    Returns:
        (success: bool, message: str)
    """
    try:
        print(f"Attempting to write to sheet: {sheet_url}")
        print(f"Data: {data}")

        # Open the spreadsheet
        sheet = client.open_by_url(sheet_url)
        print(f"✓ Opened sheet: {sheet.title}")

        # Try to find worksheet by name in a safe, non-exception path
        worksheets = sheet.worksheets()
        worksheet = None
        for w in worksheets:
            try:
                if w.title.strip().lower() == worksheet_name.strip().lower():
                    worksheet = w
                    break
            except Exception:
                # Defensive: skip any problematic worksheet objects
                continue

        if worksheet:
            print(f"✓ Using worksheet: {worksheet.title}")
        else:
            print(f"Worksheet '{worksheet_name}' not found. Attempting to create it.")
            try:
                worksheet = sheet.add_worksheet(title=worksheet_name, rows=1000, cols=max(10, len(data)))
                print(f"✓ Created worksheet: {worksheet.title}")
            except gspread.exceptions.APIError as e:
                # Likely a permission error (service account cannot edit/modify sheets)
                msg = f"Permission/API error creating worksheet '{worksheet_name}': {e}"
                print(f"✗ {msg}")
                if worksheets:
                    worksheet = worksheets[0]
                    print(f"✓ Falling back to worksheet: {worksheet.title}")
                else:
                    return False, msg
            except Exception as e:
                msg = f"Failed to create worksheet '{worksheet_name}': {e}"
                print(f"✗ {msg}")
                if worksheets:
                    worksheet = worksheets[0]
                    print(f"✓ Falling back to worksheet: {worksheet.title}")
                else:
                    return False, msg

        # Get all values from the worksheet
        all_values = worksheet.get_all_values()

        # Compute target row: next blank row after current data
        target_row = len(all_values) + 1

        # Ensure we always write into columns A..F
        # Pad or trim data to exactly 6 columns (A-F)
        desired_cols = 6
        padded = list(data[:desired_cols]) + [""] * max(0, desired_cols - len(data))

        try:
            range_a1 = f"A{target_row}:F{target_row}"
            worksheet.update(range_a1, [padded], value_input_option='USER_ENTERED')
            msg = f"Wrote row at {range_a1} in worksheet '{worksheet.title}'"
            print(f"✓ {msg}")
            return True, msg
        except Exception as e:
            msg = f"Failed to write to worksheet '{worksheet.title}' at row {target_row}: {e}"
            print(f"✗ {msg}")
            return False, msg

    except gspread.exceptions.APIError as e:
        msg = f"Google API Error: {e}"
        print(f"✗ {msg}")
        if hasattr(e, 'response'):
            print(f"Response text: {e.response.text}")
            msg = msg + f" Response: {e.response.text}"
        return False, msg
    except gspread.exceptions.SpreadsheetNotFound:
        msg = "Spreadsheet not found. Check URL and sharing."
        print(f"✗ {msg}")
        return False, msg
    except Exception as e:
        msg = f"Unexpected error: {e}"
        print(f"✗ {msg}")
        print(f"Full traceback: {traceback.format_exc()}")
        return False, msg