import os
import base64
import re
import csv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def fetch_airnoise_reports(service):
    query = 'from:no-reply@airnoise.io newer_than:7d'
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No new Airnoise emails found.")
        return

    all_flights = []
    print(f"Found {len(messages)} emails. Extracting flight data...")

    for msg in messages:
        txt = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        
        # We are now just extracting all text/plain parts
        body_text = ""
        if 'parts' in txt['payload']:
            for part in txt['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    body_text += base64.urlsafe_b64decode(data).decode('utf-8')
                elif part['mimeType'] == 'multipart/alternative':
                    for subpart in part['parts']:
                        if subpart['mimeType'] == 'text/plain':
                            data = subpart['body'].get('data', '')
                            body_text += base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            data = txt['payload']['body'].get('data', '')
            body_text = base64.urlsafe_b64decode(data).decode('utf-8')

        if body_text:
            # Look for the raw HTML tags INSIDE the plain text
            rows = re.findall(r'<tr>(.*?)</tr>', body_text, re.DOTALL)
            
            for row in rows:
                cols = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                
                if len(cols) >= 8:
                    # Clean up any HTML tags inside the cell and strip whitespace
                    clean_cols = [re.sub(r'<[^>]+>', '', c).strip() for c in cols]
                    all_flights.append(clean_cols)

    if all_flights:
        output_file = 'airnoise_flights.csv'
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Time', 'Complaint Type', 'Airport', 'Operation', 'Aircraft', 'Operator', 'Callsign', 'Distance (mi)', 'Altitude'])
            writer.writerows(all_flights)
            
        print(f"\nSuccess! Extracted {len(all_flights)} individual flight events.")
        print(f"Data saved to '{output_file}'")
        
        # Show a preview
        print("\n--- PREVIEW OF FIRST 3 ROWS ---")
        for r in all_flights[:3]:
            print(r)
    else:
        print("\nStill couldn't find the flight rows. The email format might be different.")

if __name__ == '__main__':
    print("Authenticating with Gmail...")
    gmail_service = get_gmail_service()
    fetch_airnoise_reports(gmail_service)