import re
import sys
sys.path.append("Device1/scripts")
from test_exact_drc import parse_sexpr

with open("Device1/hardware/test_direct.kicad_pcb") as f:
    text = f.read()

tokens = parse_sexpr(text)

fps = []
tracks = []
vias = []

for s, e, item in tokens:
    tag = item[1:].split()[0]
    if tag == "footprint":
        m = re.search(r'\(property "Reference" "([^"]+)"', item)
        mat = re.search(r'\(at ([-0-9.]+) ([-0-9.]+)(?: ([-0-9.]+))?', item)
        layer = re.search(r'\(layer "([^"]+)"', item)
        if mat:
            x, y = float(mat.group(1)), float(mat.group(2))
            rot = float(mat.group(3)) if mat.group(3) else 0.0
            if 3.0 <= y <= 10.0 and 2.0 <= x <= 11.0:
                fps.append((m.group(1) if m else '?', x, y, rot, layer.group(1) if layer else '?'))
    elif tag == "segment":
        pts = re.findall(r"\(start ([-0-9.]+) ([-0-9.]+)\)\s+\(end ([-0-9.]+) ([-0-9.]+)\)", item)
        layer = re.search(r'\(layer "([^"]+)"', item)
        net = re.search(r'\(net "([^"]+)"', item)
        if pts:
            x1, y1, x2, y2 = [float(p) for p in pts[0]]
            if (3.0 <= y1 <= 10.0 and 2.0 <= x1 <= 11.0) or (3.0 <= y2 <= 10.0 and 2.0 <= x2 <= 11.0):
                tracks.append((net.group(1) if net else '?', layer.group(1) if layer else '?', x1, y1, x2, y2))
    elif tag == "via":
        mat = re.search(r'\(at ([-0-9.]+) ([-0-9.]+)\)', item)
        net = re.search(r'\(net "([^"]+)"', item)
        if mat:
            x, y = float(mat.group(1)), float(mat.group(2))
            if 3.0 <= y <= 10.0 and 2.0 <= x <= 11.0:
                vias.append((net.group(1) if net else '?', x, y))

print("=== FOOTPRINTS ===")
for f in sorted(fps, key=lambda x: (x[2], x[1])):
    print(f"  {f[0]:12s} at ({f[1]:5.2f}, {f[2]:5.2f}, rot={f[3]:3.0f}) on {f[4]}")

print("\n=== VIAS ===")
for v in sorted(vias, key=lambda x: (x[2], x[1])):
    print(f"  {v[0]:15s} at ({v[1]:5.2f}, {v[2]:5.2f})")

print("\n=== TRACKS (sample) ===")
for t in tracks[:25]:
    print(f"  {t[0]:15s} on {t[1]:5s}: ({t[2]:5.2f}, {t[3]:5.2f}) -> ({t[4]:5.2f}, {t[5]:5.2f})")
