# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Design documents and a balance simulator for **Sumeeper**, a watch-only roguelike auto-battler. There is no game source code here — the deliverables are the GDD, the Excel data sheets, and simulation results used to drive balance decisions.

The user communicates in Thai; documents are written in Thai with English technical terms. Reply in Thai.

## Layout

- `game_document/` — **current source of truth**: `Sumeeper_GDD.md` plus the data sheets (`Sumeeper_Equipment_Sheet.xlsx`, `Sumeeper_Monster_Sheet.xlsx`, and Curse/Meal/Perk sheets).
- `simulate/sumeeper_combat_sim.py` — deterministic combat sim that loads the Equipment and Monster sheets by absolute path (`D:\Sumeeper\game_document\...`) and prints a player-build × monster result matrix. `simulate/README.md` is the Thai-language guide for the balance team (double-click `run_report.bat` workflow); `reference_baseline.json` + `reference/` hold the team's reference values — the report auto-diffs current sheets against them (✱ = outcome flipped), and `make_reference.bat` re-baselines. Balance numbers are now owned by a human tuner; treat our tuned set as the reference/guideline, not something to keep re-tuning unprompted.
- `backup/` — historical versions of documents and sheets. Read-only reference; never edit and never treat as current data.

## Running the sim

```bash
cd D:/Sumeeper/simulate && python sumeeper_combat_sim.py
```

Requires `openpyxl`. Works from any shell — the script forces UTF-8 stdout itself (monster names are non-ASCII). Output: `P`/`M`/`TIMEOUT` per matchup with tick count and remaining HP.

For a visual report, run `python sumeeper_sim_report.py` in the same folder — it re-runs every matchup and writes `sim_report.html` (self-contained; open in any browser): win/loss heatmap with margin coloring, click any cell for that fight's HP/DEF timeline with Special markers, plus a **Sandbox** card where the user picks any 0–3 weapons (ordered) and any monster and the fight runs instantly in the browser. The test loadouts live in `BUILDS` at the bottom of `sumeeper_combat_sim.py`, keyed by monster tier.

⚠️ The Sandbox works via a JS port of the combat engine embedded in the report template (`runFight` inside `sumeeper_sim_report.py`). **Any combat-rule change must be applied to the Python engine AND this JS port**, then verified by regenerating the report — the page can self-check: every heatmap cell re-run through the JS engine must match the Python result exactly (54/54 as of last sync).

## Combat model

The authoritative spec is the GDD sections **Auto battle** and **Damage Calculate**; the sim's module docstring declares which rules it implements plus its extra assumptions. When they disagree, the GDD wins — flag the drift instead of guessing. The summary below (in Thai, shared with the whole design team) is the current agreed understanding:

### ค่าพลังและ loadout

- base stat ตัวเริ่มต้น: **HP 10 / ATK 1 / DEF 0 / SPD 1 / Charge 1 / Max Action Gauge 2** — คงที่ตลอด run (ไม่มีเลเวล) ขยับได้ด้วย Perk; Max HP เพิ่มจาก Recipe เท่านั้น (Equipment เพิ่ม Max HP ได้เฉพาะผ่าน ability เช่น `Gain MAX HP`)
- ผู้เล่นเลือก Equipment **0–3 ชิ้น** จากที่ถือสูงสุด 6 จัดลำดับเป็น Action Sequence ได้เฉพาะช่วง Pre-Combat; ไม่เลือกเลยก็เข้า combat ได้ (ตีด้วย base stat ล้วน)
- **ค่าราย action = base stat + stat ของชิ้นนั้น** ทั้ง ATK/SPD/Charge — บวกกันเสมอ ไม่มีการแทนที่ ดังนั้นค่าจริงในเกม = ค่าในชีต + base และการอัปเกรด base stat ส่งผลกับทุก action
- **DEF เป็น stat เดียวที่รวมจากทั้ง loadout**: หลอด DEF = base DEF + Σ DEF ทุกชิ้นที่เลือกเข้า combat

### จังหวะการต่อสู้ (per-action rotation)

- สมาชิกใน sequence เป็น **active ทีละหนึ่งตำแหน่ง** — Speed Gauge เติมด้วยอัตรา base SPD + SPD ของชิ้น active (+ โบนัส SPD จาก ability) **ขั้นต่ำ 1 เสมอ** (การันตีว่า rotation ไม่มีทางค้าง — เกม watch-only ห้ามมี state ที่ไม่เดินหน้า)
- เมื่อ Speed Gauge เต็ม: ชิ้น active โจมตี 1 ครั้ง → Action Gauge เพิ่ม (base Charge + Charge ชิ้นนั้น) → เลื่อนให้ชิ้นถัดไปเป็น active; **เศษ Speed Gauge ทบไปรอบถัดไป** (ต่างจาก Action Gauge ที่ทิ้งส่วนเกิน)
- **จำนวนชิ้นไม่เพิ่มความถี่โจมตี** — ถือ 3 ชิ้นได้ความหลากหลาย, DEF รวม, burst ใหญ่ ไม่ใช่ตีถี่ขึ้น 3 เท่า; build ชิ้นเดียวหมุนชิ้นเดิมซ้ำทุก action
- ฝั่ง Feast เดินกติกาเดียวกันทีละ action — **SPD ราย action = base SPD (Monsters Config) + SPD ของ entry นั้น (Feast Sequence)** เหมือนผู้เล่น ส่วน ATK/Charge ราย action ใช้ค่า entry ตรงๆ (Config ATK เป็น legacy ไม่ถูกใช้) และหลอด DEF = Config DEF + Σ entry DEF

