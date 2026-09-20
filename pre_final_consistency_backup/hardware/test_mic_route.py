import sys, os
import pcbnew

def mm_to_nm(mm): return int(mm * 1e6)
def nm_to_mm(nm): return nm / 1e6
def vec(x, y): return pcbnew.VECTOR2I(mm_to_nm(x), mm_to_nm(y))

# Load test_vbus_in2 board (which has 0 DRC errors, only 3 mic nets unconnected)
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

print("Adding MIC routes...")

# 1. MIC_WS (U1.32 @ 4.0625, 13.750 -> MK1.1 @ 6.600, 27.136)
# Escape west on F.Cu
add_track(4.0625, 13.75, 3.30, 13.75, pcbnew.F_Cu, nets['MIC_WS'], 0.15)
add_track(3.30, 13.75, 3.30, 13.30, pcbnew.F_Cu, nets['MIC_WS'], 0.15)
add_via(3.30, 13.30, nets['MIC_WS'])
# On B.Cu, go to X=6.20, down to Y=26.40, jog to X=6.60
route_points([(3.30, 13.30), (6.20, 13.30), (6.20, 26.40), (6.60, 26.40)], pcbnew.B_Cu, nets['MIC_WS'], 0.15)
add_via(6.60, 26.40, nets['MIC_WS'])
add_track(6.60, 26.40, 6.60, 27.136, pcbnew.F_Cu, nets['MIC_WS'], 0.15)

# 2. MIC_SD (U1.33 @ 4.0625, 14.250 -> MK1.6 @ 7.500, 27.136)
# Escape west on F.Cu to (3.10, 14.25)
add_track(4.0625, 14.25, 3.10, 14.25, pcbnew.F_Cu, nets['MIC_SD'], 0.15)
add_via(3.10, 14.25, nets['MIC_SD'])
# On B.Cu, go down along X=3.45 to Y=25.50
route_points([(3.10, 14.25), (3.45, 14.25), (3.45, 25.50)], pcbnew.B_Cu, nets['MIC_SD'], 0.15)
# Via to In2.Cu or F.Cu at (3.45, 25.50)
# Let's check: can we via from B.Cu to F.Cu at (7.50, 25.50)?
# Wait, let's test if In2.Cu or B.Cu works:
# If MIC_SD stays on In2.Cu from (3.45, 25.50) to (7.50, 25.50):
add_via(3.45, 25.50, nets['MIC_SD'], layer1=pcbnew.B_Cu, layer2=pcbnew.In2_Cu)
route_points([(3.45, 25.50), (7.50, 25.50)], pcbnew.In2_Cu, nets['MIC_SD'], 0.15)
add_via(7.50, 25.50, nets['MIC_SD'], layer1=pcbnew.In2_Cu, layer2=pcbnew.F_Cu)
add_track(7.50, 25.50, 7.50, 27.136, pcbnew.F_Cu, nets['MIC_SD'], 0.15)

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
board.Save('Device1/hardware/test_mic_temp.kicad_pcb')
print("Saved test_mic_temp.kicad_pcb")
