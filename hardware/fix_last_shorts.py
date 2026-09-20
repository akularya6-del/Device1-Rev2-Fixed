with open('/Users/racoon/Documents/CHEATING/Device1/hardware/build_clean_board.py', 'r') as f:
    code = f.read()

# Fix 1: MK1 3V3 trace and via to the right
old_mk1_3v3 = """    add_track(8.4, 27.436, 7.5, 27.436, pcbnew.F_Cu, p3v3_net, 0.20)
    add_track(7.5, 27.436, 7.5, 26.5, pcbnew.F_Cu, p3v3_net, 0.20)
    add_via(7.5, 26.5, p3v3_net)"""
new_mk1_3v3 = """    add_track(8.4, 27.436, 9.2, 27.436, pcbnew.F_Cu, p3v3_net, 0.20)
    add_track(9.2, 27.436, 9.2, 26.2, pcbnew.F_Cu, p3v3_net, 0.20)
    add_via(9.2, 26.2, p3v3_net)"""
code = code.replace(old_mk1_3v3, new_mk1_3v3)

# Fix 2: U1 Pin 41 via at Y=17.8
old_u1_p41 = """    add_track(6.75, 15.938, 6.0, 16.5, pcbnew.F_Cu, p3v3_net, 0.20)
    add_via(6.0, 16.5, p3v3_net)"""
new_u1_p41 = """    add_track(6.75, 15.938, 6.75, 17.8, pcbnew.F_Cu, p3v3_net, 0.20)
    add_via(6.75, 17.8, p3v3_net)"""
code = code.replace(old_u1_p41, new_u1_p41)

# Fix 3: TP_3V3 position at (13.2, 20.0)
code = code.replace('("TP_3V3", 11.5, 25.0, "3V3"),', '("TP_3V3", 13.2, 20.0, "3V3"),')
code = code.replace('add_via(11.5, 25.0, p3v3_net) # TP_3V3', 'add_via(13.2, 20.0, p3v3_net) # TP_3V3')

with open('/Users/racoon/Documents/CHEATING/Device1/hardware/build_clean_board.py', 'w') as f:
    f.write(code)
print("Updated build_clean_board.py")
