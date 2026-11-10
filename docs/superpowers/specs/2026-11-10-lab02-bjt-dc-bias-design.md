# Lab 02 — BJT DC Bias Web App — Design

วันที่: 2026-11-10
รายวิชา: ENG29 2121 Computer Programming for Electrical Engineers (2/2569)
สถานะ: อนุมัติแนวทางและ design ในบทสนทนาแล้ว

## 1. บริบทและเจตนา

Lab 02 ให้นักศึกษาสร้าง Web Application จริงแบบ multi-file ด้วย Flask เพื่อคำนวณ
DC Operating Point ของวงจร BJT Common-Emitter แบบ Voltage-Divider Bias
จุดประสงค์การเรียนรู้คือให้เห็นว่าแอปเว็บจริงแยก Frontend (Template/CSS),
HTTP Routing (Flask), Engineering Logic (Python) และ Tests ออกจากกัน
ไม่ใช่ HTML ไฟล์เดียวที่ฝังตัวเลขคำนวณไว้

ผลลัพธ์ที่ต้องส่ง: เว็บรันที่ `http://127.0.0.1:5000/` ได้จริง รับค่าอุปกรณ์
คำนวณด้วย Python backend แสดงผลพร้อมหน่วย มี validation/warning
มี automated tests, README และ commit ขึ้น GitHub ภายในคาบ 180 นาที

## 2. เป้าหมาย (Goals)

| # | เป้าหมาย | ตรวจรับด้วย |
|---|---|---|
| G1 | `GET /` แสดงฟอร์มกรอกค่า, HTTP 200 | A1 |
| G2 | `POST /calculate` เรียก Python คำนวณและ render ผล (ไม่ hardcode) | A2 |
| G3 | ค่า VB, VE, VC, VCE, IC ตรงกับการคำนวณอ้างอิงภายใต้แบบจำลองเดียวกัน | A3 |
| G4 | ข้อมูลผิด (R≤0, β≤0, ไม่ใช่ตัวเลข, ขาดค่า) แสดง error ชัดเจนและหน้าไม่ล้ม | A4 |
| G5 | นอก forward-active (cutoff/saturation) แสดง warning ไม่รายงานว่าใช้ได้ | A5 |
| G6 | มี ≥3 unit tests ของ engineering math และ ≥1 Flask test client test | A6 |
| G7 | clone repo → ตาม README → ติดตั้ง/รัน/เทสต์ได้ | A7 |

## 3. สิ่งที่ไม่ทำ (Non-goals)

- AC small-signal, gain, Bode plot, transient, signal generator, overlay animation
- SPICE/ngspice solver หรือ DC load line
- Bias type อื่น (fixed, emitter) — เก็บไว้ Lab 3
- FET, circuit editor, ฐานข้อมูล, login, deploy สาธารณะ
- JavaScript framework หรือ build tool

## 4. Anti-goals (ทำแล้วถือว่าล้มเหลว)

- ฝังผลลัพธ์เป็นตัวเลขคงที่ใน HTML หรือคำนวณฝั่ง client แทน Python
- อ้างว่า test ผ่านโดยไม่ได้รันจริง
- แสดงผลนอก active region เป็นค่าที่เชื่อถือได้โดยไม่มี warning
- ขยาย scope จนไม่จบในคาบ

## 5. ข้อจำกัด (Constraints)

- Python 3.12.7 (มีในเครื่อง), Flask ติดตั้งใน `.venv` ของโปรเจกต์
- ใช้ `unittest` จาก stdlib (ไม่เพิ่ม pytest) ตามคำสั่งรันใน handout
- UI ภาษาอังกฤษตาม mockup (หัวข้อ/ป้าย/สถานะ) โดยมีข้อความ error/warning
  ภาษาไทย; identifier ในโค้ดเป็นภาษาอังกฤษ
- แอปอยู่ในโฟลเดอร์ `lab02/`; ไฟล์ Lab 1 ที่ root ไม่ถูกแก้
- Flask dev server ใช้เฉพาะ localhost; ไม่ commit `.venv/`, `.env`, คีย์
- ต้องไม่พึ่ง service ภายนอกตอนรัน

## 6. แนวทางที่พิจารณา (Approaches)

