import re
import subprocess
import sys
sys.path.append("Device1/scripts")
from test_exact_drc import parse_sexpr

def evaluate(l3_x, l3_y, c22_x, c22_y, c23_x, c23_y, boot0_x):
    with open("Device1/hardware/test_direct.kicad_pcb", "r") as f:
        text = f.read()

    # Move R1 to (7.9, 4.2)
    text = re.sub(
        r'(\(footprint [^\n]+\n\t\t\(layer "F\.Cu"\)\n\t\t\(uuid "[^"]+"\)\n\t\t\(at )7\.25 7\.5 90(\).*?\(property "Reference" "R1")',
        r'\g<1>7.9 4.2 0\g<2>',
        text,
        flags=re.DOTALL
    )

    # Update VR_PA via to (3.615 7.6)
    text = text.replace('(at 4.5 8.199999)', '(at 3.615 7.6)')
    text = text.replace('(start 4.5 8.199999)\n\t\t(end 3.5 8.199999)', '(start 3.615 7.6)\n\t\t(end 3.5 7.6)\n\t)\n\t(segment\n\t\t(start 3.5 7.6)\n\t\t(end 3.5 8.199999)')
    text = text.replace('(end 4.5 8.199999)', '(end 3.615 7.6)')

    tokens = parse_sexpr(text)
    removals = []
    for s, e, item in tokens:
        tag = item[1:].split()[0]
        if tag == "segment":
            if "7.25 6.99" in item or "6.5 6.99" in item:
                removals.append((s, e))
            elif '"/VR_PA"' in item and ("4.5 9.75" in item or "4.5 8.199999" in item or "4.75 9.5625" in item):
                removals.append((s, e))
            elif '"/BOOT0"' in item:
                removals.append((s, e))
        elif tag == "via":
            if "6.5 6.99" in item or '"/BOOT0"' in item:
                removals.append((s, e))

    for s, e in sorted(removals, reverse=True):
        text = text[:s] + text[e:]

    rf_fps = f"""
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
\t\t(at {l3_x} {l3_y})
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
\t\t(uuid "70010001-0000-4000-8000-000000000022")
\t\t(at {c22_x} {c22_y})
\t\t(descr "Capacitor SMD 0402 (1005 Metric)")
\t\t(property "Reference" "C22" (at 0 -1.17 0) (layer "F.SilkS") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(property "Value" "1.5pF" (at 0 1.17 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(attr smd)
\t\t(fp_rect (start -0.93 -0.47) (end 0.93 0.47) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
\t\t(fp_rect (start -0.5 -0.25) (end 0.5 0.25) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
\t\t(pad "1" smd roundrect (at -0.485 0) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RF_50OHM"))
\t\t(pad "2" smd roundrect (at 0.485 0) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RFI_P"))
\t)
\t(footprint "C_0402_1005Metric"
\t\t(layer "F.Cu")
\t\t(uuid "70010001-0000-4000-8000-000000000023")
\t\t(at {c23_x} {c23_y})
\t\t(descr "Capacitor SMD 0402 (1005 Metric)")
\t\t(property "Reference" "C23" (at 0 -1.17 0) (layer "F.SilkS") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(property "Value" "1.5pF" (at 0 1.17 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(attr smd)
\t\t(fp_rect (start -0.93 -0.47) (end 0.93 0.47) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
\t\t(fp_rect (start -0.5 -0.25) (end 0.5 0.25) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
\t\t(pad "1" smd roundrect (at -0.485 0) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RFI_N"))
\t\t(pad "2" smd roundrect (at 0.485 0) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/GND"))
\t)
"""
    idx = text.find("\t(segment")
    text = text[:idx] + rf_fps + text[idx:]

    l3_p1 = (l3_x - 0.485, l3_y)
    l3_p2 = (l3_x + 0.485, l3_y)
    c22_p1 = (c22_x - 0.485, c22_y)
    c22_p2 = (c22_x + 0.485, c22_y)
    c23_p1 = (c23_x - 0.485, c23_y)
    c23_p2 = (c23_x + 0.485, c23_y)

    tracks = f"""
\t(segment (start 4.75 9.5625) (end 4.75 8.9) (width 0.2) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000001"))
\t(segment (start 4.75 8.9) (end 3.615 8.9) (width 0.2) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000002"))
\t(segment (start 3.615 8.9) (end 3.615 8.25) (width 0.2) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000003"))
\t(segment (start 3.615 8.25) (end 3.615 7.6) (width 0.2) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000004"))

\t(segment (start 4.585 8.25) (end 5.1 8.25) (width 0.2) (layer "F.Cu") (net "/RFO_HP") (uuid "70020001-0000-4000-8000-000000000005"))
\t(segment (start 5.1 8.25) (end 5.1 7.285) (width 0.2) (layer "F.Cu") (net "/RFO_HP") (uuid "70020001-0000-4000-8000-000000000006"))
\t(segment (start 5.1 7.285) (end 5.25 7.285) (width 0.2) (layer "F.Cu") (net "/RFO_HP") (uuid "70020001-0000-4000-8000-000000000007"))
\t(segment (start 5.1 8.25) (end 5.1 9.4125) (width 0.2) (layer "F.Cu") (net "/RFO_HP") (uuid "70020001-0000-4000-8000-000000000008"))
\t(segment (start 5.1 9.4125) (end 5.25 9.5625) (width 0.2) (layer "F.Cu") (net "/RFO_HP") (uuid "70020001-0000-4000-8000-000000000009"))

\t(segment (start 6.75 9.5625) (end {l3_p2[0]} {l3_p2[1]}) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000010"))
\t(segment (start {l3_p2[0]} {l3_p2[1]}) (end {c22_p2[0]} {c22_p2[1]}) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000011"))

\t(segment (start 6.25 9.5625) (end {l3_p1[0]} {l3_p1[1]}) (width 0.15) (layer "F.Cu") (net "/RFI_N") (uuid "70020001-0000-4000-8000-000000000012"))
\t(segment (start {l3_p1[0]} {l3_p1[1]}) (end {c23_p1[0]} {c23_p1[1]}) (width 0.15) (layer "F.Cu") (net "/RFI_N") (uuid "70020001-0000-4000-8000-000000000013"))

\t(segment (start 5.25 6.315) (end {c22_p1[0]} {c22_p1[1]}) (width 0.2) (layer "F.Cu") (net "/RF_50OHM") (uuid "70020001-0000-4000-8000-000000000014"))
\t(segment (start {c22_p1[0]} {c22_p1[1]}) (end 6.315 5.2) (width 0.2) (layer "F.Cu") (net "/RF_50OHM") (uuid "70020001-0000-4000-8000-000000000015"))

\t(segment (start {c23_p2[0]} {c23_p2[1]}) (end {c23_p2[0]+0.5} {c23_p2[1]}) (width 0.2) (layer "F.Cu") (net "/GND") (uuid "70020001-0000-4000-8000-000000000016"))

\t(segment (start 7.25 9.5625) (end {boot0_x} 9.3) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000017"))
\t(segment (start {boot0_x} 9.3) (end {boot0_x} 4.2) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000018"))
\t(segment (start {boot0_x} 4.2) (end 7.25 4.0) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000019"))
\t(via (at 7.25 4.0) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000020"))
\t(segment (start {boot0_x} 4.2) (end 7.415 4.2) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000021"))
"""
    zone_idx = text.find('\t(zone\n\t\t(net "/GND")')
    text = text[:zone_idx] + tracks + text[zone_idx:]

    out_file = "Device1/hardware/test_solve.kicad_pcb"
    with open(out_file, "w") as f:
        f.write(text)

    subprocess.run(["cp", "Device1/hardware/test_direct.kicad_pro", "Device1/hardware/test_solve.kicad_pro"])

    cmd = ["kicad-cli", "pcb", "drc", "--refill-zones", "--severity-all", out_file]
    res = subprocess.run(cmd, capture_output=True, text=True)
    m_v = re.search(r"Found (\d+) DRC violations", res.stdout)
    m_u = re.search(r"Found (\d+) unconnected items", res.stdout)
    v = int(m_v.group(1)) if m_v else -1
    u = int(m_u.group(1)) if m_u else -1
    return v, u, res.stdout

v, u, out = evaluate(6.35, 8.35, 6.75, 7.25, 6.35, 6.20, 7.35)
print(f"Result: {v} violations, {u} unconnected")
with open("test_solve-drc.rpt", "r") as f:
    print(f.read())
