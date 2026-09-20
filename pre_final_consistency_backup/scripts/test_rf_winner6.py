import re

def apply_winner6():
    with open("Device1/hardware/test_direct.kicad_pcb", "r") as f:
        text = f.read()

    # 1. Update R1 position from (7.25, 7.5, 90) to (7.90, 4.20, 0)
    text = re.sub(
        r'(\(footprint [^\n]+\n\t\t\(layer "F\.Cu"\)\n\t\t\(uuid "[^"]+"\)\n\t\t\(at )7\.25 7\.5 90(\).*?\(property "Reference" "R1")',
        r'\g<1>7.9 4.2 0\g<2>',
        text,
        flags=re.DOTALL
    )

    # 2. Remove old R1 tracks and via at (6.5 6.99)
    text = re.sub(r'\t\(segment\s+\(start 7\.25 6\.99\)\s+\(end 6\.5 6\.99\).*?\n\t\)', '', text, flags=re.DOTALL)
    text = re.sub(r'\t\(segment\s+\(start 6\.5 6\.99\)\s+\(end 7\.25 6\.99\).*?\n\t\)', '', text, flags=re.DOTALL)
    text = re.sub(r'\t\(via\s+\(at 6\.5 6\.99\).*?\n\t\)', '', text, flags=re.DOTALL)

    # 3. Update VR_PA via from (4.5 8.2) to (3.615 7.6)
    text = text.replace('(at 4.5 8.199999)', '(at 3.615 7.6)')
    text = text.replace('(start 4.5 8.199999)\n\t\t(end 3.5 8.199999)', '(start 3.615 7.6)\n\t\t(end 3.5 7.6)\n\t)\n\t(segment\n\t\t(start 3.5 7.6)\n\t\t(end 3.5 8.199999)')
    text = text.replace('(end 4.5 8.199999)', '(end 3.615 7.6)')

    # Remove ALL old VR_PA F.Cu segments
    text = re.sub(r'\t\(segment\s+\(start 4\.5 9\.75\)\s+\(end 4\.5 8\.199999\).*?\n\t\)', '', text, flags=re.DOTALL)
    text = re.sub(r'\t\(segment\s+\(start 4\.75 9\.5625\)\s+\(end 4\.5 9\.75\).*?\n\t\)', '', text, flags=re.DOTALL)

    # Remove all old BOOT0 segments and old via at (7.25 8.01)
    text = re.sub(r'\t\(segment\s+\(start 7\.25 9\.56\)\s+\(end 7\.25 8\.01\).*?\n\t\)', '', text, flags=re.DOTALL)
    text = re.sub(r'\t\(via\s+\(at 7\.25 8\.01\).*?\n\t\)', '', text, flags=re.DOTALL)
    text = re.sub(r'\t\(segment\s+\(start 7\.25 8\.01\)\s+\(end 5\.6 8\.01\).*?\n\t\)', '', text, flags=re.DOTALL)
    text = re.sub(r'\t\(segment\s+\(start 5\.6 8\.01\)\s+\(end 5\.6 4\).*?\n\t\)', '', text, flags=re.DOTALL)
    text = re.sub(r'\t\(segment\s+\(start 5\.6 4\)\s+\(end 7\.25 4\).*?\n\t\)', '', text, flags=re.DOTALL)

    # Add 4 RF footprints
    rf_footprints = """
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
\t\t(at 6.7 8.3)
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
\t\t(at 6.7 7.25)
\t\t(descr "Capacitor SMD 0402 (1005 Metric)")
\t\t(property "Reference" "C23" (at 0 -1.17 0) (layer "F.SilkS") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(property "Value" "1.5pF" (at 0 1.17 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(attr smd)
\t\t(fp_rect (start -0.93 -0.47) (end 0.93 0.47) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
\t\t(fp_rect (start -0.5 -0.25) (end 0.5 0.25) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
\t\t(pad "1" smd roundrect (at -0.485 0) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RFI_N"))
\t\t(pad "2" smd roundrect (at 0.485 0) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/GND"))
\t)
\t(footprint "C_0402_1005Metric"
\t\t(layer "F.Cu")
\t\t(uuid "70010001-0000-4000-8000-000000000022")
\t\t(at 6.7 6.2)
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

    idx = text.find("\t(segment")
    text = text[:idx] + rf_footprints + text[idx:]

    rf_tracks = """
