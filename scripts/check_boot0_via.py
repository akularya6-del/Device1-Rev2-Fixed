import sys
sys.path.append("Device1/scripts")
from solve_rf_clean import get_base_board
from test_exact_drc import parse_sexpr
import subprocess
import re

base = get_base_board()

# Let's test a via at (vx, vy)
def check_via(vx, vy):
    text = base
    # add track from pin 19 (7.25, 9.5625) to (vx, vy) and via
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

    out_file = "Device1/hardware/test_via_single.kicad_pcb"
    with open(out_file, "w") as f:
        f.write(text)
    subprocess.run(["cp", "Device1/hardware/test_direct.kicad_pro", "Device1/hardware/test_via_single.kicad_pro"])
    subprocess.run(["kicad-cli", "pcb", "drc", "--refill-zones", "--severity-all", out_file], capture_output=True, text=True)
    with open("test_via_single-drc.rpt") as f:
        rpt = f.read()
    vios = re.findall(r"\[([a-z_]+)\]: ([^\n]+)", rpt)
    # filter out unconnected /VR_PA
    critical = [v for v in vios if not (v[0] == "unconnected_items" and "VR_PA" in v[1])]
    return len(critical), critical

print("Testing (7.35, 8.65):", check_via(7.35, 8.65))
print("Testing (7.40, 8.65):", check_via(7.40, 8.65))
