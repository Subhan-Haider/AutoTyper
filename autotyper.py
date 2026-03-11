import tkinter as tk
from tkinter import messagebox, ttk
from pynput.keyboard import Controller, Key, Listener
import threading
import time
import random
import pyperclip
import platform

# Windows-only: rich HTML clipboard support
if platform.system() == "Windows":
    try:
        import win32clipboard
        CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")
    except Exception:
        win32clipboard = None
        CF_HTML = None
else:
    win32clipboard = None
    CF_HTML = None

from bs4 import BeautifulSoup, NavigableString
import re
import webbrowser
import requests

keyboard = Controller()
typingActive = False
loopTyping = False

# --- Styles and Colors ---
# --- 🎨 Premium Design System ---
COLORS = {
    "window_bg": "#F3F4F6",    # Soft gray background
    "card_bg": "#FFFFFF",      # Pure white cards
    "fg_text": "#111827",      # Deep charcoal
    "fg_secondary": "#6B7280", # Muted gray
    "accent": "#4F46E5",       # Indigo primary
    "accent_hover": "#4338CA", # Darker indigo
    "success": "#10B981",      # Emerald Green
    "success_hover": "#059669",
    "danger": "#EF4444",       # Modern red
    "danger_hover": "#DC2626",
    "border": "#E5E7EB",       # Subtle borders
    "input_focus": "#818CF8"   # Light indigo for focus
}

FONTS = {
    "title": ("Segoe UI", 20, "bold"),
    "h2": ("Segoe UI", 12, "bold"),
    "body": ("Segoe UI", 10),
    "caption": ("Segoe UI", 9),
    "mono": ("Consolas", 10)
}

class PremiumButton(tk.Button):
    """A button with modern styling and hover effects."""
    def __init__(self, master, hover_bg, **kwargs):
        self.normal_bg = kwargs.get("bg")
        self.hover_bg = hover_bg
        super().__init__(master, **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e): self['bg'] = self.hover_bg
    def on_leave(self, e): self['bg'] = self.normal_bg

# --- 1. Clipboard Rich Text Detection ---

def get_clipboard_html():
    """Tries to retrieve HTML content from the Windows clipboard."""
    if not CF_HTML: return None
    try:
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(CF_HTML):
            data = win32clipboard.GetClipboardData(CF_HTML)
            win32clipboard.CloseClipboard()
            if isinstance(data, bytes):
                return data.decode("utf-8", errors="ignore")
            return data
        win32clipboard.CloseClipboard()
    except Exception as e:
        print(f"Clipboard read error: {e}")
    return None

# --- 2 & 3. HTML Parsing Engine & Formatting Detection ---

def clean_html(html_content):
    """Isolate the fragment and strip out MSO junk before doing anything else."""
    fragment_match = re.search(r"<!--StartFragment-->(.*)<!--EndFragment-->", html_content, re.DOTALL)
    html_body = fragment_match.group(1) if fragment_match else html_content

    html_body = re.sub(r"<!?\[if !supportLists\].*?<!?\[endif\]>", "", html_body, flags=re.DOTALL)
    html_body = re.sub(r"\[if !supportLists\].*?\[endif\]", "", html_body, flags=re.DOTALL)
    html_body = re.sub(r"<!--.*?-->", "", html_body, flags=re.DOTALL)
    html_body = re.sub(r"<!?\[endif\]>", "", html_body) 
    html_body = re.sub(r"<!?\[if !.*?\]>", "", html_body)
    html_body = re.sub(r"mso-.*?:\s*.*?(;|$)", "", html_body) # Specific MS Word style junk
    return html_body

def humanize_text_api(text_content):
    """Send text or cleaned HTML to subhan.tech API to make it undetectable."""
    url = "https://www.subhan.tech/api/humanize"
    payload = {
        "inputTextBox": text_content,
        "rangeSlider": 0.9,
        "aiContentDetectorDropdown": "GPTZero.me",
        "apiKey": "",
        "mode": "natural"
    }
    try:
        response = requests.post(url, json=payload, timeout=25)
        response.raise_for_status()
        data = response.json()
        if "paraphrased_text" in data:
            return data["paraphrased_text"]
    except Exception as e:
        print(f"Humanize API error: {e}")
    return text_content

