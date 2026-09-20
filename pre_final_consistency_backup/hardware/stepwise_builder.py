#!/usr/bin/env python3
"""
Stepwise Board Builder & DRC Evaluator.
Builds the board subnet-by-subnet and evaluates DRC after each step.
"""

import os
import re
import math
import subprocess
import pcbnew

def mm_to_nm(mm):
    return int(mm * 1e6)

def nm_to_mm(nm):
    return nm / 1e6

def vec(x_mm, y_mm):
    return pcbnew.VECTOR2I(mm_to_nm(x_mm), mm_to_nm(y_mm))

def eval_drc(board, step_name):
    tmp_pcb = "hardware/test_step.kicad_pcb"
    board.Save(tmp_pcb)
    subprocess.run(
        ["/opt/homebrew/bin/kicad-cli", "pcb", "drc", "--severity-all", tmp_pcb],
        capture_output=True, text=True
    )
    with open("test_step-drc.rpt") as f:
        text = f.read()
    
    # Filter out unconnected_items to focus strictly on DRC violations
    violations = [v for v in re.findall(r'\[(.*?)\]:', text) if v != 'unconnected_items']
    from collections import Counter
    c = Counter(violations)
    print(f"\n>>> [{step_name}] DRC Violations: {len(violations)}, Breakdown: {dict(c)}")
    if len(violations) > 0:
        blocks = [b.strip() for b in text.split('\n[') if b.strip()]
        count = 0
        for b in blocks:
            lines = [l.strip() for l in b.split('\n') if l.strip()]
            header = lines[0].split(']')[0]
            if header == 'unconnected_items':
                continue
            items = ' vs '.join([l for l in lines[1:] if l.startswith('@(')])
            if not items:
                items = ' | '.join(lines[1:3])
            print(f"    * [{header}] {items}")
            count += 1
            if count >= 8:
                break