\t(segment (start 4.75 9.5625) (end 4.75 8.9) (width 0.2) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000001"))
\t(segment (start 4.75 8.9) (end 3.615 8.9) (width 0.2) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000002"))
\t(segment (start 3.615 8.9) (end 3.615 8.25) (width 0.2) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000003"))
\t(segment (start 3.615 8.25) (end 3.615 7.6) (width 0.2) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000004"))

\t(segment (start 4.585 8.25) (end 5.25 8.25) (width 0.2) (layer "F.Cu") (net "/RFO_HP") (uuid "70020001-0000-4000-8000-000000000005"))

\t(segment (start 6.25 9.5625) (end 6.215 9.5275) (width 0.15) (layer "F.Cu") (net "/RFI_N") (uuid "70020001-0000-4000-8000-000000000006"))
\t(segment (start 6.215 9.5275) (end 6.215 8.3) (width 0.15) (layer "F.Cu") (net "/RFI_N") (uuid "70020001-0000-4000-8000-000000000007"))
\t(segment (start 6.215 8.3) (end 6.215 7.25) (width 0.15) (layer "F.Cu") (net "/RFI_N") (uuid "70020001-0000-4000-8000-000000000008"))

\t(segment (start 6.75 9.5625) (end 7.185 9.1275) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000009"))
\t(segment (start 7.185 9.1275) (end 7.185 8.3) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000010"))
\t(segment (start 7.185 8.3) (end 7.7 7.785) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000011"))
\t(segment (start 7.7 7.785) (end 7.7 6.715) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000012"))
\t(segment (start 7.7 6.715) (end 7.185 6.2) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000013"))

\t(segment (start 5.25 6.2) (end 6.215 6.2) (width 0.2) (layer "F.Cu") (net "/RF_50OHM") (uuid "70020001-0000-4000-8000-000000000014"))
\t(segment (start 5.25 6.315) (end 5.25 6.2) (width 0.2) (layer "F.Cu") (net "/RF_50OHM") (uuid "70020001-0000-4000-8000-000000000015"))
\t(segment (start 6.215 6.2) (end 6.29 5.8) (width 0.2) (layer "F.Cu") (net "/RF_50OHM") (uuid "70020001-0000-4000-8000-000000000016"))
\t(segment (start 6.29 5.8) (end 6.29 5.2) (width 0.2) (layer "F.Cu") (net "/RF_50OHM") (uuid "70020001-0000-4000-8000-000000000017"))

\t(segment (start 7.25 9.5625) (end 7.25 9.15) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000018"))
\t(via (at 7.25 9.15) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000019"))
\t(segment (start 7.25 9.15) (end 8.8 9.15) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000020"))
\t(segment (start 8.8 9.15) (end 8.8 4.0) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000021"))
\t(segment (start 8.8 4.0) (end 7.25 4.0) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000022"))
\t(via (at 7.25 4.0) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000023"))
\t(segment (start 7.415 4.2) (end 7.25 4.2) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000024"))
\t(segment (start 7.25 4.2) (end 7.25 4.0) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000025"))
"""

    zone_idx = text.find('\t(zone\n\t\t(net "/GND")')
    if zone_idx != -1:
        text = text[:zone_idx] + rf_tracks + text[zone_idx:]
    else:
        text = text.replace('\t(zone', rf_tracks + '\t(zone', 1)

    out_file = "Device1/hardware/test_solve.kicad_pcb"
    with open(out_file, "w") as f:
        f.write(text)
    print("Wrote", out_file)

if __name__ == "__main__":
    apply_winner6()
