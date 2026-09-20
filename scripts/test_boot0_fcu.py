import subprocess
import re
import sys
sys.path.append("Device1/scripts")
from solve_rf_clean import get_base_board

text = get_base_board()

# Add BOOT0 track on F.Cu straight to R1:
# Pin 19: (7.25, 9.5625)
# Route: (7.25, 9.5625) -> (7.25, 7.80) -> (7.39, 7.60) -> (7.39, 4.20)
# And via at (7.25, 4.00) to TP_BOOT0 on B.Cu:
boot0_tracks = """
\t(segment (start 7.25 9.5625) (end 7.25 7.8) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000020"))
\t(segment (start 7.25 7.8) (end 7.39 7.6) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000021"))
\t(segment (start 7.39 7.6) (end 7.39 4.2) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000022"))
\t(segment (start 7.39 4.2) (end 7.25 4.0) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000023"))
\t(via (at 7.25 4.0) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000024"))
"""

zone_idx = text.find('\t(zone\n\t\t(net "/GND")')
text = text[:zone_idx] + boot0_tracks + text[zone_idx:]

with open("Device1/hardware/test_boot0_fcu.kicad_pcb", "w") as f:
    f.write(text)
subprocess.run(["cp", "Device1/hardware/test_direct.kicad_pro", "Device1/hardware/test_boot0_fcu.kicad_pro"])

res = subprocess.run(["kicad-cli", "pcb", "drc", "--refill-zones", "--severity-all", "Device1/hardware/test_boot0_fcu.kicad_pcb"], capture_output=True, text=True)
with open("test_boot0_fcu-drc.rpt") as f:
    rpt = f.read()

vios = re.findall(r"\[([a-z_]+)\]: ([^\n]+)", rpt)
print(f"Total violations with straight F.Cu BOOT0: {len(vios)}")
for v in vios:
    print("  ", v)
