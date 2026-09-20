import sys
sys.path.append("Device1/scripts")
from solve_rf_drc_final import evaluate

# Let us test adding two vias on net /RFI_P to connect L3 Pad 2 (6.485, 8.38) to C22 Pad 2 (7.135, 6.15)
from test_candidate_base import test_candidate_1

# We will modify tracks to include:
# Via 1: at (v1x, v1y)
# Via 2: at (v2x, v2y)
# Track from (6.485, 8.38) to Via 1 on F.Cu
# Track from Via 1 to Via 2 on B.Cu
# Track from Via 2 to (7.135, 6.15) on F.Cu

def test_vias(v1x, v1y, v2x, v2y):
    with open("Device1/scripts/test_candidate_base.py") as f:
        code = f.read()

    # extract fps and tracks
    import re
    fps = re.search(r'fps = """([\s\S]*?)"""', code).group(1)
    tracks = re.search(r'tracks = """([\s\S]*?)"""', code).group(1)

    via_tracks = f"""
\t(segment (start 6.485 8.38) (end {v1x} {v1y}) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000030"))
\t(via (at {v1x} {v1y}) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000031"))
\t(segment (start {v1x} {v1y}) (end {v2x} {v2y}) (width 0.15) (layer "B.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000032"))
\t(via (at {v2x} {v2y}) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000033"))
\t(segment (start {v2x} {v2y}) (end 7.135 6.15) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000034"))
"""
    full_tracks = tracks + via_tracks
    name = f"via_{str(v1x).replace('.', '')}_{str(v1y).replace('.', '')}"
    cnt, vios = evaluate(name, fps, full_tracks)
    print(f"Result for ({v1x}, {v1y}) -> ({v2x}, {v2y}): {cnt} violations")
    for v in vios:
        print("  ", v)
    return cnt

# Let's test candidate via positions
test_vias(6.5, 7.8, 7.7, 6.15)
