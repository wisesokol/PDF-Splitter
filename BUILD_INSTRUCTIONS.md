# Instructions for Building Windows Executable

## Prerequisites
- Python 3.7 or higher installed
- All dependencies from requirements.txt

## Quick Build (Recommended)

1. Double-click `build.bat` 
   - This will automatically install PyInstaller, dependencies, and build the executable

2. Find the executable at: `dist\PDF_Splitter.exe`

## Manual Build

If you prefer to build manually:

```bash
# 1. Install PyInstaller
pip install pyinstaller

# 2. Install dependencies
pip install -r requirements.txt

# 3. Build executable
pyinstaller --onefile --windowed --name "PDF_Splitter" pdf_splitter_gui.py
```

## Advanced Build (Using spec file)

If you want more control over the build process:

```bash
pyinstaller build.spec
```

## Output

The executable will be created in the `dist` folder:
- `dist\PDF_Splitter.exe` - Single executable file (can be distributed standalone)

## Notes

- The executable is standalone and doesn't require Python to be installed on the target machine
- First run may take a few seconds as the application extracts temporary files
- Windows Defender may flag the executable on first run - this is normal for PyInstaller executables. You can add an exception if needed.

## Troubleshooting

- If build fails, make sure all dependencies are installed: `pip install -r requirements.txt`
- If the executable doesn't run, try building with console: replace `--windowed` with `--console` to see error messages
- For antivirus false positives, you may need to sign the executable (requires code signing certificate)

