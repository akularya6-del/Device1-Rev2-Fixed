import re
import subprocess

def parse_sexpr(text):
    tokens = []
    stack = 0
    in_string = False
    escape = False
    start = None
    for i, c in enumerate(text):
        if escape:
            escape = False
            continue
        if c == "\\":
            escape = True
            continue
        if c == "\"":
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == "(":
            if stack == 1:
                start = i
            stack += 1
        elif c == ")":
            stack -= 1
            if stack == 1 and start is not None:
                tokens.append((start, i + 1, text[start:i+1]))
                start = None
    return tokens

def build_board(l3_pos, c23_pos, c22_pos, r1_pos, via_pos, boot0_path):
    with open("Device1/hardware/test_direct.kicad_pcb", "r") as f:
        text = f.read()

    tokens = parse_sexpr(text)
    to_remove = []
    r1_token = None

    for s, e, item in tokens:
        tag = item[1:].split()[0]
        if tag == "footprint" and '(property "Reference" "R1"' in item:
            r1_token = (s, e, item)
        elif tag == "segment":
            # Check segments to remove:
            # old R1 track at (7.25 6.99)
            if "7.25 6.99" in item or "6.5 6.99" in item:
                to_remove.append((s, e))
            # old VR_PA segments around U1
            elif '"/VR_PA"' in item and ("4.5 9.75" in item or "4.5 8.199999" in item or "4.75 9.5625" in item):
                to_remove.append((s, e))
            # old BOOT0 segments
            elif '"/BOOT0"' in item:
                to_remove.append((s, e))
        elif tag == "via":
            # old R1 via at (6.5 6.99)
            if "6.5 6.99" in item:
                to_remove.append((s, e))
            # old BOOT0 via
            elif '"/BOOT0"' in item:
                to_remove.append((s, e))
            # old VR_PA via at (4.5 8.2)
            elif "4.5 8.199999" in item and '"/VR_PA"' in item:
                # We will update it
                pass

    # Sort removals backwards
    new_text = text
    # Update VR_PA via to (3.615 7.6)
    new_text = new_text.replace('(at 4.5 8.199999)', '(at 3.615 7.6)')
    new_text = new_text.replace('(start 4.5 8.199999)\n\t\t(end 3.5 8.199999)', '(start 3.615 7.6)\n\t\t(end 3.5 7.6)\n\t)\n\t(segment\n\t\t(start 3.5 7.6)\n\t\t(end 3.5 8.199999)')
    new_text = new_text.replace('(end 4.5 8.199999)', '(end 3.615 7.6)')

    # Move R1
    new_text = re.sub(
        r'(\(footprint [^\n]+\n\t\t\(layer "F\.Cu"\)\n\t\t\(uuid "[^"]+"\)\n\t\t\(at )7\.25 7\.5 90(\).*?\(property "Reference" "R1")',
        rf'\g<1>{r1_pos[0]} {r1_pos[1]} {r1_pos[2]}\g<2>',
        new_text,
        flags=re.DOTALL
    )

    # Re-parse tokens for exact deletion
    tokens2 = parse_sexpr(new_text)
    removals = []
    for s, e, item in tokens2:
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
        new_text = new_text[:s] + new_text[e:]

    # Add RF footprints
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
\t\t(at {l3_pos[0]} {l3_pos[1]} {l3_pos[2]})
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
\t\t(at {c23_pos[0]} {c23_pos[1]} {c23_pos[2]})
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
\t\t(at {c22_pos[0]} {c22_pos[1]} {c22_pos[2]})
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
    idx = new_text.find("\t(segment")
    new_text = new_text[:idx] + rf_fps + new_text[idx:]

    # Base RF tracks
    rf_tracks = f"""
\t(segment (start 4.75 9.5625) (end 4.75 8.9) (width 0.2) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000001"))
\t(segment (start 4.75 8.9) (end 3.615 8.9) (width 0.2) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000002"))
\t(segment (start 3.615 8.9) (end 3.615 8.25) (width 0.2) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000003"))
\t(segment (start 3.615 8.25) (end 3.615 7.6) (width 0.2) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000004"))
\t(segment (start 4.585 8.25) (end 5.25 8.25) (width 0.2) (layer "F.Cu") (net "/RFO_HP") (uuid "70020001-0000-4000-8000-000000000005"))

\t(segment (start 6.25 9.5625) (end {l3_pos[0]-0.485} 9.5625) (width 0.15) (layer "F.Cu") (net "/RFI_N") (uuid "70020001-0000-4000-8000-000000000006"))
\t(segment (start {l3_pos[0]-0.485} 9.5625) (end {l3_pos[0]-0.485} {l3_pos[1]}) (width 0.15) (layer "F.Cu") (net "/RFI_N") (uuid "70020001-0000-4000-8000-000000000007"))
\t(segment (start {l3_pos[0]-0.485} {l3_pos[1]}) (end {c23_pos[0]-0.485} {c23_pos[1]}) (width 0.15) (layer "F.Cu") (net "/RFI_N") (uuid "70020001-0000-4000-8000-000000000008"))

\t(segment (start 6.75 9.5625) (end {l3_pos[0]+0.485} {l3_pos[1]}) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000009"))

\t(segment (start 5.25 6.315) (end 5.25 6.2) (width 0.2) (layer "F.Cu") (net "/RF_50OHM") (uuid "70020001-0000-4000-8000-000000000014"))
\t(segment (start 5.25 6.2) (end {c22_pos[0]-0.485} {c22_pos[1]}) (width 0.2) (layer "F.Cu") (net "/RF_50OHM") (uuid "70020001-0000-4000-8000-000000000015"))
\t(segment (start {c22_pos[0]-0.485} {c22_pos[1]}) (end 6.29 5.8) (width 0.2) (layer "F.Cu") (net "/RF_50OHM") (uuid "70020001-0000-4000-8000-000000000016"))
\t(segment (start 6.29 5.8) (end 6.29 5.2) (width 0.2) (layer "F.Cu") (net "/RF_50OHM") (uuid "70020001-0000-4000-8000-000000000017"))

\t(segment (start {c23_pos[0]+0.485} {c23_pos[1]}) (end {c23_pos[0]+0.8} {c23_pos[1]}) (width 0.2) (layer "F.Cu") (net "/GND") (uuid "70020001-0000-4000-8000-000000000030"))
"""
    rf_tracks += boot0_path

    zone_idx = new_text.find('\t(zone\n\t\t(net "/GND")')
    new_text = new_text[:zone_idx] + rf_tracks + new_text[zone_idx:]

    out_file = "Device1/hardware/test_solve.kicad_pcb"
    with open(out_file, "w") as f:
        f.write(new_text)

    cmd = ["kicad-cli", "pcb", "drc", "--refill-zones", "--severity-all", out_file]
    res = subprocess.run(cmd, capture_output=True, text=True)
    m_v = re.search(r"Found (\d+) DRC violations", res.stdout)
    m_u = re.search(r"Found (\d+) unconnected items", res.stdout)
    v = int(m_v.group(1)) if m_v else -1
    u = int(m_u.group(1)) if m_u else -1
    return v, u, res.stdout

print("Engine ready.")
