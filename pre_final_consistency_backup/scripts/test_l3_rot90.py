import subprocess
import sys
sys.path.append("Device1/scripts")
from solve_rf_clean import get_base_board

text = get_base_board()

# Add L3 at (6.50, 8.00, rot=90)
# Pad 1 is (6.50, 7.515) -> RFI_N
# Pad 2 is (6.50, 8.485) -> RFI_P
l3_fp = """
\t(footprint "L_0402_1005Metric"
\t\t(layer "F.Cu")
\t\t(uuid "70010001-0000-4000-8000-000000000003")
\t\t(at 6.5 8.0 90)
\t\t(descr "Inductor SMD 0402 (1005 Metric)")
\t\t(property "Reference" "L3" (at 0 -1.17 0) (layer "F.SilkS") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(property "Value" "18nH" (at 0 1.17 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(attr smd)
\t\t(fp_rect (start -0.47 -0.93) (end 0.47 0.93) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
\t\t(fp_rect (start -0.25 -0.5) (end 0.25 0.5) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
\t\t(pad "1" smd roundrect (at 0 -0.485 90) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RFI_N"))
\t\t(pad "2" smd roundrect (at 0 0.485 90) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RFI_P"))
\t)
"""

boot0_tracks = """
\t(segment (start 7.25 9.5625) (end 7.25 8.01) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000020"))
\t(via (at 7.25 8.01) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000021"))
\t(segment (start 7.25 8.01) (end 5.6 8.01) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000022"))
\t(segment (start 5.6 8.01) (end 5.6 4.0) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000023"))
\t(segment (start 5.6 4.0) (end 7.25 4.0) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000024"))
\t(via (at 7.25 4.0) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000025"))
\t(segment (start 7.25 4.0) (end 7.415 4.2) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000026"))
"""

idx = text.find("\t(segment")
text = text[:idx] + l3_fp + text[idx:]

zone_idx = text.find('\t(zone\n\t\t(net "/GND")')
text = text[:zone_idx] + boot0_tracks + text[zone_idx:]

out_file = "Device1/hardware/test_solve.kicad_pcb"
with open(out_file, "w") as f:
    f.write(text)

subprocess.run(["cp", "Device1/hardware/test_direct.kicad_pro", "Device1/hardware/test_solve.kicad_pro"])
res = subprocess.run(["kicad-cli", "pcb", "drc", "--refill-zones", "--severity-all", out_file], capture_output=True, text=True)
with open("test_solve-drc.rpt") as f:
    rpt = f.read()

print(rpt)
