# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Design documents, data sheets, and a combat balance simulator for **Sumeeper**. There is no game source code here — deliverables are the GDD, the Excel data sheets, and balance/simulation results.

The user communicates in Thai; documents are written in Thai with English technical terms. Reply in Thai.

## What Sumeeper is

A **Minesweeper-style tile-puzzle roguelite** crossed with a deckbuilding auto-battler. The player is a young chef exploring an ingredient-filled dungeon: she opens grid tiles Minesweeper-style (analyzing clues, weighing risk per tile), and the things she uncovers — enemies ("**Feast**", food-themed monsters), ingredients, weapons, curses, perks — shape her build for that run. The objective of a run is to defeat the dungeon's final boss.

Key systems to know before touching anything:

- **Combat is watch-only auto-battle.** All decisions happen in Pre-Combat (choosing 0–3 equipment as an ordered Action Sequence); the fight then resolves automatically. No mid-combat input, so combat must never stall.
- **No leveling.** Player power comes only from Equipment, Perks, and Recipes (Max HP). Character base stats are fixed per run (starter: HP 10 / ATK 1 / DEF 0 / SPD 1 / Charge 1 / Max Action Gauge 2) and modified only by Perks.
- **Curse Gauge** replaces XP: earned by killing Feast, and at thresholds the player must pick 1 of 2 **Curses**. Accepted curses scale Feast up in real time (ATK/HP % per curse, +1 sequence action per 2 curses) — risk-vs-reward pacing knob.
- **Cooking**: ingredients found in the dungeon combine into **Meals** (buffs/effects; Recipes are the only Max HP source).
- **Encounters** on the grid: Combat, Shop, Forge (upgrade/merge equipment rarity), Perk, Item, Hint.
- **Run structure**: floors with themed variants (Myceland, Sugar Garden, Abyssalt, Capsaicia, Umamia, Edemia), currencies (Coin, Fath, Special Ingredients from bosses), Quests, and The Curse Contract.

## Data map — where to find what

| Topic | Source of truth |
| --- | --- |
| All game rules & systems (canonical) | `game_document/Sumeeper_GDD.md` — sections: Core Mechanics (Grid, Stat) · Encounter (Combat/Shop/Forge/Perk/Item/Hint) · Combat + Auto battle + Damage Calculate · Feature (Feast, Feast Sequence, Ability, Trigger/Keyword) · Curse Gauge · Cook · Equipment (Tier, Set) · Perk · Curse · Core gameloop (Run, Currency, Quest, Reward, Curse Contract) · Character · Floor Variant |
| UI/UX per screen — สิ่งที่ต้องแสดง + สิ่งที่กดได้ (ไม่ใช่ rule) | `game_document/Sumeeper_UX_Screens.md` — ตอนนี้ครอบคลุมกลุ่มหน้า Result; ถ้าขัดกับ GDD ให้ยึด GDD |
| Weapon stats, abilities, tuning weights, CP budget, rarity pools, forge scaling | `game_document/Sumeeper_Equipment_Sheet.xlsx` |
| Feast (monster) stats & action sequences & abilities | `game_document/Sumeeper_Monster_Sheet.xlsx` |
| Curses | `game_document/Sumeeper_Curse_Sheet.xlsx` |
| Meals / cooking | `game_document/Sumeeper_Meal_Sheet.xlsx` |
| Perks | `game_document/Sumeeper_Perk_Sheet.xlsx` |
| Old versions of everything | `backup/` — **read-only history**; never edit, never treat as current |

The GDD is canonical. When it disagrees with a sheet or the sim, flag the drift instead of guessing.

## Combat balance work → `simulate/`

`simulate/` holds the deterministic combat simulator and its interactive HTML report (heatmap, Combat Viewer, sandbox, reference-diff). **It exists specifically for combat/balance design work** — agents doing other tasks normally don't need it.

If your task IS combat balance or sim work: **start by reading `simulate/README.md`** (Thai guide: workflow, report anatomy, the combat-model summary, sheet/CP math, and the critical rule that the Python engine and the JS engine embedded in the report must stay in sync with the GDD and each other).

Two rules that apply even outside balance work:

- Any combat-rule change in the GDD must be mirrored in the sim engines in the same pass (see `simulate/README.md`).
- Balance numbers are owned by a human tuner. The team's tuned set is stored as a reference baseline (`simulate/reference_baseline.json` + `simulate/reference/`) — treat it as a guideline for comparison, not something to re-tune unprompted.
