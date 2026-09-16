# Brief สำหรับ agent — Review: Quest + Reward Loop

วันที่ 2026-09-09 · เขียนโดย agent ที่สำรวจ repo เอกสาร (`D:\Sumeeper`) และโปรเจกต์ Unity (`D:\git_project\Minesweeper`) branch `develop`
สถานะเอกสารนี้: **brief สั่งงาน** ไม่ใช่ข้อสรุป — ข้อค้นพบข้างในเป็น first pass ที่ **ผู้รับงานต้องตรวจซ้ำเอง**

---

## 1. งานที่ต้องทำ

Review **Quest + Reward loop** ตามที่มีอยู่ ณ ตอนนี้ — ทั้งฝั่งเอกสาร (GDD, UX_Screens) และฝั่งที่ implement ไปแล้วใน Unity — แล้วส่งรายงานที่ตอบ 4 คำถาม

1. **ตอนนี้มีอะไรอยู่จริงบ้าง** — แยกให้ชัดว่า "เขียนใน GDD แล้ว" / "มีโค้ดแล้ว" / "มีโค้ดแต่คนละกติกากับ GDD"
2. **drift อยู่ตรงไหน** — จุดที่ GDD ↔ code ↔ ชีต ไม่ตรงกัน พร้อมหลักฐาน (path:line)
3. **gap อะไรบ้างที่ขวางไม่ให้ loop ปิด** — เรียงลำดับความสำคัญ พร้อมประเมินขนาดงานหยาบๆ (S/M/L)
4. **minimal scope ที่ทำให้ loop ปิดได้** — ชุดงานที่เล็กที่สุดที่ทำให้ผู้เล่นเล่น "รับ quest → เข้าดัน → จบ run → ได้ coin → ปลดล็อคของ → รับ quest ใหม่" ได้ครบวง

**ไม่ใช่งานนี้** : จูนตัวเลข balance (เป็นของคนจูน), แก้โค้ดจริง, เขียนลง Google Sheet, ออกแบบ art/layout

---

## 2. อ่านอะไรก่อน (เรียงตามลำดับ)

| ลำดับ | ไฟล์ | ส่วนที่เกี่ยวข้อง |
| --- | --- | --- |
| 1 | `game_document/Sumeeper_GDD.md` | `Core gameloop` ทั้งหมด — Run / Currency / Quest / Reward / The Curse Contract / Threat (บรรทัด ~554–668) และ `Curse Gauge` (~436) |
| 2 | `game_document/Sumeeper_UX_Screens.md` | ข้อ 3 (Combat Result บอส), ข้อ 5 (Floor Result), ข้อ 6 (Run Result — มีสูตร payout ledger ละเอียดแล้ว), ข้อ 7 (หน้ารับ Quest ที่ยังไม่เขียน) |
| 3 | `game_document/Sumeeper_GameData_Sync_Guide.md` | แผนที่แท็บ → asset — อ่านก่อนเสนอ data model ใหม่ทุกครั้ง |
| 4 | โค้ด Unity | ตารางในข้อ 4 |

**กติกา** : GDD เป็น canonical — ถ้า code หรือชีตขัดกับ GDD ให้ **รายงานเป็น drift ไม่ใช่เดาว่าอันไหนถูก** และห้ามแก้ตัวเลข balance เอง

---

## 3. สรุปสถานะที่สำรวจมาได้ (first pass — ต้องตรวจซ้ำ)

### 3.1 ฝั่งเอกสาร — ค่อนข้างครบแล้ว

- **Reward** มีสูตรครบ: วัตถุดิบพิเศษ 0/1/2/3 ชิ้น → 0/100/300/500 coin · Fath ที่เหลือ 1 : 10 coin · คูณด้วยตัวคูณจาก **Pre-run Threat** เท่านั้น · วัตถุดิบธรรมดาไม่แปลงเป็น coin
- **การจบ run 3 ทาง** (ส่งสำเร็จ / Extract / แพ้) และรางวัลที่ต่างกันของแต่ละทาง เขียนไว้ครบ
- **UX ของ Run Result** ละเอียดถึงระดับ "ใบเสร็จต้องไล่ทีละบรรทัด" แล้ว — ใช้เป็น spec ได้เลย
- **Quest** ยังบางที่สุดในกลุ่มนี้: รู้แค่ว่า "ขอวัตถุดิบ 3 อย่างจากบอส 3 ตัวของ run นั้น" และทำหน้าที่เป็น checklist + เงื่อนไขผ่านชั้นในอนาคต — **ยังไม่มี data model, ไม่มีกติกาการเลือก/สุ่ม quest, ไม่มีหน้ารับ quest**

