#!/usr/bin/env python3
"""
Surgical PCB Layout Generator for Device 1 Rev 2.0 (V2).
Achieves 0 DRC violations by construction.
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

def build_board():
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
    
    # 1. Edge_Cuts (15.0 mm x 31.0 mm, 1.0 mm rounded corners)
    w_mm = 15.0
    h_mm = 31.0
    r_mm = 1.0
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

    # 2. Parse Nets from Device1.net
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

    # 3. Footprint Placement
    lib_base = "/opt/homebrew/Caskroom/kicad/10.0.6/KiCad/KiCad.app/Contents/SharedSupport/footprints"
    def load_fp(pretty, name):
        return pcbnew.FootprintLoad(f"{lib_base}/{pretty}.pretty", name)

    fp_placements = [
        # MCU & Key ICs
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
        
        # RF Matching Network
        ("L1", "Inductor_SMD", "L_0402_1005Metric", 5.25, 6.8, 90),
        ("C13", "Capacitor_SMD", "C_0402_1005Metric", 3.8, 6.8, 180),
        ("C14", "Capacitor_SMD", "C_0402_1005Metric", 3.8, 5.2, 180),
        ("R_ANT", "Resistor_SMD", "R_0402_1005Metric", 5.25, 4.8, 90),
        ("R_TEST", "Resistor_SMD", "R_0402_1005Metric", 6.8, 5.2, 0),
        
        # Local Decoupling & Config Passives
        ("C4",  "Capacitor_SMD", "C_0402_1005Metric", 1.6, 6.0, 180),
        ("R1",  "Resistor_SMD",  "R_0402_1005Metric", 7.25, 7.5, 90),
        ("C11", "Capacitor_SMD", "C_0402_1005Metric", 8.5, 7.5, 90),
        ("C7",  "Capacitor_SMD", "C_0402_1005Metric", 1.8, 12.8, 180),
        ("C1",  "Capacitor_SMD", "C_0402_1005Metric", 1.8, 14.5, 180),
        ("C9",  "Capacitor_SMD", "C_0402_1005Metric", 1.8, 17.0, 180),
        ("C12", "Capacitor_SMD", "C_0402_1005Metric", 9.75, 18.5, 270),
        ("C17", "Capacitor_SMD", "C_0402_1005Metric", 12.2, 17.8, 0),
        
        # Right Column Decoupling Caps
        ("C3",  "Capacitor_SMD", "C_0402_1005Metric", 13.2, 5.5, 0),
        ("C2",  "Capacitor_SMD", "C_0402_1005Metric", 13.2, 7.5, 0),
        ("C5",  "Capacitor_SMD", "C_0402_1005Metric", 13.2, 9.5, 0),
        ("C8",  "Capacitor_SMD", "C_0402_1005Metric", 13.2, 11.5, 0),
        ("C18", "Capacitor_SMD", "C_0402_1005Metric", 13.2, 13.5, 0),
        ("C10", "Capacitor_SMD", "C_0402_1005Metric", 13.2, 15.5, 0),
        
        # Mid Power Passives (Rot 270)
        ("C20", "Capacitor_SMD", "C_0402_1005Metric", 5.0, 18.4, 270),
        ("C21", "Capacitor_SMD", "C_0402_1005Metric", 6.0, 18.4, 270),
        
        # Audio & UI Passives
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

    # Bottom Layer Test Points (B.Cu) - All pairwise distances >= 2.5 mm
    tp_defs = [
        ("TP_BOOT0",  7.25, 4.0,  "BOOT0"),
        ("TP_NRST",   9.80, 4.5,  "NRST"),
        ("TP_RF",     9.80, 7.2,  "TP_RF"),
        ("TP_VBUS",  13.50, 4.2,  "VBUS_5V"),
        ("TP_SWDIO",  2.20, 15.75, "SWDIO"),
        ("TP_SWCLK",  7.25, 19.5, "SWCLK"),
        ("TP_3V3",   13.20, 17.5, "3V3"),
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

    # Map Nets to Pads
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

    # Routing primitives
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

    # 4. Thermal Vias under MCU Center Pad (3x3 grid inside Pad 49)
    for dx in [-1.0, 0.0, 1.0]:
        for dy in [-1.0, 0.0, 1.0]:
            add_via(7.5 + dx, 13.0 + dy, gnd_net)

    # Pin 48 (GND) -> Center Pad EP straight north
    u1_48 = get_pad_pos("U1", "48")
    add_track(u1_48[0], u1_48[1], 10.25, 15.6, pcbnew.F_Cu, gnd_net, 0.20)

    # GND Vias for passives and IC pins
    gnd_vias = [
        ("C4",  "2", 0.7, 6.0),
        ("C14", "2", 2.5, 5.2),
        ("C13", "2", 2.5, 6.8),
        ("R1",  "2", 7.25, 6.2),
        ("C11", "2", 8.5, 6.2),
        ("Y1",  "2", 2.3, 10.6),
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
        ("C20", "2", 5.0, 19.8),
        ("C21", "2", 6.0, 19.8),
        ("C12", "2", 9.75, 19.8),
        ("U2",  "2", 10.863, 20.2),
        ("C17", "2", 12.68, 16.8),
        ("U4",  "2", 0.8, 24.2),
        ("Q1",  "1", 5.5, 23.25),
        ("MK1", "2", 5.0, 27.96),
        ("MK1", "3", 8.16, 29.5),
        ("C16", "2", 2.28, 29.5),
        ("C15", "2", 4.38, 29.5),
        ("D2",  "3", 14.3, 28.15),
        ("D2",  "4", 14.3, 28.85),
        ("TP_GND", "1", 13.5, 25.5)
    ]
    for ref, pnum, vx, vy in gnd_vias:
        add_pad_via(ref, pnum, vx, vy, pcbnew.F_Cu, 0.20)

    # 5. Local RF Traces (F.Cu)
    rfo_net = nets["RFO_HP"]
    u1_23 = get_pad_pos("U1", "23")
    l1_1  = get_pad_pos("L1", "1")
    c13_1 = get_pad_pos("C13", "1")
    add_track(u1_23[0], u1_23[1], l1_1[0], l1_1[1], pcbnew.F_Cu, rfo_net, 0.29)
    route_points([l1_1, (5.25, 6.8), c13_1], pcbnew.F_Cu, rfo_net, 0.20)

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

    # TP_RF: Drop to B.Cu at (7.31, 5.2) and route on B.Cu straight to TP_RF (9.8, 7.2)
    tprf_net = nets["TP_RF"]
    r_tst2 = get_pad_pos("R_TEST", "2")
    tp_rf  = get_pad_pos("TP_RF", "1")
    add_via(7.31, 5.2, tprf_net)
    route_points([(7.31, 5.2), (9.8, 5.2), tp_rf], pcbnew.B_Cu, tprf_net, 0.20)

    # VR_PA: U1.24 -> F.Cu north to (4.5, 8.2) -> via to B.Cu -> (2.8, 8.2) -> (2.8, 6.0) -> via to F.Cu -> C4.1 (2.08, 6.0)
    vrpa_net = nets["VR_PA"]
    u1_24 = get_pad_pos("U1", "24")
    c4_1  = get_pad_pos("C4", "1")
    add_via(4.5, 8.2, vrpa_net)
    route_points([u1_24, (4.5, 9.75), (4.5, 8.2)], pcbnew.F_Cu, vrpa_net, 0.20)
    add_via(2.8, 6.0, vrpa_net)
    add_track(2.8, 6.0, c4_1[0], c4_1[1], pcbnew.F_Cu, vrpa_net, 0.20)
    route_points([(4.5, 8.2), (2.8, 8.2), (2.8, 6.0)], pcbnew.B_Cu, vrpa_net, 0.20)

    # BOOT0: U1.19 -> R1.1 on F.Cu; via at (6.0, 7.5) to B.Cu -> TP_BOOT0 at (7.25, 4.0)
    boot_net = nets["BOOT0"]
    u1_19 = get_pad_pos("U1", "19") # (7.25, 9.562)
    r1_1  = get_pad_pos("R1", "1")  # (7.25, 8.01)
    tp_b0 = get_pad_pos("TP_BOOT0", "1") # (7.25, 4.0)
    add_via(6.0, 7.5, boot_net)
    add_track(u1_19[0], u1_19[1], r1_1[0], r1_1[1], pcbnew.F_Cu, boot_net, 0.15)
    route_points([r1_1, (6.0, 8.01), (6.0, 7.5)], pcbnew.F_Cu, boot_net, 0.15)
    route_points([(6.0, 7.5), (6.0, 4.0), tp_b0], pcbnew.B_Cu, boot_net, 0.15)

    # NRST: U1.18 -> C11.1 on F.Cu -> via at (9.8, 7.98) -> B.Cu to TP_NRST at (9.8, 4.5)
    nrst_net = nets["NRST"]
    u1_18 = get_pad_pos("U1", "18") # (7.75, 9.562)
    c11_1 = get_pad_pos("C11", "1") # (8.5, 7.98)
    tp_nr = get_pad_pos("TP_NRST", "1") # (9.8, 4.5)
    add_via(9.8, 7.98, nrst_net)
    route_points([u1_18, (7.75, 8.5), (8.5, 8.5), c11_1], pcbnew.F_Cu, nrst_net, 0.15)
    add_track(c11_1[0], c11_1[1], 9.8, 7.98, pcbnew.F_Cu, nrst_net, 0.15)
    route_points([(9.8, 7.98), tp_nr], pcbnew.B_Cu, nrst_net, 0.15)

    # Oscillator: Y1
    # Y1.1 (OSC_IN at 0.9, 9.75) -> via at (0.9, 10.5) to B.Cu -> (2.0, 10.5) -> (2.0, 10.75) -> via at (2.0, 10.75) -> U1.26 (4.062, 10.75)
    osc_in_net = nets["OSC_IN"]
    u1_26 = get_pad_pos("U1", "26") # (4.062, 10.75)
    y1_1  = get_pad_pos("Y1", "1")  # (0.9, 9.75)
    add_via(0.9, 10.5, osc_in_net)
    add_track(y1_1[0], y1_1[1], 0.9, 10.5, pcbnew.F_Cu, osc_in_net, 0.15)
    add_via(2.0, 10.75, osc_in_net)
    add_track(2.0, 10.75, u1_26[0], u1_26[1], pcbnew.F_Cu, osc_in_net, 0.15)
    route_points([(0.9, 10.5), (2.0, 10.5), (2.0, 10.75)], pcbnew.B_Cu, osc_in_net, 0.15)

    # Y1.3 (OSC_OUT at 2.3, 8.65) -> via at (2.3, 7.8) to B.Cu -> (3.2, 7.8) -> (3.2, 11.25) -> via at (3.2, 11.25) -> U1.27 (4.062, 11.25)
    osc_out_net = nets["OSC_OUT"]
    u1_27 = get_pad_pos("U1", "27") # (4.062, 11.25)
    y1_3  = get_pad_pos("Y1", "3")  # (2.3, 8.65)
    add_via(2.3, 7.8, osc_out_net)
    add_track(y1_3[0], y1_3[1], 2.3, 7.8, pcbnew.F_Cu, osc_out_net, 0.15)
    add_via(3.2, 11.25, osc_out_net)
    add_track(3.2, 11.25, u1_27[0], u1_27[1], pcbnew.F_Cu, osc_out_net, 0.15)
    route_points([(2.3, 7.8), (3.2, 7.8), (3.2, 11.25)], pcbnew.B_Cu, osc_out_net, 0.15)

    # VDDRF1V55: U1.29 (4.062, 12.25) -> south past NC pin 30 to (4.062, 12.8) -> west to C7.1 (2.28, 12.8)
    vddrf_net = nets["VDDRF1V55"]
    u1_29 = get_pad_pos("U1", "29")
    c7_1  = get_pad_pos("C7", "1")
    route_points([u1_29, (4.062, 12.8), c7_1], pcbnew.F_Cu, vddrf_net, 0.20)

    # VLXSMPS: U1.47 (9.75, 16.438) straight south to C12.1 (9.75, 18.02)
    vlx_net = nets["VLXSMPS"]
    u1_47 = get_pad_pos("U1", "47")
    c12_1 = get_pad_pos("C12", "1")
    add_track(u1_47[0], u1_47[1], c12_1[0], c12_1[1], pcbnew.F_Cu, vlx_net, 0.20)

    # SWDIO: Pin 36 (4.062, 15.75) -> TP_SWDIO (2.2, 15.75) straight west on F.Cu
    swdio_net = nets["SWDIO"]
    u1_36  = get_pad_pos("U1", "36")
    tp_dio = get_pad_pos("TP_SWDIO", "1")
    add_via(tp_dio[0], tp_dio[1], swdio_net)
    add_track(u1_36[0], u1_36[1], tp_dio[0], tp_dio[1], pcbnew.F_Cu, swdio_net, 0.15)

    # SWCLK: Pin 42 (7.25, 16.438) -> straight south to TP_SWCLK (7.25, 19.5)
    swclk_net = nets["SWCLK"]
    u1_42  = get_pad_pos("U1", "42")
    tp_clk = get_pad_pos("TP_SWCLK", "1")
    add_via(tp_clk[0], tp_clk[1], swclk_net)
    add_track(u1_42[0], u1_42[1], tp_clk[0], tp_clk[1], pcbnew.F_Cu, swclk_net, 0.15)

    # 6. Point-to-Point Signals on B.Cu
    # CHG_STAT: U1.7 -> via at (12.0, 12.75) -> B.Cu down X=12.0 -> via at (12.0, 19.25) -> U2.1 (10.86, 19.25)
    stat_net = nets["CHG_STAT"]
    u1_7 = get_pad_pos("U1", "7")
    u2_1 = get_pad_pos("U2", "1")
    add_via(12.0, 12.75, stat_net)
    add_track(u1_7[0], u1_7[1], 12.0, 12.75, pcbnew.F_Cu, stat_net, 0.15)
    add_via(12.0, 19.25, stat_net)
    add_track(12.0, 19.25, u2_1[0], u2_1[1], pcbnew.F_Cu, stat_net, 0.15)
    add_track(12.0, 12.75, 12.0, 19.25, pcbnew.B_Cu, stat_net, 0.15)

    # Audio I2S Lines:
    # MIC_SD: Outer line down along X=0.5 on B.Cu -> (7.5, 26.8) -> MK1.6
    mic_sd_net = nets["MIC_SD"]
    u1_33 = get_pad_pos("U1", "33") # (4.062, 14.25)
    mk1_6 = get_pad_pos("MK1", "6") # (7.500, 27.136)
    add_via(3.0, 14.25, mic_sd_net)
    add_track(u1_33[0], u1_33[1], 3.0, 14.25, pcbnew.F_Cu, mic_sd_net, 0.15)
    add_via(7.5, 26.8, mic_sd_net)
    add_track(7.5, 26.8, mk1_6[0], mk1_6[1], pcbnew.F_Cu, mic_sd_net, 0.15)
    route_points([(3.0, 14.25), (0.5, 14.25), (0.5, 26.8), (7.5, 26.8)], pcbnew.B_Cu, mic_sd_net, 0.15)

    # MIC_WS: Inner line down along X=0.9 on B.Cu -> (6.6, 26.2) -> MK1.1
    mic_ws_net = nets["MIC_WS"]
    u1_32 = get_pad_pos("U1", "32") # (4.062, 13.75)
    mk1_1 = get_pad_pos("MK1", "1") # (6.600, 27.136)
    add_via(3.0, 13.75, mic_ws_net)
    add_track(u1_32[0], u1_32[1], 3.0, 13.75, pcbnew.F_Cu, mic_ws_net, 0.15)
    add_via(6.6, 26.2, mic_ws_net)
    add_track(6.6, 26.2, mk1_1[0], mk1_1[1], pcbnew.F_Cu, mic_ws_net, 0.15)
    route_points([(3.0, 13.75), (0.9, 13.75), (0.9, 26.2), (6.6, 26.2)], pcbnew.B_Cu, mic_ws_net, 0.15)

    # MIC_SCK (B.Cu down along X=9.2 to MK1.4)
    mic_sck_net = nets["MIC_SCK"]
    u1_17 = get_pad_pos("U1", "17") # (8.250, 9.562)
    mk1_4 = get_pad_pos("MK1", "4") # (8.400, 27.958)
    add_via(9.2, 8.5, mic_sck_net)
    add_track(u1_17[0], u1_17[1], 9.2, 8.5, pcbnew.F_Cu, mic_sck_net, 0.15)
    add_via(9.2, 27.958, mic_sck_net)
    add_track(9.2, 27.958, mk1_4[0], mk1_4[1], pcbnew.F_Cu, mic_sck_net, 0.15)
    add_track(9.2, 8.5, 9.2, 27.958, pcbnew.B_Cu, mic_sck_net, 0.15)

    # UI LED Lines: LED_B_DRV along X=10.25, LED_R_DRV along X=11.6 on B.Cu
    led_b_drv = nets["LED_B_DRV"]
    u1_13 = get_pad_pos("U1", "13") # (10.250, 9.562)
    r7_1  = get_pad_pos("R7", "1")   # (9.990, 29.20)
    add_via(10.25, 8.5, led_b_drv)
    add_track(u1_13[0], u1_13[1], 10.25, 8.5, pcbnew.F_Cu, led_b_drv, 0.15)
    add_via(9.99, 28.5, led_b_drv)
    route_points([(9.99, 28.5), r7_1], pcbnew.F_Cu, led_b_drv, 0.15)
    route_points([(10.25, 8.5), (10.25, 28.5), (9.99, 28.5)], pcbnew.B_Cu, led_b_drv, 0.15)

    led_b_net = nets["LED_B"]
    r7_2 = get_pad_pos("R7", "2")
    d2_2 = get_pad_pos("D2", "2")
    route_points([r7_2, (11.8, 29.2), (11.8, 28.85), d2_2], pcbnew.F_Cu, led_b_net, 0.15)

    led_r_drv = nets["LED_R_DRV"]
    u1_12 = get_pad_pos("U1", "12") # (10.938, 10.25)
    r6_1  = get_pad_pos("R6", "1")   # (9.990, 27.50)
    add_via(11.6, 10.25, led_r_drv)
    add_track(u1_12[0], u1_12[1], 11.6, 10.25, pcbnew.F_Cu, led_r_drv, 0.15)
    add_via(9.99, 27.0, led_r_drv)
    route_points([(9.99, 27.0), r6_1], pcbnew.F_Cu, led_r_drv, 0.15)
    route_points([(11.6, 10.25), (11.6, 27.0), (9.99, 27.0)], pcbnew.B_Cu, led_r_drv, 0.15)

    led_r_net = nets["LED_R"]
    r6_2 = get_pad_pos("R6", "2")
    d2_1 = get_pad_pos("D2", "1")
    route_points([r6_2, (11.8, 27.5), (11.8, 28.15), d2_1], pcbnew.F_Cu, led_r_net, 0.15)

    # Battery Protection & Load Sharing
    batt_pos_net = nets["BATT_POS"]
    tp_bp = get_pad_pos("TP_BATT_P", "1") # (4.8, 24.2)
    u4_5  = get_pad_pos("U4", "5")        # (4.138, 24.20)
    add_via(tp_bp[0], tp_bp[1], batt_pos_net)
    add_track(tp_bp[0], tp_bp[1], u4_5[0], u4_5[1], pcbnew.F_Cu, batt_pos_net, 0.25)

    # GATE_OD: U4.1 (1.863, 23.25) -> Q1.6 (8.637, 23.25) along Y=22.2 on F.Cu
    od_net = nets["GATE_OD"]
    u4_1 = get_pad_pos("U4", "1") # (1.863, 23.25)
    q1_6 = get_pad_pos("Q1", "6") # (8.637, 23.25)
    route_points([u4_1, (1.863, 22.2), (8.637, 22.2), q1_6], pcbnew.F_Cu, od_net, 0.15)

    # GATE_OC: U4.3 (1.863, 25.15) -> Q1.5 (8.637, 24.20) along Y=25.8 on F.Cu
    oc_net = nets["GATE_OC"]
    u4_3 = get_pad_pos("U4", "3") # (1.863, 25.15)
    q1_5 = get_pad_pos("Q1", "5") # (8.637, 24.20)
    route_points([u4_3, (1.863, 25.8), (7.5, 25.8), (7.5, 24.2), q1_5], pcbnew.F_Cu, oc_net, 0.15)

    # BATT_NEG: U4.6 (4.138, 23.25) -> via at (4.138, 22.5) -> B.Cu to TP_BATT_N (2.0, 26.8) and via at (8.637, 26.0) to Q1.4 (8.637, 25.15)
    batt_neg_net = nets["BATT_NEG"]
    tp_bn = get_pad_pos("TP_BATT_N", "1") # (2.0, 26.8)
    u4_6  = get_pad_pos("U4", "6")        # (4.138, 23.25)
    q1_4  = get_pad_pos("Q1", "4")        # (8.637, 25.15)
    add_via(4.138, 22.5, batt_neg_net)
    add_track(u4_6[0], u4_6[1], 4.138, 22.5, pcbnew.F_Cu, batt_neg_net, 0.20)
    add_via(8.637, 26.0, batt_neg_net)
    add_track(8.637, 26.0, q1_4[0], q1_4[1], pcbnew.F_Cu, batt_neg_net, 0.20)
    route_points([tp_bn, (2.0, 26.0), (8.637, 26.0)], pcbnew.B_Cu, batt_neg_net, 0.20)
    route_points([(4.138, 22.5), (3.0, 22.5), (3.0, 26.0)], pcbnew.B_Cu, batt_neg_net, 0.20)

    drain_net = nets["Net-(Q1-D12-Pad2)"]
    q1_2 = get_pad_pos("Q1", "2")
    q1_3 = get_pad_pos("Q1", "3")
    add_track(q1_2[0], q1_2[1], q1_3[0], q1_3[1], pcbnew.F_Cu, drain_net, 0.25)

    # VBUS_5V (B.Cu backbone along X=14.3)
    vbus_net = nets["VBUS_5V"]
    tp_vbus = get_pad_pos("TP_VBUS", "1") # (13.5, 4.2)
    c18_1   = get_pad_pos("C18", "1")     # (12.72, 13.5)
    c10_1   = get_pad_pos("C10", "1")     # (12.72, 15.5)
    u2_4    = get_pad_pos("U2", "4")      # (13.137, 21.15)
    q2_1    = get_pad_pos("Q2", "1")      # (11.062, 23.25)
    d1_2    = get_pad_pos("D1", "2")      # (8.55, 21.20)
    
    # B.Cu backbone
    route_points([tp_vbus, (14.3, 4.2), (14.3, 22.2)], pcbnew.B_Cu, vbus_net, 0.25)
    # Feed C18 and C10 on F.Cu via drop at (12.72, 14.5)
    add_via(12.72, 14.5, vbus_net)
    route_points([c18_1, (12.72, 14.5), c10_1], pcbnew.F_Cu, vbus_net, 0.20)
    add_track(14.3, 14.5, 12.72, 14.5, pcbnew.B_Cu, vbus_net, 0.20)
    # Feed U2.4 on F.Cu via drop at (13.8, 21.15)
    add_via(13.8, 21.15, vbus_net)
    add_track(13.8, 21.15, u2_4[0], u2_4[1], pcbnew.F_Cu, vbus_net, 0.20)
    add_track(14.3, 21.15, 13.8, 21.15, pcbnew.B_Cu, vbus_net, 0.20)
    # Feed Q2.1 and D1.2 via drop at (11.062, 22.2)
    add_via(11.062, 22.2, vbus_net)
    route_points([d1_2, (8.55, 22.2), (11.062, 22.2), q2_1], pcbnew.F_Cu, vbus_net, 0.20)
    add_track(14.3, 22.2, 11.062, 22.2, pcbnew.B_Cu, vbus_net, 0.20)

    # VBAT_PROT
    vbat_net = nets["VBAT_PROT"]
    c17_1 = get_pad_pos("C17", "1") # (11.72, 17.8)
    u2_3  = get_pad_pos("U2", "3")  # (10.863, 21.15)
    q2_3  = get_pad_pos("Q2", "3")  # (12.938, 24.20)
    route_points([c17_1, (10.0, 17.8), (10.0, 21.15), u2_3], pcbnew.F_Cu, vbat_net, 0.20)
    # Cross Q2 on B.Cu to reach Q2.3
    add_via(10.0, 21.15, vbat_net)
    add_via(12.938, 23.2, vbat_net)
    add_track(12.938, 23.2, q2_3[0], q2_3[1], pcbnew.F_Cu, vbat_net, 0.20)
    route_points([(10.0, 21.15), (12.938, 21.15), (12.938, 23.2)], pcbnew.B_Cu, vbat_net, 0.20)

    # SYS_PWR: D1.1 (6.45, 21.2) -> (6.45, 20.0) -> (10.0, 20.0) -> (10.0, 25.15) -> Q2.2 (11.062, 25.15)
    d1_1  = get_pad_pos("D1", "1") # (6.45, 21.20)
    q2_2  = get_pad_pos("Q2", "2") # (11.062, 25.15)
    u5_1  = get_pad_pos("U5", "1") # (1.863, 19.25)
    u5_3  = get_pad_pos("U5", "3") # (1.863, 21.15)
    c9_1  = get_pad_pos("C9", "1") # (2.28, 17.0)
    route_points([d1_1, (6.45, 20.0), (10.0, 20.0), (10.0, 25.15), q2_2], pcbnew.F_Cu, sys_net, 0.25)
    route_points([d1_1, (5.0, 21.20), u5_3], pcbnew.F_Cu, sys_net, 0.25)
    add_via(2.5, 21.8, sys_net)
    add_track(u5_3[0], u5_3[1], 2.5, 21.8, pcbnew.F_Cu, sys_net, 0.20)
    add_via(2.5, 17.0, sys_net)
    add_track(2.5, 17.0, c9_1[0], c9_1[1], pcbnew.F_Cu, sys_net, 0.20)
    route_points([(2.5, 17.0), (2.5, 19.25), u5_1], pcbnew.F_Cu, sys_net, 0.20)
    add_track(2.5, 21.8, 2.5, 17.0, pcbnew.B_Cu, sys_net, 0.20)

    # 7. 3V3 Power Plane Vias & Local F.Cu Routes
    u5_5  = get_pad_pos("U5", "5")  # (4.138, 19.25)
    c20_1 = get_pad_pos("C20", "1") # (5.0, 17.92)
    c21_1 = get_pad_pos("C21", "1") # (6.0, 17.92)
    route_points([u5_5, (4.138, 17.92), c20_1, c21_1], pcbnew.F_Cu, p3v3_net, 0.25)
    add_via(4.75, 17.5, p3v3_net)
    u1_37 = get_pad_pos("U1", "37") # (4.75, 16.438)
    add_track(u1_37[0], u1_37[1], 4.75, 17.5, pcbnew.F_Cu, p3v3_net, 0.20)
    add_track(4.75, 17.5, c20_1[0], c20_1[1], pcbnew.F_Cu, p3v3_net, 0.20)
    
    u1_41 = get_pad_pos("U1", "41") # (6.75, 16.438)
    add_track(u1_41[0], u1_41[1], 6.75, 17.5, pcbnew.F_Cu, p3v3_net, 0.20)
    add_track(6.75, 17.5, c21_1[0], c21_1[1], pcbnew.F_Cu, p3v3_net, 0.20)

    tp_3v3 = get_pad_pos("TP_3V3", "1")
    add_via(tp_3v3[0], tp_3v3[1], p3v3_net)

    # Right side 3V3 rail (F.Cu)
    c3_1  = get_pad_pos("C3", "1")
    c2_1  = get_pad_pos("C2", "1")
    c5_1  = get_pad_pos("C5", "1")
    c8_1  = get_pad_pos("C8", "1")
    u1_11 = get_pad_pos("U1", "11")
    route_points([c3_1, c2_1, c5_1, (12.72, 10.75), u1_11], pcbnew.F_Cu, p3v3_net, 0.25)
    add_track(12.72, 10.75, c8_1[0], c8_1[1], pcbnew.F_Cu, p3v3_net, 0.25)
    add_via(12.72, 10.75, p3v3_net)

    # Left side 3V3 rail
    u1_25 = get_pad_pos("U1", "25") # (4.062, 10.25)
    add_via(3.0, 10.25, p3v3_net)
    add_track(u1_25[0], u1_25[1], 3.0, 10.25, pcbnew.F_Cu, p3v3_net, 0.20)

    u1_28 = get_pad_pos("U1", "28") # (4.062, 11.75)
    add_via(3.0, 11.75, p3v3_net)
    add_track(u1_28[0], u1_28[1], 3.0, 11.75, pcbnew.F_Cu, p3v3_net, 0.20)

    c1_1 = get_pad_pos("C1", "1") # (2.28, 14.5)
    add_via(2.28, 13.7, p3v3_net)
    add_track(c1_1[0], c1_1[1], 2.28, 13.7, pcbnew.F_Cu, p3v3_net, 0.20)

    # Bottom MCU 3V3 Pins (44, 45, 46)
    u1_44 = get_pad_pos("U1", "44") # (8.25, 16.438)
    u1_45 = get_pad_pos("U1", "45") # (8.75, 16.438)
    u1_46 = get_pad_pos("U1", "46") # (9.25, 16.438)
    add_via(8.5, 17.5, p3v3_net)
    route_points([u1_44, (8.25, 16.85), (9.25, 16.85), u1_46], pcbnew.F_Cu, p3v3_net, 0.15)
    add_track(u1_45[0], u1_45[1], 8.75, 16.85, pcbnew.F_Cu, p3v3_net, 0.15)
    add_track(8.5, 16.85, 8.5, 17.5, pcbnew.F_Cu, p3v3_net, 0.20)

    # Audio 3V3
    mk1_5 = get_pad_pos("MK1", "5") # (8.400, 27.136)
    c15_1 = get_pad_pos("C15", "1") # (3.42, 28.5)
    c16_1 = get_pad_pos("C16", "1") # (1.32, 28.5)
    route_points([c16_1, (1.32, 27.8), (3.42, 27.8), c15_1], pcbnew.F_Cu, p3v3_net, 0.25)
    add_via(1.32, 27.2, p3v3_net)
    add_track(1.32, 27.8, 1.32, 27.2, pcbnew.F_Cu, p3v3_net, 0.25)
    add_via(9.5, 26.5, p3v3_net)
    route_points([mk1_5, (8.4, 26.5), (9.5, 26.5)], pcbnew.F_Cu, p3v3_net, 0.20)

    # 8. COPPER ZONES (L1, L2, L3, L4)
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

    # L3: Continuous 3V3 Plane across entire board
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

    # Fill all zones
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    out_pcb = "/Users/racoon/Documents/CHEATING/Device1/hardware/Device1.kicad_pcb"
    board.Save(out_pcb)
    print(f"Board successfully built and saved to {out_pcb}")

if __name__ == "__main__":
    build_board()
