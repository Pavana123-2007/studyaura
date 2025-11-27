'''from tkinter import *
from tkinter import ttk
from .database_handler import save_task, load_tasks, delete_task, update_task_status

def load_screen(frame):

    # ====================================
    # HEADER
    # ====================================
    Label(
        frame,
        text="📝 Task Manager",
        font=("Segoe UI", 28, "bold"),
        anchor="w"
    ).pack(fill=X, pady=10, padx=20)

    # ====================================
    # ENTRY AREA
    # ====================================
    entry_frame = Frame(frame, bg="#F3F4F6", padx=20, pady=20)
    entry_frame.pack(fill=X, pady=10)

    # Title
    Label(entry_frame, text="Task Title:", font=("Segoe UI", 14), bg="#F3F4F6").grid(row=0, column=0, sticky="w")
    title_entry = Entry(entry_frame, font=("Segoe UI", 14), width=40)
    title_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

    # Subject
    Label(entry_frame, text="Subject:", font=("Segoe UI", 14), bg="#F3F4F6").grid(row=1, column=0, sticky="w")
    subject_var = StringVar()
    subjects = ["Maths", "Physics", "Chemistry", "Biology", "Computer", "Language", "Other"]
    subject_dropdown = ttk.Combobox(entry_frame, textvariable=subject_var, values=subjects, font=("Segoe UI", 14), width=38)
    subject_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    # Deadline
    Label(entry_frame, text="Deadline:", font=("Segoe UI", 14), bg="#F3F4F6").grid(row=2, column=0, sticky="w")
    deadline_entry = Entry(entry_frame, font=("Segoe UI", 14), width=40)
    deadline_entry.insert(0, "DD-MM-YYYY")
    deadline_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    # Priority
    Label(entry_frame, text="Priority:", font=("Segoe UI", 14), bg="#F3F4F6").grid(row=3, column=0, sticky="w")
    priority_var = StringVar(value="Medium")
    priority_dropdown = ttk.Combobox(entry_frame, textvariable=priority_var, values=["High", "Medium", "Low"], font=("Segoe UI", 14), width=38)
    priority_dropdown.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    # ====================================
    # TASK LIST AREA
    # ====================================
    Label(frame, text="Your Tasks:", font=("Segoe UI", 22, "bold"), anchor="w").pack(fill=X, padx=20, pady=(10, 0))

    task_list_frame = Frame(frame, bg="#FFFFFF", padx=20, pady=20)
    task_list_frame.pack(fill=BOTH, expand=True)

    # ------------------------------------
    # DISPLAY TASKS
    # ------------------------------------
    def display_tasks():
        for w in task_list_frame.winfo_children():
            w.destroy()

        tasks = load_tasks()

        if len(tasks) == 0:
            Label(task_list_frame, text="No tasks yet. Add one above!", font=("Segoe UI", 14), fg="#6B7280").pack(pady=10)
            return

        for i, t in enumerate(tasks):

            # Priority colors
            if t["priority"] == "High":
                pr_color = "#F87171"   # red
            elif t["priority"] == "Medium":
                pr_color = "#FBBF24"   # yellow
            else:
                pr_color = "#34D399"   # green

            card = Frame(task_list_frame, bg="#EEF2FF", pady=10, padx=10)
            card.pack(fill=X, pady=6)

            # Title
            Label(card, text=f"📌 {t['title']}", font=("Segoe UI", 16, "bold"), bg="#EEF2FF").pack(anchor="w")

            # Info row
            Label(
                card,
                text=f"Subject: {t['subject']}   |   Deadline: {t['deadline']}",
                font=("Segoe UI", 12),
                bg="#EEF2FF"
            ).pack(anchor="w")

            # Priority badge
            pr_badge = Label(
                card,
                text=f"Priority: {t['priority']}",
                font=("Segoe UI", 11, "bold"),
                bg=pr_color,
                fg="white",
                padx=6,
                pady=2
            )
            pr_badge.pack(anchor="w", pady=4)

            # Status
            Label(
                card,
                text=f"Status: {t['status']}",
                font=("Segoe UI", 12, "italic"),
                bg="#EEF2FF"
            ).pack(anchor="w")

            # ----------------------------
            # BUTTONS (Delete + Complete)
            # ----------------------------
            btn_row = Frame(card, bg="#EEF2FF")
            btn_row.pack(anchor="e", pady=5)

            # Delete
            Button(
                btn_row,
                text="🗑 Delete",
                font=("Segoe UI", 11, "bold"),
                bg="#FCA5A5",
                activebackground="#F87171",
                command=lambda idx=i: [delete_task(idx), display_tasks()]
            ).pack(side=LEFT, padx=5)

            # Mark Completed
            if t["status"] != "Completed":
                Button(
                    btn_row,
                    text="✔ Mark Completed",
                    font=("Segoe UI", 11, "bold"),
                    bg="#A7F3D0",
                    activebackground="#6EE7B7",
                    command=lambda idx=i: [update_task_status(idx, "Completed"), display_tasks()]
                ).pack(side=LEFT, padx=5)

    display_tasks()

    # ====================================
    # ADD TASK BUTTON
    # ====================================
    def add_task():
        task = {
            "title": title_entry.get(),
            "subject": subject_var.get(),
            "deadline": deadline_entry.get(),
            "priority": priority_var.get(),
            "status": "Pending"
        }

        if task["title"].strip() == "":
            return

        save_task(task)
        display_tasks()

        title_entry.delete(0, END)
        subject_var.set("")
        deadline_entry.delete(0, END)
        deadline_entry.insert(0, "DD-MM-YYYY")
        priority_var.set("Medium")

    Button(
        entry_frame,
        text="➕ Add Task",
        font=("Segoe UI", 14, "bold"),
        bg="#A7F3D0",
        activebackground="#6EE7B7",
        padx=10,
        pady=5,
        command=add_task
    ).grid(row=4, column=1, pady=20, sticky="w")'''
