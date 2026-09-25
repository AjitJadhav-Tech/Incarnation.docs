import pikepdf
from pikepdf import PdfImage

INPUT_FILE = "Acct Statement_6001_11082026_16.03.37_unlocked_removed (1).pdf"

total_images = 0
total_image_bytes = 0

with pikepdf.open(INPUT_FILE) as pdf:
    print(f"Pages: {len(pdf.pages)}")
    print(f"PDF version: {pdf.pdf_version}")
    print()

    for i, page in enumerate(pdf.pages):
        if "/Resources" not in page:
            continue
        resources = page["/Resources"]
        if "/XObject" not in resources:
            continue
        xobjects = resources["/XObject"]
        for key in xobjects.keys():
            xobj = xobjects[key]
            subtype = xobj.get("/Subtype", "")
            if str(subtype) == "/Image":
                w = int(xobj.get("/Width", 0))
                h = int(xobj.get("/Height", 0))
                bpc = xobj.get("/BitsPerComponent", "?")
                cs  = xobj.get("/ColorSpace", "?")
                flt = xobj.get("/Filter", "none")
                sz  = len(xobj.read_raw_bytes())
                total_images += 1
                total_image_bytes += sz
                print(f"  Page {i+1} | {key} | {w}x{h} | BPC={bpc} | CS={cs} | Filter={flt} | {sz/1024:.1f} KB")

    print()
    print(f"Total images found : {total_images}")
    print(f"Total image data   : {total_image_bytes/1024:.1f} KB")
