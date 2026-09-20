#!/usr/bin/env python3
"""
Stepwise DRC solver script.
"""
import subprocess

# Run solve_drc.py then run kicad-cli DRC
res = subprocess.run(["/opt/homebrew/Caskroom/kicad/10.0.6/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3", "hardware/solve_drc.py"], capture_output=True, text=True)
print("Generator output:", res.stdout.strip())
if res.returncode != 0:
    print("Error:", res.stderr)

drc = subprocess.run(["/opt/homebrew/bin/kicad-cli", "pcb", "drc", "--severity-all", "hardware/Device1.kicad_pcb"], capture_output=True, text=True)
print("DRC output:", drc.stdout.strip())
