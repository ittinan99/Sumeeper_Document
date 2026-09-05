# ข้อเสนอชื่อและข้อมูล MealItem meal-01 ถึง 16 (Sumeeper_GameData › แท็บ MealItem)

วันที่ 2026-09-05 · สถานะ: **เขียนลง Google Sheet แท็บ MealItem แล้ว** (meal-01 ถึง 16 ตามข้อ 2 และ 3, คง meal-unknown/meal-junk) · ยังต้องเพิ่ม key localization 32 ตัวแล้ว Pull ใน Unity

## 1. ข้อจำกัดจากระบบที่ต้องรู้ก่อนกรอก

- คอลัมน์ `Name` และ `Description` ใน MealItem เป็น **key ของตาราง localization "Meal"** ไม่ใช่ข้อความ ตอน Pull ถ้า key ยังไม่มีในตาราง Unity จะ error ไม่สร้างให้เอง จึงต้องเพิ่ม key ใน string table ก่อน แล้วค่อย Pull MealItem
- `SpriteName` ต้องเป็นชื่อ sprite ที่อยู่ใน MealAtlas ตอนนี้มีแค่ 6 รูป: `Steak`, `Salad`, `JaowPuu`, `Sukiyaki`, `UnknownRecipe`, `latest` (รูปอาหารเสีย) meal-05 ถึง 16 จึงยังไม่มีอาร์ตของตัวเอง
- `Cost` ห้ามเว้นว่าง ร้านค้าและ item drop ดึงอาหารทุกตัวที่ `IsEnemyOnly=FALSE` และ `IsSystemItem=FALSE` เข้าพูล ถ้าว่างจะขายราคา 0
- ตาราง localization Meal ตอนนี้มี 4 ชื่อ (Sukiyaki, Steak, Salad, Jaew Puu) โดย Sukiyaki มีทั้งรูปและคำแปลแต่ยังไม่ถูกใช้

## 2. meal-01 ถึง 04: ใช้ชื่อตามชีตออกแบบ (ตัดสินใจ 2026-09-05)

เปลี่ยนจาก steak / salad / jaowpuu ไปใช้ชื่อในชีตออกแบบทั้ง 4 แถว key เดิม (`meal-steak-*`, `meal-salad-*`, `meal-jaowpuu-*`, `meal-sukiyaki-*`) จะไม่มีใครใช้ ลบออกจากตาราง Meal ได้หรือคงไว้ก็ไม่กระทบ

| Id | สูตร | Name key | Description key | SpriteName (ชั่วคราว) | Cost |
| --- | --- | --- | --- | --- | ---: |
| meal-01 | เนื้อ+เนื้อ | `meal-double-meat-burger-name` | `meal-double-meat-burger-description` | `Steak` | 50 |
| meal-02 | เนื้อ+ผัก | `meal-sandwich-name` | `meal-sandwich-description` | `Sukiyaki` | 50 |
| meal-03 | เนื้อ+เกลือ | `meal-dry-meat-name` | `meal-dry-meat-description` | `JaowPuu` | 50 |
| meal-04 | ผัก+ผัก | `meal-taco-name` | `meal-taco-description` | `Salad` | 50 |

รูปชั่วคราวใช้อาร์ตเดิมที่ใกล้เคียงวัตถุดิบ จนกว่าจะมีรูป `DoubleMeatBurger`, `Sandwich`, `DryMeat`, `Taco`

## 3. meal-05 ถึง 16: ชื่อจากชีตออกแบบ

ชื่ออังกฤษยึดตาม `Sumeeper_Meal_Sheet.xlsx` ปรับตัวสะกดให้เป็นมาตรฐาน (gimchi → Kimchi, passta → Pasta) key ใช้รูปแบบเดิม `meal-<slug>-name` / `meal-<slug>-description`

