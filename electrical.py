import math


def analyze_dc(voltage_v, resistance_ohm):
    try:
        voltage_v = float(voltage_v)
        resistance_ohm = float(resistance_ohm)
    except (TypeError, ValueError) as error:
        raise ValueError("แรงดันและความต้านทานต้องเป็นตัวเลข") from error

    if not math.isfinite(voltage_v) or not math.isfinite(resistance_ohm):
        raise ValueError("กรุณาระบุค่าตัวเลขที่ไม่ใช่อนันต์")
    if resistance_ohm <= 0:
        raise ValueError("ความต้านทานต้องมากกว่าศูนย์")

    current_a = voltage_v / resistance_ohm
    power_w = voltage_v * current_a
    return {"current_a": current_a, "power_w": power_w}


def main():
    try:
        voltage_v = input("แรงดันไฟฟ้า (โวลต์): ")
        resistance_ohm = input("ความต้านทาน (โอห์ม): ")
        result = analyze_dc(voltage_v, resistance_ohm)
    except ValueError as error:
        print(f"ข้อมูลไม่ถูกต้อง: {error}")
        return

    print(f"กระแสไฟฟ้า: {result['current_a']:.3f} A")
    print(f"กำลังไฟฟ้า: {result['power_w']:.3f} W")


if __name__ == "__main__":
    main()