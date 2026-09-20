import subprocess
import re
import sys

def run_drc():
    cmd = ["kicad-cli", "pcb", "drc", "--refill-zones", "--severity-all", "Device1/hardware/test_solve.kicad_pcb"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    m_v = re.search(r"Found (\d+) DRC violations", res.stdout)
    m_u = re.search(r"Found (\d+) unconnected items", res.stdout)
    v = int(m_v.group(1)) if m_v else -1
    u = int(m_u.group(1)) if m_u else -1
    return v, u, res.stdout

print("Optimizer module ready.")