def run_stepwise():
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)
    
    settings = board.GetDesignSettings()
    settings.m_TrackMinWidth = mm_to_nm(0.127)
    settings.m_ViasMinSize = mm_to_nm(0.45)
    settings.m_ViasMinDrill = mm_to_nm(0.25)
    settings.m_MinThroughDrill = mm_to_nm(0.25)
    settings.m_CopperEdgeClearance = mm_to_nm(0.30)
    settings.m_HoleToHoleMin = mm_to_nm(0.20)
    settings.m_HoleClearance = mm_to_nm(0.20)
    settings.m_AllowSoldermaskBridgesInFPs = True
    
    # 1. Edge_Cuts
    w_mm, h_mm, r_mm = 15.0, 31.0, 1.0
    outline_segments = [
        ((r_mm, 0), (w_mm - r_mm, 0)),
        ((w_mm, r_mm), (w_mm, h_mm - r_mm)),
        ((w_mm - r_mm, h_mm), (r_mm, h_mm)),
        ((0, h_mm - r_mm), (0, r_mm)),
        ((r_mm, 0), (0, r_mm)),
        ((w_mm - r_mm, 0), (w_mm, r_mm)),
        ((w_mm, h_mm - r_mm), (w_mm - r_mm, h_mm)),
        ((r_mm, h_mm), (0, h_mm - r_mm))
    ]
    for (x1, y1), (x2, y2) in outline_segments:
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(vec(x1, y1))
        seg.SetEnd(vec(x2, y2))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(mm_to_nm(0.15))
        board.Add(seg)

    # 2. Nets
    net_path = "/Users/racoon/Documents/CHEATING/Device1/hardware/Device1.net"
    with open(net_path) as f:
        net_text = f.read()

    net_blocks = net_text.split('(net')[1:]
    net_mappings = {}
    for nb in net_blocks:
        name_m = re.search(r'\(name \"([^\"]+)\"\)', nb)
        if name_m:
            nname = name_m.group(1)
            nodes = re.findall(r'\(ref \"([^\"]+)\"\)\s+\(pin \"([^\"]+)\"\)', nb)
            net_mappings[nname] = nodes

    nets = {}
    for nname in net_mappings.keys():
        if not nname.startswith('unconnected-'):
            net_item = pcbnew.NETINFO_ITEM(board, nname)
            board.Add(net_item)
            nets[nname] = net_item
            if nname.startswith('/'):
                nets[nname[1:]] = net_item

    gnd_net = nets["GND"]
    p3v3_net = nets["3V3"]
    sys_net = nets["SYS_PWR"]

    # 3. Footprints
    lib_base = "/opt/homebrew/Caskroom/kicad/10.0.6/KiCad/KiCad.app/Contents/SharedSupport/footprints"
    def load_fp(pretty, name):
        return pcbnew.FootprintLoad(f"{lib_base}/{pretty}.pretty", name)

    fp_placements = [
        ("U1", "Package_DFN_QFN", "QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm", 7.5, 13.0, 180),
        ("ANT1", "RF_Antenna", "Johanson_2450AT43F0100", 7.5, 2.0, 0),
        ("MK1", "Sensor_Audio", "Knowles_SPH0645LM4H-6_3.5x2.65mm", 7.5, 28.5, 0),
        ("Y1", "Crystal", "Crystal_SMD_2016-4Pin_2.0x1.6mm", 1.6, 9.2, 0),
        ("U5", "Package_TO_SOT_SMD", "SOT-23-5", 3.0, 20.2, 0),
        ("U2", "Package_TO_SOT_SMD", "SOT-23-5", 12.0, 20.2, 0),
        ("U4", "Package_TO_SOT_SMD", "SOT-23-6", 3.0, 24.2, 0),
        ("Q1", "Package_TO_SOT_SMD", "SOT-23-6", 7.5, 24.2, 0),
        ("Q2", "Package_TO_SOT_SMD", "SOT-23", 12.0, 24.2, 0),
        ("D1", "Diode_SMD", "D_SOD-323", 7.5, 21.2, 0),
        ("D2", "LED_SMD", "LED_LiteOn_LTST-C295K_1.6x0.8mm", 13.0, 28.5, 0),
        ("L1", "Inductor_SMD", "L_0402_1005Metric", 5.25, 6.8, 90),
        ("C13", "Capacitor_SMD", "C_0402_1005Metric", 3.8, 6.8, 180),
        ("C14", "Capacitor_SMD", "C_0402_1005Metric", 3.8, 5.2, 180),
        ("R_ANT", "Resistor_SMD", "R_0402_1005Metric", 5.25, 4.8, 90),
        ("R_TEST", "Resistor_SMD", "R_0402_1005Metric", 6.8, 5.2, 0),
        ("C4",  "Capacitor_SMD", "C_0402_1005Metric", 1.6, 6.0, 180),
        ("R1",  "Resistor_SMD",  "R_0402_1005Metric", 7.25, 7.5, 90),
        ("C11", "Capacitor_SMD", "C_0402_1005Metric", 8.5, 7.5, 90),
        ("C7",  "Capacitor_SMD", "C_0402_1005Metric", 1.8, 12.8, 180),
        ("C1",  "Capacitor_SMD", "C_0402_1005Metric", 1.8, 14.5, 180),
        ("C9",  "Capacitor_SMD", "C_0402_1005Metric", 1.8, 17.0, 180),
        ("C12", "Capacitor_SMD", "C_0402_1005Metric", 9.2, 18.4, 270),
        ("C17", "Capacitor_SMD", "C_0402_1005Metric", 12.2, 17.8, 0),
        ("C3",  "Capacitor_SMD", "C_0402_1005Metric", 13.2, 5.5, 0),
        ("C2",  "Capacitor_SMD", "C_0402_1005Metric", 13.2, 7.5, 0),
        ("C5",  "Capacitor_SMD", "C_0402_1005Metric", 13.2, 9.5, 0),
        ("C8",  "Capacitor_SMD", "C_0402_1005Metric", 13.2, 11.5, 0),
        ("C18", "Capacitor_SMD", "C_0402_1005Metric", 13.2, 13.5, 0),
        ("C10", "Capacitor_SMD", "C_0402_1005Metric", 13.2, 15.5, 0),
        ("C20", "Capacitor_SMD", "C_0402_1005Metric", 5.6, 18.4, 270),
        ("C21", "Capacitor_SMD", "C_0402_1005Metric", 6.8, 18.4, 270),
        ("C16", "Capacitor_SMD", "C_0402_1005Metric", 1.8, 28.5, 0),
        ("C15", "Capacitor_SMD", "C_0402_1005Metric", 3.9, 28.5, 0),
        ("R6",  "Resistor_SMD",  "R_0402_1005Metric", 10.5, 27.5, 0),
        ("R7",  "Resistor_SMD",  "R_0402_1005Metric", 10.5, 29.2, 0)
    ]

    placed_fps = {}
    for ref, pretty, name, x, y, rot in fp_placements:
        fp = load_fp(pretty, name)
        fp.SetReference(ref)
        fp.SetPosition(vec(x, y))
        fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        board.Add(fp)
        placed_fps[ref] = fp

    tp_defs = [
        ("TP_BOOT0",  7.25, 4.0,  "BOOT0"),
        ("TP_NRST",   9.80, 4.5,  "NRST"),
        ("TP_RF",     9.80, 7.2,  "TP_RF"),
        ("TP_VBUS",  13.50, 4.2,  "VBUS_5V"),
        ("TP_SWDIO",  2.20, 15.75, "SWDIO"),
        ("TP_SWCLK",  7.25, 21.0,  "SWCLK"),
        ("TP_3V3",   13.50, 17.8, "3V3"),
        ("TP_GND",   13.50, 25.5, "GND"),
        ("TP_BATT_N", 2.00, 26.8, "BATT_NEG"),
        ("TP_BATT_P", 4.80, 24.2, "BATT_POS")
    ]
    for tp_ref, x, y, tp_net in tp_defs:
        fp = load_fp("TestPoint", "TestPoint_Pad_D1.0mm")
        fp.SetReference(tp_ref)
        fp.SetPosition(vec(x, y))
        board.Add(fp)
        fp.Flip(fp.GetPosition(), True)
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        placed_fps[tp_ref] = fp

    # Map Nets
    pad_to_net = {}
    for nname, nodes in net_mappings.items():
        if not nname.startswith('unconnected-') and nname in nets:
            n_item = nets[nname]
            for ref, pin in nodes:
                pad_to_net[(ref, pin)] = n_item

    for ref, fp in placed_fps.items():
        for pad in fp.Pads():
            pnum = pad.GetNumber()
            if (ref, pnum) in pad_to_net:
                pad.SetNet(pad_to_net[(ref, pnum)])

    # Helper primitives
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

    def get_pad_pos(ref, pnum):
        fp = placed_fps[ref]
        pad = fp.FindPadByNumber(str(pnum))
        pos = pad.GetPosition()
        return (nm_to_mm(pos.x), nm_to_mm(pos.y))

    def add_pad_via(ref, pnum, vx, vy, layer=pcbnew.F_Cu, width=0.20):
        px, py = get_pad_pos(ref, pnum)
        pad = placed_fps[ref].FindPadByNumber(str(pnum))
        net = pad.GetNet()
        v = add_via(vx, vy, net)
        add_track(px, py, vx, vy, layer, net, width)
        return v

    # STEP 0: Bare footprints only
    eval_drc(board, "Step 0: Bare Footprints")

    # STEP 1: Add Copper Zones
    poly_box = [
        vec(0.20, 4.3), vec(14.80, 4.3),
        vec(14.80, 30.80), vec(0.20, 30.80)
    ]
    for layer_id, znet, conn in [
        (pcbnew.In1_Cu, gnd_net, pcbnew.ZONE_CONNECTION_FULL),
        (pcbnew.B_Cu,   gnd_net, pcbnew.ZONE_CONNECTION_THT_THERMAL),
        (pcbnew.F_Cu,   gnd_net, pcbnew.ZONE_CONNECTION_THT_THERMAL)
    ]:
        zone = pcbnew.ZONE(board)
        lset = pcbnew.LSET()
        lset.AddLayer(layer_id)
        zone.SetLayerSet(lset)
        zone.SetLayer(layer_id)
        zone.SetNet(znet)
        zone.SetMinThickness(mm_to_nm(0.15))
        zone.SetThermalReliefGap(mm_to_nm(0.20))
        zone.SetThermalReliefSpokeWidth(mm_to_nm(0.25))
        zone.SetPadConnection(conn)
        zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        chain = pcbnew.SHAPE_LINE_CHAIN()
        for p in poly_box:
            chain.Append(p.x, p.y)
        chain.SetClosed(True)
        zone.AddPolygon(chain)
        board.Add(zone)

    zone_3v3 = pcbnew.ZONE(board)
    lset_3v3 = pcbnew.LSET()
    lset_3v3.AddLayer(pcbnew.In2_Cu)
    zone_3v3.SetLayerSet(lset_3v3)
    zone_3v3.SetLayer(pcbnew.In2_Cu)
    zone_3v3.SetNet(p3v3_net)
    zone_3v3.SetMinThickness(mm_to_nm(0.15))
    zone_3v3.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    zone_3v3.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    chain_3v3 = pcbnew.SHAPE_LINE_CHAIN()
    for p in poly_box:
        chain_3v3.Append(p.x, p.y)
    chain_3v3.SetClosed(True)
    zone_3v3.AddPolygon(chain_3v3)
    board.Add(zone_3v3)

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    eval_drc(board, "Step 1: Zones Added & Filled")

    # STEP 2: Thermal Vias & GND Connections
    for dx in [-1.0, 0.0, 1.0]:
        for dy in [-1.0, 0.0, 1.0]:
            add_via(7.5 + dx, 13.0 + dy, gnd_net)

    # Pin 48 (GND) -> drop via south-east at (10.85, 17.0)
    add_pad_via("U1", "48", 10.85, 17.0, pcbnew.F_Cu, 0.15)

    gnd_vias = [
        ("C4",  "2", 0.7, 6.0),
        ("C14", "2", 2.5, 5.2),
        ("C13", "2", 2.5, 6.8),
        ("R1",  "2", 6.5, 6.99),
        ("C11", "2", 8.5, 6.2),
                ("Y1",  "4", 0.7, 8.65),
        ("C7",  "2", 1.32, 12.8),
        ("C1",  "2", 1.32, 14.5),
        ("C9",  "2", 1.32, 17.8),
        ("U5",  "2", 2.5, 20.2),
        ("C3",  "2", 14.3, 5.5),
        ("C2",  "2", 14.3, 7.5),
        ("C5",  "2", 14.3, 9.5),
        ("C8",  "2", 14.3, 11.5),
        ("C18", "2", 14.3, 13.5),
        ("C10", "2", 14.3, 15.5),
        ("C20", "2", 5.6, 19.8),
        ("C21", "2", 6.8, 19.8),
        ("C12", "2", 9.2, 19.8),
        ("U2",  "2", 10.863, 20.2),
        ("C17", "2", 12.68, 16.8),
        ("U4",  "2", 1.2, 24.2),
        ("Q1",  "1", 5.5, 23.25),
        ("MK1", "2", 5.0, 27.96),
        ("MK1", "3", 9.2, 28.5),
        ("C16", "2", 2.28, 29.5),
        ("C15", "2", 4.38, 29.5),
        ("D2",  "3", 14.3, 28.15),
        ("D2",  "4", 14.3, 28.85),
        ("TP_GND", "1", 13.5, 25.5)
    ]
    for ref, pnum, vx, vy in gnd_vias:
        add_pad_via(ref, pnum, vx, vy, pcbnew.F_Cu, 0.20)

    # Connect Y1.2 to Y1.4 on F.Cu (both GND)
    y1_2 = get_pad_pos("Y1", "2")
    y1_4 = get_pad_pos("Y1", "4")
    add_track(y1_2[0], y1_2[1], y1_4[0], y1_4[1], pcbnew.F_Cu, gnd_net, 0.15)
    filler.Fill(board.Zones())
    eval_drc(board, "Step 2: GND Vias & Thermal Reliefs")

    # STEP 3: 3V3 Power Plane Vias & Connections
    tp_3v3 = get_pad_pos("TP_3V3", "1")
    add_via(tp_3v3[0], tp_3v3[1], p3v3_net)

    # Right side 3V3 rail
    c3_1  = get_pad_pos("C3", "1")
    c2_1  = get_pad_pos("C2", "1")
    c5_1  = get_pad_pos("C5", "1")
    c8_1  = get_pad_pos("C8", "1")
    u1_11 = get_pad_pos("U1", "11")
    route_points([c3_1, c2_1, c5_1, (12.72, 10.75), u1_11], pcbnew.F_Cu, p3v3_net, 0.20)
    add_track(12.72, 10.75, c8_1[0], c8_1[1], pcbnew.F_Cu, p3v3_net, 0.20)
    add_via(12.72, 10.75, p3v3_net)

    # Left side 3V3 rail
    u1_25 = get_pad_pos("U1", "25")
    add_via(3.20, 10.25, p3v3_net)
    add_track(u1_25[0], u1_25[1], 3.20, 10.25, pcbnew.F_Cu, p3v3_net, 0.15)

    u1_28 = get_pad_pos("U1", "28")
    add_via(3.00, 11.75, p3v3_net)
    add_track(u1_28[0], u1_28[1], 3.00, 11.75, pcbnew.F_Cu, p3v3_net, 0.15)

    c1_1 = get_pad_pos("C1", "1")
    add_via(2.28, 13.8, p3v3_net)
    add_track(c1_1[0], c1_1[1], 2.28, 13.8, pcbnew.F_Cu, p3v3_net, 0.15)

    # Bottom MCU 3V3 Pins (44, 45, 46)
    u1_44 = get_pad_pos("U1", "44")
    u1_45 = get_pad_pos("U1", "45")
    u1_46 = get_pad_pos("U1", "46")
    add_via(8.5, 17.4, p3v3_net)
    route_points([u1_44, (8.25, 16.85), (9.25, 16.85), u1_46], pcbnew.F_Cu, p3v3_net, 0.15)
    add_track(u1_45[0], u1_45[1], 8.75, 16.85, pcbnew.F_Cu, p3v3_net, 0.15)
    add_track(8.5, 16.85, 8.5, 17.4, pcbnew.F_Cu, p3v3_net, 0.15)

    # Regulated 3V3 from U5 to MCU pins 37, 41 and C20, C21
    u5_5  = get_pad_pos("U5", "5")
    c20_1 = get_pad_pos("C20", "1")
    c21_1 = get_pad_pos("C21", "1")
    route_points([u5_5, (4.138, 17.92), c20_1, c21_1], pcbnew.F_Cu, p3v3_net, 0.20)
    add_via(4.75, 17.4, p3v3_net)
    u1_37 = get_pad_pos("U1", "37")
    add_track(u1_37[0], u1_37[1], 4.75, 17.4, pcbnew.F_Cu, p3v3_net, 0.15)
    add_track(4.75, 17.4, c20_1[0], c20_1[1], pcbnew.F_Cu, p3v3_net, 0.15)
    u1_41 = get_pad_pos("U1", "41")
    add_track(u1_41[0], u1_41[1], 6.75, 17.4, pcbnew.F_Cu, p3v3_net, 0.15)
    add_track(6.75, 17.4, c21_1[0], c21_1[1], pcbnew.F_Cu, p3v3_net, 0.15)

    # Audio 3V3
    mk1_5 = get_pad_pos("MK1", "5")
    c15_1 = get_pad_pos("C15", "1")
    c16_1 = get_pad_pos("C16", "1")
    route_points([c16_1, (1.32, 27.5), (3.42, 27.5), c15_1], pcbnew.F_Cu, p3v3_net, 0.20)
    add_via(3.42, 27.5, p3v3_net)
    add_via(9.2, 26.6, p3v3_net)
    add_track(mk1_5[0], mk1_5[1], 9.2, 26.6, pcbnew.F_Cu, p3v3_net, 0.20)

    filler.Fill(board.Zones())
    eval_drc(board, "Step 3: 3V3 Power Plane Vias & Connections")

    # STEP 4: RF Matching Network, Antenna, and VR_PA
    rfo_net = nets["RFO_HP"]
    u1_23 = get_pad_pos("U1", "23")
    l1_1  = get_pad_pos("L1", "1")
    c13_1 = get_pad_pos("C13", "1")
    add_track(u1_23[0], u1_23[1], l1_1[0], l1_1[1], pcbnew.F_Cu, rfo_net, 0.29)
    route_points([l1_1, (4.285, 7.285), c13_1], pcbnew.F_Cu, rfo_net, 0.20)

    rf_net = nets["RF_50OHM"]
    l1_2   = get_pad_pos("L1", "2")
    r_ant1 = get_pad_pos("R_ANT", "1")
    c14_1  = get_pad_pos("C14", "1")
    r_tst1 = get_pad_pos("R_TEST", "1")
    add_track(l1_2[0], l1_2[1], r_ant1[0], r_ant1[1], pcbnew.F_Cu, rf_net, 0.29)
    add_track(5.25, 5.2, c14_1[0], c14_1[1], pcbnew.F_Cu, rf_net, 0.20)
    add_track(5.25, 5.2, r_tst1[0], r_tst1[1], pcbnew.F_Cu, rf_net, 0.20)

    ant_net = nets["ANT_FEED"]
    r_ant2 = get_pad_pos("R_ANT", "2")
    ant_1  = get_pad_pos("ANT1", "1")
    route_points([r_ant2, (5.25, 3.5), (4.65, 2.9), ant_1], pcbnew.F_Cu, ant_net, 0.29)

    # TP_RF on B.Cu (route along Y=7.2 clear of TP_NRST)
    tprf_net = nets["TP_RF"]
    r_tst2 = get_pad_pos("R_TEST", "2")
    tp_rf  = get_pad_pos("TP_RF", "1")
    add_via(7.31, 5.2, tprf_net)
    route_points([(7.31, 5.2), (7.31, 7.2), tp_rf], pcbnew.B_Cu, tprf_net, 0.20)

    # VR_PA: U1.24 -> north to (4.5, 8.2) -> via to B.Cu -> (3.5, 8.2) -> (3.5, 6.0) -> (2.8, 6.0) -> via to F.Cu -> C4.1
    vrpa_net = nets["VR_PA"]
    u1_24 = get_pad_pos("U1", "24")
    c4_1  = get_pad_pos("C4", "1")
    add_via(4.5, 8.2, vrpa_net)
    route_points([u1_24, (4.5, 9.75), (4.5, 8.2)], pcbnew.F_Cu, vrpa_net, 0.20)
    add_via(2.8, 6.0, vrpa_net)
    add_track(2.8, 6.0, c4_1[0], c4_1[1], pcbnew.F_Cu, vrpa_net, 0.20)
    route_points([(4.5, 8.2), (3.5, 8.2), (3.5, 6.0), (2.8, 6.0)], pcbnew.B_Cu, vrpa_net, 0.20)

    filler.Fill(board.Zones())
    eval_drc(board, "Step 4: RF Front End & Matching & VR_PA")

    # STEP 5: Digital Control & System Signals (SWD, OSC, BOOT0, NRST, Decoupling)
    # 1. SWDIO
    n_swdio = nets["SWDIO"]
    add_track(4.06, 15.75, 2.20, 15.75, pcbnew.F_Cu, n_swdio, 0.15)
    add_via(2.20, 15.75, n_swdio)

    # 2. SWCLK
    n_swclk = nets["SWCLK"]
    route_points([(7.25, 16.44), (7.25, 17.30), (7.80, 17.30), (7.80, 21.00), (7.25, 21.00)], pcbnew.F_Cu, n_swclk, 0.15)
    add_via(7.25, 21.00, n_swclk)

    # 3. BOOT0
    n_boot0 = nets["BOOT0"]
    add_track(7.25, 9.56, 7.25, 8.01, pcbnew.F_Cu, n_boot0, 0.15)
    add_via(7.25, 8.01, n_boot0)
    route_points([(7.25, 8.01), (5.60, 8.01), (5.60, 4.00), (7.25, 4.00)], pcbnew.B_Cu, n_boot0, 0.15)

    # 4. NRST: direct clean path
    n_nrst = nets["NRST"]
    route_points([(7.750, 9.560), (7.750, 8.600), (7.850, 8.500), (7.850, 7.980), (9.200, 7.980), (9.200, 4.500), (9.800, 4.500)], pcbnew.F_Cu, n_nrst, 0.15)
    add_via(9.80, 4.50, n_nrst)

    # 5. VDDRF1V55
    n_vddrf = nets["VDDRF1V55"]
    route_points([(4.06, 12.25), (2.70, 12.25), (2.70, 12.80), (2.28, 12.80)], pcbnew.F_Cu, n_vddrf, 0.15)

    # 6. VLXSMPS
    n_vlx = nets["VLXSMPS"]
    route_points([(9.75, 16.44), (9.75, 17.40), (9.20, 17.40), (9.20, 17.92)], pcbnew.F_Cu, n_vlx, 0.15)

    # 7. OSC_IN: 100% on F.Cu around west edge of Y1
    n_oscin = nets["OSC_IN"]
    route_points([(4.06, 10.75), (0.50, 10.75), (0.50, 9.75), (0.90, 9.75)], pcbnew.F_Cu, n_oscin, 0.15)

    # 8. OSC_OUT: U1.27(4.06, 11.25) -> via at (2.20, 11.25) -> B.Cu to (2.70, 8.65) -> via to Y1.3(2.30, 8.65)
    n_oscout = nets["OSC_OUT"]
    add_track(4.06, 11.25, 2.20, 11.25, pcbnew.F_Cu, n_oscout, 0.15)
    add_via(2.20, 11.25, n_oscout)
    add_via(2.70, 8.65, n_oscout)
    route_points([(2.20, 11.25), (2.20, 8.65), (2.70, 8.65)], pcbnew.B_Cu, n_oscout, 0.15)
    add_track(2.70, 8.65, 2.30, 8.65, pcbnew.F_Cu, n_oscout, 0.15)

    filler.Fill(board.Zones())
    eval_drc(board, "Step 5: Digital Control & System Signals")

    # ==================== STEP 6: Power Management & Battery Protection ====================
    # 1. Q1 internal drain connection on F.Cu
    add_track(6.362, 24.20, 6.362, 25.15, pcbnew.F_Cu, nets['Net-(Q1-D12-Pad2)'], 0.20)

    # 2. BATT_POS on F.Cu to TP_BATT_P (4.80, 24.20)
    add_via(4.80, 24.20, nets['BATT_POS'])
    add_track(4.138, 24.20, 4.80, 24.20, pcbnew.F_Cu, nets['BATT_POS'], 0.20)

    # 3. GATE_OD: U4.1 to Q1.6 on F.Cu (100% on F.Cu)
    route_points([(1.863, 23.25), (1.863, 22.40), (8.637, 22.40), (8.637, 23.25)], pcbnew.F_Cu, nets['GATE_OD'], 0.15)

    # 4. GATE_OC: U4.3 to Q1.5 on F.Cu (100% on F.Cu)
    route_points([(1.863, 25.15), (1.863, 25.80), (7.500, 25.80), (7.500, 24.20), (8.637, 24.20)], pcbnew.F_Cu, nets['GATE_OC'], 0.15)

    # 5. SYS_PWR: U5.1, U5.3, C9.1, D1.1, Q2.2 (100% on F.Cu)
    route_points([(2.28, 17.00), (2.28, 18.20), (1.863, 18.20), (1.863, 19.25)], pcbnew.F_Cu, nets['SYS_PWR'], 0.20)
    route_points([(1.863, 19.25), (0.70, 19.25), (0.70, 21.15), (1.863, 21.15)], pcbnew.F_Cu, nets['SYS_PWR'], 0.20)
    route_points([(1.863, 21.15), (1.863, 21.80), (6.45, 21.80), (6.45, 21.20)], pcbnew.F_Cu, nets['SYS_PWR'], 0.20)
    route_points([(6.45, 21.80), (9.80, 21.80), (9.80, 25.15), (11.062, 25.15)], pcbnew.F_Cu, nets['SYS_PWR'], 0.15)

    # 6. VBAT_PROT: C17.1, U2.3, Q2.3 (100% on F.Cu)
    route_points([(11.720, 17.80), (12.00, 17.80), (12.00, 22.00)], pcbnew.F_Cu, nets['VBAT_PROT'], 0.20)
    route_points([(12.00, 22.00), (10.863, 22.00), (10.863, 21.15)], pcbnew.F_Cu, nets['VBAT_PROT'], 0.20)
    route_points([(12.00, 22.00), (12.938, 22.00), (12.938, 24.20)], pcbnew.F_Cu, nets['VBAT_PROT'], 0.20)

    # 7. BATT_NEG: U4.6 (4.138, 23.25), TP_BATT_N (2.00, 26.80), Q1.4 (8.637, 25.15)
    add_via(4.138, 23.25, nets['BATT_NEG'])
    add_via(2.00, 26.80, nets['BATT_NEG'])
    add_via(8.637, 25.15, nets['BATT_NEG'])
    add_track(4.138, 23.25, 2.00, 26.80, pcbnew.In2_Cu, nets['BATT_NEG'], 0.20)
    route_points([(4.138, 23.25), (4.138, 24.80), (6.50, 24.80), (8.637, 25.15)], pcbnew.In2_Cu, nets['BATT_NEG'], 0.20)

    # 8. CHG_STAT: U1.7 (10.938, 12.75) to U2.1 (10.863, 19.25)
    add_via(11.80, 12.75, nets['CHG_STAT'])
    add_track(10.938, 12.75, 11.80, 12.75, pcbnew.F_Cu, nets['CHG_STAT'], 0.15)
    add_via(11.40, 19.25, nets['CHG_STAT'])
    add_track(11.40, 19.25, 10.863, 19.25, pcbnew.F_Cu, nets['CHG_STAT'], 0.15)
    route_points([(11.80, 12.75), (11.40, 13.50), (11.40, 19.25)], pcbnew.B_Cu, nets['CHG_STAT'], 0.15)

    # 9. VBUS_5V: TP_VBUS, C18, C10, U2.4, Q2.1, D1.2
    add_via(13.50, 12.50, nets['VBUS_5V'])
    add_track(13.50, 4.20, 13.50, 12.50, pcbnew.B_Cu, nets['VBUS_5V'], 0.25)
    route_points([(13.50, 12.50), (12.72, 12.50), (12.72, 13.50), (12.72, 15.50)], pcbnew.F_Cu, nets['VBUS_5V'], 0.25)
    route_points([(12.72, 15.50), (12.72, 16.20), (14.20, 16.20), (14.20, 21.15), (13.137, 21.15)], pcbnew.F_Cu, nets['VBUS_5V'], 0.25)
    add_via(14.20, 21.15, nets['VBUS_5V'])
    add_via(11.062, 23.25, nets['VBUS_5V'])
    add_via(8.55, 20.50, nets['VBUS_5V'])
    add_track(8.55, 20.50, 8.55, 21.20, pcbnew.F_Cu, nets['VBUS_5V'], 0.25)
    add_track(14.20, 21.15, 11.062, 23.25, pcbnew.In2_Cu, nets['VBUS_5V'], 0.25)
    add_track(8.55, 20.50, 11.062, 23.25, pcbnew.In2_Cu, nets['VBUS_5V'], 0.25)

    filler.Fill(board.Zones())
    eval_drc(board, "Step 6: Power Management & Battery Protection")

    # ==================== STEP 7: Audio & UI LEDs ====================
    # 10. LED_R: R6.2 (11.01, 27.50) to D2.1 (12.40, 28.15) on F.Cu
    route_points([(11.01, 27.50), (11.80, 27.50), (11.80, 28.15), (12.40, 28.15)], pcbnew.F_Cu, nets['LED_R'], 0.15)

    # 11. LED_B: R7.2 (11.01, 29.20) to D2.2 (12.40, 28.85) on F.Cu
    route_points([(11.01, 29.20), (11.80, 29.20), (11.80, 28.85), (12.40, 28.85)], pcbnew.F_Cu, nets['LED_B'], 0.15)

    # 12. LED_R_DRV: U1.12 (10.938, 10.25) to R6.1 (9.99, 27.00)
    add_track(10.938, 10.25, 11.60, 10.15, pcbnew.F_Cu, nets['LED_R_DRV'], 0.15)
    add_via(11.60, 10.15, nets['LED_R_DRV'])
    add_via(9.99, 27.00, nets['LED_R_DRV'])
    add_track(9.99, 27.00, 9.99, 27.50, pcbnew.F_Cu, nets['LED_R_DRV'], 0.15)
    route_points([(11.60, 10.15), (10.00, 11.00), (10.00, 27.00), (9.99, 27.00)], pcbnew.B_Cu, nets['LED_R_DRV'], 0.15)

    # 13. LED_B_DRV: U1.13 (10.250, 9.562) to R7.1 (9.99, 29.20)
    add_track(10.25, 9.562, 10.25, 8.80, pcbnew.F_Cu, nets['LED_B_DRV'], 0.15)
    add_track(10.25, 8.80, 11.80, 8.80, pcbnew.F_Cu, nets['LED_B_DRV'], 0.15)
    add_via(11.80, 8.80, nets['LED_B_DRV'])
    add_via(9.99, 28.50, nets['LED_B_DRV'])
    add_track(9.99, 28.50, 9.99, 29.20, pcbnew.F_Cu, nets['LED_B_DRV'], 0.15)
    route_points([(11.80, 8.80), (12.10, 9.80), (12.10, 11.50), (12.35, 12.20), (12.35, 13.50), (12.10, 14.50), (12.10, 28.50), (9.99, 28.50)], pcbnew.B_Cu, nets['LED_B_DRV'], 0.15)

    # 14. MIC_WS: U1.32 (4.0625, 13.750) -> MK1.1 (6.600, 27.136)
    add_track(4.0625, 13.750, 3.100, 13.750, pcbnew.F_Cu, nets['MIC_WS'], 0.15)
    add_track(3.100, 13.750, 3.100, 13.300, pcbnew.F_Cu, nets['MIC_WS'], 0.15)
    add_via(3.100, 13.300, nets['MIC_WS'])
    route_points([(3.100, 13.300), (0.600, 13.300), (0.600, 25.900), (6.600, 25.900), (6.600, 26.400)], pcbnew.B_Cu, nets['MIC_WS'], 0.15)
    add_via(6.600, 26.400, nets['MIC_WS'])
    add_track(6.600, 26.400, 6.600, 27.136, pcbnew.F_Cu, nets['MIC_WS'], 0.15)

    # 15. MIC_SD: U1.33 (4.0625, 14.250) -> MK1.6 (7.500, 27.136)
    add_track(4.0625, 14.250, 3.200, 14.250, pcbnew.F_Cu, nets['MIC_SD'], 0.15)
    add_via(3.200, 14.250, nets['MIC_SD'])
    route_points([(3.200, 14.250), (3.200, 25.300), (7.500, 25.300), (7.500, 26.400)], pcbnew.B_Cu, nets['MIC_SD'], 0.15)
    add_via(7.500, 26.400, nets['MIC_SD'])
    add_track(7.500, 26.400, 7.500, 27.136, pcbnew.F_Cu, nets['MIC_SD'], 0.15)

    # 16. MIC_SCK: U1.17 (8.250, 9.5625) -> MK1.4 (8.400, 27.958)
    add_track(8.250, 9.5625, 8.400, 8.700, pcbnew.F_Cu, nets['MIC_SCK'], 0.15)
    add_via(8.400, 8.700, nets['MIC_SCK'])
    route_points([(8.400, 8.700), (5.400, 8.700), (5.400, 15.500), (6.200, 16.500), (6.200, 24.600), (8.050, 24.600), (8.050, 27.958)], pcbnew.B_Cu, nets['MIC_SCK'], 0.15)
    add_via(8.050, 27.958, nets['MIC_SCK'])
    add_track(8.050, 27.958, 8.400, 27.958, pcbnew.F_Cu, nets['MIC_SCK'], 0.15)

    filler.Fill(board.Zones())
    board.Save("hardware/Device1.kicad_pcb")
    eval_drc(board, "Step 7: Audio & UI LEDs (Complete Board)")

if __name__ == "__main__":
    run_stepwise()

