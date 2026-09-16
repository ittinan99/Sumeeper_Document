# ข้อเสนอออกแบบ : ระบบ Quest (คำเรียกร้อง) — 2026-09-11 · rev.3 (2026-09-16)

ต่อยอดจาก `game_document/proposals/QuestReward_Review_2026-09-09.md`
สถานะ : **ข้อเสนอที่ผ่านการเคาะทิศทางกับผู้ตัดสินแล้ว** (ตารางข้อ 1) — ตัวเลข balance ทุกตัวยังว่างรอคนจูน
**ยังไม่ได้เขียนลงชีตและยังไม่ได้แก้ GDD** — รายการที่ต้องแก้ใน GDD รวมไว้ที่ข้อ 13

rev.2 เพิ่มจาก rev.1 : สาย spine 8 ใบ · กระดานแบบ generate · Curse Contract ย้ายไปหลัง main quest · curse ประจำชั้น · วัตถุดิบพิเศษผูกกับ variant · BossThreatRecord key ด้วยบอส · การ์ดก่อนปลด Contract ไม่แสดงเรื่องคลัง
rev.3 เพิ่ม : ตัดสินข้อ 24–29 (บันได · ชั้นว่าง · native curse 3 ใบ · ลูกค้า · บอส 3 ระยะ · Curse Gauge รีเซ็ตต่อชั้น) · แก้นิยาม Sugar Garden / Edemia ให้ตรงกับข้อเท็จจริงว่าทุกช่องมี cover · จัดรายการ "ต้องฟัน" ใหม่ (ข้อ 14)
rev.3.1 (09-17) : ข้อ 30 วัตถุดิบธรรมดา 5 แบบ · ข้อ 31 D10 = แก้ GDD อย่างเดียว · ขยาย D5 (SoftCurrency คืออะไร) · D7 ชี้ขอบเขต = Unity/ชีต ไม่ใช่ GDD · D9 นิยามใหม่เป็นหน้า Collections (codex + จ่าย coin) บนโครง `GameMenu` ที่มีอยู่

---

## 1. สิ่งที่ตัดสินไปแล้ว

### 1.1 โครง quest

| # | ประเด็น | ข้อสรุป |
| --- | --- | --- |
| 1 | quest คืออะไร | **checklist + คำขอพิเศษ** |
| 2 | quest มาจากไหน | **hybrid** : สาย spine (main quest 8 ใบ เขียนมือ) + กระดานออร์เดอร์ (generate ตอน runtime) |
| 3 | คำขอพิเศษบังคับหรือ bonus | **ผสมตามระดับ ★** — ★ ไม่มี · ★★ bonus 1 · ★★★ บังคับ 1 + bonus 1 |
| 5 | จำนวนชั้นต่อ run | **บอส 3 ตัวคงที่ (มาตรฐาน) · ชั้นแปร 3–6** · ออร์เดอร์ฝึกหัด S1–S2 มีบอสน้อยกว่า 3 |
| 7 | ตายกลางดัน | **quest บนกระดานหาย กระดาน refresh** · **quest สาย spine ไม่หาย** (ลองใหม่ได้เรื่อยๆ) |
| 8 | เงื่อนไขบังคับพังกลาง run | **ออร์เดอร์เสีย แต่เล่นต่อได้** — เหลือทาง Extract / ตาย |
| 10 | bonus coin | **ไม่โดนตัวคูณ Threat** บวกท้ายสุด |
| 15 | spine ปลดอะไร | Floor Variant ทีละชั้น + สูตร signature + ตัวละคร · **ของใหม่ทั้งหมดมาจาก spine เท่านั้น** กระดานให้ coin |
| 16 | กระดานเปิดเมื่อไหร่ | **หลังส่ง S2 สำเร็จ** |

### 1.2 ชั้นและ Floor Variant

| # | ประเด็น | ข้อสรุป |
| --- | --- | --- |
| 9 | ชั้นที่ไม่มีบอส | **ช่องบันไดที่ซ่อนในกริด** — ชั้นบอสก็ใช้บันได แต่ล็อกจนกว่าจะฆ่าบอส |
| 11 | ช่องบันไดนับใน `TileOpenedMax` ไหม | **ไม่นับ** — "ทางออกไม่นับ" ช่องอื่นนับหมดรวมช่องบอส |
| 12 | Feast stat scaling | **ถอดตัวคูณ `floor+1` ทิ้ง** ทั้ง stat และค่า Curse Gauge (ข้อ 12) |
| 17 | ตัวตนของ Floor Variant | **แต่ละ variant มี curse ประจำชั้น** (native curse) ที่ทำงานตลอดเวลาที่อยู่ในชั้นนั้น |
| 18 | boss pool | **แต่ละ variant มี boss pool ของตัวเอง** · Feast ทุก Tier ผูกกับ variant |
| 19 | spine กับบอส | **spine ระบุตายตัว** ว่าชั้นไหนเจอบอสตัวไหน · แต่ละ variant เปิดตัวครั้งแรกด้วยบอสที่ยังไม่เคยเจอเสมอ |

### 1.3 วัตถุดิบพิเศษ · Threat · Contract

| # | ประเด็น | ข้อสรุป |
| --- | --- | --- |
| 4 | checklist กับสิทธิ์ของ | **แยกกัน** — checklist ติ๊กเสมอเมื่อล้มบอส · การเข้าคลังมีเงื่อนไข |
| 6 | วัตถุดิบพิเศษ | **เก็บสะสมข้าม run ได้** (คลัง) ใช้ปลดล็อคทีหลัง |
| 20 | ชนิดของวัตถุดิบพิเศษ | **ผูกกับ variant** — บอสทุกตัวใน variant เดียวกัน drop ชนิดเดียวกัน |
| 21 | BossThreatRecord key ด้วย | **บอส** (ตาม GDD) — บอสใหม่ของ variant เดิม = แหล่งของใหม่ |
| 22 | การ์ดก่อนปลด Contract | **ไม่แสดงเรื่องคลังเลย** — แสดงแค่ "จาน" ที่ลูกค้าขอ · ของที่เข้าคลังโผล่เป็นบรรทัดโบนัสใน Run Result เท่านั้น |
| 23 | Curse Contract อยู่ตรงไหน | **หลัง main quest** — ปลดเมื่อส่ง S8 สำเร็จ · **คำขอพิเศษ = บันไดของ campaign · Contract = บันไดของ endgame** |
| 13 | Contract ทำให้ Feast แข็งขึ้นได้ไหม | **ได้ ผ่าน curse ใบหนึ่งใน pool ของ Contract** ไม่ใช่คุณสมบัติของเลข Pre-run Threat |
| 14 | เพดาน Pre-run Threat | **เตี้ย 3–5 ระดับ** |

### 1.4 ตัดสินเพิ่ม 2026-09-16

