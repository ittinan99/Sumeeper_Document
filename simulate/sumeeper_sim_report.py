# -*- coding: utf-8 -*-
"""Generate sim_report.html — visual report of the combat sim.

Usage:  python sumeeper_sim_report.py   (then open sim_report.html in a browser)

Heatmap of every matchup (diverging color = win margin), click a cell to see
that fight's HP/DEF timeline with Special markers. Self-contained HTML, no CDN.
"""
import json
import os
import sys
from datetime import datetime

import sumeeper_combat_sim as S

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))

BUILD_NAMES = ["Heavy-1", "Rush-3", "Bal-2"]

rows, notes = [], set()
for mk in S.order:
    m = S.monsters[mk]
    cells = []
    for bname in BUILD_NAMES:
        weapons = S.BUILDS[m["tier"]][bname]
        r = S.fight(weapons, mk)
        notes |= r["notes"]
        if r["win"] == "P":
            margin = max(0.0, r["php"]) / r["pmaxhp"]
        elif r["win"] == "M":
            margin = -max(0.0, r["mhp"]) / r["mmaxhp"]
        else:
            margin = 0.0
        cells.append(dict(build=bname, weapons=weapons, mname=m["name"], win=r["win"], ticks=r["ticks"],
                          php=r["php"], mhp=r["mhp"], pmaxhp=r["pmaxhp"], mmaxhp=r["mmaxhp"],
                          psp=r["psp"], msp=r["msp"], margin=round(margin, 3),
                          history=[[t, round(a, 1), round(b, 1), round(c, 1), round(d, 1)]
                                   for t, a, b, c, d in r["history"]],
                          events=r["events"]))
    rows.append(dict(monster=m["name"], tier=m["tier"], cells=cells))

data = dict(builds=BUILD_NAMES, rows=rows, notes=sorted(notes),
            sim=dict(player=S.PLAYER, gaugeMax=S.GAUGE_MAX, tickLimit=S.TICK_LIMIT,
                     weapons=S.weapons, monsters={k: S.monsters[k] for k in S.order},
                     morder=S.order))

# ---- เวลาและที่มาของข้อมูล (โชว์หัวรายงาน กันงงว่าดูข้อมูลชุดไหนอยู่) ----
mtime = lambda p: datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M")
data["meta"] = dict(
    generated=datetime.now().strftime("%Y-%m-%d %H:%M"),
    eq_mtime=mtime(r"D:\Sumeeper\game_document\Sumeeper_Equipment_Sheet.xlsx"),
    mon_mtime=mtime(r"D:\Sumeeper\game_document\Sumeeper_Monster_Sheet.xlsx"))

# ---- เทียบกับค่าอ้างอิง (reference_baseline.json ถ้ามี) ----
data["ref"] = None
refpath = os.path.join(HERE, "reference_baseline.json")
if os.path.exists(refpath):
    with open(refpath, encoding="utf-8") as f:
        rj = json.load(f)
    STAT_M = (("hp", "HP"), ("dfs", "DEF"), ("base_spd", "base SPD"))
    STAT_E = (("atk", "ATK"), ("spd", "SPD"), ("chg", "Chg"))
    STAT_W = (("atk", "ATK"), ("dfs", "DEF"), ("spd", "SPD"), ("chg", "Chg"))
    mdiffs, wdiffs = [], []
    for k, rm in rj["monsters"].items():
        m = S.monsters.get(k)
        if not m:
            mdiffs.append(f"{rm['name']}: หายไปจากชีต"); continue
        ch = [f"{lbl} {rm[f]:g}→{m[f]:g}" for f, lbl in STAT_M if m[f] != rm[f]]
        if len(m["seq"]) != len(rm["seq"]):
            ch.append(f"จำนวน action {len(rm['seq'])}→{len(m['seq'])}")
        else:
            for i, (e, re_) in enumerate(zip(m["seq"], rm["seq"])):
                ch += [f"A{i+1} {lbl} {re_[f]:g}→{e[f]:g}" for f, lbl in STAT_E if e[f] != re_[f]]
        if ch:
            mdiffs.append(f"{rm['name']}: " + ", ".join(ch))
    mdiffs += [f"{S.monsters[k]['name']}: ตัวใหม่ (ไม่มีใน ref)" for k in S.monsters if k not in rj["monsters"]]
    for n, rw in rj["weapons"].items():
        w = S.weapons.get(n)
        if not w:
            wdiffs.append(f"{n}: หายไปจากชีต"); continue
        ch = [f"{lbl} {rw[f]:g}→{w[f]:g}" for f, lbl in STAT_W if w[f] != rw[f]]
        if ch:
            wdiffs.append(f"{n}: " + ", ".join(ch))
    wdiffs += [f"{n}: ชิ้นใหม่ (ไม่มีใน ref)" for n in S.weapons if n not in rj["weapons"]]
    data["ref"] = dict(generated=rj["generated"], note=rj.get("note", ""),
                       results=rj["results"], mdiffs=mdiffs, wdiffs=wdiffs)

