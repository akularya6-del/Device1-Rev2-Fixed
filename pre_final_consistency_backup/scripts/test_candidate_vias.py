import re
import subprocess

with open("Device1/hardware/test_solve.kicad_pcb", "r") as f:
    base_text = f.read()

# Let us remove the old BOOT0 via at (7.25 9.15) and old BOOT0 tracks
# and test placing a via at different coordinates
def test_via_at(vx, vy):
    text = base_text
    # remove current BOOT0 tracks and vias
    text = re.sub(r'\t\(segment[\s\S]*?net "/BOOT0"[\s\S]*?\n\t\)', '', text)
    text = re.sub(r'\t\(via[\s\S]*?net "/BOOT0"[\s\S]*?\n\t\)', '', text)

    # add a simple test via at (vx, vy)
    # F.Cu track from U1 Pin 19 (7.25, 9.5625) to (vx, vy)
    # Via at (vx, vy)
    # B.Cu track from (vx, vy) to (5.6, vy) -> (5.6, 4.0) -> (7.25, 4.0)
    boot0_tracks = f"""
\t(segment (start 7.25 9.5625) (end {vx} {vy}) (width 0.15) (layer "F.Cu") (net "/BOOT0") (uuid "80010001-0000-4000-8000-000000000001"))
\t(via (at {vx} {vy}) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/BOOT0") (uuid "80010001-0000-4000-8000-000000000002"))
\t(segment (start {vx} {vy}) (end 5.6 {vy}) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "80010001-0000-4000-8000-000000000003"))
\t(segment (start 5.6 {vy}) (end 5.6 4.0) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "80010001-0000-4000-8000-000000000004"))
\t(segment (start 5.6 4.0) (end 7.25 4.0) (width 0.15) (layer "B.Cu") (net "/BOOT0") (uuid "80010001-0000-4000-8000-000000000005"))
"""
    idx = text.find('\t(zone\n\t\t(net "/GND")')
    text = text[:idx] + boot0_tracks + text[idx:]

    with open("Device1/hardware/test_via_tmp.kicad_pcb", "w") as f:
        f.write(text)

    cmd = ["kicad-cli", "pcb", "drc", "--refill-zones", "--severity-all", "Device1/hardware/test_via_tmp.kicad_pcb"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    m_v = re.search(r"Found (\d+) DRC violations", res.stdout)
    v = int(m_v.group(1)) if m_v else -1
    return v, res.stdout

print("Testing via positions...")
best_v = 999
best_pos = None
for vx in [7.25, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 8.0]:
    for vy in [7.5, 7.6, 7.7, 7.8, 7.9, 8.0, 8.1, 8.2]:
        v, out = test_via_at(vx, vy)
        if v < best_v:
            best_v = v
            best_pos = (vx, vy)
            print(f"New best: {v} violations at ({vx}, {vy})")

print(f"Done. Best: {best_v} violations at {best_pos}")
