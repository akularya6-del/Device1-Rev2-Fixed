import pcbnew
import math

board = pcbnew.LoadBoard("hardware/Device1.kicad_pcb")

# Load via list from verify_all_vias.py
with open("hardware/verify_all_vias.py") as f:
    code = f.read()

import ast
tree = ast.parse(code)
vias = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and node.targets[0].id == "vias":
        vias = ast.literal_eval(node.value)
        break

print(f"Loaded {len(vias)} vias from verify_all_vias.py")

fps = list(board.GetFootprints())

def get_pads(layer):
    pads = []
    for fp in fps:
        for p in fp.Pads():
            if p.GetLayerSet().Contains(layer):
                nname = p.GetNetname()
                pos = p.GetPosition()
                sz = p.GetSize()
                pads.append((fp.GetReference(), p.GetNumber(), nname, pos.x/1e6, pos.y/1e6, sz.x/1e6, sz.y/1e6))
    return pads

f_pads = get_pads(pcbnew.F_Cu)
b_pads = get_pads(pcbnew.B_Cu)

min_clear = 999.0
min_viol = None
viol_count = 0

for vx, vy, vnname in vias:
    # Check on F.Cu
    for ref, pnum, pnname, px, py, sx, sy in f_pads:
        if pnname != vnname and not (pnname.endswith(vnname) or vnname.endswith(pnname)):
            d = math.hypot(vx - px, vy - py)
            pr = max(sx, sy) / 2.0
            clear = d - pr - 0.30  # 0.30 is via annular ring radius
            if clear < min_clear:
                min_clear = clear
                min_viol = (f"Via ({vx},{vy}) {vnname}", f"F.Cu {ref}.{pnum} ({pnname})", clear)
            if clear < 0.15:
                viol_count += 1
                print(f"VIOLATION F.Cu: Via ({vx},{vy}) [{vnname}] to {ref}.{pnum} [{pnname}] clear={clear:.3f} mm")

    # Check on B.Cu
    for ref, pnum, pnname, px, py, sx, sy in b_pads:
        if pnname != vnname and not (pnname.endswith(vnname) or vnname.endswith(pnname)):
            d = math.hypot(vx - px, vy - py)
            pr = max(sx, sy) / 2.0
            clear = d - pr - 0.30
            if clear < min_clear:
                min_clear = clear
                min_viol = (f"Via ({vx},{vy}) {vnname}", f"B.Cu {ref}.{pnum} ({pnname})", clear)
            if clear < 0.15:
                viol_count += 1
                print(f"VIOLATION B.Cu: Via ({vx},{vy}) [{vnname}] to {ref}.{pnum} [{pnname}] clear={clear:.3f} mm")

print(f"Total violations (<0.15mm): {viol_count}")
print(f"Global minimum via-to-pad clearance: {min_clear:.3f} mm for {min_viol}")
