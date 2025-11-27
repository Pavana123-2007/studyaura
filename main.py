'''# ============================================================
#  🌟 STUDYAURA — FINAL MAIN FILE (DAY 1 → DAY 9)
# ============================================================

from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import os
import threading

# Day-9 Reminder System Import
from modules.reminder_system import reminder_loop  



# ============================================================
#  🔹 THEME COLORS
# ============================================================
TITLE_BG = "#7DD3FC"
SIDEBAR_BG = "#DCE7FF"
CONTENT_BG = "#FFFFFF"
BUTTON_BG = "#AEC8FF"
BUTTON_ACTIVE = "#8EB4FF"


# ============================================================
#  🔹 MAIN WINDOW SETUP
# ============================================================
root = Tk()
root.title("🎓📚 StudyAura - Your Space for Smarter Learning")
root.geometry("1550x800")
root.state("zoomed")
root.configure(bg="#E9E9E9")


# ============================================================
#  🔹 WELCOME FRAME
# ============================================================
welcome_frame = Frame(root, bg=TITLE_BG, highlightthickness=0)
welcome_frame.pack(fill=BOTH, expand=True)


# ============================================================
#  🔹 LOAD BACKGROUND IMAGE
# ============================================================
base_path = os.path.dirname(__file__)
img_path = os.path.join(base_path, "assets/icons/background.png")

bg_image = Image.open(img_path)
bg_resized = bg_image.resize((1550, 800), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_resized)

bg_label = Label(welcome_frame, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
bg_label.image = bg_photo
bg_label.lower()


# ============================================================
#  🔹 WELCOME SCREEN TITLE
# ============================================================
title_frame = Frame(welcome_frame, bg=TITLE_BG)
title_frame.place(x=40, y=80)

shadow = Label(
    title_frame,
    text="🎓📚 StudyAura:\nTurn Plans\ninto Progress! 🧠💡",
    font=("Segoe UI", 45, "bold"),
    bg=TITLE_BG,
    fg="#000000"
)
shadow.place(x=3, y=3)

title = Label(
    title_frame,
    text="🎓📚 StudyAura:\nTurn Plans\ninto Progress! 🧠💡",
    font=("Segoe UI", 45, "bold"),
    bg=TITLE_BG,
    fg="#000000"
)
title.pack()

canvas = Canvas(welcome_frame, width=450, height=5, bg=TITLE_BG, highlightthickness=0)
canvas.place(x=120, y=370)
canvas.create_line(0, 2, 450, 2, fill="#2563EB", width=4)
canvas.create_line(0, 2, 225, 2, fill="#A855F7", width=4)

subtitle = Label(
    welcome_frame,
    text="📚 Plan Smart  |  💪 Stay Consistent  |  🚀 Achieve Excellence",
    font=("Segoe UI", 18, "bold"),
    bg=TITLE_BG,
    fg="#000000"
)
subtitle.place(x=30, y=400)


# ============================================================
#  🔹 START BUTTON
# ============================================================
style = ttk.Style()
style.configure("TButton", font=("Segoe UI", 14, "bold"), padding=10)

start_btn = ttk.Button(
    welcome_frame,
    text="✨ Start Planning Now!",
    style="TButton",
    command=lambda: show_planner()
)
start_btn.place(x=220, y=500)

footer = Label(
    welcome_frame,
    text="Designed with ❤️ by PyNova Team",
    font=("Segoe UI", 14, "bold"),
    bg=TITLE_BG,
    fg="#01050E"
)
footer.pack(side=BOTTOM, pady=20)


# ============================================================
#  🔹 PLANNER SCREEN (SIDEBAR + CONTENT)
# ============================================================
def show_planner():
    welcome_frame.pack_forget()

    global sidebar_frame, content_frame

    sidebar_frame = Frame(root, bg=SIDEBAR_BG, width=260)
    sidebar_frame.pack(side=LEFT, fill=Y)

    content_frame = Frame(root, bg=CONTENT_BG)
    content_frame.pack(side=LEFT, fill=BOTH, expand=True)

    create_sidebar_buttons()

    # ⭐ Start the Day-9 Reminder Thread
    threading.Thread(target=reminder_loop, args=(root,), daemon=True).start()

    load_screen("dashboard")
    



# ============================================================
#  🔹 SIDEBAR BUTTONS
# ============================================================
def create_sidebar_buttons():

    def make_btn(text, screen):
        return Button(
            sidebar_frame,
            text=text,
            font=("Segoe UI", 14, "bold"),
            bg=BUTTON_BG,
            activebackground=BUTTON_ACTIVE,
            bd=0,
            pady=14,
            command=lambda: load_screen(screen)
        )

    for w in sidebar_frame.winfo_children():
        w.destroy()

    make_btn("📘 Dashboard", "dashboard").pack(fill=X, padx=12, pady=(20, 6))
    make_btn("📝 Tasks", "tasks").pack(fill=X, padx=12, pady=6)
    make_btn("📊 Progress", "progress").pack(fill=X, padx=12, pady=6)
    make_btn("⚙ Settings", "settings").pack(fill=X, padx=12, pady=6)
    make_btn("🗓 Timetable", "timetable").pack(fill=X, padx=12, pady=6)


# ============================================================
#  🔹 SCREEN LOADER
# ============================================================
def load_screen(screen_name):
    for w in content_frame.winfo_children():
        w.destroy()

    if screen_name == "dashboard":
        from modules.dashboard_screen import load_screen as dash
        dash(content_frame)

    elif screen_name == "tasks":
        from modules.tasks_screen import load_screen as tasks
        tasks(content_frame)

    elif screen_name == "progress":
        from modules.progress_screen import load_screen as prog
        prog(content_frame)

    elif screen_name == "settings":
        from modules.settings_screen import load_screen as settings
        settings(content_frame)

    elif screen_name == "timetable":
        from modules.timetable_screen import load_screen as ts
        ts(content_frame)

    else:
        Label(content_frame, text="Unknown screen", font=("Segoe UI", 18)).pack(pady=20)


# ============================================================
#  🔹 START APP
# ============================================================
root.mainloop()'''
'''
modules/tasks_screen.py
Colourful + Elegant Tasks Screen for StudyAura (Theme A - Pastel Rainbow)

Usage:
    from modules.tasks_screen import show_tasks
    show_tasks(root)

Saves tasks to ../data/tasks.csv with header:
id,title,subject,priority,due_date,notes,completed
'''
# ============================================================
#  🌟 STUDYAURA — FINAL MAIN FILE (DAY 1 → Day-11) with animations
# ============================================================

