# Design Note — Lab 02 BJT DC Bias Web App

## 1. เป้าหมาย

สร้าง Web Application จริงที่รันผ่าน Flask ซึ่งรับค่าอุปกรณ์ของวงจร
BJT Common-Emitter แบบ Voltage-Divider Bias แล้วคำนวณ DC Operating Point
ด้วย Python backend และแสดงผลใน Browser พร้อม validation และ warning
เมื่อแบบจำลอง Forward-Active ใช้ไม่ได้

ขอบเขต Lab 2: DC Bias เท่านั้น ไม่มี AC, transient, Bode plot, SPICE
หรือ Bias Type อื่น

## 2. Data Flow

```
Browser (form POST)
        │  vcc, r1, r2, rc, re, beta, vbe
        ▼
Flask route  POST /calculate          (app.py)
        │  แปลง kΩ → Ω
        ▼
calculate_dc_bias(...)                 (dc_bias.py)
        │  dict: vth, rth, ib, ic, ie, vb, ve, vc, vce, region, warning
        ▼
Jinja template                         (templates/index.html)
        │  HTML + static/style.css
        ▼
Browser แสดงผล DC Bias พร้อมหน่วย
```

เหตุผลที่แยกไฟล์:

- `dc_bias.py` ทดสอบได้โดยไม่ต้องเปิดเว็บ และไม่ผูกกับ framework
- `app.py` ดูแล HTTP/form/หน่วยเท่านั้น
- `templates/` แสดงผล ไม่เก็บสมการ
- `tests/` แยก unit test ของคณิตศาสตร์ออกจาก HTTP test

## 3. สมการ (Forward-Active Approximation)

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

## 4. สมมติฐาน

- ทรานซิสเตอร์อยู่ใน Forward-Active Region
- β คงที่ และ VBE คงที่ (ไม่คิด temperature/early effect)
- ตัวต้านทานเป็นอุดมคติ
- หน่วยอินพุต: VCC/VBE เป็น V, R1/R2/RC/RE เป็น kΩ (แปลงเป็น Ω ก่อนคำนวณ)

## 5. การตรวจสอบและ Warning

| เงื่อนไข | สถานะ | การแสดงผล |
|---|---|---|
| `VTH ≤ VBE` หรือ `IB ≤ 0` | Cutoff | warning ว่าแบบจำลองใช้ไม่ได้ |
| `VCE < 0.2 V` | Saturation | warning ว่าแบบจำลองไม่น่าเชื่อถือ |
| อื่น ๆ | Forward Active | แสดงผลปกติ |

อินพุตที่ผิด (ค่าว่าง, ไม่ใช่ตัวเลข, R ≤ 0, β ≤ 0, VBE < 0) จะถูกปฏิเสธ
ด้วย `ValueError` และแสดงข้อความภาษาไทยในหน้าเดิมโดยไม่ทำให้ server ล้ม
ส่วนหัวข้อ ป้าย และสถานะบนหน้าเว็บเป็นภาษาอังกฤษตาม mockup ของรายวิชา

## 6. เอกสารอ้างอิง

- ทางเลือกและเหตุผลก่อนลงมือ: `lab02/docs/brainstorm.md`
- บันทึก code review และสิ่งที่แก้: `lab02/docs/review.md`
- Design ฉบับเต็มและบันทึกการตัดสินใจ:
  `docs/superpowers/specs/2026-11-10-lab02-bjt-dc-bias-design.md`
- แผนพัฒนา: `docs/superpowers/plans/2026-11-10-lab02-bjt-dc-bias.md`
