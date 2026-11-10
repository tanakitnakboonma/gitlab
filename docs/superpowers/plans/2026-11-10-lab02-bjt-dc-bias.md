# Lab 02 — BJT DC Bias Web App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** สร้าง Flask web app หลายไฟล์ที่รับค่าอุปกรณ์ BJT voltage-divider bias แล้วคำนวณ DC operating point ด้วย Python พร้อม validation, region warning, tests และ README ที่รันตามได้

**Architecture:** Flask route รับฟอร์ม → แปลงหน่วย kΩ→Ω → เรียก `dc_bias.py` ซึ่งเป็น pure function → render ผลด้วย Jinja template หน้าเดียว CSS แยกไฟล์ เทสต์แยกเป็น unit tests ของคณิตศาสตร์และ Flask test client

**Tech Stack:** Python 3.12, Flask 3.1.3, unittest (stdlib), Jinja2, HTML/CSS

**Spec:** `docs/superpowers/specs/2026-11-10-lab02-bjt-dc-bias-design.md`

## Global Constraints

- Python 3.12; Flask `==3.1.3` เท่านั้นใน `lab02/requirements.txt`
- ใช้ `unittest` จาก stdlib; ห้ามเพิ่ม pytest
- UI ภาษาไทย, identifier ในโค้ดภาษาอังกฤษ
- แอปอยู่ใน `lab02/`; ห้ามแก้ไฟล์ Lab 1 ที่ root (`electrical.py`, `test_electrical.py`, `git-evidence.txt`, `github-repo-url.txt`, `reflection.txt`) ยกเว้น root `README.md`
- โมเดล Forward-Active Approximation เท่านั้น; ไม่มี AC/transient/SPICE/bias type อื่น
- ฟอร์มรับความต้านทานเป็น kΩ; ภายในคำนวณด้วย Ω
- เกณฑ์: `VCE_SATURATION = 0.2` V; cutoff เมื่อ `VTH <= VBE` หรือ `IB <= 0`
- แสดงแรงดัน 3 ตำแหน่งทศนิยม; กระแสเป็น mA (IC, IE) และ µA (IB)
- ห้าม commit `.venv/`, `__pycache__/`, `.env`
- คำสั่งเทสต์หลัก (จากใน `lab02/`): `python -m unittest discover -s tests -v`
- คำสั่งเทสต์จาก root: `python -m unittest discover -s lab02/tests -t lab02 -v`

## Review Focus

- ช่อง input ว่างหรือถูกลบ placeholder ออก → ต้องเห็น error ภาษาไทยในหน้าเดิม ไม่ใช่ HTTP 500 (Task 2, Task 4)
- ผู้ใช้กรอกความต้านทานเป็น Ω (เช่น `100000`) ทั้งที่ป้ายเป็น kΩ → ต้องไม่ crash และป้าย/README ต้องระบุหน่วยชัด (Task 5, Task 6)
- ค่าติดลบ/ศูนย์ในช่องใด ๆ → ValueError ที่อ่านรู้เรื่อง ไม่ใช่ ZeroDivisionError (Task 2)
- `VTH <= VBE` (cutoff) → ต้องเห็น warning ไม่ใช่ตัวเลขล้วนที่ดูเหมือนใช้ได้ (Task 3, Task 5)
- `VCE < 0.2 V` (saturation) → ต้องเห็น warning เช่นเดียวกัน (Task 3, Task 5)

---

### Task 1: ติดตั้งสภาพแวดล้อมและ Core Calculation

**Files:**
- Create: `lab02/requirements.txt`
- Create: `lab02/dc_bias.py`
- Test: `lab02/tests/test_dc_bias.py`

**Interfaces:**
- Consumes: ไม่มี
- Produces:
  - `kohm_to_ohm(value_kohm) -> float`
  - `calculate_dc_bias(vcc, r1, r2, rc, re, beta, vbe) -> dict` โดยมี key:
    `vth, rth, ib, ic, ie, vb, ve, vc, vce, region, warning`
  - Task 1 คืน `region="Forward Active"` และ `warning=""` เสมอ (Task 3 จะเปลี่ยน logic)

- [ ] **Step 1: สร้าง venv และติดตั้ง Flask**

Run (จาก root repo):
```powershell
python -m venv lab02/.venv
lab02\.venv\Scripts\python.exe -m pip install "Flask==3.1.3"
```
Expected: ติดตั้งสำเร็จ และ `lab02\.venv\Scripts\python.exe -c "import flask; print(flask.__version__)"` พิมพ์ `3.1.3`