| # | ประเด็น | ข้อสรุป |
| --- | --- | --- |
| 24 | ช่องบันได | **1 ช่องต่อชั้น** · ชั้นบอส : เผยอัตโนมัติเมื่อบอสตาย · ชั้นว่าง : ซ่อน + ช่องรอบข้างมี**เครื่องหมายเฉพาะ**แยกจากเลข Feast · Hint encounter เผยตำแหน่งได้ |
| 25 | ชั้นว่าง | **กริดเล็กกว่า ~60–70%** · ความหนาแน่น encounter เท่าเดิม · เป็น variant ของ**ชั้นบอสถัดไป** (ทางเข้าสู่บอส) ใช้ native curse ของมัน |
| 26 | native curse 3 ใบใหม่ | นิยามตามข้อ 6.1.1 — หลักร่วม : **ข้อมูลถูกบิด แต่ความจริงรั่วทางเลขใบ้เสมอ** |
| 27 | ลูกค้า | **flavor ล้วน** แต่ใส่ `CustomerId` ตั้งแต่วันนี้ |
| 28 | บอส | **3 ระยะ** : MVP 3 (map บอสเดิมเข้า variant ต้นเกมชั่วคราวด้วยข้อมูล) → campaign 6 → กระดาน ≥12 |
| 29 | Curse Gauge | **รีเซ็ตต่อชั้นตาม GDD** · จำนวน threshold เป็นคุณสมบัติของชั้น (`FloorLayout`) · ชั้นเล็ก threshold น้อย · In-run Threat ไม่รีเซ็ต · เกจที่เหลือตอนจบชั้นสูญเปล่า (ไม่ยกยอด) |
| 30 | วัตถุดิบธรรมดา (09-17) | **สุดท้ายจะมี 5 แบบ** (ตอนนี้ชีตมี 3 แบบหลักใน recipe) → ถ้า recipe ยังเป็น combination ครบชุด : คู่ 15 + สาม 35 = **50 สูตร** (จาก 16) — ทำให้ D1(ก) แข็งขึ้น เพราะมีสูตรพอให้ spine/coin ปลดทีละชุด · `MaterialCarryMax/Min` มี TargetId เพิ่มเป็น 5 |
| 31 | D10 (09-17) | **แก้ GDD อย่างเดียว ยังไม่แตะชีต** — D5/D7 ตัดสินได้เลยแต่ลงมือตอนเฟสชีต/โค้ด |
| 32 | D1–D9 (09-17) | **เห็นด้วยตามคำแนะนำทั้งหมด** : D1 spine ปลดสูตรธรรมดา (วัตถุดิบพิเศษไม่แตะ Cook) · D2 Extract ที่ Floor Result เท่านั้น · D3 บทเรียน Extract ย้ายไป S2 · D4 ตายแล้วของยังเข้าคลัง · D5 ถอด SoftCurrency หีบให้ Fath · D6 rename เฉพาะ critical path · D7 retire config ตามตาราง · D8 native 3 ใบ = Both ที่เหลือ = Gauge · D9 Collections บนโครง GameMenu · **GDD merge เริ่ม 09-17** |
| 33 | Meal (09-17 — นอกขอบเขต quest แต่ merge ลง GDD แล้ว) | **อาหารทุกจานเข้า meal inventory เสมอ** (ทำเอง + ซื้อจาก Merchef) · **เปิด inventory และกินได้จาก 3 ที่ : กริด · Cook · Pre-Combat** · ระหว่าง combat กินไม่ได้ · GDD Shop "ซื้อแล้วกินเลย" ถูกแก้ · **โค้ดตรงแล้ว 2 ใน 3** — cook → inventory (`LifetimeScope/GameplayPresenter.cs:41,55`) · shop → inventory + เช็คช่องเต็ม (`StateMachine/Gameplay/ShopGameplayState.cs:216-232`) · **ขาด : Pre-Combat ยังไม่มีทางเปิด `UIInventory`** (grep ใน `CombatGameState` / UI Combat ไม่พบ) |

---

## 2. แนวคิดหลัก

**Quest = ออร์เดอร์อาหารจากลูกค้า** การ์ดหนึ่งใบมี 3 ชั้น

| ชั้น | คืออะไร | หน้าที่ |
| --- | --- | --- |
| **จานหลัก** | วัตถุดิบพิเศษ 3 ชิ้นจากบอส 3 ตัว (3 variant) | กำหนดว่า run นี้ไปชั้นไหน เจอบอสอะไร → เตรียม build ล่วงหน้าได้ |
| **คำขอพิเศษ** | เงื่อนไขวิธีเล่น 0–2 ข้อ | **ตัวที่ทำให้ run แต่ละครั้งต่างกันจริง** |
| **ลูกค้า** | ชื่อ + คำพูด + ของที่ปลดล็อคเมื่อส่งสำเร็จ | ให้ progression มีหน้าตา (flavor ยังไม่มีระบบ reputation) |

**ปัญหาที่โครงนี้แก้** : quest แบบเดิม ("เก็บของจากบอส 3 ตัว") เป็น *รายชื่อชั้น* ไม่ใช่ quest — ไม่แตะการตัดสินใจใดในดันเจี้ยนเลย ทั้งที่การตัดสินใจจริงอยู่ในดันทั้งหมด ชั้น "คำขอพิเศษ" คือสะพาน

**หลักที่ถือตลอด** : ★ สื่อว่า **"มัดมือผู้เล่นแค่ไหน"** ไม่ใช่ "ดันเจี้ยนยากแค่ไหน" — ความแรงของศัตรูมาจาก In-run Threat (Curse Gauge) และ curse ที่เลือกเองใน Contract เท่านั้น

**เทียบกับ Monster Hunter World** (ผู้ตัดสินยกมา) : spine ≈ Assigned quest · กระดาน ≈ Investigation · คำขอพิเศษกลุ่ม build ≈ Arena — แต่ **ต่างกันตรงบันไดความยาก** : MHW ใช้ main quest เป็นบันได (LR→HR→MR มอนสเตอร์แข็งขึ้น) ส่วน Sumeeper ตัดสินแล้วว่า Feast ไม่โตตาม progression บันไดของเราคือ Contract หลังจบเรื่อง ซึ่งใกล้ Hades (Heat) / Slay the Spire (Ascension) มากกว่า

---

## 3. โครง quest

### 3.1 สาย spine — main quest 8 ใบ (เขียนมือ)

**หน้าที่สามอย่างพร้อมกัน** : บทเรียน (แต่ละใบแนะนำระบบใหม่ทีละหนึ่ง) · ประตูปลด Floor Variant · **ลำดับ implement** (ข้อ 11)

| # | ชื่อ | ★ | บอส / ชั้น | แนะนำระบบอะไร | ปลดล็อค |
| --- | --- | --- | --- | --- | --- |
| S1 | ซุปเห็ดหม้อแรก | ★ | 1 / 1 | กริด · combat · **ช่องบันได** · Run Result · coin · กลับกิลด์ | Sugar Garden · **Cook** |
| S2 | ของหวานหลังมื้อ | ★ | 2 / 3 | **Curse Gauge + เลือก curse 1 จาก 2** · ชั้นว่าง · **Extract** (quest แรกที่มี Floor Result — D3) | Abyssalt · สูตรใบแรก · **กระดานเปิด** |
| S3 | สำรับสามจาน | ★ | 3 / 3 | รูปแบบมาตรฐาน · checklist เต็ม | Capsaicia |
| S4 | จานเผ็ดที่สุดในเมือง | ★★ | 3 / 4 | **คำขอพิเศษใบแรก** (bonus ล้วน ทำไม่ได้ก็ไม่เสียหาย) | Umamia · ตัวละครที่ 2 |
| S5 | ออร์เดอร์เงียบ | ★★★ | 3 / 5 | **เงื่อนไขบังคับใบแรก + สถานะออร์เดอร์เสีย** | Edemia |
| S6 | สองคำขอ | ★★★ | 3 / 5 | บังคับ 1 + bonus 1 พร้อมกัน | สูตรระดับสูง |
| S7 | ครัวปิดตีสาม | ★★★ | 3 / 6 | เงื่อนไขบังคับที่ตีกับ Curse Gauge โดยตรง | ตัวละครที่ 3 |
| S8 | สำรับของหัวหน้ากิลด์ | ★★★ | 3 / 6 | บทสรุป | **The Curse Contract + Threat ladder** (ข้อ 8) |

**จังหวะปลด variant โตพร้อมจำนวนบอสที่ quest ขอ** — เริ่มเกมมี Myceland เดียว S1 ขอบอสเดียว → S1 ปลด SG → S2 ขอ 2 → S2 ปลด Ab → S3 ขอ 3 ครบมาตรฐาน ไม่มีช่วงไหนที่ของไม่พอ

**กติกาของสาย spine**
- เล่นตามลำดับ (`UnlockType = QuestCompleted`) แต่ไม่บังคับเล่นติดกัน — สลับไปเก็บ coin จากกระดานได้ตลอด
- ตายแล้วไม่หาย (ข้อยกเว้นของการตัดสินข้อ 7)
- เล่นซ้ำได้เพื่อ coin แต่ไม่ได้ unlock ซ้ำ — ขึ้น ✓ ในแท็บ "ออร์เดอร์ประจำร้าน"
- **บอสระบุตายตัวทุกใบ** · ทุก variant เปิดตัวครั้งแรกด้วยบอสที่ยังไม่เคยเจอ · หลังจากนั้นซ้ำได้ (ช่องบอสใน spine มี 21 ช่อง ไม่ซ้ำเลยเป็นไปไม่ได้ และภายใต้ข้อ 22 การซ้ำไม่ทำร้ายอะไร)
- ลูกค้าวนซ้ำ 3–4 คน ไม่ใช่ 8 คน 8 ใบ (ยายช่างเย็บผ้า S1/S6 · หัวหน้ากิลด์ S3/S5/S8 · เจ้าของร้านเหล้า S4 · จดหมายไม่มีผู้ส่ง S7) — ให้รู้สึกเป็นเรื่องเล่า

> ⚠ **S1–S2 ขอวัตถุดิบน้อยกว่า 3 ชิ้น ขัดกับ GDD** ที่เขียนว่า *"คำเรียกร้องจะขอวัตถุดิบสามอย่าง"* — เสนอแก้เป็น **"3 ชิ้นคือรูปแบบมาตรฐาน · ออร์เดอร์ฝึกหัด 2 ใบแรกมีน้อยกว่าได้"** เพราะ run 3 บอสกินเวลา 40+ นาที ยาวเกินไปสำหรับการสอนครั้งแรก