"""
modules/tasks_screen.py

StudyAura Tasks Manager
Call: from modules.tasks_screen import show_tasks
      show_tasks(root)

Stores tasks in ../data/tasks.csv with columns:
id,title,subject,priority,due_date,notes,completed

Fields:
- id (int)
- title (str)
- subject (str)
- priority (Low/Med/High)
- due_date (YYYY-MM-DD or empty)
- notes (str)
- completed (0/1)

No external deps (uses csv, datetime, tkinter).
"""
"""
modules/tasks_screen.py
StudyAura — Tasks Screen (Theme A: Pastel Rainbow)

Usage:
    from modules.tasks_screen import show_tasks
    show_tasks(root)

Stores tasks in ../data/tasks.csv with columns:
id,title,subject,priority,due_date,notes,completed
"""
'''# ============================================
#  modules/tasks_screen.py (Apple-Style Premium Version — FIXED)
# ============================================

import os
import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageDraw, ImageFilter, ImageTk


# ============================================
#  FILE STORAGE
# ============================================

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tasks.csv")
os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

if not os.path.isfile(CSV_PATH):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "title", "subject", "priority", "due_date", "notes", "completed"])


def load_tasks():
    tasks = []
    try:
        with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
            rdr = csv.DictReader(f)
            for r in rdr:
                r["id"] = int(r["id"])
                r["completed"] = int(r["completed"])
                tasks.append(r)
    except:
        return []
    return tasks


def save_tasks(tasks):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "title", "subject", "priority", "due_date", "notes", "completed"]
        )
        writer.writeheader()
        for t in tasks:
            writer.writerow(t)


def next_id(tasks):
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1


# ============================================
#  GRADIENT BACKGROUND
# ============================================

def make_pastel_gradient(size):
    w, h = size
    if h <= 1:
        h = 2

    # 🌊 Ocean–Mint gradient
    colors = [
        (180, 255, 240),   # soft mint
        (120, 220, 230),   # aqua
        (80, 180, 200)     # deep teal
    ]

    img = Image.new("RGB", (w, h), colors[0])
    draw = ImageDraw.Draw(img)

    for y in range(h):
        t = y / (h - 1)

        if t < 0.5:
            tt = t / 0.5
            c1, c2 = colors[0], colors[1]
        else:
            tt = (t - 0.5) / 0.5
            c1, c2 = colors[1], colors[2]

        r = int(c1[0] + (c2[0] - c1[0]) * tt)
        g = int(c1[1] + (c2[1] - c1[1]) * tt)
        b = int(c1[2] + (c2[2] - c1[2]) * tt)
        draw.line((0, y, w, y), fill=(r, g, b))

    return img.filter(ImageFilter.GaussianBlur(6))


# ============================================
#  TASK FORM (Add / Edit)
# ============================================

class TaskForm(simpledialog.Dialog):
    def __init__(self, root, title, initial=None):
        self.initial = initial or {}
        super().__init__(root, title=title)

    def body(self, frame):
        frame.configure(bg="#FFFFFF")

        tk.Label(frame, text="Title:", bg="#FFFFFF", font=("Inter", 12)).grid(row=0, column=0, sticky="w")
        self.title_var = tk.StringVar(value=self.initial.get("title", ""))
        tk.Entry(frame, textvariable=self.title_var, width=30).grid(row=0, column=1, pady=4)

        tk.Label(frame, text="Subject:", bg="#FFFFFF", font=("Inter", 12)).grid(row=1, column=0, sticky="w")
        self.subject_var = tk.StringVar(value=self.initial.get("subject", "General"))
        tk.Entry(frame, textvariable=self.subject_var, width=25).grid(row=1, column=1, pady=4)

        tk.Label(frame, text="Priority:", bg="#FFFFFF", font=("Inter", 12)).grid(row=2, column=0, sticky="w")
        self.priority_var = tk.StringVar(value=self.initial.get("priority", "Medium"))
        ttk.Combobox(frame, textvariable=self.priority_var, values=["Low", "Medium", "High"], width=10)\
            .grid(row=2, column=1, pady=4, sticky="w")

        tk.Label(frame, text="Due (YYYY-MM-DD):", bg="#FFFFFF", font=("Inter", 12)).grid(
            row=3, column=0, sticky="w")
        self.due_var = tk.StringVar(value=self.initial.get("due_date", ""))
        tk.Entry(frame, textvariable=self.due_var, width=20).grid(row=3, column=1, pady=4)

        tk.Label(frame, text="Notes:", bg="#FFFFFF", font=("Inter", 12)).grid(row=4, column=0, sticky="nw")
        self.notes = tk.Text(frame, width=35, height=6, bg="#F7F7F7")
        self.notes.grid(row=4, column=1, pady=4)
        self.notes.insert("1.0", self.initial.get("notes", ""))

    def validate(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Error", "Title cannot be empty.")
            return False

        due = self.due_var.get().strip()
        if due:
            try:
                datetime.strptime(due, "%Y-%m-%d")
            except:
                messagebox.showwarning("Error", "Date must be YYYY-MM-DD.")
                return False

        return True

    def apply(self):
        self.result = {
            "title": self.title_var.get().strip(),
            "subject": self.subject_var.get().strip(),
            "priority": self.priority_var.get(),
            "due_date": self.due_var.get().strip(),
            "notes": self.notes.get("1.0", "end").strip(),
            "completed": int(self.initial.get("completed", 0)),
            "id": self.initial.get("id", None),
        }


# ============================================
#  MAIN SCREEN
# ============================================

def show_tasks(root):

    for w in root.winfo_children():
        w.destroy()

    root.title("StudyAura — Tasks")

    # 🌈 Canvas directly on root (IMPORTANT FIX)
    canvas = tk.Canvas(root, highlightthickness=0, bd=0)
    canvas.pack(fill="both", expand=True)
    canvas._images = {}

    # Redraw gradient when window resizes
    def redraw_bg(e=None):
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 20 or h < 20:
            return
        bg = make_pastel_gradient((w, h))
        tk_bg = ImageTk.PhotoImage(bg)
        canvas._images["bg"] = tk_bg
        canvas.create_image(0, 0, anchor="nw", image=tk_bg)

    root.bind("<Configure>", redraw_bg)

    # ======================
    # HEADER
    # ======================
    title_lbl = tk.Label(
        root,
        text="🗂️  Tasks",
        font=("Inter", 34, "bold"),
        bg="#FFFFFF",
        fg="#222222"
    )
    title_lbl.place(x=40, y=20)

    # ======================
    # BUTTON BAR
    # ======================
    bar_frame = tk.Frame(root, bg="#FFFFFF")
    bar_frame.place(x=40, y=90)

    style = ttk.Style()
    style.configure("Apple.TButton", padding=10, font=("Inter", 15))

    add_btn = ttk.Button(bar_frame, text="＋ Add", style="Apple.TButton")
    edit_btn = ttk.Button(bar_frame, text="✎ Edit", style="Apple.TButton")
    del_btn = ttk.Button(bar_frame, text="🗑 Delete", style="Apple.TButton")
    tog_btn = ttk.Button(bar_frame, text="✓ Toggle", style="Apple.TButton")
    back_btn = ttk.Button(bar_frame, text="← Back", style="Apple.TButton")

    add_btn.grid(row=0, column=0, padx=8)
    edit_btn.grid(row=0, column=1, padx=8)
    del_btn.grid(row=0, column=2, padx=8)
    tog_btn.grid(row=0, column=3, padx=8)
    back_btn.grid(row=0, column=4, padx=20)

    # ======================
    # MAIN CONTENT AREA
    # ======================
    main_frame = tk.Frame(root, bg="#FFFFFF")
    main_frame.place(x=40, y=160)

    left_card = tk.Frame(main_frame, bg="#FFFFFF", bd=0, relief="flat", padx=20, pady=20)
    left_card.grid(row=0, column=0, sticky="nsew")

    cols = ("id", "title", "subject", "priority", "due", "done")
    tree = ttk.Treeview(left_card, columns=cols, show="headings", height=18)

    tree.heading("id", text="ID")
    tree.heading("title", text="Title")
    tree.heading("subject", text="Subject")
    tree.heading("priority", text="Priority")
    tree.heading("due", text="Due")
    tree.heading("done", text="Done")

    tree.column("id", width=50, anchor="center")
    tree.column("title", width=350, anchor="w")
    tree.column("subject", width=140, anchor="w")
    tree.column("priority", width=120, anchor="center")
    tree.column("due", width=120, anchor="center")
    tree.column("done", width=70, anchor="center")

    vsb = ttk.Scrollbar(left_card, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")

    right_card = tk.Frame(main_frame, bg="#FFFFFF", padx=20, pady=20)
    right_card.grid(row=0, column=1, sticky="n")

    tk.Label(
        right_card,
        text="Details",
        font=("Inter", 18, "bold"),
        bg="#FFFFFF"
    ).pack(anchor="w")

    details = tk.Text(right_card, width=38, height=19, bg="#FFFFFF", font=("Inter", 12))
    details.pack(pady=10)

    tasks = load_tasks()

    def refresh():
        tree.delete(*tree.get_children())
        for t in tasks:
            tree.insert(
                "", "end", iid=str(t["id"]),
                values=(t["id"], t["title"], t["subject"], t["priority"], t["due_date"],
                        "✔" if t["completed"] else "")
            )
        details.delete("1.0", "end")

    refresh()

    def on_select(event):
        sel = tree.selection()
        if not sel:
            return
        iid = sel[0]
        t = next(x for x in tasks if str(x["id"]) == iid)
        details.delete("1.0", "end")
        details.insert(
            "1.0",
            f"Title: {t['title']}\n"
            f"Subject: {t['subject']}\n"
            f"Priority: {t['priority']}\n"
            f"Due: {t['due_date']}\n\n"
            f"Notes:\n{t['notes']}\n\n"
            f"Completed: {'Yes' if t['completed'] else 'No'}"
        )

    tree.bind("<<TreeviewSelect>>", on_select)

    def do_add():
        f = TaskForm(root, "Add Task")
        if f.result:
            new = f.result
            new["id"] = next_id(tasks)
            tasks.append(new)
            save_tasks(tasks)
            refresh()

    def do_edit():
        sel = tree.selection()
        if not sel:
            return
        item = sel[0]
        t = next(x for x in tasks if str(x["id"]) == item)
        f = TaskForm(root, "Edit Task", initial=t)
        if f.result:
            upd = f.result
            upd["id"] = t["id"]
            idx = tasks.index(t)
            tasks[idx] = upd
            save_tasks(tasks)
            refresh()

    def do_delete():
        sel = tree.selection()
        if not sel:
            return
        if not messagebox.askyesno("Delete", "Delete this task?"):
            return
        iid = sel[0]
        tasks[:] = [x for x in tasks if str(x["id"]) != iid]
        save_tasks(tasks)
        refresh()

    def do_toggle():
        sel = tree.selection()
        if not sel:
            return
        iid = sel[0]
        for t in tasks:
            if str(t["id"]) == iid:
                t["completed"] = 0 if t["completed"] else 1
        save_tasks(tasks)
        refresh()

    add_btn.configure(command=do_add)
    edit_btn.configure(command=do_edit)
    del_btn.configure(command=do_delete)
    tog_btn.configure(command=do_toggle)

    def go_back():
        from modules.dashboard_screen import show_dashboard
        show_dashboard(root)

    back_btn.configure(command=go_back)
'''
'''# ============================================
#  modules/tasks_screen.py (Day-12 Premium Edition)
#  Glassmorphism cards + Rounded search + Floating Add button
# ============================================

import os
import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageDraw, ImageFilter, ImageTk

# ============================================
#  FILE STORAGE (unchanged)
# ============================================

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tasks.csv")
os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

if not os.path.isfile(CSV_PATH):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "title", "subject", "priority", "due_date", "notes", "completed"])


def load_tasks():
    tasks = []
    try:
        with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
            rdr = csv.DictReader(f)
            for r in rdr:
                r["id"] = int(r["id"])
                r["completed"] = int(r["completed"])
                tasks.append(r)
    except:
        return []
    return tasks


def save_tasks(tasks):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "title", "subject", "priority", "due_date", "notes", "completed"]
        )
        writer.writeheader()
        for t in tasks:
            writer.writerow(t)


def next_id(tasks):
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1


# ============================================
#  GRADIENT BACKGROUND (your existing function preserved)
# ============================================

def make_pastel_gradient(size):
    w, h = size
    if h <= 1:
        h = 2

    # 🌊 Ocean–Mint gradient
    colors = [
        (180, 255, 240),   # soft mint
        (120, 220, 230),   # aqua
        (80, 180, 200)     # deep teal
    ]

    img = Image.new("RGB", (w, h), colors[0])
    draw = ImageDraw.Draw(img)

    for y in range(h):
        t = y / (h - 1)

        if t < 0.5:
            tt = t / 0.5
            c1, c2 = colors[0], colors[1]
        else:
            tt = (t - 0.5) / 0.5
            c1, c2 = colors[1], colors[2]

        r = int(c1[0] + (c2[0] - c1[0]) * tt)
        g = int(c1[1] + (c2[1] - c1[1]) * tt)
        b = int(c1[2] + (c2[2] - c1[2]) * tt)
        draw.line((0, y, w, y), fill=(r, g, b))

    return img.filter(ImageFilter.GaussianBlur(6))


# ============================================
#  GLASS + SHADOW GENERATORS (medium frost preset)
# ============================================

def create_rounded_glass(w, h, radius=22, alpha=120, blur_radius=8, border=2):
    """
    Return a PIL RGBA image: rounded glass panel with subtle border and blurred look.
    alpha: 0..255 (transparency of the glass fill). Medium frost uses ~120.
    blur_radius: how much blur to apply to the glass texture.
    border: thickness of the faint white border.
    """
    img = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    rect = (4, 4, 4 + w, 4 + h)

    # glass fill (white with alpha)
    fill = (255, 255, 255, alpha)
    draw.rounded_rectangle(rect, radius=radius, fill=fill)

    # faint border (slightly transparent)
    bcolor = (255, 255, 255, int(alpha * 0.25))
    draw.rounded_rectangle(rect, radius=radius, outline=bcolor, width=border)

    # slight inner highlight line at top-left
    highlight = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dh = ImageDraw.Draw(highlight)
    # thin translucent white strip
    dh.rounded_rectangle((6, 6, 6 + w, 6 + 18), radius=radius, fill=(255, 255, 255, int(alpha * 0.06)))
    img = Image.alpha_composite(img, highlight)

    # blur slightly for glassy softness
    try:
        img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    except Exception:
        pass

    return img


def create_shadow(w, h, radius=22, offset=8, blur=12):
    """
    Create a soft shadow image for the given w,h rounded rectangle.
    """
    sw, sh = w + offset * 2, h + offset * 2
    img = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    rect = (offset, offset, offset + w, offset + h)
    # dark rounded rectangle (semi transparent)
    draw.rounded_rectangle(rect, radius=radius, fill=(10, 10, 20, 100))
    try:
        img = img.filter(ImageFilter.GaussianBlur(radius=blur))
    except Exception:
        pass
    return img


# ============================================
#  TASK FORM (unchanged)
# ============================================

class TaskForm(simpledialog.Dialog):
    def __init__(self, root, title, initial=None):
        self.initial = initial or {}
        super().__init__(root, title=title)

    def body(self, frame):
        frame.configure(bg="#FFFFFF")

        tk.Label(frame, text="Title:", bg="#FFFFFF", font=("Inter", 12)).grid(row=0, column=0, sticky="w")
        self.title_var = tk.StringVar(value=self.initial.get("title", ""))
        tk.Entry(frame, textvariable=self.title_var, width=30).grid(row=0, column=1, pady=4)

        tk.Label(frame, text="Subject:", bg="#FFFFFF", font=("Inter", 12)).grid(row=1, column=0, sticky="w")
        self.subject_var = tk.StringVar(value=self.initial.get("subject", "General"))
        tk.Entry(frame, textvariable=self.subject_var, width=25).grid(row=1, column=1, pady=4)

        tk.Label(frame, text="Priority:", bg="#FFFFFF", font=("Inter", 12)).grid(row=2, column=0, sticky="w")
        self.priority_var = tk.StringVar(value=self.initial.get("priority", "Medium"))
        ttk.Combobox(frame, textvariable=self.priority_var, values=["Low", "Medium", "High"], width=10)\
            .grid(row=2, column=1, pady=4, sticky="w")

        tk.Label(frame, text="Due (YYYY-MM-DD):", bg="#FFFFFF", font=("Inter", 12)).grid(
            row=3, column=0, sticky="w")
        self.due_var = tk.StringVar(value=self.initial.get("due_date", ""))
        tk.Entry(frame, textvariable=self.due_var, width=20).grid(row=3, column=1, pady=4)

        tk.Label(frame, text="Notes:", bg="#FFFFFF", font=("Inter", 12)).grid(row=4, column=0, sticky="nw")
        self.notes = tk.Text(frame, width=35, height=6, bg="#F7F7F7")
        self.notes.grid(row=4, column=1, pady=4)
        self.notes.insert("1.0", self.initial.get("notes", ""))

    def validate(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Error", "Title cannot be empty.")
            return False

        due = self.due_var.get().strip()
        if due:
            try:
                datetime.strptime(due, "%Y-%m-%d")
            except:
                messagebox.showwarning("Error", "Date must be YYYY-MM-DD.")
                return False

        return True

    def apply(self):
        self.result = {
            "title": self.title_var.get().strip(),
            "subject": self.subject_var.get().strip(),
            "priority": self.priority_var.get(),
            "due_date": self.due_var.get().strip(),
            "notes": self.notes.get("1.0", "end").strip(),
            "completed": int(self.initial.get("completed", 0)),
            "id": self.initial.get("id", None),
        }


# ============================================
#  MAIN SCREEN (upgraded layout & visuals)
# ============================================

def show_tasks(root):
    # clear previous widgets
    for w in root.winfo_children():
        w.destroy()

    root.title("StudyAura — Tasks")

    # Main full-screen canvas (holds bg + glass panels + windows)
    canvas = tk.Canvas(root, highlightthickness=0, bd=0)
    canvas.pack(fill="both", expand=True)
    canvas._images = {}  # keep references for PhotoImage objects

    # ---------- UI coordinate helpers ----------
    PAD_X = 40
    PAD_Y = 20

    # sizes are relative; will be recomputed on resize
    def layout_and_draw():
        W = max(900, canvas.winfo_width())
        H = max(600, canvas.winfo_height())

        # ---------- Background gradient ----------
        bg = make_pastel_gradient((W, H))
        tk_bg = ImageTk.PhotoImage(bg)
        canvas._images["bg"] = tk_bg
        canvas.create_image(0, 0, anchor="nw", image=tk_bg, tags="bg_img")

        # ---------- Left glass card (task list) ----------
        left_w, left_h = int(W * 0.56), int(H * 0.66)
        left_x, left_y = PAD_X, 160

        # shadow + glass images
        shadow_img = create_shadow(left_w, left_h, radius=20, offset=6, blur=14)
        glass_img = create_rounded_glass(left_w, left_h, radius=20, alpha=120, blur_radius=6, border=2)

        canvas._images["left_shadow"] = ImageTk.PhotoImage(shadow_img)
        canvas._images["left_glass"] = ImageTk.PhotoImage(glass_img)

        # place shadow then glass
        canvas.create_image(left_x + 6, left_y + 6, anchor="nw", image=canvas._images["left_shadow"], tags="left_shadow")
        canvas.create_image(left_x, left_y, anchor="nw", image=canvas._images["left_glass"], tags="left_glass")

        # ---------- Right glass card (details) ----------
        right_w, right_h = int(W * 0.28), left_h
        right_x = left_x + left_w + 40
        right_y = left_y

        shadow_r = create_shadow(right_w, right_h, radius=18, offset=6, blur=12)
        glass_r = create_rounded_glass(right_w, right_h, radius=18, alpha=120, blur_radius=6, border=2)

        canvas._images["right_shadow"] = ImageTk.PhotoImage(shadow_r)
        canvas._images["right_glass"] = ImageTk.PhotoImage(glass_r)

        canvas.create_image(right_x + 6, right_y + 6, anchor="nw", image=canvas._images["right_shadow"], tags="right_shadow")
        canvas.create_image(right_x, right_y, anchor="nw", image=canvas._images["right_glass"], tags="right_glass")

        # ---------- Floating Add button (neon bubble) ----------
        fab_size = 84
        fab_x = left_x + left_w - fab_size // 2
        fab_y = left_y + left_h - fab_size // 2

        # neon glow circle (drawn as image)
        glow = Image.new("RGBA", (fab_size + 40, fab_size + 40), (0, 0, 0, 0))
        dg = ImageDraw.Draw(glow)
        # outer soft glow
        dg.ellipse((0, 0, fab_size + 40, fab_size + 40), fill=(35, 120, 255, 80))
        glow = glow.filter(ImageFilter.GaussianBlur(10))
        # inner solid circle
        inner = Image.new("RGBA", (fab_size, fab_size), (0, 0, 0, 0))
        di = ImageDraw.Draw(inner)
        di.ellipse((0, 0, fab_size, fab_size), fill=(45, 120, 255, 255))
        # composite into final
        final_fab = Image.new("RGBA", glow.size, (0, 0, 0, 0))
        final_fab.paste(glow, (0, 0), glow)
        final_fab.paste(inner, (20, 20), inner)
        canvas._images["fab_img"] = ImageTk.PhotoImage(final_fab)
        # center of the glow image should align to fab_x,fab_y
        canvas.create_image(fab_x - 20, fab_y - 20, anchor="nw", image=canvas._images["fab_img"], tags="fab_glow")

        # ---------- Place windows (frames) on top of glass images ----------
        # header
        # remove any existing header/windows so we don't duplicate on resize
        canvas.delete("ui_windows")

        title_lbl = tk.Label(canvas, text="🗂️  Tasks", font=("Inter", 34, "bold"), bg="", fg="#061428")
        canvas.create_window(PAD_X, 20, anchor="nw", window=title_lbl, tags="ui_windows")

        # button bar frame (keeps same button widgets)
        bar_frame = tk.Frame(canvas, bg="", bd=0)
        canvas.create_window(PAD_X, 90, anchor="nw", window=bar_frame, tags="ui_windows")

        style = ttk.Style()
        style.configure("Apple.TButton", padding=8, font=("Inter", 14), relief="flat")

        add_btn = ttk.Button(bar_frame, text="＋ Add", style="Apple.TButton")
        edit_btn = ttk.Button(bar_frame, text="✎ Edit", style="Apple.TButton")
        del_btn = ttk.Button(bar_frame, text="🗑 Delete", style="Apple.TButton")
        tog_btn = ttk.Button(bar_frame, text="✓ Toggle", style="Apple.TButton")
        back_btn = ttk.Button(bar_frame, text="← Back", style="Apple.TButton")

        add_btn.grid(row=0, column=0, padx=8)
        edit_btn.grid(row=0, column=1, padx=8)
        del_btn.grid(row=0, column=2, padx=8)
        tog_btn.grid(row=0, column=3, padx=8)
        back_btn.grid(row=0, column=4, padx=20)

        # left content frame (will be placed above left_glass)
        left_frame = tk.Frame(canvas, bg="", bd=0)
        canvas.create_window(left_x, left_y, anchor="nw", window=left_frame, tags="ui_windows", width=left_w, height=left_h)

        # inside left_frame: place search bar (glass style) and treeview area
        # create a small label with the smaller glass image as background for search bar
        sb_h = 56
        sb_w = left_w - 40

        # create search bar image (rounded smaller)
        search_img = create_rounded_glass(sb_w, sb_h, radius=14, alpha=230, blur_radius=3, border=1)  # lighter glass for search
        canvas._images["search_img"] = ImageTk.PhotoImage(search_img)
        # We'll place the search background on the canvas, then create an Entry over it.
        sb_x = left_x + 20
        sb_y = left_y + 18
        canvas.create_image(sb_x, sb_y, anchor="nw", image=canvas._images["search_img"], tags="ui_windows")

        # create a transparent frame for search entry to live in (so styling looks correct)
        search_holder = tk.Frame(canvas, bg="", bd=0)
        canvas.create_window(sb_x + 12, sb_y + 10, anchor="nw", window=search_holder, width=sb_w - 24, height=sb_h - 20, tags="ui_windows")

        search_var = tk.StringVar()
        search_entry = tk.Entry(search_holder, textvariable=search_var, bd=0, font=("Inter", 12))
        search_entry.pack(fill="both", expand=True)

        # Now create the tree and scrollbar in left_frame (positioned under the search bar)
        # We'll create an inner frame inside left_frame to get padding
        inner_left = tk.Frame(left_frame, bg="", bd=0)
        inner_left.place(x=20, y=20 + sb_h, width=left_w - 60, height=left_h - sb_h - 40)

        cols = ("id", "title", "subject", "priority", "due", "done")
        tree = ttk.Treeview(inner_left, columns=cols, show="headings", height=18)

        tree.heading("id", text="ID")
        tree.heading("title", text="Title")
        tree.heading("subject", text="Subject")
        tree.heading("priority", text="Priority")
        tree.heading("due", text="Due")
        tree.heading("done", text="Done")

        tree.column("id", width=50, anchor="center")
        tree.column("title", width=350, anchor="w")
        tree.column("subject", width=140, anchor="w")
        tree.column("priority", width=120, anchor="center")
        tree.column("due", width=120, anchor="center")
        tree.column("done", width=70, anchor="center")

        vsb = ttk.Scrollbar(inner_left, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        tree.place(x=0, y=0, relwidth=0.95, relheight=1)
        vsb.place(relx=0.95, x=0, y=0, relheight=1)

        # right content frame (details) placed above right_glass
        right_frame = tk.Frame(canvas, bg="", bd=0)
        canvas.create_window(right_x, right_y, anchor="nw", window=right_frame, tags="ui_windows", width=right_w, height=right_h)

        tk.Label(right_frame, text="Details", font=("Inter", 18, "bold"), bg="").pack(anchor="w", padx=20, pady=(20, 6))
        details = tk.Text(right_frame, width=38, height=19, bg="#FFFFFF", font=("Inter", 12))
        details.pack(padx=20, pady=(0, 20))

        # store widgets that will be referenced outside
        canvas._widgets = {
            "tree": tree,
            "details": details,
            "search_var": search_var,
            "add_btn": add_btn,
            "edit_btn": edit_btn,
            "del_btn": del_btn,
            "tog_btn": tog_btn,
            "back_btn": back_btn,
            "fab_coords": (fab_x, fab_y),
        }

        # create an invisible button over the fab area to receive clicks
        def fab_click(event=None):
            do_add()

        canvas.tag_bind("fab_glow", "<Button-1>", lambda e: fab_click())

        # place a label with a plus sign over the fab (window so text is crisp)
        fab_label = tk.Label(canvas, text="+", font=("Inter", 28, "bold"), bg="", fg="white")
        canvas.create_window(fab_x + fab_size // 2, fab_y + fab_size // 2, window=fab_label, tags="ui_windows")

        # style search result filtering
        def on_search(*args):
            q = search_var.get().strip().lower()
            refresh(filter_q=q)
        search_var.trace_add("write", on_search)

    # Debounce the redraw so resizing isn't too heavy
    redraw_after = {"id": None}

    def redraw_debounced(event=None):
        if redraw_after["id"]:
            try:
                root.after_cancel(redraw_after["id"])
            except Exception:
                pass
        redraw_after["id"] = root.after(120, lambda: (canvas.delete("all"), layout_and_draw()))

    # initial layout draw (after small delay to allow sizing)
    root.after(80, layout_and_draw)
    root.bind("<Configure>", redraw_debounced)

    # ======================
    #  Task Data + Functions (same logic as before)
    # ======================
    tasks = load_tasks()

    def refresh(filter_q=""):
        tree = canvas._widgets["tree"]
        details = canvas._widgets["details"]
        tree.delete(*tree.get_children())
        for t in tasks:
            display_title = t["title"]
            # filter
            if filter_q:
                if filter_q not in (str(t["id"]) + " " + t["title"] + " " + t["subject"]).lower():
                    continue
            tree.insert(
                "", "end", iid=str(t["id"]),
                values=(t["id"], t["title"], t["subject"], t["priority"], t["due_date"],
                        "✔" if t["completed"] else "")
            )
        details.delete("1.0", "end")

    def on_select(event):
        sel = canvas._widgets["tree"].selection()
        if not sel:
            return
        iid = sel[0]
        t = next(x for x in tasks if str(x["id"]) == iid)
        canvas._widgets["details"].delete("1.0", "end")
        canvas._widgets["details"].insert(
            "1.0",
            f"Title: {t['title']}\n"
            f"Subject: {t['subject']}\n"
            f"Priority: {t['priority']}\n"
            f"Due: {t['due_date']}\n\n"
            f"Notes:\n{t['notes']}\n\n"
            f"Completed: {'Yes' if t['completed'] else 'No'}"
        )

    # attach selection binding after initial draw (small delay)
    def attach_bindings():
        try:
            canvas._widgets["tree"].bind("<<TreeviewSelect>>", on_select)
        except Exception:
            pass

    root.after(200, attach_bindings)

    # add/edit/delete/toggle functions (reuse your logic)
    def do_add():
        f = TaskForm(root, "Add Task")
        if f.result:
            new = f.result
            new["id"] = next_id(tasks)
            tasks.append(new)
            save_tasks(tasks)
            refresh()

    def do_edit():
        sel = canvas._widgets["tree"].selection()
        if not sel:
            return
        item = sel[0]
        t = next(x for x in tasks if str(x["id"]) == item)
        f = TaskForm(root, "Edit Task", initial=t)
        if f.result:
            upd = f.result
            upd["id"] = t["id"]
            idx = tasks.index(t)
            tasks[idx] = upd
            save_tasks(tasks)
            refresh()

    def do_delete():
        sel = canvas._widgets["tree"].selection()
        if not sel:
            return
        if not messagebox.askyesno("Delete", "Delete this task?"):
            return
        iid = sel[0]
        tasks[:] = [x for x in tasks if str(x["id"]) != iid]
        save_tasks(tasks)
        refresh()

    def do_toggle():
        sel = canvas._widgets["tree"].selection()
        if not sel:
            return
        iid = sel[0]
        for t in tasks:
            if str(t["id"]) == iid:
                t["completed"] = 0 if t["completed"] else 1
        save_tasks(tasks)
        refresh()

    # attach commands to the buttons after UI created (delayed to ensure add_btn exists)
    def attach_button_commands():
        try:
            canvas._widgets["add_btn"].configure(command=do_add)
            canvas._widgets["edit_btn"].configure(command=do_edit)
            canvas._widgets["del_btn"].configure(command=do_delete)
            canvas._widgets["tog_btn"].configure(command=do_toggle)
        except Exception:
            pass

    root.after(250, attach_button_commands)

    def go_back():
        from modules.dashboard_screen import show_dashboard
        show_dashboard(root)

    # attach back command (delayed similarly)
    def attach_back():
        try:
            canvas._widgets["back_btn"].configure(command=go_back)
        except Exception:
            pass

    root.after(260, attach_back)

    # initial data fill (after UI ready)
    def initial_refresh():
        refresh()
    root.after(300, initial_refresh)
'''
# modules/tasks_screen.py
"""
StudyAura — Task Screen (Premium Ocean-Mint Gradient)
"""

