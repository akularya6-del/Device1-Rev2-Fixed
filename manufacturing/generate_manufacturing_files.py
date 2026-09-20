import csv
import os
import zipfile

# 1. Generate BOM
bom_entries = [
    # Ref, Value, Footprint, MPN, Manufacturer, LCSC, Qty
    ("U1", "STM32WL55CCU6", "QFN-48-1EP_7x7mm_P0.5mm", "STM32WL55CCU6TR", "STMicroelectronics", "C2682618", 1),
    ("ANT1", "0868AT43A0020E", "Johanson_0868AT43A0020E_CUSTOM", "0868AT43A0020E", "Johanson Technology", "C2897287", 1),
    ("Y1", "32MHz 10pF 10ppm", "Crystal_SMD_2016-4Pin_2.0x1.6mm", "XRCGB32M000F1H00R0", "Murata", "C515086", 1),
    ("MK1", "SPH0645LM4H-B", "Knowles_SPH0645LM4H-6_3.5x2.65mm", "SPH0645LM4H-B", "Knowles", "C2913165", 1),
    ("U5", "AP2112K-3.3TRG1", "SOT-23-5", "AP2112K-3.3TRG1", "Diodes Incorporated", "C439908", 1),
    ("U2", "MCP73831T-2ACI/OT", "SOT-23-5", "MCP73831T-2ACI/OT", "Microchip Direct", "C14703", 1),
    ("U4", "DW01A", "SOT-23-6", "DW01A", "Fortune Semi", "C42750", 1),
    ("Q1", "FS8205A", "SOT-23-6", "FS8205A", "Fortune Semi", "C32254", 1),
    ("Q2", "DMG2305UX-7", "SOT-23", "DMG2305UX-7", "Diodes Incorporated", "C2838446", 1),
    ("D1", "1N5819WS", "SOD-323", "1N5819WS", "JCET", "C8598", 1),
    ("D2", "Red/Blue Bi-color", "LED_0603_1608Metric", "KT-0603RGBA", "Kingbright", "C209634", 1),
    ("L1", "3.3nH", "L_0402_1005Metric", "LQG15HS3N3S02D", "Murata", "C1033", 1),
    ("L2", "47nH", "L_0402_1005Metric", "LQG15HS47NJ02D", "Murata", "C1038", 1),
    ("L3", "18nH", "L_0402_1005Metric", "LQG15HS18NJ02D", "Murata", "C1035", 1),
    ("C13", "2.2pF 50V C0G", "C_0402_1005Metric", "GJM1555C1H2R2CB01D", "Murata", "C39744", 1),
    ("C14", "1.5pF 50V C0G", "C_0402_1005Metric", "GJM1555C1H1R5CB01D", "Murata", "C39743", 1),
    ("C22", "1.5pF 50V C0G", "C_0402_1005Metric", "GJM1555C1H1R5CB01D", "Murata", "C39743", 1),
    ("C23", "1.5pF 50V C0G", "C_0402_1005Metric", "GJM1555C1H1R5CB01D", "Murata", "C39743", 1),
    ("R_ANT", "0R 5%", "R_0402_1005Metric", "0402WGF0000TCE", "Uniroyal", "C17168", 1),
    ("R1", "10k 1%", "R_0402_1005Metric", "0402WGF1002TCE", "Uniroyal", "C25744", 1),
    ("R6", "1k 1%", "R_0402_1005Metric", "0402WGF1001TCE", "Uniroyal", "C11702", 1),
    ("R7", "470R 1%", "R_0402_1005Metric", "0402WGF4700TCE", "Uniroyal", "C25118", 1),
    ("C1, C2, C3, C4, C5, C7, C8, C11, C12, C15, C18", "100nF 50V X7R", "C_0402_1005Metric", "CL05B104KO5NNNC", "Samsung", "C1525", 11),
    ("C9, C10, C16, C17, C20", "1uF 25V X5R", "C_0402_1005Metric", "CL05A105KA5NQNC", "Samsung", "C52923", 5),
    ("C21", "4.7uF 10V X5R", "C_0402_1005Metric", "CL05A475MP5NRNC", "Samsung", "C19666", 1),
]

bom_headers = ["Comment", "Designator", "Footprint", "LCSC Part #", "Manufacturer", "MFR.Part #", "Quantity"]
jlc_bom = []
for ref, val, fp, mpn, mfr, lcsc, qty in bom_entries:
    jlc_bom.append({
        "Comment": val,
        "Designator": ref,
        "Footprint": fp,
        "LCSC Part #": lcsc,
        "Manufacturer": mfr,
        "MFR.Part #": mpn,
        "Quantity": qty
    })

