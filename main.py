import gspread
import os
import json
import re
from datetime import datetime
from google.oauth2.service_account import Credentials

SHEET_ID = "1roB9ZwjGVmQulJpqeryX8o7QLbbZrpU2d2unKNL3_H0"

def run_sync():
    # 1. Connect
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    key_data = json.loads(os.environ['GCP_JSON'])
    creds = Credentials.from_service_account_info(key_data, scopes=scopes)
    client = gspread.authorize(creds)
    ss = client.open_by_key(SHEET_ID)
    
    # 2. Get Employee Sheets
    all_worksheets = {s.name.upper(): s for s in ss.worksheets()}
    
    # 3. Pull Data from COVER.PAGE
    # Assuming text to parse is in Column A of COVER.PAGE
    input_sheet = ss.worksheet("COVER.PAGE")
    data = input_sheet.get_all_values()
    
    # RegEx Patterns
    r_emp = re.compile(r'^(\d+)[\.\)\-\s]+\s*(.*)')
    r_tv = re.compile(r'\b(\d*)\s*(?:tv|tvs|hot\s*shower|wall\s*mount)\b', re.I)
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"--- Processing Batch for {today_str} ---")

    for row in data:
        if not row: continue
        line = row[0]
        match = r_emp.match(line.strip())
        
        if match:
            raw_name = match.group(2)
            
            # TV Bonus Logic
            tv_m = r_tv.search(raw_name)
            tv_bonus = (int(tv_m.group(1)) if tv_m and tv_m.group(1).isdigit() else 1) * 100 if tv_m else 0
            
            # 100% Strict Matching
            clean_in = re.sub(r'[^A-Z]', '', raw_name.upper())
            matched_name = next((name for name in all_worksheets if re.sub(r'[^A-Z]', '', name) == clean_in), None)

            if matched_name:
                emp_sheet = all_worksheets[matched_name]
                # Logic: Find empty row or specific date row and update
                # This is where Python is 50x faster than Apps Script
                print(f"UPDATING: {matched_name} | Bonus: {tv_bonus}")
                # Example: Update Column B (Earnings) and C (TV)
                # emp_sheet.append_row([today_str, 1000, tv_bonus]) 
            else:
                print(f"SKIPPED: No sheet found for {raw_name}")

if __name__ == "__main__":
    run_sync()
