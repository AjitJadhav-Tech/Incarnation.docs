from pypdf import PdfReader, PdfWriter

# ---- SETTINGS ----
INPUT_FILE  = "Acct Statement_6001_11082026_16.03.37_unlocked_removed (1)"   # ✅ fixed
OUTPUT_FILE = "Acct Statement_6001_12082026_08.27.16"
PASSWORD    = "179630860"   # put your actual password here
# ------------------

reader = PdfReader(INPUT_FILE)

if reader.is_encrypted:
    reader.decrypt(PASSWORD)

writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

existing_metadata = reader.metadata
new_metadata = {}

for key, value in existing_metadata.items():
    if key not in ("/ModDate", "/CreationDate"):
        new_metadata[key] = value

new_metadata["/ModDate"] = ""
new_metadata["/CreationDate"] = ""

writer.add_metadata(new_metadata)

with open(OUTPUT_FILE, "wb") as f:
    writer.write(f)

print("✅ Done! Cleaned PDF saved as:", OUTPUT_FILE)