### 3.2 กระดานออร์เดอร์ — generate ตอน runtime

- แสดง **3 ใบ** เลือกได้ 1 · **refresh ทุกครั้งที่จบ run** · reroll ทั้งกระดานเสีย coin *(ราคาให้คนจูน)*
- **ไม่มีแถวในชีต** — ประกอบขึ้นจาก : สุ่มระดับ ★ (ถ่วงตาม progress) → สุ่ม 3 variant จากที่ปลดแล้ว → สุ่มบอสจาก pool ของแต่ละ variant → สุ่มเงื่อนไขจาก `QuestCondition` ที่ตรงระดับ → สุ่มผังชั้นจากช่วงของระดับ → จับคู่ชื่อจาก pool `ลูกค้า × จาน`
- ให้ coin + แถบความคืบหน้าไป unlock ชิ้นถัดไป · **ไม่ให้ unlock ใหม่โดยตรง**
- ก่อนปลด Contract การ์ดแสดงแค่ "จาน" ที่ขอ ไม่แสดงเรื่องคลัง (ข้อ 7.3)

### 3.3 ระดับ ★

| ระดับ | คำขอพิเศษ | จำนวนชั้น | ค่าตอบแทน |
| --- | --- | --- | --- |
| ★ | ไม่มี | 3 | coin ตามสูตร |
| ★★ | bonus 1 | 4–5 | + bonus ก้อน *(ให้คนจูน)* |
| ★★★ | **บังคับ 1** + bonus 1 | 5–6 | + bonus ก้อนใหญ่ |

> ชั้นที่เพิ่มมาไม่ได้ทำให้ยากขึ้น มันทำให้ run **ยาวขึ้นและได้ของเยอะขึ้น** — ไม่ต้องแก้ เพราะของที่ได้เพิ่มไม่ฟรี (ฆ่า Feast → เติมเกจ → ถูกบังคับรับ curse → Feast ที่เหลือแข็งขึ้น)

### 3.4 ผังชั้น

**บอสตัวสุดท้ายอยู่ชั้นสุดท้ายเสมอ · ชั้นว่างแทรกระหว่างชั้นบอสได้** เก็บใน `FloorLayout` — แต่ละช่องระบุชนิดและจำนวน threshold ของ Curse Gauge (ข้อ 29)

| ระดับ | ตัวอย่าง |
| --- | --- |
| ★ | `[B3][B3][B3]` |
| ★★ | `[B3][E1][B3][B3]` |
| ★★★ | `[B3][E1][B3][E1][E1][B3]` |

`B` = ชั้นบอส · `E` = ชั้นว่าง · ตัวเลข = จำนวน threshold *(ค่าจริงให้คนจูน — ตัวอย่างสมมุติ)*

**กติกาของชั้นว่าง** (ข้อ 25) : กริดเล็กกว่า ~60–70% (`MapData` รองรับขนาดต่อชั้นอยู่แล้ว — `MapWide`/`MapHeight`) · ความหนาแน่น encounter เท่าเดิม → เร็วแต่ของแน่นต่อช่อง · objective เดียวคือหาบันได · **variant = variant ของชั้นบอสถัดไป** ดังนั้น `[M][E][SG]` อ่านว่า "ลงสู่ Sugar Garden สำรวจ แล้วเจอบอสของมัน" — ผู้เล่นได้ลอง native curse ก่อนเจอบอส · run 6 ชั้น (3 เล็ก) จึงยาวราว 4.5 ชั้นบอส

---

## 4. คำขอพิเศษ (Special Request)

### 4.1 ต้องเป็นข้อมูล ไม่ใช่ข้อความเขียนมือ

หนึ่งเงื่อนไข = หนึ่งแถว `ConditionType | Comparison | Value | TargetId | IsMandatory | BonusCoin` · ข้อความบนการ์ดมาจาก localization ที่แทนค่า `{value}`

### 4.2 Catalogue

| กลุ่ม | ConditionType | ตัวอย่างข้อความ | หมายเหตุ implement |
| --- | --- | --- | --- |
| **กริด** | `TileOpenedMax` | เปิดช่องรวมไม่เกิน {N} ช่อง (ทางออกไม่นับ) | **เรือธง** · `MapManager.OpenTile(x,y,isPlayerInitiated)` แยกการเปิดของผู้เล่นออกจาก cascade แล้ว (`Map/MapManager.cs:213-219`) · เช็คหลังเปิดว่าเป็นบันไดไหมค่อย increment (`EventOpenTile` ส่ง `TileInfoModel` มาแล้ว บรรทัด 232) |
| | `FlagUsedMax` | ใช้สกิลธงไม่เกิน {N} ครั้ง | `EventTileFlagged` มีแล้ว (`Map/MapManager.cs:26`) |
| **Curse Gauge** | `CurseAcceptedMin` / `Max` | รับคำสาป ≥ / ≤ {N} ใบ | พลิก risk curve ได้ทั้งสองทาง |
| **ทรัพยากร** | `FathRemainMin` | เหลือ Fath ≥ {N} ตอนส่ง | ตีกับ shop / reroll |
| | `MaterialCarryMax` / `Min` | ห้ามมี / ต้องมี {Target} ตอนส่ง | สอนว่าวัตถุดิบไม่แปลงเป็น coin |
| **Cook** | `MealCookedMin` | ทำอาหาร ≥ {N} จาน | ดึง Cook ขึ้นเส้นหลัก |
| | `MealSubmitWith` | ส่งพร้อมเมนู {Target} | |
| **Build** | `EquipmentCarryMax` | ถือ equipment ไม่เกิน {N} ชิ้น | |
| | `HpRemainMinPercent` | ส่งโดย HP ≥ {N}% | |
| | `NoShopPurchase` | ห้ามซื้อของจากร้าน | |

### 4.3 เงื่อนไขบังคับพังกลาง run → ออร์เดอร์เสีย แต่ run ไม่จบ

ไม่ใช่สถานะใหม่ — แค่ **ปิดประตูทางออกที่ ① (ส่งสำเร็จ) เหลือ ② Extract กับ ③ ตาย** ซึ่ง GDD รองรับอยู่แล้ว
- การ์ดบน HUD เปลี่ยนเป็นสีเทา + *"ออร์เดอร์เสียแล้ว — ยังเก็บของกลับได้"* · ปุ่ม Extract ที่ Floor Result เด่นขึ้น
- ยังล้มบอส เก็บ Fath เก็บของเข้าคลังได้ตามปกติ

**เหตุผล** : เปลี่ยนความผิดพลาดให้เป็นการตัดสินใจ — ถ้าพังแล้วจบ run ทันที ผู้เล่นจะเลิกแตะ ★★★

### 4.4 UX

**เงื่อนไขที่มีเพดานทุกข้อต้องมีตัวนับบน HUD ตลอดเวลา** (`เปิดแล้ว 38/45`) — ตรง `Sumeeper_UX_Screens.md` ข้อ 0 / 3

---

## 5. เงื่อนไขผ่านชั้น : ช่องบันได

**ทุกชั้นใช้โครงเดียวกัน — หา "ช่องบันได" ที่ซ่อนในกริด** · ชั้นบอส : บันไดล็อกจนกว่าจะฆ่าบอส · ชั้นว่าง : เปิดได้ทันทีที่เจอ

**ทำไม** : ทุกชั้นมีเป้าหมายที่ซ่อนในกริดเหมือนกัน เป็น minesweeper แท้ๆ และเข้าคู่กับ `TileOpenedMax` — ยิ่งอ่านเลขเก่ง ยิ่งเหลือโควตาไปเปิดหาของ · ตรงกับ `IFloorClearCondition` ที่เสนอในรายงาน 09-09

**บันไดไม่นับใน `TileOpenedMax`** — ผู้เล่นไม่ควรถูกลงโทษจากการหาทางออก ไม่งั้นผังที่สุ่มแล้วบันไดอยู่ไกลจะกลายเป็นการลงโทษที่ควบคุมไม่ได้

### 5.1 กติกาบันได (ตัดสินแล้ว — ข้อ 24)

| | ชั้นบอส | ชั้นว่าง |
| --- | --- | --- |
| จำนวน | 1 | 1 |
| ก่อนบอสตาย / ก่อนหาเจอ | ซ่อน | ซ่อน · **ช่องรอบข้างมีเครื่องหมายเฉพาะ** (ไม่ใช่เลข ไม่รวมกับเลข Feast) |
| เผยเมื่อ | **บอสตาย → โผล่บนกริดอัตโนมัติ** และปลดล็อกทันที | ผู้เล่นเปิดเจอ |
| objective ซ่อนของชั้น | บอส (1 อย่าง) | บันได (1 อย่าง) |

