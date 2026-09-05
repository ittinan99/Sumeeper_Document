"""Thin helper around the Sumeeper GameData Google Sheet (same service account Unity uses).

Usage:
  python simulate/tools/gsheet.py info                 # title + tabs (name, gid, size)
  python simulate/tools/gsheet.py read <Tab>           # dump a tab as TSV
  python simulate/tools/gsheet.py dump <out.xlsx>      # every tab -> xlsx snapshot
"""
import os, sys, json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SPREADSHEET_ID = "1Tni3eLd67CDvaygLQ_1RrWSSNK01EgXz_eUB6wDZHqQ"
KEY_CANDIDATES = [
    os.environ.get("SUMEEPER_SA_KEY", ""),
    os.path.join(os.path.dirname(__file__), "..", "..", "sumeeper-4ad3bba50861.json"),
    r"D:\git_project\Minesweeper\Secrets\sumeeper-4ad3bba50861.json",
]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def key_path():
    for p in KEY_CANDIDATES:
        if p and os.path.exists(p):
            return p
    sys.exit("service account key not found; set SUMEEPER_SA_KEY")

def service():
    creds = service_account.Credentials.from_service_account_file(key_path(), scopes=SCOPES)
    return build("sheets", "v4", credentials=creds, cache_discovery=False)

def info(svc):
    meta = svc.spreadsheets().get(spreadsheetId=SPREADSHEET_ID,
                                  fields="properties.title,sheets.properties").execute()
    print("title:", meta["properties"]["title"])
    for s in meta["sheets"]:
        p = s["properties"]; g = p.get("gridProperties", {})
        print(f"  gid={p['sheetId']:<12} idx={p['index']:<3} {p['title']:<18} rows={g.get('rowCount')} cols={g.get('columnCount')}")

def read(svc, tab):
    r = svc.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=f"'{tab}'",
                                        valueRenderOption="UNFORMATTED_VALUE").execute()
    return r.get("values", [])

def write(svc, tab, values, raw=False):
    """Overwrite from A1 (does not clear rows beyond the data)."""
    return svc.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=f"'{tab}'!A1",
        valueInputOption="RAW" if raw else "USER_ENTERED",
        body={"majorDimension": "ROWS", "values": values}).execute()

if __name__ == "__main__":
    svc = service()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "info"
    if cmd == "info":
        info(svc)
    elif cmd == "read":
        for row in read(svc, sys.argv[2]):
            print("\t".join(str(c).replace("\n", " ") for c in row))
    elif cmd == "dump":
        import openpyxl
        wb = openpyxl.Workbook(); wb.remove(wb.active)
        meta = svc.spreadsheets().get(spreadsheetId=SPREADSHEET_ID, fields="sheets.properties.title").execute()
        for s in meta["sheets"]:
            t = s["properties"]["title"]; ws = wb.create_sheet(t)
            for row in read(svc, t): ws.append(row)
        wb.save(sys.argv[2]); print("saved", sys.argv[2])
