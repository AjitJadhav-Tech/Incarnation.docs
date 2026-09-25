import pikepdf
import os
import re

# ---- SETTINGS ----
INPUT_FILE  = "Acct Statement_XX0115_22032024-5.pdf"
OUTPUT_FILE = "Acct Statement_XX0115_11092026-9.pdf"
PASSWORD    = "MOHA2406"
# ------------------

TEMP1 = "_temp1.pdf"

# ── STEP 1: Compress, wipe metadata, NO object streams so docinfo stays plain
with pikepdf.open(INPUT_FILE) as pdf:
    for key in list(pdf.docinfo.keys()):
        del pdf.docinfo[key]
    with pdf.open_metadata() as meta:
        for key in list(meta.keys()):
            del meta[key]
    pdf.save(
        TEMP1,
        compress_streams=True,
        object_stream_mode=pikepdf.ObjectStreamMode.disable,  # keep docinfo in plain trailer
        recompress_flate=True,
        normalize_content=True,
    )

# ── STEP 2: Encrypt (pikepdf injects /Producer into plain trailer here) ────
with pikepdf.open(TEMP1) as pdf:
    for key in list(pdf.docinfo.keys()):
        del pdf.docinfo[key]
    encryption = pikepdf.Encryption(user=PASSWORD, owner=PASSWORD, R=4)
    pdf.save(OUTPUT_FILE, encryption=encryption,
             object_stream_mode=pikepdf.ObjectStreamMode.disable)

os.remove(TEMP1)

# ── STEP 3: Patch raw bytes — now docinfo is in plain trailer ─────────────
with open(OUTPUT_FILE, "rb") as f:
    data = f.read()

found = re.findall(rb"/Producer\s*\([^)]*\)", data)
print("Found producer entries:", found)

patched = re.sub(rb"/Producer\s*\([^)]*\)", b"", data)
patched = re.sub(rb"/Producer\s*<[0-9a-fA-F\s]*>", b"", patched)

with open(OUTPUT_FILE, "wb") as f:
    f.write(patched)

print(f"✅ Done! {OUTPUT_FILE}  ({os.path.getsize(OUTPUT_FILE)/1024:.1f} KB)")
