import os
import csv

# -------------------------------------------------
# PATHS
# -------------------------------------------------
BASE_PATH = os.path.dirname(os.path.dirname(__file__))
DATA_FOLDER = os.path.join(BASE_PATH, "data")

TASKS_FILE = os.path.join(DATA_FOLDER, "tasks.csv")
PROGRESS_FILE = os.path.join(DATA_FOLDER, "progress.csv")
SETTINGS_FILE = os.path.join(DATA_FOLDER, "settings.csv")


# -------------------------------------------------
# ENSURE DATA FILES EXIST
# -------------------------------------------------
def ensure_files():
    """Ensure data folder + CSVs exist with correct headers."""

    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["task", "subject", "deadline", "priority", "status"])

    if not os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["task", "progress"])

    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["setting", "value"])


ensure_files()


# =====================================================
# TASKS — LOAD & SAVE
# =====================================================
def load_tasks():
    """Returns a list of tasks as dictionaries."""
    ensure_files()
    tasks = []

    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tasks.append({
                "task": row.get("task", ""),
                "subject": row.get("subject", ""),
                "deadline": row.get("deadline", ""),
                "priority": row.get("priority", ""),
                "status": row.get("status", "Pending")
            })

    return tasks


def save_tasks(tasks):
    """Writes list of task dictionaries back to tasks.csv."""
    ensure_files()

    with open(TASKS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["task", "subject", "deadline", "priority", "status"])

        for t in tasks:
            writer.writerow([
                t.get("task", ""),
                t.get("subject", ""),
                t.get("deadline", ""),
                t.get("priority", ""),
                t.get("status", "Pending")
            ])


# =====================================================
# SETTINGS HANDLER
# =====================================================
def load_settings():
    ensure_files()
    settings = {}

    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            settings[row["setting"]] = row["value"]

    return settings


def save_settings(settings: dict):
    ensure_files()

    with open(SETTINGS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["setting", "value"])

        for key, val in settings.items():
            writer.writerow([key, val])


# =====================================================
# PROGRESS HANDLER
# =====================================================
def load_progress():
    ensure_files()
    progress = {}

    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            progress[row["task"]] = row["progress"]

    return progress


def save_progress(progress_dict: dict):
    ensure_files()

    with open(PROGRESS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["task", "progress"])

        for task, prog in progress_dict.items():
            writer.writerow([task, prog])
