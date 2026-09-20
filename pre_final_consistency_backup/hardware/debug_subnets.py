#!/usr/bin/env python3
import subprocess
import pcbnew
import re

def eval_drc(board, step_name):
    tmp_pcb = "hardware/test_step.kicad_pcb"
    board.Save(tmp_pcb)
    res = subprocess.run(
        ["/opt/homebrew/bin/kicad-cli", "pcb", "drc", "--severity-all", tmp_pcb],
        capture_output=True, text=True
    )
    with open("test_step-drc.rpt") as f:
        text = f.read()
    violations = re.findall(r'\[(.*?)\]:', text)
    from collections import Counter
    c = Counter(violations)
    unc = len(re.findall(r'\[unconnected_items\]', text))
    print(f"[{step_name}] Total: {len(violations)}, Unconnected: {unc}, Breakdown: {dict(c)}")
    if len(violations) > 0:
        blocks = [b.strip() for b in text.split('\n[') if b.strip()]
        for b in blocks[1:6]:
            lines = [l.strip() for l in b.split('\n') if l.strip()]
            header = lines[0].split(']')[0]
            items = ' vs '.join([l for l in lines[1:] if l.startswith('@(')])
            if not items:
                items = ' | '.join(lines[1:3])
            print(f"    - [{header}] {items}")

if __name__ == "__main__":
    print("Debug subnets ready.")