### 3.2 ฝั่งโค้ด — loop ยังไม่ปิด

| GDD บอกว่า | โค้ดตอนนี้ | หลักฐาน |
| --- | --- | --- |
| Quest เป็น checklist ของ run | **ไม่มีเลย** — เกรป `Quest` ใน `Runtime/Scripts` ได้ 0 ไฟล์ | — |
| Special Ingredient drop 100% จากบอส T5 | ไม่มี item type นี้ · `MaterialtemConfig.asset` มีแค่ `currency-01` + `material-01..08` | `GameData/Config/ScriptableObject/MaterialtemConfig.asset` |
| จบ run 3 ทาง | มี 2 ทาง (Win/Lose) · **ไม่มี Extract** — เกรป `Extract` ได้ 0 | `GamePlay/GameplayingManager.cs:11` (`GameResultEnum { None, Win, Lose }`) |
| Win = ส่ง quest ครบ | Win = **ฆ่าบอสตัวไหนก็ได้** (`monster.IsBoss`) | `StateMachine/Gameplay/CombatGameState.cs:288-293` |
| Run Result มีใบเสร็จ payout | `UIResultPanel.Show(isWin, canGoToNextFloor)` — มีแค่ win/lose group + ปุ่มชั้นถัดไป/เมนู **ไม่มีการคำนวณรางวัลใดๆ** | `UI/UIResultPanel.cs`, `StateMachine/Gameplay/ResultGameState.cs` |
| Coin = นอกดัน, Fath = ในดัน | **สลับชื่อกัน**: `PlayerStatController.CurrentCoin` คือเงินที่ใช้ซื้อของใน Shop/Hint = Fath ตาม GDD · ส่วน `InventoryManager.SoftCurrency` เป็นอีกกระเป๋าที่ยังไม่มีใครใช้จ่าย | `Stat/PlayerStatController.cs:46-81`, `UI/Test/ShopEncounterUIController.cs:120`, `Item/ItemDropManager.cs:53-80` |
| Threat มี 2 แกน (Pre-run จาก Contract / In-run จาก curse) | `ThreatLevelManager` คือ **ระบบ XP/Level เดิมที่เปลี่ยนชื่อ** — สะสม ThreatXp จากการฆ่า, level up แล้วแจก curse **สุ่ม 1 ใบ** + item + buff stat สูงสุดของมอนสเตอร์ +1 · ไม่มี Pre-run Threat, ไม่มี Curse Contract, ไม่มี "เลือก 1 จาก 2" | `GamePlay/ThreatLevelManager.cs` |
| ตัวคูณ coin จาก Pre-run Threat | ไม่มี — ThreatLevel ปัจจุบันไปคูณ **drop ระหว่าง run** แทน | `Item/ItemDropManager.cs:69-77` |
| meta progression (unlock equipment/character/recipe) | ไม่มี — เกรป `Unlock` ได้ 0 | — |

**ข้อสังเกตที่หนักที่สุด** : คำว่า *Threat* ใน GDD กับใน code เป็นคนละระบบกัน และ *Coin/Fath* สลับความหมายกัน — ทั้งสองอย่างอยู่ตรงกลางของ Reward loop พอดี **ควรตัดสินเรื่องคำศัพท์ให้จบก่อนออกแบบต่อ** ไม่งั้นทีมจะคุยกันคนละภาษา

### 3.3 ของที่มีอยู่แล้วและใช้ต่อได้

- `IRewardService` + `RewardPresentation` (`UI/Reward/`) — popup แสดงของที่ได้ ใช้ต่อกับ Special Ingredient ได้เลย
- `ResultGameState` + `UIResultPanel` — โครงหน้าสรุปมีแล้ว เหลือเติมเนื้อ
- `FloorData` (ScriptableObject list ของ `MapData`) — โครงชั้นมีแล้ว แต่ยังไม่มี Floor Variant / boss ที่ผูกกับ quest

---

## 4. จุดที่ต้องไปดูในโค้ด (path เริ่มต้น)

