import subprocess
import re
import sys
sys.path.append("Device1/scripts")
from solve_rf_clean import get_base_board

text = get_base_board()

# In get_base_board, R1 was set to:
# 7.9 4.2 0
# Let's change R1 to:
# 7.9 4.2 180
text = text.replace('(at 7.9 4.2 0)', '(at 7.9 4.2 180)')

boot0_tracks = """
\t(segment (start 7.25 9.5625) (end 7.25 7.8) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000020"))
\t(segment (start 7.25 7.8) (end 8.0 7.05) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000021"))
\t(segment (start 8.0 7.05) (end 8.0 4.5) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000022"))
\t(segment (start 8.0 4.5) (end 8.385 4.2) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000023"))
\t(segment (start 8.385 4.2) (end 8.415 4.2) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000024"))
\t(segment (start 8.0 4.5) (end 7.25 4.0) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000025"))
\t(via (at 7.25 4.0) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000026"))
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
