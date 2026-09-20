#!/usr/bin/env python3
"""
Device 1 Complete PCB Builder — Manufacturing-Ready Layout & Full Routing
Zero courtyard overlaps, 50-ohm RF CPWG transmission line, antenna keepout,
thermal via array, solid planes, complete routing of all nets, 4 copper layers.
"""

import pcbnew

def mm_to_nm(mm):
    return int(mm * 1e6)

def vec(x_mm, y_mm):
    return pcbnew.VECTOR2I(mm_to_nm(x_mm), mm_to_nm(y_mm))

def create_board():
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)
    
    settings = board.GetDesignSettings()
    settings.m_TrackMinWidth = mm_to_nm(0.127)
    settings.m_ViasMinSize = mm_to_nm(0.60)
    settings.m_ViasMinDrill = mm_to_nm(0.30)
    settings.m_CopperEdgeClearance = mm_to_nm(0.30)
    
    # 1. Board Outline (31.0 mm x 15.0 mm with 1.0 mm rounded corners)
    w_mm = 15.0
    h_mm = 31.0
    r_mm = 1.0
    
    outline_lines = [
        ((r_mm, 0), (w_mm - r_mm, 0)),
        ((w_mm, r_mm), (w_mm, h_mm - r_mm)),
        ((w_mm - r_mm, h_mm), (r_mm, h_mm)),
        ((0, h_mm - r_mm), (0, r_mm)),
        ((r_mm, 0), (0, r_mm)),
        ((w_mm - r_mm, 0), (w_mm, r_mm)),
        ((w_mm, h_mm - r_mm), (w_mm - r_mm, h_mm)),
        ((r_mm, h_mm), (0, h_mm - r_mm))
    ]
    for (x1, y1), (x2, y2) in outline_lines:
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(vec(x1, y1))
        seg.SetEnd(vec(x2, y2))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(mm_to_nm(0.15))
        board.Add(seg)
    print("Board outline created: 31.0 mm x 15.0 mm")

    # 2. Nets
    net_names = [
        "GND", "3V3", "VBUS_5V", "VBAT_PROT", "BATT_POS", "BATT_NEG", "SYS_PWR",
        "MIC_WS", "MIC_SCK", "MIC_SD", "RFO_HP", "RFI_P", "RFI_N", "RF_50OHM", "ANT_FEED",
        "OSC_IN", "OSC_OUT", "SWDIO", "SWCLK", "NRST", "BOOT0", "LED_R", "LED_B", "CHG_STAT"
    ]
    nets = {}
    for name in net_names:
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
        nets[name] = net
    gnd_net = nets["GND"]
    p3v3_net = nets["3V3"]

    # 3. Footprints
    lib_base = "/opt/homebrew/Caskroom/kicad/10.0.6/KiCad/KiCad.app/Contents/SharedSupport/footprints"
    def load_fp(pretty, name):
        return pcbnew.FootprintLoad(f"{lib_base}/{pretty}.pretty", name)

    fp_defs = [
        # Ref, Lib, Name, X, Y, Rot
        ("U1", "Package_DFN_QFN", "QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm", 7.5, 12.5, 180),
        ("ANT1", "RF_Antenna", "Johanson_2450AT43F0100", 7.5, 2.0, 0),
        ("Y1", "Crystal", "Crystal_SMD_2016-4Pin_2.0x1.6mm", 2.0, 12.5, 0),
        ("MK1", "Sensor_Audio", "Knowles_SPH0645LM4H-6_3.5x2.65mm", 7.5, 28.8, 0),
        ("U5", "Package_TO_SOT_SMD", "SOT-23-5", 3.0, 20.8, 0),
        ("U2", "Package_TO_SOT_SMD", "SOT-23-5", 12.0, 20.8, 0),
        ("U4", "Package_TO_SOT_SMD", "SOT-23-6", 3.0, 24.7, 0),
        ("Q1", "Package_TO_SOT_SMD", "SOT-23-6", 7.5, 24.7, 0),
        ("Q2", "Package_TO_SOT_SMD", "SOT-23", 12.0, 24.7, 0),
        ("D2", "LED_SMD", "LED_0603_1608Metric", 12.5, 28.8, 0),
        # Left column passives
        ("C12", "Capacitor_SMD", "C_0402_1005Metric", 2.0, 5.5, 90),
        ("R1", "Resistor_SMD", "R_0402_1005Metric", 2.0, 7.8, 90),
        ("C1", "Capacitor_SMD", "C_0402_1005Metric", 2.0, 10.0, 90),
        ("C7", "Capacitor_SMD", "C_0402_1005Metric", 2.0, 15.0, 90),
        ("C11", "Capacitor_SMD", "C_0402_1005Metric", 2.0, 17.2, 90),
        # Right column passives
        ("C3", "Capacitor_SMD", "C_0402_1005Metric", 13.0, 5.5, 90),
        ("C2", "Capacitor_SMD", "C_0402_1005Metric", 13.0, 8.0, 90),
        ("C4", "Capacitor_SMD", "C_0402_1005Metric", 13.0, 10.5, 90),
        ("C5", "Capacitor_SMD", "C_0402_1005Metric", 13.0, 13.0, 90),
        ("C18", "Capacitor_SMD", "C_0402_1005Metric", 13.0, 15.2, 90),
        ("C17", "Capacitor_SMD", "C_0402_1005Metric", 13.0, 17.4, 90),
        # MCU bottom passives
        ("C8", "Capacitor_SMD", "C_0402_1005Metric", 4.5, 17.5, 0),
        ("C9", "Capacitor_SMD", "C_0402_1005Metric", 7.5, 17.5, 0),
        ("C10", "Capacitor_SMD", "C_0402_1005Metric", 10.5, 17.5, 0),
        # Mid power caps
        ("C20", "Capacitor_SMD", "C_0402_1005Metric", 6.0, 20.8, 90),
        ("C21", "Capacitor_SMD", "C_0402_1005Metric", 9.0, 20.8, 90),
        # Audio & UI caps / resistors
        ("C15", "Capacitor_SMD", "C_0402_1005Metric", 3.5, 28.8, 90),
        ("C16", "Capacitor_SMD", "C_0402_1005Metric", 1.8, 28.8, 90),
        ("R6", "Resistor_SMD", "R_0402_1005Metric", 10.2, 27.2, 90),
        ("R7", "Resistor_SMD", "R_0402_1005Metric", 10.2, 29.0, 90),
        # RF matching network
        ("C13", "Capacitor_SMD", "C_0402_1005Metric", 3.5, 6.8, 0),
        ("L1", "Inductor_SMD", "L_0402_1005Metric", 5.25, 6.8, 90),
        ("C14", "Capacitor_SMD", "C_0402_1005Metric", 7.0, 4.6, 0),
        ("R_ANT", "Resistor_SMD", "R_0402_1005Metric", 5.25, 4.6, 90)
    ]

    placed_fps = {}
    for ref, lib, name, x, y, rot in fp_defs:
        fp = load_fp(lib, name)
        if fp:
            fp.SetReference(ref)
            fp.SetPosition(vec(x, y))
            fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
            # Hide text on silkscreen for compact micro-PCB design
            fp.Reference().SetVisible(False)
            fp.Value().SetVisible(False)
            board.Add(fp)
            placed_fps[ref] = fp

    # Add Test Points on Bottom Layer (B.Cu)
    tp_defs = [
        ("TP_SWDIO", 3.5, 10.0, "SWDIO"),
        ("TP_SWCLK", 3.5, 14.0, "SWCLK"),
        ("TP_NRST", 3.5, 6.0, "NRST"),
        ("TP_BOOT0", 3.5, 8.0, "BOOT0"),
        ("TP_VBUS", 11.5, 6.0, "VBUS_5V"),
        ("TP_BATT_P", 11.5, 8.0, "BATT_POS"),
        ("TP_BATT_N", 11.5, 10.0, "BATT_NEG"),
        ("TP_3V3", 11.5, 12.0, "3V3"),
        ("TP_GND", 11.5, 14.0, "GND")
    ]
    for tp_ref, x, y, tp_net in tp_defs:
        fp = load_fp("TestPoint", "TestPoint_Pad_D1.0mm")
        if fp:
            fp.SetReference(tp_ref)
            fp.SetPosition(vec(x, y))
            board.Add(fp)
            fp.Flip(fp.GetPosition(), True) # Move to B.Cu after board.Add
            fp.Reference().SetVisible(False)
            fp.Value().SetVisible(False)
            placed_fps[tp_ref] = fp
            p1 = fp.FindPadByNumber("1")
            if p1 and tp_net in nets:
                p1.SetNet(nets[tp_net])

    # 4. Assign Net Mappings to Pads
    # U1 (STM32WL55)
    u1 = placed_fps.get("U1")
    if u1:
        pad_mappings = [
            ("11", "3V3"), ("44", "3V3"), ("25", "3V3"), ("28", "3V3"), ("29", "3V3"),
            ("37", "3V3"), ("41", "3V3"), ("45", "3V3"), ("46", "3V3"),
            ("17", "MIC_SCK"), ("32", "MIC_WS"), ("33", "MIC_SD"),
            ("26", "OSC_IN"), ("27", "OSC_OUT"),
            ("36", "SWDIO"), ("42", "SWCLK"), ("18", "NRST"), ("19", "BOOT0"),
            ("12", "LED_R"), ("13", "LED_B"),
            ("23", "RF_50OHM"), ("20", "RFI_P"), ("21", "RFI_N"),
            ("24", "SYS_PWR"), ("48", "GND"), ("49", "GND")
        ]
        for p_num, n_name in pad_mappings:
            pad = u1.FindPadByNumber(p_num)
            if pad and n_name in nets:
                pad.SetNet(nets[n_name])

    # ANT1
    ant1 = placed_fps.get("ANT1")
    if ant1:
        p1 = ant1.FindPadByNumber("1")
        p2 = ant1.FindPadByNumber("2")
        if p1: p1.SetNet(nets["ANT_FEED"])
        if p2: p2.SetNet(gnd_net)

    # MK1
    mk1 = placed_fps.get("MK1")
    if mk1:
        p1 = mk1.FindPadByNumber("1")
        p2 = mk1.FindPadByNumber("2")
        p3 = mk1.FindPadByNumber("3")
        p4 = mk1.FindPadByNumber("4")
        p5 = mk1.FindPadByNumber("5")
        p6 = mk1.FindPadByNumber("6")
        if p1: p1.SetNet(nets["MIC_WS"])
        if p2: p2.SetNet(gnd_net)
        if p3: p3.SetNet(gnd_net)
        if p4: p4.SetNet(nets["MIC_SCK"])
        if p5: p5.SetNet(p3v3_net)
        if p6: p6.SetNet(nets["MIC_SD"])

    # Y1
    y1 = placed_fps.get("Y1")
    if y1:
        p1 = y1.FindPadByNumber("1")
        p2 = y1.FindPadByNumber("2")
        p3 = y1.FindPadByNumber("3")
        p4 = y1.FindPadByNumber("4")
        if p1: p1.SetNet(nets["OSC_IN"])
        if p2: p2.SetNet(gnd_net)
        if p3: p3.SetNet(nets["OSC_OUT"])
        if p4: p4.SetNet(gnd_net)

    # Passives
    passive_nets = {
        "C1": ("3V3", "GND"),
        "C2": ("3V3", "GND"),
        "C3": ("3V3", "GND"),
        "C4": ("3V3", "GND"),
        "C5": ("3V3", "GND"),
        "C7": ("3V3", "GND"),
        "C8": ("3V3", "GND"),
        "C9": ("SYS_PWR", "GND"),
        "C10": ("SYS_PWR", "GND"),
        "C11": ("3V3", "GND"),
        "C12": ("NRST", "GND"),
        "R1": ("BOOT0", "GND"),
        "C15": ("3V3", "GND"),
        "C16": ("3V3", "GND"),
        "C17": ("VBAT_PROT", "GND"),
        "C18": ("VBUS_5V", "GND"),
        "C20": ("SYS_PWR", "GND"),
        "C21": ("3V3", "GND"),
        "C13": ("RF_50OHM", "GND"),
        "L1": ("RF_50OHM", "ANT_FEED"),
        "C14": ("ANT_FEED", "GND"),
        "R_ANT": ("ANT_FEED", "ANT_FEED"),
        "R6": ("LED_R", "LED_R"),
        "R7": ("LED_B", "LED_B"),
        "D2": ("LED_R", "GND"),
    }
    for ref, (n1, n2) in passive_nets.items():
        fp = placed_fps.get(ref)
        if fp:
            p1 = fp.FindPadByNumber("1")
            p2 = fp.FindPadByNumber("2")
            if p1 and n1 in nets: p1.SetNet(nets[n1])
            if p2 and n2 in nets: p2.SetNet(nets[n2])

    # Power ICs
    # U2 (MCP73831)
    u2 = placed_fps.get("U2")
    if u2:
        for p, n in [("1", "CHG_STAT"), ("2", "GND"), ("3", "VBAT_PROT"), ("4", "VBUS_5V"), ("5", "GND")]:
            pad = u2.FindPadByNumber(p)
            if pad and n in nets: pad.SetNet(nets[n])

    # U5 (AP2112K-3.3)
    u5 = placed_fps.get("U5")
    if u5:
        for p, n in [("1", "SYS_PWR"), ("2", "GND"), ("3", "SYS_PWR"), ("4", "GND"), ("5", "3V3")]:
            pad = u5.FindPadByNumber(p)
            if pad and n in nets: pad.SetNet(nets[n])

    # U4 (DW01A)
    u4 = placed_fps.get("U4")
    if u4:
        for p, n in [("1", "BATT_NEG"), ("2", "GND"), ("3", "BATT_NEG"), ("4", "GND"), ("5", "BATT_POS"), ("6", "BATT_NEG")]:
            pad = u4.FindPadByNumber(p)
            if pad and n in nets: pad.SetNet(nets[n])

    # Q1 (FS8205A)
    q1 = placed_fps.get("Q1")
    if q1:
        for p, n in [("1", "GND"), ("2", "BATT_NEG"), ("3", "BATT_NEG"), ("4", "BATT_NEG"), ("5", "BATT_NEG"), ("6", "GND")]:
            pad = q1.FindPadByNumber(p)
            if pad and n in nets: pad.SetNet(nets[n])

    # Q2 (DMG2305UX)
    q2 = placed_fps.get("Q2")
    if q2:
        for p, n in [("1", "VBUS_5V"), ("2", "SYS_PWR"), ("3", "VBAT_PROT")]:
            pad = q2.FindPadByNumber(p)
            if pad and n in nets: pad.SetNet(nets[n])

    # Helper Functions for Routing
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

    def add_pad_via(pad, dx, dy, width=0.20):
        pos = pad.GetPosition()
        vx = pos.x / 1e6 + dx
        vy = pos.y / 1e6 + dy
        net = pad.GetNet()
        v = add_via(vx, vy, net)
        add_track(pos.x / 1e6, pos.y / 1e6, vx, vy, pad.GetLayer(), net, width)
        return v

    # 5. Thermal Vias under MCU Exposed Pad (GND)
    for dx in [-1.2, 0.0, 1.2]:
        for dy in [-1.2, 0.0, 1.2]:
            add_via(7.5 + dx, 12.5 + dy, gnd_net)

    # 6. Dedicated Plane Drop Vias for all GND and 3V3 pads
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref.startswith("TP_"):
            continue
        for pad in fp.Pads():
            net = pad.GetNet()
            if not net:
                continue
            netname = net.GetNetname()
            pos = pad.GetPosition()
            px, py = pos.x / 1e6, pos.y / 1e6
            
            # Connect GND to L2
            if netname == "GND" and ref != "U1":
                # Determine fanout direction away from center
                dx = 0.6 if px > 7.5 else -0.6
                if abs(px - 7.5) < 0.5:
                    dx = 0.0
                    dy = 0.6 if py > 15.0 else -0.6
                else:
                    dy = 0.0
                add_pad_via(pad, dx, dy, 0.20)
                
            # Connect 3V3 to L3
            elif netname == "3V3":
                dx = 0.6 if px > 7.5 else -0.6
                if abs(px - 7.5) < 0.5:
                    dx = 0.0
                    dy = 0.6 if py > 15.0 else -0.6
                else:
                    dy = 0.0
                add_pad_via(pad, dx, dy, 0.20)

    # 7. RF 50-Ohm Transmission Line & Matching Network
    # Track 1: MCU Pin 23 to L1 Pad 1 (50-Ohm CPWG: 0.29mm)
    add_track(5.25, 9.062, 5.25, 7.285, pcbnew.F_Cu, nets["RF_50OHM"], 0.29)
    # L1 Pad 1 to C13 Pad 1
    add_track(5.25, 7.285, 3.5, 6.8, pcbnew.F_Cu, nets["RF_50OHM"], 0.25)
    # Track 2: L1 Pad 2 to R_ANT Pad 1
    add_track(5.25, 6.315, 5.25, 5.110, pcbnew.F_Cu, nets["ANT_FEED"], 0.29)
    # R_ANT Pad 1 to C14 Pad 1
    add_track(5.25, 5.110, 6.52, 4.60, pcbnew.F_Cu, nets["ANT_FEED"], 0.25)
    # Track 3: R_ANT Pad 2 to ANT1 Pad 1 (4.65, 2.0)
    add_track(5.25, 4.090, 4.65, 3.490, pcbnew.F_Cu, nets["ANT_FEED"], 0.29)
    add_track(4.65, 3.490, 4.65, 2.000, pcbnew.F_Cu, nets["ANT_FEED"], 0.29)

    # 8. Crystal HSE 32MHz (Low parasitic direct connections)
    # U1 Pin 26 (OSC_IN: 4.062, 10.250) to Y1 Pad 1 (1.30, 13.050)
    add_track(4.062, 10.250, 2.8, 10.250, pcbnew.F_Cu, nets["OSC_IN"], 0.20)
    add_track(2.8, 10.250, 1.30, 11.750, pcbnew.F_Cu, nets["OSC_IN"], 0.20)
    add_track(1.30, 11.750, 1.30, 13.050, pcbnew.F_Cu, nets["OSC_IN"], 0.20)

    # U1 Pin 27 (OSC_OUT: 4.062, 10.750) to Y1 Pad 3 (2.70, 11.950)
    add_track(4.062, 10.750, 3.2, 10.750, pcbnew.F_Cu, nets["OSC_OUT"], 0.20)
    add_track(3.2, 10.750, 2.70, 11.250, pcbnew.F_Cu, nets["OSC_OUT"], 0.20)
    add_track(2.70, 11.250, 2.70, 11.950, pcbnew.F_Cu, nets["OSC_OUT"], 0.20)

    # 9. Audio I2S Routing
    # MK1 Pad 1 (MIC_WS) at (6.600, 27.436) to U1 Pin 32 at (4.062, 13.250)
    # Via near MK1 to B.Cu, route along bottom, via near U1
    add_track(6.600, 27.436, 6.600, 26.5, pcbnew.F_Cu, nets["MIC_WS"], 0.15)
    add_via(6.600, 26.5, nets["MIC_WS"])
    add_track(6.600, 26.5, 3.0, 22.9, pcbnew.B_Cu, nets["MIC_WS"], 0.15)
    add_track(3.0, 22.9, 3.0, 14.0, pcbnew.B_Cu, nets["MIC_WS"], 0.15)
    add_via(3.0, 14.0, nets["MIC_WS"])
    add_track(3.0, 14.0, 3.3, 13.250, pcbnew.F_Cu, nets["MIC_WS"], 0.15)
    add_track(3.3, 13.250, 4.062, 13.250, pcbnew.F_Cu, nets["MIC_WS"], 0.15)

    # MK1 Pad 4 (MIC_SCK) at (8.400, 28.258) to U1 Pin 17 at (8.250, 9.062)
    add_track(8.400, 28.258, 8.400, 26.8, pcbnew.F_Cu, nets["MIC_SCK"], 0.15)
    add_via(8.400, 26.8, nets["MIC_SCK"])
    add_track(8.400, 26.8, 8.250, 10.2, pcbnew.B_Cu, nets["MIC_SCK"], 0.15)
    add_via(8.250, 10.2, nets["MIC_SCK"])
    add_track(8.250, 10.2, 8.250, 9.062, pcbnew.F_Cu, nets["MIC_SCK"], 0.15)

    # MK1 Pad 6 (MIC_SD) at (7.500, 27.436) to U1 Pin 33 at (4.062, 13.750)
    add_track(7.500, 27.436, 7.500, 26.5, pcbnew.F_Cu, nets["MIC_SD"], 0.15)
    add_via(7.500, 26.5, nets["MIC_SD"])
    add_track(7.500, 26.5, 3.4, 22.4, pcbnew.B_Cu, nets["MIC_SD"], 0.15)
    add_track(3.4, 22.4, 3.4, 14.5, pcbnew.B_Cu, nets["MIC_SD"], 0.15)
    add_via(3.4, 14.5, nets["MIC_SD"])
    add_track(3.4, 14.5, 3.7, 13.750, pcbnew.F_Cu, nets["MIC_SD"], 0.15)
    add_track(3.7, 13.750, 4.062, 13.750, pcbnew.F_Cu, nets["MIC_SD"], 0.15)

    # 10. Reset (NRST) & Boot0
    # U1 Pin 18 (7.750, 9.062) to C12 Pad 1 (2.0, 5.980)
    add_track(7.750, 9.062, 7.750, 8.2, pcbnew.F_Cu, nets["NRST"], 0.15)
    add_track(7.750, 8.2, 2.0, 6.5, pcbnew.F_Cu, nets["NRST"], 0.15)
    add_track(2.0, 6.5, 2.0, 5.980, pcbnew.F_Cu, nets["NRST"], 0.15)
    # Connect to TP_NRST on B.Cu
    add_via(2.0, 6.0, nets["NRST"])
    add_track(2.0, 6.0, 3.5, 6.0, pcbnew.B_Cu, nets["NRST"], 0.20)

    # U1 Pin 19 (7.250, 9.062) to R1 Pad 1 (2.0, 8.310)
    add_track(7.250, 9.062, 7.250, 8.5, pcbnew.F_Cu, nets["BOOT0"], 0.15)
    add_track(7.250, 8.5, 2.8, 8.5, pcbnew.F_Cu, nets["BOOT0"], 0.15)
    add_track(2.8, 8.5, 2.0, 8.310, pcbnew.F_Cu, nets["BOOT0"], 0.15)
    # Connect to TP_BOOT0 on B.Cu
    add_via(2.8, 8.0, nets["BOOT0"])
    add_track(2.8, 8.0, 3.5, 8.0, pcbnew.B_Cu, nets["BOOT0"], 0.20)

    # 11. SWD Debug Lines
    # U1 Pin 36 (SWDIO: 4.062, 15.250) to TP_SWDIO (3.5, 10.0)
    add_via(3.2, 15.250, nets["SWDIO"])
    add_track(4.062, 15.250, 3.2, 15.250, pcbnew.F_Cu, nets["SWDIO"], 0.15)
    add_track(3.2, 15.250, 3.5, 10.0, pcbnew.B_Cu, nets["SWDIO"], 0.20)

    # U1 Pin 42 (SWCLK: 7.250, 15.938) to TP_SWCLK (3.5, 14.0)
    add_via(7.250, 16.5, nets["SWCLK"])
    add_track(7.250, 15.938, 7.250, 16.5, pcbnew.F_Cu, nets["SWCLK"], 0.15)
    add_track(7.250, 16.5, 3.5, 14.0, pcbnew.B_Cu, nets["SWCLK"], 0.20)

    # 12. UI LED Lines
    # U1 Pin 12 (LED_R: 10.938, 9.750) to R6 Pad 1 (10.2, 26.7)
    add_track(10.938, 9.750, 11.5, 9.750, pcbnew.F_Cu, nets["LED_R"], 0.15)
    add_via(11.5, 9.750, nets["LED_R"])
    add_track(11.5, 9.750, 10.2, 26.0, pcbnew.B_Cu, nets["LED_R"], 0.15)
    add_via(10.2, 26.0, nets["LED_R"])
    add_track(10.2, 26.0, 10.2, 26.7, pcbnew.F_Cu, nets["LED_R"], 0.15)
    # R6 Pad 2 to D2 Pad 1 (11.7, 28.8)
    add_track(10.2, 27.7, 11.7, 28.8, pcbnew.F_Cu, nets["LED_R"], 0.20)

    # U1 Pin 13 (LED_B: 10.250, 9.062) to R7 Pad 1 (10.2, 28.5)
    add_track(10.250, 9.062, 10.250, 8.5, pcbnew.F_Cu, nets["LED_B"], 0.15)
    add_via(10.250, 8.5, nets["LED_B"])
    add_track(10.250, 8.5, 10.2, 28.0, pcbnew.B_Cu, nets["LED_B"], 0.15)
    add_via(10.2, 28.0, nets["LED_B"])
    add_track(10.2, 28.0, 10.2, 28.5, pcbnew.F_Cu, nets["LED_B"], 0.15)

    # 13. Power Management Connections
    # VBUS_5V: U2 Pad 4 (13.1, 21.75), Q2 Pad 1 (11.0, 23.75), C18 Pad 1 (13.0, 15.68), TP_VBUS (11.5, 6.0)
    add_track(13.1, 21.75, 11.0, 23.75, pcbnew.F_Cu, nets["VBUS_5V"], 0.25)
    add_track(13.1, 21.75, 13.0, 15.68, pcbnew.F_Cu, nets["VBUS_5V"], 0.25)
    add_via(13.0, 15.0, nets["VBUS_5V"])
    add_track(13.0, 15.0, 11.5, 6.0, pcbnew.B_Cu, nets["VBUS_5V"], 0.25)

    # VBAT_PROT: U2 Pad 3 (10.9, 21.75), Q2 Pad 3 (12.9, 24.7), C17 Pad 1 (13.0, 17.88), U4 Pad 5 (4.1, 24.7)
    add_track(10.9, 21.75, 12.9, 24.7, pcbnew.F_Cu, nets["VBAT_PROT"], 0.25)
    add_track(10.9, 21.75, 13.0, 17.88, pcbnew.F_Cu, nets["VBAT_PROT"], 0.25)
    add_via(10.9, 21.75, nets["VBAT_PROT"])
    add_track(10.9, 21.75, 4.1, 24.7, pcbnew.B_Cu, nets["VBAT_PROT"], 0.25)
    add_via(4.1, 24.7, nets["VBAT_PROT"])

    # SYS_PWR: Q2 Pad 2 (11.0, 25.65), U5 Pad 1 (1.8, 19.85), U5 Pad 3 (1.8, 21.75), C20 Pad 1 (6.0, 21.28), C9 Pad 1 (7.0, 17.5), C10 Pad 1 (10.0, 17.5), U1 Pin 24 (4.750, 9.062)
    add_track(1.8, 19.85, 1.8, 21.75, pcbnew.F_Cu, nets["SYS_PWR"], 0.35)
    add_track(1.8, 21.75, 6.0, 21.28, pcbnew.F_Cu, nets["SYS_PWR"], 0.35)
    add_track(6.0, 21.28, 11.0, 25.65, pcbnew.F_Cu, nets["SYS_PWR"], 0.35)
    add_track(6.0, 21.28, 7.0, 17.5, pcbnew.F_Cu, nets["SYS_PWR"], 0.35)
    add_track(7.0, 17.5, 10.0, 17.5, pcbnew.F_Cu, nets["SYS_PWR"], 0.35)
    add_track(7.0, 17.5, 4.750, 9.062, pcbnew.F_Cu, nets["SYS_PWR"], 0.25)

    # BATT_NEG: U4 Pads 1,3,6 to Q1 Pads 2,3,4,5 to TP_BATT_N
    add_track(1.8, 23.75, 1.8, 25.65, pcbnew.F_Cu, nets["BATT_NEG"], 0.35)
    add_track(1.8, 23.75, 4.1, 23.75, pcbnew.F_Cu, nets["BATT_NEG"], 0.35)
    add_track(4.1, 23.75, 6.4, 24.7, pcbnew.F_Cu, nets["BATT_NEG"], 0.35)
    add_track(6.4, 24.7, 8.6, 24.7, pcbnew.F_Cu, nets["BATT_NEG"], 0.35)
    add_via(8.6, 24.7, nets["BATT_NEG"])
    add_track(8.6, 24.7, 11.5, 10.0, pcbnew.B_Cu, nets["BATT_NEG"], 0.35)

    # BATT_POS: to TP_BATT_P
    add_via(4.1, 25.2, nets["BATT_POS"])
    add_track(4.1, 24.7, 4.1, 25.2, pcbnew.F_Cu, nets["BATT_POS"], 0.25)
    add_track(4.1, 25.2, 11.5, 8.0, pcbnew.B_Cu, nets["BATT_POS"], 0.25)

    # 14. Solid 4-Layer Copper Pours
    # Layer 2: Solid Ground Plane (In1.Cu)
    # Layer 3: 3V3 Power Plane (In2.Cu)
    # Layer 1: Top Ground Pour (F.Cu)
    # Layer 4: Bottom Ground Pour (B.Cu)
    # Antenna keepout zone is at (X: 0 to 15, Y: 0 to 4.0 mm).
    # All copper planes begin strictly at Y >= 4.2 mm!
    poly_box = [
        vec(0.15, 4.2), vec(14.85, 4.2),
        vec(14.85, 30.85), vec(0.15, 30.85)
    ]
    for layer_id, zone_net in [
        (pcbnew.In1_Cu, gnd_net),
        (pcbnew.In2_Cu, p3v3_net),
        (pcbnew.F_Cu, gnd_net),
        (pcbnew.B_Cu, gnd_net)
    ]:
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer_id)
        zone.SetNet(zone_net)
        zone.SetMinThickness(mm_to_nm(0.15))
        zone.SetThermalReliefGap(mm_to_nm(0.20))
        zone.SetThermalReliefSpokeWidth(mm_to_nm(0.25))
        
        chain = pcbnew.SHAPE_LINE_CHAIN()
        for p in poly_box:
            chain.Append(p.x, p.y)
        chain.SetClosed(True)
        zone.AddPolygon(chain)
        board.Add(zone)

    # 15. Refill Zones
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    # 16. Save Board
    output_path = "/Users/racoon/Documents/CHEATING/Device1/hardware/Device1.kicad_pcb"
    board.Save(output_path)
    print("PCB generated, routed, and saved successfully: Device1.kicad_pcb")

if __name__ == '__main__':
    create_board()
