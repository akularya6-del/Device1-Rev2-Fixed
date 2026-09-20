import math

# Define all vias to be placed
vias = [
    # Center pad GND vias
    (6.5, 12.0, "GND"), (7.5, 12.0, "GND"), (8.5, 12.0, "GND"),
    (6.5, 13.0, "GND"), (7.5, 13.0, "GND"), (8.5, 13.0, "GND"),
    (6.5, 14.0, "GND"), (7.5, 14.0, "GND"), (8.5, 14.0, "GND"),
    
    # GND vias
    (0.6, 6.0, "GND"),   # C4
    (2.6, 5.2, "GND"),   # C14
    (2.6, 6.8, "GND"),   # C13
    (6.4, 6.8, "GND"),   # R1
    (8.5, 6.4, "GND"),   # C11
    (3.2, 9.2, "GND"),   # Y1.2
    (0.6, 8.0, "GND"),   # Y1.4
    (0.6, 12.2, "GND"),  # C7
    (0.6, 13.8, "GND"),  # C1
    (0.6, 17.0, "GND"),  # C9
    (0.8, 20.2, "GND"),  # U5.2
    (0.8, 24.2, "GND"),  # U4.2
    (5.5, 22.8, "GND"),  # Q1.1
    (5.8, 19.8, "GND"),  # C20.2
    (6.8, 19.8, "GND"),  # C21.2
    (8.8, 19.8, "GND"),  # C12.2
    (9.8, 20.2, "GND"),  # U2.2
    (14.2, 19.25, "GND"),# U2.5
    (12.68, 18.8, "GND"),# C17.2
    (14.4, 5.5, "GND"),  # C3
    (14.4, 7.5, "GND"),  # C2
    (14.4, 9.5, "GND"),  # C5
    (14.4, 11.5, "GND"), # C8
    (14.4, 13.5, "GND"), # C18
    (14.4, 15.5, "GND"), # C10
    (5.7, 27.96, "GND"), # MK1.2
    (8.16, 30.2, "GND"), # MK1.3
    (2.28, 29.5, "GND"), # C16.2
    (4.38, 29.5, "GND"), # C15.2
    (14.4, 28.15, "GND"),# D2.3
    (14.4, 28.85, "GND"),# D2.4
    (13.2, 22.8, "GND"), # TP_GND
    
    # 3V3 vias
    (4.8, 17.2, "3V3"),  # U5.5, U1.37, C20.1
    (6.3, 17.2, "3V3"), # U1.41, C21.1
    (8.75, 17.0, "3V3"), # U1.44, 45, 46
    (11.8, 11.2, "3V3"), # U1.11, C3, 2, 5, 8
    (3.2, 10.1, "3V3"), (3.2, 11.75, "3V3"),  # U1.25, U1.28
    (2.28, 13.0, "3V3"), # C1.1
    (8.4, 26.5, "3V3"),  # MK1.5
    (2.4, 27.0, "3V3"),  # C15.1, C16.1
    (13.5, 17.8, "3V3"), # TP_3V3
    
    # Signal vias
    (6.6, 6.0, "BOOT0"),
    (7.25, 4.0, "BOOT0"), # TP_BOOT0
    (8.5, 5.4, "NRST"),
    (9.8, 4.5, "NRST"),   # TP_NRST
    (8.0, 5.2, "TP_RF"),
    (9.8, 7.2, "TP_RF"),  # TP_RF
    (2.2, 15.75, "SWDIO"),# TP_SWDIO
    (7.5, 17.0, "SWCLK"),# TP_SWCLK
    (4.75, 8.6, "VR_PA"),
    (2.08, 5.0, "VR_PA"),
    (2.0, 10.75, "OSC_IN"),
    (0.9, 10.75, "OSC_IN"),
    (2.8, 13.2, "MIC_WS"),
    (5.5, 27.14, "MIC_WS"),
    (2.8, 14.8, "MIC_SD"),
    (7.5, 26.2, "MIC_SD"),
    (8.25, 8.8, "MIC_SCK"),
    (9.2, 27.0, "MIC_SCK"),
    (11.8, 9.8, "LED_R_DRV"),
    (9.8, 26.5, "LED_R_DRV"),
    (10.25, 8.8, "LED_B_DRV"),
    (10.4, 28.3, "LED_B_DRV"),
    (11.4, 12.75, "CHG_STAT"),
    (10.0, 18.5, "CHG_STAT"),
    (2.0, 26.5, "BATT_NEG"), # TP_BATT_N
    (8.64, 25.8, "BATT_NEG"),
    (4.8, 24.2, "BATT_POS"),  # TP_BATT_P
    (1.2, 22.5, "GATE_OD"),
    (8.64, 22.5, "GATE_OD"),
    (1.86, 25.8, "GATE_OC"),
    (9.4, 24.2, "GATE_OC"),
    (13.5, 4.2, "VBUS_5V"),   # TP_VBUS
    (12.72, 12.5, "VBUS_5V"),
    (13.8, 22.0, "VBUS_5V"),
    (9.5, 21.5, "VBUS_5V"),
    (11.72, 17.0, "VBAT_PROT"),
    (10.86, 22.0, "VBAT_PROT"),
    (12.94, 25.0, "VBAT_PROT"),
    (6.45, 22.0, "SYS_PWR"),
    (10.2, 25.15, "SYS_PWR")
]

print(f"Checking pairwise distances for {len(vias)} vias...")
min_diff_net_dist = 999.0
min_diff_pair = None
min_same_net_dist = 999.0
min_same_pair = None

for i in range(len(vias)):
    for j in range(i+1, len(vias)):
        vx1, vy1, n1 = vias[i]
        vx2, vy2, n2 = vias[j]
        d = math.hypot(vx1 - vx2, vy1 - vy2)
        if n1 != n2:
            if d < min_diff_net_dist:
                min_diff_net_dist = d
                min_diff_pair = (vias[i], vias[j])
        else:
            if d < min_same_net_dist:
                min_same_net_dist = d
                min_same_pair = (vias[i], vias[j])

print(f"Min diff-net via distance: {min_diff_net_dist:.3f} mm between {min_diff_pair[0][2]} at ({min_diff_pair[0][0]},{min_diff_pair[0][1]}) and {min_diff_pair[1][2]} at ({min_diff_pair[1][0]},{min_diff_pair[1][1]})")
print(f"Min same-net via distance: {min_same_net_dist:.3f} mm between {min_same_pair[0][2]} at ({min_same_pair[0][0]},{min_same_pair[0][1]}) and {min_same_pair[1][2]} at ({min_same_pair[1][0]},{min_same_pair[1][1]})")
if min_diff_net_dist >= 0.50:
    print("SUCCESS: Hole-to-hole constraint (0.50 mm) strictly satisfied across all different-net vias!")
else:
    print("WARNING: Some vias are < 0.50 mm apart!")
