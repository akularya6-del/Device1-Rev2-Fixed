import subprocess
import re
import sys
sys.path.append("Device1/scripts")
from solve_rf_clean import get_base_board

base = get_base_board()

# We want to test a single via on net /BOOT0 connected to Pin 19 (7.25, 9.5625)
# Let us test candidate via locations (vx, vy)
def test_via(vx, vy):
    text = base
    # Add track from pin 19 to via, and via
    item = f"""
\t(segment (start 7.25 9.5625) (end {vx} {vy}) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000020"))
\t(via (at {vx} {vy}) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000021"))
"""
    idx = text.find('\t(zone\n\t\t(net "/GND")')
    text = text[:idx] + item + text[idx:]

    with open("Device1/hardware/test_via_pos.kicad_pcb", "w") as f:
        f.write(text)
    subprocess.run(["cp", "Device1/hardware/test_direct.kicad_pro", "Device1/hardware/test_via_pos.kicad_pro"])

    res = subprocess.run(["kicad-cli", "pcb", "drc", "--refill-zones", "--severity-all", "Device1/hardware/test_via_pos.kicad_pcb"], capture_output=True, text=True)
    with open("test_via_pos-drc.rpt") as f:
        rpt = f.read()

    vios = re.findall(r"\[([a-z_]+)\]: ([^\n]+)", rpt)
    # filter out unconnected /VR_PA or /BOOT0 to R1
    critical = [v for v in vios if v[0] not in ("unconnected_items",)]
    return len(critical), critical

print("Testing candidate via positions...")
candidates = []
for vx in [6.8, 6.9, 7.0, 7.1, 7.2, 7.25, 7.3, 7.4, 7.5]:
    for vy in [7.7, 7.8, 7.9, 8.0, 8.1, 8.2, 8.3, 8.4, 8.5]:
        count, crit = test_via(vx, vy)
        if count == 0:
            candidates.append((vx, vy))

print(f"Found {len(candidates)} clean via locations on the base board:")
for c in candidates:
    print("   Clean via at:", c)
