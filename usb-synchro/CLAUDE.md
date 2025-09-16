# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a USB synchronization program designed to facilitate bidirectional file synchronization between a computer and USB drives. The primary use case is uploading course preparations to USB drives and downloading session reports for internal processing.

## Core Functionality

The application must implement:

1. **USB Detection & Management**
   - Automatic detection of connected USB drives
   - User selection interface for multiple drives
   - Storage of previously used drives
   - Default USB drive configuration

2. **Bidirectional Synchronization**
   - **Upload Sync (Up)**: Synchronize specified computer directories to USB drive
   - **Download Sync (Down)**: Synchronize USB directories to specified computer directories
   - Separate configuration for each direction to prevent conflicts

3. **User Interface Requirements**
   - Drive selection interface
   - Directory mapping configuration
   - Manual synchronization triggers via buttons
   - Status feedback and progress indicators

## Architecture Considerations

### Core Components
- **USB Detection Module**: Handle drive enumeration and monitoring
- **Configuration Manager**: Store drive preferences and directory mappings
- **Synchronization Engine**: Handle file comparison and copying operations
- **UI Layer**: User interface for configuration and manual triggers

### Data Storage
- Configuration files for storing:
  - Default USB drive preferences
  - Directory mapping configurations (up/down)
  - Previously used drives list

### Synchronization Strategy
- Implement separate up/down sync configurations to avoid conflicts
- File comparison based on modification dates and sizes
- Progress tracking and error handling for large file operations

## Development Commands

### Installation
```bash
# Installation automatique (Windows)
install.bat

# Installation manuelle
python -m pip install -r requirements.txt
```

### Running the Application
```bash
# Lancement automatique (Windows)
run.bat

# Lancement manuel
python main.py
```

### Project Structure
```
src/
├── __init__.py          # Package initialization
├── usb_detector.py      # USB drive detection and monitoring
├── config_manager.py    # Configuration storage and management
├── sync_engine.py       # File synchronization logic
└── gui.py              # CustomTkinter GUI interface
main.py                 # Application entry point
requirements.txt        # Python dependencies
config/                 # Configuration storage directory
```

## Development Notes

- Target platform: Windows (based on working directory path)
- Uses `psutil` for USB detection and `customtkinter` for modern GUI
- Configuration stored in `~/.synchro_usb/config.json`
- Threading used for non-blocking synchronization operations
- Progress callbacks for real-time UI updates