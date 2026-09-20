import subprocess
import re
import sys
import os
sys.path.append("Device1/scripts")
from solve_rf_clean import get_base_board

base = get_base_board()

def check_one_via(vx, vy):
    text = base
    item = f"""
\t(segment (start 7.25 9.5625) (end {vx} {vy}) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000020"))
\t(via (at {vx} {vy}) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000021"))
\t(segment (start {vx} {vy}) (end 5.6 {vy}) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000022"))
\t(segment (start 5.6 {vy}) (end 5.6 4.0) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000023"))
\t(segment (start 5.6 4.0) (end 7.25 4.0) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000024"))
\t(via (at 7.25 4.0) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000025"))
\t(segment (start 7.25 4.0) (end 7.39 4.2) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000026"))
"""
    idx = text.find('\t(zone\n\t\t(net "/GND")')
    text = text[:idx] + item + text[idx:]

    out_file = f"Device1/hardware/test_via_{str(vy).replace('.', '')}.kicad_pcb"
    with open(out_file, "w") as f:
        f.write(text)
    pro_file = f"Device1/hardware/test_via_{str(vy).replace('.', '')}.kicad_pro"
    subprocess.run(["cp", "Device1/hardware/test_direct.kicad_pro", pro_file])
    rpt_file = f"test_via_{str(vy).replace('.', '')}-drc.rpt"
    subprocess.run(["kicad-cli", "pcb", "drc", "--refill-zones", "--severity-all", "--output", rpt_file, out_file], capture_output=True, text=True)
    with open(rpt_file) as f:
        rpt = f.read()
    vios = re.findall(r"\[([a-z_]+)\]: ([^\n]+)", rpt)
    critical = [v for v in vios if not (v[0] == "unconnected_items" and "VR_PA" in v[1])]
    print(f"Via at ({vx}, {vy}): {len(critical)} critical violations: {critical}")
    return len(critical)

for vy in [8.01, 8.10, 8.15, 8.20, 8.25, 8.30]:
    check_one_via(7.25, vy)
