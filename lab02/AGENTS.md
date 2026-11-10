# AGENTS.md — Lab 02 conventions

## Stack

- Python 3.12 (ขั้นต่ำ 3.10), Flask 3.1.3
- Test runner: `unittest` จาก standard library เท่านั้น (ห้ามเพิ่ม pytest)

## Commands

```powershell
# จาก lab02/
python -m unittest discover -s tests -v
python -m flask --app app run --debug

# จาก root repo
python -m unittest discover -s lab02/tests -t lab02 -v
```

## Rules

- `dc_bias.py` ต้องเป็น pure engineering logic: ห้าม import Flask หรือรู้จัก HTML/HTTP
- `app.py` รับ HTTP, แปลงหน่วย kΩ → Ω, เรียก `dc_bias.py`, แล้ว render template
- Template ต้องไม่ฝังผลลัพธ์หรือสมการฟิสิกส์เป็นค่าคงที่
- UI ภาษาไทย โดยคงชื่อทางเทคนิคภาษาอังกฤษ; identifier ในโค้ดเป็นภาษาอังกฤษ
- ห้ามแก้ไฟล์ Lab 1 ที่ root (`electrical.py`, `test_electrical.py`, ฯลฯ)
- ห้าม commit `.venv/`, `.env`, `__pycache__/`
- ห้ามอ้างว่า test ผ่านโดยไม่ได้รันจริง
