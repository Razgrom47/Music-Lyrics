import tkinter as tk
from tkinter import font as tkfont
import os
import time
from typing import List, Optional

# ========================= CONFIGURATION =========================
BASE_LYRICS_DIR = os.path.join(os.getcwd(), "lyrics")

# Midnight Rock
# BG_COLOR = "#0f0a1f"
# TEXT_COLOR = "#ffe8c4"
# TITLE_COLOR = "#ff79c6"
# SELECTED_COLOR = "#50fa7b"
# INSTRUCTION_COLOR = "#bd93f9"

# Cyber Neon
# BG_COLOR = "#0d0d1a"
# TEXT_COLOR = "#e0f8ff"
# TITLE_COLOR = "#00f5ff"
# SELECTED_COLOR = "#ff00aa"
# INSTRUCTION_COLOR = "#8899ff"

# Theater Black
# BG_COLOR = "#050505"
# TEXT_COLOR = "#f5f0e6"
# TITLE_COLOR = "#a8d4ff"
# SELECTED_COLOR = "#ffeb3b"
# INSTRUCTION_COLOR = "#999999"

# Deep Ocean
BG_COLOR = "#0a0a1f"
TEXT_COLOR = "#f8f1d9"
TITLE_COLOR = "#7cc6ff"
SELECTED_COLOR = "#ffd700"
INSTRUCTION_COLOR = "#88aadd"

TITLE_FONT_SIZE = 68
BLOCK_FONT_SIZE = 62
MENU_FONT_SIZE = 48
SMALL_FONT_SIZE = 28

INSTRUCTIONS_MENU = "↑↓ Navigate    ENTER Select    Q Back    ESC Quit"
INSTRUCTIONS_LYRICS = "ENTER Next block    Q Previous    Hold T (3 sec) → Menu    ESC Quit"
# ================================================================

class LyricsApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Lyrics Display")
        
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg=BG_COLOR)
        self.root.config(cursor="none")

        self.screen_width = self.root.winfo_screenwidth()

        # Fonts
        self.font_title = tkfont.Font(family="Arial", size=TITLE_FONT_SIZE, weight="bold")
        self.font_block = tkfont.Font(family="Arial", size=BLOCK_FONT_SIZE, weight="bold")
        self.font_menu = tkfont.Font(family="Arial", size=MENU_FONT_SIZE, weight="bold")
        self.font_small = tkfont.Font(family="Arial", size=SMALL_FONT_SIZE)

        # State
        self.state = "folder_select"
        self.folders: List[str] = []
        self.songs: List[str] = []
        self.lyrics_blocks: List[str] = []
        self.selected_folder = ""
        self.song_title = ""

        self.folder_idx = 0
        self.song_idx = 0
        self.block_idx = 0

        # Hold 'T' handling (fixed)
        self.t_hold_start: Optional[float] = None
        self.hold_job = None

        self.main_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.main_frame.pack(fill="both", expand=True)

        os.makedirs(BASE_LYRICS_DIR, exist_ok=True)
        self.refresh_folders()

        # Key bindings
        self.root.bind("<Escape>", lambda e: self.root.quit())
        self.root.bind("<Key>", self.on_key_press)

        self.show_current_screen()

    def refresh_folders(self):
        self.folders = sorted([
            f for f in os.listdir(BASE_LYRICS_DIR)
            if os.path.isdir(os.path.join(BASE_LYRICS_DIR, f))
        ])

    def get_txt_files(self, folder: str) -> List[str]:
        path = os.path.join(BASE_LYRICS_DIR, folder)
        return sorted([f for f in os.listdir(path) if f.lower().endswith('.txt')])

    def load_lyrics(self, filepath: str) -> List[str]:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            blocks = [block.strip() for block in content.split("\n\n") if block.strip()]
            return blocks
        except Exception:
            return ["Error loading lyrics file"]

    # ====================== SCREEN DRAWING ======================
    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_folder_select(self):
        self.clear_screen()
        tk.Label(self.main_frame, text="Select Folder", font=self.font_title,
                 fg=TITLE_COLOR, bg=BG_COLOR).pack(pady=60)

        for i, folder in enumerate(self.folders):
            color = SELECTED_COLOR if i == self.folder_idx else TEXT_COLOR
            tk.Label(self.main_frame, text=folder, font=self.font_menu,
                     fg=color, bg=BG_COLOR).pack(pady=12)

        tk.Label(self.main_frame, text=INSTRUCTIONS_MENU, font=self.font_small,
                 fg=INSTRUCTION_COLOR, bg=BG_COLOR).pack(side="bottom", pady=40)

    def show_song_select(self):
        self.clear_screen()
        title = f"Songs in: {self.selected_folder}"
        tk.Label(self.main_frame, text=title, font=self.font_title,
                 fg=TITLE_COLOR, bg=BG_COLOR).pack(pady=60)

        song_names = [os.path.splitext(s)[0].replace("_", " ").title() for s in self.songs]

        for i, name in enumerate(song_names):
            color = SELECTED_COLOR if i == self.song_idx else TEXT_COLOR
            tk.Label(self.main_frame, text=name, font=self.font_menu,
                     fg=color, bg=BG_COLOR).pack(pady=12)

        tk.Label(self.main_frame, text=INSTRUCTIONS_MENU, font=self.font_small,
                 fg=INSTRUCTION_COLOR, bg=BG_COLOR).pack(side="bottom", pady=40)

    def show_lyrics(self):
        self.clear_screen()

        tk.Label(self.main_frame, text=self.song_title, font=self.font_title,
                 fg=TITLE_COLOR, bg=BG_COLOR).pack(pady=30)

        if self.lyrics_blocks and 0 <= self.block_idx < len(self.lyrics_blocks):
            block_text = self.lyrics_blocks[self.block_idx]

            msg = tk.Message(self.main_frame, text=block_text,
                             font=self.font_block,
                             fg=TEXT_COLOR,
                             bg=BG_COLOR,
                             width=int(self.screen_width * 0.85),
                             justify="center")
            msg.pack(expand=True, fill="both", padx=60, pady=20)

            progress = f"{self.block_idx + 1} / {len(self.lyrics_blocks)}"
            tk.Label(self.main_frame, text=progress, font=self.font_small,
                     fg=INSTRUCTION_COLOR, bg=BG_COLOR).pack(side="bottom", pady=10)
        else:
            tk.Label(self.main_frame, text="End of song\nPress ENTER to go back",
                     font=self.font_menu, fg=TEXT_COLOR, bg=BG_COLOR, justify="center").pack(expand=True)

        tk.Label(self.main_frame, text=INSTRUCTIONS_LYRICS, font=self.font_small,
                 fg=INSTRUCTION_COLOR, bg=BG_COLOR).pack(side="bottom", pady=40)

    def show_current_screen(self):
        if self.state == "folder_select":
            self.show_folder_select()
        elif self.state == "song_select":
            self.show_song_select()
        elif self.state == "lyrics_view":
            self.show_lyrics()

    # ====================== INPUT HANDLING ======================
    def on_key_press(self, event):
        if self.state in ("folder_select", "song_select"):
            self.handle_menu_keys(event)
        elif self.state == "lyrics_view":
            self.handle_lyrics_keys(event)

    def handle_menu_keys(self, event):
        if event.keysym == "Up":
            if self.state == "folder_select":
                self.folder_idx = (self.folder_idx - 1) % max(1, len(self.folders))
            else:
                self.song_idx = (self.song_idx - 1) % max(1, len(self.songs))
            self.show_current_screen()

        elif event.keysym == "Down":
            if self.state == "folder_select":
                self.folder_idx = (self.folder_idx + 1) % max(1, len(self.folders))
            else:
                self.song_idx = (self.song_idx + 1) % max(1, len(self.songs))
            self.show_current_screen()

        elif event.keysym in ("Return", "KP_Enter"):
            if self.state == "folder_select" and self.folders:
                self.selected_folder = self.folders[self.folder_idx]
                self.songs = self.get_txt_files(self.selected_folder)
                self.song_idx = 0
                self.state = "song_select"
                self.show_current_screen()

            elif self.state == "song_select" and self.songs:
                filepath = os.path.join(BASE_LYRICS_DIR, self.selected_folder, self.songs[self.song_idx])
                self.song_title = os.path.splitext(self.songs[self.song_idx])[0].replace("_", " ").title()
                self.lyrics_blocks = self.load_lyrics(filepath)
                self.block_idx = 0
                self.state = "lyrics_view"
                self.show_current_screen()

        elif event.keysym.lower() == "q":
            if self.state == "song_select":
                self.state = "folder_select"
                self.show_current_screen()

    def handle_lyrics_keys(self, event):
        key = event.keysym.lower()

        if key in ("return", "kp_enter"):
            self.block_idx += 1
            if self.block_idx >= len(self.lyrics_blocks):
                self.state = "song_select"
            self.show_current_screen()

        elif key == "q":
            self.block_idx = max(0, self.block_idx - 1)
            self.show_current_screen()

        elif key == "t":
            if self.t_hold_start is None:
                self.t_hold_start = time.time()          # ← Fixed: use Python's time module
                self.check_t_hold()

    def check_t_hold(self):
        if self.t_hold_start is None:
            return

        if time.time() - self.t_hold_start >= 3.0:      # 3 seconds
            self.state = "song_select"
            self.t_hold_start = None
            self.show_current_screen()
        else:
            # Check again after 100ms
            self.hold_job = self.root.after(100, self.check_t_hold)

    def run(self):
        print("🎤 Lyrics Display App Started")
        print(f"Using lyrics folder: {BASE_LYRICS_DIR}")
        print("Press ESC to quit.\n")
        self.root.mainloop()


if __name__ == "__main__":
    app = LyricsApp()
    app.run()