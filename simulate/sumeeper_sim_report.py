# -*- coding: utf-8 -*-
"""Generate sim_report.html — visual report of the combat sim.

Usage:  python sumeeper_sim_report.py   (then open sim_report.html in a browser)

Heatmap of every matchup (diverging color = win margin), click a cell to see
that fight's HP/DEF timeline with Special markers. Self-contained HTML, no CDN.
"""
import json
import sys
import sumeeper_combat_sim as S

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

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
</style>
</head>
<body>
<h1>Sumeeper Combat Sim Report</h1>
<div class="sub">Heatmap: สีน้ำเงิน = ผู้เล่นชนะ, สีแดง = มอนสเตอร์ชนะ — ยิ่งเข้มยิ่งชนะขาด (วัดจาก % HP ที่เหลือ) · ตัวเลขในช่อง = จำนวน tick · คลิกช่องเพื่อดูกราฟไฟต์นั้น</div>
<div class="tiles" id="tiles"></div>
<div class="card"><h2>ผลทุกคู่ (build × monster)</h2><table class="hm" id="hm"></table></div>
<div class="card" id="sandbox">
  <h2>Sandbox — จัดชุดสู้เอง</h2>
  <div class="sub">คลิกอาวุธเพื่อเพิ่มเข้า sequence (สูงสุด 3 ชิ้น กดซ้ำได้ถ้าถือซ้ำ) · คลิกชิ้นใน sequence เพื่อเอาออก · ไม่เลือกเลย = ตีด้วย base stat · ผลจะรันใหม่ทันทีที่เปลี่ยนอะไรก็ตาม</div>
  <div id="wpool"></div>
  <div class="sbrow">
    <span>Sequence:</span> <span id="wseq"><span style="color:var(--muted)">— ว่าง —</span></span>
    <button id="clearSeq">ล้าง</button>
    <label>สู้กับ <select id="mSel"></select></label>
  </div>
  <div class="sub" id="sbStats"></div>
</div>
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