def parse_html_formatting(html_body):
    """
    Parses HTML content into structured segments.
    Detects Bold, Italic, Underline, Font-size, Headings, Lists, and Tables.
    """
    soup = BeautifulSoup(html_body, "html.parser")
    segments = []

    def get_font_size(node):
        style = node.get("style", "").lower()
        size_match = re.search(r"font-size:\s*(\d+)pt", style)
        if size_match: return int(size_match.group(1))
        size_match = re.search(r"font-size:\s*(\d+)px", style)
        if size_match: return int(int(size_match.group(1)) * 0.75) # Approx px to pt
        return None

    def process_node(node, current_format):
        if isinstance(node, NavigableString):
            text = str(node)
            # Normalize Word whitespace (tab/newline chars in NavigableStrings)
            text = text.replace("\r", "")
            if not text.strip() and text != " ":
                # If it's just formatting whitespace (newlines between tags), ignore it
                return
                
            # Split text by newlines so we can handle them as distinct events
            parts = re.split(r"(\n)", text)
            for part in parts:
                if part == "\n":
                    segments.append({"type": "newline", "content": "\n", "format": {}})
                elif part:
                    segments.append({
                        "type": "text",
                        "content": part,
                        "format": current_format.copy()
                    })
        elif node.name == "br":
            segments.append({"type": "newline", "content": "\n", "format": {}})
        elif node.name in ["p", "div", "tr", "h1", "h2", "h3", "h4", "h5", "h6"]:
            # Ensure a clean break before a block element
            if segments and segments[-1]["type"] != "newline":
                segments.append({"type": "newline", "content": "\n", "format": {}})
            
            fmt = current_format.copy()
            if node.name.startswith("h"):
                fmt["heading"] = int(node.name[1])
                fmt["bold"] = True

            for child in node.children:
                process_node(child, fmt)
            
            # Ensure a clean break after a block element
            if segments and segments[-1]["type"] != "newline":
                segments.append({"type": "newline", "content": "\n", "format": {}})

        # List Detection
        elif node.name in ["ul", "ol"]:
            list_type = node.name 
            items = node.find_all("li", recursive=False)
            for i, li in enumerate(items, 1):
                prefix = "• " if list_type == "ul" else f"{i}. "
                segments.append({"type": "text", "content": prefix, "format": current_format})
                for child in li.children:
                    process_node(child, current_format)
                segments.append({"type": "newline", "content": "\n", "format": {}})

        # Table Detection
        elif node.name == "table":
            rows = []
            for tr in node.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if cells: rows.append(cells)
            if rows:
                segments.append({"type": "table", "content": rows, "format": current_format})

        # Formatting Nodes
        else:
            new_fmt = current_format.copy()
            if node.name in ["b", "strong"]: new_fmt["bold"] = True
            if node.name in ["i", "em"]: new_fmt["italic"] = True
            if node.name in ["u"]: new_fmt["underline"] = True
            
            style = node.get("style", "").lower()
            if "font-weight:700" in style or "bold" in style: new_fmt["bold"] = True
            if "italic" in style: new_fmt["italic"] = True
            if "underline" in style: new_fmt["underline"] = True
            
            size = get_font_size(node)
            if size: new_fmt["size"] = size

            for child in node.children:
                process_node(child, new_fmt)

    initial_format = {"bold": False, "italic": False, "underline": False, "size": None, "heading": None}
    process_node(soup, initial_format)
    
    # Pass 2: Style Optimization (Merge identical adjacent segments & handle spaces)
    if not segments: return []
    
    # Merge spaces into surrounding formatting to prevent toggle flickering
    for i in range(1, len(segments) - 1):
        if segments[i]["type"] == "text":
            content = segments[i].get("content", "")
            if isinstance(content, str) and content.isspace():
                f1 = segments[i-1].get("format")
                f2 = segments[i+1].get("format")
                if isinstance(f1, dict) and f1 == f2:
                    segments[i]["format"] = f1.copy()

    optimized = []
    for s in segments:
        if not optimized:
            if s["type"] != "newline": 
                optimized.append(s)
            continue
            
        # Merge identical adjacent text segments
        prev = optimized[-1]
        if s["type"] == "text" and prev["type"] == "text" and s["format"] == prev["format"]:
            prev["content"] = str(prev["content"]) + str(s["content"])
        
        # Deduplicate consecutive newlines
        elif s["type"] == "newline" and prev["type"] == "newline":
            continue
        else:
            optimized.append(s)
    
    # Remove any trailing newline junk
    while optimized and optimized[-1]["type"] == "newline":
        optimized.pop()
            
    return optimized

