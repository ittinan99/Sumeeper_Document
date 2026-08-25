# -*- coding: utf-8 -*-
"""เก็บ snapshot ค่าปัจจุบันเป็น "ค่าอ้างอิง" (reference baseline)

รันเมื่อไหร่: ตอนที่ค่าชุดปัจจุบันคือชุดที่อยากใช้เป็นฐานเปรียบเทียบ
ผลลัพธ์:
  - reference_baseline.json   (stat + ผลแพ้ชนะทุกคู่ — sim_report ใช้เทียบอัตโนมัติ)
  - reference/Sumeeper_Equipment_Sheet_ref.xlsx และ Monster_ref.xlsx (สำเนาชีตเต็ม)

วิธีรัน:  python make_reference.py   หรือดับเบิลคลิก make_reference.bat
"""
import json
import os
import shutil
import sys
from datetime import datetime

import sumeeper_combat_sim as S

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))

results = {}
for mk in S.order:
    m = S.monsters[mk]
    results[mk] = {}
    for bname, names in S.BUILDS[m["tier"]].items():
        r = S.fight(names, mk)
        results[mk][bname] = dict(win=r["win"], ticks=r["ticks"], php=r["php"], mhp=r["mhp"])

ref = dict(
    generated=datetime.now().strftime("%Y-%m-%d %H:%M"),
    note="ค่าอ้างอิงจากรอบ balance โดยทีม (sim) — ใช้เทียบกับค่าที่จูนใหม่",
    monsters={k: dict(name=m["name"], tier=m["tier"], hp=m["hp"], dfs=m["dfs"], base_spd=m["base_spd"],
                      seq=[dict(atk=e["atk"], spd=e["spd"], chg=e["chg"]) for e in m["seq"]])
              for k, m in S.monsters.items()},
    weapons={n: dict(rar=w["rar"], atk=w["atk"], dfs=w["dfs"], spd=w["spd"], chg=w["chg"])
             for n, w in S.weapons.items() if not n.startswith("__")},
    results=results,
)

out = os.path.join(HERE, "reference_baseline.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(ref, f, ensure_ascii=False, indent=1)

os.makedirs(os.path.join(HERE, "reference"), exist_ok=True)
shutil.copy(r"D:\Sumeeper\game_document\Sumeeper_Equipment_Sheet.xlsx",
            os.path.join(HERE, "reference", "Sumeeper_Equipment_Sheet_ref.xlsx"))
shutil.copy(r"D:\Sumeeper\game_document\Sumeeper_Monster_Sheet.xlsx",
            os.path.join(HERE, "reference", "Sumeeper_Monster_Sheet_ref.xlsx"))

print(f"บันทึกค่าอ้างอิงแล้ว: {out}")
print("สำเนาชีตอยู่ในโฟลเดอร์ reference/ — รายงานรอบต่อไปจะเทียบกับชุดนี้อัตโนมัติ")
