# คู่มือแก้ไข Google Sheet และระบบ Pull/Push ของ Unity (สำหรับ agent)

อัปเดต 2026-09-05 · เขียนจากการไล่โค้ดจริงใน `D:\git_project\Minesweeper` และการทำงานจริงกับชีตทั้งสองตัว

อ่านคู่กับ `simulate/tools/gsheet.py` (เครื่องมืออ่าน/เขียนชีต) และ `Assets/Minesweeeper/Editor/GameDataSheetSync/README.md` ในโปรเจกต์ Unity (คู่มือของตัว sync เอง)

---

## 1. ภาพรวม: ข้อมูลอยู่ที่ไหน อะไรเป็นต้นทาง

| แหล่ง | คืออะไร | ใครอ่าน |
| --- | --- | --- |
| **Google Sheet `Sumeeper_GameData`** (id `1Tni3eLd67CDvaygLQ_1RrWSSNK01EgXz_eUB6wDZHqQ`) | ค่า config ทุกตัวที่เกมโหลดจริง 18 แท็บ | Unity ผ่านหน้าต่าง Sheet Sync (Pull เข้า ScriptableObject) |
| **Google Sheet `Sumeeper_Localize`** (id `1y_xoIiqclAEgq96TrAIq2rdf78ucWmR4M2YXziL7BrI`) | ข้อความทุกภาษา แยกแท็บตาม string table (Meal, Recipe, Weapon, Perk, Curse, Material, Monster, Skill, Sumeeper_Localize) | Unity Localization package (คนละระบบกับ Sheet Sync) |
| `game_document/Sumeeper_GameData.xlsx` | **สำเนา offline** ของชีต GameData ใช้อ่านเร็วและ diff ได้โดยไม่ต้องต่อเน็ต | agent |
| `game_document/Sumeeper_*_Sheet.xlsx` (Meal, Equipment, Monster, Curse, Perk) | **เอกสารออกแบบ** ของทีม ไม่ใช่สิ่งที่ Unity อ่าน | คนออกแบบ, agent |
| `game_document/Sumeeper_GDD.md` | กติกาเกม canonical | ทุกคน |
| ScriptableObject ใน `Assets/Minesweeeper/Runtime/Scripts/GameData/Config/ScriptableObject/*.asset` | สิ่งที่ build จริงใช้ ได้มาจากการ Pull | Unity runtime |

หลักคิด: **GDD บอกกติกา → ชีตออกแบบบอกเจตนา → GameData Sheet คือค่าที่เกมใช้ → asset ใน Unity คือสำเนาล่าสุดที่ Pull มา** ถ้าสี่อย่างนี้ไม่ตรงกัน ให้รายงาน drift ไม่ใช่เดาเอง

---

## 2. การเข้าถึงชีต

### 2.1 Credential

- ใช้ **service account** `sumeeper-gamedata@sumeeper.iam.gserviceaccount.com` ตัวเดียวกับที่ Unity ใช้
- ไฟล์ key (gitignored ทั้งสองที่ ห้าม commit ห้าม print เนื้อหา):
  - `D:\Sumeeper\sumeeper-4ad3bba50861.json`
  - `D:\git_project\Minesweeper\Secrets\sumeeper-4ad3bba50861.json` (path ที่ Sheet Sync ตั้งไว้ใน `GameDataSheetSyncSettings.asset`)
- ชีตทั้งสองตัวถูกแชร์ให้ service account เป็น Editor แล้ว ถ้าได้ HTTP 403 แปลว่ามีชีตใหม่ที่ยังไม่ได้แชร์ ให้ขอผู้ใช้กด Share ให้อีเมลข้างต้น
- ถ้าไม่มี key บนเครื่อง จะทำอะไรกับชีตไม่ได้เลย (ลิงก์เป็น private, API key อ่านได้เฉพาะชีตสาธารณะ) ให้ขอผู้ใช้วางไฟล์ key ก่อน

