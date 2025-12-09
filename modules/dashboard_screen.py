'''# ==========================================
#  modules/dashboard_screen.py (NEON ICONS FIXED)
# ==========================================

import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from analytics.analytics_window import AnalyticsWindow

ICON_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")


def show_dashboard(root):

    # Clear previous screen
    for widget in root.winfo_children():
        widget.destroy()

    container = tk.Frame(root, bg="#0B0A21")
    container.pack(fill="both", expand=True)

    canvas = tk.Canvas(container, bg="#0B0A21", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # IMPORTANT: store all images here so Tkinter does not delete them
    canvas.icon_cache = []

    # -------------------------------------------------------
    # HEADER
    # -------------------------------------------------------
    header = tk.Label(canvas, text="StudyAura",
                      font=("Inter", 44, "bold"),
                      bg="#0B0A21", fg="white")

    subtitle = tk.Label(canvas,
                        text="Your space for smarter learning ✨",
                        font=("Inter", 20),
                        bg="#0B0A21", fg="white")

    h_id = canvas.create_window(600, -70, anchor="nw", window=header)
    s_id = canvas.create_window(550, 10, anchor="nw", window=subtitle)

    def animate_header(step=0):
        if step <= 20:
            canvas.coords(h_id, 600, -70 + step * 3.5)
            canvas.coords(s_id,550, 10 + step * 3.5)
            root.after(17, lambda: animate_header(step + 1))

    animate_header()

    # -------------------------------------------------------
    # ICON BUTTONS
    # -------------------------------------------------------
    buttons = [
        ("Tasks",       "tasks_icon.png"),
        ("Timetable",   "timetable_icon.png"),
        ("Analytics",   "analytics_icon.png"),
        ("Reports",     "reports_icon.png"),
        ("Pomodoro",    "pomodoro_icon.png"),
        ("Settings",    "settings_icon.png"),
    ]

    loaded_icons = []

    for title, filename in buttons:
        path = os.path.join(ICON_DIR, filename)

        try:
            img = Image.open(path).resize((200, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            # STORE TO PREVENT GARBAGE COLLECTION
            canvas.icon_cache.append(photo)

            loaded_icons.append(photo)

        except Exception as e:
            print("Icon failed:", path, e)
            loaded_icons.append(None)

    # -------------------------------------------------------
    # GRID FRAME
    # -------------------------------------------------------
    grid = tk.Frame(canvas, bg="#0B0A21")
    canvas.create_window(250, 120, anchor="nw", window=grid)

    # -------------------------------------------------------
    # CARD CREATOR
    # -------------------------------------------------------
    def create_card(parent, title, icon_img):

        w, h = 260, 260

        card = tk.Canvas(parent, width=w, height=h,
                         bg="#0B0A21", highlightthickness=0)

        # ICON (MIDDLE)
        if icon_img:
            card.create_image(w//2, h//2 - 30, image=icon_img)

        # TITLE
        card.create_text(w//2, h - 55, text=title,
                         font=("Inter", 20, "bold"),
                         fill="white")

        # SUB-TEXT
        card.create_text(w//2, h - 30, text=f"Open {title}",
                         font=("Inter", 11),
                         fill="#CCCCCC")

        # Hover effect
        def hover(e):
            card.scale("all", w/2, h/2, 1.06, 1.06)

        def leave(e):
            card.scale("all", w/2, h/2, 1/1.06, 1/1.06)

        card.bind("<Enter>", hover)
        card.bind("<Leave>", leave)

        # Click effects
        def click(e):
            if title == "Tasks":
                from modules.tasks_screen import show_tasks
                show_tasks(root)

            elif title == "Timetable":
                from modules.timetable_screen import show_timetable
                show_timetable(root)

            elif title == "Analytics":
                AnalyticsWindow(root)

            elif title == "Pomodoro":
                from modules.pomodoro_timer import open_pomodoro
                open_pomodoro(root)

            else:
                print(title, "clicked")

        card.bind("<Button-1>", click)

        return card

    # -------------------------------------------------------
    # PLACE CARDS IN 3×2 GRID
    # -------------------------------------------------------
    r = c = 0
    for i, (title, _) in enumerate(buttons):
        card = create_card(grid, title, loaded_icons[i])
        card.grid(row=r, column=c, padx=40, pady=40)

        c += 1
        if c == 3:
            c = 0
            r += 1
'''
# modules/dashboard_screen.py
"""
Dashboard — wxPython. Uses your PNG cards in assets/icons/.
Click a card → replaces main area with corresponding screen (embedded panel).
Provides show_dashboard() entrypoint for main.py.
"""

