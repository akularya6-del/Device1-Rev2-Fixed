import sys
sys.path.append("Device1/scripts")
from solve_rf_drc_final import evaluate

# C23 rotated 90 properly:
# Footprint at (6.30, 7.20, 90)
# Pad 1 is at (6.30, 6.715) -> RFI_N (or GND)
# Pad 2 is at (6.30, 7.685) -> GND (or RFI_N)
# Let's check: Pad 2 at (6.30, 7.685) is closer to L3 Pad 1 (5.515, 8.38), so Pad 2 = /RFI_N!
# Pad 1 at (6.30, 6.715) = /GND!

fps = """
\t(footprint "L_0402_1005Metric"
\t\t(layer "F.Cu")
\t\t(uuid "70010001-0000-4000-8000-000000000002")
\t\t(at 4.1 8.25)
\t\t(descr "Inductor SMD 0402 (1005 Metric)")
\t\t(property "Reference" "L2" (at 0 -1.17 0) (layer "F.SilkS") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(property "Value" "47nH" (at 0 1.17 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(attr smd)
\t\t(fp_rect (start -0.93 -0.47) (end 0.93 0.47) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
\t\t(fp_rect (start -0.5 -0.25) (end 0.5 0.25) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
\t\t(pad "1" smd roundrect (at -0.485 0) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/VR_PA"))
\t\t(pad "2" smd roundrect (at 0.485 0) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RFO_HP"))
\t)
\t(footprint "L_0402_1005Metric"
\t\t(layer "F.Cu")
\t\t(uuid "70010001-0000-4000-8000-000000000003")
\t\t(at 6.0 8.38)
\t\t(descr "Inductor SMD 0402 (1005 Metric)")
\t\t(property "Reference" "L3" (at 0 -1.17 0) (layer "F.SilkS") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(property "Value" "18nH" (at 0 1.17 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(attr smd)
\t\t(fp_rect (start -0.93 -0.47) (end 0.93 0.47) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
\t\t(fp_rect (start -0.5 -0.25) (end 0.5 0.25) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
\t\t(pad "1" smd roundrect (at -0.485 0) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RFI_N"))
\t\t(pad "2" smd roundrect (at 0.485 0) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RFI_P"))
\t)
\t(footprint "C_0402_1005Metric"
\t\t(layer "F.Cu")
\t\t(uuid "70010001-0000-4000-8000-000000000023")
\t\t(at 6.30 7.20 90)
\t\t(descr "Capacitor SMD 0402 (1005 Metric)")
\t\t(property "Reference" "C23" (at 0 -1.17 90) (layer "F.SilkS") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(property "Value" "1.5pF" (at 0 1.17 90) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(attr smd)
\t\t(fp_rect (start -0.93 -0.47) (end 0.93 0.47) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
\t\t(fp_rect (start -0.5 -0.25) (end 0.5 0.25) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
\t\t(pad "1" smd roundrect (at -0.485 0) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/GND"))
\t\t(pad "2" smd roundrect (at 0.485 0) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RFI_N"))
\t)
\t(footprint "C_0402_1005Metric"
\t\t(layer "F.Cu")
\t\t(uuid "70010001-0000-4000-8000-000000000022")
\t\t(at 6.65 6.15)
\t\t(descr "Capacitor SMD 0402 (1005 Metric)")
\t\t(property "Reference" "C22" (at 0 -1.17 0) (layer "F.SilkS") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(property "Value" "1.5pF" (at 0 1.17 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(attr smd)
\t\t(fp_rect (start -0.93 -0.47) (end 0.93 0.47) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
\t\t(fp_rect (start -0.5 -0.25) (end 0.5 0.25) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
\t\t(pad "1" smd roundrect (at -0.485 0) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RF_50OHM"))
\t\t(pad "2" smd roundrect (at 0.485 0) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RFI_P"))
\t)
"""

tracks = """
\t(segment (start 4.75 9.5625) (end 4.75 9.1) (width 0.15) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000001"))
\t(segment (start 4.75 9.1) (end 3.615 9.1) (width 0.15) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000002"))
\t(segment (start 3.615 9.1) (end 3.615 8.25) (width 0.15) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000003"))
\t(segment (start 3.615 8.25) (end 3.615 7.6) (width 0.2) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000004"))

\t(segment (start 5.25 9.5625) (end 5.25 9.2) (width 0.15) (layer "F.Cu") (net "/RFO_HP") (uuid "70020001-0000-4000-8000-000000000005"))
\t(segment (start 5.25 9.2) (end 4.585 8.25) (width 0.15) (layer "F.Cu") (net "/RFO_HP") (uuid "70020001-0000-4000-8000-000000000006"))
\t(segment (start 4.585 8.25) (end 5.25 7.285) (width 0.2) (layer "F.Cu") (net "/RFO_HP") (uuid "70020001-0000-4000-8000-000000000007"))
\t(segment (start 5.25 7.285) (end 4.28 6.80) (width 0.2) (layer "F.Cu") (net "/RFO_HP") (uuid "70020001-0000-4000-8000-000000000008"))

\t(segment (start 6.75 9.5625) (end 6.75 8.9) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000010"))
\t(segment (start 6.75 8.9) (end 6.485 8.38) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000011"))
\t(segment (start 6.485 8.38) (end 7.135 6.15) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000012"))

\t(segment (start 6.25 9.5625) (end 6.25 9.05) (width 0.15) (layer "F.Cu") (net "/RFI_N") (uuid "70020001-0000-4000-8000-000000000014"))
\t(segment (start 6.25 9.05) (end 5.515 8.38) (width 0.15) (layer "F.Cu") (net "/RFI_N") (uuid "70020001-0000-4000-8000-000000000015"))
\t(segment (start 5.515 8.38) (end 6.30 7.685) (width 0.15) (layer "F.Cu") (net "/RFI_N") (uuid "70020001-0000-4000-8000-000000000016"))

\t(segment (start 6.165 6.15) (end 6.29 5.2) (width 0.15) (layer "F.Cu") (net "/RF_50OHM") (uuid "70020001-0000-4000-8000-000000000017"))

\t(segment (start 7.25 9.5625) (end 7.25 8.01) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000020"))
\t(via (at 7.25 8.01) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000021"))
\t(segment (start 7.25 8.01) (end 5.6 8.01) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000022"))
\t(segment (start 5.6 8.01) (end 5.6 4.0) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000023"))
\t(segment (start 5.6 4.0) (end 7.25 4.0) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000024"))
\t(via (at 7.25 4.0) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000025"))
\t(segment (start 7.25 4.0) (end 7.39 4.2) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000026"))
"""

evaluate("c23_rot90_clean", fps, tracks)
