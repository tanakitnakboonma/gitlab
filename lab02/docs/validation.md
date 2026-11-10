# Validation — Lab 02 BJT DC Bias

เอกสารนี้บันทึกการตรวจสอบผลลัพธ์ของเว็บกับ **การคำนวณอิสระ**
ค่าที่แสดงในตารางต้องได้จากการรันโปรแกรมจริงและกรอกค่าด้วยตนเอง
ไม่ใช่การคัดลอกจาก README โดยไม่ตรวจ

## 1. ชุดทดสอบอ้างอิง

VCC = 12 V, R1 = 100 kΩ, R2 = 22 kΩ, RC = 2.2 kΩ, RE = 1 kΩ,
β = 100, VBE = 0.70 V

### Hand calculation

| ขั้น | สมการ | ค่า |
|---|---|---|
| VTH | 12 × 22 / (100 + 22) | 2.1639 V |
| RTH | 100 × 22 / (100 + 22) | 18.0328 kΩ |
| IB | (2.1639 − 0.70) / (18.0328 + 101 × 1) | 12.299 µA |
| IC | 100 × 12.299 µA | 1.2299 mA |
| IE | 101 × 12.299 µA | 1.2422 mA |
| VE | 1.2422 mA × 1 kΩ | 1.2422 V |
| VB | 1.2422 + 0.70 | 1.9422 V |
| VC | 12 − 1.2299 mA × 2.2 kΩ | 9.2943 V |
| VCE | 9.2943 − 1.2422 | 8.0521 V |

### ค่าที่เว็บแสดง (กรอกจากหน้าเว็บ)

| ปริมาณ | ค่าที่แสดง | หน่วย | ตรงกับ hand calculation |
|---|---|---|---|
| VB | 1.942 | V | ใช่ |
| VE | 1.242 | V | ใช่ |
| VC | 9.294 | V | ใช่ |
| VCE | 8.052 | V | ใช่ |
| IC | 1.230 | mA | ใช่ |
| IB | 12.299 | µA | ใช่ |
| IE | 1.242 | mA | ใช่ |
| Region | Forward Active | — | ใช่ |

## 2. กรณี Outside Active Region

| กรณี | ค่าที่ใช้ | ผลที่คาด | ผลจริง |
|---|---|---|---|
| Cutoff | R2 = 1 kΩ (VTH ≈ 0.119 V < VBE) | region = Cutoff + warning | ตรง |
| Saturation | RE = 0.1 kΩ (VCE ≈ 0.026 V < 0.2 V) | region = Saturation + warning | ตรง |

## 3. Input Validation

ทดสอบแล้วว่าอินพุตต่อไปนี้แสดง error และหน้าเว็บไม่ล้ม:

- `VCC = 0`, `R1 = 0`, `R2 = -1`, `RC = 0`, `RE = 0`
- `β = 0`, `β = -5`
- `VBE = -0.1`
- ค่าไม่ใช่ตัวเลข (`abc`), ค่าว่าง, `1,000`
- `NaN`, `Infinity`

## 4. Automated Tests

รันจากในโฟลเดอร์ `lab02/`:

```powershell
python -m unittest discover -s tests -v
```

หรือจาก root repo:

```powershell
python -m unittest discover -s lab02/tests -t lab02 -v
```

ผลที่คาด: 16 tests ผ่านทั้งหมด 0 failures

- `tests/test_dc_bias.py` — ค่าอ้างอิง, validation, cutoff/saturation
- `tests/test_web.py` — GET form, POST ผลลัพธ์, POST error, warning, CSS

## 5. หมายเหตุ

- ผล DC Bias ที่อยู่นอก Forward-Active Region เป็นเพียงค่าจากสมการ
  ไม่ใช่ผลจำลองที่แม่นยำ ต้องอ่าน warning ทุกครั้ง
- ตัวเลขบนหน้าเว็บปัดเศษเพื่อแสดงผล (3 ตำแหน่ง) การตรวจละเอียดใช้ค่า
  จาก unit tests ที่มี tolerance กำหนดไว้