import os, io, wx
from PIL import Image
from modules.neon_base_wx import DARK_BG
# filenames expected in assets/icons/ (you already provided them)
PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
ICONS_DIR = os.path.join(PROJECT_ROOT, "assets", "icons")

CARD_FILES = {
    "tasks": "tasks_icon.png",
    "timetable": "timetable_icon.png",
    "analytics": "analytics_icon.png",
    "reports": "reports_icon.png",
    "pomodoro": "pomodoro_icon.png",
    "settings": "settings_icon.png",
}

class CardButton(wx.Panel):
    def __init__(self, parent, key, filename, click_cb):
        super().__init__(parent, style=wx.NO_BORDER)
        self.key = key
        self.filename = filename
        self.click_cb = click_cb
        self.bmp = wx.StaticBitmap(self)
        s = wx.BoxSizer(wx.VERTICAL)
        s.AddStretchSpacer(1)
        s.Add(self.bmp, 0, wx.ALIGN_CENTER)
        s.AddStretchSpacer(1)
        self.SetSizer(s)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.bmp.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.bmp.Bind(wx.EVT_ENTER_WINDOW, self.on_enter)
        self.bmp.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
        self._pil_image = None
        self._size = (0,0)

    def load_image(self, w, h):
        path = os.path.join(ICONS_DIR, self.filename) if self.filename else None
        if path and os.path.isfile(path):
            pil = Image.open(path).convert("RGBA")
            iw, ih = pil.size
            scale = min(w/iw, h/ih)
            nw, nh = int(iw*scale), int(ih*scale)
            pil = pil.resize((nw, nh), Image.LANCZOS)
            # center in canvas
            base = Image.new("RGBA", (w,h), (0,0,0,0))
            base.paste(pil, ((w-nw)//2,(h-nh)//2), pil)
        else:
            base = Image.new("RGBA",(w,h), (20,24,36,255))
        self._pil_image = base
        self._size = (w,h)
        self._set_bitmap_from_pil(base)

    def _set_bitmap_from_pil(self, pil):
        with io.BytesIO() as b:
            pil.save(b, format="PNG"); b.seek(0)
            img = wx.Image(b)
            self.bmp.SetBitmap(wx.Bitmap(img))
            self.Layout()

    def on_enter(self, evt):
        if self._pil_image is None: return
        w,h = self._size
        scaled = self._pil_image.resize((int(w*1.04), int(h*1.04)), Image.LANCZOS)
        self._set_bitmap_from_pil(scaled)
        evt.Skip()

    def on_leave(self, evt):
        if self._pil_image is None: return
        self._set_bitmap_from_pil(self._pil_image)
        evt.Skip()

    def on_click(self, evt):
        if callable(self.click_cb):
            self.click_cb(self.key)
        evt.Skip()

class DashboardFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="StudyAura", size=(1220,820))
        self.SetBackgroundColour(wx.Colour(DARK_BG))
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.Colour(DARK_BG))
        vs = wx.BoxSizer(wx.VERTICAL)
        header = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self.panel, label="StudyAura")
        tf = title.GetFont(); tf.SetPointSize(28); tf.SetWeight(wx.FONTWEIGHT_BOLD); title.SetFont(tf); title.SetForegroundColour(wx.Colour(255,255,255))
        sub = wx.StaticText(self.panel, label="Your space for smarter learning ✨"); sf=sub.GetFont(); sf.SetPointSize(11); sub.SetFont(sf); sub.SetForegroundColour(wx.Colour(200,210,220))
        header.Add(title,0,wx.ALIGN_CENTER|wx.TOP,12); header.Add(sub,0,wx.ALIGN_CENTER|wx.TOP,6)
        vs.Add(header,0,wx.EXPAND)
        # main content area: top has grid of cards; below it the embedded screen area
        self.grid_panel = wx.Panel(self.panel); self.grid_panel.SetBackgroundColour(wx.Colour(DARK_BG))
        self.grid_sizer = wx.GridSizer(rows=2, cols=3, hgap=48, vgap=56)
        self.grid_panel.SetSizer(self.grid_sizer)
        self.cards = {}
        order = ["tasks","timetable","analytics","reports","pomodoro","settings"]
        for key in order:
            fname = CARD_FILES.get(key)
            btn = CardButton(self.grid_panel, key, fname, click_cb=self.on_card_click)
            self.cards[key] = btn
            self.grid_sizer.Add(btn, 0, wx.ALIGN_CENTER)
        vs.Add(self.grid_panel, 0, wx.EXPAND|wx.ALL, 24)
        # embedded screen placeholder (fills remainder)
        self.embed_panel = wx.Panel(self.panel); self.embed_panel.SetBackgroundColour(wx.Colour(DARK_BG))
        vs.Add(self.embed_panel, 1, wx.EXPAND|wx.ALL, 12)
        self.panel.SetSizer(vs)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.current_embedded = None
        self.on_size(None)

    def on_size(self, evt):
        # compute card size and load icons
        gp = self.grid_panel.GetClientSize()
        if gp.width <= 0:
            gp = self.GetSize()
        cols = 3
        total_hgap = (cols - 1) * 48
        per_w = max(220, (gp.width - total_hgap) // cols)
        per_h = per_w
        for key, btn in self.cards.items():
            btn.SetMinSize((per_w, per_h))
            btn.SetInitialSize((per_w, per_h))
            btn.load_image(int(per_w*0.75), int(per_h-2*0.75))
        self.Layout()
        if evt: evt.Skip()

    def on_card_click(self, key):
        # embed the corresponding module screen into self.embed_panel
        # try to import modules.<key>_screen and call show_<key>(parent)
        # before embedding, destroy previous child(s)
        for child in self.embed_panel.GetChildren():
            child.Destroy()
        try:
            modname = f"modules.{key}_screen"
            mod = __import__(modname, fromlist=["*"])
            fn = f"show_{key}"
            if hasattr(mod, fn):
                pnl = getattr(mod, fn)(self.embed_panel)
                if pnl:
                    s = self.embed_panel.GetSizer()
                    if not s:
                        self.embed_panel.SetSizer(wx.BoxSizer(wx.VERTICAL))
                    self.embed_panel.GetSizer().Add(pnl, 1, wx.EXPAND)
                    self.embed_panel.Layout()
                    self.current_embedded = pnl
            else:
                # function not found: fallback message
                self._show_placeholder(f"Module {modname} found but no function {fn}()")
        except Exception as e:
            self._show_placeholder(f"Could not load module for '{key}':\n{e}")

    def _show_placeholder(self, message):
        pnl = wx.Panel(self.embed_panel)
        pnl.SetBackgroundColour(wx.Colour(DARK_BG))
        s = wx.BoxSizer(wx.VERTICAL)
        txt = wx.StaticText(pnl, label=message)
        txt.SetForegroundColour(wx.Colour(220,220,220))
        s.AddStretchSpacer(1)
        s.Add(txt, 0, wx.ALIGN_CENTER|wx.ALL, 18)
        s.AddStretchSpacer(1)
        pnl.SetSizer(s)
        self.embed_panel.GetSizer().Add(pnl, 1, wx.EXPAND)
        self.embed_panel.Layout()

# API for main.py
def show_dashboard(*args, **kwargs):
    app = wx.App(False)
    frame = DashboardFrame()
    frame.Show()
    app.MainLoop()
