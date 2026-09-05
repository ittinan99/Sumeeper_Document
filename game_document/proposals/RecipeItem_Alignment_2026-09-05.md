# MealRecipe กับ RecipeItem: id ที่ "ชนกัน" คือสัญญาของโค้ด ไม่ใช่บั๊ก

วันที่ 2026-09-05 · สถานะ: **เขียนลง Google Sheet แท็บ RecipeItem แล้ว** (16 แถวตามตารางข้อ 3, ตัดสินใจโดยผู้ออกแบบ: สูตรปลดล็อคด้วยการลองทำ ไอเทมสูตรเป็นเงาของ MealRecipe) · ยังต้อง Pull ใน Unity หลังเพิ่ม key localization

## 1. โค้ดใช้สองแท็บนี้อย่างไร

| แท็บ | ScriptableObject | หน้าที่ในเกม |
| --- | --- | --- |
| `MealRecipe` | `MealRecipeConfig` | ตาราง "วัตถุดิบชุดนี้ → ได้อาหารอะไร" หน้าทำอาหารใช้ตัวนี้แปลงของในหม้อเป็นเมนู และ `CookRecipeMemory` จำ id ของสูตรที่ผู้เล่นเคยทำสำเร็จ |
| `RecipeItem` | `RecipeItemConfig` (InventoryItemConfig ชนิด Recipe) | ไอเทม "สูตรอาหาร" ที่ถือใน recipe inventory การมีไอเทมนี้ = รู้สูตรนั้นตั้งแต่ต้น |

จุดสำคัญอยู่ที่ `UICookPanelPresenter.GetKnownRecipes()` และ `ToUIRecipeNodeModelList()`: รายการสูตรที่หน้าทำอาหารแสดง = ไอเทม RecipeItem ที่ผู้เล่นถือ รวมกับสูตรที่เคยค้นพบ แล้ว**เอา id ของไอเทมนั้นไปค้นใน MealRecipe โดยตรง** (`TryGetMealRecipeDataById(recipeItem.Id)`) ถ้า id ไม่ตรงกัน สูตรนั้นจะไม่ถูกแสดง

ดังนั้น **`RecipeItem.Id` ต้องเท่ากับ `MealRecipe.Id` เสมอ** การใช้ `recipe-01` ทั้งสองแท็บถูกต้องแล้ว ห้ามเปลี่ยน prefix เป็น `recipe-item-01`

## 2. ปัญหาจริงคือเนื้อหาไม่ตรงกัน

RecipeItem 3 แถวที่มีอยู่เป็นของสูตรชุดเก่า (ตอน Unity ยังใช้ recipe-01 ถึง 04 กับ meal-99) ตอนนี้ MealRecipe เปลี่ยนเป็น 16 สูตรแล้ว แต่ RecipeItem ไม่ได้ตามไป

| Id | RecipeItem บอกว่า | MealRecipe บอกว่า | ผลในเกม |
| --- | --- | --- | --- |
| recipe-01 | salad, รูป ingredient-cabbage | เนื้อ+เนื้อ → meal-01 (Double Meat Burger) | ชื่อไอเทมไม่ตรงกับสูตร |
| recipe-02 | meat ball, รูป ingredient-meat 1 | เนื้อ+ผัก → meal-02 (Sandwich) | ชื่อไอเทมไม่ตรงกับสูตร |
| recipe-03 | steak, รูป ingredient-salt | เนื้อ+เกลือ → meal-03 (Dry Meat) | ชื่อไอเทมไม่ตรงกับสูตร |
| recipe-04 ถึง 16 | ไม่มีแถว | มีสูตร | ไม่มีไอเทมสูตรให้ปลดล็อคได้ในอนาคต |

ข้อสังเกตเพิ่มเติม