- [ ] **Step 2: สร้าง `lab02/requirements.txt`**

เนื้อหา:
```text
Flask==3.1.3
```

- [ ] **Step 3: เขียน failing test**

สร้าง `lab02/tests/test_dc_bias.py`:
```python
import unittest

from dc_bias import calculate_dc_bias, kohm_to_ohm

VALID = dict(vcc=12, r1=100_000, r2=22_000, rc=2_200, re=1_000, beta=100, vbe=0.70)


def calc(**overrides):
    return calculate_dc_bias(**{**VALID, **overrides})


class TestKohmToOhm(unittest.TestCase):
    def test_converts_kohm_to_ohm(self):
        self.assertAlmostEqual(kohm_to_ohm(100), 100_000.0)
        self.assertAlmostEqual(kohm_to_ohm("2.2"), 2_200.0)


class TestReferenceValues(unittest.TestCase):
    def test_example_circuit(self):
        r = calc()
        self.assertAlmostEqual(r["vth"], 2.1639, delta=1e-3)
        self.assertAlmostEqual(r["rth"], 18_032.79, delta=0.1)
        self.assertAlmostEqual(r["ib"], 12.299e-6, delta=0.01e-6)
        self.assertAlmostEqual(r["ic"], 1.2299e-3, delta=0.01e-3)
        self.assertAlmostEqual(r["ie"], 1.2422e-3, delta=0.01e-3)
        self.assertAlmostEqual(r["ve"], 1.2422, delta=1e-3)
        self.assertAlmostEqual(r["vb"], 1.9422, delta=1e-3)
        self.assertAlmostEqual(r["vc"], 9.2943, delta=1e-3)
        self.assertAlmostEqual(r["vce"], 8.0521, delta=1e-3)
        self.assertEqual(r["region"], "Forward Active")
        self.assertEqual(r["warning"], "")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: รันให้เห็นว่า fail**

Run (จาก `lab02/`): `python -m unittest discover -s tests -v`
Expected: FAIL ด้วย `ModuleNotFoundError: No module named 'dc_bias'`

- [ ] **Step 5: implement `lab02/dc_bias.py`**

Signature และสูตร (ตาม spec §7.4):
```python
VCE_SATURATION = 0.2


def kohm_to_ohm(value_kohm):
    """แปลง kΩ เป็น Ω (รับ str หรือ number)"""
    ...


def calculate_dc_bias(vcc, r1, r2, rc, re, beta, vbe):
    """รับค่า SI (V, Ω) คืน dict ผลลัพธ์ DC bias"""
    ...
