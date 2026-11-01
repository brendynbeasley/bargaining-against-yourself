"""Download the two public inputs and save small, committed copies in data/raw/.

Run from the repository root:

    python src/fetch_data.py

What it fetches:
  1. Cornell ILR / Illinois LER Labor Action Tracker, every event it lists
     (https://striketracker.ilr.cornell.edu/labor_actions.json). Only the strike rows and the
     columns the analysis needs are kept, in data/raw/labor_action_tracker_strikes.csv.
  2. FRED series BAA, Moody's seasoned Baa corporate bond yield, monthly, percent
     (fredgraph.csv, no key). Saved to data/raw/fred_baa.csv.

Both files are small and committed. The analysis scripts read only the committed CSVs,
so this script is needed only to refresh them.
Each file is written to a temporary name first and then renamed.
"""
import json
from datetime import date
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
UA = {"User-Agent": "Brendyn Beasley research 83249437+brendynbeasley@users.noreply.github.com"}

TRACKER_URL = "https://striketracker.ilr.cornell.edu/labor_actions.json"
FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAA"


def write_atomic(df, path):
    tmp = path.with_suffix(".tmp")
    df.to_csv(tmp, index=False)
    tmp.replace(path)


def fetch_tracker():
    r = requests.get(TRACKER_URL, headers=UA, timeout=120)
    r.raise_for_status()
    raw = json.loads(r.text)
    events = list(raw.values()) if isinstance(raw, dict) else raw
    print(f"Labor Action Tracker: {len(events)} events downloaded")
    rows = []
    for e in events:
        if e.get("Action_type") != "Strike":
            continue
        locs = e.get("locations") or []
        states = sorted({loc.get("State") for loc in locs if loc.get("State")})
        rows.append({
            "id": e.get("id"),
            "employer": (e.get("Employer") or "").strip(),
            "labor_organization": (e.get("Labor_Organization") or "").strip(),
            "start_date": e.get("Start_date"),
            "end_date": e.get("End_date"),
            "duration_days": e.get("Duration"),
            "participants": e.get("Approximate_Number_of_Participants"),
            "bargaining_unit_size": e.get("Bargaining_Unit_Size"),
            "authorized": e.get("Authorized") or "",
            "industry": "; ".join(e.get("Industry") or []),
            "demands": "; ".join(e.get("Worker_demands") or []),
            "states": "; ".join(states),
            "n_locations": len(locs),
        })
    df = pd.DataFrame(rows).sort_values(["start_date", "id"])
    print(f"  kept {len(df)} strikes, dropped {len(events) - len(df)} protests and untyped events")
    write_atomic(df, RAW / "labor_action_tracker_strikes.csv")


def fetch_fred():
    r = requests.get(FRED_URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = RAW / "fred_baa.tmp"
    tmp.write_text(r.text)
    df = pd.read_csv(tmp)
    print(f"FRED BAA: {len(df)} monthly rows, {df.iloc[0, 0]} to {df.iloc[-1, 0]}")
    tmp.replace(RAW / "fred_baa.csv")


if __name__ == "__main__":
    RAW.mkdir(parents=True, exist_ok=True)
    fetch_tracker()
    fetch_fred()
    (RAW / "DOWNLOADED.txt").write_text(
        f"Downloaded {date.today().isoformat()} by src/fetch_data.py\n"
        f"labor_action_tracker_strikes.csv  {TRACKER_URL}\n"
        f"fred_baa.csv                      {FRED_URL}\n")
    print("done")
