# Review : Quest + Reward Loop — 2026-09-09

ตอบ brief `game_document/briefs/Quest_Reward_Loop_Review_Brief_2026-09-09.md`
ขอบเขต : เอกสาร (`Sumeeper_GDD.md`, `Sumeeper_UX_Screens.md`) · ชีต `Sumeeper_GameData` (อ่านสด 18 แท็บ) · โค้ด Unity `D:\git_project\Minesweeper` branch `develop` @ `94d38e66`
**ไม่ได้แก้ไฟล์ใดๆ ในโปรเจกต์ Unity · ไม่ได้เขียนลงชีต · ไม่ได้ตั้งตัวเลข balance** (ตัวเลขทุกตัวที่โผล่ในเอกสารนี้เป็นค่าที่ยกมาจาก GDD ตรงๆ หรือเป็นช่องว่างให้คนจูนกรอก)

---

## 1. สรุป 5 บรรทัด

1. **loop ยังไม่ปิด และยังไม่ใกล้ปิด** — ปลายทางของ run ตอนนี้คือปุ่ม "กลับเมนูหลัก" ที่ไม่ให้อะไรเลย ไม่มีการคำนวณรางวัล และไม่มีอะไร persist ข้าม run (ทั้งโปรเจกต์ **ไม่มีระบบ save เลย** — เกรป `PlayerPrefs` / `SaveData` / `ES3` ได้ 0)
2. ขาดหนักที่สุด 3 อย่างตามลำดับ : **(ก) ระบบ save/MetaSave** — ถ้าไม่มี ต่อให้คำนวณ coin ได้ก็ไม่มีที่เก็บ · **(ข) Quest ทั้งระบบ** (data model / หน้ารับ quest / checklist) — เกรป `Quest` ได้ 0 ไฟล์ · **(ค) แยก Floor Result ออกจาก Run Result + ใบเสร็จ payout** — ตอนนี้เป็นหน้าเดียวกันและไม่คิดเงิน
3. drift ที่อันตรายที่สุดไม่ใช่ของที่ขาด แต่คือ **คำเดียวกันหมายถึงคนละอย่าง** : `CurrentCoin` ในโค้ด = Fath ตาม GDD และ `ThreatLevelManager` = ระบบ Level เดิม ไม่ใช่ Threat ทั้งสองแกนของ GDD — ยืนยันตามที่ brief สงสัยไว้ **ต้องเคาะคำศัพท์ให้จบก่อนเขียนโค้ดใหม่**
4. พบ blocker เชิงโครงสร้างที่ brief ยังไม่ได้จับ : **บอสถูกสุ่มตัวตน ณ ตอน spawn** (`GetRandomEnemyDataWithTier`) ทั้งเกมมีบอส preset เดียวใช้ซ้ำทั้ง 3 ชั้น และชีตมี Feast T5 อยู่ **แค่ 2 ตัว** — ข้อกำหนด GDD ที่ว่า "quest กำหนดบอส 3 ตัวล่วงหน้าให้ผู้เล่นวางแผน" จึงยังทำไม่ได้แม้เขียนระบบ quest เสร็จ
5. minimal scope ที่ทำให้วงปิดจริงประเมินไว้ **10 งาน** (ข้อ 4) โดย 4 งานทำได้ทันทีโดยไม่ต้องรอคำตอบจากคนตัดสิน ที่เหลือรอคำตอบในข้อ 6

---

## 2. ตาราง drift

