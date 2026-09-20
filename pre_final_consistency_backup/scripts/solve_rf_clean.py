import re
import subprocess
import sys
sys.path.append("Device1/scripts")
from test_exact_drc import parse_sexpr

def get_base_board():
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

    return text

print("Base board generator ready.")