### 2.2 เครื่องมือ

ต้องมี `google-auth` และ `google-api-python-client` (`pip install google-auth google-api-python-client`)

```bash
python simulate/tools/gsheet.py info            # ชื่อแท็บ + gid + ขนาด
python simulate/tools/gsheet.py read MealStat   # อ่านแท็บเป็น TSV
python simulate/tools/gsheet.py dump out.xlsx   # snapshot ทุกแท็บ
```

ในสคริปต์อื่นใช้ `import gsheet; svc = gsheet.service(); gsheet.read(svc, tab); gsheet.write(svc, tab, rows)`
สำหรับชีต localization ใช้ `svc.spreadsheets().values()` กับ id ของชีตนั้นโดยตรง (ดูตัวอย่างในหัวข้อ 6)

`simulate/tools/meal_stat.py` เป็นตัวอย่างเครื่องมือเฉพาะทาง: คำนวณ MealStat จากน้ำหนักวัตถุดิบ, dry-run เทียบค่าจริง, `--write` เมื่อได้รับอนุญาต

### 2.3 กติกาการเขียน

1. **อ่านและ diff ได้เสมอ แต่เขียนลงชีตเมื่อผู้ใช้สั่งชัดเจนเท่านั้น** ตัวเลข balance เป็นของคนจูน (ดู CLAUDE.md) ถ้ายังไม่ได้สั่ง ให้ทำเป็นข้อเสนอใน `game_document/proposals/` พร้อมเหตุผลและตารางที่พร้อมกรอก
2. ก่อนเขียน ให้ **อ่านแท็บนั้นมาก่อนและพิมพ์ dry-run** (ค่าเดิม → ค่าใหม่) เขียนเสร็จให้อ่านกลับมาตรวจ
3. `gsheet.write()` เขียนทับจาก A1 แต่ **ไม่ล้างแถวที่อยู่ต่ำกว่าข้อมูลใหม่** ถ้าจำนวนแถวลดลงต้องเคลียร์แถวส่วนเกินเอง (หรือใช้ `values().clear` ก่อน)
4. คงแถวระบบไว้เสมอ เช่น `meal-unknown`, `meal-junk` ใน MealItem และ `weapon-fist` ใน WeaponItem/WeaponStat (ถูกอ้างจาก GameConfig)
5. หลังเขียนชีต ให้ **อัปเดตสำเนา xlsx** ในโปรเจกต์ให้ตรง (`dump` ทั้งไฟล์ หรือเขียนทับเฉพาะแท็บด้วย openpyxl) และบันทึกสถานะในเอกสาร proposal ที่เกี่ยวข้อง
6. อย่าแตะแท็บ `_enum` ด้วยมือ ระบบ Push สร้างและ merge เอง

---

## 3. แผนที่แท็บ GameData → asset ใน Unity

| แท็บ | gid | asset (ScriptableObject) | Layout | string table ที่ Name/Description อ้าง |
| --- | --- | --- | --- | --- |
| `_enum` | 1479094555 | (ระบบสร้าง) รายการ enum สำหรับ dropdown | — | — |
| `GameConfig` | 0 | `GameConfig` | KeyValue | — |
| `EnemyData` | 1198172807 | `EnemyData` (EnemyDataConfig) | Table + child `EnemySkillData` | Monster |
| `EnemySkillData` | 1825548156 | (แท็บลูกของ EnemyData) | Table | — |
| `Perk` | 695276241 | `NewPerk` (ModifierConfig) | Table | Perk |
| `Curse` | 1915792882 | `NewCurse` (ModifierConfig) | Table | Curse |
| `WeaponStat` | 1229638342 | `WeaponStatConfig` | Table + child `WeaponSkillData` | — |
| `WeaponSkillData` | 1971665255 | (แท็บลูกของ WeaponStat) | Table | — |
| `PlayerXP` | 1332930404 | `PlayerXPConfig` | Table | — |
| `WeaponDrop` | 1884556795 | `WeaponDropConfig` | Table (Drops เป็น JSON) | — |
| `WeaponSet` | 990583394 | `WeaponSetConfig` | Table (SetBonuses เป็น JSON) | — |
| `ForgeRecipe` | 1710035258 | `ForgeRecipeConfig` | Table | — |
| `MaterialItem` | 1070535420 | `MaterialtemConfig` (สะกดแบบนี้จริง) | Table | Material |
| `WeaponItem` | 1362033112 | `WeaponItemConfig` | Table | Weapon |
| `MealItem` | 410281667 | `MealItemConfig` | Table | Meal |
| `MealStat` | 1565312550 | `MealStatConfig` | Table | — |
| `MealRecipe` | 1522967372 | `MealRecipeConfig` | Table (MaterialIds เป็น JSON) | — |
| `RecipeItem` | 2127034453 | `RecipeItemConfig` | Table | Recipe |

