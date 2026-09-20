with open('/Users/racoon/Documents/CHEATING/Device1/hardware/route_perfect.py', 'r') as f:
    code = f.read()

# 1. R6, R7, D2 placement
code = code.replace('("R6", "Resistor_SMD", "R_0402_1005Metric", 9.5, 27.6, 90),', '("R6", "Resistor_SMD", "R_0402_1005Metric", 10.6, 27.2, 0),')
code = code.replace('("R7", "Resistor_SMD", "R_0402_1005Metric", 9.5, 29.4, 90),', '("R7", "Resistor_SMD", "R_0402_1005Metric", 10.6, 29.4, 0),')
code = code.replace('("D2", "LED_SMD", "LED_0603_1608Metric", 12.5, 28.8, 0),', '("D2", "LED_SMD", "LED_0603_1608Metric", 13.0, 28.3, 90),')

# 2. MK1 3V3 via
code = code.replace('add_track(8.4, 27.436, 9.4, 27.436, pcbnew.F_Cu, p3v3_net, 0.25)\n    add_via(9.4, 27.436, p3v3_net)',
                    'add_track(8.4, 27.436, 8.4, 26.2, pcbnew.F_Cu, p3v3_net, 0.25)\n    add_via(8.4, 26.2, p3v3_net)')

# 3. TP_NRST on B.Cu
code = code.replace('("TP_NRST", 9.5, 22.8, "NRST"),', '("TP_NRST", 9.5, 24.5, "NRST"),')

# 4. Y1 area 3V3 via
code = code.replace('add_track(1.8, 10.48, 1.8, 11.2, pcbnew.F_Cu, p3v3_net, 0.25)\n    add_via(1.8, 11.2, p3v3_net)',
                    'add_track(1.8, 10.48, 1.8, 9.5, pcbnew.F_Cu, p3v3_net, 0.25)\n    add_via(1.8, 9.5, p3v3_net)')
code = code.replace('add_track(3.2, 11.2, 1.8, 11.2, pcbnew.F_Cu, p3v3_net, 0.25)',
                    'add_track(3.2, 9.75, 1.8, 9.5, pcbnew.F_Cu, p3v3_net, 0.25)')

# 5. RF C13 stub from L1 pad 1 (7.285)
code = code.replace('add_track(5.25, 6.8, 3.98, 6.8, pcbnew.F_Cu, nets["RF_50OHM"], 0.25)',
                    'add_track(5.25, 7.285, 3.98, 6.8, pcbnew.F_Cu, nets["RF_50OHM"], 0.25)')

# 6. U1 pin 41 via at 17.0
code = code.replace('add_track(6.75, 15.938, 6.75, 16.6, pcbnew.F_Cu, p3v3_net, 0.20)\n    add_via(6.75, 16.6, p3v3_net)',
                    'add_track(6.75, 15.938, 6.75, 17.0, pcbnew.F_Cu, p3v3_net, 0.20)\n    add_via(6.75, 17.0, p3v3_net)')

with open('/Users/racoon/Documents/CHEATING/Device1/hardware/route_perfect.py', 'w') as f:
    f.write(code)
print("Updated route_perfect.py with precise clearances")
