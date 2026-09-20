import sys
sys.path.append("Device1/scripts")
from solve_rf_drc_final import evaluate

# Let's test a via on net /GND right at C23 Pad 2 (7.135, 7.10) or (7.135, 7.00)
def test_gnd_via(via_x, via_y):
    with open("Device1/scripts/test_zero_triumph.py") as f:
        text = f.read()

    fps = text.split('fps = """')[1].split('"""')[0]
    tracks = text.split('tracks = """')[1].split('"""')[0]

    # Replace GND segment with via:
    old_gnd = '\t(segment (start 7.135 7.10) (end 7.38 7.10) (width 0.15) (layer "F.Cu") (net "/GND") (uuid "70020001-0000-4000-8000-000000000027"))'
    new_gnd = f'\t(via (at {via_x} {via_y}) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/GND") (uuid "70020001-0000-4000-8000-000000000027"))'
    tracks = tracks.replace(old_gnd, new_gnd)

    name = f"gnd_via_{str(via_x).replace('.', '')}_{str(via_y).replace('.', '')}"
    cnt, vios = evaluate(name, fps, tracks)
    print(f"Via at ({via_x}, {via_y}): {cnt} violations: {vios}")

test_gnd_via(7.135, 7.10)