path ทั้งหมดอ้างจากราก `D:\git_project\Minesweeper\Assets\Minesweeeper\Runtime\Scripts\` (สะกดสาม e) เว้นที่ระบุเป็นอย่างอื่น

### 2.1 drift ที่ brief ระบุไว้ — ยืนยันแล้วทั้งหมด

| หัวข้อ | GDD ว่าอย่างไร | code/ชีตเป็นอย่างไร | หลักฐาน | ข้อเสนอ |
| --- | --- | --- | --- | --- |
| Quest | เป็น checklist ของ run + เงื่อนไขผ่านชั้นในอนาคต | ไม่มีเลย — `grep -rn "Quest" --include=*.cs` = 0 hits | — | สร้างใหม่ทั้งชุด (ข้อ 5.1) |
| Special Ingredient | drop 100% จากบอส T5 | ไม่มี item type นี้ · `MaterialItem` มี `currency-01` + `material-01..08` เท่านั้น · บอสทั้ง 2 ตัวใน `EnemyData` drop แต่ material ธรรมดา | ชีต `MaterialItem` · ชีต `EnemyData` แถว `enemy-15`/`enemy-16` (DropItems = material-01/02/03) | เพิ่ม enum member ท้าย `ItemTypeEnum` (ข้อ 5.2) |
| จบ run 3 ทาง | ส่งสำเร็จ / Extract / แพ้ | มี 2 ทาง · `grep -rni extract` = 0 | `GamePlay/GameplayingManager.cs:11-16` | เพิ่ม `Extracted` **ต่อท้าย** enum |
| Win = ส่ง quest ครบ | — | Win = ฆ่าบอสตัวไหนก็ได้ | `StateMachine/Gameplay/CombatGameState.cs:291-293` | แยก FloorClear (ต่อชั้น) ออกจาก RunEnd (ต่อ run) |
| Run Result มีใบเสร็จ payout | ไล่ทีละบรรทัดตามสูตร | `Show(isWin, canGoToNextFloor)` — มีแค่ win/lose group + ปุ่ม **ไม่คิดเงินเลย** | `UI/UIResultPanel.cs:39-47` · `StateMachine/Gameplay/ResultGameState.cs:18-24` | แยกหน้า (ข้อ 4 งานที่ 4-5) |
| Coin = นอกดัน / Fath = ในดัน | — | สลับกันจริง : `PlayerStatController.CurrentCoin` คือเงินที่ใช้ใน Shop/Hint/reroll = Fath ตาม GDD · `InventoryManager.SoftCurrency` เป็นกระเป๋าที่ **ได้จาก Treasure อย่างเดียวและไม่มีใครใช้จ่าย** | `Stat/PlayerStatController.cs:46-81` · `StateMachine/Gameplay/ShopGameplayState.cs:225,280` · `StateMachine/Gameplay/HintGameplayState.cs:30` · `Item/ItemDropManager.cs:57-80` | rename เป็นงานก้อนเดียว (ข้อ 4 งานที่ 0) |
| Threat 2 แกน | Pre-run (Contract) / In-run (curse) | `ThreatLevelManager` = ระบบ XP/Level เดิม : สะสม XP จากการฆ่า → level up → **สุ่ม curse 1 ใบใส่ให้เลย** + buff stat สูงสุดของมอนสเตอร์ +1 · ไม่มี Pre-run · ไม่มี Contract · ไม่มี "เลือก 1 จาก 2" | `GamePlay/ThreatLevelManager.cs:56-101` (โดยเฉพาะ `ApplyThreatLevelUp` บรรทัด 84-101) | เปลี่ยนชื่อเป็น CurseGauge แล้วเพิ่ม Pre-run แยกต่างหาก |
| ตัวคูณ coin จาก Pre-run Threat | ตัวคูณเดียวในสูตรรางวัล | ไม่มี — `ThreatLevel` ปัจจุบันไปคูณ **drop ระหว่าง run** (weapon tier + soft currency) แทน | `Item/ItemDropManager.cs:69-79,115,138,225,275` | ตัดขาดสองเรื่องนี้ออกจากกัน |
| meta progression | unlock equipment/character/recipe | ไม่มี — `grep -rn "Unlock"` = 0 · `HomeMenu` ปุ่ม Start ยิงเข้า Gameplaying ตรงๆ | `UI/Page/HomeMenu.cs:19` | ต้องมีหน้ากิลด์ (ข้อ 4 งานที่ 8) |

### 2.2 drift ที่พบเพิ่มระหว่างตรวจ — ไม่ได้อยู่ใน brief

| หัวข้อ | GDD ว่าอย่างไร | code/ชีตเป็นอย่างไร | หลักฐาน | ข้อเสนอ |
| --- | --- | --- | --- | --- |
| **ไม่มีระบบ save ใดๆ ทั้งโปรเจกต์** | Coin/unlock/BossThreatRecord ต้องอยู่ข้าม run | เกรป `PlayerPrefs` / `SaveData` / `ES3` / `JsonUtility.ToJson` เจอแต่ log กับ map editor · inventory เป็น `ScriptableObject` ที่ถูก `ClearInventory()` ทุกครั้งที่เริ่ม run | `Inventory/InventoryObject.cs:6` · `StateMachine/Gameplay/GameplayingStateController.cs:80` | **นี่คือ blocker ที่แท้จริงของ loop** ต้องทำก่อนงาน payout |
| **บอสถูกสุ่มตัวตนตอน spawn** | quest กำหนดบอส 3 ตัวล่วงหน้า ผู้เล่นเห็นชื่อ/ชั้นตั้งแต่รับ quest เพื่อวางแผน build | `EnemyData = GameDataManager.GetRandomEnemyDataWithTier(monsterData.Tier)` — ตัวตนของบอสถูกสุ่มตอนสร้างกริด ไม่ใช่ตอนรับ quest | `Stat/MonsterStatController.cs:39` | generator ต้องรับ boss id จาก RunContext (ข้อ 4 งานที่ 7) |
| **มีบอส preset เดียวใช้ซ้ำทุกชั้น + T5 ในชีตมีแค่ 2 ตัว** | 3 บอสต่างกันต่อ run | `Monster/Boss.asset` ตัวเดียว ถูกอ้างจาก `MapData_Floor01/02/03` ครบทั้งสาม · ชีต `EnemyData` มี Tier 5 แค่ `enemy-15` (jelly-udon), `enemy-16` (deer-bokchoy) | `Map/MapData_Floor0{1,2,3}.asset` · ชีต `EnemyData` | content gap — ต้องมีบอส ≥3 ตัวก่อน quest แรกจะทำงานได้จริง |
| Feast base stat ไม่ผูกกับ floor-index | "ค่าพลังพื้นฐานของ Feast มาจาก species/tier ของตัวมันเอง (ไม่ผูกกับ floor-index)" | `statGainFromFloor = currentFloor + 1` แล้วคูณ ATK/DEF/SPD/HP **และ XP** ทั้งหมด | `Stat/MonsterStatController.cs:337-346` | drift ตรงข้ามกับ GDD ชัดเจน — ต้องเคาะว่าถอด multiplier หรือแก้ GDD (**ไม่ตัดสินเองเพราะเป็นเรื่อง balance**) |
| Curse Gauge ได้ค่าคงที่ตาม Tier | "เป็นค่าคงที่ตาม Tier (T1–T5) — ไม่อิงเลเวลปัจจุบันของ Feast ตัวนั้น เพื่อกัน runaway scaling" | `AddThreatXp(monster.XP)` โดย `XP = preset.XP * (currentFloor+1)` → ค่าเกจโตตามชั้น | `StateMachine/Gameplay/CombatGameState.cs:329` + `Stat/MonsterStatController.cs:345` | เป็น runaway scaling ที่ GDD สั่งห้ามไว้ตรงๆ |
| Curse Gauge รีเซ็ตทุกครั้งที่เปลี่ยนชั้น | GDD หัวข้อ Curse Gauge + Floor Clear | `ThreatLevelManager` ไม่มีเมธอด Reset เลย และ `OnNextFloorButtonClicked` ไม่เรียกอะไรที่รีเซ็ตมัน — เกจสะสมยาวทั้ง run | `GamePlay/ThreatLevelManager.cs` (ทั้งไฟล์) · `StateMachine/Gameplay/ResultGameState.cs:54-62` | เพิ่ม `ResetGauge()` ตอนเปลี่ยนชั้น โดย curse ที่รับไปแล้วต้องไม่หาย |
| curse scaling = ATK/HP % + 1 action ต่อ 2 curse ไม่ scale SPD/Charge | GDD หัวข้อ Curse Gauge | โค้ดทำ `AddEnemyHighestStatPlus(1)` = +1 กับ stat ที่สูงที่สุด (ATK/DEF/SPD ตัวใดตัวหนึ่ง) — คนละกติกาทั้งหมด และแตะ SPD ได้ด้วย | `GamePlay/ThreatLevelManager.cs:96` | mirror กติกา GDD และต้องแก้ sim engine ทั้งสองตัวพร้อมกัน (`simulate/README.md`) |
| Curse = เลือก 1 จาก 2 (บังคับเลือก) | GDD + UX ข้อ 2 | `GetRandomPickableModifiers(1, Curse)` แล้ว `AddModifier` ให้ทันที — ผู้เล่นไม่ได้เลือก | `GamePlay/ThreatLevelManager.cs:88-92` | ทำหน้า Curse Choice ตาม UX ข้อ 2 |
| **ห้ามแสดง Coin ระหว่างอยู่ในดันเจี้ยน** | UX ข้อ 0 : "ในดันเจี้ยนใช้ Fath เท่านั้น" | HUD แสดง **สองกระเป๋าพร้อมกัน** : `ShowCoin` แสดง `CurrentCoin` ต่อท้ายด้วย `"F"` (Fath) ส่วน `UIGameplayController.PopulateMoney()` แสดง `SoftCurrency` = `currency-01` ซึ่ง localize key คือ `material-coin-name` | `UI/showCoin.cs:31` · `UI/UIGameplayController.cs:632-637` · ชีต `MaterialItem` แถว `currency-01` | ถอดกระเป๋าที่สองออกจาก HUD ในดัน หรือยุบให้เหลือกระเป๋าเดียว |
| `MaterialItem.Type` ต้องเป็น `Material` | Sync Guide ข้อ 4.3 + `GetAllMaterials()` กรองด้วย `ItemType == Material` | **`material-04` (cantonese), `material-05` (lettuce), `material-06` (meat 2), `material-07` (spring onion) มี Type = `None`** ทั้งในชีตและใน asset ที่ Pull มาแล้ว → 4 ตัวนี้จะไม่โผล่ในลิสต์วัตถุดิบ/หน้าทำอาหาร | ชีต `MaterialItem` (gid 1070535420) · `GameData/Config/ScriptableObject/MaterialtemConfig.asset:131,155,179,203` · `Inventory/InventoryManager.cs:28` | **data bug ที่แก้ได้ทันที** (แก้ 4 เซลล์ → Pull) — ไม่ได้แก้ให้เพราะ brief ห้ามเขียนชีต |
| แท็บ `PlayerXP` + `GameConfig.maxPlayerLevel` / `statIncreasePerLevel` / `freeStatPointPerLevel` | GDD : "ระบบ Level-based stat growth ถูกถอดออกทั้งหมด" | ยังอยู่ในชีต (`maxPlayerLevel 50`, `PlayerXP` มีตารางเต็ม) และ `statIncreasePerLevel = 0` แปลว่าถูกทำให้เป็นหมันแทนที่จะถอด | ชีต `GameConfig`, `PlayerXP` · `GameData/Config/GameConfig.cs:20-28` | retire ทีเดียวพร้อมงาน rename (ข้อ 6 คำถามที่ 7) |
| `game_document/Sumeeper_GameData.xlsx` (offline mirror) | CLAUDE.md + Sync Guide ข้อ 1 อ้างว่ามีไฟล์นี้ | **ถูกลบไปแล้ว** ใน commit `e15a39b` (774 KB → 0) — agent ที่เชื่อเอกสารจะหาไฟล์ไม่เจอ (รอบนี้อ่านจากชีตสดผ่าน `simulate/tools/gsheet.py` แทน) | `git log --diff-filter=D -- game_document/Sumeeper_GameData.xlsx` | สร้าง snapshot ใหม่ (`gsheet.py dump`) หรือแก้ CLAUDE.md ให้ตรง |

---

## 3. ตาราง gap

ขนาดงานเป็นการประเมินหยาบของงาน implement ฝั่ง Unity : **S** ≈ ≤1 วัน · **M** ≈ 2–4 วัน · **L** ≈ ≥1 สัปดาห์

| # | สิ่งที่ขาด | ขวางอะไร | ขนาด | ลำดับ |
| --- | --- | --- | --- | --- |
| 1 | **ระบบ save / MetaSave** (Coin, unlock, CompletedQuestCount, BossThreatRecord) | ขวางทุกอย่างที่อยู่หลังคำว่า "จบ run" — coin ที่คำนวณได้ไม่มีที่เก็บ | M | 1 |
| 2 | **การตัดสินคำศัพท์ Coin/Fath + Threat** แล้ว rename ในโค้ด | ขวางการเขียนโค้ดใหม่ทุกบรรทัด (คนละภาษากับ GDD) และยิ่งเลื่อนยิ่งแพง | M | 1 |
| 3 | **RunContext** (run-scoped state : QuestId, PreRunThreat, CollectedSpecialIngredientIds, ExitReason) | ขวาง payout, checklist, quest ทั้งหมด — ตอนนี้ state กระจายตาม manager ไม่มีที่รวม | S | 2 |
| 4 | **แยก Floor Result ออกจาก Run Result** | ตอนนี้ `ResultGameState` เป็นหน้าจบชั้น แต่พอถึงชั้นสุดท้ายกลายเป็นหน้าจบ run โดยไม่มีเนื้อหาของ run เลย | M | 2 |
| 5 | **สูตร payout + ใบเสร็จ** (UX ข้อ 6 ช่วงที่ 2) | ไม่มี coin = ไม่มี progression | M | 3 |
| 6 | **Special Ingredient** : item type, mapping boss→ingredient, drop 100% | เป็นทั้ง objective ของ quest และตัวแปรหลักของสูตรรางวัล | M | 3 |
| 7 | **Quest data model + checklist HUD + สถานะส่งสำเร็จ** | เป็น objective ของ run ทั้งอัน | L | 4 |
| 8 | **บอสถูกกำหนดจาก quest** (generator รับ boss list) + บอส ≥3 ตัวในชีต | quest ที่ขอของจากบอส 3 ตัวสร้างไม่ได้ ถ้าบอสยังสุ่มและมีตัวเดียว | M (โค้ด) + M (content) | 4 |
| 9 | **Extract** (`GameResultEnum.Extracted` + ปุ่มใน Floor Result + popup ยืนยัน) | ตัดการตัดสินใจแบบ extraction ซึ่งเป็นแกน risk/reward ของเกม | S | 5 |
| 10 | **หน้ากิลด์** : รับ quest, ร้าน unlock, เห็นบอส 3 ตัว | เป็นหัวและหางของ loop — ตอนนี้ Start ยิงเข้าดันเจี้ยนตรงๆ | L | 5 |
| 11 | **Pre-run Threat + The Curse Contract** + ป้าย "บอสตัวไหนให้/ไม่ให้ของ" | ทำให้ตัวคูณรางวัลเป็น 1.0 ตายตัว = risk/reward ก่อน run หายทั้งแกน | L | 6 |
| 12 | **Unlock** (equipment/character/recipe + เงื่อนไข + ราคา) | ปลายทางของ coin — ถ้าไม่มี coin ก็ไม่มีความหมาย | M | 6 |
| 13 | **Curse Choice 1-of-2 + reset เกจต่อชั้น + scaling ตาม GDD** | ไม่ขวาง loop โดยตรง แต่เป็น drift ที่กระทบ balance ทั้งเกม และต้อง mirror ลง sim engine ทั้งสองตัว | M | 7 |

---

## 4. Minimal scope ที่ทำให้ loop ปิด

เป้าหมาย : เล่นได้ครบวง **รับ quest → เข้าดัน → จบ run → ได้ coin → ปลดล็อคของ → รับ quest ใหม่**

หลักที่ใช้ตัด : ทุกอย่างที่ **ไม่ได้อยู่บนเส้นวง** ถูกเลื่อนออกแม้จะอยู่ใน GDD — โดยเฉพาะ **Pre-run Threat ให้ตรึงเป็น 0 และตัวคูณ = 1.0** ในเฟสนี้ (Contract เป็นงานก้อนใหญ่ที่ต่อทีหลังได้โดยไม่ต้องรื้อ ถ้าเขียนสูตร payout ให้รับตัวคูณจากภายนอกตั้งแต่แรก)

| # | งาน | ขนาด | รอคำตอบข้อ 6? |
| --- | --- | --- | --- |
| 0 | **เคาะคำศัพท์แล้ว rename ให้ตรง GDD** — `PlayerStatController.CurrentCoin` → `Fath` · `ThreatLevelManager` → `CurseGaugeManager` (`ThreatLevel` → `AcceptedCurseCount`) · จัดการกระเป๋า `SoftCurrency` ที่ไม่มีใครใช้ · retire `PlayerXP` / `maxPlayerLevel` | M | **รอข้อ 7, 11** |
| 1 | **MetaSave + ระบบ save** — JSON ไฟล์เดียว : `Coin`, `UnlockedIds[]`, `CompletedQuestIds[]`, `BossThreatRecord` | M | ไม่ต้องรอ |
| 2 | **RunContext** — object run-scoped ที่ถือ `QuestId`, `PreRunThreat` (ยัง = 0), `CollectedSpecialIngredientIds`, `Fath`, `ExitReason` | S | ไม่ต้องรอ |
| 3 | **Special Ingredient** — เพิ่ม `SpecialIngredient` **ต่อท้าย** `ItemTypeEnum` (ห้ามแทรกกลาง — asset เก็บ enum เป็น index) + คอลัมน์ `SpecialIngredientId` ใน `EnemyData` + drop 100% ที่ `HandleMonsterDeath` | M | **รอข้อ 4** |
| 4 | **แยก state จบชั้น/จบ run** — `FloorResultGameState` (ปุ่ม: ลงชั้นถัดไป / Extract) กับ `RunResultGameState` (ใบเสร็จ) + เพิ่ม `GameResultEnum.Extracted` ต่อท้าย enum | M | **รอข้อ 12** |
| 5 | **สูตร payout + ใบเสร็จ** ตาม GDD หัวข้อ Reward และ UX ข้อ 6 ช่วงที่ 2 — เขียนเป็น service ที่รับ `RunContext` แล้วคืน ledger ทีละบรรทัด (unit-test ได้โดยไม่ต้องเปิดเกม) แล้วบวก coin เข้า MetaSave | M | **รอข้อ 6** (เขียนโครงได้เลย ใส่ตัวคูณ 1.0 ไปก่อน) |
| 6 | **Quest data model + checklist** — แท็บ `Quest` (ข้อ 5.1) + checklist บน HUD ระหว่าง run + เงื่อนไข "ส่งสำเร็จ" = ครบ 3 ชิ้น **และ** `ExitReason != Death` | L | **รอข้อ 1, 2, 3, 5** |
| 7 | **บอสมาจาก quest** — `EncounterGenerator` / `MonsterStatController.InitMonster` รับ boss id จาก RunContext แทน `GetRandomEnemyDataWithTier` + เพิ่มบอสในชีตให้ ≥3 ตัว + แยก `Boss.asset` ต่อชั้น | M + M | **รอข้อ 1, 10** |
| 8 | **หน้ากิลด์ขั้นต่ำ** — ลิสต์ quest ที่รับได้, ปุ่มรับ, โชว์บอส 3 ตัวของ quest, ร้าน unlock ที่ใช้ coin | L | **รอข้อ 2, 3** |
| 9 | **Unlock ขั้นต่ำ** — แท็บ `Unlock` (ข้อ 5.4) + ตรวจเงื่อนไขตอนจบ run + แสดงตาม UX ข้อ 6 ช่วงที่ 3 | M | ไม่ต้องรอ |

**เลื่อนออกจากเฟสนี้ได้** (ไม่อยู่บนเส้นวง) : The Curse Contract / Pre-run Threat จริง, Curse Choice 1-of-2, Floor Variant, การแก้ scaling ให้ตรง GDD — ยกเว้น **ถ้าตัดสินใจแก้ scaling ต้อง mirror ลง sim engine ทั้ง Python และ JS ในรอบเดียวกัน** ตาม `simulate/README.md`

**ทำได้ทันทีโดยไม่ต้องรอใคร** : งานที่ 1, 2, 9 + แก้ `MaterialItem.Type` ของ material-04..07 ในชีต

**เห็นด้วยกับ straw-man ของ brief ข้อ 5.4** เรื่องแยก `IFloorClearCondition` — ตอนนี้เงื่อนไขผ่านชั้นฝังอยู่ที่ `CombatGameState.cs:291` เป็น `if (monster.IsBoss)` บรรทัดเดียว การดึงออกเป็น interface ตอนแยก state (งานที่ 4) ราคาถูกมาก และทำให้เปลี่ยนไปใช้ quest checklist ทีหลังได้โดยไม่แตะ state machine

**ต่างจาก straw-man หนึ่งข้อ** : brief จัด rename เป็น "งานก้อนเดียวทำก่อนงานอื่น" — เห็นด้วยว่าต้องทำก่อน แต่เสนอให้ **จำกัดขอบเขตเฉพาะสิ่งที่อยู่บน critical path ของ loop** (Coin→Fath, ThreatLevelManager→CurseGauge) แล้วปล่อย rename ส่วนที่เหลือไว้ก่อน เพราะมี feature branch ค้างหลายอันตามที่ brief เอง flag ไว้ — rename ทั้งโปรเจกต์รอบเดียวจะทำให้ทุก branch ที่ค้างอยู่ merge เจ็บพร้อมกัน

---

## 5. ข้อเสนอ data model

หัวคอลัมน์เขียนตามฟอร์แมตใน `Sumeeper_GameData_Sync_Guide.md` ข้อ 4.1 (`Name` / `Description` = **key** ของ localization ไม่ใช่ข้อความ · list/object = JSON · enum = ชื่อสมาชิกตามแท็บ `_enum`)
**ยังไม่ได้เขียนลงชีตจริง** ตามข้อห้ามใน brief

### 5.1 แท็บใหม่ `Quest` → asset `QuestConfig` · Layout `Table` · string table ใหม่ `Quest`

| Id | Name | Description | BossIds | FloorCount | UnlockType | UnlockValue | IsStarter |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `quest-01` | `quest-01-name` | `quest-01-description` | `["enemy-15","enemy-16","enemy-17"]` | `3` | `None` | `0` | `TRUE` |

- `BossIds` = **source of truth ของบอสใน run นั้น** เรียงตามชั้น (index 0 = ชั้นแรก) ต้องเป็น `EnemyData.Id` ที่ `Tier = 5`
- วัตถุดิบที่ quest ขอ **ไม่เก็บซ้ำในแท็บนี้** — derive จาก `EnemyData.SpecialIngredientId` ของบอสแต่ละตัว (ข้อ 5.2) เพื่อไม่ให้มีสองที่ที่ขัดกันได้
- `FloorCount` แยกจากจำนวนบอส เพื่อรองรับคำตอบข้อ 6 คำถามที่ 1 (บอส 3 ตัวใน 6 ชั้น) — ถ้าคำตอบคือ "บอส 3 ตัว 3 ชั้น" คอลัมน์นี้ก็เท่ากับ 3 เสมอ
- `UnlockType` / `UnlockValue` = เงื่อนไขปลดล็อค quest — ต้องเพิ่มคอลัมน์ enum ใหม่ในแท็บ `_enum` : `None`, `QuestCompleted`, `BossDefeated`

### 5.2 คอลัมน์ใหม่ในแท็บ `EnemyData` (แนะนำ) แทนการทำแท็บแยก

| คอลัมน์ | ค่า | หมายเหตุ |
| --- | --- | --- |
| `SpecialIngredientId` | `special-01` / เว้นว่างถ้าไม่ใช่บอส | 1:1 กับบอสตามที่ GDD กำหนด |

เหตุผลที่เลือกทางนี้แทนแท็บ `BossReward` แยก : ความสัมพันธ์เป็น 1:1 กับแถวบอสอยู่แล้ว · Sync Guide ข้อ 4.2 ระบุว่า "แถวแม่เป็นเจ้าของความสัมพันธ์" · เพิ่มคอลัมน์ในแท็บเดิมปลอดภัยกว่าเพิ่มแท็บ (แค่ header→field mapping ไม่ต้องตั้ง Sheet Sync entry ใหม่)

**แถวใหม่ในแท็บ `MaterialItem`** — วัตถุดิบพิเศษเป็นแถวปกติ ใช้ `Type` ค่าใหม่

| Id | Name | Description | Type | Rarity | AtlasName | SpriteName | Cost | IsEnemyOnly | IsSystemItem |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `special-01` | `special-01-name` | `special-01-description` | `SpecialIngredient` | `Legendary` | `MaterialAtlas` | *(รออาร์ต)* | `0` | `FALSE` | `FALSE` |

> ⚠ **`SpecialIngredient` ต้องเพิ่มต่อท้าย `ItemTypeEnum` (`Inventory/InventoryManager.cs:326-334`) เท่านั้น** — asset เก็บ enum เป็น index (`type: 3` = Material) การแทรกกลางจะทำให้ทุกแถวที่มีอยู่เพี้ยนเป็นชนิดอื่น (หมายเหตุเดียวกับหัวข้อ Ability ใน GDD)
> `Cost = 0` ตั้งใจ : วัตถุดิบพิเศษต้องไม่ขึ้นร้าน — ต้องมีเงื่อนไขกันในโค้ดด้วย ไม่ใช่พึ่ง Cost อย่างเดียว (Sync Guide ข้อ 4.3 : Cost ว่าง = ขายฟรี)

### 5.3 แท็บใหม่ `ThreatReward` → asset `ThreatRewardConfig` · Layout `Table`

| PreRunThreat | CoinMultiplier |
| --- | --- |
| `0` | `1.0` |
| `1` | *(ให้คนจูนกรอก)* |
| `2` | *(ให้คนจูนกรอก)* |

**ทุกช่องนอกจากแถว 0 เว้นว่างไว้ให้คนจูน** — แถว `0 → 1.0` เป็น identity ไม่ใช่การจูน ใส่ไว้เพื่อให้ minimal scope รันได้โดยไม่ต้องรอคำตอบข้อ 6 คำถามที่ 6

### 5.4 แท็บใหม่ `Unlock` → asset `UnlockConfig` · Layout `Table`

| Id | TargetType | TargetId | CoinCost | RequireQuestCompleted | RequireBossIds |
| --- | --- | --- | --- | --- | --- |
| `unlock-01` | `Equipment` | `weapon-xx` | *(ให้คนจูนกรอก)* | `0` | `[]` |
| `unlock-02` | `Recipe` | `recipe-xx` | *(ให้คนจูนกรอก)* | `3` | `["enemy-15"]` |

`TargetType` = คอลัมน์ enum ใหม่ในแท็บ `_enum` : `Equipment`, `Character`, `Recipe` (ตาม GDD หัวข้อ Core gameloop + Special Ingredients)

### 5.5 เพิ่มใน `GameConfig` (KeyValue)

| Key | Value | ที่มา |
| --- | --- | --- |
| `coinPerSpecialIngredient` | `[0,100,300,500]` | GDD หัวข้อ Reward (ยกมาจาก GDD ไม่ใช่ตัวเลขที่ตั้งเอง) |
| `fathToCoinRate` | `10` | GDD หัวข้อ Reward (1 fath : 10 coin) |
| `specialIngredientsPerQuest` | `3` | GDD หัวข้อ Quest |

### 5.6 สูตร payout ที่แปลจาก GDD — reviewer ตรวจแล้วว่าตรง

```
coinFromIngredients = coinPerSpecialIngredient[ collected.Count ]        // 0 / 100 / 300 / 500
coinFromFath        = (exitReason == Death) ? 0 : remainingFath * 10
total               = (coinFromIngredients + coinFromFath) * threatMultiplier[preRunThreat]