รายการ binding อยู่ที่ `Assets/Minesweeeper/Editor/GameDataSheetSync/GameDataSheetSyncSettings.asset` (ดูช่อง `defaultLocalizationTable` ของแต่ละ entry ด้วย)

---

## 4. รูปแบบข้อมูลในเซลล์และสัญญาของ id

### 4.1 รูปแบบเซลล์

| ชนิด field | ในเซลล์ | ตัวอย่าง |
| --- | --- | --- |
| int / float | ตัวเลขล้วน จุดทศนิยมเป็น `.` | `50`, `0.5` |
| bool | `TRUE` / `FALSE` | |
| enum | ชื่อสมาชิกตามแท็บ `_enum` (ตัวพิมพ์ต้องตรง) | `OnHalf`, `GainStatusEffect`, `Armor` |
| list / object | JSON หนึ่งบรรทัดหรือหลายบรรทัดก็ได้ | `["material-01","material-02"]`, `[{"rarity":"Common","rate":70}]` |
| LocalizedString (Name, Description, ModifierName) | **key** ในตาราง localization ไม่ใช่ข้อความ | `meal-kimchi-name` |
| asset reference | path ของ asset | (ไม่มีในแท็บปัจจุบัน) |

header คือชื่อ field ใน C# ขึ้นต้นตัวใหญ่ (`Id`, `MaxHP`, `SkillTriggerType`) การ Pull จับคู่แบบไม่สนตัวพิมพ์ คอลัมน์ที่ไม่ตรง field ใดจะถูก**ข้ามพร้อม warning** ไม่ใช่ error

### 4.2 id ที่เป็นสัญญากับโค้ด (ห้ามเปลี่ยนโดยไม่แก้โค้ด/ข้อมูลอีกฝั่ง)

- **`RecipeItem.Id` ต้องเท่ากับ `MealRecipe.Id` หนึ่งต่อหนึ่ง** หน้าทำอาหารเอา id ของไอเทมสูตรที่ถืออยู่ไปค้น MealRecipe โดยตรง (`UICookPanelPresenter`) ดังนั้น `recipe-01` ทั้งสองแท็บคือของคู่กัน
- **id ของ skill ในแท็บลูก** (`EnemySkillData`, `WeaponSkillData`) ถูกอ้างจากคอลัมน์ `Skills` ของแท็บแม่ แถวแม่เป็นเจ้าของความสัมพันธ์ เพิ่ม skill ให้ศัตรูโดยเติม id ในลิสต์ของแถวแม่ แถวลูกที่ไม่มีใครอ้างจะถูกรายงาน ไม่ถูกลบ
- `MealRecipe.MealId` → `MealItem.Id` และ `MealStat.Id` ต้องมีครบสามที่
- `EnemyData.WeaponIds` → `WeaponStat.Id` (อาวุธของมอนสเตอร์ตั้ง `IsEnemyOnly=TRUE` ใน WeaponItem)
- `ForgeRecipe.InputWeaponId/OutputWeaponId` → `WeaponStat.Id` และ `WeaponItem.Id`
- `GameConfig.FistWeaponId / FailedMealId / UnknownMealId` → id ที่ต้องมีอยู่จริง
- `MealStat.BuffId` ยังไม่มีโค้ดอ่าน (2026-09-05) เว้นว่างไว้จนกว่าจะมี contract