# --- 10. AutoTyper Execution ---

def type_segments(segments, wpm, accuracy, device):
    global typingActive
    delay = 60 / (wpm * 5)
    if device == "phone": delay *= 1.4
    
    # State tracking
    current_fmt = {"bold": False, "italic": False, "underline": False, "heading": None}

    def safe_tap(key, ctrl=False, alt=False):
        """Simulate a safe, deliberate key interaction."""
        if ctrl: keyboard.press(Key.ctrl)
        if alt: keyboard.press(Key.alt)
        time.sleep(0.05)
        keyboard.tap(key)
        time.sleep(0.05)
        if alt: keyboard.release(Key.alt)
        if ctrl: keyboard.release(Key.ctrl)
        time.sleep(0.2) # Essential buffer for the Word/OS input buffer

    def reset_styles():
        """Aggressive reset to Normal formatting."""
        nonlocal current_fmt
        safe_tap('b', ctrl=True); current_fmt["bold"] = False
        safe_tap('b', ctrl=True); # Toggle twice to ensure we know current state? No, safer to just tell user.
        # Actually, let's just force whatever our FIRST segment expects.
        current_fmt = {"bold": False, "italic": False, "underline": False, "heading": None}

    def sync_formatting(target_fmt):
        nonlocal current_fmt
        # Bold
        if target_fmt.get("bold", False) != current_fmt["bold"]:
            safe_tap('b', ctrl=True)
            current_fmt["bold"] = target_fmt.get("bold")
        # Italic
        if target_fmt.get("italic", False) != current_fmt["italic"]:
            safe_tap('i', ctrl=True)
            current_fmt["italic"] = target_fmt.get("italic")
        # Underline
        if target_fmt.get("underline", False) != current_fmt["underline"]:
            safe_tap('u', ctrl=True)
            current_fmt["underline"] = target_fmt.get("underline")
        # Headings
        if target_fmt.get("heading") != current_fmt["heading"]:
            level = target_fmt.get("heading")
            safe_tap(str(level) if level else '0', ctrl=True, alt=True)
            current_fmt["heading"] = level

    # STARTUP: Assume Word is in 'Normal' mode (Style OFF). 
    # If the user has formatting ON, they should turn it OFF first.
    current_fmt = {"bold": False, "italic": False, "underline": False, "heading": None}

    for seg in segments:
        if not typingActive: break

        if seg["type"] == "newline":
            keyboard.tap(Key.enter)
            time.sleep(0.5) # Give Word time to auto-list or indent
            continue
            
        if seg["type"] == "text":
            sync_formatting(seg["format"])
            
            for char in seg["content"]:
                if not typingActive: return
                
                # Accuracy
                if accuracy < 100 and random.randint(1, 100) > accuracy:
                    keyboard.type(random.choice("abcdefghijklmnopqrstuvwxyz"))
                    time.sleep(delay)
                    keyboard.tap(Key.backspace)
                    time.sleep(delay)
                
                if char == ' ':
                    keyboard.tap(Key.space)
                    time.sleep(delay * 1.5)
                else:
                    keyboard.type(char) 
                    time.sleep(delay * random.uniform(0.9, 1.1))

    # Reset at end
    sync_formatting({"bold": False, "italic": False, "underline": False, "heading": None})

# --- GUI Logic ---

