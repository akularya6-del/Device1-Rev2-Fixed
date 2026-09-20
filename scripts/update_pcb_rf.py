import pcbnew
import sys
import os

def update_pcb(in_path, out_path):
    board = pcbnew.LoadBoard(in_path)
    
    # 1. Update ANT1
    ant1 = board.FindFootprintByReference("ANT1")
    if not ant1:
        print("ERROR: ANT1 not found!")
        return False
    
    print("Found ANT1 at", pcbnew.ToMM(ant1.GetPosition().x), pcbnew.ToMM(ant1.GetPosition().y))
    # Update ANT1 properties
    ant1.SetValue("0868AT43A0020E")
    ant1.SetDescription("Johanson Technology 0868AT43A0020E 868MHz Ceramic Chip Antenna (7.0x2.0mm body, land pattern 1.0x1.8mm pads, 5.1mm gap, 6.1mm pitch)")
    
    # Update pads of ANT1
    for pad in ant1.Pads():
        num = pad.GetNumber()
        if num == "1":
            pad.SetPos0(pcbnew.VECTOR2I(pcbnew.FromMM(-3.05), 0))
            pad.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(7.5 - 3.05), pcbnew.FromMM(2.0)))
            pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.0), pcbnew.FromMM(1.8)))
            pad.SetRoundRectRadiusRatio(0.2)
        elif num == "2":
            pad.SetPos0(pcbnew.VECTOR2I(pcbnew.FromMM(3.05), 0))
            pad.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(7.5 + 3.05), pcbnew.FromMM(2.0)))
            pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.0), pcbnew.FromMM(1.8)))
            pad.SetRoundRectRadiusRatio(0.2)
            
    # Update graphical lines of ANT1: remove old graphics and add new
    # Keep fab and silk lines matching 0868AT43A0020E
    for item in list(ant1.GraphicalItems()):
        ant1.Remove(item)
        
    def add_line(layer, x1, y1, x2, y2, width):
        line = pcbnew.PCB_SHAPE(ant1)
        line.SetShape(pcbnew.SHAPE_T_SEGMENT)
        line.SetLayer(layer)
        line.SetWidth(pcbnew.FromMM(width))
        line.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        line.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        ant1.Add(line)
        
    # Fab lines (body 7.0x2.0)
    add_line(pcbnew.F_Fab, -3.5, -1.0, -3.0, -1.0, 0.1)
    add_line(pcbnew.F_Fab, -3.5, -0.5, -3.5, 1.0, 0.1)
    add_line(pcbnew.F_Fab, -3.5, -0.5, -3.0, -1.0, 0.1)
    add_line(pcbnew.F_Fab, -3.5, 1.0, 3.5, 1.0, 0.1)
    add_line(pcbnew.F_Fab, 3.5, 1.0, 3.5, -1.0, 0.1)
    add_line(pcbnew.F_Fab, 3.5, -1.0, -3.0, -1.0, 0.1)
    # Silk
    add_line(pcbnew.F_SilkS, -2.3, -1.15, 2.3, -1.15, 0.12)
    add_line(pcbnew.F_SilkS, -2.3, 1.15, 2.3, 1.15, 0.12)
    # Courtyard
    add_line(pcbnew.F_CrtYd, -3.8, -1.25, 3.8, -1.25, 0.05)
    add_line(pcbnew.F_CrtYd, 3.8, -1.25, 3.8, 1.25, 0.05)
    add_line(pcbnew.F_CrtYd, 3.8, 1.25, -3.8, 1.25, 0.05)
    add_line(pcbnew.F_CrtYd, -3.8, 1.25, -3.8, -1.25, 0.05)

    # 2. Update /ANT_FEED track segments
    net_ant = board.FindNet("/ANT_FEED")
    # Remove old track segments near (4.65, 2.0)
    tracks_to_remove = []
    for track in board.GetTracks():
        if track.GetClass() == "PCB_TRACK":
            s = track.GetStart()
            e = track.GetEnd()
            sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
            ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
            if abs(sy - 2.0) < 0.05 or abs(ey - 2.0) < 0.05 or abs(sx - 4.65) < 0.05 or abs(ex - 4.65) < 0.05:
                if track.GetNetname() == "/ANT_FEED":
                    tracks_to_remove.append(track)
                    
    for t in tracks_to_remove:
        board.Remove(t)
        print("Removed old ANT_FEED track")
        
    def add_track(net, x1, y1, x2, y2, width, layer=pcbnew.F_Cu):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        t.SetWidth(pcbnew.FromMM(width))
        t.SetLayer(layer)
        t.SetNet(net)
        board.Add(t)
        return t

    # New ANT_FEED tracks: (5.25, 3.5) -> (4.45, 2.7) -> (4.45, 2.0)
    add_track(net_ant, 5.25, 3.50, 4.45, 2.70, 0.29)
    add_track(net_ant, 4.45, 2.70, 4.45, 2.00, 0.29)
    print("Added new ANT_FEED track segments terminating at (4.45, 2.00)")

    # Save initial board
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(out_path)
    print("Saved to", out_path)
    return True

if __name__ == "__main__":
    update_pcb("Device1/hardware/Device1.kicad_pcb", "Device1/hardware/test_ant_pcb.kicad_pcb")