import os
import csv
import uuid
from datetime import datetime
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from PIL import Image, ImageDraw, ImageTk, ImageFilter

# -------------------------
# Paths & ensure files
# -------------------------
MODULE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.normpath(os.path.join(MODULE_DIR, "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)
CSV_PATH = os.path.join(DATA_DIR, "tasks.csv")

# Ensure CSV exists
if not os.path.isfile(CSV_PATH):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id", "title", "description", "subject",
            "priority", "due_date", "created_at", "completed"
        ])


# -------------------------
# CSV Helpers
# -------------------------
def read_tasks():
    tasks = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["completed"] = row.get("completed") == "True"
            tasks.append(row)
    return tasks


def write_tasks(tasks):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "id", "title", "description", "subject",
            "priority", "due_date", "created_at", "completed"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for t in tasks:
            t["completed"] = "True" if t.get("completed") else "False"
            writer.writerow(t)


# -------------------------
# Gradient Background
# -------------------------
def make_ocean_mint_gradient(width, height):
    img = Image.new("RGB", (width, height), "#BFF0E6")
    draw = ImageDraw.Draw(img)

    top = (15,160,146)
    mid = (101,214,187)
    bottom = (197,252,238)

    for y in range(height):
        ratio = y / (height - 1)
        if ratio < 0.5:
            r = int(top[0] + (mid[0] - top[0]) * (ratio / 0.5))
            g = int(top[1] + (mid[1] - top[1]) * (ratio / 0.5))
            b = int(top[2] + (mid[2] - top[2]) * (ratio / 0.5))
        else:
            r = int(mid[0] + (bottom[0] - mid[0]) * ((ratio - 0.5) / 0.5))
            g = int(mid[1] + (bottom[1] - mid[1]) * ((ratio - 0.5) / 0.5))
            b = int(mid[2] + (bottom[2] - mid[2]) * ((ratio - 0.5) / 0.5))
        draw.line([(0,y), (width,y)], fill=(r,g,b))

    return img


