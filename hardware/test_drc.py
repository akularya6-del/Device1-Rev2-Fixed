#!/usr/bin/env python3
import subprocess
import re

def run_drc():
    res = subprocess.run(
        ["/opt/homebrew/bin/kicad-cli", "pcb", "drc", "--severity-all", "hardware/Device1.kicad_pcb"],
        capture_output=True, text=True
    )
    report = res.stdout + res.stderr
    with open("Device1-drc.rpt") as f:
        text = f.read()
    
    # parse summary
    violations = re.findall(r'\[(.*?)\]:', text)
    from collections import Counter
    c = Counter(violations)
    print("Violations summary:", dict(c))
    unconnected = re.findall(r'\[unconnected_items\]', text)
    print(f"Total violations: {len(violations)}, Unconnected: {len(unconnected)}")
    
    # print all violations in detail (first 20)
    blocks = [b.strip() for b in text.split('\n[') if b.strip()]
    print("\n--- Details of first 20 violations ---")
    for i, b in enumerate(blocks[1:21]):
        lines = [l.strip() for l in b.split('\n') if l.strip()]
        header = lines[0]
        items = " | ".join(lines[1:3])
        print(f"{i+1:02d}: [{header}] ::: {items}")

if __name__ == "__main__":
    run_drc()
