import pcbnew
import sys
import subprocess

def build_rf_board(in_pcb, out_pcb):
    # Read text to ensure nets exist in s-expression
    with open(in_pcb, "r") as f:
        text = f.read()

    # Ensure U1 pin 20 and 21 have nets /RFI_P and /RFI_N
    old_p20 = """\t\t(pad "20" smd roundrect
\t\t\t(at 0.75 3.4375 180)
\t\t\t(size 0.25 0.875)
\t\t\t(layers "F.Cu" "F.Mask" "F.Paste")
\t\t\t(roundrect_rratio 0.25)
\t\t\t(uuid "0bd38467-a83c-40b0-af2f-a039f84ccab0")
\t\t)"""
    new_p20 = """\t\t(pad "20" smd roundrect
\t\t\t(at 0.75 3.4375 180)
\t\t\t(size 0.25 0.875)
\t\t\t(layers "F.Cu" "F.Mask" "F.Paste")
\t\t\t(roundrect_rratio 0.25)
\t\t\t(net "/RFI_P")
\t\t\t(uuid "0bd38467-a83c-40b0-af2f-a039f84ccab0")
\t\t)"""

    old_p21 = """\t\t(pad "21" smd roundrect
\t\t\t(at 1.25 3.4375 180)
\t\t\t(size 0.25 0.875)
\t\t\t(layers "F.Cu" "F.Mask" "F.Paste")
\t\t\t(roundrect_rratio 0.25)
\t\t\t(uuid "06e99a04-7cc4-4c60-87d2-cb5a250cef99")
\t\t)"""
    new_p21 = """\t\t(pad "21" smd roundrect
\t\t\t(at 1.25 3.4375 180)
\t\t\t(size 0.25 0.875)
\t\t\t(layers "F.Cu" "F.Mask" "F.Paste")
\t\t\t(roundrect_rratio 0.25)
\t\t\t(net "/RFI_N")
\t\t\t(uuid "06e99a04-7cc4-4c60-87d2-cb5a250cef99")
\t\t)"""

    text = text.replace(old_p20, new_p20).replace(old_p21, new_p21)
    with open(out_pcb, "w") as f:
        f.write(text)

    # Now load board with pcbnew
    board = pcbnew.LoadBoard(out_pcb)
    
    net_ant = board.FindNet("/ANT_FEED")
    net_rfo = board.FindNet("/RFO_HP")
    net_rf50 = board.FindNet("/RF_50OHM")
    net_vrpa = board.FindNet("/VR_PA")
    net_gnd = board.FindNet("/GND")
    net_rfip = board.FindNet("/RFI_P")
    net_rfin = board.FindNet("/RFI_N")
    net_boot0 = board.FindNet("/BOOT0")
    net_nrst = board.FindNet("/NRST")

    print(f"Loaded nets: RFI_P={net_rfip is not None}, RFI_N={net_rfin is not None}")

    # 1. Replace ANT1
    ant1_old = board.FindFootprintByReference("ANT1")
    if ant1_old:
        board.Remove(ant1_old)
    ant1_new = pcbnew.FootprintLoad("Device1/hardware/Device1.pretty", "Johanson_0868AT43A0020E_CUSTOM")
    ant1_new.SetReference("ANT1")
    ant1_new.SetValue("0868AT43A0020E")
    ant1_new.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(7.5), pcbnew.FromMM(2.0)))
    ant1_new.Reference().SetVisible(False)
    ant1_new.Value().SetVisible(False)
    ant1_new.FindPadByNumber("1").SetNet(net_ant)
    board.Add(ant1_new)

    # Remove old ANT_FEED tracks near (4.65, 2.0)
    for track in list(board.GetTracks()):
        if track.GetClass() == "PCB_TRACK" and track.GetNetname() == "/ANT_FEED":
            sx, sy = pcbnew.ToMM(track.GetStart().x), pcbnew.ToMM(track.GetStart().y)
            ex, ey = pcbnew.ToMM(track.GetEnd().x), pcbnew.ToMM(track.GetEnd().y)
            if abs(sy - 2.0) < 0.1 or abs(ey - 2.0) < 0.1 or abs(sy - 2.9) < 0.1 or abs(ey - 2.9) < 0.1:
                board.Remove(track)

    def add_track(net, x1, y1, x2, y2, width=0.20, layer=pcbnew.F_Cu):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        t.SetWidth(pcbnew.FromMM(width))
        t.SetLayer(layer)
        t.SetNet(net)
        board.Add(t)
        return t

    # New ANT_FEED tracks
    add_track(net_ant, 5.25, 3.50, 4.45, 2.70, 0.29)
    add_track(net_ant, 4.45, 2.70, 4.45, 2.00, 0.29)

    # 2. Shift R_TEST east to (8.50, 5.20)
    # Remove old R_TEST tracks/vias
    r_test = board.FindFootprintByReference("R_TEST")
    if r_test:
        r_test.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(8.50), pcbnew.FromMM(5.20)))
        # Connect R_TEST pad 1 (8.015, 5.20) to RF_50OHM
        add_track(net_rf50, 6.75, 5.20, 8.015, 5.20, 0.20)
        # Shift TP_RF via from (7.31, 5.20) to (8.985, 5.20)
        for track in board.GetTracks():
            if track.GetClass() == "PCB_VIA":
                vx, vy = pcbnew.ToMM(track.GetPosition().x), pcbnew.ToMM(track.GetPosition().y)
                if abs(vx - 7.31) < 0.05 and abs(vy - 5.20) < 0.05:
                    track.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(8.985), pcbnew.FromMM(5.20)))
            elif track.GetClass() == "PCB_TRACK" and track.GetNetname() == "/TP_RF":
                # update connection to via
                sx, sy = pcbnew.ToMM(track.GetStart().x), pcbnew.ToMM(track.GetStart().y)
                ex, ey = pcbnew.ToMM(track.GetEnd().x), pcbnew.ToMM(track.GetEnd().y)
                if abs(sx - 7.31) < 0.05 and abs(sy - 5.20) < 0.05:
                    track.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(8.985), pcbnew.FromMM(5.20)))
                if abs(ex - 7.31) < 0.05 and abs(ey - 5.20) < 0.05:
                    track.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(8.985), pcbnew.FromMM(5.20)))

    # 3. Add L2 (47nH RF choke) at (4.50, 8.28), rot=0
    l1 = board.FindFootprintByReference("L1")
    l2 = pcbnew.Cast_to_FOOTPRINT(l1.Duplicate(False))
    l2.SetReference("L2")
    l2.SetValue("47nH")
    l2.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(4.50), pcbnew.FromMM(8.28)))
    l2.SetOrientationDegrees(0.0)
    l2.Reference().SetVisible(False)
    l2.Value().SetVisible(False)
    l2.FindPadByNumber("1").SetNet(net_vrpa)
    l2.FindPadByNumber("2").SetNet(net_rfo)
    board.Add(l2)
    # Connect L2 pad 2 (4.985, 8.28) to RFO_HP trace at (5.25, 8.28)
    add_track(net_rfo, 4.985, 8.28, 5.25, 8.28, 0.20)

    # 4. Add L3 (18nH Balun) at (6.50, 8.28), rot=0
    l3 = pcbnew.Cast_to_FOOTPRINT(l1.Duplicate(False))
    l3.SetReference("L3")
    l3.SetValue("18nH")
    l3.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(6.50), pcbnew.FromMM(8.28)))
    l3.SetOrientationDegrees(0.0)
    l3.Reference().SetVisible(False)
    l3.Value().SetVisible(False)
    l3.FindPadByNumber("1").SetNet(net_rfin)
    l3.FindPadByNumber("2").SetNet(net_rfip)
    board.Add(l3)
    # Connect L3 pad 1 (6.015, 8.28) to U1 Pin 21 (6.25, 9.5625)
    add_track(net_rfin, 6.25, 9.5625, 6.25, 8.515, 0.15)
    add_track(net_rfin, 6.25, 8.515, 6.015, 8.28, 0.15)
    # Connect L3 pad 2 (6.985, 8.28) to U1 Pin 20 (6.75, 9.5625)
    add_track(net_rfip, 6.75, 9.5625, 6.75, 8.515, 0.15)
    add_track(net_rfip, 6.75, 8.515, 6.985, 8.28, 0.15)

    # 5. Add C23 (1.5pF Balance cap) at (6.25, 6.80), rot=90
    c13 = board.FindFootprintByReference("C13")
    c23 = pcbnew.Cast_to_FOOTPRINT(c13.Duplicate(False))
    c23.SetReference("C23")
    c23.SetValue("1.5pF")
    c23.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(6.25), pcbnew.FromMM(6.80)))
    c23.SetOrientationDegrees(90.0)
    c23.Reference().SetVisible(False)
    c23.Value().SetVisible(False)
    c23.FindPadByNumber("1").SetNet(net_rfin)
    c23.FindPadByNumber("2").SetNet(net_gnd)
    board.Add(c23)
    # Connect C23 Pad 1 (6.25, 7.285) to L3 Pad 1 (6.015, 8.28)
    add_track(net_rfin, 6.25, 7.285, 6.25, 8.045, 0.15)
    add_track(net_rfin, 6.25, 8.045, 6.015, 8.28, 0.15)

    # 6. Add C22 (1.5pF Coupling cap) at (6.75, 5.20), rot=0
    c22 = pcbnew.Cast_to_FOOTPRINT(c13.Duplicate(False))
    c22.SetReference("C22")
    c22.SetValue("1.5pF")
    c22.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(6.75), pcbnew.FromMM(5.20)))
    c22.SetOrientationDegrees(0.0)
    c22.Reference().SetVisible(False)
    c22.Value().SetVisible(False)
    c22.FindPadByNumber("1").SetNet(net_rf50)
    c22.FindPadByNumber("2").SetNet(net_rfip)
    board.Add(c22)
    # Connect C22 Pad 1 (6.265, 5.20) to RF_50OHM trace at (5.25, 5.20)
    add_track(net_rf50, 6.265, 5.20, 5.25, 5.20, 0.20)
    # Connect C22 Pad 2 (7.235, 5.20) north to L3 Pad 2 (6.985, 8.28)
    add_track(net_rfip, 7.235, 5.20, 7.235, 8.035, 0.15)
    add_track(net_rfip, 7.235, 8.035, 6.985, 8.28, 0.15)

    # Refill zones and save
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(out_pcb)
    print("PCB layout successfully written to", out_pcb)

if __name__ == "__main__":
    build_rf_board("Device1/hardware/Device1.kicad_pcb", "Device1/hardware/test_rf_clean.kicad_pcb")
