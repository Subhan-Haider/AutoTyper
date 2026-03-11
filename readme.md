<div align="center">

# ⌨️ AutoTyper Pro

**The ultimate keyboard simulation tool — types your rich text exactly as formatted, with human-like precision.**

[![Build EXE](https://github.com/Subhan-Haider/AutoTyper/actions/workflows/build.yml/badge.svg)](https://github.com/Subhan-Haider/AutoTyper/actions/workflows/build.yml)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)](https://github.com/Subhan-Haider/AutoTyper)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Download](https://img.shields.io/badge/Download-EXE-brightgreen?logo=github)](https://github.com/Subhan-Haider/AutoTyper/actions/workflows/build.yml)

[⬇️ Download EXE](#-download) • [🚀 Quick Start](#-quick-start) • [✨ Features](#-features) • [🐛 Troubleshooting](#-troubleshooting)

</div>

---

## 📌 What is AutoTyper Pro?

AutoTyper Pro goes far beyond basic copy-paste. It reads the **HTML formatting directly from your clipboard** (copied from Word, Google Docs, etc.) and **simulates real keystrokes** — including `Ctrl+B`, `Ctrl+I`, headings, lists, and tables — to reproduce your document exactly in the destination app.

> 💡 **Pair it with [subhan.tech](https://subhan.tech) to humanize AI-generated text first, then AutoTyper will type it out naturally — completely bypassing AI detectors.**

---

## ⬇️ Download

### Option A — Download Pre-Built EXE (Easiest)
1. Go to [**Actions → Build AutoTyper EXE**](https://github.com/Subhan-Haider/AutoTyper/actions/workflows/build.yml)
2. Click the latest successful run ✅
3. Scroll down to **Artifacts** and download **`AutoTyper-Windows`**
4. Unzip → run `AutoTyper.exe` — no Python needed!

### Option B — Run from Source
```bash
git clone https://github.com/Subhan-Haider/AutoTyper.git
cd AutoTyper
pip install pynput beautifulsoup4 pyperclip pywin32 requests
python autotyper.py
```

---

## 🚀 Quick Start

1. **Open** your destination app (Word, Google Docs, etc.) and place your cursor where typing should begin
2. **Copy** rich text from any source (`Ctrl+C`)
3. **Launch** AutoTyper Pro
4. Check the status shows **"Advanced Rich Text detected!"**
5. Click **Start Auto Typing** — you have **3 seconds** to switch to your target window
6. Done! To stop anytime, click **Stop Typing**

> ⚠️ Make sure your destination document cursor is on a **plain, unformatted line** before starting.

---

## ✨ Features

### 📝 Rich Text Formatting
| Feature | Details |
|---|---|
| **Bold / Italic / Underline** | Detects and types with `Ctrl+B`, `Ctrl+I`, `Ctrl+U` |
| **Headings (H1–H6)** | Applies heading styles via `Ctrl+Alt+1–6` |
| **Bullet & Numbered Lists** | Outputs list prefixes (`•`, `1.`) automatically |
| **Tables** | Parses and types table content row by row |
| **MSO Junk Removal** | Strips Microsoft Office formatting clutter before parsing |

### 🤖 Human-Like Simulation
| Setting | Details |
|---|---|
| **WPM Speed** | Adjustable words-per-minute (default: 120) |
| **Accuracy** | Set 1–100% — below 100% introduces & corrects random typos |
| **Natural Timing** | Keystroke delays vary ±10% randomly to mimic real humans |
| **Device Mode** | `Computer` or `Phone` (phone adds 1.4× delay) |
| **Loop / Repeat** | Type the same content multiple times automatically |

### 🤖 Auto-Humanize Integration
- Toggle **"Auto-Humanize"** to send your text through [subhan.tech](https://subhan.tech) before typing
- Makes AI-written content undetectable to GPTZero and other AI detectors

---

## 🖥️ Interface

```
┌─────────────────────────────────────────┐
│           AutoTyper Pro v2.0            │
│         [ Ready to detect... ]          │
├─────────────────────────────────────────┤
│  ⌨️ TEXT SOURCE                         │
│  ┌───────────────────────────────────┐  │
│  │ Or type manual text here...       │  │
│  └───────────────────────────────────┘  │
│                                         │
│  ⏱️ CONFIGURATION                       │
│  Speed (WPM):          [ 120 ]          │
│  Accuracy (1-100%):    [ 100 ]          │
│  Repeat Count:         [  1  ]          │
│  Simulation Mode:      [Computer ▾]     │
│                                         │
│  [B] [I] [U]  🔁 Loop  🤖 Auto-Humanize│
├─────────────────────────────────────────┤
│        [ ✅ Start Auto Typing ]         │
│          [ ❌ Stop Typing ]             │
└─────────────────────────────────────────┘
```

---

## ⚙️ How It Works

1. **Clipboard Reading** — Reads `HTML Format` from the Windows clipboard (set by Word/Docs on copy)
2. **HTML Parsing** — BeautifulSoup4 traverses the DOM tree, tracking active styles in a state dictionary
3. **Segment Building** — Converts the HTML tree into an ordered list of `{text, format}` segments
4. **Keyboard Playback** — `pynput` replays each segment, toggling formatting hotkeys when the style changes

---

## ⚠️ Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Keystrokes skipped or jumbled | Target app can't keep up | Lower the WPM |
| Formatting is inverted (bold where it shouldn't be) | Bold was already ON in destination doc | Reset all formatting to Normal first |
| Works in Word but not Notepad | Notepad doesn't support rich text | Use a rich text editor |
| Lists not formatting as lists | AutoTyper types bullet chars, not list toggles | Expected behavior — current limitation |

---

## 🗺️ Roadmap

- [ ] Global hotkey for emergency stop (`Shift+Esc`)
- [ ] macOS support (`Cmd` keys + macOS clipboard formats)
- [ ] Custom hotkey config via `.json` settings file
- [ ] Tab-based table spacing for better cross-app compatibility

---

## 🤝 Contributing

1. Fork the project
2. Create your branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m "Add my feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

Built with ❤️ by [Subhan Haider](https://subhan.tech) • [subhan.tech](https://subhan.tech)

</div>