// ---- stat tiles ----
{
  const wins = DATA.builds.map(b => 0);
  DATA.rows.forEach(r => r.cells.forEach((c,i) => { if (c.win==="P") wins[i]++; }));
  $("#tiles").innerHTML = DATA.builds.map((b,i) =>
    `<div class="tile"><div class="v">${wins[i]}<span style="font-size:13px;color:var(--ink2)">/${DATA.rows.length}</span></div>
     <div class="k">${b} — ผู้เล่นชนะ</div></div>`).join("");
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
      return `<td class="cell" id="c-${ri}-${ci}" style="background:${col.bg};color:${col.ink}"
                  data-ri="${ri}" data-ci="${ci}">${c.win} · t${c.ticks}</td>`;
    }).join("") + `</tr>`;
  });
  t.innerHTML = html;
  t.querySelectorAll("td.cell").forEach(td => {
    td.onclick = () => select(+td.dataset.ri, +td.dataset.ci);
    td.onmousemove = ev => {
      const c = DATA.rows[+td.dataset.ri].cells[+td.dataset.ci];
      const m = DATA.rows[+td.dataset.ri];
      showTip(ev, `<b>${m.monster}</b> vs ${c.build}<br>${c.weapons.join(" + ")}<br>` +
        `ผล: ${c.win==="P"?"ผู้เล่นชนะ":c.win==="M"?"มอนสเตอร์ชนะ":"TIMEOUT"} ใน ${c.ticks} tick<br>` +
        `HP เหลือ — ผู้เล่น ${c.php}/${c.pmaxhp} · มอนสเตอร์ ${c.mhp}/${c.mmaxhp}<br>` +
        `Special — ผู้เล่น ${c.psp} ครั้ง · มอนสเตอร์ ${c.msp} ครั้ง`);
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

function runFight(loadoutNames, mkey) {
  const notes = new Set(), events = [];
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
  e.sequence = m.seq.map(x => ({ ...x, spd: m.spd }));
  e.abilities = m.abil;
  p.cur_abil = p.abilities; e.cur_abil = e.abilities;

  function applyAb(a, owner, foe, when) {
    if (a.trig !== when) return;
    const { verb, tgt } = a, mag = a.mag;
    if (typeof mag !== "number") { notes.add("Scaling not simulated (" + owner.name + ")"); return; }
    if (verb === "Gain") {
      if (tgt === "ATK") owner.atk_bonus += mag;
      else if (tgt === "DEF") owner.dfs += mag;
      else if (tgt === "SPD") owner.spd += mag;
      else if (tgt === "Thorn") owner.thorn += mag;
      else if (tgt === "Armor" || tgt === "Shield") owner.armor += mag;
      else notes.add("Gain " + tgt + " not simulated");
    } else if (verb === "Restore") owner.hp = Math.min(owner.maxhp, owner.hp + mag);
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
  function deal(def, atk_, dmg) {
    if (dmg <= 0) return;
    const had = def.dfs > 0, ab = Math.min(Math.max(def.dfs, 0), dmg);
    def.dfs -= ab; def.hp -= dmg - ab;
    if (had && def.dfs <= 0) fire(def, atk_, "On-Exposed", true, def.abilities);
  }
  function hitE(attacker, defender, atk) {
    const dmg = Math.max(1, atk - defender.armor);
    const wasAbove = defender.hp > defender.maxhp / 2;
    deal(defender, attacker, dmg);
    fire(attacker, defender, "On-Hit", false, attacker.cur_abil);
    fire(defender, attacker, "On-Damaged", false, defender.abilities);
    if (wasAbove && defender.hp <= defender.maxhp / 2) fire(defender, attacker, "On-Half", true, defender.abilities);
    if (defender.thorn > 0) deal(attacker, defender, defender.thorn);
  }
  function doSpecial(ent, foe, t) {
    events.push([t, ent.name === "player" ? "P" : "M"]);
    const sp = ent.abilities.filter(a => a.lane === "Special");
    if (sp.length) sp.forEach(a => applyAb(a, ent, foe, "Special"));
    else { ent.cur_abil = []; deal(foe, ent, Math.max(1, ent.burst_atk + ent.atk_bonus - foe.armor)); }
    ent.specials++;
  }
  function stepE(ent, foe, t) {
    const entry = ent.sequence[ent.seq_idx];
    ent.seq_idx = (ent.seq_idx + 1) % ent.sequence.length;
    ent.cur_abil = ent.abilities.concat(entry.abil || []);
    hitE(ent, foe, entry.atk + ent.atk_bonus);
    ent.agauge += entry.chg;
    if (ent.agauge >= ent.maxag && foe.hp > 0 && ent.hp > 0) { ent.agauge = 0; doSpecial(ent, foe, t); }
    ent.cur_abil = ent.abilities;
  }

  fire(p, e, "On-Start", true, p.abilities);
  fire(e, p, "On-Start", true, e.abilities);
  let t = 0;
  const history = [[0, p.hp, p.dfs, e.hp, e.dfs]];
  const snap = () => history.push([t, r1(p.hp), r1(p.dfs), r1(e.hp), r1(e.dfs)]);
  while (t < SIM.tickLimit && p.hp > 0 && e.hp > 0) {
    t++;
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
           psp: p.specials, msp: e.specials, history, events, notes: [...notes] };
}

// ---- sandbox UI ----
const sb = { seq: [], monster: SIM.morder[0] };
const RARITIES = ["Common", "Rare", "Epic", "Legend", "Mythic"];

function renderPool() {
  $("#wpool").innerHTML = RARITIES.map(rar => {
    const ws = Object.values(SIM.weapons).filter(w => w.rar === rar);
    if (!ws.length) return "";
    return `<div class="rgroup"><div class="rname">${rar.toUpperCase()}</div>` +
      ws.map(w => `<span class="wchip${sb.seq.includes(w.name) ? " inseq" : ""}" data-w="${w.name}"
        title="ATK ${w.atk} · DEF ${w.dfs} · SPD ${w.spd} · Chg ${w.chg}">${w.name}</span>`).join("") + `</div>`;
  }).join("");
  $("#wpool").querySelectorAll(".wchip").forEach(ch => ch.onclick = () => {
    if (sb.seq.length >= 3) return;
    sb.seq.push(ch.dataset.w); refreshSandbox();
  });
}
function renderSeq() {
  $("#wseq").innerHTML = sb.seq.length
    ? sb.seq.map((n, i) => `<span class="sqchip" data-i="${i}" title="คลิกเพื่อเอาออก">${i + 1}. ${n} ✕</span>`).join("")
    : `<span style="color:var(--muted)">— ว่าง —</span>`;
  $("#wseq").querySelectorAll(".sqchip").forEach(ch => ch.onclick = () => {
    sb.seq.splice(+ch.dataset.i, 1); refreshSandbox();
  });
}
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
}
function refreshSandbox() { renderPool(); renderSeq(); renderStats(); runSandbox(); }
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
  $("#clearSeq").onclick = () => { sb.seq = []; refreshSandbox(); };
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
renderPool(); renderSeq(); renderStats();
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