- `AtlasName` ของ RecipeItem ว่าง แต่ `SpriteName` ชี้ sprite ใน MaterialAtlas รูปจึงน่าจะโหลดไม่ขึ้นถ้าเคยถูกแสดง
- ชื่อและรูปของ RecipeItem **ไม่ถูกใช้ในหน้าทำอาหาร** (หน้านั้นดึงชื่อและรูปจาก MealItem ของเมนูปลายทาง) จะเห็นก็ต่อเมื่อไอเทมสูตรถูกแสดงเป็นไอเทม เช่นใน inventory, hover, ร้านค้า
- **ตอนนี้ไม่มีทางได้ไอเทมสูตรเลย** ไม่มี drop pool, shop pool หรือ item encounter ที่แจกชนิด Recipe และ `RecipeInventoryObject.asset` ว่าง ผู้เล่นรู้สูตรได้ทางเดียวคือลองทำแล้วจำ (`CookRecipeMemory`, รีเซ็ตทุก run ตาม `ResetCookMemoryOnNewRun=TRUE`) RecipeItem จึงเป็นระบบที่เตรียมไว้สำหรับ "ปลดล็อค Recipe ด้วยวัตถุดิบพิเศษ" ตาม GDD ซึ่งยังไม่ได้ทำ

## 3. ข้อเสนอ: ให้ RecipeItem เป็นเงาของ MealRecipe ครบ 16 แถว

หลักการ: 1 สูตรใน MealRecipe = 1 ไอเทมสูตรใน RecipeItem id เดียวกัน ชื่อและรูปยืมจากเมนูปลายทาง เพื่อไม่ต้องเพิ่มคำแปลและอาร์ตอีกชุด

| คอลัมน์ | ค่า | เหตุผล |
| --- | --- | --- |
| `Id` | ตรงกับ MealRecipe (`recipe-01` ถึง `recipe-16`) | สัญญาของโค้ด |
| `Name` | key ชื่อเมนูปลายทาง เช่น `meal-double-meat-burger-name` | ไอเทมสูตรแสดงชื่อเดียวกับเมนู ไม่ต้องเพิ่ม key ใหม่ |
| `Description` | `recipe-generic-description` (key เดียวใช้ร่วมทุกแถว) | เพิ่ม key ใหม่ 1 ตัว: "สูตรอาหาร ใช้ทำได้ที่หน้าทำอาหาร" |
| `Type` | `Recipe` | |
| `Rarity` | `None` | |
| `AtlasName` | `MealAtlas` | แก้จากค่าว่าง |
| `SpriteName` | รูปเดียวกับ MealItem ของเมนูปลายทาง | ยืมอาร์ตชั่วคราวชุดเดียวกัน จนกว่าจะมีรูปม้วนสูตร |
| `Cost` | 100 | ยังไม่มีร้านไหนขาย ใส่กันค่าว่างไว้ก่อน (อาหาร 2 ชิ้นราคา 50) |
| `IsEnemyOnly` / `IsSystemItem` | `FALSE` / `FALSE` | |

ตารางกรอก

