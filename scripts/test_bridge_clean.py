import sys
sys.path.append("Device1/scripts")
from solve_rf_drc_final import evaluate
import ast

with open("Device1/scripts/test_candidate_base.py") as f:
    text = f.read()

fps_raw = text.split('fps = """')[1].split('"""')[0]
tracks_raw = text.split('tracks = """')[1].split('"""')[0]

fps = ast.literal_eval('"""' + fps_raw + '"""')
base_tracks = ast.literal_eval('"""' + tracks_raw + '"""')

def test_bridge(v1x, v1y, v2x, v2y):
    extra = f"""
\t(segment (start 6.485 8.38) (end {v1x} {v1y}) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000030"))
\t(via (at {v1x} {v1y}) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000031"))
\t(segment (start {v1x} {v1y}) (end {v2x} {v2y}) (width 0.15) (layer "B.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000032"))
\t(via (at {v2x} {v2y}) (size 0.45) (drill 0.25) (layers "F.Cu" "B.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000033"))
\t(segment (start {v2x} {v2y}) (end 7.135 6.15) (width 0.15) (layer "F.Cu") (net "/RFI_P") (uuid "70020001-0000-4000-8000-000000000034"))
"""
    name = f"b_{str(v1x).replace('.', '')}_{str(v1y).replace('.', '')}_{str(v2x).replace('.', '')}_{str(v2y).replace('.', '')}"
    cnt, vios = evaluate(name, fps, base_tracks + extra)
    print(f"Via bridge ({v1x}, {v1y}) -> ({v2x}, {v2y}): {cnt} violations")
    for v in vios:
        print("  ", v)
    return cnt

test_bridge(6.5, 7.8, 7.7, 6.15)
