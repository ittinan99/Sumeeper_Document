# Sumeeper Combat Sim — คู่มือสำหรับทีม balance

เครื่องมือจำลองการต่อสู้ อ่านค่าจากชีตจริงใน `game_document/` โดยตรง — แก้ตัวเลขในชีต แล้วรันดูผลได้เลย ไม่ต้องแก้โค้ด

## วิธีใช้ (สั้นที่สุด)

1. แก้ค่าในชีต (`Sumeeper_Monster_Sheet.xlsx` / `Sumeeper_Equipment_Sheet.xlsx`) แล้ว **Save**
2. ดับเบิลคลิก **`run_report.bat`** — รายงาน `sim_report.html` จะเปิดในเบราว์เซอร์เอง
3. ดูผล: ช่องไหนมี **✱ = ผลแพ้ชนะพลิกจากค่าอ้างอิง** และการ์ด "เทียบกับค่าอ้างอิง" จะไล่ให้ว่าแก้ stat ตัวไหนไปบ้าง

ต้องมี Python + `openpyxl` ในเครื่อง (ถ้ายังไม่มี: `pip install openpyxl`)

## ในรายงานมีอะไรบ้าง

| ส่วน | ใช้ทำอะไร |
| --- | --- |
| แถบสรุปบนสุด | จำนวนชัยชนะของ build ตัวแทน 3 สาย + จำนวนคู่ที่ผลพลิกจาก ref |
| เทียบกับค่าอ้างอิง | ลิสต์ stat ทุกตัวที่ต่างจาก ref (monster และ equipment) |
| Combat Viewer | ดูไฟต์เล่นเป็นฉากทีละ tick — เห็นจังหวะ rotation, Special, DEF แตก (ปรับความเร็ว x1–x8) |
| Sandbox | จัดชุดอาวุธ 0–3 ชิ้น + เลือกมอนสเตอร์เอง ผลรันทันทีในเบราว์เซอร์ |
| Heatmap | ผลทุกคู่ (18 มอนสเตอร์ × 3 builds) — น้ำเงิน=ผู้เล่นชนะ แดง=มอนสเตอร์ชนะ ยิ่งเข้มยิ่งขาด, คลิกเพื่อเปิด Viewer + กราฟ |
| กราฟ timeline | HP/DEF ราย tick ของไฟต์ที่เลือก แยกสองแผง |
| ตารางท้ายหน้า | ข้อมูลดิบทุกคู่ copy ไปใช้ต่อได้ |

## ค่าอ้างอิง (reference)

- `reference_baseline.json` + โฟลเดอร์ `reference/` (สำเนาชีตเต็ม) คือ **ชุดค่าที่ทีม sim จูนไว้เป็นแนวทาง** — รายงานทุกครั้งจะเทียบกับชุดนี้อัตโนมัติ
- ถ้าจูนจนพอใจและอยากตั้งค่าชุดใหม่เป็นฐาน: ดับเบิลคลิก **`make_reference.bat`** (ชุดเก่าจะถูกทับ — ถ้าอยากเก็บให้ copy โฟลเดอร์ `reference/` ออกไปก่อน)
- การเทียบครอบคลุมเฉพาะ stat (HP/ATK/DEF/SPD/Charge) — การแก้ ability ยังไม่ถูกลิสต์ในการ์ด diff แต่มีผลใน sim ตามปกติ

## เป้าหมายของค่าอ้างอิงชุดนี้ (แนวทางที่ทีม sim ใช้ตอนจูน)

1. ทุกมอนสเตอร์ต้องแพ้ให้ build ตรง tier **อย่างน้อย 1 ใน 3** — ห้ามมี wall ที่ตันทุกทาง
2. โค้งความยาก: T1 เป็นมิตร → T2–T3 สูสี → T4 ยาก (แพ้เฉพาะสายที่ถูกทาง) → บอส T5 ชนะได้แบบเฉียดฉิว
3. ไม่มี TIMEOUT (การต่อสู้ต้องจบเสมอ — เกมเป็น watch-only) และไฟต์ฝั่งชนะไม่ควรจบเร็วกว่า ~10 tick
4. ทั้งสาม archetype (Heavy/Rush/Balance) ต้องมีเขตที่ตัวเองเก่งที่สุด