questComplete       = collected.Count == 3 && exitReason != Death
วัตถุดิบธรรมดา       = ไม่เข้าสูตร แต่ต้องแสดงจำนวนที่เหลือ (UX ข้อ 6 ช่วงที่ 2)
```

ตรวจกับ GDD หัวข้อ Reward แล้วตรงทุกบรรทัด รวมถึงกติกา "แพ้ = ได้ coin จากวัตถุดิบพิเศษที่เก็บได้แล้ว แต่ fath ถูกริบทั้งหมด และไม่นับว่าส่งสำเร็จแม้เก็บครบ 3 ชิ้น" — straw-man ของ brief ข้อ 5.2 แปลถูกแล้ว

### 5.7 MetaSave — ไม่ใช่ชีต เป็นไฟล์ save ฝั่ง client

```
MetaSave (JSON, persist ข้าม run)
  Coin : int
  UnlockedIds : string[]              // อ้าง Unlock.TargetId
  CompletedQuestIds : string[]
  BossThreatRecord : { bossId : int } // Pre-run Threat สูงสุดที่เคยล้มบอสตัวนั้นสำเร็จ
```

`BossThreatRecord` เป็นตัวตัดสินสิทธิ์วัตถุดิบพิเศษตาม GDD หัวข้อ Threat : ให้ก็ต่อเมื่อ `currentPreRunThreat > BossThreatRecord[bossId]` — เห็นด้วยกับ straw-man ของ brief ข้อ 5.1 ทุกประการ **แต่เตือนว่ากติกานี้สร้างเคสตันที่ GDD ยังไม่ปิด** (ข้อ 6 คำถามที่ 5)

### 5.8 RunContext — run-scoped ไม่ persist

```
RunContext
  QuestId · PreRunThreat · ContractCurseIds[]
  BossIds[]                       // สำเนาจาก Quest ตอนรับ — ล็อกไว้กันชีตเปลี่ยนกลาง run
  CollectedSpecialIngredientIds[] · Fath · CurrentFloor
  AcceptedCurseIds[]              // In-run Threat = Count ของลิสต์นี้
  ExitReason : { None, QuestComplete, Extracted, Death }
