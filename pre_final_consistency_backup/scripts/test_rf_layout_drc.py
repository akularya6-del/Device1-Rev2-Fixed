import sys
import pcbnew
import re

def run_test():
    with open("Device1/hardware/test_direct.kicad_pcb", "r") as f:
        text = f.read()

    # Define the 4 new RF components:
    # L2: 47nH choke between VR_PA and RFO_HP
    # L3: 18nH balun between RFI_N and RFI_P
    # C23: 1.5pF balance between RFI_N and GND
    # C22: 1.5pF coupling between RF_50OHM and RFI_P

    rf_footprints = """
\t(footprint "Inductor_SMD:L_0402_1005Metric"
\t\t(layer "F.Cu")
\t\t(uuid "70010001-0000-4000-8000-000000000002")
\t\t(at 4.5 8.3)
\t\t(descr "Inductor SMD 0402 (1005 Metric)")
\t\t(property "Reference" "L2" (at 0 -1.17 0) (layer "F.SilkS") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(property "Value" "47nH" (at 0 1.17 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(attr smd)
\t\t(fp_rect (start -0.93 -0.47) (end 0.93 0.47) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
\t\t(fp_rect (start -0.5 -0.25) (end 0.5 0.25) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
\t\t(pad "1" smd roundrect (at -0.485 0) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/VR_PA"))
\t\t(pad "2" smd roundrect (at 0.485 0) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RFO_HP"))
\t)
\t(footprint "Inductor_SMD:L_0402_1005Metric"
\t\t(layer "F.Cu")
\t\t(uuid "70010001-0000-4000-8000-000000000003")
\t\t(at 6.5 8.3)
\t\t(descr "Inductor SMD 0402 (1005 Metric)")
\t\t(property "Reference" "L3" (at 0 -1.17 0) (layer "F.SilkS") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(property "Value" "18nH" (at 0 1.17 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(attr smd)
\t\t(fp_rect (start -0.93 -0.47) (end 0.93 0.47) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
\t\t(fp_rect (start -0.5 -0.25) (end 0.5 0.25) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
\t\t(pad "1" smd roundrect (at -0.485 0) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RFI_N"))
\t\t(pad "2" smd roundrect (at 0.485 0) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RFI_P"))
\t)
\t(footprint "Capacitor_SMD:C_0402_1005Metric"
\t\t(layer "F.Cu")
\t\t(uuid "70010001-0000-4000-8000-000000000023")
\t\t(at 6.25 6.8 90)
\t\t(descr "Capacitor SMD 0402 (1005 Metric)")
\t\t(property "Reference" "C23" (at 0 -1.17 90) (layer "F.SilkS") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(property "Value" "1.5pF" (at 0 1.17 90) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(attr smd)
\t\t(fp_rect (start -0.47 -0.93) (end 0.47 0.93) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
\t\t(fp_rect (start -0.25 -0.5) (end 0.25 0.5) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
\t\t(pad "1" smd roundrect (at 0 0.485 90) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RFI_N"))
\t\t(pad "2" smd roundrect (at 0 -0.485 90) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/GND"))
\t)
\t(footprint "Capacitor_SMD:C_0402_1005Metric"
\t\t(layer "F.Cu")
\t\t(uuid "70010001-0000-4000-8000-000000000022")
\t\t(at 6.8 5.2)
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

    # Shift R_TEST to (8.80, 5.20)
    # Find R_TEST footprint and update its (at ...)
    r_test_pat = r'(\t\(footprint "R_0402_1005Metric"[^\n]*\n\t\t\(layer "F\.Cu"\)[^\n]*\n\t\t\(uuid "[^"]*"\)\n\t\t\(at )6\.8 5\.2'
    text = re.sub(r_test_pat, r'\g<1>8.8 5.2', text, count=1)

    # Shift R1 to (8.00, 7.50)
    r1_pat = r'(\t\(footprint "R_0402_1005Metric"[^\n]*\n\t\t\(layer "F\.Cu"\)[^\n]*\n\t\t\(uuid "[^"]*"\)\n\t\t\(at )7\.25 7\.5'
    text = re.sub(r1_pat, r'\g<1>8.0 7.5', text, count=1)

    # Shift C11 to (9.50, 7.50)
    c11_pat = r'(\t\(footprint "C_0402_1005Metric"[^\n]*\n\t\t\(layer "F\.Cu"\)[^\n]*\n\t\t\(uuid "[^"]*"\)\n\t\t\(at )8\.5 7\.5'
    text = re.sub(c11_pat, r'\g<1>9.5 7.5', text, count=1)

    # Insert new footprints before the closing paren of kicad_pcb
    # Find last footprint or insert before the first segment
    idx = text.find("\t(segment")
    if idx != -1:
        text = text[:idx] + rf_footprints + text[idx:]
    else:
        text = text[:-2] + rf_footprints + "\n)\n"

    # Add tracks for new RF components:
    rf_tracks = """
\t(segment (start 4.5 8.3) (end 5.25 8.3) (width 0.2) (layer "F.Cu") (net "/RFO_HP") (uuid "70020001-0000-4000-8000-000000000001"))
\t(segment (start 6.015 8.3) (end 6.25 8.535) (width 0.15) (layer "F.Cu") (net "/RFI_N") (uuid "70020001-0000-4000-8000-000000000002"))
\t(segment (start 6.25 8.535) (end 6.25 9.5625) (width 0.15) (layer "F.Cu") (net "/RFI_N") (uuid "70020001-0000-4000-8000-000000000003"))
\t(segment (start 6.985 8.3) (end 6.75 8.535) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000004"))
\t(segment (start 6.75 8.535) (end 6.75 9.5625) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000005"))
\t(segment (start 6.015 8.3) (end 6.25 8.065) (width 0.15) (layer "F.Cu") (net "/RFI_N") (uuid "70020001-0000-4000-8000-000000000006"))
\t(segment (start 6.25 8.065) (end 6.25 7.285) (width 0.15) (layer "F.Cu") (net "/RFI_N") (uuid "70020001-0000-4000-8000-000000000007"))
\t(segment (start 6.315 5.2) (end 5.25 5.2) (width 0.2) (layer "F.Cu") (net "/RF_50OHM") (uuid "70020001-0000-4000-8000-000000000008"))
\t(segment (start 7.285 5.2) (end 7.285 8.0) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000009"))
\t(segment (start 7.285 8.0) (end 6.985 8.3) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000010"))
"""
    # Insert new tracks before the closing paren
    text = text.rstrip()
    if text.endswith(")"):
        text = text[:-1] + rf_tracks + "\n)\n"

    with open("Device1/hardware/test_rf_layout.kicad_pcb", "w") as f:
        f.write(text)

    print("Saved test_rf_layout.kicad_pcb")

if __name__ == "__main__":
    run_test()