| Id | สูตร | Name key | SpriteName (ชั่วคราว) |
| --- | --- | --- | --- |
| recipe-01 | เนื้อ+เนื้อ → meal-01 | `meal-double-meat-burger-name` | `Steak` |
| recipe-02 | เนื้อ+ผัก → meal-02 | `meal-sandwich-name` | `Sukiyaki` |
| recipe-03 | เนื้อ+เกลือ → meal-03 | `meal-dry-meat-name` | `JaowPuu` |
| recipe-04 | ผัก+ผัก → meal-04 | `meal-taco-name` | `Salad` |
| recipe-05 | ผัก+เกลือ → meal-05 | `meal-kimchi-name` | `Salad` |
| recipe-06 | เกลือ+เกลือ → meal-06 | `meal-candy-cane-name` | `JaowPuu` |
| recipe-07 | เนื้อ 3 → meal-07 | `meal-meat-lord-name` | `Steak` |
| recipe-08 | เนื้อ 2 ผัก 1 → meal-08 | `meal-meat-pasta-name` | `Sukiyaki` |
| recipe-09 | เนื้อ 2 เกลือ 1 → meal-09 | `meal-honey-ham-name` | `Steak` |
| recipe-10 | เนื้อ 1 ผัก 2 → meal-10 | `meal-meat-stew-name` | `Sukiyaki` |
| recipe-11 | เนื้อ ผัก เกลือ → meal-11 | `meal-shabu-name` | `Sukiyaki` |
| recipe-12 | เนื้อ 1 เกลือ 2 → meal-12 | `meal-spicy-meat-name` | `JaowPuu` |
| recipe-13 | ผัก 3 → meal-13 | `meal-natures-plate-name` | `Salad` |
| recipe-14 | ผัก 2 เกลือ 1 → meal-14 | `meal-veggie-tempura-name` | `Salad` |
| recipe-15 | ผัก 1 เกลือ 2 → meal-15 | `meal-fruit-cake-name` | `JaowPuu` |
| recipe-16 | เกลือ 3 → meal-16 | `meal-grand-seasoning-name` | `JaowPuu` |

ทุกแถว: Description = `recipe-generic-description`, Type = Recipe, Rarity = None, AtlasName = MealAtlas, Cost = 100, IsEnemyOnly = FALSE, IsSystemItem = FALSE

key ใหม่ในตาราง Recipe (string table "Recipe"): `recipe-generic-description` · en "A recipe. Cook it at the cooking screen." · th "สูตรอาหาร ใช้ทำได้ที่หน้าทำอาหาร" · key เดิม `recipe-salad-*`, `recipe-meat-ball-*`, `recipe-steak-*` ไม่มีใครใช้แล้ว

**แก้ไข 2026-09-05 (หลัง Pull ครั้งแรก error):** การยืม key `meal-*` ใช้ไม่ได้จริง เพราะ RecipeItem resolve key ผ่านตาราง `Recipe` เสมอ (ทั้งจากแถวเดิมใน asset และจากแถวต้นแบบที่ถูก copy ตอนเพิ่มแถว) จึงเปลี่ยนเป็น **key ของตาราง Recipe เอง** คือ `recipe-<slug>-name` (เช่น `recipe-double-meat-burger-name` = "Double Meat Burger Recipe" / "สูตรเบอร์เกอร์เนื้อคู่") เพิ่มลงชีต localization แท็บ Recipe แถว 9 ถึง 24 แล้ว และอัปเดตคอลัมน์ Name ใน GameData RecipeItem แล้ว ไม่ต้องล้าง asset หรือเปลี่ยน default table อีก

## 4. ทางเลือกที่เบากว่า

ถ้ายังไม่ทำระบบปลดล็อคสูตรในเร็วๆ นี้ ลบ 3 แถวเก่าใน RecipeItem ทิ้งให้เหลือแต่ header ก็พอ (Pull แล้ว asset จะว่าง หน้าทำอาหารยังทำงานได้เพราะพึ่ง CookRecipeMemory อย่างเดียว) แล้วค่อยเติม 16 แถวตอนทำระบบจริง ข้อเสียคือชีตจะไม่สะท้อนโครงข้อมูลที่ GDD วางไว้

## 5. สิ่งที่ควรบันทึกไว้กันสับสนซ้ำ

- เพิ่ม Note ในแท็บ RecipeItem แถวบนสุด: "Id ต้องตรงกับ MealRecipe.Id หนึ่งต่อหนึ่ง"
- GDD หัวข้อ Cook ควรระบุสองทางของการรู้สูตร: **ถือไอเทมสูตร** (ถาวร ผ่านการปลดล็อคด้วยวัตถุดิบพิเศษ) และ **ค้นพบด้วยการลองทำ** (จำเฉพาะใน run เพราะ `ResetCookMemoryOnNewRun=TRUE`)
- Pull ลำดับ: string table ก่อน → MealRecipe → MealItem → RecipeItem
