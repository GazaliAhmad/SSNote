# SSNote™ – Stupidly Simple Notepad

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen.svg)

A lightweight, bloat-free notepad app for Windows. Built with Python and Tkinter.

- No registry entries  
- No background services  
- No clutter  
- Just a fast, minimal, single-tasking text editor

---

## 🚀 Features

- ✅ Save, open, and autosave `.txt` files  
- ✅ Recent files list (up to 5 items)  
- ✅ Dark mode with toggle (overrides system setting)  
- ✅ Word wrap toggle with saved state  
- ✅ Auto theme detection (on first launch)  
- ✅ Autosave every 2 minutes (if enabled)  
- ✅ Manual or automatic save on exit  
- ✅ Unified status bar with:
  - Current file name  
  - Word and character count  
  - Time since last save  
- ✅ MIT licensed, portable, and clean

---

## 📦 Installation (for Users)

### Option 1: Download the Executable

> Coming soon in [Releases](https://github.com/GazaliAhmad/SSNote/releases)  
> Just download and run `ssnote.exe`. No installation required.

### Option 2: Run from Source (Python 3.11+)

```bash
pip install -r requirements.txt
python ssnote.py
```

### Option 3: Build the Standalone Executable

```bash
pyinstaller --onefile --windowed --icon=ssnote.ico ssnote.py
```

---

## 🛠 Developer Setup

For contributors and developers:

```bash
pip install -r dev-requirements.txt
```

Includes optional tools:

- `pyinstaller` – for packaging  
- `black`, `flake8`, `mypy` – for code formatting, linting, and type-checking  
- `pytest` – for unit tests (planned for future)

---

## 📄 License

SSNote is released under the [MIT License](LICENSE).  
Use it, modify it, redistribute it. Attribution is appreciated but not required.

---

## 👤 Author

[Gazali Ahmad](https://github.com/GazaliAhmad)
