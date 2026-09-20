import pcbnew
import json
import subprocess

def test():
    board = pcbnew.LoadBoard('/Users/racoon/Documents/CHEATING/Device1/hardware/Device1.kicad_pcb')
    nets = {net.GetNetname(): net for net in board.GetNetsByName().values()}
    gnd = nets['GND']
    p3v3 = nets['3V3']
    print("GND netcode:", gnd.GetNetCode(), "3V3 netcode:", p3v3.GetNetCode())

test()