| แนวทาง | ลักษณะ | ข้อดี | ข้อเสีย | สรุป |
|---|---|---|---|---|
| **A. Server-rendered Flask + Jinja** | ฟอร์ม POST → route → เรียก `dc_bias.py` → render ผลในหน้าเดียว | ตรง acceptance A1–A7, ชิ้นส่วนน้อย, เสี่ยงต่ำสุด, เห็น data flow ชัด | หน้าอัปเดตเต็มหน้า (ไม่ใช่ SPA) | **เลือก** |
| B. Flask JSON API + fetch | frontend JS เรียก API แล้ววาดผล | UX ลื่นกว่า | เพิ่ม JS, API contract, เทสต์อีกชั้น; ไม่ได้คะแนนเพิ่ม | ไม่เลือก |
| C. ไฟล์ HTML เดียวคำนวณใน JS | ไม่มี backend | ง่ายสุด | ผิดโจทย์ multi-file/backend, ไม่ผ่าน A2/A7 | ไม่เลือก |

เหตุผลที่เลือก A: โจทย์กำหนด Flask + multi-file + Python backend ชัดเจน และ A คือ
วิธีที่ตรงข้อกำหนดมากที่สุดโดยใช้เวลาน้อยที่สุด

## 7. การออกแบบ

### 7.1 โครงสร้างไฟล์

```
lab02/
├── app.py                  # Flask routes: GET /, POST /calculate
├── dc_bias.py              # pure engineering logic (ไม่ import Flask/HTML)
├── templates/index.html    # ฟอร์ม + ผลลัพธ์ (Jinja)
├── static/style.css
├── tests/
│   ├── test_dc_bias.py     # unit tests ของคณิตศาสตร์
│   └── test_web.py         # Flask test client
├── requirements.txt        # Flask
├── README.md               # วิธีติดตั้ง/รัน/เทสต์
├── AGENTS.md               # convention สั้น ๆ
└── docs/
    ├── design-note.md
    ├── validation.md
    └── reflection.md
```

ที่ root repo: แก้ `README.md` ที่มี conflict marker ค้างอยู่ให้เป็น README
ของรายวิชา และชี้ไปที่ `lab02/`

### 7.2 HTTP Contract

| Method | Path | อินพุต | ผลลัพธ์ |
|---|---|---|---|
| GET | `/` | — | 200, ฟอร์มว่าง/ค่าเริ่มต้นตัวอย่าง |
| POST | `/calculate` | form: `vcc, r1, r2, rc, re, beta, vbe` | 200, หน้าเดิม + ผลลัพธ์หรือ error |
| GET | `/static/style.css` | — | 200 |

- ค่าที่ผู้ใช้กรอกต้องคงอยู่ในฟอร์มหลัง submit (ทั้งกรณีสำเร็จและ error)
- Error จาก validation: HTTP 200 พร้อมข้อความในหน้า (ไม่ throw 500)
- ไม่มี route อื่นในขอบเขตนี้

### 7.3 โมดูลคำนวณ (`dc_bias.py`)

```python
def calculate_dc_bias(vcc, r1, r2, rc, re, beta, vbe):
    """รับค่าหน่วย SI (V, Ω) คืน dict ผลลัพธ์ + region warning.
    raise ValueError เมื่ออินพุตไม่ถูกต้อง"""

def kohm_to_ohm(value_kohm): ...
```

ผลลัพธ์ที่คืน: `vth, rth, ib, ic, ie, vb, ve, vc, vce, region, warning`
(กระแสหน่วย A, แรงดันหน่วย V; การแปลงหน่วยทำที่ชั้น route/template)

### 7.4 สมการ (Forward-Active Approximation, β และ VBE คงที่)

```
VTH = VCC · R2 / (R1 + R2)
RTH = R1·R2 / (R1 + R2)
IB  = (VTH − VBE) / (RTH + (β+1)·RE)
IC  = β·IB
IE  = (β+1)·IB
VE  = IE·RE
VB  = VE + VBE
VC  = VCC − IC·RC
VCE = VC − VE
```

ค่าอ้างอิงสำหรับ fixture (VCC=12 V, R1=100 kΩ, R2=22 kΩ, RC=2.2 kΩ,
RE=1 kΩ, β=100, VBE=0.70 V):

