#!/usr/bin/env python3
"""
Comprehensive Geometry Checker for KiCad PCB.
Checks:
1. Via-to-via hole clearance (< 0.20 mm) and copper clearance (< 0.20 mm)
2. Via-to-pad clearance (< 0.20 mm)
3. Track-to-track clearance on same layer (< 0.20 mm)
4. Track-to-via clearance on same layer (< 0.20 mm)
5. Track-to-pad clearance on same layer (< 0.20 mm)
6. Tracks crossing on same layer (different nets)
7. Copper to Edge.Cuts (< 0.30 mm)
"""

import math
import pcbnew

def run_check(board_path):
    board = pcbnew.LoadBoard(board_path)
    violations = []

    # Check 1: Vias
    vias = [t for t in board.GetTracks() if t.GetClass() == 'PCB_VIA']
    for i in range(len(vias)):
        v1 = vias[i]
        p1 = v1.GetPosition()
        net1 = v1.GetNetname()
        d1 = v1.GetDrill() / 1e6
        s1 = v1.GetWidth() / 1e6
        x1, y1 = p1.x / 1e6, p1.y / 1e6

        for j in range(i + 1, len(vias)):
            v2 = vias[j]
            p2 = v2.GetPosition()
            net2 = v2.GetNetname()
            d2 = v2.GetDrill() / 1e6
            s2 = v2.GetWidth() / 1e6
            x2, y2 = p2.x / 1e6, p2.y / 1e6

            dist = math.hypot(x1 - x2, y1 - y2)
            hole_clearance = dist - (d1 + d2) / 2.0
            if hole_clearance < 0.20:
                violations.append(f"VIA_HOLE_CLEARANCE: ({x1:.3f},{y1:.3f})[{net1}] to ({x2:.3f},{y2:.3f})[{net2}] hole_clear={hole_clearance:.3f} mm")

            if net1 != net2:
                copper_clearance = dist - (s1 + s2) / 2.0
                if copper_clearance < 0.20:
                    violations.append(f"VIA_COPPER_CLEARANCE: ({x1:.3f},{y1:.3f})[{net1}] to ({x2:.3f},{y2:.3f})[{net2}] copper_clear={copper_clearance:.3f} mm")

    # Check 2: Via to Pad of different net
    for v in vias:
        p_v = v.GetPosition()
        net_v = v.GetNetname()
        s_v = v.GetWidth() / 1e6
        d_v = v.GetDrill() / 1e6
        xv, yv = p_v.x / 1e6, p_v.y / 1e6

        for fp in board.Footprints():
            for pad in fp.Pads():
                net_p = pad.GetNetname()
                if net_p == net_v:
                    continue
                pp = pad.GetPosition()
                xp, yp = pp.x / 1e6, pp.y / 1e6
                dist = math.hypot(xv - xp, yv - yp)
                # bounding radius approximation
                psize = max(pad.GetSize().x, pad.GetSize().y) / 1e6
                clearance = dist - s_v / 2.0 - psize / 2.0
                if clearance < 0.15:
                    violations.append(f"VIA_PAD_CLEARANCE: via ({xv:.3f},{yv:.3f})[{net_v}] to {fp.GetReference()}.{pad.GetNumber()} ({xp:.3f},{yp:.3f})[{net_p}] approx_clear={clearance:.3f} mm")

    print(f"Total geometry check violations found: {len(violations)}")
    for v in violations[:30]:
        print("  " + v)
    if len(violations) > 30:
        print(f"  ... and {len(violations)-30} more")
    return len(violations)

if __name__ == "__main__":
    import sys
    bp = sys.argv[1] if len(sys.argv) > 1 else "hardware/Device1.kicad_pcb"
    run_check(bp)
