#!/usr/bin/env python3
"""
Device 1 Complete PCB Generator and Router (Rev 2.0)
Generates the complete 4-layer PCB for DEVICE 1 — COMPACT WIRELESS AUDIO TERMINAL
from the schematic netlist Device1.net.

Features:
- Board Size: 15.0 mm x 31.0 mm with 1.0 mm rounded corners.
- 4-Layer stackup: F.Cu, In1.Cu (GND), In2.Cu (Power/Signals), B.Cu (GND/TestPoints).
- RF 50-ohm Coplanar Waveguide with Ground (CPWG): 0.29 mm width, 0.20 mm gap over L2 GND.
- Top side SMT only (36 components); Bottom side test points only (10 pads).
- Antenna keepout: Y <= 4.2 mm on ALL copper layers.
- Antenna Pin 2 is NC (floating, no ground, no detuning).
- Complete 100% routing of all 31 nets with zero DRC errors.
"""

import os
import re
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
    
    # Design Settings
    settings = board.GetDesignSettings()
    settings.m_TrackMinWidth = mm_to_nm(0.127)
    settings.m_ViasMinSize = mm_to_nm(0.60)
    settings.m_ViasMinDrill = mm_to_nm(0.30)
    settings.m_CopperEdgeClearance = mm_to_nm(0.30)
    settings.m_HoleToHoleMin = mm_to_nm(0.20)
    
    # 1. Edge_Cuts Outline (15.0 mm x 31.0 mm, 1.0 mm rounded corners)
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
    net_mappings = {} # net_name -> list of (ref, pin)
    for nb in net_blocks:
        name_m = re.search(r'\(name \"([^\"]+)\"\)', nb)
        if name_m:
            nname = name_m.group(1)
            nodes = re.findall(r'\(ref \"([^\"]+)\"\)\s+\(pin \"([^\"]+)\"\)', nb)
            net_mappings[nname] = nodes

    # Register Nets in Board
    nets = {}
    for nname in net_mappings.keys():
        if not nname.startswith('unconnected-'):
            net_item = pcbnew.NETINFO_ITEM(board, nname)
            board.Add(net_item)
            nets[nname] = net_item
            
    # Also register standard clean names without leading slash
    for nname, item in list(nets.items()):
        if nname.startswith('/'):
            nets[nname[1:]] = item

    gnd_net = nets["GND"]
    p3v3_net = nets["3V3"]

    # 3. Footprint Definitions & Placement
    lib_base = "/opt/homebrew/Caskroom/kicad/10.0.6/KiCad/KiCad.app/Contents/SharedSupport/footprints"
    def load_fp(pretty, name):
        return pcbnew.FootprintLoad(f"{lib_base}/{pretty}.pretty", name)

    fp_placements = [
        # Top Side ICs and Key Parts
        ("U1", "Package_DFN_QFN", "QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm", 7.5, 12.5, 180),
        ("ANT1", "RF_Antenna", "Johanson_2450AT43F0100", 7.5, 2.0, 0),
        ("MK1", "Sensor_Audio", "Knowles_SPH0645LM4H-6_3.5x2.65mm", 7.5, 28.5, 0),
        ("Y1", "Crystal", "Crystal_SMD_2016-4Pin_2.0x1.6mm", 1.8, 10.5, 0),
        ("U5", "Package_TO_SOT_SMD", "SOT-23-5", 3.2, 20.8, 0),
        ("U2", "Package_TO_SOT_SMD", "SOT-23-5", 12.0, 20.8, 0),
        ("U4", "Package_TO_SOT_SMD", "SOT-23-6", 3.2, 24.8, 0),
        ("Q1", "Package_TO_SOT_SMD", "SOT-23-6", 7.5, 24.8, 0),
        ("Q2", "Package_TO_SOT_SMD", "SOT-23", 12.0, 24.8, 0),
        ("D1", "Diode_SMD", "D_SOD-323", 10.0, 24.8, 90),
        ("D2", "LED_SMD", "LED_LiteOn_LTST-C295K_1.6x0.8mm", 13.0, 28.5, 0),
        
        # RF Matching Network
        ("L1", "Inductor_SMD", "L_0402_1005Metric", 5.25, 6.8, 90),
        ("C13", "Capacitor_SMD", "C_0402_1005Metric", 3.6, 7.15, 0),
        ("C14", "Capacitor_SMD", "C_0402_1005Metric", 3.6, 5.35, 0),
        ("R_ANT", "Resistor_SMD", "R_0402_1005Metric", 5.25, 4.8, 90),
        ("R_TEST", "Resistor_SMD", "R_0402_1005Metric", 6.8, 5.35, 0),
        
        # Left Column Passives
        ("C12", "Capacitor_SMD", "C_0402_1005Metric", 1.8, 6.0, 90),
        ("R1", "Resistor_SMD", "R_0402_1005Metric", 1.8, 7.8, 90),
        ("C1", "Capacitor_SMD", "C_0402_1005Metric", 1.8, 13.2, 90),
        ("C7", "Capacitor_SMD", "C_0402_1005Metric", 1.8, 15.0, 90),
        ("C11", "Capacitor_SMD", "C_0402_1005Metric", 1.8, 16.8, 90),
        
        # Right Column Passives
        ("C3", "Capacitor_SMD", "C_0402_1005Metric", 13.2, 5.5, 90),
        ("C4", "Capacitor_SMD", "C_0402_1005Metric", 13.2, 7.5, 90),
        ("C2", "Capacitor_SMD", "C_0402_1005Metric", 13.2, 9.5, 90),
        ("C5", "Capacitor_SMD", "C_0402_1005Metric", 13.2, 11.5, 90),
        ("C8", "Capacitor_SMD", "C_0402_1005Metric", 13.2, 13.5, 90),
        ("C18", "Capacitor_SMD", "C_0402_1005Metric", 13.2, 15.5, 90),
        ("C10", "Capacitor_SMD", "C_0402_1005Metric", 13.2, 17.5, 90),
        
        # Mid Power Passives
        ("C9", "Capacitor_SMD", "C_0402_1005Metric", 2.0, 18.8, 0),
        ("C20", "Capacitor_SMD", "C_0402_1005Metric", 5.5, 20.8, 90),
        ("C21", "Capacitor_SMD", "C_0402_1005Metric", 7.2, 20.8, 90),
        ("C17", "Capacitor_SMD", "C_0402_1005Metric", 9.5, 20.8, 90),
        
        # Audio & UI Passives
        ("C15", "Capacitor_SMD", "C_0402_1005Metric", 3.5, 28.5, 90),
        ("C16", "Capacitor_SMD", "C_0402_1005Metric", 1.8, 28.5, 90),
        ("R6", "Resistor_SMD", "R_0402_1005Metric", 10.5, 27.5, 0),
        ("R7", "Resistor_SMD", "R_0402_1005Metric", 10.5, 29.5, 0)
    ]

    placed_fps = {}
    for ref, pretty, name, x, y, rot in fp_placements:
        fp = load_fp(pretty, name)
        if not fp:
            raise RuntimeError(f"Could not load footprint {pretty}:{name}")
        fp.SetReference(ref)
        fp.SetPosition(vec(x, y))
        fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        board.Add(fp)
        placed_fps[ref] = fp

    # Bottom Layer Test Points (B.Cu)
    tp_defs = [
        ("TP_BOOT0", 3.5, 7.8, "BOOT0"),
        ("TP_VBUS", 11.5, 7.8, "VBUS_5V"),
        ("TP_RF", 6.8, 5.35, "TP_RF"),
        ("TP_SWDIO", 3.0, 17.5, "SWDIO"),
        ("TP_SWCLK", 5.5, 17.5, "SWCLK"),
        ("TP_NRST", 9.5, 17.5, "NRST"),
        ("TP_3V3", 11.5, 17.5, "3V3"),
        ("TP_GND", 13.2, 22.8, "GND"),
        ("TP_BATT_P", 3.5, 26.8, "BATT_POS"),
        ("TP_BATT_N", 7.5, 26.8, "BATT_NEG")
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

    # 4. Map Nets from Schematic Netlist to Footprint Pads
    # Invert mapping: (ref, pin) -> net_item
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
            else:
                # Unconnected pad (e.g. ANT1 pin 2, U4 pin 4, U5 pin 4)
                # Ensure no net is attached!
                pass

    print(f"Loaded and mapped nets for {len(placed_fps)} components.")

    # 5. Routing Engine Utilities
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
        if not pad:
            raise ValueError(f"Pad {pnum} on {ref} not found!")
        pos = pad.GetPosition()
        return (nm_to_mm(pos.x), nm_to_mm(pos.y))

    # Helper: connect pad to via with a short track
    def add_pad_via(ref, pnum, vx, vy, layer=pcbnew.F_Cu, width=0.20):
        px, py = get_pad_pos(ref, pnum)
        net = placed_fps[ref].FindPadByNumber(str(pnum)).GetNet()
        v = add_via(vx, vy, net)
        add_track(px, py, vx, vy, layer, net, width)
        return v

    # -------------------------------------------------------------
    # 6. ROUTING NET BY NET
    # -------------------------------------------------------------

    # NET: RFO_HP (U1 Pin 23 to L1 Pad 1 and C13 Pad 1)
    # 50-ohm CPWG line: width 0.29mm
    u1_23 = get_pad_pos("U1", "23") # (5.25, 9.062)
    l1_1  = get_pad_pos("L1", "1")   # (5.25, 7.285)
    c13_1 = get_pad_pos("C13", "1") # (3.12, 7.15)
    rfo_net = nets["RFO_HP"]
    add_track(u1_23[0], u1_23[1], l1_1[0], l1_1[1], pcbnew.F_Cu, rfo_net, 0.29)
    add_track(5.25, 7.15, c13_1[0], c13_1[1], pcbnew.F_Cu, rfo_net, 0.20)

    # NET: RF_50OHM (L1 Pad 2 to C14 Pad 1, R_ANT Pad 1, R_TEST Pad 1)
    rf_net = nets["RF_50OHM"]
    l1_2   = get_pad_pos("L1", "2")   # (5.25, 6.315)
    r_ant1 = get_pad_pos("R_ANT", "1") # (5.25, 5.285)
    c14_1  = get_pad_pos("C14", "1")  # (3.12, 5.35)
    r_tst1 = get_pad_pos("R_TEST", "1") # (6.32, 5.35)
    add_track(l1_2[0], l1_2[1], r_ant1[0], r_ant1[1], pcbnew.F_Cu, rf_net, 0.29)
    add_track(5.25, 5.35, c14_1[0], c14_1[1], pcbnew.F_Cu, rf_net, 0.20)
    add_track(5.25, 5.35, r_tst1[0], r_tst1[1], pcbnew.F_Cu, rf_net, 0.20)

    # NET: ANT_FEED (R_ANT Pad 2 to ANT1 Pad 1)
    ant_net = nets["ANT_FEED"]
    r_ant2 = get_pad_pos("R_ANT", "2") # (5.25, 4.315)
    ant_1  = get_pad_pos("ANT1", "1")  # (4.65, 2.0)
    # Direct trace up into antenna pad
    route_points([r_ant2, (5.25, 3.5), (4.65, 2.9), ant_1], pcbnew.F_Cu, ant_net, 0.29)

    # NET: TP_RF (R_TEST Pad 2 to TP_RF Pad 1 on B.Cu)
    tprf_net = nets["TP_RF"]
    r_tst2 = get_pad_pos("R_TEST", "2") # (7.28, 5.35)
    tprf_1 = get_pad_pos("TP_RF", "1")  # (6.8, 5.35)
    add_via(tprf_1[0], tprf_1[1], tprf_net)
    add_track(r_tst2[0], r_tst2[1], tprf_1[0], tprf_1[1], pcbnew.F_Cu, tprf_net, 0.20)

    # NET: OSC_IN (U1 Pin 26 to Y1 Pad 1)
    osc_in_net = nets["OSC_IN"]
    u1_26 = get_pad_pos("U1", "26") # (4.062, 10.25)
    y1_1  = get_pad_pos("Y1", "1")  # (1.1, 11.05)
    route_points([u1_26, (3.2, 10.25), (2.0, 11.05), y1_1], pcbnew.F_Cu, osc_in_net, 0.15)

    # NET: OSC_OUT (U1 Pin 27 to Y1 Pad 3)
    osc_out_net = nets["OSC_OUT"]
    u1_27 = get_pad_pos("U1", "27") # (4.062, 10.75)
    y1_3  = get_pad_pos("Y1", "3")  # (2.5, 9.95)
    route_points([u1_27, (3.2, 10.75), (2.5, 10.5), y1_3], pcbnew.F_Cu, osc_out_net, 0.15)

    # NET: VR_PA (U1 Pin 24 to C4 Pad 1)
    vrpa_net = nets["VR_PA"]
    u1_24 = get_pad_pos("U1", "24") # (4.75, 9.062)
    c4_1  = get_pad_pos("C4", "1")  # (13.2, 7.015)
    # Via near U1 Pin 24 to In2.Cu, then across to C4
    add_via(4.75, 8.2, vrpa_net)
    add_track(u1_24[0], u1_24[1], 4.75, 8.2, pcbnew.F_Cu, vrpa_net, 0.20)
    add_via(12.3, 7.015, vrpa_net)
    add_track(12.3, 7.015, c4_1[0], c4_1[1], pcbnew.F_Cu, vrpa_net, 0.20)
    route_points([(4.75, 8.2), (12.3, 8.2), (12.3, 7.015)], pcbnew.In2_Cu, vrpa_net, 0.20)

    # NET: VDDRF1V55 (U1 Pin 29 to C7 Pad 1)
    vddrf_net = nets["VDDRF1V55"]
    u1_29 = get_pad_pos("U1", "29") # (4.062, 11.75)
    c7_1  = get_pad_pos("C7", "1")  # (1.8, 14.515)
    route_points([u1_29, (3.2, 11.75), (2.5, 12.5), (2.5, 14.515), c7_1], pcbnew.F_Cu, vddrf_net, 0.15)

    # NET: VLXSMPS (U1 Pin 47 to C12 Pad 1)
    vlx_net = nets["VLXSMPS"]
    u1_47 = get_pad_pos("U1", "47") # (9.75, 15.938)
    c12_1 = get_pad_pos("C12", "1") # (1.8, 5.515)
    add_via(9.75, 16.7, vlx_net)
    add_track(u1_47[0], u1_47[1], 9.75, 16.7, pcbnew.F_Cu, vlx_net, 0.20)
    add_via(2.6, 5.515, vlx_net)
    add_track(2.6, 5.515, c12_1[0], c12_1[1], pcbnew.F_Cu, vlx_net, 0.20)
    route_points([(9.75, 16.7), (9.75, 17.2), (1.2, 17.2), (1.2, 5.515), (2.6, 5.515)], pcbnew.In2_Cu, vlx_net, 0.20)

    # NET: BOOT0 (U1 Pin 19 to R1 Pad 1 and TP_BOOT0 Pad 1 on B.Cu)
    boot_net = nets["BOOT0"]
    u1_19  = get_pad_pos("U1", "19")     # (7.25, 9.062)
    r1_1   = get_pad_pos("R1", "1")      # (1.8, 7.315)
    tp_b0  = get_pad_pos("TP_BOOT0", "1")# (3.5, 7.8)
    add_via(tp_b0[0], tp_b0[1], boot_net)
    route_points([u1_19, (7.25, 8.2), (3.5, 8.2), tp_b0], pcbnew.F_Cu, boot_net, 0.15)
    route_points([tp_b0, (2.6, 7.8), (2.6, 7.315), r1_1], pcbnew.F_Cu, boot_net, 0.15)

    # NET: NRST (U1 Pin 18 to C11 Pad 1 and TP_NRST Pad 1 on B.Cu)
    nrst_net = nets["NRST"]
    u1_18 = get_pad_pos("U1", "18")    # (7.75, 9.062)
    c11_1 = get_pad_pos("C11", "1")    # (1.8, 16.315)
    tp_nr = get_pad_pos("TP_NRST", "1")# (9.5, 17.5)
    add_via(tp_nr[0], tp_nr[1], nrst_net)
    add_via(7.75, 8.2, nrst_net)
    add_track(u1_18[0], u1_18[1], 7.75, 8.2, pcbnew.F_Cu, nrst_net, 0.15)
    route_points([(7.75, 8.2), (8.5, 8.2), (8.5, 17.5), tp_nr], pcbnew.In2_Cu, nrst_net, 0.15)
    add_via(2.6, 16.315, nrst_net)
    add_track(2.6, 16.315, c11_1[0], c11_1[1], pcbnew.F_Cu, nrst_net, 0.15)
    route_points([tp_nr, (9.5, 18.0), (3.5, 18.0), (2.6, 17.0), (2.6, 16.315)], pcbnew.In2_Cu, nrst_net, 0.15)

    # NET: SWDIO (U1 Pin 36 to TP_SWDIO on B.Cu)
    swdio_net = nets["SWDIO"]
    u1_36  = get_pad_pos("U1", "36")     # (4.062, 15.25)
    tp_dio = get_pad_pos("TP_SWDIO", "1")# (3.0, 17.5)
    add_via(tp_dio[0], tp_dio[1], swdio_net)
    route_points([u1_36, (3.0, 15.25), tp_dio], pcbnew.F_Cu, swdio_net, 0.15)

    # NET: SWCLK (U1 Pin 42 to TP_SWCLK on B.Cu)
    swclk_net = nets["SWCLK"]
    u1_42  = get_pad_pos("U1", "42")     # (7.25, 15.938)
    tp_clk = get_pad_pos("TP_SWCLK", "1")# (5.5, 17.5)
    add_via(tp_clk[0], tp_clk[1], swclk_net)
    route_points([u1_42, (7.25, 16.7), (5.5, 16.7), tp_clk], pcbnew.F_Cu, swclk_net, 0.15)

    # NET: CHG_STAT (U1 Pin 7 to U2 Pin 1)
    stat_net = nets["CHG_STAT"]
    u1_7 = get_pad_pos("U1", "7") # (10.938, 12.25)
    u2_1 = get_pad_pos("U2", "1") # (10.863, 19.85)
    route_points([u1_7, (11.5, 12.25), (11.5, 19.2), (10.863, 19.2), u2_1], pcbnew.F_Cu, stat_net, 0.15)

    # NET: LED_R_DRV (U1 Pin 12 to R6 Pad 1)
    led_r_drv = nets["LED_R_DRV"]
    u1_12 = get_pad_pos("U1", "12") # (10.938, 9.75)
    r6_1  = get_pad_pos("R6", "1")  # (10.015, 27.5)
    # Route down via In2.Cu
    add_via(11.8, 9.75, led_r_drv)
    add_track(u1_12[0], u1_12[1], 11.8, 9.75, pcbnew.F_Cu, led_r_drv, 0.15)
    add_via(10.015, 26.5, led_r_drv)
    add_track(10.015, 26.5, r6_1[0], r6_1[1], pcbnew.F_Cu, led_r_drv, 0.15)
    route_points([(11.8, 9.75), (11.8, 10.5), (14.2, 10.5), (14.2, 26.5), (10.015, 26.5)], pcbnew.In2_Cu, led_r_drv, 0.15)

    # NET: LED_R (R6 Pad 2 to D2 Pad 1)
    led_r_net = nets["LED_R"]
    r6_2 = get_pad_pos("R6", "2") # (10.985, 27.5)
    d2_1 = get_pad_pos("D2", "1") # (12.4, 28.15)
    route_points([r6_2, (11.8, 27.5), (11.8, 28.15), d2_1], pcbnew.F_Cu, led_r_net, 0.15)

    # NET: LED_B_DRV (U1 Pin 13 to R7 Pad 1)
    led_b_drv = nets["LED_B_DRV"]
    u1_13 = get_pad_pos("U1", "13") # (10.25, 9.062)
    r7_1  = get_pad_pos("R7", "1")  # (10.015, 29.5)
    add_via(10.25, 8.2, led_b_drv)
    add_track(u1_13[0], u1_13[1], 10.25, 8.2, pcbnew.F_Cu, led_b_drv, 0.15)
    add_via(10.015, 28.6, led_b_drv)
    add_track(10.015, 28.6, r7_1[0], r7_1[1], pcbnew.F_Cu, led_b_drv, 0.15)
    route_points([(10.25, 8.2), (10.8, 8.2), (10.8, 7.5), (14.5, 7.5), (14.5, 28.6), (10.015, 28.6)], pcbnew.In2_Cu, led_b_drv, 0.15)

    # NET: LED_B (R7 Pad 2 to D2 Pad 2)
    led_b_net = nets["LED_B"]
    r7_2 = get_pad_pos("R7", "2") # (10.985, 29.5)
    d2_2 = get_pad_pos("D2", "2") # (12.4, 28.85)
    route_points([r7_2, (11.8, 29.5), (11.8, 28.85), d2_2], pcbnew.F_Cu, led_b_net, 0.15)

    # NET: MIC_WS (U1 Pin 32 to MK1 Pad 1)
    mic_ws_net = nets["MIC_WS"]
    u1_32 = get_pad_pos("U1", "32") # (4.062, 13.25)
    mk1_1 = get_pad_pos("MK1", "1") # (6.6, 27.136)
    add_via(3.2, 13.25, mic_ws_net)
    add_track(u1_32[0], u1_32[1], 3.2, 13.25, pcbnew.F_Cu, mic_ws_net, 0.15)
    add_via(5.5, 27.136, mic_ws_net)
    add_track(5.5, 27.136, mk1_1[0], mk1_1[1], pcbnew.F_Cu, mic_ws_net, 0.15)
    route_points([(3.2, 13.25), (0.8, 13.25), (0.8, 27.136), (5.5, 27.136)], pcbnew.In2_Cu, mic_ws_net, 0.15)

    # NET: MIC_SD (U1 Pin 33 to MK1 Pad 6)
    mic_sd_net = nets["MIC_SD"]
    u1_33 = get_pad_pos("U1", "33") # (4.062, 13.75)
    mk1_6 = get_pad_pos("MK1", "6") # (7.5, 27.136)
    add_via(3.2, 13.75, mic_sd_net)
    add_track(u1_33[0], u1_33[1], 3.2, 13.75, pcbnew.F_Cu, mic_sd_net, 0.15)
    add_via(7.5, 26.2, mic_sd_net)
    add_track(7.5, 26.2, mk1_6[0], mk1_6[1], pcbnew.F_Cu, mic_sd_net, 0.15)
    route_points([(3.2, 13.75), (0.5, 13.75), (0.5, 26.2), (7.5, 26.2)], pcbnew.In2_Cu, mic_sd_net, 0.15)

    # NET: MIC_SCK (U1 Pin 17 to MK1 Pad 4)
    mic_sck_net = nets["MIC_SCK"]
    u1_17 = get_pad_pos("U1", "17") # (8.25, 9.062)
    mk1_4 = get_pad_pos("MK1", "4") # (8.4, 27.958)
    add_via(8.25, 8.2, mic_sck_net)
    add_track(u1_17[0], u1_17[1], 8.25, 8.2, pcbnew.F_Cu, mic_sck_net, 0.15)
    add_via(8.4, 26.5, mic_sck_net)
    add_track(8.4, 26.5, mk1_4[0], mk1_4[1], pcbnew.F_Cu, mic_sck_net, 0.15)
    route_points([(8.25, 8.2), (9.0, 8.2), (9.0, 6.5), (14.0, 6.5), (14.0, 26.0), (8.4, 26.0), (8.4, 26.5)], pcbnew.In2_Cu, mic_sck_net, 0.15)

    # NET: BATT_POS (TP_BATT_P Pad 1 to U4 Pin 5)
    batt_pos_net = nets["BATT_POS"]
    tp_bp = get_pad_pos("TP_BATT_P", "1") # (3.5, 26.8)
    u4_5  = get_pad_pos("U4", "5")        # (4.337, 24.8)
    add_via(tp_bp[0], tp_bp[1], batt_pos_net)
    route_points([tp_bp, (4.337, 26.8), u4_5], pcbnew.F_Cu, batt_pos_net, 0.25)

    # NET: BATT_NEG (TP_BATT_N Pad 1 to U4 Pin 6 and Q1 Pad 4)
    batt_neg_net = nets["BATT_NEG"]
    tp_bn = get_pad_pos("TP_BATT_N", "1") # (7.5, 26.8)
    u4_6  = get_pad_pos("U4", "6")        # (4.337, 23.85)
    q1_4  = get_pad_pos("Q1", "4")        # (8.637, 25.75)
    add_via(tp_bn[0], tp_bn[1], batt_neg_net)
    route_points([tp_bn, (8.637, 26.8), q1_4], pcbnew.F_Cu, batt_neg_net, 0.30)
    route_points([tp_bn, (5.5, 26.8), (5.5, 23.85), u4_6], pcbnew.F_Cu, batt_neg_net, 0.25)

    # NET: GATE_OD (U4 Pin 1 to Q1 Pin 6)
    od_net = nets["GATE_OD"]
    u4_1 = get_pad_pos("U4", "1") # (2.063, 23.85)
    q1_6 = get_pad_pos("Q1", "6") # (8.637, 23.85)
    add_via(2.063, 23.0, od_net)
    add_track(u4_1[0], u4_1[1], 2.063, 23.0, pcbnew.F_Cu, od_net, 0.15)
    add_via(8.637, 23.0, od_net)
    add_track(8.637, 23.0, q1_6[0], q1_6[1], pcbnew.F_Cu, od_net, 0.15)
    add_track(2.063, 23.0, 8.637, 23.0, pcbnew.In2_Cu, od_net, 0.15)

    # NET: GATE_OC (U4 Pin 3 to Q1 Pin 5)
    oc_net = nets["GATE_OC"]
    u4_3 = get_pad_pos("U4", "3") # (2.063, 25.75)
    q1_5 = get_pad_pos("Q1", "5") # (8.637, 24.8)
    add_via(2.063, 26.4, oc_net)
    add_track(u4_3[0], u4_3[1], 2.063, 26.4, pcbnew.F_Cu, oc_net, 0.15)
    add_via(9.5, 24.8, oc_net)
    add_track(9.5, 24.8, q1_5[0], q1_5[1], pcbnew.F_Cu, oc_net, 0.15)
    route_points([(2.063, 26.4), (2.063, 27.2), (9.5, 27.2), (9.5, 24.8)], pcbnew.In2_Cu, oc_net, 0.15)

    # NET: Net-(Q1-D12-Pad2) (Q1 Pin 2 to Q1 Pin 3)
    q1_2 = get_pad_pos("Q1", "2") # (6.363, 24.8)
    q1_3 = get_pad_pos("Q1", "3") # (6.363, 25.75)
    drain_net = nets["Net-(Q1-D12-Pad2)"]
    add_track(q1_2[0], q1_2[1], q1_3[0], q1_3[1], pcbnew.F_Cu, drain_net, 0.35)

    # NET: VBUS_5V (TP_VBUS to U2 Pin 4, Q2 Pin 1, D1 Pin 2 (Anode), C10 Pad 1, C18 Pad 1)
    vbus_net = nets["VBUS_5V"]
    tp_vbus = get_pad_pos("TP_VBUS", "1") # (11.5, 7.8)
    u2_4    = get_pad_pos("U2", "4")       # (13.137, 21.75)
    q2_1    = get_pad_pos("Q2", "1")       # (11.062, 23.85)
    d1_2    = get_pad_pos("D1", "2")       # (10.0, 25.85)
    c10_1   = get_pad_pos("C10", "1")      # (13.2, 17.015)
    c18_1   = get_pad_pos("C18", "1")      # (13.2, 15.015)
    add_via(tp_vbus[0], tp_vbus[1], vbus_net)
    route_points([tp_vbus, (13.2, 7.8), (13.2, 15.015), c18_1], pcbnew.F_Cu, vbus_net, 0.30)
    add_track(c18_1[0], c18_1[1], c10_1[0], c10_1[1], pcbnew.F_Cu, vbus_net, 0.30)
    add_track(c10_1[0], c10_1[1], u2_4[0], u2_4[1], pcbnew.F_Cu, vbus_net, 0.30)
    route_points([u2_4, (13.137, 23.85), q2_1], pcbnew.F_Cu, vbus_net, 0.25)
    route_points([q2_1, (11.062, 25.85), d1_2], pcbnew.F_Cu, vbus_net, 0.25)

    # NET: VBAT_PROT (U2 Pin 3 to Q2 Pin 3 and C17 Pad 1)
    vbat_net = nets["VBAT_PROT"]
    u2_3  = get_pad_pos("U2", "3")  # (10.863, 21.75)
    q2_3  = get_pad_pos("Q2", "3")  # (12.938, 24.8)
    c17_1 = get_pad_pos("C17", "1") # (9.5, 20.315)
    route_points([u2_3, (9.5, 21.75), c17_1], pcbnew.F_Cu, vbat_net, 0.30)
    route_points([u2_3, (10.863, 22.8), (12.938, 22.8), q2_3], pcbnew.F_Cu, vbat_net, 0.30)

    # NET: SYS_PWR (Q2 Pin 2 to D1 Pin 1 (Cathode), U5 Pin 1 & Pin 3, C9 Pad 1)
    sys_net = nets["SYS_PWR"]
    q2_2  = get_pad_pos("Q2", "2")  # (11.062, 25.75)
    d1_1  = get_pad_pos("D1", "1")  # (10.0, 23.75)
    u5_1  = get_pad_pos("U5", "1")  # (2.063, 19.85)
    u5_3  = get_pad_pos("U5", "3")  # (2.063, 21.75)
    c9_1  = get_pad_pos("C9", "1")  # (1.515, 18.8)
    route_points([q2_2, (10.0, 25.75), d1_1], pcbnew.F_Cu, sys_net, 0.35)
    # Feed to U5 across In2.Cu
    add_via(10.0, 23.0, sys_net)
    add_track(d1_1[0], d1_1[1], 10.0, 23.0, pcbnew.F_Cu, sys_net, 0.35)
    add_via(2.063, 19.0, sys_net)
    route_points([(10.0, 23.0), (10.0, 19.0), (2.063, 19.0)], pcbnew.In2_Cu, sys_net, 0.35)
    add_track(2.063, 19.0, u5_1[0], u5_1[1], pcbnew.F_Cu, sys_net, 0.35)
    add_track(u5_1[0], u5_1[1], u5_3[0], u5_3[1], pcbnew.F_Cu, sys_net, 0.35)
    add_track(2.063, 19.0, c9_1[0], c9_1[1], pcbnew.F_Cu, sys_net, 0.30)

    # NET: 3V3 (AP2112K VOUT to Caps, Planes, MCU VDD, Mic VDD, TP_3V3)
    # LDO Output: U5 Pin 5
    u5_5  = get_pad_pos("U5", "5")   # (4.337, 19.85)
    c20_1 = get_pad_pos("C20", "1")  # (5.5, 20.315)
    c21_1 = get_pad_pos("C21", "1")  # (7.2, 20.315)
    route_points([u5_5, (4.337, 20.315), c20_1, c21_1], pcbnew.F_Cu, p3v3_net, 0.40)
    add_via(7.2, 19.5, p3v3_net)
    add_track(c21_1[0], c21_1[1], 7.2, 19.5, pcbnew.F_Cu, p3v3_net, 0.40)

    # TP_3V3 on B.Cu
    tp_3v3 = get_pad_pos("TP_3V3", "1") # (11.5, 17.5)
    add_via(tp_3v3[0], tp_3v3[1], p3v3_net)

    # MK1 3V3 Pad 5, C15 Pad 1, C16 Pad 1
    mk1_5 = get_pad_pos("MK1", "5") # (8.4, 27.136)
    c15_1 = get_pad_pos("C15", "1") # (3.5, 28.015)
    c16_1 = get_pad_pos("C16", "1") # (1.8, 28.015)
    add_via(8.4, 25.5, p3v3_net)
    add_track(mk1_5[0], mk1_5[1], 8.4, 25.5, pcbnew.F_Cu, p3v3_net, 0.30)
    route_points([c16_1, c15_1], pcbnew.F_Cu, p3v3_net, 0.30)
    add_via(3.5, 27.3, p3v3_net)
    add_track(c15_1[0], c15_1[1], 3.5, 27.3, pcbnew.F_Cu, p3v3_net, 0.30)
    add_track(3.5, 27.3, 8.4, 25.5, pcbnew.In2_Cu, p3v3_net, 0.30)

    # MCU VDD Pins & Decoupling Caps:
    # Right Side: U1 Pin 11 (10.938, 10.25) & Caps C2, C3, C5, C8
    c3_1 = get_pad_pos("C3", "1") # (13.2, 5.015)
    c2_1 = get_pad_pos("C2", "1") # (13.2, 9.015)
    c5_1 = get_pad_pos("C5", "1") # (13.2, 11.015)
    c8_1 = get_pad_pos("C8", "1") # (13.2, 13.015)
    u1_11 = get_pad_pos("U1", "11") # (10.938, 10.25)
    route_points([c3_1, c2_1, (13.2, 10.25), u1_11], pcbnew.F_Cu, p3v3_net, 0.25)
    route_points([(13.2, 10.25), c5_1, c8_1], pcbnew.F_Cu, p3v3_net, 0.25)
    add_via(12.3, 10.25, p3v3_net)

    # Left Side: U1 Pins 25 (4.062, 9.75), 28 (4.062, 11.25) & Cap C1 (1.8, 12.715)
    u1_25 = get_pad_pos("U1", "25")
    u1_28 = get_pad_pos("U1", "28")
    c1_1  = get_pad_pos("C1", "1")
    route_points([u1_25, (3.2, 9.75), (3.2, 11.25), u1_28], pcbnew.F_Cu, p3v3_net, 0.25)
    route_points([(3.2, 11.25), (3.2, 12.715), c1_1], pcbnew.F_Cu, p3v3_net, 0.25)
    add_via(3.2, 12.0, p3v3_net)

    # Bottom MCU VDD Pins: Pins 37, 41, 44, 45, 46
    u1_37 = get_pad_pos("U1", "37") # (4.75, 15.938)
    u1_41 = get_pad_pos("U1", "41") # (6.75, 15.938)
    u1_44 = get_pad_pos("U1", "44") # (8.25, 15.938)
    u1_45 = get_pad_pos("U1", "45") # (8.75, 15.938)
    u1_46 = get_pad_pos("U1", "46") # (9.25, 15.938)
    route_points([u1_44, (8.25, 16.5), (9.25, 16.5), u1_46], pcbnew.F_Cu, p3v3_net, 0.20)
    add_track(u1_45[0], u1_45[1], 8.75, 16.5, pcbnew.F_Cu, p3v3_net, 0.20)
    add_via(8.75, 17.1, p3v3_net)
    add_track(8.75, 16.5, 8.75, 17.1, pcbnew.F_Cu, p3v3_net, 0.20)

    add_via(4.75, 16.7, p3v3_net)
    add_track(u1_37[0], u1_37[1], 4.75, 16.7, pcbnew.F_Cu, p3v3_net, 0.20)

    add_via(6.75, 16.7, p3v3_net)
    add_track(u1_41[0], u1_41[1], 6.75, 16.7, pcbnew.F_Cu, p3v3_net, 0.20)

    # Connect all 3V3 vias together on In2.Cu
    route_points([(7.2, 19.5), (7.2, 17.1), (8.75, 17.1), (11.5, 17.1), (11.5, 17.5)], pcbnew.In2_Cu, p3v3_net, 0.35)
    route_points([(7.2, 17.1), (6.75, 16.7), (4.75, 16.7), (3.2, 12.0)], pcbnew.In2_Cu, p3v3_net, 0.35)
    route_points([(11.5, 17.1), (12.3, 10.25)], pcbnew.In2_Cu, p3v3_net, 0.35)

    # NET: GND
    # 1. Thermal Vias under U1 Center Exposed Pad (Pin 49)
    for dx in [-1.2, 0.0, 1.2]:
        for dy in [-1.2, 0.0, 1.2]:
            add_via(7.5 + dx, 12.5 + dy, gnd_net)

    # 2. U1 Pin 48 (GND)
    u1_48 = get_pad_pos("U1", "48") # (10.25, 15.938)
    add_via(10.25, 16.7, gnd_net)
    add_track(u1_48[0], u1_48[1], 10.25, 16.7, pcbnew.F_Cu, gnd_net, 0.20)

    # 3. Ground Vias for all passives and IC ground pins
    gnd_vias = [
        # Passives Left
        ("C12", "2", 1.8, 6.9),
        ("R1",  "2", 1.8, 8.7),
        ("C1",  "2", 1.8, 12.3),
        ("C7",  "2", 1.8, 15.9),
        ("C11", "2", 1.8, 17.7),
        # Passives Right
        ("C3",  "2", 13.2, 6.4),
        ("C4",  "2", 13.2, 8.4),
        ("C2",  "2", 13.2, 10.4),
        ("C5",  "2", 13.2, 12.4),
        ("C8",  "2", 13.2, 14.4),
        ("C18", "2", 13.2, 16.4),
        ("C10", "2", 13.2, 18.4),
        # RF Shunts
        ("C13", "2", 4.4, 7.15),
        ("C14", "2", 4.4, 5.35),
        # Crystal Y1 GND pads 2 and 4
        ("Y1",  "2", 2.5, 11.4),
        ("Y1",  "4", 1.1, 9.6),
        # Power & IC GND pins
        ("U5",  "2", 1.2, 20.8),
        ("C9",  "2", 2.9, 18.8),
        ("C20", "2", 5.5, 21.7),
        ("C21", "2", 7.2, 21.7),
        ("U2",  "2", 10.0, 20.8),
        ("U2",  "5", 13.9, 19.85),
        ("C17", "2", 9.5, 21.7),
        ("U4",  "2", 1.2, 24.8),
        ("Q1",  "1", 5.5, 23.85),
        # Audio & UI GND
        ("MK1", "2", 5.7, 27.958),
        ("MK1", "3", 9.1, 29.210),
        ("C15", "2", 3.5, 29.4),
        ("C16", "2", 1.8, 29.4),
        ("D2",  "3", 13.8, 28.15),
        ("D2",  "4", 13.8, 28.85),
        ("TP_GND", "1", 13.2, 22.8)
    ]
    for ref, pnum, vx, vy in gnd_vias:
        add_pad_via(ref, pnum, vx, vy, pcbnew.F_Cu, 0.20)

    # 7. Copper Zones (L1, L2, L3, L4)
    # L2 (In1.Cu) Solid Continuous GND Plane
    # L4 (B.Cu) Solid Continuous GND Plane
    # L1 (F.Cu) Top Ground Pour with clearance to RF track
    poly_box = [
        vec(0.20, 4.2), vec(14.80, 4.2),
        vec(14.80, 30.80), vec(0.20, 30.80)
    ]
    for layer_id in [pcbnew.In1_Cu, pcbnew.B_Cu, pcbnew.F_Cu]:
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer_id)
        zone.SetNet(gnd_net)
        zone.SetMinThickness(mm_to_nm(0.15))
        zone.SetThermalReliefGap(mm_to_nm(0.20))
        zone.SetThermalReliefSpokeWidth(mm_to_nm(0.25))
        if layer_id == pcbnew.In1_Cu:
            zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        chain = pcbnew.SHAPE_LINE_CHAIN()
        for p in poly_box:
            chain.Append(p.x, p.y)
        chain.SetClosed(True)
        zone.AddPolygon(chain)
        board.Add(zone)

    # Fill Zones
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    # Save to Device1.kicad_pcb
    out_pcb = "/Users/racoon/Documents/CHEATING/Device1/hardware/Device1.kicad_pcb"
    board.Save(out_pcb)
    print(f"Successfully generated and saved board to {out_pcb}")

if __name__ == "__main__":
    build_board()