| ปริมาณ | ค่า |
|---|---|
| VTH | 2.1639 V |
| RTH | 18.0328 kΩ |
| IB | 12.299 µA |
| IC | 1.2299 mA |
| IE | 1.2422 mA |
| VE | 1.2422 V |
| VB | 1.9422 V |
| VC | 9.2943 V |
| VCE | 8.0521 V |
| Region | Forward Active |

### 7.5 Validation

raise `ValueError` พร้อมข้อความภาษาไทย เมื่อ:

- ค่าใดก็ตามแปลงเป็น float ไม่ได้ หรือเป็น NaN/Infinity หรือเว้นว่าง
- `VCC ≤ 0`, `R1 ≤ 0`, `R2 ≤ 0`, `RC ≤ 0`, `RE ≤ 0`
- `β ≤ 0`, `VBE < 0`

ข้อความ error ต้องบอกชื่อพารามิเตอร์และเหตุผล เช่น
"R1 ต้องมากกว่าศูนย์ (Ω)"

### 7.6 การแบ่ง Region และ Warning

| เงื่อนไข | Region | การแสดงผล |
|---|---|---|
| `VTH ≤ VBE` หรือ `IB ≤ 0` | Cutoff | warning ว่าแบบจำลอง forward-active ใช้ไม่ได้ |
| `VCE < 0.2 V` | Saturation (หรือใกล้) | warning เช่นเดียวกัน |
| อื่น ๆ | Forward Active | แสดงผลปกติ |

ห้ามอ้างว่าผลแม่นยำเมื่ออยู่นอก active region — ต้องแสดง warning คู่กับค่าเสมอ
(ค่าที่คำนวณได้ยังแสดงได้ แต่ต้องมีข้อความกำกับ)

### 7.7 หน้าจอ (wireframe ข้อความ)

```
BJT DC Bias Calculator — Voltage Divider
[ VCC (V) ][12]   [ R1 (kΩ) ][100]  [ R2 (kΩ) ][22]
[ RC (kΩ) ][2.2]  [ RE (kΩ) ][1]    [ β ][100]  [ VBE (V) ][0.70]
                 [ Calculate DC Bias ]

ผลลัพธ์
VB 1.942 V | VE 1.242 V | VC 9.294 V
VCE 8.052 V | IC 1.230 mA | IB 12.30 µA | IE 1.242 mA
STATUS: Forward Active
(กล่อง warning สีส้มถ้าอยู่นอก active region / กล่อง error สีแดงเมื่ออินพุตผิด)
```

### 7.8 แผนเทสต์

`tests/test_dc_bias.py`

1. ค่าอ้างอิงตัวอย่าง → ตรวจ VB, VE, VC, VCE, IC ตามตาราง 7.4 (tolerance 1e-3)
2. `VTH ≤ VBE` → region = cutoff + warning ไม่ว่าง
3. `VCE < 0.2 V` (เช่น RE = 0.1 kΩ) → region = saturation + warning
4. อินพุตผิด: R=0, R ติดลบ, β=0, ค่าไม่ใช่ตัวเลข, ค่าขาด → `ValueError`
5. `kohm_to_ohm` แปลงถูก (100 kΩ → 100000 Ω)

`tests/test_web.py`

1. `GET /` → 200 และมีชื่อฟิลด์ `vcc`, `r1`, `beta`
2. `POST /calculate` ด้วยค่าตัวอย่าง → 200 และหน้าแสดง `1.942` / `8.052`
3. `POST /calculate` ด้วย `r1=0` → 200, แสดงข้อความ error, ไม่มี 500

### 7.9 เอกสารส่งงาน

- `lab02/README.md`: venv, install, run, test, ตัวอย่างค่า, ข้อจำกัดแบบจำลอง
- `lab02/docs/design-note.md`: สรุป design, สมการ, สมมติฐาน
- `lab02/docs/validation.md`: ตาราง hand calculation เทียบค่าจากเว็บ + ผลทดสอบ region
- `lab02/docs/reflection.md`: **ฉบับร่าง** ให้เจ้าของงานตรวจและเขียนใหม่ด้วยตัวเอง
- root `README.md`: แก้ conflict marker และชี้ไปที่ `lab02/`

## 8. การตัดสินใจที่ผมเลือกให้ (ตรวจทับได้)

