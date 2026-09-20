import re
import subprocess
import sys
import os
sys.path.append("Device1/scripts")
from solve_rf_clean import get_base_board
from test_exact_drc import parse_sexpr

def build_and_test(c22_pos, l3_pos, c23_pos, boot0_via, label="test"):
    base_text = get_base_board()

    # Remove old RFO_HP segment
    tokens = parse_sexpr(base_text)
    removals = []
    for s, e, item in tokens:
        if 'net "/RFO_HP"' in item and "segment" in item:
            if "9.5625" in item or "7.285" in item:
                removals.append((s, e))

    for s, e in sorted(removals, reverse=True):
        base_text = base_text[:s] + base_text[e:]

    c22_x, c22_y, c22_rot = c22_pos
    l3_x, l3_y, l3_rot = l3_pos
    c23_x, c23_y, c23_rot = c23_pos
    bvia_x, bvia_y = boot0_via

    fps = f"""
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
\t\t(at {l3_x} {l3_y} {l3_rot})
\t\t(descr "Inductor SMD 0402 (1005 Metric)")
\t\t(property "Reference" "L3" (at 0 -1.17 {l3_rot}) (layer "F.SilkS") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(property "Value" "18nH" (at 0 1.17 {l3_rot}) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(attr smd)
\t\t(fp_rect (start {"-0.47 -0.93" if l3_rot==90 else "-0.93 -0.47"}) (end {"0.47 0.93" if l3_rot==90 else "0.93 0.47"}) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
\t\t(fp_rect (start {"-0.25 -0.5" if l3_rot==90 else "-0.5 -0.25"}) (end {"0.25 0.5" if l3_rot==90 else "0.5 0.25"}) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
\t\t(pad "1" smd roundrect (at {"-0.485 0 90" if l3_rot==90 else "-0.485 0"}) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RFI_N"))
\t\t(pad "2" smd roundrect (at {"0.485 0 90" if l3_rot==90 else "0.485 0"}) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RFI_P"))
\t)
\t(footprint "C_0402_1005Metric"
\t\t(layer "F.Cu")
\t\t(uuid "70010001-0000-4000-8000-000000000022")
\t\t(at {c22_x} {c22_y} {c22_rot})
\t\t(descr "Capacitor SMD 0402 (1005 Metric)")
\t\t(property "Reference" "C22" (at 0 -1.17 {c22_rot}) (layer "F.SilkS") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(property "Value" "1.5pF" (at 0 1.17 {c22_rot}) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(attr smd)
\t\t(fp_rect (start {"-0.47 -0.93" if c22_rot==90 else "-0.93 -0.47"}) (end {"0.47 0.93" if c22_rot==90 else "0.93 0.47"}) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
\t\t(fp_rect (start {"-0.25 -0.5" if c22_rot==90 else "-0.5 -0.25"}) (end {"0.25 0.5" if c22_rot==90 else "0.5 0.25"}) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
\t\t(pad "1" smd roundrect (at {"-0.485 0 90" if c22_rot==90 else "-0.485 0"}) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RF_50OHM"))
\t\t(pad "2" smd roundrect (at {"0.485 0 90" if c22_rot==90 else "0.485 0"}) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RFI_P"))
\t)
\t(footprint "C_0402_1005Metric"
\t\t(layer "F.Cu")
\t\t(uuid "70010001-0000-4000-8000-000000000023")
\t\t(at {c23_x} {c23_y} {c23_rot})
\t\t(descr "Capacitor SMD 0402 (1005 Metric)")
\t\t(property "Reference" "C23" (at 0 -1.17 {c23_rot}) (layer "F.SilkS") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(property "Value" "1.5pF" (at 0 1.17 {c23_rot}) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))
\t\t(attr smd)
\t\t(fp_rect (start {"-0.47 -0.93" if c23_rot==90 else "-0.93 -0.47"}) (end {"0.47 0.93" if c23_rot==90 else "0.93 0.47"}) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
\t\t(fp_rect (start {"-0.25 -0.5" if c23_rot==90 else "-0.5 -0.25"}) (end {"0.25 0.5" if c23_rot==90 else "0.5 0.25"}) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
\t\t(pad "1" smd roundrect (at {"-0.485 0 90" if c23_rot==90 else "-0.485 0"}) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/RFI_N"))
\t\t(pad "2" smd roundrect (at {"0.485 0 90" if c23_rot==90 else "0.485 0"}) (size 0.59 0.64) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (net "/GND"))
\t)
"""

    tracks = f"""
\t(segment (start 4.75 9.5625) (end 4.75 9.1) (width 0.15) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000001"))
\t(segment (start 4.75 9.1) (end 3.615 9.1) (width 0.15) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000002"))
\t(segment (start 3.615 9.1) (end 3.615 8.25) (width 0.15) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000003"))
\t(segment (start 3.615 8.25) (end 3.615 7.6) (width 0.2) (layer "F.Cu") (net "/VR_PA") (uuid "70020001-0000-4000-8000-000000000004"))

\t(segment (start 5.25 9.5625) (end 5.25 8.6) (width 0.15) (layer "F.Cu") (net "/RFO_HP") (uuid "70020001-0000-4000-8000-000000000005"))
\t(segment (start 5.25 8.6) (end 4.585 8.25) (width 0.15) (layer "F.Cu") (net "/RFO_HP") (uuid "70020001-0000-4000-8000-000000000006"))
\t(segment (start 4.585 8.25) (end 5.25 7.285) (width 0.2) (layer "F.Cu") (net "/RFO_HP") (uuid "70020001-0000-4000-8000-000000000007"))
\t(segment (start 5.25 7.285) (end 4.28 6.80) (width 0.2) (layer "F.Cu") (net "/RFO_HP") (uuid "70020001-0000-4000-8000-000000000008"))

\t(segment (start 7.25 9.5625) (end 7.25 {bvia_y}) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000020"))
\t(via (at {bvia_x} {bvia_y}) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000021"))
\t(segment (start {bvia_x} {bvia_y}) (end 5.6 {bvia_y}) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000022"))
\t(segment (start 5.6 {bvia_y}) (end 5.6 4.0) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000023"))
\t(segment (start 5.6 4.0) (end 7.25 4.0) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000024"))
\t(via (at 7.25 4.0) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000025"))
\t(segment (start 7.25 4.0) (end 7.415 4.2) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "70020001-0000-4000-8000-000000000026"))
"""

    idx = base_text.find("\t(segment")
    base_text = base_text[:idx] + fps + base_text[idx:]

    zone_idx = base_text.find('\t(zone\n\t\t(net "/GND")')
    base_text = base_text[:zone_idx] + tracks + base_text[zone_idx:]

    out_file = f"Device1/hardware/test_{label}.kicad_pcb"
    with open(out_file, "w") as f:
        f.write(base_text)

    subprocess.run(["cp", "Device1/hardware/test_direct.kicad_pro", f"Device1/hardware/test_{label}.kicad_pro"])
    res = subprocess.run(["kicad-cli", "pcb", "drc", "--refill-zones", "--severity-all", out_file], capture_output=True, text=True)
    with open(f"test_{label}-drc.rpt") as f:
        rpt = f.read()

    vios = re.findall(r"\[([a-z_]+)\]: ([^\n]+)", rpt)
    return len(vios), vios, rpt

print("Solver framework ready.")
