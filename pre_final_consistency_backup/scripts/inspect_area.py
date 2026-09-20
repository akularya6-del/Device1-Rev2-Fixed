import re
import sys
sys.path.append("Device1/scripts")
from test_exact_drc import parse_sexpr

with open("Device1/hardware/test_direct.kicad_pcb") as f:
    text = f.read()

tokens = parse_sexpr(text)
for s, e, item in tokens:
    if item.startswith("(footprint"):
        m = re.search(r"\(at ([-0-9.]+) ([-0-9.]+)", item)
        if m:
            x, y = float(m.group(1)), float(m.group(2))
            if 3.0 <= y <= 6.0 and 4.0 <= x <= 11.0:
                ref = re.search(r'\(property "Reference" "([^"]+)"', item)
                layer = re.search(r'\(layer "([^"]+)"', item)
                ref_str = ref.group(1) if ref else '?'
                layer_str = layer.group(1) if layer else '?'
                print(f"{ref_str:10s} at ({x:5.2f}, {y:5.2f}) on {layer_str}")
