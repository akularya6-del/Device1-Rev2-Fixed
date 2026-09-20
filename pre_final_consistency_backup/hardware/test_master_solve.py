import sys, os
import pcbnew

def mm_to_nm(mm): return int(mm * 1e6)
def nm_to_mm(nm): return nm / 1e6
def vec(x, y): return pcbnew.VECTOR2I(mm_to_nm(x), mm_to_nm(y))

board = pcbnew.LoadBoard('Device1/hardware/test_nrst_flawless.kicad_pcb')
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

def add_via(x, y, net, drill=0.25, size=0.45):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(vec(x, y))
    v.SetWidth(mm_to_nm(size))
    v.SetDrill(mm_to_nm(drill))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(net)
    board.Add(v)
    return v

def route_points(points, layer, net, width=0.15):
    for i in range(len(points) - 1):
        add_track(points[i][0], points[i][1], points[i+1][0], points[i+1][1], layer, net, width)

print("1. Routing MIC_WS...")
add_track(4.0625, 13.750, 3.100, 13.750, pcbnew.F_Cu, nets['MIC_WS'], 0.15)
add_track(3.100, 13.750, 3.100, 13.300, pcbnew.F_Cu, nets['MIC_WS'], 0.15)
add_via(3.100, 13.300, nets['MIC_WS'])
route_points([(3.100, 13.300), (0.600, 13.300), (0.600, 25.900), (6.600, 25.900), (6.600, 26.400)], pcbnew.B_Cu, nets['MIC_WS'], 0.15)
add_via(6.600, 26.400, nets['MIC_WS'])
add_track(6.600, 26.400, 6.600, 27.136, pcbnew.F_Cu, nets['MIC_WS'], 0.15)

print("2. Routing MIC_SD...")
add_track(4.0625, 14.250, 3.200, 14.250, pcbnew.F_Cu, nets['MIC_SD'], 0.15)
add_via(3.200, 14.250, nets['MIC_SD'])
route_points([(3.200, 14.250), (3.200, 25.300), (7.500, 25.300), (7.500, 26.400)], pcbnew.B_Cu, nets['MIC_SD'], 0.15)
add_via(7.500, 26.400, nets['MIC_SD'])
add_track(7.500, 26.400, 7.500, 27.136, pcbnew.F_Cu, nets['MIC_SD'], 0.15)

print("3. Routing MIC_SCK...")
# From (8.250, 9.5625) to (8.400, 8.700) on F.Cu
add_track(8.250, 9.5625, 8.400, 8.700, pcbnew.F_Cu, nets['MIC_SCK'], 0.15)
add_via(8.400, 8.700, nets['MIC_SCK'])
route_points([(8.400, 8.700), (5.400, 8.700), (5.400, 15.500), (6.200, 16.500), (6.200, 24.600), (8.050, 24.600), (8.050, 27.958)], pcbnew.B_Cu, nets['MIC_SCK'], 0.15)
add_via(8.050, 27.958, nets['MIC_SCK'])
add_track(8.050, 27.958, 8.400, 27.958, pcbnew.F_Cu, nets['MIC_SCK'], 0.15)

print("Filling zones...")
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
board.Save('Device1/hardware/test_master_solved.kicad_pcb')
print("Successfully generated test_master_solved.kicad_pcb")
