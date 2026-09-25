# Incarnation.ai - PDF Date & Lock Tool

A comprehensive desktop application for manipulating PDF metadata, timestamps, and encryption. Set precise creation/modification dates, apply password protection, and remove software fingerprints from your PDF documents.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ Features

### Desktop GUI Application (`app.py`)
- 🎨 **Modern Dark-Themed Interface** - Beautiful, intuitive Tkinter GUI
- 📅 **Precise Date Control** - Set creation and modification dates down to the second
- 🔒 **Password Protection** - Encrypt PDFs with user/owner passwords
- 📊 **PDF Inspection** - View metadata, page count, file size, and encryption status
- 🗜️ **Compression** - Reduce file size with stream compression
- 🧹 **Metadata Wiping** - Remove title, author, and producer information
- 🕵️ **Forensic Cleaning** - Strip library fingerprints and software signatures
- ⏱️ **IST Timezone Support** - Indian Standard Time (UTC+5:30) by default

### CLI Scripts
- **`groover.py`** - Advanced CLI script with three-step processing
- **`clean_and_lock.py`** - Alternative pypdf-based CLI tool
- **`diagnose.py`** - PDF image analysis and diagnostic utility

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/AjitJadhav-Tech/Incarnation.docs.git
cd Incarnation.docs
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running the Application

#### Windows
Double-click `Run PDF Date and Lock.bat` or run:
```cmd
"Run PDF Date and Lock.bat"
```

#### Command Line (Any OS)
```bash
python app.py
```

## 📖 Usage Guide

### GUI Application

1. **Load PDF**
   - Click "Browse" to select your source PDF
   - Enter password if the PDF is already locked
   - Click "Inspect" to view current metadata

2. **Set Dates**
   - Adjust creation date using spinboxes (DD/MM/YYYY HH:MM:SS)
   - Set modification date or check "Leave Modified blank"
   - Use helper buttons: "Now", "From file", "Match creation"

3. **Configure Options**
   - Enter new password for output PDF
   - Toggle "Lock output with this password"
   - Enable compression to reduce file size
   - Enable metadata wiping for privacy
   - Enable producer tag stripping for forensic cleaning

4. **Process**
   - Choose output location with "Save As"
   - Click "Process PDF" to generate the new file
   - View progress and results in the log panel

### CLI Scripts

#### Using groover.py
Edit the settings in the script:
```python
INPUT_FILE  = "input.pdf"
OUTPUT_FILE = "output.pdf"
PASSWORD    = "your_password"
```
Then run:
```bash
python groover.py
```

#### Using clean_and_lock.py
Edit the settings:
```python
INPUT_FILE  = "input.pdf"
OUTPUT_FILE = "output.pdf"
PASSWORD    = "your_password"
CREATED_DATE = "11-09-2026 13:46:16"  # DD-MM-YYYY HH:MM:SS
```
Then run:
```bash
python clean_and_lock.py
```

#### Using diagnose.py
Analyze PDF images:
```python
INPUT_FILE = "document.pdf"
```
Then run:
```bash
python diagnose.py
```

## 🛠️ Technical Details

### Core Engine (`pdf_engine.py`)

**Key Functions:**
- `inspect_pdf()` - Extract and analyze PDF metadata
- `process_pdf()` - Main processing engine with multi-stage approach
- `format_pdf_date()` - Convert datetime to PDF date format
- `format_xmp_date()` - Convert datetime to XMP metadata format

**Processing Pipeline:**
1. Open and decrypt source PDF (if password-protected)
2. Apply date modifications to document info and XMP metadata
3. Optionally compress streams and normalize content
4. Apply encryption if password is provided
5. Perform byte-level patching to remove producer/modification tags
6. Save final output

### Libraries Used
- **pikepdf** - Robust PDF manipulation (primary engine)
- **pypdf** - Alternative PDF library (clean_and_lock.py)
- **tkinter** - Cross-platform GUI framework
- **re** - Regular expressions for byte-level patching

## 📁 Project Structure

```
Incarnation.ai/
├── app.py                          # Main GUI application
├── pdf_engine.py                   # Core PDF processing engine
├── groover.py                      # Advanced CLI script
├── clean_and_lock.py               # Alternative CLI script
├── diagnose.py                     # PDF diagnostic utility
├── requirements.txt                # Python dependencies
├── Run PDF Date and Lock.bat       # Windows launcher
└── README.md                       # This file
```

## ⚙️ Configuration

### Timezone
Default timezone is IST (Indian Standard Time, UTC+5:30). To change, modify in `pdf_engine.py`:
```python
IST = timezone(timedelta(hours=5, minutes=30))
```

### GUI Theme Colors
Customize the appearance in `app.py`:
```python
APP_BG = "#101418"      # App background
PANEL = "#171d24"       # Panel background
ACCENT = "#3d9cf0"      # Accent color
TEXT = "#e8eef5"        # Text color
```

## 🔒 Security & Privacy

This tool is designed for legitimate document management purposes:
- ✅ Set accurate timestamps for archival purposes
- ✅ Protect sensitive documents with encryption
- ✅ Remove metadata for privacy compliance
- ✅ Clean documents before sharing

**Note:** Ensure you have the legal right to modify any documents you process.

## 🐛 Troubleshooting

### "PasswordError: PDF is locked"
- Ensure you've entered the correct open password
- Click "Inspect" after entering the password

### "Invalid date"
- Check that day/month/year values are valid
- Ensure hours (0-23), minutes (0-59), seconds (0-59) are in range

### "Producer tag still present"
- Some PDFs may have compressed object streams
- Try running the script twice
- Use `groover.py` for more aggressive cleaning

### GUI won't start
```bash
# Reinstall tkinter (Ubuntu/Debian)
sudo apt-get install python3-tk

# Verify pikepdf installation
pip install --upgrade pikepdf
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Ajit Jadhav**
- GitHub: [@AjitJadhav-Tech](https://github.com/AjitJadhav-Tech)

## 🙏 Acknowledgments

- Built with [pikepdf](https://github.com/pikepdf/pikepdf)
- GUI powered by Tkinter
- Inspired by the need for forensic PDF tools

## 📞 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the troubleshooting section above
- Review the code comments for implementation details

---

**⚠️ Disclaimer:** This tool is provided for legitimate document management purposes. Users are responsible for ensuring they have appropriate rights to modify any documents they process.