```
การคำนวณ:
```python
vth = vcc * r2 / (r1 + r2)
rth = r1 * r2 / (r1 + r2)
ib = (vth - vbe) / (rth + (beta + 1) * re)
ic = beta * ib
ie = (beta + 1) * ib
ve = ie * re
vb = ve + vbe
vc = vcc - ic * rc
vce = vc - ve
```
Task นี้ยังไม่ต้องมี validation (Task 2) และยังไม่ต้องแยก region (Task 3);
คืน `"region": "Forward Active"`, `"warning": ""`

- [ ] **Step 6: รันเทสต์ให้ผ่าน**

Run: `python -m unittest discover -s tests -v`
Expected: 2 tests, OK

- [ ] **Step 7: Commit**

```bash
git add lab02/requirements.txt lab02/dc_bias.py lab02/tests/test_dc_bias.py
git commit -m "feat(lab02): add DC bias core calculation"
```

---

### Task 2: Input Validation

**Files:**
- Modify: `lab02/dc_bias.py`
- Test: `lab02/tests/test_dc_bias.py`

**Interfaces:**
- Consumes: `calculate_dc_bias(...)`, `kohm_to_ohm(...)` จาก Task 1
- Produces: `ValueError` พร้อมข้อความภาษาไทยจากทั้งสองฟังก์ชัน เมื่ออินพุตผิด;
  helper ภายใน `_to_float(label, value) -> float`

- [ ] **Step 1: เพิ่ม failing tests**

ต่อท้าย `lab02/tests/test_dc_bias.py`:
```python
class TestValidation(unittest.TestCase):
    def test_zero_or_negative_components(self):
        for field in ("vcc", "r1", "r2", "rc", "re"):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    calc(**{field: 0})
                with self.assertRaises(ValueError):
                    calc(**{field: -1})

    def test_invalid_beta(self):
        with self.assertRaises(ValueError):
            calc(beta=0)
        with self.assertRaises(ValueError):
            calc(beta=-5)

    def test_negative_vbe(self):
        with self.assertRaises(ValueError):
            calc(vbe=-0.1)

    def test_non_numeric_blank_and_malformed(self):
        for value in ("abc", "", None, "1,000"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    calc(vcc=value)

    def test_non_finite(self):
        for value in (float("nan"), float("inf")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    calc(r1=value)

    def test_kohm_to_ohm_rejects_bad_values(self):
        for value in (0, -1, "abc", ""):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    kohm_to_ohm(value)
```

- [ ] **Step 2: รันให้เห็นว่า fail**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL (validation tests ล้ม เพราะยังไม่มี ValueError)

- [ ] **Step 3: implement validation**

ใน `lab02/dc_bias.py` เพิ่ม `import math` และ:
- `_to_float(label, value)`: `float(value)`; ถ้า TypeError/ValueError → `ValueError(f"{label} ต้องเป็นตัวเลข")`; ถ้าไม่ `math.isfinite` → `ValueError(f"{label} ต้องเป็นจำนวนจำกัด")`
- `calculate_dc_bias` แปลงทุกค่าด้วย `_to_float` โดย label คือ `VCC, R1, R2, RC, RE, β, VBE`
- ตรวจ: `VCC <= 0` → `"VCC ต้องมากกว่าศูนย์"`; `R1/R2/RC/RE <= 0` → `"<ชื่อ> ต้องมากกว่าศูนย์"`; `β <= 0` → `"β ต้องมากกว่าศูนย์"`; `VBE < 0` → `"VBE ต้องไม่ติดลบ"`
- `kohm_to_ohm` ใช้ `_to_float("ความต้านทาน", value_kohm)` และ raise `"ความต้านทานต้องมากกว่าศูนย์"` เมื่อ `<= 0` แล้วคูณ 1000

- [ ] **Step 4: รันเทสต์ให้ผ่าน**

Run: `python -m unittest discover -s tests -v`
Expected: ทุก test ผ่าน

- [ ] **Step 5: Commit**

```bash
git add lab02/dc_bias.py lab02/tests/test_dc_bias.py
git commit -m "feat(lab02): validate DC bias inputs"
```

---

### Task 3: Region Detection และ Warning

**Files:**
- Modify: `lab02/dc_bias.py`
- Test: `lab02/tests/test_dc_bias.py`

**Interfaces:**
- Consumes: `calculate_dc_bias(...)` จาก Task 1–2
- Produces: `region` เป็น `"Forward Active" | "Cutoff" | "Saturation"`;
  `warning` เป็นข้อความไทย หรือ `""`

- [ ] **Step 1: เพิ่ม failing tests**

ต่อท้ายไฟล์ test:
```python
class TestRegion(unittest.TestCase):
    def test_cutoff_when_vth_below_vbe(self):
        r = calc(r2=1_000)
        self.assertEqual(r["region"], "Cutoff")
        self.assertIn("cutoff", r["warning"].lower())

    def test_saturation_when_vce_below_limit(self):
        r = calc(re=100)
        self.assertEqual(r["region"], "Saturation")
        self.assertIn("saturation", r["warning"].lower())

    def test_forward_active_has_no_warning(self):
        r = calc()
        self.assertEqual(r["region"], "Forward Active")
        self.assertEqual(r["warning"], "")
```

- [ ] **Step 2: รันให้เห็นว่า fail**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL — region ยังเป็น `"Forward Active"` เสมอ

- [ ] **Step 3: implement region logic**

หลังคำนวณ `vce`:
```python
if vth <= vbe or ib <= 0:
    region = "Cutoff"
    warning = ("VTH ≤ VBE หรือ IB ≤ 0: อยู่ในโหมด Cutoff "
               "ค่าที่แสดงมาจากสมการ forward-active และไม่ใช่ค่าที่ใช้ได้จริง")
elif vce < VCE_SATURATION:
    region = "Saturation"
    warning = ("VCE < 0.2 V: อยู่ในโหมด Saturation หรือใกล้เคียง "
               "ผลจาก forward-active approximation ไม่น่าเชื่อถือ")
else:
    region = "Forward Active"
    warning = ""
```
ค่าตัวเลขยังคืนตามที่คำนวณได้ (ไม่ clamp) ตาม design §11 ข้อ 3

- [ ] **Step 4: รันเทสต์ให้ผ่าน**

Run: `python -m unittest discover -s tests -v`
Expected: ทุก test ผ่าน

- [ ] **Step 5: Commit**

```bash
git add lab02/dc_bias.py lab02/tests/test_dc_bias.py
git commit -m "feat(lab02): flag cutoff and saturation regions"
```

---

### Task 4: Flask Routes และ Template

**Files:**
- Create: `lab02/app.py`
- Create: `lab02/templates/index.html`
- Test: `lab02/tests/test_web.py`

**Interfaces:**
- Consumes: `calculate_dc_bias`, `kohm_to_ohm` จาก Task 1–3
- Produces:
  - `app` (Flask instance) importable จาก `app.py`
  - `GET /` → 200 ฟอร์ม
  - `POST /calculate` → 200 หน้าเดิม + `result` หรือ `error`
  - template variables: `form` (dict ของ string), `result` (dict หรือ None), `error` (str หรือ None)

- [ ] **Step 1: เขียน failing test**

สร้าง `lab02/tests/test_web.py`:
```python
import unittest

from app import app


class TestWeb(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def post(self, **overrides):
        data = {
            "vcc": "12", "r1": "100", "r2": "22", "rc": "2.2",
            "re": "1", "beta": "100", "vbe": "0.70",
        }
        data.update(overrides)
        return self.client.post("/calculate", data=data)

    def test_get_form(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        for field in ("vcc", "r1", "r2", "rc", "re", "beta", "vbe"):
            self.assertIn(f'name="{field}"', html)

    def test_post_valid_shows_results(self):
        response = self.post()
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("1.942", html)
        self.assertIn("8.052", html)

    def test_post_invalid_shows_error(self):
        response = self.post(r1="0")
        self.assertEqual(response.status_code, 200)
        self.assertIn("มากกว่าศูนย์", response.get_data(as_text=True))

    def test_post_cutoff_shows_warning(self):
        html = self.post(r2="1").get_data(as_text=True)
        self.assertIn("Cutoff", html)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: รันให้เห็นว่า fail**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL ด้วย `ModuleNotFoundError: No module named 'app'`

- [ ] **Step 3: implement `lab02/app.py`**

```python
from flask import Flask, render_template, request

from dc_bias import calculate_dc_bias, kohm_to_ohm

app = Flask(__name__)

DEFAULTS = {
    "vcc": "12", "r1": "100", "r2": "22", "rc": "2.2",
    "re": "1", "beta": "100", "vbe": "0.70",
}
```
- `index()` (GET `/`): `render_template("index.html", form=DEFAULTS, result=None, error=None)`
- `calculate()` (POST `/calculate`): อ่าน `form = {key: request.form.get(key, "") for key in DEFAULTS}`; เรียก
  `calculate_dc_bias(vcc=form["vcc"], r1=kohm_to_ohm(form["r1"]), r2=kohm_to_ohm(form["r2"]), rc=kohm_to_ohm(form["rc"]), re=kohm_to_ohm(form["re"]), beta=form["beta"], vbe=form["vbe"])`
  แล้ว `render_template(... result=result, error=None)`; ถ้า `ValueError` → `render_template(... result=None, error=str(error))` (HTTP 200)

- [ ] **Step 4: สร้าง `lab02/templates/index.html` (โครงขั้นต่ำ)**

ต้องมี:
- `<form action="{{ url_for('calculate') }}" method="post">`
- `<input>` 7 ตัว โดย `name` ตรงกับ `vcc, r1, r2, rc, re, beta, vbe` และ `value="{{ form.<key> }}"`
- ปุ่ม submit ข้อความ `Calculate DC Bias`
- เมื่อ `error` ไม่ว่าง: แสดงในกล่อง class `error` พร้อมข้อความ
- เมื่อ `result` ไม่เป็น None: แสดงตัวเลขด้วย filter มาตรฐาน Jinja:
  `{{ "%.3f"|format(result.vb) }}` สำหรับ VB, VE, VC, VCE;
  `{{ "%.3f"|format(result.ic * 1000) }}` สำหรับ IC (mA);
  `{{ "%.3f"|format(result.ib * 1_000_000) }}` สำหรับ IB (µA);
  `{{ "%.3f"|format(result.ie * 1000) }}` สำหรับ IE (mA)
- แสดง `result.region` และ `result.warning` เมื่อไม่ว่าง

- [ ] **Step 5: รันเทสต์ให้ผ่าน**

Run: `python -m unittest discover -s tests -v`
Expected: 13 tests, OK (หรือมากกว่า)

- [ ] **Step 6: Commit**

```bash
git add lab02/app.py lab02/templates/index.html lab02/tests/test_web.py
git commit -m "feat(lab02): add Flask routes and results page"
```

---

### Task 5: UI, CSS และ Warning/Error Display

**Files:**
- Create: `lab02/static/style.css`
- Modify: `lab02/templates/index.html`
- Test: `lab02/tests/test_web.py`

**Interfaces:**
- Consumes: template variables และ routes จาก Task 4
- Produces: หน้าเว็บ responsive ที่มีป้ายหน่วย, กล่อง `.error` และ `.warning`; `GET /static/style.css` → 200

- [ ] **Step 1: เพิ่ม failing tests**

ต่อท้าย `lab02/tests/test_web.py`:
```python
    def test_units_and_stylesheet_are_linked(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("kΩ", html)
        self.assertIn('rel="stylesheet"', html)
        self.assertEqual(self.client.get("/static/style.css").status_code, 200)
```
(เพิ่มเป็น method ในคลาส `TestWeb` เดิม)

- [ ] **Step 2: รันให้เห็นว่า fail**

Run: `python -m unittest discover -s tests -v`
Expected: FAIL — ยังไม่มี `static/style.css`

- [ ] **Step 3: implement CSS**

`lab02/static/style.css` ใช้ palette จาก handout:
`--navy:#103658; --blue:#1d638b; --teal:#0c8078; --paper:#f5f8fc; --ink:#17344b; --line:#d3e0ec; --orange:#b85c2c`
ต้องมี:
- body พื้น `--paper`, ฟอนต์ Tahoma/Noto Sans Thai
- `.card` พื้นขาว ขอบ `--line` radius 9px padding 24px max-width 1080px
- ฟอร์มเป็น grid 2–3 คอลัมน์; `@media (max-width: 640px)` เหลือ 1 คอลัมน์
- `.error` พื้นแดงอ่อน ขอบซ้ายแดง; `.warning` พื้นส้มอ่อน ขอบซ้าย `--orange`
- `.results` เป็นตาราง/การ์ดอ่านง่าย ตัวเลข `font-variant-numeric: tabular-nums`
- ปุ่ม submit สี `--blue` ตัวอักษรขาว

- [ ] **Step 4: ปรับ `index.html`**

- `<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">`
- หัวเรื่อง `BJT DC Bias Calculator — Voltage Divider Bias`
- ป้าย input: `VCC (V)`, `R1 (kΩ)`, `R2 (kΩ)`, `RC (kΩ)`, `RE (kΩ)`, `β`, `VBE (V)`
- แสดง `error` ใน `<p class="error">` และ `warning` ใน `<p class="warning">`
- แสดง IB/IE ตาม Task 4
- คงค่าที่กรอกไว้หลัง submit

- [ ] **Step 5: รันเทสต์ให้ผ่าน**

Run: `python -m unittest discover -s tests -v`
Expected: ทุก test ผ่าน

- [ ] **Step 6: ตรวจด้วยตา (smoke test)**

Run:
```powershell
python -m flask --app app run --port 5000
```
เปิด `http://127.0.0.1:5000/` ตรวจ: ฟอร์มแสดง, กด Calculate ด้วยค่า 12/100/22/2.2/1/100/0.70 เห็นผล, กรอก r1=0 เห็น error, กรอก r2=1 เห็น warning แล้วหยุด server
Expected: หน้าเว็บใช้งานได้ ไม่มี traceback ใน terminal

- [ ] **Step 7: Commit**

```bash
git add lab02/static/style.css lab02/templates/index.html lab02/tests/test_web.py
git commit -m "feat(lab02): style the DC bias calculator page"
```

---

### Task 6: README, AGENTS.md และเอกสารส่งงาน

**Files:**
- Create: `lab02/README.md`
- Create: `lab02/AGENTS.md`
- Create: `lab02/docs/design-note.md`
- Create: `lab02/docs/validation.md`
- Create: `lab02/docs/reflection.md`
- Modify: `README.md` (root — ลบ conflict marker)

**Interfaces:**
- Consumes: คำสั่งรัน/เทสต์จริงจาก Task 1–5 และค่าอ้างอิงจาก spec §7.4
- Produces: เอกสารที่ทำให้ A7 ผ่าน (clone → install → run → test)

- [ ] **Step 1: เขียน `lab02/README.md`**

ต้องมี:
- โครงสร้างโปรเจกต์ (tree ตาม design §7.1)
- ต้องมี Python 3.10+ (ทดสอบกับ 3.12)
- Windows PowerShell:
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  python -m pip install -r requirements.txt
  python -m flask --app app run --debug
  python -m unittest discover -s tests -v
  ```
- macOS/Linux: `python3 -m venv .venv`, `source .venv/bin/activate`, คำสั่งที่เหลือเหมือนกัน
- ทางเลือกจาก root: `python -m unittest discover -s lab02/tests -t lab02 -v`
- เปิด `http://127.0.0.1:5000/`
- ตารางอินพุต/หน่วย และค่าตัวอย่างพร้อมผลลัพธ์ (ตาม spec §7.4)
- ข้อจำกัด: forward-active, β/VBE คงที่, ไม่มี AC/transient, ผลนอก active region เป็น warning
- หมายเหตุความปลอดภัย: dev server เฉพาะ localhost, ห้าม commit `.venv/`

- [ ] **Step 2: เขียน `lab02/AGENTS.md`**

สั้น ๆ: Python 3.12 + Flask, unittest, รันเทสต์คำสั่งใด, UI ไทย/โค้ดอังกฤษ, `dc_bias.py` ห้าม import Flask, อย่าแก้ Lab 1, ห้าม hardcode ผลลัพธ์ใน template

- [ ] **Step 3: เขียน `lab02/docs/design-note.md`**

สรุป 1–2 หน้า: เป้าหมาย, data flow (Browser → Flask → dc_bias → template), สมการ, สมมติฐาน forward-active, เหตุผลที่แยกไฟล์, link ไป `docs/superpowers/specs/2026-11-10-lab02-bjt-dc-bias-design.md`

- [ ] **Step 4: เขียน `lab02/docs/validation.md`**

- ตาราง hand calculation: VTH, RTH, IB, IC, IE, VE, VB, VC, VCE พร้อมค่าจากสมการ
- ตารางเทียบค่าที่เว็บแสดง (กรอกด้วยตนเอง) กับค่าอ้างอิง
- ผลกรณี cutoff (R2=1 kΩ) และ saturation (RE=0.1 kΩ)
- วิธีรันเทสต์และผลที่คาด (`python -m unittest discover -s tests -v`)
- ระบุว่าค่าตัวเลขต้องได้จากการรันจริง ไม่คัดลอกจาก README

- [ ] **Step 5: เขียน `lab02/docs/reflection.md` (ฉบับร่าง)**

โครง 4 หัวข้อ พร้อมบรรทัด `TODO: เขียนด้วยคำของนักศึกษาเอง`:
1. อะไรที่ AI ช่วยและอะไรที่เราตรวจเอง
2. การแยก Frontend/Backend/Logic มีผลต่อการแก้สมการอย่างไร
3. ข้อจำกัดของ forward-active approximation
4. ถ้ามีเวลาอีก 1 ชั่วโมงจะทำอะไรต่อ

- [ ] **Step 6: เขียน root `README.md` ใหม่**

เนื้อหา:
```markdown
# gitlab
ใช้สำหรับเรียนแลปคอมพิวเตอร์โปรแกรมไฟฟ้า (ENG29 2121)

## Lab 01 — DC Circuit Calculator
- `electrical.py` / `test_electrical.py`
- รัน: `python electrical.py`
- เทสต์: `python -m unittest test_electrical.py -v`

## Lab 02 — BJT DC Bias Web App
- แอป Flask อยู่ใน `lab02/`
- วิธีติดตั้ง/รัน/เทสต์: ดู `lab02/README.md`
```
ห้ามเหลือ `<<<<<<<`, `=======`, `>>>>>>>` ในไฟล์

- [ ] **Step 7: ตรวจเอกสาร**

Run:
```bash
grep -rn "<<<<<<<\|>>>>>>>" README.md lab02/ || echo "no conflict markers"
python -m unittest discover -s lab02/tests -t lab02 -v
```
Expected: `no conflict markers` และเทสต์ผ่านทั้งหมด

- [ ] **Step 8: Commit**

```bash
git add README.md lab02/README.md lab02/AGENTS.md lab02/docs
git commit -m "docs(lab02): add README, validation notes and reflection draft"
```

---

### Task 7: Final Verification, Evidence และ GitHub

**Files:**
- Create: `lab02/git-evidence.txt`
- Modify: ไม่มี

**Interfaces:**
- Consumes: ทุกอย่างจาก Task 1–6
- Produces: หลักฐานรันจริง + commit + push

- [ ] **Step 1: รันเทสต์ทั้งหมดใน venv**

Run (จาก root):
```powershell
lab02\.venv\Scripts\python.exe -m unittest discover -s lab02/tests -t lab02 -v
```
Expected: ทุก test ผ่าน 0 failures

- [ ] **Step 2: smoke test ฝั่ง HTTP**

Run (จาก `lab02/`):
```powershell
lab02\.venv\Scripts\python.exe -m flask --app app run --port 5000
```
อีก terminal:
```powershell
(Invoke-WebRequest http://127.0.0.1:5000/).StatusCode
(Invoke-WebRequest -Method POST http://127.0.0.1:5000/calculate -Body @{vcc=12;r1=100;r2=22;rc=2.2;re=1;beta=100;vbe=0.70}).Content -match "1.942"
```
Expected: `200` และ `True`; แล้วหยุด server

- [ ] **Step 3: สร้าง `lab02/git-evidence.txt` จาก output จริง**

Run:
```powershell
"=== unittest ===" | Out-File -Encoding utf8 lab02/git-evidence.txt
lab02\.venv\Scripts\python.exe -m unittest discover -s lab02/tests -t lab02 -v 2>&1 | Out-File -Append -Encoding utf8 lab02/git-evidence.txt
"=== git log ===" | Out-File -Append -Encoding utf8 lab02/git-evidence.txt
git log --oneline -10 | Out-File -Append -Encoding utf8 lab02/git-evidence.txt
"=== git status ===" | Out-File -Append -Encoding utf8 lab02/git-evidence.txt
git status --short | Out-File -Append -Encoding utf8 lab02/git-evidence.txt
```
Expected: ไฟล์มี output จริงของการรัน (ห้ามพิมพ์ปลอม)

- [ ] **Step 4: ตรวจสถานะก่อน commit**

Run: `git status --short`
Expected: ไม่มี `.venv/`, `__pycache__/`, `.env`; มีเฉพาะไฟล์ที่ตั้งใจ

- [ ] **Step 5: Commit evidence**

```bash
git add lab02/git-evidence.txt
git commit -m "docs(lab02): record verification evidence"
```

- [ ] **Step 6: Merge เข้า main**

```bash
git checkout main
git merge --no-ff lab02-bjt-dc-bias -m "merge: Lab 02 BJT DC bias web app"
```
Expected: merge สำเร็จ ไม่มี conflict

- [ ] **Step 7: Push (ได้รับอนุมัติแล้ว)**

```bash
git push -u origin main
```
Expected: push สำเร็จ; `git log --oneline -1` แสดง commit ล่าสุด

- [ ] **Step 8: รายงานผล**

สรุป: URL repo, commit SHA, คำสั่งรัน, ผลเทสต์, และสิ่งที่นักศึกษาต้องแก้เอง
(`lab02/docs/reflection.md`)

---

## Self-Review

- **Spec coverage:** G1 (Task 4), G2 (Task 4), G3 (Task 1, 4), G4 (Task 2, 4), G5 (Task 3, 5), G6 (Task 1–5), G7 (Task 6) — ครบ; non-goals ไม่ถูก implement
- **Step scan:** ทุก step มีผลตรวจได้; ไม่มี "handle edge cases" ลอย ๆ (validation ระบุเงื่อนไขและข้อความชัด)
- **Type consistency:** `calculate_dc_bias(...) -> dict` key ชุดเดียวกันตลอด; `kohm_to_ohm(value_kohm)` ใช้ชื่อเดียวกันทุก task; template variables `form/result/error` ตรงกัน
- **Review Focus:** ทุกบรรทัดมี test ใน task ที่เป็นเจ้าของ (Task 2, 4, 5)
- **Proportion:** โค้ดในแผนมีเฉพาะ test และ signature/สูตรที่ spec ตรึงไว้ ส่วน body/template/CSS ให้ผู้ลงมือเขียน