TEMPLATE = r"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sumeeper Sim Report</title>
<style>
  :root {
    color-scheme: light;
    --page:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#898781;
    --grid:#e1e0d9; --axis:#c3c2b7; --ring:rgba(11,11,11,.10);
    --p-hp:#2a78d6; --p-def:#86b6ef; --m-hp:#eb6834; --m-def:#f2ab85;
    --div-mid:#f0efec;
  }
  @media (prefers-color-scheme: dark) {
    :root:where(:not([data-theme="light"])) {
      color-scheme: dark;
      --page:#0d0d0d; --surface:#1a1a19; --ink:#ffffff; --ink2:#c3c2b7; --muted:#898781;
      --grid:#2c2c2a; --axis:#383835; --ring:rgba(255,255,255,.10);
      --p-hp:#3987e5; --p-def:#5f8fc4; --m-hp:#d95926; --m-def:#b57c5e;
      --div-mid:#383835;
    }
  }
  * { box-sizing:border-box; margin:0; }
  body { background:var(--page); color:var(--ink);
         font-family:system-ui,-apple-system,"Segoe UI",sans-serif; padding:24px; }
  h1 { font-size:20px; } h2 { font-size:15px; margin-bottom:10px; }
  .sub { color:var(--ink2); font-size:13px; margin-top:4px; }
  .card { background:var(--surface); border:1px solid var(--ring); border-radius:10px;
          padding:16px 18px; margin-top:16px; }
  .tiles { display:flex; gap:12px; margin-top:16px; flex-wrap:wrap; }
  .tile { background:var(--surface); border:1px solid var(--ring); border-radius:10px;
          padding:10px 16px; min-width:120px; }
  .tile .v { font-size:24px; font-weight:600; } .tile .k { font-size:12px; color:var(--ink2); }
  table.hm { border-collapse:separate; border-spacing:2px; width:100%; }
  table.hm th { font-size:12px; color:var(--ink2); font-weight:500; padding:4px 6px; text-align:left; }
  table.hm th.bh { text-align:center; }
  table.hm td.tier { font-size:11px; color:var(--muted); padding-top:10px; letter-spacing:.4px; }
  td.cell { border-radius:4px; text-align:center; font-size:12px; padding:7px 4px;
            cursor:pointer; min-width:86px; font-variant-numeric:tabular-nums; }
  td.cell.sel { outline:2px solid var(--ink); outline-offset:1px; }
  .legend { display:flex; gap:16px; align-items:center; flex-wrap:wrap;
            font-size:12px; color:var(--ink2); margin-top:10px; }
  .chip { display:inline-block; width:12px; height:12px; border-radius:3px; vertical-align:-2px; }
  .lg-line { display:inline-block; width:22px; height:0; vertical-align:3px; border-top:2px solid; }
  .lg-dash { border-top-style:dashed; }
  #tip { position:fixed; pointer-events:none; background:var(--surface); color:var(--ink);
         border:1px solid var(--ring); box-shadow:0 2px 10px rgba(0,0,0,.18);
         border-radius:8px; padding:8px 10px; font-size:12px; display:none; z-index:9;
         font-variant-numeric:tabular-nums; }
  svg text { fill:var(--muted); font-size:11px; font-family:inherit; }
  details { margin-top:16px; } summary { cursor:pointer; color:var(--ink2); font-size:13px; }
  table.flat { border-collapse:collapse; margin-top:10px; font-size:12px; width:100%;
               font-variant-numeric:tabular-nums; }
  table.flat th, table.flat td { border-bottom:1px solid var(--grid); padding:4px 8px; text-align:left; }
  table.flat th { color:var(--ink2); font-weight:500; }
  .note { font-size:12px; color:var(--muted); margin-top:8px; }
  .rgroup { margin-top:8px; }
  .rname { font-size:11px; color:var(--muted); letter-spacing:.4px; margin-bottom:2px; }
  .wchip { display:inline-block; border:1px solid var(--ring); border-radius:6px;
           padding:3px 9px; margin:2px 3px 2px 0; cursor:pointer; font-size:12px;
           background:var(--page); color:var(--ink); user-select:none; }
  .wchip:hover { border-color:var(--muted); }
  .wchip.inseq { border-color:var(--p-hp); box-shadow:inset 0 0 0 1px var(--p-hp); }
  .sqchip { display:inline-block; border-radius:6px; padding:3px 9px; margin:0 4px 0 0;
            cursor:pointer; font-size:12px; background:var(--p-hp); color:#fff; user-select:none; }
  .sbrow { margin-top:12px; font-size:13px; display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
  .sbrow select { font:inherit; padding:3px 6px; background:var(--page); color:var(--ink);
                  border:1px solid var(--ring); border-radius:6px; max-width:260px; }
  .sbrow button { font:inherit; font-size:12px; padding:3px 10px; border-radius:6px;
                  border:1px solid var(--ring); background:var(--page); color:var(--ink2); cursor:pointer; }
  .slot { position:relative; }
  .slot .num { font-size:11px; color:var(--muted); margin-right:4px; }
  .slotbtn { font:inherit; font-size:13px; padding:5px 12px; border-radius:8px; min-width:170px;
             text-align:left; border:1px solid var(--ring); background:var(--page);
             color:var(--ink); cursor:pointer; }
  .slotbtn.empty { color:var(--muted); }
  .slotbtn:hover { border-color:var(--muted); }
  .dd { position:absolute; z-index:20; top:calc(100% + 4px); left:0; width:290px;
        background:var(--surface); border:1px solid var(--ring); border-radius:10px;
        box-shadow:0 8px 24px rgba(0,0,0,.25); padding:8px; }
  .dd input { width:100%; box-sizing:border-box; font:inherit; font-size:13px; padding:6px 10px;
              border:1px solid var(--ring); border-radius:7px; background:var(--page);
              color:var(--ink); margin-bottom:6px; }
  .ddlist { max-height:300px; overflow-y:auto; }
  .ddgroup { font-size:10px; color:var(--muted); letter-spacing:.5px; padding:6px 6px 2px; }
  .opt { display:flex; align-items:center; gap:7px; padding:5px 8px; border-radius:6px;
         cursor:pointer; font-size:13px; }
  .opt:hover { background:var(--page); }
  .opt.cur { outline:1px solid var(--p-hp); }
  .opt small { color:var(--muted); font-size:10px; margin-left:auto; white-space:nowrap; }
  /* ---- combat viewer (game-scene look; deliberately dark in both themes) ---- */
  #scene { position:relative; border-radius:12px; overflow:hidden; margin-top:8px;
           background:
             radial-gradient(ellipse 60% 45% at 50% 12%, #0c0a09 0%, transparent 60%),
             linear-gradient(180deg, #34302b 0%, #241f1b 45%, #1a1614 75%, #12100e 100%);
           color:#f4efe8; }
  #arena { position:relative; display:flex; justify-content:space-around; align-items:flex-end;
           gap:12px; padding:44px 10px 14px; min-height:250px; }
  .torch { position:absolute; top:14px; font-size:20px; opacity:.8; animation:flick 1.6s infinite alternate; }
  @keyframes flick { from{opacity:.55; transform:scale(.95)} to{opacity:.9; transform:scale(1.05)} }
  .fighter { width:46%; max-width:300px; text-align:center; }
  .portrait { font-size:76px; line-height:1.05; display:inline-block;
              transition:transform .12s ease; filter:drop-shadow(0 6px 6px rgba(0,0,0,.5)); }
  .portrait.lungeL { transform:translateX(52px) scale(1.1); }
  .portrait.lungeR { transform:translateX(-52px) scale(1.1); }
  .portrait.hurt { animation:shake .3s; }
  .portrait.glow { filter:drop-shadow(0 0 14px #eda100); transform:scale(1.18); }
  .portrait.dead { transform:rotate(100deg) translateY(16px); opacity:.3; transition:all .6s; }
  @keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-8px)} 75%{transform:translateX(8px)} }
  .fname { font-size:12px; font-weight:600; margin:2px 0 4px; opacity:.9; }
  .hprow { display:flex; align-items:baseline; justify-content:center; gap:8px; }
  .hpbig { font-size:22px; font-weight:800; font-variant-numeric:tabular-nums;
           text-shadow:0 2px 3px rgba(0,0,0,.7); }
  .hpbig small { font-size:13px; font-weight:600; opacity:.75; }
  .defbadge { font-size:12px; font-weight:700; background:#26364d; border:1px solid #4a6a96;
              border-radius:6px 6px 10px 10px; padding:1px 8px; font-variant-numeric:tabular-nums; }
  .vbar { position:relative; height:12px; border-radius:4px; background:rgba(0,0,0,.55);
          overflow:hidden; margin-top:4px; border:1px solid rgba(255,255,255,.14); }
  .vbar .fill { position:absolute; inset:0 auto 0 0; transition:width .18s ease; }
  .vbar.hp .fill { background:linear-gradient(180deg,#f16a5f,#d03b3b); }
  .vbar.def { height:7px; } .vbar.def .fill { background:#86b6ef; }
  .agseg { display:flex; gap:3px; margin-top:5px; }
  .agseg span { flex:1; height:10px; border-radius:2px; background:rgba(0,0,0,.5);
                border:1px solid rgba(255,255,255,.16); }
  .agseg span.on { background:linear-gradient(180deg,#ffd257,#eda100); border-color:#eda100; }
  .sgthin { height:4px; border-radius:2px; background:rgba(0,0,0,.5); overflow:hidden; margin-top:5px; }
  .sgthin div { height:100%; transition:width .15s linear; }
  #loadout { display:flex; justify-content:space-between; align-items:flex-end; gap:10px;
             padding:10px 14px 12px; background:rgba(0,0,0,.45);
             border-top:1px solid rgba(255,255,255,.08); }
  .lgroup { display:flex; gap:8px; align-items:flex-end; }
  .wcard { text-align:center; opacity:.55; transition:all .18s; filter:grayscale(.4); }
  .wcard.act { opacity:1; filter:none; transform:translateY(-4px) scale(1.12); }
  .wcard .wico { font-size:30px; line-height:1.1; display:block;
                 filter:drop-shadow(0 3px 3px rgba(0,0,0,.6)); }
  .wcard .wnm { font-size:8px; opacity:.8; max-width:64px; overflow:hidden;
                text-overflow:ellipsis; white-space:nowrap; margin:1px auto 2px; }
  .wbadges { display:flex; gap:3px; justify-content:center; }
  .wbadges b { font-size:10px; font-weight:800; border-radius:5px 5px 8px 8px; padding:0 5px;
               font-variant-numeric:tabular-nums; }
  .wbadges .batk { background:#7a5b16; border:1px solid #eda100; color:#ffe6a8; }
  .wbadges .bchg { background:#1e3a5c; border:1px solid #5598e7; color:#cde2fb; }
  .fx { position:absolute; font-weight:800; font-size:17px; pointer-events:none; color:#fff;
        text-shadow:0 2px 4px rgba(0,0,0,.85); animation:floatup 1.1s ease-out forwards;
        white-space:nowrap; z-index:5; }
  .fx.big { font-size:23px; }
  @keyframes floatup { 0%{opacity:0; transform:translateY(8px) scale(.8)} 15%{opacity:1; transform:scale(1.1)}
                       30%{transform:scale(1)} 100%{opacity:0; transform:translateY(-52px)} }
  #vbanner { position:absolute; left:50%; top:34%; transform:translate(-50%,-50%);
             font-size:24px; font-weight:800; display:none; z-index:6; color:#fff;
             background:rgba(0,0,0,.75); border:1px solid rgba(255,255,255,.25);
             border-radius:12px; padding:10px 22px; text-shadow:0 2px 4px rgba(0,0,0,.8); }
  .vctrl { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-top:4px; font-size:12px; color:var(--ink2); }
  .vctrl button { font:inherit; font-size:12px; padding:3px 12px; border-radius:6px;
                  border:1px solid var(--ring); background:var(--page); color:var(--ink); cursor:pointer; }
  .vctrl button.on { border-color:var(--p-hp); box-shadow:inset 0 0 0 1px var(--p-hp); }
</style>
</head>
<body>
<h1>Sumeeper Combat Sim Report</h1>
<div class="sub">Heatmap: สีน้ำเงิน = ผู้เล่นชนะ, สีแดง = มอนสเตอร์ชนะ — ยิ่งเข้มยิ่งชนะขาด (วัดจาก % HP ที่เหลือ) · ตัวเลขในช่อง = จำนวน tick · คลิกช่องเพื่อดู Combat Viewer และกราฟไฟต์นั้น</div>
<div class="sub" id="metaLine" style="font-size:11px"></div>
<div class="tiles" id="tiles"></div>
<div class="card" id="refCard" style="display:none">
  <h2>เทียบกับค่าอ้างอิง (ref)</h2>
  <div class="sub" id="refHead"></div>
  <div id="refBody" style="font-size:13px; margin-top:8px"></div>
</div>
<div class="card" id="arenaCard">
  <h2 id="vTitle">Combat Viewer</h2>
  <div class="vctrl">
    <button id="vPlay">⏸ หยุด</button>
    <button id="vRestart">↻ เริ่มใหม่</button>
    <span>ความเร็ว:</span>
    <button class="vspd on" data-s="1">x1</button>
    <button class="vspd" data-s="2">x2</button>
    <button class="vspd" data-s="4">x4</button>
    <button class="vspd" data-s="8">x8</button>
    <span id="vTick" style="margin-left:auto;font-variant-numeric:tabular-nums"></span>
  </div>
  <div id="scene">
    <div id="arena">
      <span class="torch" style="left:12px">🔥</span>
      <span class="torch" style="right:12px; animation-delay:.7s">🔥</span>
      <div id="vbanner"></div>
      <div class="fighter">
        <span class="portrait" id="poP">🧑‍🍳</span>
        <div class="fname" style="color:#9ec5f4">ผู้เล่น</div>
        <div class="hprow"><span class="hpbig" id="vhpPt"></span><span class="defbadge" id="vdefPt"></span></div>
        <div class="vbar hp"><div class="fill" id="vhpP"></div></div>
        <div class="vbar def"><div class="fill" id="vdefP"></div></div>
        <div class="agseg" id="vagP"></div>
        <div class="sgthin"><div id="vsgP" style="background:#5598e7"></div></div>
      </div>
      <div class="fighter">
        <span class="portrait" id="poM">👾</span>
        <div class="fname" id="vnameM" style="color:#f2ab85"></div>
        <div class="hprow"><span class="hpbig" id="vhpMt"></span><span class="defbadge" id="vdefMt"></span></div>
        <div class="vbar hp"><div class="fill" id="vhpM"></div></div>
        <div class="vbar def"><div class="fill" id="vdefM"></div></div>
        <div class="agseg" id="vagM"></div>
        <div class="sgthin"><div id="vsgM" style="background:#eb6834"></div></div>
      </div>
    </div>
    <div id="loadout">
      <div class="lgroup" id="vseqP"></div>
      <div class="lgroup" id="vseqM"></div>
    </div>
  </div>
  <div class="note">เลขใหญ่ = HP · ป้ายโล่ = หลอด DEF ที่เหลือ (รับดาเมจก่อน HP) · ช่องเหลือง = Action Gauge เต็มแล้วออก Special · เส้นบางล่าง = Speed Gauge (เติมด้วย SPD ของชิ้นที่ยกขึ้น) · การ์ดล่างซ้าย = sequence ผู้เล่น (ป้ายทอง ATK / ป้ายฟ้า Charge ค่าจริงราย action) ขวา = ของมอนสเตอร์</div>
</div>
<div class="card" id="sandbox">
  <h2>Loadout</h2>
  <div class="sub">เลือกอาวุธลงช่อง 1–3 (ลำดับช่อง = ลำดับ Action Sequence) — คลิกช่องแล้วพิมพ์ค้นหาได้ · เว้นว่างทุกช่อง = ตีด้วย base stat · ผลรันใหม่ทันทีที่เปลี่ยน</div>
  <div class="sbrow" id="slots"></div>
  <div class="sbrow">
    <button id="clearSeq">ล้างทุกช่อง</button>
    <label>สู้กับ <select id="mSel"></select></label>
  </div>
  <div class="sub" id="sbStats"></div>
</div>
<div class="card"><h2>ผลทุกคู่ (build × monster)</h2><table class="hm" id="hm"></table></div>
<div class="card" id="detailCard">
  <h2 id="dTitle">เลือกช่องจาก heatmap หรือจัดชุดใน Sandbox เพื่อดู timeline</h2>
  <div class="sub" id="dSub"></div>
  <div id="chart"></div>
  <div class="legend" id="dLegend" style="display:none">
    <span><span class="lg-line" style="border-color:var(--p-hp)"></span> เส้นทึบ = HP</span>
    <span><span class="lg-line lg-dash" style="border-color:var(--p-def)"></span> เส้นประ = หลอด DEF</span>
    <span>◆ = Special ออก</span>
    <span>○ = DEF หมด (On-Exposed)</span>
    <span>✕ = ตาย</span>
  </div>
  <div class="note" id="howto" style="display:none">
    <b>วิธีอ่าน:</b> แกนนอนคือเวลา (tick) · กราฟแยกสองแผง — บนคือผู้เล่น ล่างคือมอนสเตอร์ <b>คนละสเกลกัน</b>
    เพราะ HP สองฝั่งต่างกันมาก · ดาเมจจะกินเส้นประ (หลอด DEF) ก่อนเสมอ —
    สังเกตว่าเส้นทึบ (HP) เริ่มไหลลงหลังจากเส้นประแตะศูนย์ที่จุด ○ ·
    เส้นเป็นขั้นบันไดเพราะค่าเปลี่ยนเป็นจังหวะตาม action ไม่ใช่ต่อเนื่อง ·
    เอาเมาส์ชี้บนกราฟเพื่อดูตัวเลขราย tick
  </div>
</div>
<details><summary>ดูเป็นตาราง (accessibility / copy ได้)</summary><table class="flat" id="flat"></table></details>
<div class="note" id="notes"></div>
<div id="tip"></div>
<script>
const DATA = __DATA__;
const $ = s => document.querySelector(s);
const tip = $("#tip");
const isDark = () => matchMedia("(prefers-color-scheme: dark)").matches;

function pal() {
  const d = isDark();
  return { mid: d ? [56,56,53] : [240,239,236],
           blue: d ? [57,135,229] : [42,120,214],
           red:  d ? [230,103,103] : [227,73,72] };
}
const lerp = (a,b,t) => a.map((v,i)=>Math.round(v+(b[i]-v)*t));
const lum = c => { const f=v=>{v/=255; return v<=.03928?v/12.92:((v+.055)/1.055)**2.4};
                   return .2126*f(c[0])+.7152*f(c[1])+.0722*f(c[2]); };

function cellColor(margin) {
  const p = pal();
  const c = margin >= 0 ? lerp(p.mid, p.blue, Math.min(1, margin))
                        : lerp(p.mid, p.red, Math.min(1, -margin));
  return { bg:`rgb(${c})`, ink: lum(c) > 0.35 ? "#0b0b0b" : "#ffffff" };
}

// ---- header meta + stat tiles + ref comparison ----
$("#metaLine").textContent = `รายงานสร้างเมื่อ ${DATA.meta.generated} · Equipment Sheet แก้ล่าสุด ${DATA.meta.eq_mtime} · Monster Sheet แก้ล่าสุด ${DATA.meta.mon_mtime}`;
const refFlip = (mk, build) => {
  if (!DATA.ref || !DATA.ref.results[mk]) return null;
  const rr = DATA.ref.results[mk][build];
  return rr && rr.win !== undefined ? rr : null;
};
{
  const wins = DATA.builds.map(b => 0);
  let flips = 0;
  DATA.rows.forEach((r, ri) => r.cells.forEach((c, i) => {
    if (c.win === "P") wins[i]++;
    const rr = refFlip(DATA.sim.morder[ri], c.build);
    if (rr && rr.win !== c.win) flips++;
  }));
  $("#tiles").innerHTML = DATA.builds.map((b, i) =>
    `<div class="tile"><div class="v">${wins[i]}<span style="font-size:13px;color:var(--ink2)">/${DATA.rows.length}</span></div>
     <div class="k">${b} — ผู้เล่นชนะ</div></div>`).join("") +
    (DATA.ref ? `<div class="tile"><div class="v">${flips}</div><div class="k">คู่ที่ผลพลิกจาก ref ✱</div></div>` : "");
  if (DATA.ref) {
    const R = DATA.ref;
    $("#refCard").style.display = "block";
    $("#refHead").textContent = `ref บันทึกเมื่อ ${R.generated} — ${R.note} · ช่องที่มีเครื่องหมาย ✱ ใน heatmap คือผลแพ้ชนะพลิกจาก ref (ดูค่า ref ได้ใน tooltip) · ตั้งค่าปัจจุบันเป็น ref ใหม่: รัน make_reference.bat`;
    const sec = (title, arr) => arr.length
      ? `<div style="margin-top:6px"><b>${title} (${arr.length})</b><ul style="margin:4px 0 0 20px">` +
        arr.map(d => `<li>${d}</li>`).join("") + `</ul></div>` : "";
    $("#refBody").innerHTML =
      (R.mdiffs.length || R.wdiffs.length)
        ? sec("Monster ที่ค่าต่างจาก ref", R.mdiffs) + sec("Equipment ที่ค่าต่างจาก ref", R.wdiffs)
        : `<span style="color:var(--muted)">ค่า stat ทั้งหมดตรงกับ ref ทุกตัว (ยังไม่มีการจูนใหม่)</span>`;
  }
}

// ---- heatmap ----
function renderHeatmap() {
  const t = $("#hm");
  let html = `<tr><th>Monster</th>` + DATA.builds.map(b=>`<th class="bh">${b}</th>`).join("") + `</tr>`;
  let lastTier = 0;
  DATA.rows.forEach((r, ri) => {
    if (r.tier !== lastTier) {
      lastTier = r.tier;
      html += `<tr><td class="tier" colspan="${DATA.builds.length+1}">TIER ${r.tier}</td></tr>`;
    }
    html += `<tr><th>${r.monster}</th>` + r.cells.map((c, ci) => {
      const col = cellColor(c.margin);
      const rr = refFlip(DATA.sim.morder[ri], c.build);
      const flip = rr && rr.win !== c.win;
      return `<td class="cell" id="c-${ri}-${ci}" style="background:${col.bg};color:${col.ink}${flip ? ";font-weight:800" : ""}"
                  data-ri="${ri}" data-ci="${ci}">${flip ? "✱ " : ""}${c.win} · t${c.ticks}</td>`;
    }).join("") + `</tr>`;
  });
  t.innerHTML = html;
  t.querySelectorAll("td.cell").forEach(td => {
    td.onclick = () => select(+td.dataset.ri, +td.dataset.ci);
    td.onmousemove = ev => {
      const c = DATA.rows[+td.dataset.ri].cells[+td.dataset.ci];
      const m = DATA.rows[+td.dataset.ri];
      const rr = refFlip(DATA.sim.morder[+td.dataset.ri], c.build);
      showTip(ev, `<b>${m.monster}</b> vs ${c.build}<br>${c.weapons.join(" + ")}<br>` +
        `ผล: ${c.win==="P"?"ผู้เล่นชนะ":c.win==="M"?"มอนสเตอร์ชนะ":"TIMEOUT"} ใน ${c.ticks} tick<br>` +
        `HP เหลือ — ผู้เล่น ${c.php}/${c.pmaxhp} · มอนสเตอร์ ${c.mhp}/${c.mmaxhp}<br>` +
        `Special — ผู้เล่น ${c.psp} ครั้ง · มอนสเตอร์ ${c.msp} ครั้ง` +
        (rr ? `<br><span style="color:var(--muted)">Ref: ${rr.win} t${rr.ticks} (pHP ${rr.php} / mHP ${rr.mhp})` +
              (rr.win !== c.win ? " — <b>ผลพลิก!</b>" : "") + `</span>` : ""));
    };
    td.onmouseleave = hideTip;
  });
}
function showTip(ev, html) {
  tip.innerHTML = html; tip.style.display = "block";
  const w = tip.offsetWidth, h = tip.offsetHeight;
  tip.style.left = Math.min(ev.clientX + 14, innerWidth - w - 8) + "px";
  tip.style.top  = Math.min(ev.clientY + 14, innerHeight - h - 8) + "px";
}
function hideTip() { tip.style.display = "none"; }

// ---- detail chart ----
let selected = null, lastView = null;
function select(ri, ci) {
  selected = [ri, ci]; lastView = "cell";
  document.querySelectorAll("td.cell.sel").forEach(e=>e.classList.remove("sel"));
  const td = $(`#c-${ri}-${ci}`); if (td) td.classList.add("sel");
  const r = DATA.rows[ri], c = r.cells[ci];
  $("#dTitle").textContent = `${r.monster} (T${r.tier}) vs ${c.build}`;
  $("#dSub").textContent = `${c.weapons.length?c.weapons.join(" + "):"(base stat ล้วน)"} — ${c.win==="P"?"ผู้เล่นชนะ":c.win==="M"?"มอนสเตอร์ชนะ":"TIMEOUT"} ใน ${c.ticks} tick`;
  $("#dLegend").style.display = "flex";
  drawChart(c);
  // sync loadout dropdowns + monster select with the clicked matchup
  sb.slots = [c.weapons[0] || null, c.weapons[1] || null, c.weapons[2] || null];
  sb.monster = DATA.sim.morder[ri];
  $("#mSel").value = sb.monster;
  renderSlots(); renderStats();
  viewerLoad(c.weapons, DATA.sim.morder[ri], `${r.monster} vs ${c.build}`);
}

// ---- combat engine (JS port of sumeeper_combat_sim.py — MUST stay in sync with it) ----
const SIM = DATA.sim;
let __aid = 0;
Object.values(SIM.weapons).forEach(w => w.abil.forEach(a => a.__id = ++__aid));
Object.values(SIM.monsters).forEach(m => { m.abil.forEach(a => a.__id = ++__aid);
  m.seq.forEach(e => e.abil.forEach(a => a.__id = ++__aid)); });
const r1 = v => Math.round(v * 10) / 10;

function mkEnt(name, hp, dfs, maxag) {
  return { name, hp, maxhp: hp, dfs, maxag, spd: 0, atk_bonus: 0, thorn: 0, armor: 0,
           sgauge: 0, agauge: 0, seq_idx: 0, fired: new Set(), specials: 0,
           sequence: [], abilities: [], cur_abil: [], burst_atk: 0 };
}

function runFight(loadoutNames, mkey, wantRec) {
  const notes = new Set(), events = [];
  const REC = wantRec ? { snaps: [], evs: [] } : null;  // detailed playback log for the Combat Viewer
  let curT = 0;
  const m = SIM.monsters[mkey], P = SIM.player;
  const pw = loadoutNames.map(n => SIM.weapons[n]);
  const p = mkEnt("player", P.hp, P.dfs + pw.reduce((s, w) => s + w.dfs, 0), P.maxag);
  p.sequence = pw.length
    ? pw.map(w => ({ atk: P.atk + w.atk, spd: P.spd + w.spd, chg: P.chg + w.chg,
                     abil: w.abil.filter(a => a.lane === "Action") }))
    : [{ atk: P.atk, spd: P.spd, chg: P.chg, abil: [] }];
  p.abilities = pw.flatMap(w => w.abil.filter(a => a.lane !== "Action"));
  p.burst_atk = p.sequence.reduce((s, e) => s + e.atk, 0);
  const e = mkEnt(m.name, m.hp, m.dfs, m.maxag);
  e.sequence = m.seq.map(x => ({ ...x, spd: m.base_spd + x.spd }));  // per-action SPD = base + entry (same rule as player)
  e.abilities = m.abil;
  p.cur_abil = p.abilities; e.cur_abil = e.abilities;

  function applyAb(a, owner, foe, when) {
    if (a.trig !== when) return;
    const { verb, tgt } = a, mag = a.mag;
    if (typeof mag !== "number") { notes.add("Scaling not simulated (" + owner.name + ")"); return; }
    if (verb === "Gain") {
      if (tgt === "ATK") owner.atk_bonus += mag;
      else if (tgt === "DEF") { owner.dfs += mag; if (REC) REC.evs.push({ t: curT, kind: "gaindef", side: sideOf(owner), dmg: mag }); }
      else if (tgt === "SPD") owner.spd += mag;
      else if (tgt === "Thorn") owner.thorn += mag;
      else if (tgt === "Armor" || tgt === "Shield") owner.armor += mag;
      else notes.add("Gain " + tgt + " not simulated");
    } else if (verb === "Restore") {
      owner.hp = Math.min(owner.maxhp, owner.hp + mag);
      if (REC) REC.evs.push({ t: curT, kind: "heal", side: sideOf(owner), dmg: mag });
    }
    else if (verb === "Lose") {
      if (tgt === "ATK") owner.atk_bonus -= mag;
      else if (tgt === "DEF") owner.dfs -= mag;
    } else if (verb === "Convert" || verb === "Eater") notes.add(verb + " not simulated (" + owner.name + ")");
  }
  function fire(ent, foe, when, once, pool) {
    (pool || ent.abilities).forEach(a => {
      const key = a.__id + "|" + when;
      if (once && ent.fired.has(key)) return;
      if (a.trig === when) { if (once) ent.fired.add(key); applyAb(a, ent, foe, when); }
    });
  }
  const sideOf = ent => ent.name === "player" ? "P" : "M";
  function deal(def, atk_, dmg) {
    if (dmg <= 0) return;
    const had = def.dfs > 0, ab = Math.min(Math.max(def.dfs, 0), dmg);
    def.dfs -= ab; def.hp -= dmg - ab;
    if (had && def.dfs <= 0) {
      if (REC) REC.evs.push({ t: curT, kind: "exposed", side: sideOf(def) });
      fire(def, atk_, "On-Exposed", true, def.abilities);
    }
  }
  function hitE(attacker, defender, atk) {
    const dmg = Math.max(1, atk - defender.armor);
    const wasAbove = defender.hp > defender.maxhp / 2;
    deal(defender, attacker, dmg);
    fire(attacker, defender, "On-Hit", false, attacker.cur_abil);
    fire(defender, attacker, "On-Damaged", false, defender.abilities);
    if (wasAbove && defender.hp <= defender.maxhp / 2) fire(defender, attacker, "On-Half", true, defender.abilities);
    if (defender.thorn > 0) {
      deal(attacker, defender, defender.thorn);
      if (REC) REC.evs.push({ t: curT, kind: "thorn", side: sideOf(attacker), dmg: defender.thorn });
    }
    return dmg;
  }
  function doSpecial(ent, foe, t) {
    events.push([t, sideOf(ent)]);
    const sp = ent.abilities.filter(a => a.lane === "Special");
    let d = null;
    if (sp.length) sp.forEach(a => applyAb(a, ent, foe, "Special"));
    else { ent.cur_abil = []; d = Math.max(1, ent.burst_atk + ent.atk_bonus - foe.armor); deal(foe, ent, d); }
    if (REC) REC.evs.push({ t, kind: "special", side: sideOf(ent), dmg: d });
    ent.specials++;
  }
  function stepE(ent, foe, t) {
    const myIdx = ent.seq_idx;
    const entry = ent.sequence[myIdx];
    ent.seq_idx = (myIdx + 1) % ent.sequence.length;
    ent.cur_abil = ent.abilities.concat(entry.abil || []);
    const d = hitE(ent, foe, entry.atk + ent.atk_bonus);
    if (REC) REC.evs.push({ t, kind: "hit", side: sideOf(ent), idx: myIdx, dmg: d });
    ent.agauge += entry.chg;
    if (ent.agauge >= ent.maxag && foe.hp > 0 && ent.hp > 0) { ent.agauge = 0; doSpecial(ent, foe, t); }
    ent.cur_abil = ent.abilities;
  }

  fire(p, e, "On-Start", true, p.abilities);
  fire(e, p, "On-Start", true, e.abilities);
  let t = 0;
  const history = [[0, p.hp, p.dfs, e.hp, e.dfs]];
  const snap = () => {
    history.push([t, r1(p.hp), r1(p.dfs), r1(e.hp), r1(e.dfs)]);
    if (REC) REC.snaps.push([t, r1(p.hp), r1(p.dfs), r1(p.sgauge), p.agauge, p.seq_idx,
                             r1(e.hp), r1(e.dfs), r1(e.sgauge), e.agauge, e.seq_idx]);
  };
  if (REC) REC.snaps.push([0, p.hp, p.dfs, 0, 0, 0, e.hp, e.dfs, 0, 0, 0]);
  while (t < SIM.tickLimit && p.hp > 0 && e.hp > 0) {
    t++; curT = t;
    p.sgauge += Math.max(1, p.sequence[p.seq_idx].spd + p.spd);
    e.sgauge += Math.max(1, e.sequence[e.seq_idx].spd + e.spd);
    if (p.sgauge >= SIM.gaugeMax) { p.sgauge -= SIM.gaugeMax; stepE(p, e, t); }
    if (e.hp <= 0 || p.hp <= 0) { snap(); break; }
    if (e.sgauge >= SIM.gaugeMax) { e.sgauge -= SIM.gaugeMax; stepE(e, p, t); }
    snap();
  }
  const win = e.hp <= 0 ? "P" : (p.hp <= 0 ? "M" : "TIMEOUT");
  return { build: "Sandbox", weapons: loadoutNames, mname: m.name, win, ticks: t,
           php: r1(p.hp), mhp: r1(e.hp), pmaxhp: p.maxhp, mmaxhp: e.maxhp,
           psp: p.specials, msp: e.specials, history, events, notes: [...notes], rec: REC };
}

// ---- combat viewer (tick-by-tick playback of a logged fight) ----
const MEMOJI = { MONSTER_ORANGECAT:"🐱", MONSTER_ONPIRENION:"🧅", MONSTER_MUSHROOMRAT:"🍄",
  MONSTER_CABBAGEDOG:"🐶", MONSTER_CHERRYBIRD:"🐦", MONSTER_PUDDINGCRAP:"🦀",
  MONSTER_SUGARTIGER:"🐯", MONSTER_SPICYHEDGEHOG:"🦔", MONSTER_BLUEFIN:"🐟",
  MONSTER_PIZZATURTLE:"🐢", MONSTER_DURAINBOMB:"💣", MONSTER_CHIVE:"🧄",
  MONSTER_BROCOLION:"🥦", MONSTER_BANANAOCTOPUS:"🐙", MONSTER_UBEECORN:"🦄",
  MONSTER_MONKEYCUPSSPICES:"🐵", MONSTER_DEARBOKCHOY:"🥬", MONSTER_JELLYUDON:"🍜" };
const TICK_MS = 550;  // x1 pace: slow enough to read each action
const V = { timer:null, i:0, playing:false, speed:1, rec:null, meta:null };
const WEMOJI = { "Frying pan":"🍳", "Broken Plate":"🍽️", "Mysterious Pot":"🍲", "Mortar and Pestle":"🥣",
  "Spirit Fork":"🔱", "Chopping Board":"🪵", "Windmill Spatula":"🌪️", "Cloud Cutting Spoon":"☁️",
  "Immortal Ladle":"✨", "Darkness Apron":"🥷", "Infinity Gloves":"🧤", "Bottomless Chef's Hat":"👒",
  "Miracle Knife":"🔪", "⟨ex⟩ Twin Ladle":"⚔️", "Golden pan":"🥇", "Surya Dough Kneader":"🥖",
  "The Great Microwave":"🎛️", "Dragon Bone Ladle":"🐉", "Emperor Knife":"👑", "Gaint Fork":"🍴",
  "Maid Apron":"🎀", "Peem":"🐣", "Cast Iron Lid":"🛡️", "Butcher Cleaver":"🪓", "Titan Stone Mortar":"🗿" };

function viewerLoad(weapons, mkey, label) {
  const r = runFight(weapons, mkey, true);
  const m = SIM.monsters[mkey];
  V.rec = r.rec;
  V.meta = { weapons, mkey, label, win: r.win, ticks: r.ticks,
    pmax: r.pmaxhp, mmax: r.mmaxhp, pagmax: SIM.player.maxag, magmax: m.maxag,
    pdefmax: Math.max(1, ...V.rec.snaps.map(s => s[2])), mdefmax: Math.max(1, ...V.rec.snaps.map(s => s[7])),
    pseq: weapons.length ? weapons : ["Base"], mseq: m.seq.map((x, i) => `A${i+1}·${x.atk}`),
    mname: m.name };
  $("#vTitle").textContent = `Combat Viewer — ${label}`;
  $("#vnameM").textContent = m.name;
  $("#poM").textContent = MEMOJI[mkey] || "👾";
  $("#poP").classList.remove("dead"); $("#poM").classList.remove("dead");
  $("#vbanner").style.display = "none";
  const P = SIM.player;
  const card = (ico, nm, atk, chg) =>
    `<div class="wcard"><span class="wico">${ico}</span><span class="wnm">${nm}</span>` +
    `<span class="wbadges"><b class="batk">⚔${atk}</b><b class="bchg">⚡${chg}</b></span></div>`;
  $("#vseqP").innerHTML = weapons.length
    ? weapons.map(n => { const w = SIM.weapons[n];
        return card(WEMOJI[n] || "🍴", n, P.atk + w.atk, P.chg + w.chg); }).join("")
    : card("👊", "Base", P.atk, P.chg);
  $("#vseqM").innerHTML = m.seq.map((x, i) => card(MEMOJI[mkey] || "👾", `A${i+1}`, x.atk, x.chg)).join("");
  $("#vagP").innerHTML = Array.from({length: V.meta.pagmax}, () => "<span></span>").join("");
  $("#vagM").innerHTML = Array.from({length: V.meta.magmax}, () => "<span></span>").join("");
  vRestart();
}
function setBars(s) {
  const M = V.meta;
  $("#vhpP").style.width = Math.max(0, s[1] / M.pmax * 100) + "%";
  $("#vhpPt").innerHTML = `${s[1]}<small>/${M.pmax}</small>`;
  $("#vdefP").style.width = Math.max(0, s[2] / M.pdefmax * 100) + "%";
  $("#vdefPt").textContent = `🛡 ${s[2]}`;
  $("#vsgP").style.width = Math.min(100, s[3] / SIM.gaugeMax * 100) + "%";
  $("#vagP").querySelectorAll("span").forEach((el, i) => el.classList.toggle("on", i < s[4]));
  $("#vseqP").querySelectorAll(".wcard").forEach((el, i) => el.classList.toggle("act", i === s[5]));
  $("#vhpM").style.width = Math.max(0, s[6] / M.mmax * 100) + "%";
  $("#vhpMt").innerHTML = `${s[6]}<small>/${M.mmax}</small>`;
  $("#vdefM").style.width = Math.max(0, s[7] / M.mdefmax * 100) + "%";
  $("#vdefMt").textContent = `🛡 ${s[7]}`;
  $("#vsgM").style.width = Math.min(100, s[8] / SIM.gaugeMax * 100) + "%";
  $("#vagM").querySelectorAll("span").forEach((el, i) => el.classList.toggle("on", i < s[9]));
  $("#vseqM").querySelectorAll(".wcard").forEach((el, i) => el.classList.toggle("act", i === s[10]));
}
function fxText(side, text, big, dy, color) {
  const el = document.createElement("div");
  el.className = "fx" + (big ? " big" : "");
  el.textContent = text;
  el.style[side === "P" ? "left" : "right"] = "14%";
  el.style.top = (64 + (dy || 0)) + "px";
  if (color) el.style.color = color;
  $("#arena").appendChild(el);
  setTimeout(() => el.remove(), 1100);
}
function animEvents(t) {
  const evs = V.rec.evs.filter(e => e.t === t);
  evs.forEach((ev, i) => setTimeout(() => {
    const actorPo = ev.side === "P" ? "#poP" : "#poM";
    const target = ev.side === "P" ? "M" : "P";
    const targetPo = ev.side === "P" ? "#poM" : "#poP";
    if (ev.kind === "hit" || (ev.kind === "special" && ev.dmg != null)) {
      const po = $(actorPo);
      po.classList.add(ev.side === "P" ? "lungeL" : "lungeR");
      if (ev.kind === "special") po.classList.add("glow");
      setTimeout(() => { po.classList.remove("lungeL", "lungeR", "glow"); }, 180);
      const tp = $(targetPo);
      tp.classList.add("hurt"); setTimeout(() => tp.classList.remove("hurt"), 320);
      fxText(target, (ev.kind === "special" ? "💥 −" : "−") + ev.dmg, ev.kind === "special",
             i * 20, ev.kind === "special" ? "#ffd257" : "#fff");
    } else if (ev.kind === "special") {
      const po = $(actorPo);
      po.classList.add("glow"); setTimeout(() => po.classList.remove("glow"), 300);
      fxText(ev.side, "✨ SPECIAL!", true, i * 20, "#ffd257");
    } else if (ev.kind === "thorn") {
      fxText(ev.side, `🌵 −${ev.dmg}`, false, 28 + i * 20, "#7ddb7d");
    } else if (ev.kind === "exposed") {
      fxText(ev.side, "🛡 DEF แตก!", true, 12 + i * 20, "#9ec5f4");
    } else if (ev.kind === "heal") {
      fxText(ev.side, `+${ev.dmg}`, false, i * 20, "#7ddb7d");
    } else if (ev.kind === "gaindef") {
      fxText(ev.side, `🛡 +${ev.dmg}`, false, 22 + i * 20, "#9ec5f4");
    }
  }, i * 110));
}
function vFrame() {
  if (V.i >= V.rec.snaps.length) { vEnd(); return; }
  const s = V.rec.snaps[V.i];
  setBars(s);
  if (V.i > 0) animEvents(s[0]);
  $("#vTick").textContent = `tick ${s[0]} / ${V.meta.ticks}`;
  V.i++;
}
function vEnd() {
  clearInterval(V.timer); V.timer = null; V.playing = false;
  $("#vPlay").textContent = "▶ เล่น";
  const b = $("#vbanner");
  if (V.meta.win === "P") { $("#poM").classList.add("dead"); b.textContent = "🏆 ผู้เล่นชนะ!"; b.style.color = "#9ec5f4"; }
  else if (V.meta.win === "M") { $("#poP").classList.add("dead"); b.textContent = `${V.meta.mname} ชนะ!`; b.style.color = "#f2ab85"; }
  else { b.textContent = "หมดเวลา (TIMEOUT)"; b.style.color = "#c3c2b7"; }
  b.style.display = "block";
}
function vStart() {
  clearInterval(V.timer);
  V.playing = true; $("#vPlay").textContent = "⏸ หยุด";
  V.timer = setInterval(vFrame, TICK_MS / V.speed);
}
function vRestart() {
  clearInterval(V.timer); V.i = 0;
  $("#poP").classList.remove("dead"); $("#poM").classList.remove("dead");
  $("#vbanner").style.display = "none";
  vFrame(); vStart();
}
$("#vPlay").onclick = () => { if (V.playing) { clearInterval(V.timer); V.playing = false; $("#vPlay").textContent = "▶ เล่น"; } else if (V.rec) vStart(); };
$("#vRestart").onclick = () => { if (V.rec) vRestart(); };
document.querySelectorAll(".vspd").forEach(b => b.onclick = () => {
  V.speed = +b.dataset.s;
  document.querySelectorAll(".vspd").forEach(x => x.classList.toggle("on", x === b));
  if (V.playing) vStart();
});

// ---- sandbox UI: 3 loadout slots, each a searchable dropdown ----
const sb = { slots: ["Frying pan", "Chopping Board", null], monster: SIM.morder[0] };
Object.defineProperty(sb, "seq", { get() { return this.slots.filter(Boolean); } });
const RARITIES = ["Common", "Rare", "Epic", "Legend", "Mythic"];

function slotLabel(n) {
  return n ? `${WEMOJI[n] || "🍴"} ${n}` : "— ว่าง —";
}
function ddOptions(filter) {
  const q = (filter || "").toLowerCase();
  let html = `<div class="opt" data-v="">🚫 — ว่าง — <small>ไม่ใส่อาวุธช่องนี้</small></div>`;
  RARITIES.forEach(rar => {
    const ws = Object.values(SIM.weapons).filter(w => w.rar === rar &&
      (!q || w.name.toLowerCase().includes(q) || rar.toLowerCase().includes(q)));
    if (!ws.length) return;
    html += `<div class="ddgroup">${rar.toUpperCase()}</div>` + ws.map(w =>
      `<div class="opt" data-v="${w.name}">${WEMOJI[w.name] || "🍴"} ${w.name}
         <small>⚔${w.atk} 🛡${w.dfs} 💨${w.spd} ⚡${w.chg}</small></div>`).join("");
  });
  return html;
}
function closeDds() { document.querySelectorAll(".dd").forEach(d => d.remove()); }
function renderSlots() {
  $("#slots").innerHTML = [0, 1, 2].map(i =>
    `<div class="slot" data-i="${i}"><span class="num">ช่อง ${i + 1}</span>` +
    `<button class="slotbtn${sb.slots[i] ? "" : " empty"}">${slotLabel(sb.slots[i])} ▾</button></div>`).join("");
  $("#slots").querySelectorAll(".slot").forEach(sl => {
    const i = +sl.dataset.i;
    sl.querySelector(".slotbtn").onclick = ev => {
      ev.stopPropagation();
      const wasOpen = !!sl.querySelector(".dd");
      closeDds();
      if (wasOpen) return;
      const dd = document.createElement("div");
      dd.className = "dd";
      dd.innerHTML = `<input placeholder="พิมพ์ชื่ออาวุธหรือ rarity..."><div class="ddlist">${ddOptions("")}</div>`;
      dd.onclick = e => e.stopPropagation();
      sl.appendChild(dd);
      const inp = dd.querySelector("input"), list = dd.querySelector(".ddlist");
      const wire = () => list.querySelectorAll(".opt").forEach(o => {
        if (o.dataset.v === (sb.slots[i] || "")) o.classList.add("cur");
        o.onclick = () => { sb.slots[i] = o.dataset.v || null; closeDds(); refreshSandbox(); };
      });
      wire();
      inp.oninput = () => { list.innerHTML = ddOptions(inp.value); wire(); };
      inp.onkeydown = e => {
        if (e.key === "Enter") { const o = list.querySelector(".opt:not([data-v=''])") || list.querySelector(".opt"); if (o) o.click(); }
        if (e.key === "Escape") closeDds();
      };
      inp.focus();
    };
  });
}
document.addEventListener("click", closeDds);
function renderStats() {
  const P = SIM.player;
  const pw = sb.seq.map(n => SIM.weapons[n]);
  const defSum = P.dfs + pw.reduce((s, w) => s + w.dfs, 0);
  const per = pw.length
    ? pw.map((w, i) => `${i + 1}) ATK ${P.atk + w.atk} · SPD ${P.spd + w.spd} · Chg ${P.chg + w.chg}`).join("   ")
    : `ATK ${P.atk} · SPD ${P.spd} · Chg ${P.chg}`;
  const burst = pw.length ? pw.reduce((s, w) => s + P.atk + w.atk, 0) : P.atk;
  $("#sbStats").textContent =
    `ค่าจริงราย action (base+ชิ้น): ${per}   |   หลอด DEF รวม ${defSum} · Special burst ${burst} · HP ${P.hp} · MaxAG ${P.maxag}`;
}
function runSandbox() {
  lastView = "sandbox"; selected = null;
  document.querySelectorAll("td.cell.sel").forEach(e => e.classList.remove("sel"));
  const c = runFight(sb.seq, sb.monster);
  const m = SIM.monsters[sb.monster];
  $("#dTitle").textContent = `Sandbox: ${m.name} (T${m.tier})`;
  $("#dSub").textContent = `${sb.seq.length ? sb.seq.join(" + ") : "(base stat ล้วน)"} — ` +
    `${c.win === "P" ? "ผู้เล่นชนะ" : c.win === "M" ? "มอนสเตอร์ชนะ" : "TIMEOUT"} ใน ${c.ticks} tick · ` +
    `HP เหลือ ผู้เล่น ${c.php}/${c.pmaxhp} มอนสเตอร์ ${c.mhp}/${c.mmaxhp} · Special ${c.psp}/${c.msp}` +
    (c.notes.length ? ` · ไม่ได้จำลอง: ${c.notes.join(", ")}` : "");
  $("#dLegend").style.display = "flex";
  drawChart(c);
  viewerLoad(sb.seq.slice(), sb.monster, `Sandbox vs ${m.name}`);
}
function refreshSandbox() { renderSlots(); renderStats(); runSandbox(); }
{
  const sel = $("#mSel");
  let html = "", lastTier = 0;
  SIM.morder.forEach(k => {
    const m = SIM.monsters[k];
    if (m.tier !== lastTier) { if (lastTier) html += `</optgroup>`; html += `<optgroup label="Tier ${m.tier}">`; lastTier = m.tier; }
    html += `<option value="${k}">${m.name}</option>`;
  });
  sel.innerHTML = html + `</optgroup>`;
  sel.onchange = () => { sb.monster = sel.value; runSandbox(); };
  $("#clearSeq").onclick = () => { sb.slots = [null, null, null]; refreshSandbox(); };
}

function drawChart(c) {
  $("#howto").style.display = "block";
  const W = Math.min(860, $("#detailCard").clientWidth - 20);
  const ml = 44, mr = 110, PH = 120, GAP = 34, mt = 22, mb = 30;
  const H = mt + PH + GAP + PH + mb;
  const iw = W - ml - mr;
  const hist = c.history;
  const xmax = Math.max(1, hist[hist.length-1][0]);
  const X = t => ml + t / xmax * iw;
  const css = getComputedStyle(document.documentElement);
  const col = n => css.getPropertyValue(n).trim();

  // one panel = one entity: solid HP + dashed DEF, own y-scale
  function panel(top, hpIdx, defIdx, cHP, cDEF, title, side) {
    const ymax = Math.max(...hist.flatMap(h => [h[hpIdx], h[defIdx]]), 1);
    const Y = v => top + PH - Math.max(0, v) / ymax * PH;
    const stepPath = k => hist.map((h, i) =>
      i === 0 ? `M${X(h[0])},${Y(h[k])}` : `H${X(h[0])}V${Y(h[k])}`).join("");
    let s = `<text x="${ml}" y="${top-8}" style="fill:${col("--ink2")};font-weight:600">${title}</text>`;
    const stepv = Math.max(1, Math.ceil(ymax / 3));
    for (let v = 0; v <= ymax; v += stepv)
      s += `<line x1="${ml}" x2="${W-mr}" y1="${Y(v)}" y2="${Y(v)}" stroke="${col("--grid")}"/>` +
           `<text x="${ml-6}" y="${Y(v)+4}" text-anchor="end">${v}</text>`;
    s += `<line x1="${ml}" x2="${W-mr}" y1="${Y(0)}" y2="${Y(0)}" stroke="${col("--axis")}"/>`;
    s += `<path d="${stepPath(defIdx)}" fill="none" stroke="${cDEF}" stroke-width="2" stroke-dasharray="4 4"/>`;
    s += `<path d="${stepPath(hpIdx)}" fill="none" stroke="${cHP}" stroke-width="2"/>`;
    // direct labels at line ends (ink tokens, not series color)
    const last = hist[hist.length-1];
    let yH = Y(last[hpIdx]), yD = Y(last[defIdx]);
    if (Math.abs(yH - yD) < 13) { if (yH <= yD) { yH -= 7; yD += 7; } else { yH += 7; yD -= 7; } }
    s += `<text x="${W-mr+8}" y="${yH+4}" style="fill:${col("--ink2")}">HP ${last[hpIdx]}</text>` +
         `<text x="${W-mr+8}" y="${yD+4}" style="fill:${col("--muted")}">DEF ${last[defIdx]}</text>`;
    // event: DEF pool emptied (On-Exposed moment)
    if (hist[0][defIdx] > 0) {
      const bi = hist.findIndex((h, i) => i > 0 && h[defIdx] <= 0 && hist[i-1][defIdx] > 0);
      if (bi > 0) {
        const bx = X(hist[bi][0]);
        s += `<circle cx="${bx}" cy="${Y(0)}" r="5" fill="none" stroke="${cDEF}" stroke-width="2"/>` +
             `<text x="${bx}" y="${Y(0)+16}" text-anchor="middle" style="fill:${col("--muted")}">DEF หมด t${hist[bi][0]}</text>`;
      }
    }
    // event: Specials fired by this entity (diamond on its HP line)
    c.events.filter(([, sd]) => sd === side).forEach(([t]) => {
      const h = hist.find(x => x[0] >= t) || last;
      const y = Y(h[hpIdx]);
      s += `<path d="M${X(t)},${y-5} l5,5 l-5,5 l-5,-5 z" fill="${cHP}" stroke="${col("--surface")}" stroke-width="2"/>`;
    });
    // event: death
    if (last[hpIdx] <= 0) {
      const dx = X(last[0]), dy = Y(0);
      s += `<path d="M${dx-5},${dy-5} l10,10 M${dx+5},${dy-5} l-10,10" stroke="${cHP}" stroke-width="2.5"/>`;
    }
    return s;
  }

  const topP = mt, topM = mt + PH + GAP;
  const xt = Math.max(1, Math.ceil(xmax / 8));
  let xax = "";
  for (let t = 0; t <= xmax; t += xt)
    xax += `<text x="${X(t)}" y="${H-10}" text-anchor="middle">${t}</text>`;
  xax += `<text x="${W-mr}" y="${H-10}" text-anchor="start" style="fill:${col("--muted")}">&#160;&#160;tick (เวลา)</text>`;

  $("#chart").innerHTML =
    `<svg id="svg" width="${W}" height="${H}" role="img" aria-label="HP/DEF timeline">
      ${panel(topP, 1, 2, col("--p-hp"), col("--p-def"), "ผู้เล่น", "P")}
      ${panel(topM, 3, 4, col("--m-hp"), col("--m-def"), c.mname || "มอนสเตอร์", "M")}
      ${xax}
      <line id="xh" y1="${mt}" y2="${topM+PH}" stroke="${col("--axis")}" stroke-dasharray="2 3" style="display:none"/>
    </svg>`;
  const svg = $("#svg");
  svg.onmousemove = ev => {
    const box = svg.getBoundingClientRect();
    const t = Math.round((ev.clientX - box.left - ml) / iw * xmax);
    if (t < 0 || t > xmax) { hideTip(); $("#xh").style.display="none"; return; }
    const h = hist.reduce((a,b) => b[0] <= t ? b : a, hist[0]);
    const xh = $("#xh"); xh.setAttribute("x1", X(t)); xh.setAttribute("x2", X(t)); xh.style.display="";
    showTip(ev, `<b>tick ${h[0]}</b><br>ผู้เล่น — HP ${h[1]} · DEF ${h[2]}<br>มอนสเตอร์ — HP ${h[3]} · DEF ${h[4]}`);
  };
  svg.onmouseleave = () => { hideTip(); const x=$("#xh"); if(x) x.style.display="none"; };
}

// ---- flat table ----
{
  let html = `<tr><th>Monster</th><th>Tier</th><th>Build</th><th>Loadout</th><th>ผล</th>
              <th>Ticks</th><th>pHP</th><th>mHP</th><th>Special P/M</th></tr>`;
  DATA.rows.forEach(r => r.cells.forEach(c => {
    html += `<tr><td>${r.monster}</td><td>${r.tier}</td><td>${c.build}</td>
      <td>${c.weapons.join(" + ")}</td><td>${c.win}</td><td>${c.ticks}</td>
      <td>${c.php}/${c.pmaxhp}</td><td>${c.mhp}/${c.mmaxhp}</td><td>${c.psp}/${c.msp}</td></tr>`;
  }));
  $("#flat").innerHTML = html;
}
$("#notes").textContent = DATA.notes.length ? "NOT SIMULATED: " + DATA.notes.join(", ") : "";
renderHeatmap();
renderSlots(); renderStats();
runSandbox();  // combat scene is always on — start with the default loadout right away
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
  renderHeatmap();
  if (lastView === "cell" && selected) select(...selected);
  else if (lastView === "sandbox") runSandbox();
});
</script>
</body>
</html>
"""

html = TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False))
out = "sim_report.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print(f"wrote {out}: {len(data['rows'])} monsters x {len(BUILD_NAMES)} builds")