```

---

## 6. คำถามค้าง

### 6.1 คำถามจาก brief ข้อ 6 — ยังไม่มีคำตอบทั้ง 7 ข้อ (ไม่ตอบเองตามที่ brief สั่ง)

1. quest 1 ชุด = กี่ชั้น (บอส 3 ตัวใน 3 ชั้น หรือกระจายใน 6 ชั้น) → กระทบคอลัมน์ `FloorCount` (ข้อ 5.1) และจำนวน `MapData` ที่ต้องสร้าง
2. quest มาจากไหน (ลิสต์มือ / สุ่มจาก pool / ปลดตาม progression) → กระทบว่าต้องมีคอลัมน์ `UnlockType` จริงไหม
3. เลือก quest ได้กี่อันต่อครั้ง / reroll ได้ไหม → กระทบหน้ากิลด์ (งานที่ 8)
4. Special Ingredient เก็บข้าม run ได้ไหม หรือถูกใช้หมดตอนส่ง quest → **กระทบว่าต้องมีช่องใน MetaSave หรือไม่** ต้องได้คำตอบก่อนเริ่มงานที่ 3
5. ล้มบอสเดิมซ้ำที่ Threat เท่าเดิม → ไม่ได้ของ แล้ว quest ที่ขอชิ้นนั้นส่งสำเร็จได้ไหม → **เคสตันที่ทำให้ผู้เล่นเล่นต่อไม่ได้ ต้องปิดก่อนปล่อย**
6. ตัวคูณ coin ต่อ 1 Pre-run Threat → ตาราง 5.3
7. `MaxThreatLevel` / `MoneyGainPerMonsterTier` / `CurrencyGainMultiplier` จะ retire หรือ remap → กระทบงานที่ 0

### 6.2 คำถามที่พบเพิ่มระหว่างตรวจ

8. **Feast base stat ยังคูณด้วย `floor+1` อยู่ (`MonsterStatController.cs:339`) ทั้งที่ GDD เขียนว่า "ไม่ผูกกับ floor-index" — จะถอด multiplier ตาม GDD หรือแก้ GDD ให้ยอมรับของที่มี?** เป็นเรื่อง balance ล้วนจึงไม่ตัดสินเอง แต่ต้องตัดสินก่อนงานจูนรอบหน้า เพราะ sim engine ทั้งสองตัวอิงกติกา GDD
9. **Curse Gauge ควรรีเซ็ตต่อชั้นตาม GDD หรือสะสมยาวตามที่โค้ดทำอยู่?** ถ้ารีเซ็ตตาม GDD ต้องนิยาม "Max ของชั้นนั้น" และจำนวน threshold ต่อชั้น ซึ่งยังไม่มีที่ไหนเลย — ทั้ง GDD ชีต และโค้ด
10. **บอส T5 ในชีตมีแค่ 2 ตัว แต่ quest ต้องใช้ 3 ตัวต่อ run — จะเพิ่มบอสใหม่ หรือให้ quest ใช้บอสซ้ำได้ต่างชั้น?** (ถ้าใช้ซ้ำได้ ต้องนิยามว่าวัตถุดิบพิเศษซ้ำนับเป็น 2/3 หรือ 1/3)
11. **`SoftCurrency` (`currency-01`) จะเอาอย่างไร** — เป็นกระเป๋าที่ได้จาก Treasure อย่างเดียวและไม่มีใครใช้จ่าย : จะยุบเข้ากับ Fath, ทำให้เป็น Coin จริงตาม GDD, หรือถอดทิ้ง? (ถ้าถอดต้องจัดการแถว `currency-01` ในชีตด้วย)
12. **หน้า Result ปัจจุบันเป็นทั้ง Floor Result และ Run Result** — ตอนแยกออกจากกัน จะเก็บ `UIResultPanel` เดิมไว้เป็น Floor Result แล้วสร้าง Run Result ใหม่ หรือสร้างใหม่ทั้งสองหน้า? (กระทบขนาดงานที่ 4 ระหว่าง M กับ L)
