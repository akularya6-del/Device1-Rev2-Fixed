import subprocess
import re
import os

def run_drc(pcb_path):
    cmd = ["kicad-cli", "pcb", "drc", "--refill-zones", "--severity-all", pcb_path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    m_v = re.search(r"Found (\d+) DRC violations", res.stdout)
    m_u = re.search(r"Found (\d+) unconnected items", res.stdout)
    m_f = re.search(r"Found (\d+) Footprint errors", res.stdout)
    v = int(m_v.group(1)) if m_v else -1
    u = int(m_u.group(1)) if m_u else -1
    f = int(m_f.group(1)) if m_f else -1
    return v, u, f, res.stdout

print("Script runner ready.")