def start_typing():
    global typingActive, loopTyping
    
    html = get_clipboard_html()
    if html:
        try:
            html = clean_html(html)
            if humanize_var.get():
                status_var.set("Status: Humanizing rich text...")
                root.update()
                html = humanize_text_api(html)
                
            segments = parse_html_formatting(html)
            status_var.set("Status: Advanced Rich Text detected!")
        except Exception as e:
            print(f"Parse error: {e}")
            html = None

    if not html:
        # Fallback to text box
        try:
            txt = text_box.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
        except tk.TclError:
            txt = text_box.get("1.0", tk.END).strip()
        
        if not txt:
            messagebox.showwarning("Empty", "No formatted content in clipboard or text in box.")
            return
            
        if humanize_var.get():
            status_var.set("Status: Humanizing text...")
            root.update()
            txt = humanize_text_api(txt)
            
        fmt = {"bold": bold_var.get(), "italic": italic_var.get(), "underline": underline_var.get(), "size": None, "heading": None}
        segments = [{"type": "text", "content": txt, "format": fmt}]
        status_var.set("Status: Basic text fallback.")

    try:
        wpm = int(wpm_entry.get())
        acc = int(accuracy_entry.get())
        loop = loop_var.get()
        repeat = int(repeat_entry.get())
        dev = device_var.get()
    except:
        messagebox.showerror("Error", "Invalid numeric settings.")
        return

    typingActive = True
    start_btn.config(state="disabled")

    def run():
        global typingActive
        count = 0
        while typingActive and (loop or count < repeat):
            status_var.set(f"Typing... (Round {count+1})")
            type_segments(segments, wpm, acc, dev)
            count += 1
            if typingActive and (loop or count < repeat):
                time.sleep(1)
        
        status_var.set("Status: Done")
        start_btn.config(state="normal")
        typingActive = False

    # Start countdown
    def countdown(n):
        global typingActive
        if not typingActive: return
        if n > 0:
            status_var.set(f"Starting in {n}s...")
            root.after(1000, countdown, n-1)
        else:
            threading.Thread(target=run, daemon=True).start()
    
    countdown(3)

def stop_typing():
    global typingActive
    typingActive = False
    status_var.set("Status: Stopped")

# --- GUI Setup ---
# --- 🖥️ GUI Structure ---
root = tk.Tk()
root.title("AutoTyper Pro v2.0")
root.geometry("560x780")
root.configure(bg=COLORS["window_bg"])

# --- Header Layer ---
header_frame = tk.Frame(root, bg=COLORS["window_bg"])
header_frame.pack(fill="x", pady=(30, 10))

tk.Label(header_frame, text="AutoTyper Pro", bg=COLORS["window_bg"], fg=COLORS["accent"], font=FONTS["title"]).pack()
status_pill = tk.Frame(root, bg=COLORS["card_bg"], bd=0, highlightthickness=0)
status_pill.pack(pady=5)

status_var = tk.StringVar(value="Ready to detect clipboard...")
tk.Label(status_pill, textvariable=status_var, bg=COLORS["card_bg"], fg=COLORS["fg_secondary"], font=FONTS["caption"], padx=15, pady=4).pack()

# --- Main Card ---
main_card = tk.Frame(root, bg=COLORS["card_bg"], bd=0, highlightthickness=0)
main_card.pack(fill="both", expand=True, padx=30, pady=20)

# Instruction Section
tk.Label(main_card, text="⌨️ TEXT SOURCE", bg=COLORS["card_bg"], fg=COLORS["fg_secondary"], font=FONTS["h2"]).pack(anchor="w", padx=20, pady=(20, 5))
tk.Label(main_card, text="Copy from Word/Docs to auto-detect formatting.", bg=COLORS["card_bg"], fg=COLORS["fg_secondary"], font=FONTS["caption"]).pack(anchor="w", padx=20)

text_box = tk.Text(main_card, height=3, bg=COLORS["window_bg"], fg=COLORS["fg_text"], borderwidth=0, font=FONTS["mono"], padx=10, pady=10)
text_box.pack(fill="x", padx=20, pady=10)
text_box.insert("1.0", "Or type manual text here...")

# Settings Section
tk.Label(main_card, text="⏱️ CONFIGURATION", bg=COLORS["card_bg"], fg=COLORS["fg_secondary"], font=FONTS["h2"]).pack(anchor="w", padx=20, pady=(15, 5))