**หลัก : บันไดต้องหาเจอด้วยฝีมือ ไม่ใช่โชค** — ถ้าบันไดไม่ส่งสัญญาณ การหาคือเปิดช่องปลอดภัยไปเรื่อยๆ ซึ่งทำให้ `TileOpenedMax` กลายเป็นการโยนเหรียญ · แต่**ห้ามรวมบันไดเข้าเลข Feast** ไม่งั้นตรรกะการอ่านเลขพัง → แยกเป็นสองช่องทางข้อมูล : เลขบอก "อันตรายรอบตัว" · เครื่องหมายบอก "ทางออกอยู่ใกล้" · ชั้นบอสไม่ต้องหาสองรอบ (หาบอสแล้วหาบันไดอีก) จึงเผยให้เลย

**Hint encounter (Flavour Prophet)** ควรมีตัวเลือก "เผยตำแหน่งบันได" — ได้ของฟรีจากระบบเดิม

---

## 6. Floor Variant — ตัวตนเชิงกลไก

### 6.1 curse ประจำชั้น (native curse)

**แต่ละ variant มี curse ที่ทำงานตลอดเวลาที่อยู่ในชั้นนั้น** — และ lore ใน GDD หัวข้อ Floor Variant เขียนกติกาไว้ให้แล้วครึ่งหนึ่ง

| variant | ประโยคใน GDD | กติกา | สถานะโค้ด |
| --- | --- | --- | --- |
| **Myceland** | *"ละอองคำสาปล่องลอยอยู่ในอากาศ ส่งผลให้การมองเห็นคลาดเคลื่อน"* | เลขใบ้เพี้ยน | = `minus-shifter` มีแล้ว |
| **Sugar Garden** | *"ยิ่งดูน่ากิน ยิ่งอันตราย … พลาดท่าเพราะเชื่อในรูปลักษณ์"* | เลขใบ้นับ Feast ทุกตัวเป็น 1 ไม่ว่า Tier ไหน (รู้ว่ามี ไม่รู้ว่าแรง) | ใหม่ |
| **Abyssalt** | *"ซุ่มในความมืด โจมตีเมื่อเป้าหมายเข้ามาในระยะ"* | ระยะ taunt กว้างขึ้น | = `ignore-me` มีแล้ว |
| **Capsaicia** | *"ยิ่งพื้นที่ที่ถูกสำรวจมาก ความดุร้ายยิ่งรุนแรง"* | เปิดช่องเยอะ = Feast แรงขึ้น | ใหม่ (GDD เขียนเป็นกติกาอยู่แล้ว) |
| **Umamia** | *"ดูดซับพลังงานออกจากทุกอย่าง … ทั้งอาหารที่นำเข้ามา"* | อาหารฟื้นน้อยลง | = `meal-of-fatigue` มีแล้ว |
| **Edemia** | *"ไม่มีทางรู้ว่าอันไหนเป็นผลไม้จริง อันไหนรอวันฟัก"* | หีบบางใบเป็นไข่ — เปิดช่องเห็นเป็นหีบ กดรับของแล้วฟักเป็น Feast | ใหม่ |

**ทำไมสำคัญ** : ตอนถอดตัวคูณ `floor+1` (ข้อ 12) ปัญหาคือ "ชั้น 6 = ชั้น 1 ถ้า roster เหมือนกัน" — curse ประจำชั้นแก้ตรงจุดกว่าการถ่วง Tier เพราะชั้นต่างกันเพราะ **เล่นไม่เหมือนกัน** ไม่ใช่เพราะเลขสูงกว่า · Floor Variant เลิกเป็นแค่ธีมอาร์ต · และผู้เล่นจะรู้จัก curse เหล่านี้ก่อนถึง Contract (ข้อ 8) — เซ็นสัญญา = พาบรรยากาศของชั้นนั้นติดตัวไปทั้ง run

**กติกาสามข้อที่ต้องถือ**
1. **ไม่นับเป็น In-run Threat** — มันคืออากาศของชั้น ไม่ใช่คำสาปที่เลือกรับ ถ้านับ Feast จะ scale ตามชั้นอีก = `floor+1` กลับมาในคราบใหม่
2. **ต้องเห็นก่อนลงชั้น** — UX ข้อ 5 บังคับไว้แล้ว (*"กติกาพิเศษของชั้นนั้น"*)
3. **เวอร์ชันประจำชั้นเบากว่าเวอร์ชันในสัญญา** — id เดียวกัน คนละ stack

#### 6.1.1 นิยาม native curse 3 ใบใหม่ (ข้อ 26)

**ข้อเท็จจริงที่บังคับรูปแบบ** : ทุกช่องมี cover จนกว่าจะเปิด (`Map/Generator/MapGenerator.cs:104-108`) — Feast, หีบ, encounter **มองไม่เห็นก่อนเปิดทั้งหมด** ดังนั้น "ปลอมตัวบนช่อง" ทำไม่ได้ การบิดข้อมูลต้องเกิดที่**เลขใบ้**หรือ**หลังเปิดแล้ว**เท่านั้น

**หลักร่วม** : ข้อมูลถูกบิด แต่ความจริงรั่วทางเลขใบ้เสมอ — คนอ่านเลขละเอียดจับพิรุธได้ คนเปิดมั่วโดน · ต่างจาก `minus-shifter` (Myceland) ที่บิด*ตัวเลขเอง*

| variant | ชื่อเสนอ | กติกา | พิรุธที่รั่ว | ถอยได้ไหม | ค่าคนจูน |
| --- | --- | --- | --- | --- | --- |
| **Sugar Garden** | หน้าตาเหมือนกันหมด | เลขใบ้นับ Feast ทุกตัวเป็น **1** ไม่ว่า Tier ไหน (ปกติเลขสะท้อน Tier) · Tier จริงเห็นที่ Pre-Combat | รู้*ตำแหน่ง*ครบ แต่ไม่รู้*ความแรง* — ต้องเดาจาก pattern/ตำแหน่ง | ได้ (จ่าย STA) — "พลาดท่าเพราะเชื่อรูปลักษณ์" คือจ่าย STA ถอย | — (on/off) · stack สำหรับ Contract ให้คนจูนนิยาม |
| **Capsaicia** | ยิ่งเปิดยิ่งดุ | ทุก {X} ช่องที่ผู้เล่นเปิดในชั้นนี้ Feast ทุกตัวในชั้น ATK +{Y}% · มิเตอร์ "ความร้อน" บน HUD | มิเตอร์เห็นตลอด — ไม่ซ่อน | — | X, Y |
| **Edemia** | ไข่ในหีบ | Item encounter {N}% เป็นไข่ · **เลขใบ้รอบมันนับเป็น Feast ตั้งแต่ก่อนเปิด** · เปิดช่องเห็นเป็นหีบปกติ · กด "รับของ" = ฟัก → Pre-Combat · ทิ้งหีบไว้ไม่แตะได้ | หีบที่เลขรอบข้าง "บวกไม่ลงตัว" ถ้าไม่นับมันเป็น Feast | ได้ | N · Tier ของ Feast ที่ฟัก |

**ข้อควรระวัง** : Sugar Garden กับ Edemia **ต้องเผยตัวจริงที่ Pre-Combat** (ไม่ใช่ตอนเข้า combat) ไม่งั้นละเมิด "การตัดสินใจทั้งหมดอยู่ Pre-Combat" · Capsaicia **ต้องรีเซ็ตเมื่อออกจากชั้น** และ**ไม่นับ In-run Threat** ไม่งั้นคือ scaling สะสมอีกตัว · Sugar Garden สมมุติว่าเลขใบ้ปัจจุบันสะท้อน Tier (`map[row,col] = Tier` ใน `EncounterGenerator.cs:281`) — **ต้องตรวจสูตรคำนวณเลขใบ้ก่อน implement**

### 6.2 boss pool และ Feast ต่อ variant

- **Feast ทุกตัว (ทุก Tier) ผูกกับ variant** ผ่าน `EnemyData.FloorVariantId` — แก้ปัญหาปัจจุบันที่ `GetRandomEnemyDataWithTier` (`Stat/MonsterStatController.cs:39`) สุ่มข้าม variant ได้ (Myceland spawn sugar-tiger ได้)
- แต่ละ variant ต้องมีบอส **≥1 ตัวสำหรับ spine · ≥2 ตัวเพื่อให้กระดานมีความหลากหลาย** — ตอนนี้ทั้งชีตมี T5 แค่ 2 ตัว

### 6.3 วัตถุดิบพิเศษผูกกับ variant