# -------------------------
# Task Card UI
# -------------------------
class TaskCard(tk.Frame):
    def __init__(self, parent, task, edit, delete, toggle, **kw):
        super().__init__(parent, bg="", **kw)
        self.task = task
        self.on_edit = edit
        self.on_delete = delete
        self.on_toggle = toggle

        bg = "#FFFFFF" if not task["completed"] else "#E8FFF3"

        box = tk.Frame(self, bg=bg)
        box.pack(fill="x", padx=8, pady=6)

        # TITLE
        top = tk.Frame(box, bg=bg)
        top.pack(fill="x", pady=4)
        tk.Label(top, text=task["title"], font=("Inter", 12, "bold"), bg=bg).pack(side="left")

        # PRIORITY
        pri_color = {
            "High": "#FF6B6B",
            "Medium": "#FFB457",
            "Low": "#6BCB77"
        }.get(task["priority"], "#555")

        tk.Label(top, text=task["priority"], fg=pri_color,
                 font=("Inter", 9, "bold"), bg=bg).pack(side="right")

        # META
        meta = tk.Frame(box, bg=bg)
        meta.pack(fill="x")
        meta_text = f"{task['subject']}"
        if task["due_date"]:
            meta_text += f" • Due {task['due_date']}"
        tk.Label(meta, text=meta_text, bg=bg, fg="#444", font=("Inter", 9)).pack(anchor="w")

        # DESC + BUTTONS
        row = tk.Frame(box, bg=bg)
        row.pack(fill="x", pady=6)

        short = task["description"][:120] + ("..." if len(task["description"]) > 120 else "")
        tk.Label(row, text=short, bg=bg, fg="#333", font=("Inter", 9),
                 wraplength=400, justify="left").pack(side="left", expand=True)

        btns = tk.Frame(row, bg=bg)
        btns.pack(side="right")

        tk.Button(btns, text="✔" if task["completed"] else "∘",
                  command=self.toggle, bd=0).pack(side="left", padx=4)
        tk.Button(btns, text="✎", command=self.edit, bd=0).pack(side="left", padx=4)
        tk.Button(btns, text="🗑", command=self.delete, bd=0).pack(side="left", padx=4)

    def edit(self):
        self.on_edit(self.task)

    def delete(self):
        self.on_delete(self.task)

    def toggle(self):
        self.on_toggle(self.task)


