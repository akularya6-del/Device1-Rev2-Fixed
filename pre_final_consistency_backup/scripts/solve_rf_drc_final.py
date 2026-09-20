import subprocess
import os
import re
import sys
sys.path.append("Device1/scripts")
from solve_rf_clean import get_base_board
from test_exact_drc import parse_sexpr

def evaluate(layout_name, fps_sexpr, tracks_sexpr):
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

    idx = base_text.find("\t(segment")
    base_text = base_text[:idx] + fps_sexpr + base_text[idx:]

    zone_idx = base_text.find('\t(zone\n\t\t(net "/GND")')
    base_text = base_text[:zone_idx] + tracks_sexpr + base_text[zone_idx:]

    out_file = f"Device1/hardware/test_{layout_name}.kicad_pcb"
    with open(out_file, "w") as f:
        f.write(base_text)

    subprocess.run(["cp", "Device1/hardware/test_direct.kicad_pro", f"Device1/hardware/test_{layout_name}.kicad_pro"])
    rpt_file = f"test_{layout_name}-drc.rpt"
    res = subprocess.run(["kicad-cli", "pcb", "drc", "--refill-zones", "--severity-all", "--output", rpt_file, out_file], capture_output=True, text=True)
    if res.returncode != 0 and not os.path.exists(rpt_file):
        print("kicad-cli error:", res.stderr, res.stdout)
    with open(rpt_file) as f:
        rpt = f.read()

    vios = re.findall(r"\[([a-z_]+)\]: ([^\n]+)", rpt)
    print(f"[{layout_name}] Found {len(vios)} violations:")
    for v in vios:
        print("  ", v)
    return len(vios), vios

print("Final DRC evaluator ready.")
