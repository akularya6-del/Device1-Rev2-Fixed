import os
import zipfile

root_dir = "/Users/racoon/Documents/CHEATING/Device1"
zip_path = os.path.join(root_dir, "manufacturing", "Device1_COMPLETE_HANDOFF.zip")

exclude_exts = {".pyc", ".DS_Store", ".o"}
exclude_dirs = {"__pycache__", ".git"}

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for foldername, subfolders, filenames in os.walk(root_dir):
        # Filter subfolders
        subfolders[:] = [d for d in subfolders if d not in exclude_dirs]
        for filename in filenames:
            if filename == "Device1_COMPLETE_HANDOFF.zip":
                continue
            if any(filename.endswith(ext) for ext in exclude_exts):
                continue
            if filename.startswith("."):
                continue
            filepath = os.path.join(foldername, filename)
            arcname = os.path.relpath(filepath, root_dir)
            zf.write(filepath, arcname)

print(f"Turnkey Handoff ZIP created: {zip_path} ({os.path.getsize(zip_path)} bytes)")