from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import os
import threading

# Day-9 Reminder System Import (if present)
try:
    from modules.reminder_system import reminder_loop
except Exception:
    # If the reminder module isn't present yet, ignore gracefully
    reminder_loop = None

# NEW DASHBOARD IMPORT (IMPORTANT)
from modules.dashboard_screen import show_dashboard


# ============================================================
#  🔹 THEME COLORS (WELCOME SCREEN)
# ============================================================
TITLE_BG = "#7DD3FC"
SIDEBAR_BG = "#DCE7FF"
CONTENT_BG = "#FFFFFF"
BUTTON_BG = "#AEC8FF"
BUTTON_ACTIVE = "#8EB4FF"


# ============================================================
#  🔹 MAIN WINDOW SETUP
# ============================================================
root = Tk()
root.title("🎓📚 StudyAura - Your Space for Smarter Learning")
root.geometry("1550x800")
# start maximized (safe cross-platform)
try:
    root.state("zoomed")
except Exception:
    pass
root.configure(bg="#E9E9E9")


# ============================================================
#  🔹 WELCOME FRAME
# ============================================================
welcome_frame = Frame(root, bg=TITLE_BG, highlightthickness=0)
welcome_frame.pack(fill=BOTH, expand=True)


# ============================================================
#  🔹 LOAD BACKGROUND IMAGE
# ============================================================
base_path = os.path.dirname(__file__)
img_path = os.path.join(base_path, "assets", "icons", "background.png")