### 4.3 ค่าที่ห้ามว่าง

- `Cost` ของทุก item ที่ `IsEnemyOnly=FALSE` และ `IsSystemItem=FALSE` เพราะร้านค้าและ drop ดึงเข้าพูลทั้งหมด ว่าง = ขายฟรี
- `Name` ของ item ที่ผู้เล่นเห็น (ว่างได้เฉพาะแถวระบบอย่าง `meal-unknown`)
- `AtlasName` ต้องเป็น atlas ที่มี sprite ชื่อนั้นจริง (Meal ใช้ `MealAtlas` ซึ่งตอนนี้มีรูป Steak, Salad, JaowPuu, Sukiyaki, UnknownRecipe, latest เท่านั้น)

---

## 5. ระบบ Sheet Sync ใน Unity (GameData)

หน้าต่าง **Tools › Game Data › Google Sheet Sync** มีปุ่ม Pull / Push รายแท็บ และ Pull All / Push All ทุกครั้งพิมพ์ report `key: old -> new` ลง Console

### 5.1 Pull (ชีต → asset)

- อ่านเฉพาะคอลัมน์ที่ match field แถวที่ไม่ match ถูกข้ามพร้อม warning จึงลบข้อมูลใน asset โดยไม่ตั้งใจไม่ได้ แต่ก็แปลว่า **คอลัมน์สะกดผิดจะเงียบหาย**
- **ล้มทั้ง entry ที่ error แรก** ไม่มี partial apply (เช่น key localization ไม่มี) แก้แล้ว Pull ใหม่ทั้งแท็บ
- แถวใหม่ที่ asset ยังไม่มี ระบบ **copy element สุดท้ายของ list มาเป็นต้นแบบ** แล้วทับด้วยค่าจากชีต ผลข้างเคียงสองอย่าง:
  - field ที่ไม่มีคอลัมน์ในชีตจะได้ค่าของแถวก่อนหน้า
  - **LocalizedString ของแถวใหม่จะชี้ตาราง localization เดียวกับแถวต้นแบบ** และระบบจะยึดตารางที่ field ชี้อยู่เดิมก่อนเสมอ ค่า `Default Localization Table` ใช้เฉพาะเมื่อ field ยังไม่ชี้ตารางใดเลย ดังนั้น key ที่ใส่ในแท็บต้องอยู่ในตารางที่ entry นั้นผูกอยู่ (RecipeItem → Recipe, MealItem → Meal ฯลฯ) อย่ายืม key ข้ามตาราง
- แท็บลูก (skill) ถูกอ่านตามลิสต์ id ในแถวแม่

### 5.2 Push (asset → ชีต)

- **เขียนทับทั้งแท็บ** จาก asset (clear แล้วเขียนใหม่) แต่คงลำดับแถวเดิมและคอลัมน์ส่วนเกินทางขวา (เช่น Note) ไว้
- สิ่งที่แก้ในชีตแล้วยังไม่ได้ Pull **จะหายทันทีที่ใคร Push แท็บนั้น** กติกาทีม: แก้ที่ชีตแล้ว Pull ก่อนเสมอ ห้าม Push ทับโดยไม่ดู diff
- Push สร้าง/merge แท็บ `_enum` และตั้ง dropdown ให้คอลัมน์ enum ใหม่, สร้าง id ให้ skill ที่ยังไม่มี id, เปิด wrap ให้เซลล์
- ใช้ Push เมื่อ: สร้างแท็บใหม่ครั้งแรก (ให้ header ถูก), เพิ่ม enum ในโค้ดแล้วต้องการ dropdown ใหม่, หรือแก้ข้อมูลใน Inspector แล้วอยากดันขึ้นชีต