| Id | สูตร | Name key | Description key | SpriteName (ชั่วคราว) | Cost |
| --- | --- | --- | --- | --- | ---: |
| meal-05 | ผัก+เกลือ | `meal-kimchi-name` | `meal-kimchi-description` | `Salad` | 50 |
| meal-06 | เกลือ+เกลือ | `meal-candy-cane-name` | `meal-candy-cane-description` | `JaowPuu` | 50 |
| meal-07 | เนื้อ 3 | `meal-meat-lord-name` | `meal-meat-lord-description` | `Steak` | 75 |
| meal-08 | เนื้อ 2 ผัก 1 | `meal-meat-pasta-name` | `meal-meat-pasta-description` | `Sukiyaki` | 75 |
| meal-09 | เนื้อ 2 เกลือ 1 | `meal-honey-ham-name` | `meal-honey-ham-description` | `Steak` | 75 |
| meal-10 | เนื้อ 1 ผัก 2 | `meal-meat-stew-name` | `meal-meat-stew-description` | `Sukiyaki` | 75 |
| meal-11 | เนื้อ ผัก เกลือ | `meal-shabu-name` | `meal-shabu-description` | `Sukiyaki` | 75 |
| meal-12 | เนื้อ 1 เกลือ 2 | `meal-spicy-meat-name` | `meal-spicy-meat-description` | `JaowPuu` | 75 |
| meal-13 | ผัก 3 | `meal-natures-plate-name` | `meal-natures-plate-description` | `Salad` | 75 |
| meal-14 | ผัก 2 เกลือ 1 | `meal-veggie-tempura-name` | `meal-veggie-tempura-description` | `Salad` | 75 |
| meal-15 | ผัก 1 เกลือ 2 | `meal-fruit-cake-name` | `meal-fruit-cake-description` | `JaowPuu` | 75 |
| meal-16 | เกลือ 3 | `meal-grand-seasoning-name` | `meal-grand-seasoning-description` | `JaowPuu` | 75 |

คอลัมน์อื่นกรอกเหมือน meal-01: `Type=Meal`, `Rarity=None`, `AtlasName=MealAtlas`, `IsEnemyOnly=FALSE`, `IsSystemItem=FALSE`

**Cost** อาหาร 2 ชิ้นคงราคาเดิม 50 อาหาร 3 ชิ้นเสนอ 75 (1.5 เท่า ตามจำนวนวัตถุดิบ) เป็นค่าตั้งต้นให้จูน

**SpriteName ชั่วคราว** เลือกจากรูปที่มีตามวัตถุดิบเด่นของจาน (เนื้อ → Steak, เนื้อ+ผัก → Sukiyaki, ผัก → Salad, เกลือ → JaowPuu) เพื่อให้เกมแสดงผลได้ทันที ต้องการอาร์ตใหม่รวม 16 รูป (4 รูปของ meal-01 ถึง 04 ในข้อ 2 และ 12 รูปนี้): `Kimchi`, `CandyCane`, `MeatLord`, `MeatPasta`, `HoneyHam`, `MeatStew`, `Shabu`, `SpicyMeat`, `NaturesPlate`, `VeggieTempura`, `FruitCake`, `GrandSeasoning` เมื่อมีรูปแล้วเปลี่ยน SpriteName เป็นชื่อไฟล์และเพิ่มลง MealAtlas

## 4. แถวที่ต้องเพิ่มในตาราง localization "Meal"

Description เว้นว่างได้เหมือน 4 รายการเดิม (ตอนนี้ description ทุกตัวว่าง) แต่ key ต้องมี

| Key | en-US | th |
| --- | --- | --- |
| `meal-double-meat-burger-name` | Double Meat Burger | เบอร์เกอร์เนื้อคู่ |
| `meal-sandwich-name` | Sandwich | แซนด์วิช |
| `meal-dry-meat-name` | Dry Meat | เนื้อแดดเดียว |
| `meal-taco-name` | Taco | ทาโก้ |
| `meal-kimchi-name` | Kimchi | กิมจิ |
| `meal-candy-cane-name` | Candy Cane | ลูกกวาดไม้เท้า |
| `meal-meat-lord-name` | The Meat Lord | เจ้าแห่งเนื้อ |
| `meal-meat-pasta-name` | Meat Pasta | พาสต้าเนื้อ |
| `meal-honey-ham-name` | Honey Ham | แฮมน้ำผึ้ง |
| `meal-meat-stew-name` | Meat Stew | สตูว์เนื้อ |
| `meal-shabu-name` | Shabu | ชาบู |
| `meal-spicy-meat-name` | Spicy Meat | เนื้อรสจัด |
| `meal-natures-plate-name` | Nature's Plate | จานธรรมชาติ |
| `meal-veggie-tempura-name` | Veggie Tempura | เทมปุระผัก |
| `meal-fruit-cake-name` | Fruit Cake | ฟรุตเค้ก |
| `meal-grand-seasoning-name` | Grand Seasoning | สุดยอดเครื่องปรุง |

และ key description อีก 16 ตัวชื่อเดียวกันลงท้าย `-description` ค่าว่าง รวม key ใหม่ 32 ตัว

## 5. ลำดับการทำ

1. เพิ่ม key ทั้ง 32 ตัวในตาราง Meal (ผ่าน Unity Localization Tables หรือชีต localization แล้ว Pull string table)
2. กรอก MealItem ตามข้อ 2 และ 3 ใน Google Sheet
3. Unity: Sheet Sync › Pull ที่ MealItemConfig
4. เปิดหน้า Cook ตรวจว่า 16 เมนูแสดงชื่อและรูปครบ