## แก้ปัญหาที่เจอบ่อย

- **รันแล้ว error เรื่องค่า HP ว่าง** → เปิด Monster Sheet ใน Excel กด Save หนึ่งครั้ง (สูตรยังไม่ถูกคำนวณ) หรือพิมพ์เลขลงเซลล์ตรงๆ
- **แก้ชีตแล้วผลไม่เปลี่ยน** → เช็กว่ากด Save ไฟล์แล้ว และดูบรรทัด "แก้ล่าสุด" ใต้หัวรายงานว่าตรงกับเวลาที่แก้จริง
- **คอลัมน์ Combat Power ในชีตไม่อัปเดต** → เป็นสูตร Excel ต้องเปิดไฟล์ให้ Excel คำนวณ — sim ไม่ได้ใช้คอลัมน์นี้ (อ่าน stat ดิบ) ผลจึงถูกเสมอ
- มอนสเตอร์ที่ใช้ ability สาย **Convert/Eater** ยังไม่ถูกจำลอง — ดูรายชื่อท้ายรายงานบรรทัด NOT SIMULATED

## สรุปกติกา combat (ความเข้าใจร่วมของทีม — ฉบับเต็มอยู่ใน GDD หัวข้อ Auto battle / Damage Calculate)

### ค่าพลังและ loadout

- base stat ตัวเริ่มต้น: **HP 10 / ATK 1 / DEF 0 / SPD 1 / Charge 1 / Max Special Gauge 2** — คงที่ตลอด run (ไม่มีเลเวล) ขยับได้ด้วย Perk; Max HP เพิ่มจาก Recipe เท่านั้น (Equipment เพิ่ม Max HP ได้เฉพาะผ่าน ability เช่น `Gain MAX HP`)
- ผู้เล่นเลือก Equipment **0–3 ชิ้น** จากที่ถือสูงสุด 6 จัดลำดับเป็น Action Sequence ได้เฉพาะช่วง Pre-Combat; ไม่เลือกเลยก็เข้า combat ได้ (ตีด้วย base stat ล้วน)
- **ค่าราย action = base stat + stat ของชิ้นนั้น** ทั้ง ATK/SPD/Charge — บวกกันเสมอ ไม่มีการแทนที่ ดังนั้น**ค่าจริงในเกม = ค่าในชีต + base** และการอัปเกรด base stat ส่งผลกับทุก action
- **DEF เป็น stat เดียวที่รวมจากทั้ง loadout**: หลอด DEF = base DEF + Σ DEF ทุกชิ้นที่เลือกเข้า combat

### จังหวะการต่อสู้ (per-action rotation)

- สมาชิกใน sequence เป็น **active ทีละหนึ่งตำแหน่ง** — Speed Gauge เติมด้วยอัตรา base SPD + SPD ของชิ้น active (+ โบนัส SPD จาก ability) **ขั้นต่ำ 1 เสมอ** (การันตีว่า rotation ไม่มีทางค้าง — เกม watch-only ห้ามมี state ที่ไม่เดินหน้า)
- เมื่อ Speed Gauge เต็ม: ชิ้น active โจมตี 1 ครั้ง → Special Gauge เพิ่ม (base Charge + Charge ชิ้นนั้น) → เลื่อนให้ชิ้นถัดไปเป็น active; **เศษ Speed Gauge ทบไปรอบถัดไป** (ต่างจาก Special Gauge ที่ทิ้งส่วนเกิน)
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

### Trigger / Keyword / Special