1. ฟอร์มรับความต้านทานเป็น **kΩ** แล้วแปลงเป็น Ω ที่ชั้น route (โจทย์เน้นเรื่องหน่วย)
2. Validation error ตอบ HTTP 200 พร้อมหน้าเดิม (ไม่ใช้ 400) เพื่อให้ฟอร์มยังใช้งานได้
3. เกณฑ์ saturation ใช้ `VCE < 0.2 V`
4. เกณฑ์ cutoff ใช้ `VTH ≤ VBE` หรือ `IB ≤ 0`
5. แสดง IB และ IE เพิ่มจากค่าที่โจทย์บังคับ
6. วางแอปใน `lab02/` ไม่รื้อโครง Lab 1
7. `reflection.md` เป็นฉบับร่าง ต้องให้นักศึกษาแก้เองก่อนส่ง

## 9. สิ่งที่เหลือให้ผู้ลงมือทำ (Builder)

- ลำดับและจำนวน commit ย่อย, ข้อความ commit
- รายละเอียด CSS/การจัดวางหน้าจอ (ใช้ palette น้ำเงิน-เขียวตาม handout)
- ถ้อยคำ warning/error ภาษาไทยให้อ่านง่าย
- จำนวนทศนิยมในการแสดงผล (แนะนำ 3 ตำแหน่ง V, 3 ตำแหน่ง mA)

## 10. แผน Git

1. branch `lab02-bjt-dc-bias` (สร้างแล้ว)
2. commit design doc นี้
3. implement ตามแผน TDD แล้ว commit เป็นชุดงาน
4. merge เข้า `main`
5. push ขึ้น `origin` (ได้รับอนุมัติแล้ว)

## 11. ผล Builder Check และคำตอบ (คำตัดสินของผม)

รีวิวโดย subagent อ่านอย่างเดียว ไม่สามารถถามผู้เขียนได้ พบ 5 คำถาม
ทั้งหมดตัดสินได้โดยไม่เปลี่ยนสิ่งที่ต้องส่ง:

1. **คำสั่งรัน/เทสต์ใน README** — ใช้ `cd lab02` เป็นหลักตาม handout
   (`python -m flask --app app run --debug`,
   `python -m unittest discover -s tests -v`) และเพิ่มคำสั่งทางเลือกจาก root
   `python -m unittest discover -s lab02/tests -t lab02 -v` เพื่อให้ grader
   รันจาก root ได้โดยไม่ต้องมี `__init__.py` พิเศษ
2. **API ของ `calculate_dc_bias`** — รับค่าเป็น string หรือ number ก็ได้
   และแปลง/validate ภายในตัวเอง (เหมือน `analyze_dc` ของ Lab 1) เพื่อให้
   test ครอบคลุม A4 ได้จริง; route เรียก `kohm_to_ohm` ก่อนส่งค่าที่เป็น Ω
   และใช้ helper `_to_float` ร่วมกัน ไม่ให้ validation กระจาย
3. **ค่าในโหมด Cutoff** — คืนค่าที่คำนวณได้จากสมการตรง ๆ (เพื่อ traceability)
   แต่ template ต้องแสดง warning เต็มรูปแบบว่าเป็นค่าที่ไม่สมเหตุสมผลทางกายภาพ
   และห้ามตีความเป็นผลจำลอง; test ตรวจเฉพาะ region + warning ไม่ผูกกับค่าตัวเลข
4. **หลักฐานส่งงาน** — เพิ่ม `lab02/git-evidence.txt` ที่บันทึก output จริงของ
   unittest และ `git log`/`git status` (ตามแบบ Lab 1) โดยไม่ทับไฟล์ Lab 1
5. **root README** — เขียนใหม่ให้เป็น README ของรายวิชา: เก็บส่วน Lab 1
   (DC Circuit Calculator + วิธีรัน/เทสต์) และเพิ่มส่วน Lab 2 ชี้ไปที่
   `lab02/README.md`; ตัดบรรทัด "Temporary note for diff practice" ที่เป็น
   ของแบบฝึกหัด diff ออก

คำตัดสินเพิ่มเติมระหว่างรีวิว: **ต้องมี** `lab02/tests/__init__.py` (ไฟล์ว่าง)
เพื่อให้ `python -m unittest discover -s lab02/tests -t lab02 -v` จาก root ทำงานได้
— ทดลองแล้วว่าไม่มีไฟล์นี้จะได้ `ImportError: Start directory is not importable`;
ไม่ต้องมี `lab02/__init__.py` และโครงไฟล์อื่นคงตาม §7.1
