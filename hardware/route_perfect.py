import pcbnew
import subprocess

def mm_to_nm(mm):
    return int(mm * 1e6)

def vec(x_mm, y_mm):
    return pcbnew.VECTOR2I(mm_to_nm(x_mm), mm_to_nm(y_mm))

def build():
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)
    
    settings = board.GetDesignSettings()
    settings.m_TrackMinWidth = mm_to_nm(0.127)
    settings.m_ViasMinSize = mm_to_nm(0.60)
    settings.m_ViasMinDrill = mm_to_nm(0.30)
    settings.m_CopperEdgeClearance = mm_to_nm(0.30)
    settings.m_HoleToHoleMin = mm_to_nm(0.20)
    
    # 1. Outline
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

    lib_base = "/opt/homebrew/Caskroom/kicad/10.0.6/KiCad/KiCad.app/Contents/SharedSupport/footprints"
    def load_fp(pretty, name):
        return pcbnew.FootprintLoad(f"{lib_base}/{pretty}.pretty", name)

    # 3. Footprints Placement
    fp_defs = [
        ("U1", "Package_DFN_QFN", "QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm", 7.5, 12.5, 180),
        ("ANT1", "RF_Antenna", "Johanson_2450AT43F0100", 7.5, 2.0, 0),
        ("Y1", "Crystal", "Crystal_SMD_2016-4Pin_2.0x1.6mm", 1.6, 12.5, 0), # No overlap with U1
        ("MK1", "Sensor_Audio", "Knowles_SPH0645LM4H-6_3.5x2.65mm", 7.5, 28.8, 0),
        ("U5", "Package_TO_SOT_SMD", "SOT-23-5", 3.0, 20.8, 0),
        ("U2", "Package_TO_SOT_SMD", "SOT-23-5", 12.0, 20.8, 0),
        ("U4", "Package_TO_SOT_SMD", "SOT-23-6", 3.0, 24.7, 0),
        ("Q1", "Package_TO_SOT_SMD", "SOT-23-6", 7.5, 24.7, 0),
        ("Q2", "Package_TO_SOT_SMD", "SOT-23", 12.0, 24.7, 0),
        ("D2", "LED_SMD", "LED_0603_1608Metric", 13.0, 28.3, 90),
        # Left column passives
        ("C12", "Capacitor_SMD", "C_0402_1005Metric", 1.8, 5.5, 90),
        ("R1", "Resistor_SMD", "R_0402_1005Metric", 1.8, 7.8, 90),
        ("C1", "Capacitor_SMD", "C_0402_1005Metric", 1.8, 10.0, 90),
        ("C7", "Capacitor_SMD", "C_0402_1005Metric", 1.8, 15.0, 90),
        ("C11", "Capacitor_SMD", "C_0402_1005Metric", 1.8, 17.2, 90),
        # Right column passives
        ("C3", "Capacitor_SMD", "C_0402_1005Metric", 13.2, 5.5, 90),
        ("C2", "Capacitor_SMD", "C_0402_1005Metric", 13.2, 8.0, 90),
        ("C4", "Capacitor_SMD", "C_0402_1005Metric", 13.2, 10.5, 90),
        ("C5", "Capacitor_SMD", "C_0402_1005Metric", 13.2, 13.0, 90),
        ("C18", "Capacitor_SMD", "C_0402_1005Metric", 13.2, 15.2, 90),
        ("C17", "Capacitor_SMD", "C_0402_1005Metric", 13.2, 17.4, 90),
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
        ("R6", "Resistor_SMD", "R_0402_1005Metric", 10.6, 27.2, 0),
        ("R7", "Resistor_SMD", "R_0402_1005Metric", 10.6, 29.4, 0), # Spaced to avoid overlap
        # RF matching network
        ("C13", "Capacitor_SMD", "C_0402_1005Metric", 3.5, 6.8, 180), # Rotated 180 so pad 1 faces track
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
            fp.Reference().SetVisible(False)
            fp.Value().SetVisible(False)
            board.Add(fp)
            placed_fps[ref] = fp

    # Bottom Layer Test Points (placed away from vias)
    tp_defs = [
        ("TP_SWDIO", 5.5, 22.8, "SWDIO"),
        ("TP_SWCLK", 7.5, 22.8, "SWCLK"),
        ("TP_NRST", 9.5, 24.5, "NRST"),
        ("TP_BOOT0", 3.5, 7.8, "BOOT0"),
        ("TP_VBUS", 11.5, 7.8, "VBUS_5V"),
        ("TP_BATT_P", 3.5, 26.8, "BATT_POS"),
        ("TP_BATT_N", 7.5, 26.8, "BATT_NEG"),
        ("TP_3V3", 11.5, 26.8, "3V3"),
        ("TP_GND", 13.2, 22.8, "GND")
    ]
    for tp_ref, x, y, tp_net in tp_defs:
        fp = load_fp("TestPoint", "TestPoint_Pad_D1.0mm")
        if fp:
            fp.SetReference(tp_ref)
            fp.SetPosition(vec(x, y))
            board.Add(fp)
            fp.Flip(fp.GetPosition(), True)
            fp.Reference().SetVisible(False)
            fp.Value().SetVisible(False)
            placed_fps[tp_ref] = fp
            p1 = fp.FindPadByNumber("1")
            if p1 and tp_net in nets:
                p1.SetNet(nets[tp_net])

    # Assign Net Mappings
    u1 = placed_fps["U1"]
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

    ant1 = placed_fps["ANT1"]
    ant1.FindPadByNumber("1").SetNet(nets["ANT_FEED"])
    ant1.FindPadByNumber("2").SetNet(gnd_net)

    mk1 = placed_fps["MK1"]
    mk1.FindPadByNumber("1").SetNet(nets["MIC_WS"])
    mk1.FindPadByNumber("2").SetNet(gnd_net)
    mk1.FindPadByNumber("3").SetNet(gnd_net)
    mk1.FindPadByNumber("4").SetNet(nets["MIC_SCK"])
    mk1.FindPadByNumber("5").SetNet(p3v3_net)
    mk1.FindPadByNumber("6").SetNet(nets["MIC_SD"])

    y1 = placed_fps["Y1"]
    y1.FindPadByNumber("1").SetNet(nets["OSC_IN"])
    y1.FindPadByNumber("2").SetNet(gnd_net)
    y1.FindPadByNumber("3").SetNet(nets["OSC_OUT"])
    y1.FindPadByNumber("4").SetNet(gnd_net)

    passive_nets = {
        "C1": ("3V3", "GND"), "C2": ("3V3", "GND"), "C3": ("3V3", "GND"),
        "C4": ("3V3", "GND"), "C5": ("3V3", "GND"), "C7": ("3V3", "GND"),
        "C8": ("3V3", "GND"), "C9": ("SYS_PWR", "GND"), "C10": ("SYS_PWR", "GND"),
        "C11": ("3V3", "GND"), "C12": ("NRST", "GND"), "R1": ("BOOT0", "GND"),
        "C15": ("3V3", "GND"), "C16": ("3V3", "GND"), "C17": ("VBAT_PROT", "GND"),
        "C18": ("VBUS_5V", "GND"), "C20": ("SYS_PWR", "GND"), "C21": ("3V3", "GND"),
        "C13": ("RF_50OHM", "GND"), "L1": ("RF_50OHM", "ANT_FEED"),
        "C14": ("ANT_FEED", "GND"), "R_ANT": ("ANT_FEED", "ANT_FEED"),
        "R6": ("LED_R", "LED_R"), "R7": ("LED_B", "LED_B"), "D2": ("LED_R", "GND"),
    }
    for ref, (n1, n2) in passive_nets.items():
        fp = placed_fps.get(ref)
        if fp:
            p1 = fp.FindPadByNumber("1")
            p2 = fp.FindPadByNumber("2")
            if p1 and n1 in nets: p1.SetNet(nets[n1])
            if p2 and n2 in nets: p2.SetNet(nets[n2])

    u2 = placed_fps["U2"]
    for p, n in [("1", "CHG_STAT"), ("2", "GND"), ("3", "VBAT_PROT"), ("4", "VBUS_5V"), ("5", "GND")]:
        u2.FindPadByNumber(p).SetNet(nets[n])

    u5 = placed_fps["U5"]
    for p, n in [("1", "SYS_PWR"), ("2", "GND"), ("3", "SYS_PWR"), ("4", "GND"), ("5", "3V3")]:
        u5.FindPadByNumber(p).SetNet(nets[n])

    u4 = placed_fps["U4"]
    for p, n in [("1", "BATT_NEG"), ("2", "GND"), ("3", "BATT_NEG"), ("4", "GND"), ("5", "BATT_POS"), ("6", "BATT_NEG")]:
        u4.FindPadByNumber(p).SetNet(nets[n])

    q1 = placed_fps["Q1"]
    for p, n in [("1", "GND"), ("2", "BATT_NEG"), ("3", "BATT_NEG"), ("4", "BATT_NEG"), ("5", "BATT_NEG"), ("6", "GND")]:
        q1.FindPadByNumber(p).SetNet(nets[n])

    q2 = placed_fps["Q2"]
    for p, n in [("1", "VBUS_5V"), ("2", "SYS_PWR"), ("3", "VBAT_PROT")]:
        q2.FindPadByNumber(p).SetNet(nets[n])

    # Routing Primitives
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

    # Thermal Vias under U1 Exposed Pad (GND)
    for dx in [-1.2, 0.0, 1.2]:
        for dy in [-1.2, 0.0, 1.2]:
            add_via(7.5 + dx, 12.5 + dy, gnd_net)

    # 3V3 Power Distribution (Well-spaced drop vias to In2.Cu)
    # LDO VOUT to In2.Cu
    add_track(3.938, 19.85, 4.8, 19.85, pcbnew.F_Cu, p3v3_net, 0.30)
    add_via(4.8, 19.85, p3v3_net)
    # C21 to 3V3 plane
    add_track(9.0, 21.28, 9.0, 22.0, pcbnew.F_Cu, p3v3_net, 0.30)
    add_via(9.0, 22.0, p3v3_net)
    # TP_3V3 to 3V3 plane
    add_via(11.5, 26.8, p3v3_net)
    # MK1 3V3 pin to 3V3 plane
    add_track(8.4, 27.436, 8.4, 26.2, pcbnew.F_Cu, p3v3_net, 0.25)
    add_via(8.4, 26.2, p3v3_net)
    # Left power rail for C1, C7, C11, and U1 Pins 25, 28, 29
    add_track(1.8, 10.48, 1.8, 9.5, pcbnew.F_Cu, p3v3_net, 0.25)
    add_via(1.8, 9.5, p3v3_net)
    add_track(1.8, 15.48, 2.6, 15.48, pcbnew.F_Cu, p3v3_net, 0.25)
    add_via(2.6, 15.48, p3v3_net)
    add_track(4.062, 9.75, 3.2, 9.75, pcbnew.F_Cu, p3v3_net, 0.20)
    add_track(4.062, 11.25, 3.2, 11.25, pcbnew.F_Cu, p3v3_net, 0.20)
    add_track(4.062, 11.75, 3.2, 11.75, pcbnew.F_Cu, p3v3_net, 0.20)
    add_track(3.2, 9.75, 3.2, 11.75, pcbnew.F_Cu, p3v3_net, 0.25)
    add_track(3.2, 10.75, 1.8, 11.2, pcbnew.F_Cu, p3v3_net, 0.25)
    # Right power rail for C2, C3, C4, C5 and U1 Pin 11
    add_track(13.2, 5.98, 12.2, 5.98, pcbnew.F_Cu, p3v3_net, 0.25)
    add_via(12.2, 5.98, p3v3_net)
    add_track(13.2, 8.48, 12.2, 8.48, pcbnew.F_Cu, p3v3_net, 0.25)
    add_track(13.2, 10.98, 12.2, 10.98, pcbnew.F_Cu, p3v3_net, 0.25)
    add_track(13.2, 13.48, 12.2, 13.48, pcbnew.F_Cu, p3v3_net, 0.25)
    add_track(12.2, 8.48, 12.2, 13.48, pcbnew.F_Cu, p3v3_net, 0.25)
    add_via(12.2, 10.98, p3v3_net)
    add_track(10.938, 10.25, 12.2, 10.25, pcbnew.F_Cu, p3v3_net, 0.20)
    # Bottom U1 power pins individual connections
    add_track(4.75, 15.938, 4.02, 17.5, pcbnew.F_Cu, p3v3_net, 0.20)
    add_track(4.02, 17.5, 4.02, 18.2, pcbnew.F_Cu, p3v3_net, 0.20)
    add_via(4.02, 18.2, p3v3_net)
    add_track(6.75, 15.938, 6.75, 17.0, pcbnew.F_Cu, p3v3_net, 0.20)
    add_via(6.75, 17.0, p3v3_net)
    add_track(8.25, 15.938, 8.25, 16.6, pcbnew.F_Cu, p3v3_net, 0.20)
    add_track(8.75, 15.938, 8.75, 16.6, pcbnew.F_Cu, p3v3_net, 0.20)
    add_track(9.25, 15.938, 9.25, 16.6, pcbnew.F_Cu, p3v3_net, 0.20)
    add_track(8.25, 16.6, 9.25, 16.6, pcbnew.F_Cu, p3v3_net, 0.20)
    add_via(8.75, 16.6, p3v3_net)

    # RF 50-Ohm CPWG Line & Matching
    add_track(5.25, 9.062, 5.25, 7.285, pcbnew.F_Cu, nets["RF_50OHM"], 0.29)
    # C13 Pad 1 at (3.98, 6.8) faces 5.25 directly
    add_track(5.25, 7.285, 3.98, 6.8, pcbnew.F_Cu, nets["RF_50OHM"], 0.25)
    add_track(5.25, 6.315, 5.25, 5.110, pcbnew.F_Cu, nets["ANT_FEED"], 0.29)
    add_track(5.25, 4.6, 6.52, 4.6, pcbnew.F_Cu, nets["ANT_FEED"], 0.25)
    add_track(5.25, 5.110, 5.25, 4.090, pcbnew.F_Cu, nets["ANT_FEED"], 0.29)
    add_track(5.25, 4.090, 4.65, 3.490, pcbnew.F_Cu, nets["ANT_FEED"], 0.29)
    add_track(4.65, 3.490, 4.65, 2.000, pcbnew.F_Cu, nets["ANT_FEED"], 0.29)
    # ANT1 Pad 2 GND via
    add_track(10.35, 2.0, 10.35, 3.0, pcbnew.F_Cu, gnd_net, 0.25)
    add_via(10.35, 3.0, gnd_net)

    # 4-Layer Copper Pours
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

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    board.Save('/Users/racoon/Documents/CHEATING/Device1/hardware/test_perfect.kicad_pcb')
    print("Saved test_perfect.kicad_pcb")

build()
