import re
import subprocess
import sys
import os

# Helper to parse s-expressions
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

# Clean base board
with open("Device1/hardware/test_direct.kicad_pcb", "r") as f:
    base_text = f.read()

# Update R1 position to (7.9, 4.2)
base_text = re.sub(
    r'(\(footprint [^\n]+\n\t\t\(layer "F\.Cu"\)\n\t\t\(uuid "[^"]+"\)\n\t\t\(at )7\.25 7\.5 90(\).*?\(property "Reference" "R1")',
    r'\g<1>7.9 4.2 0\g<2>',
    base_text,
    flags=re.DOTALL
)

# Update VR_PA via to (3.615 7.6)
base_text = base_text.replace('(at 4.5 8.199999)', '(at 3.615 7.6)')
base_text = base_text.replace('(start 4.5 8.199999)\n\t\t(end 3.5 8.199999)', '(start 3.615 7.6)\n\t\t(end 3.5 7.6)\n\t)\n\t(segment\n\t\t(start 3.5 7.6)\n\t\t(end 3.5 8.199999)')
base_text = base_text.replace('(end 4.5 8.199999)', '(end 3.615 7.6)')

tokens = parse_sexpr(base_text)
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
    base_text = base_text[:s] + base_text[e:]

print("Clean base board created with", len(removals), "removals.")
