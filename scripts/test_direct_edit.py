import sys
import subprocess

def test_edit():
    with open("Device1/hardware/Device1.kicad_pcb", "r") as f:
        text = f.read()

    # 1. Replace ANT1
    # Find ANT1 block
    import re
    ant1_pattern = r'(\t\(footprint "(?:Johanson_2450AT43F0100|Device1:Johanson_0868AT43A0020E_CUSTOM)".*?\n\t\))'
    
    new_ant1 = """\t(footprint "Device1:Johanson_0868AT43A0020E_CUSTOM"
\t\t(layer "F.Cu")
\t\t(uuid "1da6a275-9d3d-4900-b734-9e2d47f0f959")
\t\t(at 7.5 2)
\t\t(descr "Johanson Technology 0868AT43A0020E 868MHz Ceramic Chip Antenna (7.0x2.0mm body, land pattern 1.0x1.8mm pads, 5.1mm gap, 6.1mm pitch)")
\t\t(tags "antenna 868MHz Johanson 0868AT43A0020E")
\t\t(property "Reference" "ANT1"
\t\t\t(at 0 -2.05 0)
\t\t\t(layer "F.SilkS")
\t\t\t(hide yes)
\t\t\t(uuid "7f96dad9-d812-42b7-9d48-a32d73cbc467")
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1 1)
\t\t\t\t\t(thickness 0.15)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Value" "0868AT43A0020E"
\t\t\t(at 0 2.05 0)
\t\t\t(layer "F.Fab")
\t\t\t(hide yes)
\t\t\t(uuid "d413db40-841a-44c0-a387-67b22fa501fc")
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1 1)
\t\t\t\t\t(thickness 0.15)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" "Device1:Johanson_0868AT43A0020E_CUSTOM"
\t\t\t(at 0 0 0)
\t\t\t(layer "F.Fab")
\t\t\t(hide yes)
\t\t\t(uuid "a172191e-efa7-4b17-8b2f-0330abe2e61c")
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t(thickness 0.15)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Datasheet" "https://www.johansontechnology.com/datasheets/0868AT43A0020/0868AT43A0020.pdf"
\t\t\t(at 0 0 0)
\t\t\t(layer "F.Fab")
\t\t\t(hide yes)
\t\t\t(uuid "a050b530-f71c-4de6-b51c-c3a0b11567c4")
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t(thickness 0.15)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Description" "868MHz Ceramic Chip Antenna"
\t\t\t(at 0 0 0)
\t\t\t(layer "F.Fab")
\t\t\t(hide yes)
\t\t\t(uuid "b9148b1d-ef23-4552-87eb-1188432328fa")
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t(thickness 0.15)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(attr smd)
\t\t(fp_line (start -3.5 -1) (end -3 -1) (stroke (width 0.1) (type solid)) (layer "F.Fab") (uuid "f9556d63-1b54-43e3-ae8f-e4dc9add9a09"))
\t\t(fp_line (start -3.5 -0.5) (end -3.5 1) (stroke (width 0.1) (type solid)) (layer "F.Fab") (uuid "e965a1ab-ee2c-47e0-85e3-44fc6e9d95c5"))
\t\t(fp_line (start -3.5 -0.5) (end -3 -1) (stroke (width 0.1) (type solid)) (layer "F.Fab") (uuid "27ad0735-922d-4163-9b37-7af1db0b5b98"))
\t\t(fp_line (start -3.5 1) (end 3.5 1) (stroke (width 0.1) (type solid)) (layer "F.Fab") (uuid "c6566085-f5be-4416-9286-904d9c7925e0"))
\t\t(fp_line (start 3.5 1) (end 3.5 -1) (stroke (width 0.1) (type solid)) (layer "F.Fab") (uuid "aae81be0-0d92-407b-a4ab-2870284a137b"))
\t\t(fp_line (start 3.5 -1) (end -3 -1) (stroke (width 0.1) (type solid)) (layer "F.Fab") (uuid "3b9a1d42-ef44-48bc-91aa-fc8492023dc8"))
\t\t(fp_line (start -2.3 -1.15) (end 2.3 -1.15) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "543d9caf-8d24-421b-9114-bfacadc4edae"))
\t\t(fp_line (start -2.3 1.15) (end 2.3 1.15) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "ed2edc1c-1e56-4533-b32b-a14a189117ba"))
\t\t(fp_circle (center -4.0 -0.5) (end -3.9 -0.5) (stroke (width 0.12) (type solid)) (fill solid) (layer "F.SilkS") (uuid "d562c784-5842-4dd8-8c39-b95389225cfa"))
\t\t(fp_line (start -3.8 -1.25) (end 3.8 -1.25) (stroke (width 0.05) (type solid)) (layer "F.CrtYd") (uuid "1b868a21-3441-4658-8463-1afec095fb8c"))
\t\t(fp_line (start 3.8 -1.25) (end 3.8 1.25) (stroke (width 0.05) (type solid)) (layer "F.CrtYd") (uuid "3897035a-a511-4902-9e21-1f7c33d7df81"))
\t\t(fp_line (start 3.8 1.25) (end -3.8 1.25) (stroke (width 0.05) (type solid)) (layer "F.CrtYd") (uuid "45100001-0000-4000-8000-000000000001"))
\t\t(fp_line (start -3.8 1.25) (end -3.8 -1.25) (stroke (width 0.05) (type solid)) (layer "F.CrtYd") (uuid "ad0a0015-7370-43f1-baca-a9cdd3b1ed5e"))
\t\t(fp_text user "${REFERENCE}"
\t\t\t(at 0 0 0)
\t\t\t(layer "F.Fab")
\t\t\t(uuid "6e7c7970-8f0c-4d5c-aa26-68a06c6f4bd8")
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1 1)
\t\t\t\t\t(thickness 0.15)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(pad "1" smd roundrect
\t\t\t(at -3.05 0)
\t\t\t(size 1 1.8)
\t\t\t(layers "F.Cu" "F.Mask" "F.Paste")
\t\t\t(roundrect_rratio 0.2)
\t\t\t(net "/ANT_FEED")
\t\t\t(uuid "34da4069-7def-46c1-b3e8-d46ef4623c43")
\t\t)
\t\t(pad "2" smd roundrect
\t\t\t(at 3.05 0)
\t\t\t(size 1 1.8)
\t\t\t(layers "F.Cu" "F.Mask" "F.Paste")
\t\t\t(roundrect_rratio 0.2)
\t\t\t(uuid "6ae3aa59-d478-408a-a883-b22d5b64703c")
\t\t)
\t)"""

    text = re.sub(ant1_pattern, new_ant1, text, count=1, flags=re.DOTALL)

    # 2. Update ANT_FEED track segments
    old_tracks = """\t(segment
\t\t(start 4.65 2.9)
\t\t(end 4.65 2)
\t\t(width 0.29)
\t\t(layer "F.Cu")
\t\t(net "/ANT_FEED")
\t\t(uuid "55070369-a68c-4ad1-a5cb-ea094c39211e")
\t)
\t(segment
\t\t(start 5.25 3.5)
\t\t(end 4.65 2.9)
\t\t(width 0.29)
\t\t(layer "F.Cu")
\t\t(net "/ANT_FEED")
\t\t(uuid "73b3c33d-9d39-4c8f-9454-cefdd1898892")
\t)"""

    new_tracks = """\t(segment
\t\t(start 5.25 3.5)
\t\t(end 4.45 2.7)
\t\t(width 0.29)
\t\t(layer "F.Cu")
\t\t(net "/ANT_FEED")
\t\t(uuid "73b3c33d-9d39-4c8f-9454-cefdd1898892")
\t)
\t(segment
\t\t(start 4.45 2.7)
\t\t(end 4.45 2)
\t\t(width 0.29)
\t\t(layer "F.Cu")
\t\t(net "/ANT_FEED")
\t\t(uuid "55070369-a68c-4ad1-a5cb-ea094c39211e")
\t)"""

    text = text.replace(old_tracks, new_tracks)

    # 3. Add net to U1 Pin 20 and Pin 21
    old_p20 = """\t\t(pad "20" smd roundrect
\t\t\t(at 0.75 3.4375 180)
\t\t\t(size 0.25 0.875)
\t\t\t(layers "F.Cu" "F.Mask" "F.Paste")
\t\t\t(roundrect_rratio 0.25)
\t\t\t(uuid "0bd38467-a83c-40b0-af2f-a039f84ccab0")
\t\t)"""
    new_p20 = """\t\t(pad "20" smd roundrect
\t\t\t(at 0.75 3.4375 180)
\t\t\t(size 0.25 0.875)
\t\t\t(layers "F.Cu" "F.Mask" "F.Paste")
\t\t\t(roundrect_rratio 0.25)
\t\t\t(net "/RFI_P")
\t\t\t(uuid "0bd38467-a83c-40b0-af2f-a039f84ccab0")
\t\t)"""

    old_p21 = """\t\t(pad "21" smd roundrect
\t\t\t(at 1.25 3.4375 180)
\t\t\t(size 0.25 0.875)
\t\t\t(layers "F.Cu" "F.Mask" "F.Paste")
\t\t\t(roundrect_rratio 0.25)
\t\t\t(uuid "06e99a04-7cc4-4c60-87d2-cb5a250cef99")
\t\t)"""
    new_p21 = """\t\t(pad "21" smd roundrect
\t\t\t(at 1.25 3.4375 180)
\t\t\t(size 0.25 0.875)
\t\t\t(layers "F.Cu" "F.Mask" "F.Paste")
\t\t\t(roundrect_rratio 0.25)
\t\t\t(net "/RFI_N")
\t\t\t(uuid "06e99a04-7cc4-4c60-87d2-cb5a250cef99")
\t\t)"""

    text = text.replace(old_p20, new_p20).replace(old_p21, new_p21)

    with open("Device1/hardware/test_direct.kicad_pcb", "w") as f:
        f.write(text)

    print("Wrote test_direct.kicad_pcb")

if __name__ == "__main__":
    test_edit()
