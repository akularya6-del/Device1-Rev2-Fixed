import sys, os
import pcbnew, subprocess

def mm_to_nm(mm): return int(mm * 1e6)
def nm_to_mm(nm): return nm / 1e6
def vec(x, y): return pcbnew.VECTOR2I(mm_to_nm(x), mm_to_nm(y))

board = pcbnew.LoadBoard('Device1/hardware/test_vbus_in2.kicad_pcb')
raw_nets = board.GetNetsByName()
nets = {str(k).lstrip('/'): v for k, v in raw_nets.items()}

def add_track(x1, y1, x2, y2, layer, net, width=0.15):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(vec(x1, y1))
    t.SetEnd(vec(x2, y2))
    t.SetWidth(mm_to_nm(width))
    t.SetLayer(layer)
    t.SetNet(net)
    board.Add(t)
    return t

def add_via(x, y, net, drill=0.25, size=0.45, layer1=pcbnew.F_Cu, layer2=pcbnew.B_Cu):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(vec(x, y))
    v.SetWidth(mm_to_nm(size))
    v.SetDrill(mm_to_nm(drill))
    v.SetLayerPair(layer1, layer2)
    v.SetNet(net)
    board.Add(v)
    return v

def route_points(points, layer, net, width=0.15):
    for i in range(len(points) - 1):
        add_track(points[i][0], points[i][1], points[i+1][0], points[i+1][1], layer, net, width)

print("--- Routing MIC_WS ---")
# U1.32 @ (4.0625, 13.750) -> MK1.1 @ (6.600, 27.136)
# Escape west on F.Cu to (3.10, 13.75)
add_track(4.0625, 13.750, 3.100, 13.750, pcbnew.F_Cu, nets['MIC_WS'], 0.15)
add_via(3.100, 13.750, nets['MIC_WS'])
# On B.Cu, go along X=3.20 down to Y=25.80, then jog east to X=6.60, then to Y=26.40
route_points([(3.100, 13.750), (3.200, 13.750), (3.200, 25.800), (6.600, 25.800), (6.600, 26.400)], pcbnew.B_Cu, nets['MIC_WS'], 0.15)
add_via(6.600, 26.400, nets['MIC_WS'])
add_track(6.600, 26.400, 6.600, 27.136, pcbnew.F_Cu, nets['MIC_WS'], 0.15)

print("--- Routing MIC_SD ---")
# U1.33 @ (4.0625, 14.250) -> MK1.6 @ (7.500, 27.136)
# Pin 33 escapes west on F.Cu to (2.60, 14.25) -> (2.60, 15.00) -> via at (2.60, 15.00)
# Wait, let's check via at (2.60, 15.00):
# Pad 36 (/SWDIO) is at (4.062, 15.750). Via /SWDIO is at (2.20, 15.75).
# Center between (2.20, 15.75) and (4.062, 15.75) is ~3.10.
# At (3.10, 14.80), distance to SWDIO via (2.20, 15.75) is sqrt(0.9^2 + 0.95^2) = 1.31 mm.
# Distance to Pin 33 (4.062, 14.25) is sqrt(0.96^2 + 0.55^2) = 1.1 mm.
add_track(4.0625, 14.250, 3.100, 14.800, pcbnew.F_Cu, nets['MIC_SD'], 0.15)
add_via(3.100, 14.800, nets['MIC_SD'])
# On B.Cu, go to X=6.20 at Y=14.80, down to Y=25.20, then jog east to X=7.50, then to Y=26.40
route_points([(3.100, 14.800), (6.200, 14.800), (6.200, 25.200), (7.500, 25.200), (7.500, 26.400)], pcbnew.B_Cu, nets['MIC_SD'], 0.15)
add_via(7.500, 26.400, nets['MIC_SD'])
add_track(7.500, 26.400, 7.500, 27.136, pcbnew.F_Cu, nets['MIC_SD'], 0.15)

print("--- Routing MIC_SCK ---")
# U1.17 @ (8.250, 9.562) -> MK1.4 @ (8.400, 27.958)
# Escape north on F.Cu to (8.250, 9.100) -> (9.000, 9.100) -> (9.000, 8.300)
route_points([(8.250, 9.5625), (8.250, 9.100), (9.000, 9.100), (9.000, 8.300)], pcbnew.F_Cu, nets['MIC_SCK'], 0.15)
add_via(9.000, 8.300, nets['MIC_SCK'])
# On In2.Cu: go around thermal pad & obstacles
# (9.00, 8.30) -> (9.00, 16.50) -> (7.80, 17.50) -> (7.80, 26.50) -> (9.00, 27.50)
# Wait, let's check In2.Cu at Y=24.80: remember BATT_NEG is at Y=24.80 on In2.Cu!
# So on In2.Cu, we can't cross Y=24.80 at X in [4.138, 8.637]!
# But can MIC_SCK stay EAST of X=8.637, e.g. at X=9.00 on B.Cu?
# Let's check: on B.Cu, what is at X=9.00?
# LED_R_DRV is at X=10.00! GND via at (9.20, 19.80).
# If MIC_SCK jogs to X=8.60 around Y=19.80:
# (9.00, 8.30) -> (9.00, 18.50) -> (8.50, 19.00) -> (8.50, 20.00)...
# Or on In2.Cu: east of 8.637, e.g. X=9.00:
# At X=9.00, Y=24.80: BATT_NEG ends at (8.637, 25.150)!
# So X=9.00 is EAST of BATT_NEG on In2.Cu!
# Let's test on In2.Cu:
route_points([(9.000, 8.300), (9.000, 18.500), (8.400, 19.800), (8.400, 23.500), (8.900, 24.500), (8.900, 27.500)], pcbnew.In2_Cu, nets['MIC_SCK'], 0.15)
add_via(8.900, 27.500, nets['MIC_SCK'])
add_track(8.900, 27.500, 8.400, 27.958, pcbnew.F_Cu, nets['MIC_SCK'], 0.15)

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
board.Save('Device1/hardware/test_step7_eval.kicad_pcb')
print("Saved test_step7_eval.kicad_pcb")
