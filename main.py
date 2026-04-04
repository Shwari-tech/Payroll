import gspread
import os
import json
import re
from google.oauth2.service_account import Credentials

# CONFIGURATION
SHEET_ID = "1roB9ZwjGVmQulJpqeryX8o7QLbbZrpU2d2unKNL3_H0"

def run_sync():
    # 1. AUTHENTICATION
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        key_data = json.loads(os.environ['GCP_JSON'])
        creds = Credentials.from_service_account_info(key_data, scopes=scopes)
        client = gspread.authorize(creds)
    except Exception as e:
        print(f"AUTH ERROR: {e}")
        return

    ss = client.open_by_key(SHEET_ID)
    all_sheets = [s.name for s in ss.worksheets()]
    
    # 2. LOGIC PATTERNS
    r_emp = re.compile(r'^(\d+)[\.\)\-\s]+\s*(.*)')
    r_tv = re.compile(r'\b(\d*)\s*(?:tv|tvs|hot\s*shower|wall\s*mount)\b', re.I)
    
    # 3. PULL DATA FROM COVER PAGE
    try:
        input_sheet = ss.worksheet("COVER.PAGE")
        rows = input_sheet.get_all_values() 
    except Exception as e:
        print(f"SHEET ERROR: Could not find COVER.PAGE - {e}")
        return

    print("--- SHWARI HIGH-SPEED SYNC ACTIVE ---")
    
    for row in rows:
        if not row or not row[0]: continue
        line = row[0]
        match = r_emp.match(line.strip())
        
        if match:
            raw_name = match.group(2)
            
            # TV Bonus Logic (+100 per unit)
            tv_m = r_tv.search(raw_name)
            tv_count = 1
            if tv_m and tv_m.group(1) and tv_m.group(1).isdigit():
                tv_count = int(tv_m.group(1))
            tv_bonus = (tv_count * 100) if tv_m else 0
            
            # 100% Strict Name Matching
            clean_input = re.sub(r'[^A-Z]', '', raw_name.upper())
            matched_sheet_name = None
            
            for s_name in all_sheets:
                clean_s = re.sub(r'[^A-Z]', '', s_name.upper())
                if clean_s == clean_input:
                    matched_sheet_name = s_name
                    break
            
            if matched_sheet_name:
                print(f"SUCCESS: {matched_sheet_name} | TV Bonus: KES {tv_bonus}")
                # Future: Add spreadsheet update command here
            else:
                print(f"STRICT MATCH FAILED: {raw_name} (No exact sheet found)")

if __name__ == "__main__":
    run_sync()
