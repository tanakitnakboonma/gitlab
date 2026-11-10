# Brainstorm & Planning — Lab 02 BJT DC Bias Web App

ไฟล์นี้สรุปการระดมความคิดก่อนลงมือ ทางเลือกที่พิจารณา เหตุผลที่เลือก
และความเสี่ยงที่วางแผนรับมือไว้ ใช้คู่กับ
`docs/superpowers/specs/2026-11-10-lab02-bjt-dc-bias-design.md` (spec)
และ `docs/superpowers/plans/2026-11-10-lab02-bjt-dc-bias.md` (แผน 7 tasks)

## 1. โจทย์และข้อจำกัด

- ต้องเป็น Flask Web App จริง เปิดผ่าน Browser แล้วรับค่าและแสดงผลได้
- ต้องเป็น **multi-file** และมี backend คำนวณ ไม่ใช่ JavaScript ล้วน
- เนื้อหาเป็น **DC Bias** ของ BJT Common-Emitter แบบ Voltage-Divider Bias
- ต้องมีหน่วยกำกับ ระบุสมมติฐาน และเตือนเมื่ออยู่นอก Forward-Active
- ต้องมี automated tests, input validation และ warning
- ต้องมี README, Git history และ reflection สำหรับส่งงาน

## 2. ทางเลือกที่พิจารณา

### 2.1 โครงแอป: ไฟล์เดียว หรือแยก frontend/backend/logic

| ทางเลือก | ข้อดี | ข้อเสีย |
|---|---|---|
| `app.py` ไฟล์เดียว | เขียนเร็ว | สมการปนกับ HTTP, เทสต์ยาก, ไม่ตรงเกณฑ์ multi-file |
| แยก `dc_bias.py` + `app.py` + template + static | เทสต์สมการแยกได้, เปลี่ยน UI/สมการอิสระ, ตรงเกณฑ์ | ต้องจัดการ import/โครงไฟล์ |

**สรุป:** ใช้ multi-file ตามข้อกำหนด และแยก `dc_bias.py` ให้ไม่ import Flask

### 2.2 คำนวณฝั่ง client (JavaScript) หรือ server (Python)

| ทางเลือก | ข้อดี | ข้อเสีย |
|---|---|---|
| JavaScript ใน Browser | ตอบสนองทันที ไม่ต้อง POST | ไม่ได้ใช้ backend, เทสต์สมการด้วย Python ยาก |
| Flask + Python | ตรวจสอบด้วย unittest ได้, แสดงแนวคิด backend ชัด | ต้องมี server และ round-trip |

**สรุป:** คำนวณที่ Python backend ทั้งหมด เพื่อให้ตรงโจทย์และทดสอบได้

### 2.3 หน่วยอินพุต: รับเป็น Ω หรือ kΩ

| ทางเลือก | ข้อดี | ข้อเสีย |
|---|---|---|
| รับเป็น Ω | ตรงกับ SI โดยตรง | ตัวเลขใหญ่ (100000) ผู้ใช้กรอกผิดง่าย |
| รับเป็น kΩ | ตรงกับ handout และค่าจริงในวงจร | ต้องแปลงหน่วยก่อนคำนวณ |

**สรุป:** รับเป็น kΩ แสดงป้ายหน่วยคงที่ทุกช่อง และแปลงเป็น Ω
ที่ขอบ `app.py` ก่อนเรียก `dc_bias.py` เพื่อไม่ให้สมการปนเรื่องหน่วย

### 2.4 อินพุตนอก Forward-Active: reject หรือคำนวณแล้วเตือน

| ทางเลือก | ข้อดี | ข้อเสีย |
|---|---|---|
| reject เมื่อ VTH ≤ VBE หรือ VCE ต่ำ | ไม่แสดงค่าที่ไม่มีความหมาย | ผู้ใช้ไม่เห็นว่าวงจรอยู่โหมดใด |
| คำนวณตามสมการแล้วติด warning | เห็นค่าประมาณและเข้าใจข้อจำกัด | ต้องอธิบายให้ชัดว่าค่าไม่น่าเชื่อถือ |

**สรุป:** คำนวณแล้วเตือน พร้อมสถานะ `Cutoff` / `Saturation`
เพราะจุดประสงค์คือให้เห็นว่าสมการ Forward-Active ใช้ไม่ได้เมื่อไร

### 2.5 ภาษา UI: ไทย หรืออังกฤษ

**สรุป:** ใช้อังกฤษตาม mockup ของรายวิชา (`Input Parameters`,
`DC Bias Results`, `Active region approximation OK`) แต่คงข้อความ
error/warning เป็นภาษาไทยเพื่อให้อ่านเข้าใจง่าย

### 2.6 กลยุทธ์ทดสอบ

- เขียน test ก่อน แล้วเฝ้าดู fail (RED) ก่อนเขียนโค้ด (GREEN)
- แยก `tests/test_dc_bias.py` (สมการ/validation) จาก
  `tests/test_web.py` (HTTP/Jinja/CSS)
- ใช้ค่าอ้างอิงจากการคำนวณมือ พร้อม tolerance
- ทดสอบ warning ทั้ง Cutoff และ Saturation ไม่ใช่แค่ข้อความในหน้า
- ทดสอบค่าว่าง/ค่าที่หายไป/ค่าศูนย์/ค่า NaN/Infinity

## 3. แผนงานที่ได้

แบ่งเป็น 7 tasks ที่มีจุดตรวจสอบชัดเจน:

1. venv + core calculation
2. input validation
3. region detection และ warning
4. Flask routes + template
5. UI/CSS + warning/error display
6. README/AGENTS/design/validation/reflection
7. final verification, evidence และ GitHub

แต่ละ task ใช้ TDD: เขียน failing test → รันเห็น fail → เขียนโค้ดน้อยที่สุด
→ รันจนผ่าน → commit

## 4. ความเสี่ยงและการลดความเสี่ยง

| ความเสี่ยง | การลดความเสี่ยง |
|---|---|
| พอร์ต 5000 ถูกโปรแกรมอื่นใช้ | ตรวจก่อนรัน และใช้ 5001 สำหรับ smoke test โดยไม่ฆ่า process เจ้าของพอร์ต |
| กรอกหน่วยผิด (Ω แทน kΩ) | ป้ายหน่วยคงที่ทุกช่อง, README ระบุชัด, แปลงหน่วยที่จุดเดียว |
| ค่าผิดทำให้ ZeroDivisionError | validation ก่อนคำนวณ + tests สำหรับ 0/ค่าลบ/ค่าที่ไม่ใช่ตัวเลข |
| warning ถูกซ่อนโดยไม่รู้ตัว | test ตรวจ `class="warning"` และข้อความเฉพาะของ Cutoff/Saturation |
| UI เพี้ยนบนจอเล็ก | responsive breakpoints + ตรวจ screenshot จริง |
| เอกสารไม่ครบตามเกณฑ์ | checklist ท้าย README ที่โยงเกณฑ์ → ไฟล์หลักฐาน |

## 5. บทสรุป

การตัดสินใจหลักคือ **แยกสมการออกจาก HTTP**, **คำนวณที่ backend**,
**รับหน่วย kΩ แล้วแปลงที่ขอบ**, และ **เตือนแทนการ reject** เมื่ออยู่นอก
Forward-Active ผลลัพธ์คือแอปที่ทดสอบได้ทีละชั้นและอธิบายข้อจำกัดได้ชัดเจน