try:
    bg_image = Image.open(img_path)
    bg_resized = bg_image.resize((1550, 800), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_resized)

    bg_label = Label(welcome_frame, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    bg_label.image = bg_photo
    bg_label.lower()
except Exception:
    # If background image missing, keep solid TITLE_BG
    pass


# ============================================================
#  🔹 WELCOME SCREEN TITLE (unchanged visually)
# ============================================================
# We'll animate positions — initial y moved down then animated up
title_frame = Frame(welcome_frame, bg=TITLE_BG)
title_frame.place(x=40, y=160)  # animated to y=80

shadow = Label(
    title_frame,
    text="🎓📚 StudyAura:\nTurn Plans\ninto Progress! 🧠💡",
    font=("Segoe UI", 45, "bold"),
    bg=TITLE_BG,
    fg="#000000"
)
shadow.place(x=3, y=3)

title = Label(
    title_frame,
    text="🎓📚 StudyAura:\nTurn Plans\ninto Progress! 🧠💡",
    font=("Segoe UI", 45, "bold"),
    bg=TITLE_BG,
    fg="#000000"
)
title.pack()

# Underline canvas (will slide up with animation)
canvas = Canvas(welcome_frame, width=450, height=5, bg=TITLE_BG, highlightthickness=0)
canvas.place(x=120, y=450)  # animated to y=370
canvas.create_line(0, 2, 450, 2, fill="#2563EB", width=4)
canvas.create_line(0, 2, 225, 2, fill="#A855F7", width=4)

subtitle = Label(
    welcome_frame,
    text="📚 Plan Smart  |  💪 Stay Consistent  |  🚀 Achieve Excellence",
    font=("Segoe UI", 18, "bold"),
    bg=TITLE_BG,
    fg="#000000"
)
subtitle.place(x=30, y=480)  # animated to y=400


# ============================================================
#  🔹 ANIMATIONS (Balanced: smooth + responsive)
# ============================================================

def animate_welcome():
    """Balanced slide animations for title, line and subtitle."""
    frames = 25
    start_y_title = 160
    end_y_title = 80
    start_y_line = 450
    end_y_line = 370
    start_y_sub = 480
    end_y_sub = 400

    dy_title = (end_y_title - start_y_title) / frames
    dy_line = (end_y_line - start_y_line) / frames
    dy_sub = (end_y_sub - start_y_sub) / frames

    def step(i=0):
        if i > frames:
            # Ensure final positions set
            title_frame.place_configure(y=end_y_title)
            canvas.place_configure(y=end_y_line)
            subtitle.place_configure(y=end_y_sub)
            return

        title_frame.place_configure(y=int(start_y_title + dy_title * i))
        canvas.place_configure(y=int(start_y_line + dy_line * i))
        subtitle.place_configure(y=int(start_y_sub + dy_sub * i))
        root.after(16, lambda: step(i + 1))

    # short delay then animate
    root.after(180, step)


# run animation once on start
root.after(200, animate_welcome)


# ============================================================
#  🔹 START BUTTON (unchanged look, now calls show_planner)
# ============================================================
style = ttk.Style()
style.configure("TButton", font=("Segoe UI", 14, "bold"), padding=10)

start_btn = ttk.Button(
    welcome_frame,
    text="✨ Start Planning Now!",
    style="TButton",
    command=lambda: show_planner()
)
start_btn.place(x=220, y=500)


footer = Label(
    welcome_frame,
    text="Designed with ❤️ by PyNova Team",
    font=("Segoe UI", 14, "bold"),
    bg=TITLE_BG,
    fg="#01050E"
)
footer.pack(side=BOTTOM, pady=20)


# ============================================================
#  🔹 NAVIGATION: show_planner (destroys welcome and opens dashboard)
# ============================================================
def show_planner():
    """Clear the window and open the animated Dashboard."""
    # Stop any reminder loop thread if running gracefully (non-blocking)
    try:
        if reminder_loop:
            pass
    except Exception:
        pass

    # Clear root widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Call the dashboard loader
    show_dashboard(root)


# ============================================================
#  🔹 MAINLOOP
# ============================================================
if __name__ == "__main__":
    root.mainloop()