`FloorVariant.SpecialIngredientId` — บอสทุกตัวใน variant เดียวกัน drop ชนิดเดียวกัน · quest "ขอของจาก variant X" จึงพอใจด้วยบอสตัวไหนของ X ก็ได้ (generator ของกระดานมีอิสระ) ส่วน spine ระบุตัวเอง

---

## 7. รางวัล · วัตถุดิบพิเศษ · คลัง

### 7.1 quest หนึ่งใบให้อะไร

| # | ได้อะไร | ต้องส่งสำเร็จไหม |
| --- | --- | --- |
| 1 | coin ตามสูตร | ❌ Extract ก็ได้ |
| 2 | วัตถุดิบพิเศษเข้าคลัง (ตามเงื่อนไข 7.2) | ❌ ผูกกับการล้มบอส ไม่ผูกกับ quest |
| 3 | bonus coin จากคำขอพิเศษ | ✅ |
| 4 | ปลดล็อคสูตร / ตัวละคร / Floor Variant | ✅ และเฉพาะ spine |
| 5 | `CompletedQuestCount` +1 | ✅ |

**เส้นแบ่ง** : 1–2 = "ของที่ขนออกจากดัน" ได้เสมอถ้ายังไม่ตาย · 3–5 = "ค่าจ้างจากลูกค้า" ต้องส่งถึงมือ

### 7.2 โมเดลวัตถุดิบพิเศษ (checklist / คลัง / BossThreatRecord)

```
บอสตาย            →  drop วัตถุดิบของ variant นั้น  →  checklist +1        (เสมอ ไม่มีเงื่อนไข)
จบ run (ทุกทาง)   →  ต่อบอสแต่ละตัวที่ล้ม :
                       PreRunThreat > record[bossId]  →  +1 คลัง · record[bossId] = PreRunThreat
                       ไม่งั้น                        →  ของถูก "ส่งให้ลูกค้า" ไม่เข้าคลัง
ก่อนปลด Contract  →  การ์ดทุกใบไม่แสดงเรื่องคลัง — แสดงแค่ "จาน" ที่ขอ
                     ของที่เข้าคลังโผล่เป็นบรรทัดโบนัสใน Run Result ช่วงที่ 3
หลังปลด Contract  →  การ์ดโชว์ "ให้ / ไม่ให้" ต่อบอส  ← การโผล่ของป้ายนี้คือการสอน endgame
```

**หลัก** : "ของขวัญที่ไม่ได้สัญญา" ไม่สับสน — "สัญญาที่ไม่ได้ทำตาม" ถึงสับสน · campaign ทั้งหมดอยู่ที่ Threat 0 ดังนั้นบอสแต่ละตัวให้ของเข้าคลังครั้งเดียวตลอด campaign ถ้าไปโชว์บนการ์ดจะขึ้น "ไม่ให้" ตั้งแต่ครั้งที่สอง ทั้งที่ยังไม่มีปุ่มเพิ่ม Threat ให้กด

**งบคลังตลอดเกม** = `จำนวนบอสทั้งหมด × (MaxThreat + 1)` — เพิ่มบอส = endgame ยาวขึ้น · ต้นทุน `Unlock` ที่คิดเป็นวัตถุดิบพิเศษต้องอยู่ในงบนี้ (ควรให้ unlock ส่วนใหญ่คิดเป็น coin แล้วใช้วัตถุดิบพิเศษเฉพาะของสำคัญ)

**คลังกลายเป็น codex ไปในตัว** — บอกว่าล้มบอสตัวไหนที่ Threat เท่าไหร่มาแล้ว

### 7.3 สูตร payout

```
coinFromIngredients = coinPerSpecialIngredient[ collected.Count ]     // 0 / 100 / 300 / 500
coinFromFath        = (exitReason == Death) ? 0 : remainingFath * fathToCoinRate
subtotal            = (coinFromIngredients + coinFromFath) * threatMultiplier[preRunThreat]   // = ×1.0 ตลอด campaign
bonusCoin           = (questState == Submitted) ? sum(เงื่อนไข bonus ที่ผ่าน) : 0            // ไม่โดนตัวคูณ
total               = subtotal + bonusCoin

questState  : Active | Failed(ออร์เดอร์เสีย) | Submitted
exitReason  : QuestComplete | Extracted | Death
ส่งสำเร็จ    = collected == บอสทั้งหมดของ quest && questState != Failed && exitReason != Death
```

### 7.4 ตัวอย่างเดียวกัน เล่น 3 แบบ

การ์ด **ออร์เดอร์เงียบ ★★★** · Pre-run Threat 2 (endgame) · 6 ชั้น · *ตัวคูณ ×1.5 เป็นเลขสมมุติ ไม่ใช่ข้อเสนอ*

| | **A · ส่งสำเร็จ** | **B · ออร์เดอร์เสีย แล้วดันต่อ** | **C · ตายชั้น 4** |
| --- | --- | --- | --- |
| วัตถุดิบพิเศษ | 3 → 500 | 3 → 500 | 2 → 300 |
| Fath ที่เหลือ | 60 → 600 | 40 → 400 | 55 → **ริบ 0** |
| × ตัวคูณ | 1,100 ×1.5 → 1,650 | 900 ×1.5 → 1,350 | 300 ×1.5 → 450 |
| + bonus "HP ≥ 50%" | +250 | — | — |
| **coin สุทธิ** | **1,900** | **1,350** | **450** |
| เข้าคลัง | 3 (ถ้าผ่าน record) | **3** | 2 |
| ปลดล็อคสูตร | ✅ | ✗ | ✗ |
| quest บนกระดาน | สำเร็จ | ยังเลือกใหม่ได้ | **หาย · refresh** |

พังเงื่อนไขเสีย ~29% + สูตร แต่คลังยังครบ · ตายเสีย ~76% · **B ยังคุ้มพอที่จะเล่นต่อ** — เหตุผลทั้งหมดของข้อ 4.3

---

## 8. Endgame : The Curse Contract (ปลดหลัง S8)

**ทำไมอยู่หลัง main quest ไม่ใช่กลาง campaign**

| | Contract หลัง main quest (เลือก) | Contract กลาง campaign |
| --- | --- | --- |
| ผู้เล่นเจอตอน | รู้เกมแล้ว ประเมินเดิมพันเป็น | ยังไม่รู้ว่า build ที่ดีหน้าตายังไง |
| BossThreatRecord | **เครื่องยนต์ของ endgame** ทำงานเต็มที่ | สะดุดตั้งแต่ยังทัวร์ content |
| ความยากท้าย campaign | คำขอพิเศษ + roster + native curse | ซ้อนกับคำขอพิเศษ |
| MVP | **ตัด Contract ออกทั้งก้อน** ไม่มีสถานะครึ่งๆ | ต้องมีก่อนจบ campaign |
| genre | Ascension / Heat / Master Rank | แทบไม่มีใครทำ |

**โครง**
- ปลดเมื่อส่ง S8 สำเร็จ · เลือก curse ใส่สัญญาก่อนเข้า run · **Pre-run Threat = ผลรวม `ContractThreatValue`** · เพดาน 3–5
- **pool ของ Contract** = curse ประจำชั้นทั้ง 6 (ข้อ 6.1 — ผู้เล่นรู้จักหมดแล้ว stack ได้สูงกว่าเวอร์ชันประจำชั้น) + curse กลุ่ม buff Feast ที่เพิ่มใหม่
- Pre-run Threat ทำสองอย่างตาม GDD : ตัวคูณ coin (`ThreatReward`) + สิทธิ์เข้าคลัง (`record[bossId]`) · **ไม่คูณ stat Feast โดยตรง** — ถ้าอยากให้ Feast แข็ง ให้เลือก curse กลุ่มนี้ใส่สัญญาเอง

| curse ใหม่ (เสนอ) | ผล | MaxStack |
| --- | --- | --- |
| `well-fed` | Feast ทุกตัว HP +{N}% | 3 |
| `sharpened-fangs` | Feast ทุกตัว ATK +{N}% | 3 |
| `restless` | Feast ทุกตัว +1 action ต่อท้าย sequence | 1 |

**ทำไม buff Feast เป็น curse ไม่ใช่คุณสมบัติของเลข Threat** : GDD หัวข้อ Threat ไม่ต้องแก้ (In-run ยังเป็นตัวเดียวที่ scale อัตโนมัติ · Contract ยัง "ยากผ่านผลของ curse") · ผู้เล่นเลือกเองว่าจะเอาความยากแบบ "โดนบิดข้อมูล" หรือ "ศัตรูเลือดหนา" · ไม่มี scaling ที่ซ่อน · โค้ดรองรับ (`GameplayModifierManager.AddEnemyHighestStatPlus` + handler pattern — เพิ่มสมาชิก `ModifierEffectType` **ต่อท้าย** เท่านั้น) · curse ที่มีอยู่ 10 ใบ (ใช้จริง 7) เป็น friction ล้วน ไม่มีใบไหนแตะ stat Feast — ถ้าปล่อยไว้ผู้เล่นที่อ่านกริดเก่งจะรับตัวคูณ coin ฟรี