### 5.3 ลำดับที่ปลอดภัยเมื่อแก้ข้อมูลที่มี localization

1. เพิ่ม key ในชีต Localize แท็บที่ตรงกับ string table ของ entry นั้น (ดูหัวข้อ 6)
2. ใน Unity: Pull string table นั้นให้ key เข้ามาก่อน (หัวข้อ 6.2)
3. แก้/เพิ่มแถวในชีต GameData
4. Sheet Sync › Pull แท็บที่แก้ ไล่จากแท็บที่ถูกอ้างก่อน (เช่น MealStat, MealRecipe → MealItem → RecipeItem)
5. ตรวจ asset: นับ record, เปิดหน้าจอที่ใช้ข้อมูลนั้นใน Play mode
6. อัปเดตสำเนา xlsx และเอกสาร proposal แล้ว commit asset ที่เปลี่ยน (ไม่ commit `Secrets/`)

---

## 6. ระบบ Localization (คนละระบบกับ Sheet Sync)

### 6.1 โครงชีต Localize

ทุกแท็บมีคอลัมน์ `Key | English (United States)(en-US) | Thai(th)` และ **Key Id เก็บใน note ของเซลล์ Key** (สร้างโดย Unity ตอน Pull ครั้งแรก แถวใหม่เว้น note ว่างไว้ ห้ามพิมพ์เลขเอง)

ตัวอย่างต่อท้ายแถวใหม่ (append ไม่ทับของเดิม):

```python
svc.spreadsheets().values().append(
    spreadsheetId="1y_xoIiqclAEgq96TrAIq2rdf78ucWmR4M2YXziL7BrI",
    range="'Meal'!A1:C", valueInputOption="RAW", insertDataOption="INSERT_ROWS",
    body={"values": [["meal-kimchi-name", "Kimchi", "กิมจิ"],
                     ["meal-kimchi-description", "", ""]]}).execute()
```

ก่อน append ให้อ่านคอลัมน์ A มาเช็คว่า key ยังไม่มี (กัน key ซ้ำซึ่ง Unity จะไฮไลต์เป็นสีแดง)

รูปแบบ key ที่ใช้อยู่: `<ประเภท>-<slug>-name` และ `-description` เช่น `meal-double-meat-burger-name`, `recipe-generic-description`, `material-salt-name`

### 6.2 Pull ใน Unity

เลือก asset String Table Collection เช่น `Assets/Minesweeeper/Localization/Meal.asset` → Inspector → Extensions → Google Sheets Extension → **Pull** (ครั้งแรกอาจเด้ง browser ให้ authorize บัญชี Google ของผู้ใช้ token เก็บที่ `Library/Google/`) ตรวจผลที่ `Meal Shared Data.asset` (จำนวน `m_Key:` ต้องเพิ่ม)

ข้อความ error ของ Sheet Sync ที่ชี้มาที่นี่: `string table 'Meal' has no entry 'xxx'` = key ยังไม่ถูก Pull เข้า Unity หรือใส่ผิดตาราง

---

## 7. Workflow มาตรฐาน

### 7.1 ปรับตัวเลข balance ในแท็บที่มีอยู่

1. อ่านแท็บด้วย `gsheet.py read` หรือจาก xlsx
2. คำนวณ/เสนอค่าใหม่ พร้อมเหตุผลอิงโค้ดจริง (เช่นเช็คว่า stat นั้นถูกใช้อย่างไรใน `PlayerStatController`, `CurseEffectManager`) เขียนเป็น proposal
3. เมื่อผู้ใช้อนุมัติ: เขียนลงชีต → อ่านกลับ → อัปเดต xlsx → บอกผู้ใช้ Pull แท็บไหน

### 7.2 เพิ่ม record ใหม่ (เช่นเมนูอาหารใหม่)

