import pcbnew

board = pcbnew.LoadBoard('/Users/racoon/Documents/CHEATING/Device1/hardware/Device1.kicad_pcb')
nets = {net.GetNetname(): net for net in board.GetNetsByName().values()}
p3v3 = nets['3V3']

# Add a via at (9.0, 20.0) net 3V3
via = pcbnew.PCB_VIA(board)
via.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(9.0), pcbnew.FromMM(20.0)))
via.SetWidth(pcbnew.FromMM(0.60))
via.SetDrill(pcbnew.FromMM(0.30))
via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
via.SetNet(p3v3)
board.Add(via)

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
board.Save('/Users/racoon/Documents/CHEATING/Device1/hardware/test_via.kicad_pcb')
print("Saved test_via board")