def add_setting_row(parent, label, default_val):
    row = tk.Frame(parent, bg=COLORS["card_bg"])
    row.pack(fill="x", padx=20, pady=4)
    tk.Label(row, text=label, bg=COLORS["card_bg"], fg=COLORS["fg_text"], font=FONTS["body"], width=18, anchor="w").pack(side="left")
    ent = tk.Entry(row, bg=COLORS["window_bg"], fg=COLORS["fg_text"], borderwidth=0, highlightthickness=0, font=FONTS["mono"])
    ent.insert(0, default_val)
    ent.pack(side="right", fill="x", expand=True, ipady=4)
    return ent

wpm_entry = add_setting_row(main_card, "Speed (WPM):", "120")
accuracy_entry = add_setting_row(main_card, "Accuracy (1-100%):", "100")
repeat_entry = add_setting_row(main_card, "Repeat Count:", "1")

# Device Dropdown
dev_row = tk.Frame(main_card, bg=COLORS["card_bg"])
dev_row.pack(fill="x", padx=20, pady=4)
tk.Label(dev_row, text="Simulation Mode:", bg=COLORS["card_bg"], fg=COLORS["fg_text"], font=FONTS["body"], width=18, anchor="w").pack(side="left")
device_var = tk.StringVar(value="computer")
dev_menu = ttk.OptionMenu(dev_row, device_var, "computer", "computer", "phone")
dev_menu.configure(style="TCombobox") # Using a clean style potentially
dev_menu.pack(side="right", fill="x", expand=True)

# Formatting Toggles
style_frame = tk.Frame(main_card, bg=COLORS["card_bg"])
style_frame.pack(fill="x", padx=20, pady=(20, 10))

def create_toggle(parent, text, var):
    cb = tk.Checkbutton(parent, text=text, variable=var, bg=COLORS["card_bg"], 
                        activebackground=COLORS["card_bg"], fg=COLORS["fg_text"], 
                        font=FONTS["caption"], selectcolor=COLORS["card_bg"])
    cb.pack(side="left", padx=5)

bold_var, italic_var, underline_var, loop_var, humanize_var = tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar()
create_toggle(style_frame, "B", bold_var)
create_toggle(style_frame, "I", italic_var)
create_toggle(style_frame, "U", underline_var)
create_toggle(style_frame, "🔁 Loop", loop_var)
create_toggle(style_frame, "🤖 Auto-Humanize", humanize_var)

# --- Action Layer ---
footer = tk.Frame(root, bg=COLORS["window_bg"])
footer.pack(fill="x", pady=20)

start_btn = PremiumButton(footer, text="Start Auto Typing", command=start_typing, 
                          bg=COLORS["success"], fg="white", font=FONTS["h2"], 
                          hover_bg=COLORS["success_hover"], relief="flat", padx=50, pady=12)
start_btn.pack()

stop_btn = PremiumButton(footer, text="Stop Typing (ESC)", command=stop_typing, 
                         bg=COLORS["danger"], fg="white", font=FONTS["caption"], 
                         hover_bg=COLORS["danger_hover"], relief="flat", padx=20, pady=5)
stop_btn.pack(pady=10)

# The first element packed with side="bottom" goes to the very bottom
subhan_link = tk.Label(root, text="💡 Need to bypass AI detectors? Humanize text at subhan.tech", 
                       bg=COLORS["window_bg"], fg=COLORS["accent"], font=FONTS["caption"], cursor="hand2")
subhan_link.pack(side="bottom", pady=(0, 20))

def _on_enter(e): subhan_link.config(fg=COLORS["accent_hover"])
def _on_leave(e): subhan_link.config(fg=COLORS["accent"])
subhan_link.bind("<Enter>", _on_enter)
subhan_link.bind("<Leave>", _on_leave)
subhan_link.bind("<Button-1>", lambda e: webbrowser.open("https://subhan.tech"))

tk.Label(root, text="Pro Features: Auto-Headings • Tables • Bullet Lists", 
         bg=COLORS["window_bg"], fg=COLORS["fg_secondary"], font=FONTS["caption"]).pack(side="bottom", pady=5)

root.mainloop()
