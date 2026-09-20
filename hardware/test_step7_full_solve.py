import sys, os
import pcbnew

def mm_to_nm(mm): return int(mm * 1e6)
def nm_to_mm(nm): return nm / 1e6
def vec(x, y): return pcbnew.VECTOR2I(mm_to_nm(x), mm_to_nm(y))

# Load the verified step 0-5 board
board = pcbnew.LoadBoard('hardware/test_step.kicad_pcb')
raw_nets = board.GetNetsByName()
nets = {str(k).lstrip('/'): v for k, v in raw_nets.items()}

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

print("Building Step 6 & 7 Unified Clean Routing...")

# ==================== STEP 6 ====================
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
add_via(10.00, 19.25, nets['CHG_STAT'])
add_track(10.00, 19.25, 10.863, 19.25, pcbnew.F_Cu, nets['CHG_STAT'], 0.15)
route_points([(11.80, 12.75), (11.80, 17.80), (10.00, 18.60), (10.00, 19.25)], pcbnew.B_Cu, nets['CHG_STAT'], 0.15)

# 9. VBUS_5V: TP_VBUS, C18, C10, U2.4, Q2.1, D1.2
add_via(13.50, 12.50, nets['VBUS_5V'])
add_track(13.50, 4.20, 13.50, 12.50, pcbnew.B_Cu, nets['VBUS_5V'], 0.25)
route_points([(13.50, 12.50), (12.72, 12.50), (12.72, 13.50), (12.72, 15.50)], pcbnew.F_Cu, nets['VBUS_5V'], 0.25)
route_points([(12.72, 15.50), (12.72, 16.20), (14.20, 16.20), (14.20, 21.15), (13.137, 21.15)], pcbnew.F_Cu, nets['VBUS_5V'], 0.25)
add_via(14.20, 21.15, nets['VBUS_5V'])
add_via(11.062, 23.25, nets['VBUS_5V'])
add_via(8.55, 20.50, nets['VBUS_5V'])
add_track(8.55, 20.50, 8.55, 21.20, pcbnew.F_Cu, nets['VBUS_5V'], 0.25)
route_points([(8.55, 20.50), (8.55, 23.25), (11.062, 23.25)], pcbnew.B_Cu, nets['VBUS_5V'], 0.25)
add_track(14.20, 21.15, 11.062, 23.25, pcbnew.In2_Cu, nets['VBUS_5V'], 0.25)

# ==================== STEP 7 ====================
# 10. LED_R: R6.2 (11.01, 27.50) to D2.1 (12.40, 28.15) on F.Cu
route_points([(11.01, 27.50), (11.80, 27.50), (11.80, 28.15), (12.40, 28.15)], pcbnew.F_Cu, nets['LED_R'], 0.15)

# 11. LED_B: R7.2 (11.01, 29.20) to D2.2 (12.40, 28.85) on F.Cu
route_points([(11.01, 29.20), (11.80, 29.20), (11.80, 28.85), (12.40, 28.85)], pcbnew.F_Cu, nets['LED_B'], 0.15)

# 12. LED_B_DRV: U1.13 (10.250, 9.562) to R7.1 (9.99, 29.20)
add_track(10.25, 9.562, 10.25, 8.80, pcbnew.F_Cu, nets['LED_B_DRV'], 0.15)
add_track(10.25, 8.80, 11.40, 8.80, pcbnew.F_Cu, nets['LED_B_DRV'], 0.15)
add_via(11.40, 8.80, nets['LED_B_DRV'])
add_via(10.50, 28.50, nets['LED_B_DRV'])
add_track(10.50, 28.50, 9.99, 29.20, pcbnew.F_Cu, nets['LED_B_DRV'], 0.15)
route_points([(11.40, 8.80), (11.40, 16.50), (11.40, 18.00), (11.40, 28.00), (10.50, 28.50)], pcbnew.B_Cu, nets['LED_B_DRV'], 0.15)

# 13. LED_R_DRV: U1.12 (10.938, 10.25) to R6.1 (9.99, 27.50)
add_track(10.938, 10.25, 12.20, 10.25, pcbnew.F_Cu, nets['LED_R_DRV'], 0.15)
add_via(12.20, 10.25, nets['LED_R_DRV'])
add_via(10.50, 26.80, nets['LED_R_DRV'])
add_track(10.50, 26.80, 9.99, 27.50, pcbnew.F_Cu, nets['LED_R_DRV'], 0.15)
route_points([(12.20, 10.25), (12.15, 12.00), (12.15, 18.00), (12.15, 26.50), (10.50, 26.80)], pcbnew.B_Cu, nets['LED_R_DRV'], 0.15)

# 14. MIC_WS: U1.32 (4.062, 13.75) to MK1.1 (6.600, 27.136)
add_track(4.062, 13.75, 3.20, 13.75, pcbnew.F_Cu, nets['MIC_WS'], 0.15)
add_track(3.20, 13.75, 3.20, 13.30, pcbnew.F_Cu, nets['MIC_WS'], 0.15)
add_via(3.20, 13.30, nets['MIC_WS'])
add_via(6.60, 26.20, nets['MIC_WS'])
add_track(6.60, 26.20, 6.60, 27.136, pcbnew.F_Cu, nets['MIC_WS'], 0.15)
route_points([(3.20, 13.30), (0.45, 13.30), (0.45, 26.20), (6.60, 26.20)], pcbnew.B_Cu, nets['MIC_WS'], 0.15)

# 15. MIC_SD: U1.33 (4.062, 14.25) to MK1.6 (7.500, 27.136)
add_track(4.062, 14.25, 3.20, 14.25, pcbnew.F_Cu, nets['MIC_SD'], 0.15)
add_track(3.20, 14.25, 3.20, 15.00, pcbnew.F_Cu, nets['MIC_SD'], 0.15)
add_via(3.20, 15.00, nets['MIC_SD'])
add_via(7.50, 26.20, nets['MIC_SD'])
add_track(7.50, 26.20, 7.50, 27.136, pcbnew.F_Cu, nets['MIC_SD'], 0.15)
route_points([(3.20, 15.00), (0.75, 15.00), (0.75, 26.00), (7.50, 26.00), (7.50, 26.20)], pcbnew.B_Cu, nets['MIC_SD'], 0.15)

# 16. MIC_SCK: U1.17 (8.250, 9.562) to MK1.4 (8.400, 27.958)
add_via(8.25, 8.80, nets['MIC_SCK'])
add_track(8.25, 9.562, 8.25, 8.80, pcbnew.F_Cu, nets['MIC_SCK'], 0.15)
add_via(8.40, 27.20, nets['MIC_SCK'])
add_track(8.40, 27.20, 8.40, 27.958, pcbnew.F_Cu, nets['MIC_SCK'], 0.15)
route_points([(8.25, 8.80), (9.20, 9.50), (9.20, 16.50), (8.20, 17.50), (8.20, 26.50), (8.40, 27.20)], pcbnew.In2_Cu, nets['MIC_SCK'], 0.15)

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
board.Save('hardware/test_step7_solved.kicad_pcb')
print("Successfully generated and saved test_step7_solved.kicad_pcb")
