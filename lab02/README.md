# Lab 02 — BJT DC Bias Web App

Flask Web Application สำหรับคำนวณ **DC Operating Point** ของวงจร BJT
Common-Emitter แบบ **Voltage-Divider Bias** ภายใต้สมมติฐาน Forward-Active
(β และ VBE คงที่)

## โครงสร้างโปรเจกต์

```
lab02/
├── app.py                  # Flask application & HTTP routes
├── dc_bias.py              # independent engineering calculations
├── templates/
│   └── index.html          # input form + DC results (Jinja)
├── static/
│   └── style.css           # responsive layout and presentation
├── tests/
│   ├── __init__.py
│   ├── test_dc_bias.py     # unit tests for engineering logic
│   └── test_web.py         # Flask HTTP route tests
├── requirements.txt        # Flask and necessary dependencies
├── README.md               # install/run instructions
├── AGENTS.md               # AI coding conventions
├── git-evidence.txt        # real unittest / git output
└── docs/
    ├── design-note.md
    ├── validation.md
    └── reflection.md
```

## สิ่งที่ต้องมี

- Python 3.10 ขึ้นไป (ทดสอบด้วย Python 3.12.7)
- Git (ถ้าต้องการ clone repository)

## ติดตั้งและรัน (Windows PowerShell)

```powershell
cd lab02
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m flask --app app run --debug
```

เปิด `http://127.0.0.1:5000/` ใน Browser

## ติดตั้งและรัน (macOS / Linux)

```bash
cd lab02
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m flask --app app run --debug
```

## รัน Automated Tests

จากในโฟลเดอร์ `lab02/`:

```powershell
python -m unittest discover -s tests -v
```

หรือจาก root ของ repository:

```powershell
python -m unittest discover -s lab02/tests -t lab02 -v
```

## อินพุตและผลลัพธ์

| อินพุต | หน่วย | ความหมาย |
|---|---|---|
| VCC | V | แรงดันเลี้ยงวงจร |
| R1 | kΩ | ตัวต้านทาน VCC–Base |
| R2 | kΩ | ตัวต้านทาน Base–Ground |
| RC | kΩ | ตัวต้านทาน VCC–Collector |
| RE | kΩ | ตัวต้านทาน Emitter–Ground |
| β | — | อัตราขยายกระแส (hFE) |
| VBE | V | แรงดัน Base–Emitter |

ผลลัพธ์ที่แสดง: `VB, VE, VC, VCE` (V), `IC, IE` (mA), `IB` (µA)
พร้อมสถานะการทำงาน (`Forward Active`, `Cutoff`, `Saturation`)

## ค่าตัวอย่าง

VCC = 12 V, R1 = 100 kΩ, R2 = 22 kΩ, RC = 2.2 kΩ, RE = 1 kΩ,
β = 100, VBE = 0.70 V

| ปริมาณ | ค่าอ้างอิง |
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

## สมการที่ใช้

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

## ข้อจำกัดของแบบจำลอง

- ใช้ Forward-Active Approximation เท่านั้น (β และ VBE คงที่)
- ไม่คิด Early effect, temperature, AC small-signal หรือ transient
- ถ้า `VTH ≤ VBE` หรือ `IB ≤ 0` → แสดง `Cutoff` และ warning
- ถ้า `VCE < 0.2 V` → แสดง `Saturation` และ warning
- ค่าที่อยู่นอก Active Region ไม่ควรนำไปใช้โดยไม่ตรวจสอบซ้ำ

## หมายเหตุความปลอดภัย

- Flask development server ใช้เฉพาะเครื่องพัฒนา (`127.0.0.1`) ไม่เปิดสู่เครือข่ายสาธารณะ
- ห้าม commit `.venv/`, `.env`, API keys หรือ credentials
- ตรวจ `git status` และ `git diff --staged` ก่อน push ทุกครั้ง

## แก้ปัญหาที่พบบ่อย

| อาการ | วิธีแก้ |
|---|---|
| `Address already in use` | มีโปรแกรมอื่นใช้พอร์ต 5000 อยู่ ใช้ `python -m flask --app app run --debug --port 5001` |
| `flask: command not found` | ยังไม่ activate venv หรือยังไม่ `pip install -r requirements.txt` |
| เปิดไฟล์ `templates/index.html` ตรง ๆ แล้วคำนวณไม่ได้ | ต้องรันผ่าน Flask server เท่านั้น เพราะการคำนวณอยู่ที่ Python backend |
| หน้าเว็บแสดง error ภาษาไทย | เป็นการ validation ตามที่ออกแบบ ให้แก้ค่าอินพุตตามข้อความ |