เติมให้ครบทุกแท็บที่อ้างกัน: `MealRecipe` (สูตร) + `MealStat` (ค่า) + `MealItem` (ชื่อ/รูป/ราคา) + `RecipeItem` (id เดียวกับ MealRecipe) + key ในชีต Localize แท็บ Meal และ Recipe + รูปใน MealAtlas (หรือใช้รูปเดิมเป็น placeholder แล้วบันทึกว่าต้องทำอาร์ต)

### 7.3 เพิ่มแท็บ/config ใหม่

ทำในหน้าต่าง Sheet Sync: เพิ่ม entry (Target Asset, Sheet Name, Root Property Path, Layout, Default Localization Table, child table ถ้ามี) แล้ว **Push ครั้งแรก** เพื่อสร้าง header จากนั้นค่อยแก้ในชีตแล้ว Pull

### 7.4 ตรวจว่าชีตกับ Unity ตรงกัน

- นับ record ใน asset: `grep -c "^  - id:" <asset>` เทียบจำนวนแถวในชีต
- diff ชีตกับ xlsx ด้วยสคริปต์ (ตัวอย่างอยู่ในประวัติงาน 2026-09-05: normalize แล้วเทียบทุกเซลล์)
- asset ที่ยังไม่เคย Pull จะมีชุดข้อมูลเก่า (เคยเจอ MealItem มี 5 แถวขณะที่ชีตมี 19)

---

## 8. Troubleshooting

| อาการ | สาเหตุ | แก้ |
| --- | --- | --- |
| HTTP 401 ตอน export/เปิดลิงก์ | ชีต private และไม่ได้ใช้ credential | ใช้ `gsheet.py` กับ service account |
| HTTP 403 `The caller does not have permission` | ชีตนั้นยังไม่ได้แชร์ให้ service account | ขอผู้ใช้ Share เป็น Editor |
| `Service account key file not found` ใน Unity | ไม่มี `Secrets/sumeeper-4ad3bba50861.json` ในโปรเจกต์ (gitignored จึงไม่มากับ git) | copy key ไปวาง |
| `string table 'X' has no entry 'key'` | key ยังไม่ Pull เข้า Unity หรือใส่ key ของตารางอื่น | เพิ่ม key ในแท็บที่ถูกต้อง → Pull string table → Pull GameData ใหม่ |
| Pull ผ่านแต่ค่าไม่เปลี่ยน | header สะกดไม่ตรง field (ถูกข้ามพร้อม warning) | ดู Console หา "unmapped" แก้ header |
| ค่าที่แก้ในชีตหายไป | มีคน Push ทับ | ดูประวัติเวอร์ชันของ Google Sheet กู้คืน แล้วตกลงลำดับ Pull ก่อน Push |
| แถวใหม่ได้ค่าแปลกในคอลัมน์ที่ไม่มีในชีต | copy จากแถวสุดท้าย | เพิ่มคอลัมน์ให้ครบทุก field |
| item ขายราคา 0 | Cost ว่าง | เติม Cost |
| หน้าทำอาหารไม่โชว์สูตรที่ถือ | `RecipeItem.Id` ไม่ตรง `MealRecipe.Id` | แก้ id ให้ตรง |

---

## 9. สิ่งที่ห้ามทำ

- ห้าม commit หรือ print ไฟล์ key ห้ามวาง key ใน `Assets/`
- ห้าม Push จาก Unity ทับแท็บที่มีคนแก้ในชีตโดยยังไม่ Pull
- ห้ามเปลี่ยน id ที่เป็นสัญญา (หัวข้อ 4.2) โดยไม่แก้ทุกที่ที่อ้าง
- ห้ามเขียน balance ลงชีตโดยไม่มีคำสั่งชัดเจนจากผู้ใช้ ทำ proposal แทน
- ห้ามแก้ `_enum` ด้วยมือ และห้ามพิมพ์ Key Id ใน note ของชีต Localize เอง
