# File Backup Logger

## Description
A program that backs up files and directories with versioning, logs the operations locally, and includes a GUI. Alternatively, the program can be written in C++ if you're more comfortable working with it.

## Getting Started
1. Clone this repository or download the files.
2. Install required packages if necessary.
3. Run the `main.py` or `main.cpp` file to get started.

Keep in mind that the code must be written in OOP.

## Tasks
- Research how to copy folders in Python using `shutil`. Create initial project folder and file structure.
- Implement basic folder selection (manually or via `input()`). Write code to copy folder contents to a backup location.
- Add timestamp and version of the program is backuping an software directory to backup folder names (e.g., backup_2025-05-01_v227-3-3).
- Add error handling (e.g., non-existent folder, permission denied). Start writing a simple .log file (backup time, status).
- Clean up code. Create `backup.py` and move reusable functions there. Test with multiple folders and large files.
- Add ZIP compression to backups using `zipfile`. Let user choose between zipped or plain copy.
- Improve the log format. Add file count and backup duration.
- Add tkinter GUI to select source/destination folders and trigger backup.
- Add config file (e.g., .json) to store user preferences (folders, backup interval).
- Final testing. Create README with instructions and screenshots. Submit as Git repo.

## Key Features
| Feature | What it does |
|---------|--------------|
| **ZIP ⇄ Folder toggle** | Choose compressed or plain backups with a single checkbox/flag |
| **Rotating logs** | `logs/backup.log` keeps the last 5 × 512 KB runs |
| **Real progress bar** | Per-file % progress in the GUI (threads keep UI responsive) |
| **Auto version-bump** | `config.json` patch number increments after every successful run |
| **Config file** | Edit defaults without touching Python (`backup_root`, `compress`, etc.) |
| **pytest suite** | Six tests guard the core engine + GUI logic (headless) |
---

## 🏃‍♂️ Quick Start

```bash
# clone and enter repo
git clone https://github.com/your-account/file-backup-logger.git
cd file-backup-logger

# 1️⃣ create & activate a virtual env
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows

# 2️⃣ install dev dependencies (only pytest)
pip install -r requirements.txt

# 3️⃣ launch the GUI
python -m src.gui
```

## Project layout
file-backup-logger/
├─ src/
│  ├─ backup.py    ← engine (copy / zip / versioning / progress)
│  ├─ config.py    ← JSON prefs (created on first run)
│  ├─ logger.py    ← rotating log wrapper
│  └─ gui.py       ← Tkinter front-end
├─ tests/          ← pytest cases (headless)
├─ backups/        ← generated at runtime (git-ignored)
├─ logs/           ← rotating log files (git-ignored)
├─ README.md
└─ requirements.txt