**วงจร endgame** : ไต่ Threat 1 → MaxThreat · แต่ละระดับเปิดวัตถุดิบพิเศษของบอสทุกตัวใหม่หมด · การ์ดกระดานเริ่มโชว์ "ให้ / ไม่ให้" ต่อบอส · คลังโตเป็นคลื่น

---

## 9. ตัวอย่างการ์ด (endgame — หลังปลด Contract)

```
┌ ออร์เดอร์เงียบ ─────────────────────────── ★★★ ┐
│ ไม่ระบุชื่อ (จดหมายไม่มีผู้ส่ง)                  │
│ "เข้าไป เอาของ ออกมา อย่าให้มันรู้ตัว"          │
│                                                │
│ จานหลัก                                        │
│   ○ ไข่ผลไม้        กวางผักกวางตุ้ง · Edemia    │
│   ○ หมึกดำก้นบึ้ง    ปลาหมึกตาบอด  · Abyssalt   │
│      ⚠ เคยล้มที่ Threat นี้แล้ว — ไม่เข้าคลัง     │
│   ○ เมล็ดพริกมังกร   พริกมังกร     · Capsaicia  │
│                                                │
│ ผังชั้น  [บอส][ว่าง][บอส][ว่าง][ว่าง][บอส]      │
│ กติกาชั้น  Edemia: ช่องไอเทมบางช่องเป็น Feast    │
│           Abyssalt: ระยะ taunt +1               │
│           Capsaicia: ยิ่งเปิดยิ่งดุ               │
│                                                │
│ คำขอพิเศษ                                      │
│   ◆ เปิดช่องรวมไม่เกิน 45 ช่อง (ทางออกไม่นับ) [บังคับ] │
│   ◇ ส่งโดย HP ไม่ต่ำกว่า 50%          +250 coin │
└────────────────────────────────────────────────┘
```

ก่อนปลด Contract การ์ดใบเดียวกัน **ไม่มีบรรทัด ⚠** และไม่มีเรื่องคลังเลย · บรรทัด ⚠ ต้องอัปเดตทันทีเมื่อปรับ Contract ขึ้น-ลง (GDD หัวข้อ Threat)

> ชื่อบอส / วัตถุดิบ / ลูกค้าเป็น **placeholder** — ชีตมี T5 แค่ `enemy-15`, `enemy-16`

---

## 10. Data model

หัวคอลัมน์ตาม `Sumeeper_GameData_Sync_Guide.md` ข้อ 4.1 · **ยังไม่ได้เขียนลงชีตจริง**

### 10.1 แท็บใหม่ `FloorVariant` → `FloorVariantConfig` · Table · string table ใหม่ `FloorVariant`

| Id | Name | Description | SpecialIngredientId | NativeCurseId | NativeCurseStack | MapAssetName |
| --- | --- | --- | --- | --- | --- | --- |
| `variant-myceland` | `variant-myceland-name` | `variant-myceland-description` | `special-01` | `minus-shifter` | `1` | `MusroomMapAssets` |

ตอนนี้ Floor Variant ไม่มีตัวตนในชีตเลย (มีแค่ `MapData` ScriptableObject + `MapAssets` 3 ชุด) แท็บนี้จึงใหม่ทั้งหมด

### 10.2 คอลัมน์ใหม่ในแท็บ `EnemyData`

| คอลัมน์ | ค่า | หมายเหตุ |
| --- | --- | --- |
| `FloorVariantId` | `variant-myceland` | **ทุก Feast ทุก Tier** ไม่ใช่แค่บอส · spawn ต้องกรองด้วยคอลัมน์นี้ |

*(ตัด `SpecialIngredientId` ที่เสนอใน rev.1 ออก — ย้ายไป `FloorVariant`)*

### 10.3 แท็บใหม่ `Quest` → `QuestConfig` · Table · string table ใหม่ `Quest` — **เฉพาะ spine**

| Id | Name | Description | CustomerId | CustomerQuote | Rank | BossIds | FloorLayout | ConditionIds | RewardUnlockIds | UnlockType | UnlockValue |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `quest-s01` | `quest-s01-name` | … | `customer-vera` | `quest-s01-quote` | `1` | `["enemy-17"]` | `["Boss"]` | `[]` | `["unlock-variant-sugar","unlock-cook"]` | `None` | `0` |
| `quest-s05` | `quest-s05-name` | … | `customer-anon` | `quest-s05-quote` | `3` | `["enemy-16","enemy-18","enemy-19"]` | `["Boss","Empty","Boss","Empty","Boss"]` | `["cond-04","cond-11"]` | `["unlock-variant-edemia"]` | `QuestCompleted` | `4` |

- `BossIds` เรียงตามลำดับที่เจอ · แต่ละตัวต้อง `Tier = 5` และ variant ต้องปลดแล้ว ณ quest นั้น
- `FloorLayout` จำนวน `Boss` = ความยาว `BossIds` · ช่องสุดท้ายต้องเป็น `Boss`
- กระดาน **ไม่มีแถว** — ใช้ `QuestNamePool` (10.4)

### 10.4 แท็บใหม่ `QuestNamePool` · Table · string table `Quest`

| Id | Kind | Name | Quote |
| --- | --- | --- | --- |
| `pool-cust-01` | `Customer` | `pool-cust-01-name` | `pool-cust-01-quote` |
| `pool-dish-01` | `Dish` | `pool-dish-01-name` | |

### 10.5 แท็บใหม่ `QuestCondition` → `QuestConditionConfig` · Table · string table `Quest`

| Id | Description | ConditionType | Comparison | Value | TargetId | IsMandatory | BonusCoin | MinRank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cond-04` | `cond-tile-opened-max` | `TileOpenedMax` | `LessOrEqual` | `45` | | `TRUE` | `0` | `3` |
| `cond-11` | `cond-hp-remain-min` | `HpRemainMinPercent` | `GreaterOrEqual` | `50` | | `FALSE` | *(คนจูน)* | `2` |

`MinRank` ให้ generator ของกระดานกรอง · `ConditionType` / `Comparison` = คอลัมน์ enum ใหม่ใน `_enum`

### 10.6 คอลัมน์ใหม่ในแท็บ `Curse`

| คอลัมน์ | ค่า | ใช้ทำอะไร |
| --- | --- | --- |
| `CurseSource` | `Contract` / `Gauge` / `Both` | ตอนนี้ `GroupType` ทุกใบ = `Normal` แยก pool ไม่ได้ |
| `ContractThreatValue` | int *(คนจูน)* | ใบนี้ = Pre-run Threat กี่แต้ม · `0` = เลือกในสัญญาไม่ได้ |

### 10.7 แถวใหม่ในแท็บ `MaterialItem`

| Id | Name | Description | Type | Rarity | AtlasName | SpriteName | Cost | IsEnemyOnly | IsSystemItem |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `special-01` … `special-06` | `special-01-name` | … | `SpecialIngredient` | `Legendary` | `MaterialAtlas` | *(รออาร์ต)* | `0` | `FALSE` | `FALSE` |

> ⚠ `SpecialIngredient` ต้องเพิ่ม**ต่อท้าย** `ItemTypeEnum` (`Inventory/InventoryManager.cs:326-334`) — asset เก็บ enum เป็น index · ต้องมีเงื่อนไขในโค้ดกันไม่ให้ขึ้นร้าน ไม่ใช่พึ่ง `Cost = 0`

### 10.8 `ThreatReward` · `Unlock` · `GameConfig`

`ThreatReward` (`PreRunThreat | CoinMultiplier` แถว 0 = 1.0 ที่เหลือคนจูน) และ `Unlock` ตามรายงาน 09-09 ข้อ 5.3 / 5.4 · เพิ่มใน `GameConfig` : `coinPerSpecialIngredient [0,100,300,500]` · `fathToCoinRate 10` · `questBoardSlotCount 3` · `questBoardRerollCost` *(คนจูน)* · `maxPreRunThreat` *(3–5)*

### 10.9 MetaSave (ไฟล์ save ฝั่ง client)

```
MetaSave
  Coin : int
  UnlockedIds : string[]
  CompletedQuestIds : string[]
  SpecialIngredientStash : { ingredientId : count }
  BossThreatRecord : { bossId : int }          // key = บอส
  CurrentBoardQuests : GeneratedQuest[]        // กระดานต้องคงอยู่ข้าม session (เก็บทั้งใบ ไม่ใช่แค่ id)
  IsContractUnlocked : bool
