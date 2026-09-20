import sys
sys.path.append("Device1/scripts")
from auto_solve_drc import build_and_test

# Test candidates
# C22: between RF_50OHM and RFI_P
# L3: between RFI_P and RFI_N
# C23: between RFI_N and GND
# boot0_via: (x, y)

candidates = [
    # Candidate 1:
    # L3 at (6.65, 8.35, rot=0), C22 at (6.65, 7.25, rot=0), C23 at (6.65, 6.20, rot=0), boot0_via=(7.25, 7.85)
    ((6.65, 7.25, 0), (6.65, 8.35, 0), (6.65, 6.20, 0), (7.25, 7.85), "c1"),

    # Candidate 2:
    # L3 at (6.60, 8.35, rot=0), C22 at (6.60, 7.25, rot=0), C23 at (6.60, 6.20, 0), boot0_via=(7.25, 7.85)
    ((6.60, 7.25, 0), (6.60, 8.35, 0), (6.60, 6.20, 0), (7.25, 7.85), "c2"),

    # Candidate 3:
    # L3 at (6.55, 8.35, rot=0), C22 at (6.55, 7.25, rot=0), C23 at (6.55, 6.20, 0), boot0_via=(7.25, 7.85)
    ((6.55, 7.25, 0), (6.55, 8.35, 0), (6.55, 6.20, 0), (7.25, 7.85), "c3"),

    # Candidate 4:
    # L3 at (6.50, 8.35, rot=0), C22 at (6.50, 7.25, rot=0), C23 at (6.50, 6.20, 0), boot0_via=(7.25, 7.85)
    ((6.50, 7.25, 0), (6.50, 8.35, 0), (6.50, 6.20, 0), (7.25, 7.85), "c4"),
]

for c22, l3, c23, bvia, label in candidates:
    count, vios, rpt = build_and_test(c22, l3, c23, bvia, label)
    print(f"[{label}] violations={count}")
    for vtype, vdesc in vios[:5]:
        print(f"   {vtype}: {vdesc}")
