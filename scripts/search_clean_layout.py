import re
import subprocess
import sys
import math

# We want to find a layout of:
# L2 at (4.10, 8.25, rot=0)
# R1 at (7.90, 4.20, rot=0)
# L3, C22, C23 positions and orientations
# that produces 0 courtyard overlaps AND 0 DRC violations.

# Fixed obstacles (courtyards):
fixed_crts = [
    ("U1", 3.87, 11.13, 8.87, 17.13),
    ("L1", 4.78, 5.72, 5.87, 7.73),
    ("L2", 3.17, 5.03, 7.78, 8.72),
    ("R_ANT", 4.78, 5.72, 3.87, 5.73),
    ("C14", 2.87, 4.73, 4.73, 5.67),
    ("C13", 2.87, 4.73, 6.33, 7.27),
    ("R_TEST", 5.87, 7.73, 4.73, 5.67),
    ("C11", 8.03, 8.97, 6.57, 8.43),
    ("R1", 6.97, 8.83, 3.73, 4.67)
]

def get_crt(x, y, rot):
    if rot == 0:
        return (x - 0.93, x + 0.93, y - 0.47, y + 0.47)
    else:
        return (x - 0.47, x + 0.47, y - 0.93, y + 0.93)

def check_overlap(box1, box2):
    minx1, maxx1, miny1, maxy1 = box1
    minx2, maxx2, miny2, maxy2 = box2
    return not (maxx1 <= minx2 or maxx2 <= minx1 or maxy1 <= miny2 or maxy2 <= miny1)

valid_placements = []
# Grid search over candidate positions
for r3 in [0, 90]:
    for x3 in [6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9]:
        for y3 in [8.0, 8.1, 8.2, 8.3, 8.4]:
            b3 = get_crt(x3, y3, r3)
            if any(check_overlap(b3, f[1:]) for f in fixed_crts): continue

            for r22 in [0, 90]:
                for x22 in [6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9]:
                    for y22 in [6.2, 6.4, 6.6, 6.8, 7.0, 7.2, 7.4]:
                        b22 = get_crt(x22, y22, r22)
                        if check_overlap(b3, b22): continue
                        if any(check_overlap(b22, f[1:]) for f in fixed_crts): continue

                        for r23 in [0, 90]:
                            for x23 in [6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9]:
                                for y23 in [6.0, 6.2, 6.4, 6.6, 6.8, 7.0, 7.2, 7.4]:
                                    b23 = get_crt(x23, y23, r23)
                                    if check_overlap(b3, b23) or check_overlap(b22, b23): continue
                                    if any(check_overlap(b23, f[1:]) for f in fixed_crts): continue

                                    valid_placements.append((
                                        (x3, y3, r3),
                                        (x22, y22, r22),
                                        (x23, y23, r23)
                                    ))

print(f"Found {len(valid_placements)} valid collision-free footprint placements!")