```

### 10.10 RunContext (run-scoped ไม่ persist)

```
RunContext
  Quest : QuestSnapshot            // สำเนาทั้งใบ (spine หรือที่ generate) — ล็อกกันชีตเปลี่ยนกลาง run
  QuestState : Active | Failed | Submitted
  PreRunThreat · ContractCurseIds[]
  CollectedBossIds[] · Fath · CurrentFloor
  AcceptedCurseIds[]               // In-run Threat = Count · ไม่รวม native curse ของชั้น
  ConditionProgress : { conditionId : currentValue }
  ExitReason : None | QuestComplete | Extracted | Death
```

---

## 11. ผลกระทบต่อ minimal scope ในรายงาน 09-09 — **spine คือลำดับ implement**

| ทำถึง | ต้องมีอะไรแล้ว | ตรงกับรายงาน 09-09 |
| --- | --- | --- |
| **S1–S3** | กริด · combat · **บันได** · Run Result · payout · MetaSave · unlock · หน้ากิลด์ · `FloorVariant` + `EnemyData.FloorVariantId` · native curse 3 ใบที่มีโค้ดแล้ว | **= "loop ปิด" ทั้งดุ้น** — งานที่ 1–5, 8, 9 |
| S4 | ระบบเงื่อนไข + ตัวนับ HUD + generator กระดาน | งานใหม่ M |
| S5–S7 | เงื่อนไขบังคับ + สถานะออร์เดอร์เสีย + native curse อีก 3 ใบ | M |
| **S8 / endgame** | Contract UI · `ThreatReward` · `CurseSource` · curse กลุ่ม buff Feast · ป้าย "ให้/ไม่ให้" | **ตัดออกจาก MVP ได้ทั้งก้อน ไม่เหลือเศษ** |

การเปลี่ยนแปลงจากประเมินเดิม : งาน "แยก Floor/Run Result" ขยับ **M → M+** (เพิ่มบันได + `IFloorClearCondition`) · เพิ่มงาน "ระบบเงื่อนไข" **M** · เพิ่มงาน "`FloorVariant` + กรอง spawn ตาม variant" **S–M** · ลำดับหลักไม่เปลี่ยน : MetaSave → RunContext → แยก Result → payout → Quest → เงื่อนไข → หน้ากิลด์

---

## 12. การตัดสินที่กระทบนอกขอบเขต Quest : Feast โตจาก Threat ทางเดียว

ต้อง merge เข้า GDD หัวข้อ Curse Gauge และ mirror ลง sim engine ทั้ง Python และ JS

| ที่ | ตอนนี้ | ต้องเป็น |
| --- | --- | --- |
| `Stat/MonsterStatController.cs:337-346` | `statGainFromFloor = currentFloor + 1` คูณ ATK/DEF/SPD/HP | ค่า base ของ species/tier ตรงๆ |
| `Stat/MonsterStatController.cs:345` | `XP = preset.XP * (currentFloor+1)` | ค่าคงที่ตาม Tier |
| `GamePlay/ThreatLevelManager.cs:56-72, 103-107` | สะสมยาวทั้ง run · threshold = `ThreatBaseCost + level × Growth` | **รีเซ็ตเกจต่อชั้น** (ข้อ 29) · threshold เป็นลิสต์ต่อชั้นจาก `FloorLayout` · `AcceptedCurseCount` (= In-run Threat) ไม่รีเซ็ต · `MaxThreatLevel` ไม่ใช้แล้ว |

**ต้องแก้คู่กันเสมอ** — ถ้าแก้แค่ stat แต่ปล่อยค่าเกจ ชั้นลึกจะเติมเกจเร็วขึ้น → รับ curse ถี่ขึ้น → In-run Threat โตตามชั้นอยู่ดี ความยากตามหมายเลขชั้นกลับมาทางประตูหลัง

**เหตุผล** : GDD สัญญาว่า *"ความยากไต่ขึ้นตามพฤติกรรมของผู้เล่นเอง ไม่ใช่ตามหมายเลขชั้น"* — ตัดตัวคูณแล้วระบบ self-balance เพราะพลังผู้เล่นกับพลังศัตรูโตจากการกระทำเดียวกัน (ฆ่า Feast) · ความรู้สึก "ลึกขึ้น" มาจาก native curse (ข้อ 6.1) + สัดส่วน Tier ใน roster ไม่ใช่ตัวคูณ

**ต้องแจ้งคนจูนก่อนลงมือ** — เปลี่ยนตัวเลขทุก combat · `simulate/reference_baseline.json` เทียบไม่ได้อีก

---

## 13. รายการที่ต้องแก้ใน GDD — **merge แล้ว 2026-09-17** (ทุกแถวด้านล่างลงใน `Sumeeper_GDD.md` แล้ว · `Sumeeper_UX_Screens.md` ข้อ 3 และ 5 แก้ตามเรื่องบันได · ชีตยังไม่แตะตาม D10)

| หัวข้อ GDD | แก้อะไร |
| --- | --- |
| **Quest** | เพิ่มชั้น "คำขอพิเศษ" · "3 ชิ้นคือมาตรฐาน ออร์เดอร์ฝึกหัด 2 ใบแรกน้อยกว่าได้" · spine/กระดาน · ★ |
| **Floor Clear** | เปลี่ยน "ปัจจุบัน = ฆ่าบอส" → ช่องบันได (ชั้นบอสล็อกจนฆ่าบอส) |
| **Reward** | bonus ไม่คูณ Threat · สถานะออร์เดอร์เสีย · Threat multiplier = 1.0 ตลอด campaign |
| **Special Ingredients** | ผูกกับ variant · คลัง · record key = บอส · ก่อนปลด Contract ไม่แสดงบนการ์ด |
| **Floor Variant** | เพิ่ม native curse ต่อ variant (แปลจาก lore ที่มีอยู่) · boss pool ต่อ variant |
| **Curse Gauge** | ยืนยัน "ไม่ผูกกับ floor-index" ทั้ง stat และค่าเกจ (โค้ดต้องตาม) |
| **Curse** | แยก pool `Contract` / `Gauge` · เพิ่ม curse กลุ่ม buff Feast · native curse ไม่นับ In-run Threat |
| **The Curse Contract** | ปลดหลัง main quest · pool = native curse + buff Feast · เพดาน 3–5 |
| **Threat** | ไม่แก้ — ยืนยันว่า In-run เป็นตัวเดียวที่ scale อัตโนมัติ |
| **Core gameloop** | เพิ่ม endgame loop (Threat ladder → คลัง → unlock) |

---

## 14. คำถามค้าง

### 14.1 ต้องฟัน — ดีไซน์ (ผู้ตัดสิน) · เรียงตามสิ่งที่มันบล็อก

| # | เรื่อง | ทางเลือก | แนะนำ | บล็อกอะไร |
| --- | --- | --- | --- | --- |
| D1 | **สูตร signature ที่ spine ปลดคืออะไร** — Cook ปัจจุบันรู้จักแค่ `material-01..03` (16 สูตร = combination ครบชุด) **ไม่มีสูตรที่ใช้วัตถุดิบพิเศษเลย** | (ก) ปลด*สูตรธรรมดา*จาก 16 นี้ — fiction: ลูกค้าสอนสูตรตอบแทน · (ข) recipe type ใหม่ที่ใช้วัตถุดิบพิเศษ — แต่ของไปคลัง ไม่อยู่ใน run inventory → ขัดกันเอง | **(ก)** — วัตถุดิบพิเศษเป็น meta currency ล้วน ไม่แตะ Cook | `Unlock` · reward S2/S6 · **S1** |
| D2 | **Extract กดได้ที่ไหน** — GDD: *"ยุติ run กลางทางได้ตลอด"* · UX: ปุ่มอยู่ Floor Result เท่านั้น · HUD กริดยังไม่เขียน | Floor Result เท่านั้น / HUD ทุกเมื่อ | **Floor Result เท่านั้น** — กลางกริดมี Retreat (Pre-Combat) อยู่แล้ว และ "ดันต่อหรือถอย" ควรถามตอนจบชั้น · บันได = จังหวะออก | FloorResult state · HUD |
| D3 | **Extract ปลดที่ S3 → ย้ายไป S2?** — ตามตาราง spine สองออร์เดอร์แรกถอนตัวไม่ได้ | S3 / S2 | **S2** — quest แรกที่มี Floor Result (มีชั้นว่าง) · S1 ชั้นเดียวไม่มี Floor Result อยู่แล้ว | ตาราง spine · S2 |
| D4 | **ตายแล้วของเข้าคลังไหม** — โมเดล 7.2 เขียน "ทุกทาง" · GDD เดิมพูดถึงแค่ coin | เข้า / ไม่เข้า | **เข้า** — ตายเสีย Fath + สำเร็จ + bonus พอแล้ว ถ้าเสียคลังด้วย ★★★ endgame จะโหดเกิน · *แค่ยืนยัน* | payout |
| D5 | **`SoftCurrency` (`currency-01`)** — ค้างจาก 09-09 · **คืออะไร** : กระเป๋าที่สองในโค้ด เก็บเป็น item `currency-01` ใน material inventory (`Inventory/InventoryManager.cs:9,80`) · **ได้จากหีบ (Treasure) เท่านั้น** (`Item/ItemDropManager.cs:47,68-80` สูตร `(ThreatLevel+1) × CurrencyGainMultiplier × treasure.Tier`) · **โชว์บน HUD ในดัน** ด้วยชื่อ localize `material-coin-name` (`UI/UIGameplayController.cs:632-637`) · **ไม่มีใครใช้จ่าย** — ร้าน/Hint/reroll ใช้ `CurrentCoin` (= Fath) หมด · **ถูก `ClearInventory()` ทุกต้น run** จึงไม่ persist ด้วย → เป็นระบบตาย : เติมจากหีบ โชว์ว่าเป็น "coin" ใช้ไม่ได้ หายทุก run · และละเมิด UX ข้อ 0 (ห้ามโชว์ Coin ในดัน) | ถอด (หีบให้ Fath แทนผ่าน `AddMoney`) / ยุบเข้า Fath (= อย่างเดียวกันในทางปฏิบัติ) / ทำให้เป็น Coin จริงที่ persist — **ขัด GDD** เพราะ Coin ต้องคำนวณตอน Run Result ไม่ใช่เก็บในดัน | **ถอด** — หีบให้ Fath ตาม Tier แทน · ลบแถว `currency-01` (เฟสชีต) · ถอด HUD บรรทัดที่สอง · `CurrencyGainMultiplier` ตายตามไปด้วย (D7) | งานที่ 0 |
| D6 | **ขอบเขต rename** | critical path / ทั้งโปรเจกต์ | **critical path** (Coin→Fath · ThreatLevelManager→CurseGauge) — feature branch ค้างหลายอัน | งานที่ 0 |
| D7 | **retire config เดิม** (brief Q7) — **ขอบเขต : Unity `GameData/Config/GameConfig.cs` + แถว KeyValue ในชีต `GameConfig` + แท็บ `PlayerXP`/asset `PlayerXPConfig` — ไม่เกี่ยวกับ GDD** (GDD ไม่มีชื่อเหล่านี้อยู่แล้ว เพราะถอด leveling ไปแล้ว) · ตัดสินวันนี้ได้ ลงมือตอนเฟสชีต/โค้ด (ข้อ 31) | — | `MaxThreatLevel` ถอด (threshold ต่อชั้นแทน) · `MoneyGainPerMonsterTier` เก็บ rename → `FathGainPerTier` · `CurrencyGainMultiplier` ถอดพร้อม D5 · แท็บ `PlayerXP` + `maxPlayerLevel`/`statIncreasePerLevel`/`freeStatPointPerLevel` ถอด | งานที่ 0 |
| D8 | **จัด pool curse 10 ใบเดิม** — `CurseSource` ใบไหน Gauge / Contract / Both | — | 3 ใบที่เป็น native (`minus-shifter` `ignore-me` `meal-of-fatigue`) = `Both` · friction อื่น = `Gauge` ไปก่อน · ใบที่ `IsEnabled=False` ยังไม่จัด | Gauge pool บล็อก **S2** |
| D9 | **หน้า Collections ใน MVP** — ผู้ตัดสินนิยาม (09-17) : หน้าที่บอกว่า equipment เหลืออะไร ปลดอย่างไร · recipe ที่เคยปลด · Feast ที่เคยพบ — คือ **codex + จุดจ่าย coin ปลดของ ในหน้าเดียว** (ไม่ใช่ "ร้าน" แยก) · **โครงมีอยู่แล้ว** : scene `GameMenu` มีปุ่ม Monsters / Upgrade / RecipeBook / Investigate (`UI/Page/GameMenu.cs`) → Monsters = Feast codex (`UI/ShowMonsterPanel.cs` มีแล้ว) · RecipeBook = recipe codex · Upgrade (ระบบ skill-level เดิม `Upgate/`) = repurpose เป็นแท็บ Equipment/Character | — | **แท็บ Feast** : พบ/ไม่พบ + ต่อบอสโชว์ Threat สูงสุดที่เคยล้ม (= `BossThreatRecord` ทำหน้าที่ codex ตามข้อ 7.2) · **แท็บ Recipe** : ปลดแล้ว/ยัง + มาจาก spine ใบไหน · **แท็บ Equipment** : ล็อก/ปลด + เงื่อนไข (`Unlock` : coin / CompletedQuest / RequireBossIds) + **กดจ่าย coin ที่การ์ดนั้นเลย** · MVP : equipment 3–5 ชิ้นราคา coin + สูตรธรรมดาที่ไม่ได้มาจาก spine · วัตถุดิบพิเศษเป็นราคาเฉพาะตัวละคร/สูตรระดับสูง (endgame) | หน้ากิลด์ · **S1** |
| D10 | ~~อนุมัติแก้ GDD + สร้างแท็บใหม่ในชีต~~ → **ตัดสินแล้ว (09-17) : แก้ GDD อย่างเดียว ยังไม่แตะชีต** (ข้อ 31) — รอคำสั่ง "ไป" เพื่อ merge ตามข้อ 13 | — | — | ทุกอย่าง |

### 14.2 dependency ฝั่ง content (ไม่ใช่ตัดสิน แต่ต้องมีคนทำ)

| ของ | ตอนนี้มี | MVP ต้องมี | เต็มต้องมี | ถ้าไม่ทัน |
| --- | --- | --- | --- | --- |
| บอส T5 | 2 | 3 (map ข้อมูลชั่วคราวได้) | 6 → ≥12 | ใช้ `FloorVariantId` ย้ายบอสข้าม variant ชั่วคราว |
| ตัวละคร | **1** (`Player/MainChar.asset`) | 1 | 3 (S4, S7 ปลดตัวที่ 2/3) | เปลี่ยน reward S4/S7 เป็นสูตร/equipment ไปก่อน |
| native curse FX/UI | 3 ใบมีโค้ด ไม่มี FX เฉพาะ | 3 (M · SG · Ab) | 6 | SG ใช้แค่เลข ไม่ต้อง FX |
| ลูกค้า | 0 | 2 (ยาย · หัวหน้ากิลด์) | 4 + pool | placeholder text |
| sprite วัตถุดิบพิเศษ | 0 | 3 | 6 | ใช้ sprite material เดิมชั่วคราว |
| ชื่อ/บท spine | 0 | S1–S3 | S1–S8 | — |

### 14.2 ตัวเลขที่รอคนจูน

`threatMultiplier[]` · `BonusCoin` และ `Value` ของทุกเงื่อนไข · `questBoardRerollCost` · `maxPreRunThreat` (3–5) · `ContractThreatValue` ทุกใบ · `NativeCurseStack` ทุก variant · ค่า N ของ `well-fed` / `sharpened-fangs` · ราคาและเงื่อนไข `Unlock` ทุกแถว

### 14.3 ต้องเช็คข้อเท็จจริงก่อน implement (agent เช็คได้ ไม่ต้องฟัน)

- **สูตรคำนวณเลขใบ้** — สะท้อน Tier (รวมค่า) หรือนับหัว? กระทบนิยาม Sugar Garden (6.1.1)
- **Hint encounter ปัจจุบันเผยอะไรได้บ้าง** — จะเพิ่ม "เผยบันได" ได้ไหม
- ✅ ตรวจแล้ว : `MapData` รองรับกริดคนละขนาดต่อชั้น (`MapWide`/`MapHeight`) · ทุกช่องมี cover จนกว่าจะเปิด · ตัวละครมี 1 ตัว

### 14.4 data bug แก้ได้ทันที (ไม่ต้องฟัน)

- `MaterialItem.Type` ของ `material-04..07` = `None` → แก้ 4 เซลล์เป็น `Material` แล้ว Pull

### 14.5 ปิดแล้ว ไม่ต้องถกซ้ำ

การตัดสิน 29 ข้อในตารางข้อ 1 — ถ้าจะเปิดใหม่ให้เปิดเป็นข้อ D ใหม่ในตาราง 14.1 พร้อมเหตุผล
