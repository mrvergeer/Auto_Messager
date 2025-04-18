import pandas as pd
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build


def fetch_and_process_sheet(credentials_path, spreadsheet_id, data_range):
    try:
        # Authenticate with Google Sheets API
        creds = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )

        # Build the Google Sheets service
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        # Fetch data from the specified range
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=data_range).execute()
        data = result.get('values', [])

        if data:
            # Assuming the first row is the header after removing IDs
            set_df = pd.DataFrame(data[1:], columns=data[0])
            return set_df
        else:
            return pd.DataFrame()

    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        return pd.DataFrame()


if __name__ == '__main__':
    # Example usage if you run this file directly
    credentials_file = os.getenv('CREDENTIALS_FILE')
    sheet_id = os.getenv('SPREADSHEET_ID')
    sheet_range = os.getenv('SHEET_RANGE')

    df = fetch_and_process_sheet(credentials_file, sheet_id, sheet_range)
    if not df.empty:
        print("DataFrame loaded successfully:")
        print(df.head())
    else:
        print("Failed to load DataFrame.")
