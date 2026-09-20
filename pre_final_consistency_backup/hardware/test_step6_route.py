import sys, os
import pcbnew

def mm_to_nm(mm): return int(mm * 1e6)
def nm_to_mm(nm): return nm / 1e6
def vec(x, y): return pcbnew.VECTOR2I(mm_to_nm(x), mm_to_nm(y))

board = pcbnew.LoadBoard("hardware/test_step.kicad_pcb")

# Net references
raw_nets = board.GetNetsByName()
nets = {}
for k, v in raw_nets.items():
    s = str(k)
    nets[s] = v
    nets[s.lstrip('/')] = v


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

# 1. Q1 internal drain connection: Q1.2 to Q1.3 on F.Cu
add_track(6.362, 24.20, 6.362, 25.15, pcbnew.F_Cu, nets["Net-(Q1-D12-Pad2)"], 0.20)

# 2. BATT_POS: U4.5 to TP_BATT_P (4.8, 24.2)
add_via(4.80, 24.20, nets["BATT_POS"])
add_track(4.138, 24.20, 4.80, 24.20, pcbnew.F_Cu, nets["BATT_POS"], 0.20)

# 3. GATE_OD: U4.1 (1.863, 23.25) -> Q1.6 (8.637, 23.25)
route_points([(1.863, 23.25), (1.863, 22.40), (8.637, 22.40), (8.637, 23.25)], pcbnew.F_Cu, nets["GATE_OD"], 0.15)

# 4. GATE_OC: U4.3 (1.863, 25.15) -> Q1.5 (8.637, 24.20)
route_points([(1.863, 25.15), (1.863, 25.80), (9.85, 25.80), (9.85, 24.20), (8.637, 24.20)], pcbnew.F_Cu, nets["GATE_OC"], 0.15)

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

out_file = "hardware/test_step6_try.kicad_pcb"
board.Save(out_file)
print("Saved to", out_file)
