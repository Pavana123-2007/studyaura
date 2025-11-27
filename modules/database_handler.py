import csv
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/tasks.csv")

# -------------------------------------------
# SAVE A NEW TASK
# -------------------------------------------
def save_task(task):
    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["title", "subject", "deadline", "priority", "status"])

        writer.writerow([
            task["title"],
            task["subject"],
            task["deadline"],
            task["priority"],
            task["status"]
        ])

# -------------------------------------------
# LOAD ALL TASKS
# -------------------------------------------
def load_tasks():
    if not os.path.isfile(DATA_FILE):
        return []

    with open(DATA_FILE, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

# -------------------------------------------
# DELETE TASK by INDEX
# -------------------------------------------
def delete_task(index):
    tasks = load_tasks()
    if index < 0 or index >= len(tasks):
        return

    tasks.pop(index)

    with open(DATA_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "subject", "deadline", "priority", "status"])
        for t in tasks:
            writer.writerow([t["title"], t["subject"], t["deadline"], t["priority"], t["status"]])

# -------------------------------------------
# UPDATE TASK STATUS
# -------------------------------------------
def update_task_status(index, new_status):
    tasks = load_tasks()
    if index < 0 or index >= len(tasks):
        return

    tasks[index]["status"] = new_status

    with open(DATA_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "subject", "deadline", "priority", "status"])
        for t in tasks:
            writer.writerow([t["title"], t["subject"], t["deadline"], t["priority"], t["status"]])
def get_task_stats():
    tasks = load_tasks()

    total = len(tasks)
    completed = sum(1 for t in tasks if t["status"] == "Completed")
    pending = total - completed

    # Subject-wise stats
    subjects = {}
    for t in tasks:
        subject = t["subject"]
        if subject not in subjects:
            subjects[subject] = {"total": 0, "completed": 0}

        subjects[subject]["total"] += 1
        if t["status"] == "Completed":
            subjects[subject]["completed"] += 1

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "subjects": subjects,
    }
from datetime import datetime, timedelta


def parse_deadline(date_str):
    try:
        return datetime.strptime(date_str, "%d-%m-%Y")
    except:
        return None


def get_deadline_groups():
    tasks = load_tasks()
    today = datetime.today().date()

    overdue = []
    due_today = []
    due_tomorrow = []

    for t in tasks:
        dt = parse_deadline(t["deadline"])
        if dt is None:
            continue

        d = dt.date()

        if d < today:
            overdue.append(t)
        elif d == today:
            due_today.append(t)
        elif d == today.replace(day=today.day+1):
            due_tomorrow.append(t)

    return overdue, due_today, due_tomorrow
# ========================================================
# TIMETABLE STORAGE
# ========================================================
import csv
import os

TIMETABLE_FILE = os.path.join(os.path.dirname(__file__), "../data/timetable.csv")

def save_session(session):
    file_exists = os.path.isfile(TIMETABLE_FILE)

    with open(TIMETABLE_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["day", "subject", "start_time", "duration"])

        writer.writerow([
            session["day"],
            session["subject"],
            session["start_time"],
            session["duration"]
        ])

def load_sessions():
    if not os.path.isfile(TIMETABLE_FILE):
        return []

    with open(TIMETABLE_FILE, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)
def get_next_session():
    sessions = load_sessions()
    now = datetime.now()
    today = now.strftime("%A")

    closest = None
    min_diff = timedelta(hours=24)

    for s in sessions:
        if s["day"] != today:
            continue
        
        try:
            t = datetime.strptime(s["start_time"], "%H:%M")
            session_time = now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
            diff = session_time - now

            if timedelta(0) < diff < min_diff:
                min_diff = diff
                closest = s

        except:
            continue

    return closest, min_diff