# -------------------------
# MAIN TASKS SCREEN
# -------------------------
class TasksScreen(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.tasks = []
        self.filtered = []

        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.resize)

        self.topbar = tk.Frame(self.canvas, bg="")
        self.build_topbar()

        self.scroll_area = tk.Frame(self.canvas)
        self.build_scroll()

        self.bg_image = None
        self.draw_bg()
        self.place_widgets()

        self.reload()

    # ---------------------
    # TOP BAR
    # ---------------------
    def build_topbar(self):
        f = self.topbar
        tk.Label(f, text="Tasks", fg="#073B38",
                 font=("Inter", 18, "bold")).grid(row=0, column=0, padx=6)

        self.search_var = tk.StringVar()
        e = ttk.Entry(f, textvariable=self.search_var, width=30)
        e.grid(row=0, column=1, padx=6)
        e.bind("<KeyRelease>", lambda e: self.apply_filters())

        self.priority_var = tk.StringVar(value="All")
        c = ttk.Combobox(f, textvariable=self.priority_var,
                         values=["All", "High", "Medium", "Low"],
                         width=8, state="readonly")
        c.grid(row=0, column=2, padx=6)
        c.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        ttk.Button(f, text="+ Add Task", command=self.add).grid(row=0, column=3, padx=8)
        ttk.Button(f, text="Refresh", command=self.reload).grid(row=0, column=4, padx=4)

    # ---------------------
    # SCROLLING CARDS
    # ---------------------
    def build_scroll(self):
        self.cards_canvas = tk.Canvas(self.scroll_area, bd=0, highlightthickness=0)
        self.cards_frame = tk.Frame(self.cards_canvas, bg="")
        self.scroll_y = ttk.Scrollbar(self.scroll_area, orient="vertical",
                                      command=self.cards_canvas.yview)
        self.cards_canvas.configure(yscrollcommand=self.scroll_y.set)

        self.scroll_y.pack(side="right", fill="y")
        self.cards_canvas.pack(side="left", fill="both", expand=True)
        self.cards_canvas.create_window((0,0), window=self.cards_frame, anchor="nw")

        self.cards_frame.bind("<Configure>",
                              lambda e: self.cards_canvas.configure(scrollregion=self.cards_canvas.bbox("all")))

    # ---------------------
    # DRAW BACKGROUND
    # ---------------------
    def draw_bg(self, w=None, h=None):
        w = w or max(800, self.canvas.winfo_width())
        h = h or max(600, self.canvas.winfo_height())

        img = make_ocean_mint_gradient(w, h)
        self.bg_image = ImageTk.PhotoImage(img)

        self.canvas.delete("bg")
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image, tags="bg")

    def resize(self, e):
        self.draw_bg(e.width, e.height)
        self.place_widgets()

    def place_widgets(self):
        self.canvas.delete("top")
        self.canvas.delete("list")

        self.canvas.create_window(20, 20, anchor="nw", window=self.topbar, tags="top")
        self.canvas.create_window(20, 70, anchor="nw",
                                  window=self.scroll_area,
                                  width=self.canvas.winfo_width() - 40,
                                  height=self.canvas.winfo_height() - 90,
                                  tags="list")

    # ---------------------
    # LOGIC
    # ---------------------
    def reload(self):
        self.tasks = read_tasks()
        self.apply_filters()

    def apply_filters(self):
        q = self.search_var.get().lower().strip()
        pri = self.priority_var.get()

        self.filtered = []
        for t in self.tasks:
            if q and q not in t["title"].lower() and q not in t["subject"].lower():
                continue
            if pri != "All" and t["priority"] != pri:
                continue
            self.filtered.append(t)

        self.render()

    def render(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()

        for t in self.filtered:
            TaskCard(
                self.cards_frame,
                t,
                edit=self.edit,
                delete=self.delete,
                toggle=self.toggle
            ).pack(fill="x")

    # ---------------------
    # OPERATIONS
    # ---------------------
    def add(self):
        d = TaskDialog(self.root, "Add Task")
        if d.result:
            new = {
                "id": str(uuid.uuid4()),
                "title": d.result["title"],
                "description": d.result["description"],
                "subject": d.result["subject"],
                "priority": d.result["priority"],
                "due_date": d.result["due"],
                "created_at": datetime.now().isoformat(),
                "completed": False
            }
            self.tasks.append(new)
            write_tasks(self.tasks)
            self.apply_filters()

    def edit(self, task):
        d = TaskDialog(self.root, "Edit Task", task)
        if d.result:
            task.update({
                "title": d.result["title"],
                "description": d.result["description"],
                "subject": d.result["subject"],
                "priority": d.result["priority"],
                "due_date": d.result["due"]
            })
            write_tasks(self.tasks)
            self.apply_filters()

    def delete(self, task):
        self.tasks = [t for t in self.tasks if t["id"] != task["id"]]
        write_tasks(self.tasks)
        self.apply_filters()

    def toggle(self, task):
        task["completed"] = not task["completed"]
        write_tasks(self.tasks)
        self.apply_filters()


# -------------------------
# Task Dialog
# -------------------------
class TaskDialog(simpledialog.Dialog):
    def __init__(self, parent, title, initial=None):
        self.initial = initial
        self.result = None
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="Title").grid(row=0, column=0)
        self.title_e = ttk.Entry(master, width=45)
        self.title_e.grid(row=0, column=1, pady=4)

        tk.Label(master, text="Subject").grid(row=1, column=0)
        self.subject_e = ttk.Entry(master, width=30)
        self.subject_e.grid(row=1, column=1, pady=4)

        tk.Label(master, text="Priority").grid(row=2, column=0)
        self.priority_v = tk.StringVar(value="Medium")
        self.priority_c = ttk.Combobox(master,
                                       textvariable=self.priority_v,
                                       values=["High","Medium","Low"],
                                       width=10, state="readonly")
        self.priority_c.grid(row=2, column=1, pady=4, sticky="w")

        tk.Label(master, text="Due Date").grid(row=3, column=0)
        self.due_e = ttk.Entry(master, width=20)
        self.due_e.grid(row=3, column=1, pady=4, sticky="w")

        tk.Label(master, text="Description").grid(row=4, column=0)
        self.desc_t = tk.Text(master, width=45, height=6)
        self.desc_t.grid(row=4, column=1, pady=4)

        if self.initial:
            self.title_e.insert(0, self.initial["title"])
            self.subject_e.insert(0, self.initial["subject"])
            self.priority_v.set(self.initial["priority"])
            self.due_e.insert(0, self.initial["due_date"])
            self.desc_t.insert("1.0", self.initial["description"])

        return self.title_e

    def apply(self):
        self.result = {
            "title": self.title_e.get().strip(),
            "subject": self.subject_e.get().strip(),
            "priority": self.priority_v.get(),
            "due": self.due_e.get().strip(),
            "description": self.desc_t.get("1.0", "end").strip()
        }


# -------------------------
# Main Entry for Dashboard
# -------------------------
def show_tasks_screen(root):
    for c in root.winfo_children():
        if getattr(c, "_is_tasks_screen", False):
            c.destroy()

    s = TasksScreen(root)
    s._is_tasks_screen = True
    s.pack(fill="both", expand=True)
    return s


# BACKWARD COMPATIBILITY — Dashboard expects show_tasks()
def show_tasks(root):
    return show_tasks_screen(root)


# DEBUG MODE
if __name__ == "__main__":
    r = tk.Tk()
    r.geometry("1000x700")
    show_tasks_screen(r)
    r.mainloop()
