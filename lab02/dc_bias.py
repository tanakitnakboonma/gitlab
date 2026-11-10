VCE_SATURATION = 0.2


def kohm_to_ohm(value_kohm):
    """แปลง kΩ เป็น Ω (รับ str หรือ number)"""
    return float(value_kohm) * 1000


def calculate_dc_bias(vcc, r1, r2, rc, re, beta, vbe):
    """รับค่า SI (V, Ω) คืน dict ผลลัพธ์ DC bias"""
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
