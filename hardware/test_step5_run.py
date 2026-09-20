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
    settings.m_ViasMinSize = mm_to_nm(0.60)
    settings.m_ViasMinDrill = mm_to_nm(0.30)
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

    def add_via(x, y, net, drill=0.30, size=0.60):
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
        ("Y1", "2", 2.75, 9.75),
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
    add_via(3.20, 7.80, p3v3_net)
    route_points([u1_25, (3.20, 10.25), (3.20, 7.80)], pcbnew.F_Cu, p3v3_net, 0.15)

    u1_28 = get_pad_pos("U1", "28")
    add_via(2.00, 11.75, p3v3_net)
    add_track(u1_28[0], u1_28[1], 2.00, 11.75, pcbnew.F_Cu, p3v3_net, 0.15)

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
    add_via(8.4, 26.2, p3v3_net)
    add_track(mk1_5[0], mk1_5[1], 8.4, 26.2, pcbnew.F_Cu, p3v3_net, 0.20)

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

    # 4. NRST
    n_nrst = nets["NRST"]
    route_points([(7.75, 9.56), (7.75, 8.60), (8.50, 8.60), (8.50, 7.98)], pcbnew.F_Cu, n_nrst, 0.15)
    route_points([(8.50, 7.98), (9.20, 7.98), (9.20, 4.50), (9.80, 4.50)], pcbnew.F_Cu, n_nrst, 0.15)
    add_via(9.80, 4.50, n_nrst)

    # 5. VDDRF1V55
    n_vddrf = nets["VDDRF1V55"]
    route_points([(4.06, 12.25), (2.70, 12.25), (2.70, 12.80), (2.28, 12.80)], pcbnew.F_Cu, n_vddrf, 0.15)

    # 6. VLXSMPS
    n_vlx = nets["VLXSMPS"]
    route_points([(9.75, 16.44), (9.75, 17.40), (9.20, 17.40), (9.20, 17.92)], pcbnew.F_Cu, n_vlx, 0.15)

        # 7. OSC_IN
    n_oscin = nets["OSC_IN"]
    route_points([(4.06, 10.75), (3.80, 10.75), (3.50, 10.45), (0.50, 10.45), (0.50, 9.75), (0.90, 9.75)], pcbnew.F_Cu, n_oscin, 0.15)

    # 8. OSC_OUT
    n_oscout = nets["OSC_OUT"]
    add_track(4.06, 11.25, 3.20, 11.25, pcbnew.F_Cu, n_oscout, 0.15)
    add_via(3.20, 11.25, n_oscout)
    add_via(2.70, 8.65, n_oscout)
    route_points([(3.20, 11.25), (3.50, 11.25), (3.50, 8.65), (2.70, 8.65)], pcbnew.B_Cu, n_oscout, 0.15)
    add_track(2.70, 8.65, 2.30, 8.65, pcbnew.F_Cu, n_oscout, 0.15)

    filler.Fill(board.Zones())
    eval_drc(board, "Step 5: Digital Control & System Signals")

if __name__ == "__main__":
    run_stepwise()