รากโปรเจกต์ Unity: `D:\git_project\Minesweeper\Assets\Minesweeeper\Runtime\Scripts\` (โฟลเดอร์สะกด **สาม e**)

| หัวข้อ | ไฟล์ |
| --- | --- |
| จบเกม / ผลการเล่น | `GamePlay/GameplayingManager.cs`, `StateMachine/Gameplay/ResultGameState.cs`, `UI/UIResultPanel.cs` |
| เงื่อนไขชนะ / ตายบอส | `StateMachine/Gameplay/CombatGameState.cs` (`HandleMonsterDeath`, `HandlePlayerDeath`) |
| currency + drop | `Stat/PlayerStatController.cs`, `Item/ItemDropManager.cs`, `Inventory/InventoryManager.cs` |
| threat / curse gauge ปัจจุบัน | `GamePlay/ThreatLevelManager.cs`, `GamePlay/GameplayModifierManager.cs`, `GamePlay/CurseEffectManager.cs` |
| โครง state ทั้งหมด | `StateMachine/Gameplay/GameplayingStateController.cs`, `LifetimeScope/GamePlayLifetimeScope.cs` |
| reward popup | `UI/Reward/IRewardService.cs`, `UI/Reward/RewardPresentation.cs` |
| config ที่เกมโหลด | `GameData/Config/GameConfig.cs` + `GameData/Config/ScriptableObject/*.asset` |

**ข้อควรระวัง** : asset เก็บ enum เป็น **index** — ถ้าจะเสนอลบ/สลับลำดับ enum ใดๆ ต้องเขียนกำกับว่าข้อมูลเดิมจะเพี้ยน (หมายเหตุเดียวกับหัวข้อ Ability ใน GDD)

---

## 5. การออกแบบเบื้องต้น (straw-man — ยิงทิ้งได้)

ใส่ไว้เพื่อให้เห็นภาพร่วมกันเร็วขึ้น **ไม่ใช่ข้อสรุป** — ผู้รับงานเสนอแบบอื่นได้ แต่ต้องบอกเหตุผลเทียบกับแบบนี้

### 5.1 Data model ที่น่าจะต้องมี

```
QuestConfig (แท็บใหม่ในชีต GameData)
  id | Name | Description | BossIds (3 ตัว, JSON) | FloorIds | UnlockCondition
      └─ บอสถูกกำหนดจาก quest ⇒ MapGenerator ต้องรับ boss list จาก run context ไม่ใช่สุ่มเอง

SpecialIngredient
  ผูก 1:1 กับ boss  →  bossId → specialIngredientId
  ทางเลือก: เพิ่ม type ใหม่ใน MaterialItem (field `type` เป็น int อยู่แล้ว) แทนการสร้าง config แยก

RunContext (run-scoped, ไม่ persist)
  QuestId · PreRunThreat · ContractCurseIds[] · CollectedSpecialIngredientIds[]
  Fath · CurrentFloor · InRunThreat (= จำนวน curse ที่รับ) · AcceptedCurseIds[]

MetaSave (persist ข้าม run)
  Coin · UnlockedEquipment/Character/Recipe · CompletedQuestCount
  BossThreatRecord : Dictionary<bossId, highestPreRunThreatCleared>
      └─ ใช้ตัดสินสิทธิ์วัตถุดิบพิเศษ: ให้ก็ต่อเมื่อ currentPreRunThreat > highestPreRunThreatCleared
```

### 5.2 สูตร payout (แปลตรงจาก GDD — reviewer ต้องตรวจว่าตรงจริง)

```
coinFromIngredients = {0:0, 1:100, 2:300, 3:500}[collectedSpecialIngredients.Count]
coinFromFath        = (จบแบบแพ้) ? 0 : remainingFath * 10
total               = (coinFromIngredients + coinFromFath) * threatMultiplier[preRunThreat]

questComplete       = collected == 3 && exitReason != Death
วัตถุดิบธรรมดา      = ไม่เข้าสูตร (แต่ต้องโชว์ว่าเหลือเท่าไหร่ เพื่อสอนให้ทำอาหารก่อนออก)
```

`threatMultiplier[]` เป็นตัวเลข balance → **ห้ามตั้งเอง** ให้เสนอเป็นช่องว่างในตารางให้คนจูนกรอก

### 5.3 Flow ที่ทำให้ loop ปิด

```
กิลด์ (รับ quest + ตั้ง Curse Contract → ได้ PreRunThreat + รู้ว่าบอสตัวไหนให้/ไม่ให้ของ)
   ↓
Floor N: กริด → encounter → บอส → Special Ingredient (ถ้ามีสิทธิ์) → checklist +1
   ↓
Floor Result: [ลงชั้นถัดไป] หรือ [Extract ← ของใหม่]
   ↓
Run Result: ใบเสร็จ payout → coin เข้า MetaSave → unlock ที่เงื่อนไขครบ
   ↓
กลับกิลด์ → quest ใหม่
```

### 5.4 ข้อเสนอเรื่องขอบเขต (ให้ reviewer เห็นด้วย/ค้าน)

- **เงื่อนไขผ่านชั้น** : คง "ฆ่าบอสของชั้น" ไว้ก่อนตาม GDD ข้อ *ปัจจุบัน* แต่แยกออกมาเป็น interface (เช่น `IFloorClearCondition`) เพื่อเปลี่ยนเป็น quest checklist ทีหลังโดยไม่รื้อ state machine
- **คำศัพท์** : rename ในโค้ดให้ตรง GDD (`CurrentCoin` → Fath, `ThreatLevelManager` → CurseGauge) เป็นงานก้อนเดียวทำก่อนงานอื่น — reviewer ประเมินด้วยว่าคุ้มไหมเทียบความเสี่ยงตอน merge (มี feature branch ค้างอยู่หลายอัน)
- **Extract** : เพิ่ม `GameResultEnum.Extracted` แยกออกมา แทนการยัดใน Win/Lose เพราะรางวัลต่างกันจริง

---

## 6. คำถามที่ต้องได้คำตอบจากคนตัดสิน (รวบรวมมา อย่าตอบเอง)

1. quest 1 ชุด = กี่ชั้น? GDD บอกบอส 3 ตัว/run แต่ UX เขียน "Floor Result ~3–6 ครั้งต่อ run" — บอส 3 ตัวใน 3 ชั้น หรือกระจายใน 6 ชั้น?
2. quest มาจากไหน — ลิสต์ที่ออกแบบมือ, สุ่มจาก pool, หรือปลดตาม progression?
3. เลือก quest ได้กี่อันต่อครั้ง และ reroll ได้ไหม?
4. Special Ingredient เก็บข้าม run ได้ไหม (GDD บอกใช้ปลดล็อค character/recipe) หรือถูกใช้หมดตอนส่ง quest?
5. ถ้าล้มบอสตัวเดิมซ้ำที่ Threat เท่าเดิม → ไม่ได้วัตถุดิบพิเศษ แล้ว **quest ที่ขอของชิ้นนั้นจะส่งสำเร็จได้ไหม**? (GDD ยังไม่ปิดเคสนี้ และเป็นเคสที่ทำให้ผู้เล่นติดตันได้)
6. ตัวคูณ coin ต่อ 1 Pre-run Threat เป็นเท่าไหร่ (ตัวเลข balance)
7. `MaxThreatLevel` / `MoneyGainPerMonsterTier` / `CurrencyGainMultiplier` ใน GameConfig ปัจจุบัน จะ retire หรือ remap เป็นอะไรในระบบใหม่

---

## 7. ส่งงานอย่างไร

เขียนเป็นไฟล์เดียวที่ `game_document/proposals/QuestReward_Review_<YYYY-MM-DD>.md` โครงตามนี้

1. **สรุป 5 บรรทัด** — loop ปิดหรือยัง ขาดอะไรสำคัญที่สุด 3 อย่าง
2. **ตาราง drift** — `หัวข้อ | GDD ว่าอย่างไร | code/ชีตเป็นอย่างไร | หลักฐาน (path:line) | ข้อเสนอ`
3. **ตาราง gap** — `สิ่งที่ขาด | ขวางอะไร | ขนาดงาน S/M/L | ลำดับ`
4. **Minimal scope ที่ทำให้ loop ปิด** — ลิสต์งานเรียงลำดับ พร้อมระบุว่าอันไหนต้องรอคำตอบจากข้อ 6 ก่อน
5. **ข้อเสนอ data model** — ถ้าเสนอแท็บใหม่ในชีต ให้เขียนหัวคอลัมน์ครบตามฟอร์แมตใน Sync Guide (**ยังไม่ต้องเขียนลงชีตจริง**)
6. **คำถามค้าง** — ข้อ 6 ที่ยังไม่มีคำตอบ + ที่ค้นเจอเพิ่ม

**ข้อห้าม** : ห้ามเขียน Google Sheet · ห้ามแก้ไฟล์ในโปรเจกต์ Unity · ห้ามตั้งตัวเลข balance เอง (ยกเว้นระบุชัดว่าเป็น placeholder ให้คนจูนกรอก) · ห้ามแตะ `backup/`
