import re
import subprocess
import sys
sys.path.append("Device1/scripts")
from test_exact_drc import build_board

# Fix test_solve.kicad_pro via diameter rule
with open("Device1/hardware/test_direct.kicad_pro", "r") as f:
    pro_text = f.read()

# Make sure via diameter in netclass Default allows 0.45mm
pro_text = re.sub(r'\"via_dia\":\s*[0-9.]+', '"via_dia": 0.45', pro_text)
pro_text = re.sub(r'\"via_diameter\":\s*[0-9.]+', '"via_diameter": 0.45', pro_text)
with open("Device1/hardware/test_solve.kicad_pro", "w") as f:
    f.write(pro_text)

print("Testing via positions with clean kicad_pro...")

results = []
# We will test:
# L3 at (6.7, 8.3, 0)
# C22 at (6.7, 7.25, 0)
# C23 at (6.7, 6.2, 0)
# R1 at (7.9, 4.2, 0)
# And via at (vx, vy)
for vx in [7.25, 7.30, 7.35, 7.40, 7.45, 7.50]:
    for vy in [7.60, 7.65, 7.70, 7.75, 7.80, 7.85]:
        boot0_path = f"""
\t(segment (start 7.25 9.5625) (end {vx} {vy}) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "80010001-0000-4000-8000-000000000001"))
\t(via (at {vx} {vy}) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/BOOT0") (uuid "80010001-0000-4000-8000-000000000002"))
\t(segment (start {vx} {vy}) (end 5.6 {vy}) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "80010001-0000-4000-8000-000000000003"))
\t(segment (start 5.6 {vy}) (end 5.6 4.0) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "80010001-0000-4000-8000-000000000004"))
\t(segment (start 5.6 4.0) (end 7.25 4.0) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "80010001-0000-4000-8000-000000000005"))
\t(segment (start 7.25 4.0) (end 7.415 4.2) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "80010001-0000-4000-8000-000000000006"))
"""
        # Also need RFI_P connection:
        rfi_p_track = f"""
\t(segment (start 6.75 9.5625) (end 7.185 8.3) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "80020001-0000-4000-8000-000000000001"))
\t(segment (start 7.185 8.3) (end 7.185 7.25) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "80020001-0000-4000-8000-000000000002"))
"""
        v, u, out = build_board((6.7, 8.3, 0), (6.7, 6.2, 0), (6.7, 7.25, 0), (7.9, 4.2, 0), (vx, vy), boot0_path + rfi_p_track)
        results.append((v, u, vx, vy))

results.sort(key=lambda x: (x[0], x[1]))
print("Top 10 via positions:")
for r in results[:10]:
    print(f"  Via at ({r[2]:.2f}, {r[3]:.2f}) -> {r[0]} violations, {r[1]} unconnected")

