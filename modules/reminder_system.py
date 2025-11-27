from tkinter import *
from datetime import datetime, timedelta
import threading
import time
from .database_handler import load_tasks, load_sessions, parse_deadline

# --------------------------------------------------
# POPUP WINDOW FUNCTION
# --------------------------------------------------
def show_popup(title, message):
    popup = Toplevel()
    popup.title(title)
    popup.geometry("400x250")
    popup.configure(bg="#FFF7ED")

    Label(
        popup, text=title, 
        font=("Segoe UI", 18, "bold"), 
        bg="#FFF7ED"
    ).pack(pady=10)

    Label(
        popup, text=message, 
        font=("Segoe UI", 14), 
        bg="#FFF7ED", 
        wraplength=350
    ).pack(pady=10)

    Button(
        popup, text="OK", 
        font=("Segoe UI", 12, "bold"),
        bg="#FFD6A5", 
        command=popup.destroy
    ).pack(pady=15)


# --------------------------------------------------
# REMINDER CHECK LOOP
# --------------------------------------------------
def reminder_loop(root):
    while True:
        try:
            check_deadlines(root)
            check_study_sessions(root)
        except:
            pass
        
        time.sleep(10)   # check every 10 seconds


# --------------------------------------------------
# CHECK DEADLINES
# --------------------------------------------------
def check_deadlines(root):
    tasks = load_tasks()
    now = datetime.now().date()

    for t in tasks:
        d = parse_deadline(t["deadline"])
        if not d:
            continue

        d = d.date()

        # overdue alert
        if d < now and t["status"] != "Completed":
            root.after(0, lambda: show_popup(
                "⚠ Overdue Task",
                f"{t['title']} was due on {t['deadline']}!"
            ))
            return

        # due today
        if d == now:
            root.after(0, lambda: show_popup(
                "🟡 Due Today",
                f"{t['title']} is due today!"
            ))
            return

        # due tomorrow
        if d == now + timedelta(days=1):
            root.after(0, lambda: show_popup(
                "🔵 Due Tomorrow",
                f"{t['title']} is due tomorrow!"
            ))
            return


# --------------------------------------------------
# CHECK STUDY SESSIONS
# --------------------------------------------------
def check_study_sessions(root):
    sessions = load_sessions()
    now = datetime.now()

    for s in sessions:
        try:
            time_str = s["start_time"]
            session_time = datetime.strptime(time_str, "%H:%M")
            session_dt = now.replace(
                hour=session_time.hour,
                minute=session_time.minute,
                second=0,
                microsecond=0
            )

            # Only alert if session is today
            today_name = now.strftime("%A")
            if s["day"] != today_name:
                continue

            diff = session_dt - now

            # alert 15 minutes before
            if timedelta(minutes=14) < diff < timedelta(minutes=16):
                root.after(0, lambda: show_popup(
                    "📘 Study Session Soon",
                    f"{s['subject']} session starts at {s['start_time']}!"
                ))
                return

        except:
            continue
