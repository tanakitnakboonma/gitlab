import math

VCE_SATURATION = 0.2


def _to_float(label, value):
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} ต้องเป็นตัวเลข") from error
    if not math.isfinite(number):
        raise ValueError(f"{label} ต้องเป็นจำนวนจำกัด")
    return number


def kohm_to_ohm(value_kohm):
    """แปลง kΩ เป็น Ω (รับ str หรือ number)"""
    value_ohm = _to_float("ความต้านทาน", value_kohm) * 1000
    if value_ohm <= 0:
        raise ValueError("ความต้านทานต้องมากกว่าศูนย์")
    return value_ohm


def calculate_dc_bias(vcc, r1, r2, rc, re, beta, vbe):
    """รับค่า SI (V, Ω) คืน dict ผลลัพธ์ DC bias"""
    vcc = _to_float("VCC", vcc)
    r1 = _to_float("R1", r1)
    r2 = _to_float("R2", r2)
    rc = _to_float("RC", rc)
    re = _to_float("RE", re)
    beta = _to_float("β", beta)
    vbe = _to_float("VBE", vbe)

    if vcc <= 0:
        raise ValueError("VCC ต้องมากกว่าศูนย์")
    if r1 <= 0:
        raise ValueError("R1 ต้องมากกว่าศูนย์")
    if r2 <= 0:
        raise ValueError("R2 ต้องมากกว่าศูนย์")
    if rc <= 0:
        raise ValueError("RC ต้องมากกว่าศูนย์")
    if re <= 0:
        raise ValueError("RE ต้องมากกว่าศูนย์")
    if beta <= 0:
        raise ValueError("β ต้องมากกว่าศูนย์")
    if vbe < 0:
        raise ValueError("VBE ต้องไม่ติดลบ")

    vth = vcc * r2 / (r1 + r2)
    rth = r1 * r2 / (r1 + r2)
    ib = (vth - vbe) / (rth + (beta + 1) * re)
    ic = beta * ib
    ie = (beta + 1) * ib
    ve = ie * re
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve

    return {
        "vth": vth,
        "rth": rth,
        "ib": ib,
        "ic": ic,
        "ie": ie,
        "vb": vb,
        "ve": ve,
        "vc": vc,
        "vce": vce,
        "region": "Forward Active",
        "warning": "",
    }
