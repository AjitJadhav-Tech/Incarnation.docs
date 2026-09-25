from pypdf import PdfReader, PdfWriter
from datetime import datetime
import os
import re

# ---- SETTINGS ----
INPUT_FILE  = "Acct Statement_XX0115_11092026-09.pdf"  # Use original unencrypted file
OUTPUT_FILE = "Acct Statement_XX0115_11092026-FINALL.pdf"
PASSWORD    = "MOHA2406"
CREATED_DATE = "11-09-2026 13:46:16"  # Format: DD-MM-YYYY HH:MM:SS
# ------------------

# Convert to PDF date format
dt = datetime.strptime(CREATED_DATE, "%d-%m-%Y %H:%M:%S")
pdf_date = dt.strftime("D:%Y%m%d%H%M%S")

print(f"Input date: {CREATED_DATE}")
print(f"PDF format: {pdf_date}")

reader = PdfReader(INPUT_FILE)

# Decrypt if encrypted
if reader.is_encrypted:
    reader.decrypt(PASSWORD)

writer = PdfWriter()

# Copy all pages
for page in reader.pages:
    writer.add_page(page)

# Set ONLY CreationDate - nothing else
# This completely replaces any existing metadata
writer.add_metadata({
    "/CreationDate": pdf_date
})

# Encrypt
writer.encrypt(user_password=PASSWORD, owner_password=PASSWORD, algorithm="AES-128")

# Write to file
with open(OUTPUT_FILE, "wb") as f:
    writer.write(f)

# Patch raw bytes to remove pypdf producer and ModDate
with open(OUTPUT_FILE, "rb") as f:
    data = f.read()

# More aggressive pattern matching for Producer and ModDate
# Match both string literals () and hex strings <>
data = re.sub(rb"/Producer\s*\([^)]*\)", b"", data)
data = re.sub(rb"/Producer\s*<[0-9a-fA-F\s]*>", b"", data)
data = re.sub(rb"/Producer\s*/", b"/", data)  # catch orphaned /Producer keys

data = re.sub(rb"/ModDate\s*\([^)]*\)", b"", data)
data = re.sub(rb"/ModDate\s*<[0-9a-fA-F\s]*>", b"", data)
data = re.sub(rb"/ModDate\s*/", b"/", data)  # catch orphaned /ModDate keys

# Debug: check what we found
if b"ModDate" in data:
    print("⚠️  Warning: ModDate still present after patching")
if b"Producer" in data:
    print("⚠️  Warning: Producer still present after patching")

with open(OUTPUT_FILE, "wb") as f:
    f.write(data)

print(f"\n✅ Done!")
print(f"   Input:  {INPUT_FILE} ({os.path.getsize(INPUT_FILE)/1024:.1f} KB)")
print(f"   Output: {OUTPUT_FILE} ({os.path.getsize(OUTPUT_FILE)/1024:.1f} KB)")
print(f"   CreationDate: {CREATED_DATE}")
print(f"   Password: {PASSWORD}")
