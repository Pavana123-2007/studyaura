# ==========================================
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

        '''# TITLE
        card.create_text(w//2, h - 55, text=title,
                         font=("Inter", 20, "bold"),
                         fill="white")

        # SUB-TEXT
        card.create_text(w//2, h - 30, text=f"Open {title}",
                         font=("Inter", 11),
                         fill="#CCCCCC")'''

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

