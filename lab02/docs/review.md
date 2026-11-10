# Code Review Record — Lab 02 BJT DC Bias Web App

บันทึกการ review โค้ดด้วย fresh context (reviewer ที่ไม่ใช่ผู้เขียน)
พร้อม finding และวิธีแก้ที่ตรวจซ้ำแล้วด้วยเทสต์

## 1. ขอบเขตที่ review

| รายการ | ค่า |
|---|---|
| Base commit | `d4505ba` (main ก่อนเริ่ม Lab 02) |
| Head ที่ review | `bf27a74` |
| ขอบเขต | ทุกไฟล์ใน `lab02/` + เอกสาร plan/spec |
| วิธีตรวจ | อ่าน diff ทั้งชุด, รัน unittest, ยิง HTTP ผ่าน Flask test client |

## 2. สรุปผล

| ระดับ | จำนวน | สถานะ |
|---|---|---|
| Critical (ต้องแก้) | 0 | — |
| Important (ควรแก้) | 3 | แก้ครบ |
| Minor (เก็บรายละเอียด) | 3 | แก้ครบ |

## 3. Findings และวิธีแก้

### Important 1 — ข้อความ error ไม่บอกว่า resistor ตัวไหนผิด

- **ปัญหา:** `kohm_to_ohm` ใช้ label คงที่ `"ความต้านทาน"` ทำให้ R1/R2/RC/RE
  แสดงข้อความเหมือนกัน ผู้ใช้ต้องเดาว่าช่องไหนผิด
- **แก้ไข:** เพิ่มพารามิเตอร์ `label` ให้ `kohm_to_ohm(value, label)`
  และให้ `app.py` ส่ง `"R1"`, `"R2"`, `"RC"`, `"RE"` ข้อความจึงเป็น
  `R1 ต้องมากกว่าศูนย์ (kΩ)` เป็นต้น
- **เทสต์:** `test_kohm_to_ohm_names_the_field`,
  `test_post_invalid_shows_error`, `test_post_blank_field_shows_error`,
  `test_post_missing_field_shows_error`
- **Commit:** `1452815`

### Important 2 — Web tests ยังไม่พิสูจน์ warning/blank input จริง

- **ปัญหา:** เดิมทดสอบแค่ว่ามีคำว่า `Cutoff` ซึ่งปรากฏอยู่แล้วในบรรทัดสถานะ
  ถ้าลบกล่อง warning ออก เทสต์ก็ยังผ่าน; ไม่มีเทสต์ค่าว่าง/ฟิลด์หาย/
  Saturation ผ่าน HTTP
- **แก้ไข:** เพิ่มการตรวจ `class="warning"` และข้อความเฉพาะ,
  ทดสอบ `r1=""`, ฟิลด์ `r2` หาย, `re="0.1"` (Saturation),
  ค่าที่กรอกยังอยู่ในฟอร์มหลัง error และกล่อง `Active region approximation OK`
- **เทสต์:** `test_post_cutoff_shows_warning`, `test_post_saturation_shows_warning`,
  `test_post_blank_field_shows_error`, `test_post_missing_field_shows_error`,
  `test_post_keeps_submitted_values`, `test_post_active_shows_ok_status`
- **Commit:** `6423b8e`

### Important 3 — ยังไม่ merge/push เข้า main

- **ปัญหา:** งานอยู่บน branch `lab02-bjt-dc-bias` แต่ `main`/`origin/main`
  ยังไม่มี Lab 02
- **แก้ไข:** merge แบบ `--no-ff` เข้า `main` แล้ว push ขึ้น GitHub
- **ผล:** merge commit `6b29103`, `origin/main` ตรงกับ local

### Minor 1 — เอกสารระบุจำนวนเทสต์เก่า

- **ปัญหา:** `docs/validation.md` เขียน 16 tests แต่ชุดจริงมีมากกว่า
- **แก้ไข:** อัปเดตเป็นจำนวนจริง และ rerun หลังเพิ่มเทสต์ทุกครั้ง
- **สถานะ:** แก้แล้ว (ปัจจุบัน 24 tests)

### Minor 2 — ข้อความ Saturation hardcode `0.2 V`

- **ปัญหา:** logic ใช้ `VCE_SATURATION` แต่ข้อความเขียน `0.2` ตรง ๆ
  ถ้าเปลี่ยนค่าคงที่จะทำให้ข้อความไม่ตรง
- **แก้ไข:** ใช้ f-string interpolate `VCE_SATURATION`
- **สถานะ:** แก้แล้ว

### Minor 3 — ยังไม่กัน `OverflowError` / ค่าอนันต์หลังแปลงหน่วย

- **ปัญหา:** `float(10**400)` ทำให้ `OverflowError` แทน `ValueError`;
  `kohm_to_ohm(1e308)` คูณ 1000 แล้วเป็น `inf`
- **แก้ไข:** `_to_float` catch `OverflowError` และตรวจ `math.isfinite`
  หลังคูณ 1000 อีกครั้ง
- **สถานะ:** แก้แล้ว

## 4. ข้อที่ตัดสินใจไม่แก้ (นอกขอบเขต Lab)

| เรื่อง | เหตุผล |
|---|---|
| CSRF token / authentication / HTTPS | แอปสอนบน localhost ไม่ได้ deploy สาธารณะ |
| JavaScript validation ฝั่ง client | โจทย์กำหนด server-side validation และไม่มี JS framework |
| POST/redirect/GET | หน้าเดียว ไม่ได้ใช้งานระยะยาว |
| แสดง VTH/RTH บนหน้าเว็บ | เกณฑ์กำหนดเฉพาะ VB/VE/VC/VCE/IB/IC/IE; VTH/RTH อยู่ในเอกสาร |
| ตรวจหน่วยอัตโนมัติ (Ω vs kΩ) | heuristic อาจเตือนผิด; ใช้ป้ายหน่วยและ README แทน |
| กราฟ DC Load Line | เกินขอบเขต DC Bias ของ Lab 2 |

## 5. การตรวจซ้ำหลังแก้

```powershell
# จาก root repo
lab02\.venv\Scripts\python.exe -m unittest discover -s lab02/tests -t lab02 -v
```

ผลล่าสุด: **24 tests ผ่านทั้งหมด 0 failures** (ดู `lab02/git-evidence.txt`)

ตรวจเพิ่มเติม:

- Lab 1 เดิมยังผ่าน: `python -m unittest test_electrical.py -v` → 3 tests OK
- HTTP smoke test บนพอร์ต 5001: GET/POST 200, error box, warning box, CSS 200
- ตรวจ screenshot จริงใน Browser: `docs/screenshot.jpg`
