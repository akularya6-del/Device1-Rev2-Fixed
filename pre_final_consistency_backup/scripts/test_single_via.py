import subprocess
import re
import sys
sys.path.append("Device1/scripts")
from solve_rf_clean import get_base_board

def test_boot0_via_only(vx, vy):
    text = get_base_board()

    # Route BOOT0:
    # Pin 19 (7.25, 9.5625) -> via (vx, vy)
    # via (vx, vy) -> (5.6, vy) on B.Cu
    # (5.6, vy) -> (5.6, 4.0) on B.Cu
    # (5.6, 4.0) -> (7.25, 4.0) on B.Cu
    # via (7.25, 4.0) to F.Cu
    # (7.25, 4.0) -> (7.39, 4.2) on F.Cu to R1 Pad 1
    tracks = f"""
\t(segment (start 7.25 9.5625) (end {vx} {vy}) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000020"))
\t(via (at {vx} {vy}) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000021"))
\t(segment (start {vx} {vy}) (end 5.6 {vy}) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000022"))
\t(segment (start 5.6 {vy}) (end 5.6 4.0) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000023"))
\t(segment (start 5.6 4.0) (end 7.25 4.0) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000024"))
\t(via (at 7.25 4.0) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000025"))
\t(segment (start 7.25 4.0) (end 7.39 4.2) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000026"))
"""
    zone_idx = text.find('\t(zone\n\t\t(net "/GND")')
    text = text[:zone_idx] + tracks + text[zone_idx:]

    with open("Device1/hardware/test_via_eval.kicad_pcb", "w") as f:
        f.write(text)
    subprocess.run(["cp", "Device1/hardware/test_direct.kicad_pro", "Device1/hardware/test_via_eval.kicad_pro"])

    res = subprocess.run(["kicad-cli", "pcb", "drc", "--refill-zones", "--severity-all", "Device1/hardware/test_via_eval.kicad_pcb"], capture_output=True, text=True)
    with open("test_via_eval-drc.rpt") as f:
        rpt = f.read()

    vios = re.findall(r"\[([a-z_]+)\]: ([^\n]+)", rpt)
    # Filter out unconnected VR_PA (which is expected because L2 is not yet placed)
    vios = [v for v in vios if not ("unconnected_items" in v[0] and "/VR_PA" in v[1])]
    return len(vios), vios, rpt

# Test (7.25, 8.01)
c, v, r = test_boot0_via_only(7.25, 8.01)
print(f"(7.25, 8.01): {c} violations")
for item in v:
    print("  ", item)