# Write JLCPCB BOM
jlc_bom_path = "/Users/racoon/Documents/CHEATING/Device1/manufacturing/JLCPCB_UPLOAD/Device1_BOM.csv"
with open(jlc_bom_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=bom_headers)
    writer.writeheader()
    writer.writerows(jlc_bom)

# Write Root BOM
root_bom_path = "/Users/racoon/Documents/CHEATING/Device1/DEVICE1_FINAL_BOM.csv"
with open(root_bom_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=bom_headers)
    writer.writeheader()
    writer.writerows(jlc_bom)

print("Generated BOM files: Device1_BOM.csv and DEVICE1_FINAL_BOM.csv")

# 2. Parse pos file and generate JLCPCB CPL
pos_path = "/Users/racoon/Documents/CHEATING/Device1/manufacturing/assembly/Device1_pos.csv"
cpl_path = "/Users/racoon/Documents/CHEATING/Device1/manufacturing/JLCPCB_UPLOAD/Device1_CPL.csv"
root_cpl_path = "/Users/racoon/Documents/CHEATING/Device1/DEVICE1_FINAL_CPL.csv"

rot_offsets = {
    "U1": 0,
    "U2": 0,
    "U5": 0,
    "U4": 0,
    "Q1": 0,
    "Q2": 0,
    "MK1": 0,
    "Y1": 0,
    "ANT1": 0,
    "D2": 0,
}

cpl_rows = []
with open(pos_path, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        ref = row["Ref"].strip('"')
        val = row["Val"].strip('"')
        if ref.startswith("TP_") or ref == "R_TEST" or "DNP" in val.upper():
            continue # Skip test points and DNP components from SMT pick-and-place assembly
        pkg = row["Package"].strip('"')
        pos_x = float(row["PosX"])
        pos_y = abs(float(row["PosY"])) # Make coordinates positive relative to (0,0)
        rot = float(row["Rot"])
        side = "Top" if row["Side"].strip('"').lower() == "top" else "Bottom"
        
        cal_rot = (rot + rot_offsets.get(ref, 0)) % 360
        
        cpl_rows.append({
            "Designator": ref,
            "Val": val,
            "Package": pkg,
            "Mid X": f"{pos_x:.3f}mm",
            "Mid Y": f"{pos_y:.3f}mm",
            "Rotation": f"{cal_rot:.1f}",
            "Layer": side
        })

cpl_headers = ["Designator", "Val", "Package", "Mid X", "Mid Y", "Rotation", "Layer"]
with open(cpl_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=cpl_headers)
    writer.writeheader()
    writer.writerows(cpl_rows)

with open(root_cpl_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=cpl_headers)
    writer.writeheader()
    writer.writerows(cpl_rows)

print(f"Generated CPL files: {cpl_path} and {root_cpl_path} ({len(cpl_rows)} SMT components)")

# 3. Create Gerber ZIP for JLCPCB
gerbers_dir = "/Users/racoon/Documents/CHEATING/Device1/manufacturing/gerbers"
drill_dir = "/Users/racoon/Documents/CHEATING/Device1/manufacturing/drill"
zip_path = "/Users/racoon/Documents/CHEATING/Device1/manufacturing/JLCPCB_UPLOAD/Device1_Gerbers.zip"

essential_gerber_exts = [
    "-F_Cu.gtl", "-In1_Cu.g1", "-In2_Cu.g2", "-B_Cu.gbl",
    "-F_Mask.gts", "-B_Mask.gbs", "-F_Silkscreen.gto", "-B_Silkscreen.gbo",
    "-F_Paste.gtp", "-B_Paste.gbp", "-Edge_Cuts.gm1",
    "-F_Cu.gbr", "-In1_Cu.gbr", "-In2_Cu.gbr", "-B_Cu.gbr",
    "-F_Mask.gbr", "-B_Mask.gbr", "-F_Silkscreen.gbr", "-B_Silkscreen.gbr",
    "-F_Paste.gbr", "-B_Paste.gbr", "-Edge_Cuts.gbr"
]

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in os.listdir(gerbers_dir):
        if any(f.endswith(ext) for ext in essential_gerber_exts):
            zf.write(os.path.join(gerbers_dir, f), f)
            print(f"  Added to Gerber ZIP: {f}")
    for f in os.listdir(drill_dir):
        if f.endswith(".drl"):
            zf.write(os.path.join(drill_dir, f), f)
            print(f"  Added to Gerber ZIP: {f}")

print(f"Generated JLCPCB Gerber ZIP: {zip_path}")