### การคำนวณความเสียหาย (ต่อการโจมตี 1 ครั้ง)

1. ตั้งต้น = ATK ของ action นั้น
2. หักด้วย **Armor** ของผู้ถูกตี — ตัวลดความเสียหายตัวเดียวในระบบ
3. **Damage Floor 1** — ทุกการโจมตีเข้าอย่างน้อย 1 เสมอ ไม่มีการตีแล้วไม่เกิดผล
4. ความเสียหายกิน **หลอด DEF** ของผู้ถูกตีก่อนแบบ 1:1
5. ส่วนที่เกินหลอดทะลุเข้า HP ทันทีในการตีครั้งเดียวกัน

- หลอด DEF เติมเต็มใหม่ทุกต้น combat (DEF 1 ≈ HP 1 ที่ฟื้นฟรีทุกไฟต์); `Gain DEF` กลาง combat เติมเกินค่าเริ่มต้นได้เป็นเกราะชั่วคราว แต่ไม่ข้าม combat; `Lose DEF` กินหลอดตรงๆ ไม่นับเป็นการโจมตี
- **Thorn** สะท้อนตาม stack เมื่อถูกตี: ไม่โดน Armor หัก ไม่ติด floor แต่กินหลอด DEF ของผู้โจมตีก่อนตามปกติ

### Trigger และ Keyword

- **On-Start** (เริ่ม combat) / **On-Hit** (ผู้ตี ทุก action) / **On-Damaged** (ผู้ถูกตี ทุกครั้งที่โดน) / **On-Half** (ครั้งเดียว เมื่อ HP ตกถึงครึ่ง) / **On-Exposed** (ครั้งเดียว เฉพาะเมื่อ DEF เปลี่ยนจาก >0 เป็น 0 — เริ่ม combat ที่ 0 อยู่แล้วไม่ยิงตลอดไฟต์) / **Special** / Death / Passive
- "Shield" เป็นคำเก่า = **Armor**; **Fury** นิยามไว้ใน GDD แต่ยังไม่มีของชิ้นไหนใช้และ sim ยังไม่รองรับ

### Special

- Action Gauge มี MaxAG ช่อง (คงที่ต่อตัวละคร ขยับด้วย Perk ไม่ผันตาม loadout) — เต็มแล้วใช้ Special ทันที รีเซ็ตเป็น 0 **ทิ้ง Charge ส่วนเกิน**
- Special พื้นฐานของผู้เล่น = **burst โจมตี 1 ครั้ง** ค่า = Σ ATK ราย action ของทุกชิ้นใน loadout (แต่ละชิ้นคิด base + ชิ้น) — โดน Armor หักครั้งเดียว ติด floor 1 กินหลอด DEF ตามปกติ; Primary Perk บางสาย Replaces Special
- Feast ส่วนใหญ่มี Special ของตัวเอง (แปลงจาก ability สายรุกเดิม) ส่วน ability สาย reactive คงเป็น trigger ปกติ

## Sheet structure and balance math

`Sumeeper_Equipment_Sheet.xlsx` tabs: `Equipment` (stats + computed Sum/Ability Value/Combat Power), `Ability` (one row per ability: Trigger/Verb/Target/Magnitude/lane), `Weights` (all tuning knobs), per-rarity pool tabs, `Forge Scaler`.

Combat Power budget system: `CP = Σ(stat × stat-weight) + Charge × charge-weight + Σ(Trigger-w × Verb-w × Magnitude-w × Target-w)` per ability, tuned so CP ≈ the rarity base in `Weights` (Common 6 / Rare 9 / Epic 13 / Legend 17 / Mythic 22). Remember: because per-action values add base stats, the effective in-game value of a sheet stat is sheet value + 1.

`Sumeeper_Monster_Sheet.xlsx` tabs: `Monsters Config` (base HP/ATK/DEF/SPD per monster — DEF/SPD bases are live, HP/ATK are legacy), `Feast` (rollup: hand-set HP and Max AG **values**; its DEF/SPD formula cells sum ALL sequence entries — that is the old entity-sum model, ignored by the sim), `Feast Sequence` (per-action ATK/DEF/SPD/Charge + action-lane abilities), `Feast Combat Ability` (triggered abilities). Per-action SPD = Config base SPD + entry SPD; per-action ATK/Charge = entry values as-is; DEF pool = Config DEF + Σ entry DEF; HP/MaxAG from the Feast tab's value cells.

## Working rules

- The GDD is canonical. When a combat rule changes, update the GDD, the sim logic, **and** the sim's docstring assumptions together in the same pass — they have drifted before (e.g. On-Exposed was never fired by the old sim).
- The sim intentionally does not implement everything: Convert/Eater verbs and Scaling magnitudes are logged in `NOT SIMULATED` notes rather than silently skipped. Keep that pattern when adding mechanics.
- When proposing balance changes, compute the impact against the real sheets (load them with openpyxl) rather than reasoning from the GDD alone.
