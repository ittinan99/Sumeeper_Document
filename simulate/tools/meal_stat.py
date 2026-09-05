"""Build MealStat rows from per-ingredient weights (additive model) and diff/write them to the sheet.

  python simulate/tools/meal_stat.py                 # dry-run: show proposed vs live
  python simulate/tools/meal_stat.py --write         # write to Google Sheet tab MealStat
  python simulate/tools/meal_stat.py --meat 3,1,0 --veg 1,2,0 --salt 0,0,2   # weights = HP,STA,MaxHP
"""
import sys, os, argparse
sys.path.insert(0, os.path.dirname(__file__))
import gsheet

# material-01 = meat (m), material-02 = cabbage/veg (v), material-03 = salt (s)
MAT = {"m": "material-01", "v": "material-02", "s": "material-03"}

def parse(w):
    hp, sta, mx = (int(x) for x in w.split(","))
    return {"HP": hp, "STA": sta, "MaxHP": mx}

def build(weights, recipes):
    rows = []
    for meal_id, mats in recipes:
        tot = {"HP": 0, "STA": 0, "MaxHP": 0}
        for code in mats:
            for k in tot: tot[k] += weights[code][k]
        rows.append([meal_id, tot["HP"], tot["MaxHP"], tot["STA"]])
    return rows

def live_recipes(svc):
    import json
    inv = {v: k for k, v in MAT.items()}
    out = []
    for r in gsheet.read(svc, "MealRecipe")[1:]:
        if len(r) < 3 or not r[0]: continue
        out.append((r[2], "".join(inv[m] for m in json.loads(r[1]))))
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--meat", default="3,1,0"); ap.add_argument("--veg", default="1,2,0"); ap.add_argument("--salt", default="0,0,2")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    weights = {"m": parse(a.meat), "v": parse(a.veg), "s": parse(a.salt)}

    svc = gsheet.service()
    recipes = live_recipes(svc)
    live = gsheet.read(svc, "MealStat")
    header = live[0]
    live_by_id = {r[0]: r for r in live[1:] if r}
    proposed = build(weights, recipes)

    print(f"weights HP,STA,MaxHP  meat={a.meat} veg={a.veg} salt={a.salt}")
    print(f"{'id':<9}{'code':<6}{'live HP/Max/STA':<18}{'new HP/Max/STA':<16}")
    changed = 0
    for (mid, code), row in zip(recipes, proposed):
        old = live_by_id.get(mid, [mid, "", "", ""])
        o = f"{old[1]}/{old[2]}/{old[3]}"; n = f"{row[1]}/{row[2]}/{row[3]}"
        mark = "" if o == n else "  <-"
        changed += o != n
        print(f"{mid:<9}{code:<6}{o:<18}{n:<16}{mark}")
    print(f"{changed} of {len(proposed)} rows change")

    if a.write:
        # keep header + BuffId column (col 5) untouched
        values = [header] + [row + [live_by_id.get(row[0], ["", "", "", "", ""])[4] if len(live_by_id.get(row[0], [])) > 4 else ""] for row in proposed]
        res = gsheet.write(svc, "MealStat", values)
        print("written:", res.get("updatedRange"), res.get("updatedCells"), "cells")
