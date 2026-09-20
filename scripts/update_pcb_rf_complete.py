import pcbnew
import sys
import os

def update_pcb_full(pcb_path):
    board = pcbnew.LoadBoard(pcb_path)
    
    # -------------------------------------------------------------
    # 1. Update ANT1 Footprint & Feed Track
    # -------------------------------------------------------------
    ant1_old = board.FindFootprintByReference("ANT1")
    if ant1_old:
        board.Remove(ant1_old)
        print("Removed old ANT1 footprint")
        
    ant1_new = pcbnew.FootprintLoad("Device1/hardware/Device1.pretty", "Johanson_0868AT43A0020E_CUSTOM")
    ant1_new.SetReference("ANT1")
    ant1_new.SetValue("0868AT43A0020E")
    ant1_new.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(7.5), pcbnew.FromMM(2.0)))
    ant1_new.Reference().SetVisible(False)
    ant1_new.Value().SetVisible(False)

    net_ant = board.FindNet("/ANT_FEED")
    pad1 = ant1_new.FindPadByNumber("1")
    pad1.SetNet(net_ant)
    board.Add(ant1_new)
    print("Added Johanson_0868AT43A0020E_CUSTOM footprint as ANT1")

    # Remove old track segments near (4.65, 2.0)
    tracks_to_remove = []
    for track in board.GetTracks():
        if track.GetClass() == "PCB_TRACK":
            s = track.GetStart()
            e = track.GetEnd()
            sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
            ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
            if (abs(sy - 2.0) < 0.05 and abs(sx - 4.65) < 0.05) or \
               (abs(ey - 2.0) < 0.05 and abs(ex - 4.65) < 0.05) or \
               (abs(sy - 2.9) < 0.05 and abs(sx - 4.65) < 0.05) or \
               (abs(ey - 2.9) < 0.05 and abs(ex - 4.65) < 0.05):
                if track.GetNetname() == "/ANT_FEED":
                    tracks_to_remove.append(track)

    for t in tracks_to_remove:
        board.Remove(t)
        print("Removed old ANT_FEED track segment")

    # Add new ANT_FEED track segments: (5.25, 3.50) -> (4.45, 2.70) -> (4.45, 2.00)
    def add_track(net, x1, y1, x2, y2, width, layer=pcbnew.F_Cu):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        t.SetWidth(pcbnew.FromMM(width))
        t.SetLayer(layer)
        t.SetNet(net)
        board.Add(t)
        return t

    add_track(net_ant, 5.25, 3.50, 4.45, 2.70, 0.29)
    add_track(net_ant, 4.45, 2.70, 4.45, 2.00, 0.29)
    print("Routed new 50-ohm ANT_FEED track to Pad 1 at (4.45, 2.00)")

    # -------------------------------------------------------------
    # 2. Nets & U1 Pin 20/21 assignment
    # -------------------------------------------------------------
    u1 = board.FindFootprintByReference("U1")
    net_rfo = board.FindNet("/RFO_HP")
    net_rf50 = board.FindNet("/RF_50OHM")
    net_vrpa = board.FindNet("/VR_PA")
    net_gnd = board.FindNet("/GND")

    # Fetch or create RFI_P and RFI_N nets
    # In KiCad 10, nets can be retrieved or assigned via pad.SetNet
    # If board doesn't have RFI_P, we can find it or ensure it exists
    # First check if nets exist in board
    net_rfip = board.FindNet("/RFI_P")
    net_rfin = board.FindNet("/RFI_N")
    
    # Assign U1 pin 20 and pin 21
    pad20 = u1.FindPadByNumber("20")
    pad21 = u1.FindPadByNumber("21")
    if net_rfip:
        pad20.SetNet(net_rfip)
    if net_rfin:
        pad21.SetNet(net_rfin)
    print("U1 pin 20 and pin 21 nets set")

    # -------------------------------------------------------------
    # 3. Move R1 GND via from (6.50, 6.99) to (7.25, 6.30)
    # -------------------------------------------------------------
    for track in board.GetTracks():
        if track.GetClass() == "PCB_VIA":
            pos = track.GetPosition()
            x, y = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
            if abs(x - 6.50) < 0.05 and abs(y - 6.99) < 0.05:
                track.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(7.25), pcbnew.FromMM(6.30)))
                print("Moved R1 GND via to (7.25, 6.30)")
        elif track.GetClass() == "PCB_TRACK":
            s, e = track.GetStart(), track.GetEnd()
            sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
            ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
            if (abs(sx - 7.25) < 0.05 and abs(sy - 6.99) < 0.05 and abs(ex - 6.50) < 0.05 and abs(ey - 6.99) < 0.05) or \
               (abs(ex - 7.25) < 0.05 and abs(ey - 6.99) < 0.05 and abs(sx - 6.50) < 0.05 and abs(sy - 6.99) < 0.05):
                track.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(7.25), pcbnew.FromMM(6.99)))
                track.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(7.25), pcbnew.FromMM(6.30)))
                print("Updated R1 GND track to connect to (7.25, 6.30)")

    # -------------------------------------------------------------
    # 4. Create L2 (47nH RF Choke)
    # -------------------------------------------------------------
    # Duplicate an 0402 footprint (L1 or C13)
    l1 = board.FindFootprintByReference("L1")
    l2 = pcbnew.Cast_to_FOOTPRINT(l1.Duplicate(False))
    l2.SetReference("L2")
    l2.SetValue("47nH")
    l2.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(4.80), pcbnew.FromMM(8.40)))
    l2.SetOrientationDegrees(0.0)
    l2.Reference().SetVisible(False)
    l2.Value().SetVisible(False)

    p1 = l2.FindPadByNumber("1")
    p2 = l2.FindPadByNumber("2")
    p1.SetNet(net_vrpa)
    p2.SetNet(net_rfo)
    board.Add(l2)
    print("Added L2 at (4.80, 8.40)")

    # Connect L2 Pad 1 (4.315, 8.40) to VR_PA trace at (4.50, 8.40)
    add_track(net_vrpa, 4.315, 8.40, 4.50, 8.40, 0.20)
    # Connect L2 Pad 2 (5.285, 8.40) to RFO_HP trace at (5.25, 8.40)
    add_track(net_rfo, 5.285, 8.40, 5.25, 8.40, 0.20)

    # -------------------------------------------------------------
    # 5. Create L3 (18nH Balun Inductor)
    # -------------------------------------------------------------
    l3 = pcbnew.Cast_to_FOOTPRINT(l1.Duplicate(False))
    l3.SetReference("L3")
    l3.SetValue("18nH")
    l3.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(6.25), pcbnew.FromMM(8.65)))
    l3.SetOrientationDegrees(0.0)
    l3.Reference().SetVisible(False)
    l3.Value().SetVisible(False)

    p1 = l3.FindPadByNumber("1")
    p2 = l3.FindPadByNumber("2")
    if net_rfin:
        p1.SetNet(net_rfin)
    if net_rfip:
        p2.SetNet(net_rfip)
    board.Add(l3)
    print("Added L3 at (6.25, 8.65)")

    # Connect L3 Pad 1 (5.765, 8.65) to U1 Pin 21 (6.25, 9.5625)
    add_track(net_rfin, 6.25, 9.5625, 6.25, 9.135, 0.15)
    add_track(net_rfin, 6.25, 9.135, 5.765, 8.65, 0.15)
    # Connect L3 Pad 2 (6.735, 8.65) to U1 Pin 20 (6.75, 9.5625)
    add_track(net_rfip, 6.75, 9.5625, 6.75, 8.65, 0.15)
    add_track(net_rfip, 6.75, 8.65, 6.735, 8.65, 0.15)

    # -------------------------------------------------------------
    # 6. Create C23 (1.5pF Balance Capacitor to GND)
    # -------------------------------------------------------------
    c13 = board.FindFootprintByReference("C13")
    c23 = pcbnew.Cast_to_FOOTPRINT(c13.Duplicate(False))
    c23.SetReference("C23")
    c23.SetValue("1.5pF")
    c23.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(5.765), pcbnew.FromMM(7.65)))
    c23.SetOrientationDegrees(90.0)
    c23.Reference().SetVisible(False)
    c23.Value().SetVisible(False)

    p1 = c23.FindPadByNumber("1")
    p2 = c23.FindPadByNumber("2")
    if net_rfin:
        p1.SetNet(net_rfin)
    p2.SetNet(net_gnd)
    board.Add(c23)
    print("Added C23 at (5.765, 7.65)")

    # Connect C23 Pad 1 (5.765, 8.135) to L3 Pad 1 (5.765, 8.65)
    add_track(net_rfin, 5.765, 8.65, 5.765, 8.135, 0.15)

    # -------------------------------------------------------------
    # 7. Create C22 (1.5pF Coupling Capacitor)
    # -------------------------------------------------------------
    c22 = pcbnew.Cast_to_FOOTPRINT(c13.Duplicate(False))
    c22.SetReference("C22")
    c22.SetValue("1.5pF")
    c22.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(5.95), pcbnew.FromMM(6.315)))
    c22.SetOrientationDegrees(0.0)
    c22.Reference().SetVisible(False)
    c22.Value().SetVisible(False)

    p1 = c22.FindPadByNumber("1")
    p2 = c22.FindPadByNumber("2")
    p1.SetNet(net_rf50)
    if net_rfip:
        p2.SetNet(net_rfip)
    board.Add(c22)
    print("Added C22 at (5.95, 6.315)")

    # Connect C22 Pad 1 (5.465, 6.315) to L1 Pad 2 (5.25, 6.315)
    add_track(net_rf50, 5.465, 6.315, 5.25, 6.315, 0.20)

    # Connect C22 Pad 2 (6.435, 6.315) to RFI_P at L3 Pad 2 (6.735, 8.65)
    # Route: (6.435, 6.315) -> (6.435, 8.35) -> (6.735, 8.65)
    add_track(net_rfip, 6.435, 6.315, 6.435, 8.35, 0.15)
    add_track(net_rfip, 6.435, 8.35, 6.735, 8.65, 0.15)

    # -------------------------------------------------------------
    # 8. Refill zones & Save
    # -------------------------------------------------------------
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(pcb_path)
    print("Successfully saved updated PCB to", pcb_path)

if __name__ == "__main__":
    pcb = sys.argv[1] if len(sys.argv) > 1 else "Device1/hardware/Device1.kicad_pcb"
    update_pcb_full(pcb)
