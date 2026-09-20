with open('/Users/racoon/Documents/CHEATING/Device1/hardware/route_perfect.py', 'r') as f:
    code = f.read()

# Fix 1: Move R6 and R7 slightly down/spaced
code = code.replace('("R6", "Resistor_SMD", "R_0402_1005Metric", 10.2, 26.8, 90),', '("R6", "Resistor_SMD", "R_0402_1005Metric", 9.5, 27.6, 90),')
code = code.replace('("R7", "Resistor_SMD", "R_0402_1005Metric", 10.2, 29.2, 90),', '("R7", "Resistor_SMD", "R_0402_1005Metric", 9.5, 29.4, 90),')

# Fix 2: Remove continuous track across U1 bottom pins
old_u1_bottom = """    # Bottom U1 power bus for Pins 37, 41, 44, 45, 46 and C8
    add_track(4.75, 15.938, 9.25, 15.938, pcbnew.F_Cu, p3v3_net, 0.25)
    add_track(4.75, 15.938, 4.02, 17.5, pcbnew.F_Cu, p3v3_net, 0.25)
    add_track(7.0, 15.938, 7.0, 16.8, pcbnew.F_Cu, p3v3_net, 0.25)
    add_via(7.0, 16.8, p3v3_net)"""

new_u1_bottom = """    # Bottom U1 power pins individual connections
    add_track(4.75, 15.938, 4.02, 17.5, pcbnew.F_Cu, p3v3_net, 0.20)
    add_track(4.02, 17.5, 4.02, 18.2, pcbnew.F_Cu, p3v3_net, 0.20)
    add_via(4.02, 18.2, p3v3_net)
    add_track(6.75, 15.938, 6.75, 16.6, pcbnew.F_Cu, p3v3_net, 0.20)
    add_via(6.75, 16.6, p3v3_net)
    add_track(8.25, 15.938, 8.25, 16.6, pcbnew.F_Cu, p3v3_net, 0.20)
    add_track(8.75, 15.938, 8.75, 16.6, pcbnew.F_Cu, p3v3_net, 0.20)
    add_track(9.25, 15.938, 9.25, 16.6, pcbnew.F_Cu, p3v3_net, 0.20)
    add_track(8.25, 16.6, 9.25, 16.6, pcbnew.F_Cu, p3v3_net, 0.20)
    add_via(8.75, 16.6, p3v3_net)"""

code = code.replace(old_u1_bottom, new_u1_bottom)

# Fix 3: C11 via position
code = code.replace("add_track(1.8, 15.48, 1.8, 16.2, pcbnew.F_Cu, p3v3_net, 0.25)\n    add_via(1.8, 16.2, p3v3_net)", "add_track(1.8, 15.48, 2.6, 15.48, pcbnew.F_Cu, p3v3_net, 0.25)\n    add_via(2.6, 15.48, p3v3_net)")

with open('/Users/racoon/Documents/CHEATING/Device1/hardware/route_perfect.py', 'w') as f:
    f.write(code)
print("Updated route_perfect.py")