- Trigger: **On-Start** (เริ่ม combat) / **On-Hit** (ผู้ตี ทุก action) / **On-Damaged** (ผู้ถูกตี ทุกครั้งที่โดน) / **On-Half** (ครั้งเดียว เมื่อ HP ตกถึงครึ่ง) / **On-Exposed** (ครั้งเดียว เฉพาะเมื่อ DEF เปลี่ยนจาก >0 เป็น 0 — เริ่ม combat ที่ 0 อยู่แล้วไม่ยิงตลอดไฟต์) / **Special** / Death / Passive
- **ไม่จำลอง On-Action** — engine ของเกมมี trigger นี้แยกจาก Special (ยิงตอน tick ปกติ ก่อนดาเมจ และแทนที่การโจมตีได้) แต่ดีไซน์ยืนกติกา "ทุก action โจมตีเสมอ" และไม่มีข้อมูลชิ้นไหนใช้ทางแทนที่จริง sim จึงตีทุก tick ตรงตามกติกา — ดูหัวข้อ *On-Action vs On-Hit vs Special* ใน GDD ถ้าวันไหนกติกาเปลี่ยน ต้องแก้ engine ทั้งสองตัวพร้อม GDD
- "Shield" เป็นคำเก่า = **Armor**; **Fury** นิยามไว้ใน GDD แต่ยังไม่มีของชิ้นไหนใช้และ sim ยังไม่รองรับ
- Special Gauge มี MaxSG ช่อง (คงที่ต่อตัวละคร ขยับด้วย Perk ไม่ผันตาม loadout) — เต็มแล้วใช้ Special ทันที รีเซ็ตเป็น 0 ทิ้ง Charge ส่วนเกิน
- Special พื้นฐานของผู้เล่น = **burst โจมตี 1 ครั้ง** ค่า = Σ ATK ราย action ของทุกชิ้นใน loadout — โดน Armor หักครั้งเดียว ติด floor 1 กินหลอด DEF ตามปกติ; Primary Perk บางสาย Replaces Special; Feast ส่วนใหญ่มี Special ของตัวเอง

## โครงชีตและสูตร Combat Power

**`Sumeeper_Equipment_Sheet.xlsx`** — แท็บ: `Equipment` (stat + คอลัมน์คำนวณ Sum/Ability Value/Combat Power), `Ability` (1 แถวต่อ ability: Trigger/Verb/Target/Magnitude/lane), `Weights` (ปุ่มจูนทั้งหมด), แท็บ pool ราย rarity, `Forge Scaler`

ระบบ budget: `CP = Σ(stat × stat-weight) + Charge × charge-weight + Σ(Trigger-w × Verb-w × Magnitude-w × Target-w)` ต่อ ability — จูนให้ CP ≈ ค่าฐานของ rarity ใน `Weights` (Common 6 / Rare 9 / Epic 13 / Legend 17 / Mythic 22) อย่าลืมว่าค่าจริงในเกม = ค่าชีต + base

**`Sumeeper_Monster_Sheet.xlsx`** — แท็บ: `Monsters Config` (base ราย monster — **DEF/SPD ใช้จริง**, HP/ATK เป็น legacy), `Feast` (rollup: เซลล์ **ค่า** HP กับ Max SG ตั้งด้วยมือ; ส่วนเซลล์สูตร DEF/SPD ที่รวมทุก entry คือโมเดลเก่า sim ไม่ใช้), `Feast Sequence` (ATK/DEF/SPD/Charge ราย action + ability สาย action), `Feast Combat Ability` (ability สาย trigger)

## สำหรับคนแก้โค้ด

- Engine หลัก: `sumeeper_combat_sim.py` (กติกาย่อ + assumption ประกาศไว้ใน docstring บนสุด) — build ตัวแทนอยู่ท้ายไฟล์ตัวแปร `BUILDS`
- ⚠️ ใน `sumeeper_sim_report.py` มี **engine ฉบับ JS** (`runFight`) สำหรับ Sandbox/Viewer — แก้กติกา combat ต้องแก้ทั้งสองที่แล้วเช็ก parity (หน้ารายงานเช็กเองได้: ทุกช่อง heatmap ที่รันซ้ำด้วย JS ต้องตรง python 54/54)
- สเปกกติกาฉบับเต็ม: `game_document/Sumeeper_GDD.md` หัวข้อ Auto battle / Damage Calculate (GDD เป็น canonical เสมอ)
