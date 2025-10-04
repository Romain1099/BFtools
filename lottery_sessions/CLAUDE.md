# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Description

Lottery Sessions is a student lottery application with session tracking and integrated scoring. It generates an interactive HTML interface with animations for randomly selecting students and tracking their performance over time. Built with Flask backend and ES6 modular JavaScript frontend.

## Running the Application

### Initial Setup (First Time)
```bash
init.bat
```
Creates virtual environment and installs dependencies.

### Development Mode
```bash
run.bat
```
Activates venv and runs `lottery_sessions.py`.

### Building Executable (Windows)
```bash
build.bat
```
Activates venv, installs dependencies, and generates `lottery_sessions.exe` using PyInstaller.

### Running Tests
```bash
python test_app.py
```

## Architecture Overview

### Backend (Python/Flask)
- **lottery_sessions.py** - Main Flask server with REST API endpoints, auto-finds free port and opens browser
- **backend/csv_manager.py** - CSV file operations with thread-safe locking, backups (5 max), and variant support
- **backend/session_tracker.py** - Session history tracking, cycle management, and statistics

### Frontend (ES6 Modules)
The frontend uses a **modular architecture by responsibility**. All modules are in `static/modules/`:

- **state.js** - Global state (`CONFIG`, `state`) and localStorage wrapper (`Storage`)
- **api.js** - REST API client for backend communication
- **ui.js** - DOM manipulation, modals, notifications, stats display
- **utils.js** - Reusable utility functions (date formatting, position calculations)
- **students.js** - Student management (load, display, stats)
- **classes.js** - Class/variant CRUD operations
- **cycles.js** - Cycle progress and reset logic
- **scoring.js** - Scoring panel and score recording
- **draw.js** - Lottery draw logic and badge display

**Entry point**: `static/main.js` imports modules and initializes app

**Legacy**: `static/animations.js` contains shuffle/highlight animations (not yet modularized)

### Data Flow Examples

**Initial Load**:
```
main.js → Classes.load() → API.getClasses()
       → Classes.select() → Students.load() → API.getStudents()
       → Display.updateTags() + Cycles.updateProgress()
```

**Draw Lottery**:
```
Draw.perform() → startShuffleAnimation() → Draw.selectWinners()
             → API.recordDraw() → Cycles.updateProgress()
             → Scoring.showPanel()
```

**Score Recording**:
```
Scoring.handleScore() → API.updateScore()
                      → Students.load() + Cycles.updateProgress()
                      → Display.updateTags()
```

## CSV File Format

### Structure
```csv
nom;prenom;2024-10-01;2024-10-02;2024-10-03
Dupont;Jean;2;ABS;1
Martin;Marie;;0;3
```

- **Fixed columns**: `nom`, `prenom`
- **Date columns**: Auto-added in YYYY-MM-DD format
- **Score values**: `0-3` (numeric scores), `ABS` (absent), `` (not questioned)

### Class Variants
- **Base class**: `classe_<name>.csv` (e.g., `classe_1ere-TC_QF.csv`)
- **Variant**: `classe_<name>_<type>.csv` (e.g., `classe_1ere-TC_QF_TD1.csv`)
- Variants share students (nom/prenom) but have separate history
- Base class is auto-created from variant if it doesn't exist

## Key API Endpoints

- `GET /api/classes` - List all classes
- `GET /api/classes_with_variants` - Classes grouped with variants
- `POST /api/create_variant` - Create variant of a class
- `GET /api/students/<class_name>` - Get students with history
- `POST /api/score` - Update student score (0-3 or "ABS")
- `GET /api/cycle_progress/<class_name>` - Get cycle progression
- `POST /api/reset_cycle/<class_name>` - Archive cycle and reset
- `GET /api/config` - Get animation configuration
- `POST /api/shutdown` - Graceful server shutdown

## Configuration

**File**: `data/config.json` (auto-created if missing)

Contains animation parameters:
- `animation.shuffle` - Shuffle animation settings (duration, radius, angles)
- `animation.highlight` - Highlight animation settings (rounds, delays)
- `animation.general` - General animation settings (delays, transitions)

## Key Concepts

### Sessions
- **Each day = new session**: Students become available again daily
- **ABS status**: Absent students don't count toward cycle progress
- Independent sessions: Student absent on day 1 can be selected on day 2

### Cycles
- Cycle completes when all students have a **real score (0-3)** at least once
- ABS doesn't count as "questioned" for cycle progress
- On cycle completion: archive to `data/cycles/classe_<name>_<start>_<end>.csv` and reset active class to nom/prenom only

### Draw Modes
- **Without replacement** (default): Students can't be drawn again same day
- **With replacement**: Students can be drawn multiple times same day
- **History mode**: When enabled, excludes students already questioned in cycle

## File Locking
`csv_manager.py` uses thread-safe locks (`threading.Lock`) per class file to prevent concurrent write issues. Each file gets its own lock via `_get_file_lock()`.

## PyInstaller Build
When frozen (`sys.frozen`), the app:
- Uses `sys._MEIPASS` for templates/static
- Looks for `data/` directory next to the `.exe`
- Auto-creates `data/` and `config.json` if missing
