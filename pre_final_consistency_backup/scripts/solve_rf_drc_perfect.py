import re
import subprocess

def test_variant(name, l3_pos, c23_pos, c22_pos, r1_pos, tracks_func):
    with open("Device1/hardware/test_direct.kicad_pcb", "r") as f:
        text = f.read()

    # Move R1
    text = re.sub(
        r'(\(footprint [^\n]+\n\t\t\(layer "F\.Cu"\)\n\t\t\(uuid "[^"]+"\)\n\t\t\(at )7\.25 7\.5 90(\).*?\(property "Reference" "R1")',
        rf'\g<1>{r1_pos[0]} {r1_pos[1]} {r1_pos[2]}\g<2>',
        text,
        flags=re.DOTALL
    )

    # Remove old R1 tracks and via at (6.5 6.99)
    text = text.replace('3959da48-c89b-449e-87fc-2e457f12e8c2', 'DEL1') # segment
    text = text.replace('86423c72-ff81-42e1-88df-b747b0a70146', 'DEL2') # via
    # Delete by uuid
    text = re.sub(r'\t\((?:segment|via)[\s\S]*?DEL[12][\s\S]*?\n\t\)', '', text)
    # Also remove any remaining segment mentioning (start 7.25 6.99) or (end 6.5 6.99)
    text = re.sub(r'\t\(segment[\s\S]*?7\.25 6\.99[\s\S]*?\n\t\)', '', text)
    text = re.sub(r'\t\(via[\s\S]*?6\.5 6\.99[\s\S]*?\n\t\)', '', text)

    # Update VR_PA via from (4.5 8.2) to (3.615 7.6)
    text = text.replace('(at 4.5 8.199999)', '(at 3.615 7.6)')
    text = text.replace('(start 4.5 8.199999)\n\t\t(end 3.5 8.199999)', '(start 3.615 7.6)\n\t\t(end 3.5 7.6)\n\t)\n\t(segment\n\t\t(start 3.5 7.6)\n\t\t(end 3.5 8.199999)')
    text = text.replace('(end 4.5 8.199999)', '(end 3.615 7.6)')

    # Remove all old VR_PA segments by UUID
    text = text.replace('3f83d549-d423-4c15-8e93-485c538b696e', 'DEL_VRPA1')
    text = text.replace('63bf6428-73fc-4bf2-9b4e-2ad7fd9d86c4', 'DEL_VRPA2')
    text = re.sub(r'\t\(segment[\s\S]*?DEL_VRPA[12][\s\S]*?\n\t\)', '', text)

    # Remove all old BOOT0 segments and via
    text = text.replace('bda44e89-5e41-4a92-b03e-a0fb7c310d93', 'DEL_BOOT1')
    text = text.replace('ad8c6d70-6333-40a5-90ed-21a5db795e24', 'DEL_BOOT2')
    text = text.replace('876490cb-8f39-4df1-bb6d-61910e36dbe9', 'DEL_BOOT3')
    text = text.replace('abe23e48-bc45-48e0-93ef-cb8eb7990a65', 'DEL_BOOT4')
    text = text.replace('f877d22f-8598-4667-b2f0-bee5537190e2', 'DEL_BOOT5')
    text = re.sub(r'\t\((?:segment|via)[\s\S]*?DEL_BOOT[12345][\s\S]*?\n\t\)', '', text)

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
    idx = text.find("\t(segment")
    text = text[:idx] + rf_fps + text[idx:]

    # Get tracks
    rf_tracks = tracks_func(l3_pos, c23_pos, c22_pos, r1_pos)

    zone_idx = text.find('\t(zone\n\t\t(net "/GND")')
    if zone_idx != -1:
        text = text[:zone_idx] + rf_tracks + text[zone_idx:]
    else:
        text = text.replace('\t(zone', rf_tracks + '\t(zone', 1)

    out_file = "Device1/hardware/test_solve.kicad_pcb"
    with open(out_file, "w") as f:
        f.write(text)

    # Run DRC
    cmd = ["kicad-cli", "pcb", "drc", "--refill-zones", "--severity-all", out_file]
    res = subprocess.run(cmd, capture_output=True, text=True)
    m_v = re.search(r"Found (\d+) DRC violations", res.stdout)
    m_u = re.search(r"Found (\d+) unconnected items", res.stdout)
    v = int(m_v.group(1)) if m_v else -1
    u = int(m_u.group(1)) if m_u else -1
    print(f"[{name}] Violations: {v}, Unconnected: {u}")
    return v, u, res.stdout

print("Test variant framework ready.")
