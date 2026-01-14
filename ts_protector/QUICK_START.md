# Quick Start Guide - TS Protector Pro

Get up and running with TS Protector Pro in 5 minutes!

## Prerequisites

- Windows 10/11 (64-bit)
- Python 3.10 or higher
- Internet connection

## Installation

### Method 1: Run from Source (Development)

1. **Clone and navigate to project**
   ```bash
   cd ts_protector
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

### Method 2: Build Executable

1. **Install build dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **Build the executable**
   ```bash
   pyinstaller build.spec
   ```

3. **Run the executable**
   ```bash
   dist\TSProtectorPro.exe
   ```

## First Launch

1. **WARP Check**: If Cloudflare WARP is not installed, you'll see a prompt
   - Click "Yes" to auto-install (requires admin rights)
   - Or download manually from: https://1.1.1.1/

2. **Enable Auto-Detection**
   - Check ✓ "Auto-detect TeamSpeak"
   - The app will now monitor for TeamSpeak

3. **Optional Settings**
   - ☑ Start with Windows - Launch on boot
   - ☑ Minimize to tray - Hide to system tray

## Usage

### Automatic Mode (Recommended)
1. Enable "Auto-detect TeamSpeak"
2. Launch TeamSpeak → VPN connects automatically
3. Close TeamSpeak → VPN disconnects automatically

### Manual Mode
1. Click "CONNECT" button
2. Use TeamSpeak
3. Click "DISCONNECT" when done

## Verify It's Working

1. **Check Status**: Should show green indicator when connected
2. **Check IP**: Your IP should change after connecting
3. **Check Log**: Activity log shows connection events

## Troubleshooting

### WARP Not Found
```bash
# Check if WARP is installed
dir "C:\Program Files\Cloudflare\Cloudflare WARP\warp-cli.exe"

# If not found, download from: https://1.1.1.1/
```

### TeamSpeak Not Detected
- Verify TeamSpeak is running
- Check Task Manager for "ts3client_win64.exe"
- Try manual mode if auto-detection fails

### Permission Issues
- Run as Administrator (right-click → "Run as administrator")
- Required for WARP installation and registry access

## Common Commands

### Check WARP Status
```bash
warp-cli status
```

### Manual WARP Connection
```bash
warp-cli connect
warp-cli disconnect
```

### View Logs
```bash
# Windows
%APPDATA%\TSProtectorPro\logs\activity.log
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Report issues on GitHub

## Support

- **Issues**: GitHub Issues
- **Questions**: GitHub Discussions

---

**Need help?** Open an issue with:
- OS version (Windows 10/11)
- Python version (`python --version`)
- Error message or screenshot
- Steps to reproduce

Happy protecting! 🛡️
