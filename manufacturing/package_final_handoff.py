import os
import zipfile
import shutil

root_dir = "/Users/racoon/Documents/CHEATING/Device1"
mfg_zip = os.path.join(root_dir, "manufacturing", "Device1_COMPLETE_HANDOFF_FINAL.zip")
root_zip = os.path.join(root_dir, "Device1_COMPLETE_HANDOFF_FINAL.zip")

# Copy JLCPCB Gerbers to root for convenience
jlc_gerbers = os.path.join(root_dir, "manufacturing", "JLCPCB_UPLOAD", "Device1_Gerbers.zip")
if os.path.exists(jlc_gerbers):
    shutil.copy(jlc_gerbers, os.path.join(root_dir, "Device1_Gerbers.zip"))

# Folders to include
include_dirs = ["hardware", "manufacturing", "firmware", "docs", "validation", "Device1.pretty"]

# Key root files to include
include_root_files = [
    "Device1.kicad_pcb",
    "Device1.kicad_sch",
    "Device1.kicad_pro",
    "Device1.kicad_prl",
    "Device1.kicad_sym",
    "fp-lib-table",
    "sym-lib-table",
    "Device1-drc.rpt",
    "Device1-erc.rpt",
    "DEVICE1_FINAL_BOM.csv",
    "DEVICE1_FINAL_CPL.csv",
    "Device1_Gerbers.zip",
    "RF_REFERENCE_COMPARISON_FINAL.md",
    "VALIDATION_REPORT_FINAL.md",
    "AUDIO_RF_BUDGET_FINAL.md",
    "DEVICE1_FINAL_CONSISTENCY_REPAIR_PLAN.md",
    "README.md",
]

exclude_exts = {".pyc", ".DS_Store", ".o", ".bak"}
exclude_dirs = {"__pycache__", ".git", "scratch_reports", "before_blocker_repair", "pre_execution_backup", "pre_final_consistency_backup"}

if os.path.exists(mfg_zip):
    os.remove(mfg_zip)

with zipfile.ZipFile(mfg_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
    # 1. Add top-level individual files
    for fname in include_root_files:
        fpath = os.path.join(root_dir, fname)
        if os.path.exists(fpath):
            zf.write(fpath, fname)
            zf.write(fpath, f"Device1/{fname}")

    # 2. Add subdirectories
    for d in include_dirs:
        dirpath = os.path.join(root_dir, d)
        if not os.path.exists(dirpath):
            continue
        for foldername, subfolders, filenames in os.walk(dirpath):
            subfolders[:] = [sd for sd in subfolders if sd not in exclude_dirs]
            for filename in filenames:
                if filename.endswith(".zip"):
                    continue
                if any(filename.endswith(ext) for ext in exclude_exts):
                    continue
                if filename.startswith("."):
                    continue
                filepath = os.path.join(foldername, filename)
                relpath = os.path.relpath(filepath, root_dir)
                zf.write(filepath, f"Device1/{relpath}")

# Copy to root
shutil.copy(mfg_zip, root_zip)

print(f"Final Handoff ZIP successfully created at:")
print(f"  {mfg_zip} ({os.path.getsize(mfg_zip)} bytes)")
print(f"  {root_zip} ({os.path.getsize(root_zip)} bytes)")
