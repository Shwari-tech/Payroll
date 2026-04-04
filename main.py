import gspread, os, json, re
from google.oauth2.service_account import Credentials

SHEET_ID = "1roB9ZwjGVmQulJpqeryX8o7QLbbZrpU2d2unKNL3_H0"

def run_sync():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    key_data = json.loads(os.environ['GCP_JSON'])
    creds = Credentials.from_service_account_info(key_data, scopes=scopes)
    client = gspread.authorize(creds)
    ss = client.open_by_key(SHEET_ID)
    
    all_sheets = {s.name.upper(): s for s in ss.worksheets()}
    input_sheet = ss.worksheet("COVER.PAGE")
    data = input_sheet.get_all_values()
    
    r_emp = re.compile(r'^(\d+)[\.\)\-\s]+\s*(.*)')
    r_tv = re.compile(r'\b(\d*)\s*(?:tv|tvs|hot\s*shower)\b', re.I)

    print("--- Processing High Speed Batch ---")
    for row in data:
        if not row: continue
        match = r_emp.match(row[0].strip())
        if match:
            raw_name = match.group(2)
            tv_m = r_tv.search(raw_name)
            tv_bonus = (int(tv_m.group(1)) if tv_m and tv_m.group(1).isdigit() else 1) * 100 if tv_m else 0
            
            clean_in = re.sub(r'[^A-Z]', '', raw_name.upper())
            matched = next((name for name in all_sheets if re.sub(r'[^A-Z]', '', name) == clean_in), None)

            if matched:
                print(f"SUCCESS: {matched} | Bonus: {tv_bonus}")
            else:
                print(f"FAILED: {raw_name}")

if __name__ == "__main__":
    run_sync()
