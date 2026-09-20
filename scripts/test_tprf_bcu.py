import subprocess
import re
import sys
sys.path.append("Device1/scripts")
from solve_rf_clean import get_base_board
from test_exact_drc import parse_sexpr

text = get_base_board()

# In get_base_board, let's also update TP_RF track on B.Cu:
# Replace:
# (segment (start 7.31 5.2) (end 7.31 7.2) ... (layer "B.Cu") (net "/TP_RF"))
# (segment (start 7.31 7.2) (end 9.8 7.2) ... (layer "B.Cu") (net "/TP_RF"))
# with:
# (segment (start 7.31 5.2) (end 9.8 5.2) (width 0.2) (layer "B.Cu") (net "/TP_RF"))
# (segment (start 9.8 5.2) (end 9.8 7.2) (width 0.2) (layer "B.Cu") (net "/TP_RF"))

tokens = parse_sexpr(text)
removals = []
for s, e, item in tokens:
    if 'net "/TP_RF"' in item and "segment" in item and "B.Cu" in item:
        removals.append((s, e))

for s, e in sorted(removals, reverse=True):
    text = text[:s] + text[e:]

new_tprf = """
\t(segment (start 7.31 5.2) (end 9.8 5.2) (width 0.2) (layer "B.Cu") (net "/TP_RF") (uuid "70030001-0000-4000-8000-000000000001"))
\t(segment (start 9.8 5.2) (end 9.8 7.2) (width 0.2) (layer "B.Cu") (net "/TP_RF") (uuid "70030001-0000-4000-8000-000000000002"))
"""
zone_idx = text.find('\t(zone\n\t\t(net "/GND")')
text = text[:zone_idx] + new_tprf + text[zone_idx:]

with open("Device1/hardware/test_tprf.kicad_pcb", "w") as f:
    f.write(text)
subprocess.run(["cp", "Device1/hardware/test_direct.kicad_pro", "Device1/hardware/test_tprf.kicad_pro"])

res = subprocess.run(["kicad-cli", "pcb", "drc", "--refill-zones", "--severity-all", "Device1/hardware/test_tprf.kicad_pcb"], capture_output=True, text=True)
with open("test_tprf-drc.rpt") as f:
    rpt = f.read()

vios = re.findall(r"\[([a-z_]+)\]: ([^\n]+)", rpt)
print(f"Total violations with rerouted TP_RF on B.Cu: {len(vios)}")
for v in vios:
    print("  ", v)
