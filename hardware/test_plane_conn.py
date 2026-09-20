import pcbnew
import subprocess

board = pcbnew.LoadBoard('/Users/racoon/Documents/CHEATING/Device1/hardware/Device1.kicad_pcb')
nets = {net.GetNetname(): net for net in board.GetNetsByName().values()}
p3v3 = nets['3V3']

# Find C2 pad 1 and C3 pad 1
fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
c2_p1 = fps['C2'].FindPadByNumber('1')
c3_p1 = fps['C3'].FindPadByNumber('1')

def add_via_and_track(pad, dx, dy):
    pos = pad.GetPosition()
    v_pos = pcbnew.VECTOR2I(pos.x + pcbnew.FromMM(dx), pos.y + pcbnew.FromMM(dy))
    
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(v_pos)
    via.SetWidth(pcbnew.FromMM(0.60))
    via.SetDrill(pcbnew.FromMM(0.30))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetNet(pad.GetNet())
    board.Add(via)
    
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(pos)
    track.SetEnd(v_pos)
    track.SetWidth(pcbnew.FromMM(0.20))
    track.SetLayer(pcbnew.F_Cu)
    track.SetNet(pad.GetNet())
    board.Add(track)

add_via_and_track(c2_p1, -0.8, 0.0)
add_via_and_track(c3_p1, -0.8, 0.0)

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
board.Save('/Users/racoon/Documents/CHEATING/Device1/hardware/test_plane.kicad_pcb')
print("Saved test_plane.kicad_pcb")
