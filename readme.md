# 🚀 AutoTyper Pro v2.0

*The ultimate keyboard simulation tool that goes beyond basic text insertion, preserving your rich text formatting with human-like precision.*

---

## 📖 Table of Contents
- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [Under the Hood](#-under-the-hood)
- [Prerequisites](#-prerequisites)
- [Installation Guide](#-installation-guide)
- [Comprehensive Usage Guide](#-comprehensive-usage-guide)
- [User Interface Overview](#-user-interface-overview)
- [Advanced Configuration](#-advanced-configuration)
- [Troubleshooting & Limitations](#-troubleshooting--limitations)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 About the Project

AutoTyper Pro is not your average copy-paste tool. Built entirely in Python, it serves as a sophisticated automation engine designed to simulate human typing. Whether you are generating content, migrating data, or simply avoiding the appearance of automated pasting, AutoTyper Pro ensures your text is delivered exactly as it was formatted in the source document.

**Pro Tip:** For the best results when working with AI-generated content, we highly recommend first humanizing your text using [subhan.tech](https://subhan.tech). By pairing subhan.tech's natural language humanization with AutoTyper Pro's human-like typing simulation, your content will appear completely authentic and naturally written.

Unlike traditional auto-typers that strip away all context and paste raw text strings, AutoTyper Pro taps directly into the Windows Clipboard. It intercepts complex HTML formatting—including bold, italics, underlines, headings, and even lists and tables—and translates them into synchronized keyboard shortcuts on the fly. This ensures that your destination document looks exactly like your source.

---

## ✨ Key Features

### 📝 Advanced Rich Text Parsing
- **Style Preservation**: Seamlessly carries over **Bold**, *Italic*, and <ins>Underline</ins> text.
- **Structural Integrity**: Recognizes Heading tags (H1-H6) and triggers the appropriate style commands in your target word processor.
- **Complex Elements**: Automatically formats bulleted lists, numbered lists, and structured tables, interpreting them as sequential keyboard inputs.
- **Smart Cleansing**: Built-in regex filters actively strip out messy MSO (Microsoft Office) formatting junk and hidden comments, ensuring only clean layout commands are processed.

### 🤖 Human-Like Typing Simulation
- **Adjustable WPM**: Set an exact Word Per Minute (WPM) speed. The engine uses specialized delay algorithms to match the specified cadence.
- **Variable Keystroke Timing**: Rather than a static delay between characters, the delay randomly fluctuates (between 0.9x and 1.1x of the base delay) to mimic natural finger movements.
- **Simulated Errors & Corrections**: Adjust the "Accuracy" slider below 100% to introduce deliberate typos. The bot will automatically type an incorrect character and immediately backspace it, perfectly mimicking human error correction.

### 📱 Device Profile Simulation
- **Computer Mode**: Standard, steady typing cadence designed for typical desktop inputs.
- **Phone Mode**: Automatically introduces a 1.4x multiplier to inter-character delays, simulating the slightly slower, more deliberate cadence of mobile typing.

### 🛡️ Robust Fallback Systems
- If no supported rich text is found on the clipboard, the application gracefully degrades to using the plain text provided in the GUI's text box, ensuring the typing engine is never stuck.

---

## 🛠️ Under the Hood

### The Parsing Engine
When you copy text from Word or Google Docs, Windows stores various representations of that data. AutoTyper Pro explicitly targets the `HTML Format` clipboard type. It isolates the `<!--StartFragment-->` and uses BeautifulSoup4 to build a navigable tree of the text. 

As it traverses this tree, it tracks the active styles in a state dictionary. When the state changes (e.g., entering a `<b>` tag), it records an event to toggle `Ctrl+B`.

### The Synchronization Engine
The `type_segments` function is responsible for acting out the parsed script. It uses `pynput` to take control of your global keyboard. Before typing any sequence of characters, it checks its internal formatting state against the required state of the upcoming text chunk. If a mismatch is detected, it deliberately issues the required hotkey toggles (e.g., `Ctrl+I`, `Ctrl+U`) with safe, baked-in delays (0.2s) to allow the target application's buffer to catch up.

---

## 📋 Prerequisites

To run AutoTyper Pro locally, you will need the following installed on your system:
- **Python 3.8+** (Built and tested primarily on 3.10)
- **Windows OS** (Due to heavy reliance on `win32clipboard` and Windows-specific HTML clipboard fragment formatting)

---

## 💻 Installation Guide

### 1. Clone the Repository
Begin by downloading the source code to your local machine:
```bash
git clone https://github.com/yourusername/AutoTyperPro.git
cd AutoTyperPro
```

### 2. Set Up a Virtual Environment (Recommended)
Isolating your dependencies prevents conflicts with other Python projects.
```bash
python -m venv .venv
# Activate the environment
.venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
Install the required packages using the standard pip package manager:
```bash
pip install -r requirements.txt
```
*(If a requirements.txt is not provided, simply run: `pip install pynput beautifulsoup4 pyperclip pywin32`)*

---

## 🚀 Comprehensive Usage Guide

### Phase 1: Preparation
1. **Target Application:** Open the destination application where you want the text to be typed (e.g., Microsoft Word, Google Docs).
2. **Reset Styles:** Ensure the cursor is on a fresh, unformatted line. The destination document style *must* be set to "Normal" (no bold/italics toggled on).

### Phase 2: Execution
1. **Launch the App:** Run `python autotyper.py`.
2. **Copy Source:** Highlight your rich text from your source document or web page and press `Ctrl+C`.
3. **Check Status:** Look at the AutoTyper Pro GUI. The status pill should turn green/update to read: **"Status: Advanced Rich Text detected!"**
4. **Tune Parameters:** Adjust your WPM and Accuracy as needed.
5. **Start:** Click the **Start Auto Typing** button.
6. **Focus:** You have exactly 3 seconds to click back into your target document and place your blinking cursor exactly where the text should begin.

### Phase 3: Monitoring
- Do **not** touch your keyboard or mouse while the engine is typing.
- To abort an operation early, click the red **Stop Typing** button or rapidly press the `ESC` key (if hotkey support is bound).

---

## 🎨 User Interface Overview

AutoTyper Pro features a custom, premium Tkinter interface utilizing a modern, flat-design color palette (Indigo/Emerald/Charcoal) meant to feel native and responsive.

- **Status Pill:** Provides real-time feedback on clipboard detection and current engine state (Ready, Typing, Done).
- **Text Source Field:** Allows for manual raw text entry if the clipboard parsing fails or is unneeded.
- **Configuration Panel:** Clean, borderless entry fields for numeric inputs (WPM, Accuracy, Repeats).
- **Style Toggles:** Manual overrides for forcing Bold (B), Italic (I), or Underline (U) on raw text inputs.
- **Simulation Dropdown:** Toggle between "computer" and "phone" timing algorithms.

---

## ⚙️ Advanced Configuration

### Handling Specific Hotkeys
The default hotkeys used by the engine to toggle formatting in the destination app are standard Windows shortcuts:
- `Ctrl + B` (Bold)
- `Ctrl + I` (Italic)
- `Ctrl + U` (Underline)
- `Ctrl + Alt + [1-6]` (Headings)

If your target application uses different hotkeys (e.g., Markdown based editors, or foreign language OS configurations), you will need to modify the `sync_formatting()` function within `autotyper.py`.

---

## ⚠️ Troubleshooting & Limitations

- **"Keystrokes are being skipped or jumbled!"**
  - **Cause:** Your target application cannot process the simulated keystrokes as fast as AutoTyper is sending them. This often happens with heavy web-based editors.
  - **Solution:** Lower the WPM.

- **"Formatting is inverted (Bold is Normal, Normal is Bold)!"**
  - **Cause:** You started the typing process while the target document already had Bold toggled *ON*. AutoTyper toggles styles based on absolute states relative to an assumed *OFF* starting point.
  - **Solution:** Stop the script, clear the formatting in the destination document, make sure no toolbar icons are highlighted, and try again.

- **"It works with Word, but not in Notepad!"**
  - **Cause:** Notepad does not support Rich Text. Sending `Ctrl+B` strokes to Notepad will not actually make the text bold.

- **"List items aren't formatting correctly."**
  - **Cause:** AutoTyper outputs bullets as literal characters (`•`) rather than triggering the destination application's "List" formatting toggle. This is a current limitation of universally translating HTML lists across different word processors.

---

## 🗺️ Roadmap

- [ ] Add global hotkey listener for emergency Stop/Abort (e.g., `Shift+Esc`).
- [ ] Implement macOS support natively (handling `Cmd` vs `Ctrl` and `pyobjc` clipboard formats).
- [ ] Add support for dynamically passing custom hotkey configurations via a `.json` settings file.
- [ ] Improve HTML Table translation to automatically handle `Tab` delimited spacing.

---

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---
*Built with ❤️ for automation enthusiasts.*
