# modules/timetable_screen.py
"""
Day-13 — Timetable screen for StudyAura

Usage:
    from modules.timetable_screen import show_timetable
    show_timetable(root)
"""

import os
import csv
import uuid
import tkinter as tk
from tkinter import ttk, simpledialog, colorchooser, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFilter

# Paths
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
TIMETABLE_CSV = os.path.join(DATA_DIR, "timetable.csv")

# Ensure data dir exists
os.makedirs(DATA_DIR, exist_ok=True)

# Default neon palette (hex)
NEON_PALETTE = [
    "#FF4D6D",  # pink
    "#6CFFB3",  # mint
    "#9BE1FF",  # baby blue
    "#FFD36C",  # amber
    "#C58CFF",  # violet
    "#61FFDA",  # aqua
    "#FF9AE0",  # light rose
    "#9AFF9A",  # light green
]

# Days and default time rows
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DEFAULT_SLOTS = [
    "07:00", "09:00", "11:00", "13:00", "15:00", "17:00", "19:00"
]  # rows represent start times; end time chosen in dialog


# --------------------------
# CSV helpers
# --------------------------
def load_entries():
    entries = []
    if os.path.isfile(TIMETABLE_CSV):
        try:
            with open(TIMETABLE_CSV, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    entries.append(r)
        except Exception:
            # corrupt file — ignore and return empty
            return []
    return entries


def save_entries(entries):
    # Ensure fieldnames order
    fieldnames = ["id", "day", "start", "end", "subject", "color", "notes"]
    with open(TIMETABLE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for e in entries:
            writer.writerow(e)


# --------------------------
# Small UI helpers
# --------------------------
def neon_button(master, text, command, width=18, padx=6):
    """
    Build a neon-style ttk-like button using Canvas for consistent look.
    Returns the widget (a Canvas containing the button visuals).
    """
    c = tk.Canvas(master, width=width * 10, height=40, bd=0, highlightthickness=0, bg=master["bg"])
    # draw rounded rect with glow effect by layering
    w = int(width * 10)
    h = 40
    radius = 10

    def draw_button(fill="#2A2A2A", outline="#FFFFFF", textcol="white"):
        c.delete("all")
        # glow layers (outer faint)
        for i, alpha in enumerate([100, 70, 40]):
            bbox = (6 - i, 6 - i, w - 6 + i, h - 6 + i)
            try:
                c.create_oval(bbox[0], bbox[1], bbox[0] + 2 * radius, bbox[1] + 2 * radius, outline="", fill=fill, stipple="")
            except Exception:
                pass
        # main rounded rectangle (simple approximation)
        c.create_rectangle(radius, 0, w - radius, h, fill=fill, outline=outline)
        c.create_oval(0, 0, radius * 2, radius * 2, fill=fill, outline=outline)
        c.create_oval(w - radius * 2, 0, w, radius * 2, fill=fill, outline=outline)
        # text
        c.create_text(w // 2, h // 2, text=text, font=("Inter", 11, "bold"), fill=textcol)
    # initial draw
    draw_button(fill="#111827", outline="#7C3AED", textcol="white")

    def on_enter(e):
        draw_button(fill="#1F2937", outline="#A78BFA", textcol="white")
        c.scale("all", w / 2, h / 2, 1.02, 1.02)

    def on_leave(e):
        draw_button(fill="#111827", outline="#7C3AED", textcol="white")
        c.scale("all", w / 2, h / 2, 1 / 1.02, 1 / 1.02)

    c.bind("<Enter>", on_enter)
    c.bind("<Leave>", on_leave)
    c.bind("<Button-1>", lambda e: command())
    return c


# --------------------------
# Timetable main UI
# --------------------------
def show_timetable(root):
    """
    Build the timetable UI inside root (clears previous widgets).
    This keeps the same pattern as other screens: call show_timetable(root).
    """
    for widget in root.winfo_children():
        widget.destroy()

    # root background
    root.configure(bg="#0B0A21")

    container = tk.Frame(root, bg="#0B0A21")
    container.pack(fill="both", expand=True, padx=12, pady=12)

    header_frame = tk.Frame(container, bg="#0B0A21")
    header_frame.pack(fill="x", padx=8, pady=(6, 10))

    title = tk.Label(header_frame, text="🗓️ Weekly Timetable", font=("Inter", 24, "bold"), bg="#0B0A21", fg="white")
    title.pack(side="left", padx=(6, 12))

    subtitle = tk.Label(header_frame, text="Add subjects, times and colorful neon slots", font=("Inter", 11), bg="#0B0A21", fg="#D1D5DB")
    subtitle.pack(side="left")

    # Right-side action buttons
    actions = tk.Frame(header_frame, bg="#0B0A21")
    actions.pack(side="right", padx=6)

    # Neon buttons
    def _safe_refresh():
        refresh_grid()

    add_btn = neon_button(actions, "Add Slot", lambda: open_add_dialog())
    add_btn.pack(side="right", padx=6)
    export_btn = neon_button(actions, "Export CSV", lambda: export_csv())
    export_btn.pack(side="right", padx=6)
    clear_btn = neon_button(actions, "Clear All", lambda: clear_all_confirm())
    clear_btn.pack(side="right", padx=6)
    back_btn = neon_button(actions, "Back", lambda: back_to_dashboard(root))
    back_btn.pack(side="right", padx=6)

    # Main content frame (glass-like panel)
    content = tk.Frame(container, bg="#0B0A21")
    content.pack(fill="both", expand=True, padx=6, pady=6)

    grid_frame = tk.Frame(content, bg="#0B0A21")
    grid_frame.pack(fill="both", expand=True, padx=6, pady=6)

    # Load entries
    entries = load_entries()

    # Map by cell for rendering
    # each entry: dict with id, day, start, end, subject, color, notes

    # We'll render a grid of labels inside a table
    # row 0: header (days)
    # rows 1..N: time slots (DEFAULT_SLOTS)

    TIME_SLOTS = DEFAULT_SLOTS[:]  # allow future customization

    # Keep references to label widgets so we can update them
    cell_widgets = {}

    def refresh_grid():
        """Clear and rebuild the timetable grid (keeps icon references safe)."""
        nonlocal entries, cell_widgets
        entries = load_entries()

        # clear current grid
        for child in grid_frame.winfo_children():
            child.destroy()
        cell_widgets = {}

        # header row: empty corner + days
        corner = tk.Frame(grid_frame, width=120, height=40, bg="#0B0A21")
        corner.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        for c, day in enumerate(DAYS, start=1):
            lbl = tk.Label(grid_frame, text=day, bg="#0B0A21", fg="white", font=("Inter", 12, "bold"), width=18, height=2)
            lbl.grid(row=0, column=c, sticky="nsew", padx=1, pady=1)

        # rows
        for r, start_time in enumerate(TIME_SLOTS, start=1):
            # time label
            tl = tk.Label(grid_frame, text=start_time, bg="#0B0A21", fg="#E5E7EB", font=("Inter", 11), width=12, height=4)
            tl.grid(row=r, column=0, sticky="nsew", padx=1, pady=1)
            for c, day in enumerate(DAYS, start=1):
                frame = tk.Frame(grid_frame, bg="#0B0A21", width=180, height=80, bd=0)
                frame.grid_propagate(False)
                frame.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)
                # create inner label for color and text
                inner = tk.Label(frame, text="", bg="#0B0A21", fg="white", wraplength=150, justify="center", font=("Inter", 10, "bold"))
                inner.place(relx=0.5, rely=0.45, anchor="center")
                cell_widgets[(day, start_time)] = (frame, inner)

        # place entries into grid
        for e in entries:
            day = e.get("day")
            start = e.get("start")
            subj = e.get("subject", "")
            color = e.get("color", NEON_PALETTE[0])
            notes = e.get("notes", "")
            eid = e.get("id")

            key = (day, start)
            if key in cell_widgets:
                frame, inner = cell_widgets[key]
                # set bg color for frame
                try:
                    frame.configure(bg=color)
                    inner.configure(text=subj + ("\n" + notes if notes else ""), bg=color)
                except tk.TclError:
                    # invalid color — fallback
                    frame.configure(bg="#2b2b2b")
                    inner.configure(bg="#2b2b2b", text=subj)

                # right-click menu on frame
                def make_menu(eid=eid):
                    m = tk.Menu(root, tearoff=0)
                    m.add_command(label="Edit", command=lambda _=None: open_add_dialog(eid))
                    m.add_command(label="Delete", command=lambda _=None: delete_entry_confirm(eid))
                    return m

                def on_rclick(event, eid=eid):
                    menu = make_menu()
                    menu.tk_popup(event.x_root, event.y_root)

                frame.bind("<Button-3>", on_rclick)
                inner.bind("<Button-3>", on_rclick)

        # configure grid sizing weights
        for i in range(len(TIME_SLOTS) + 1):
            grid_frame.rowconfigure(i, weight=1)
        for j in range(len(DAYS) + 1):
            grid_frame.columnconfigure(j, weight=1)

    # --------------------------
    # Dialogs: add / edit
    # --------------------------
    def open_add_dialog(entry_id=None):
        """
        Opens a Toplevel dialog to add (entry_id=None) or edit (entry_id=existing id).
        """
        nonlocal entries
        dialog = tk.Toplevel(root)
        dialog.transient(root)
        dialog.grab_set()
        dialog.title("Add / Edit Slot")
        dialog.configure(bg="#0B0A21")
        dialog.geometry("420x420")

        # find existing entry if editing
        existing = None
        if entry_id:
            for it in entries:
                if it.get("id") == entry_id:
                    existing = it
                    break

        # fields: day, start, end, subject, color, notes
        tk.Label(dialog, text="Day", bg="#0B0A21", fg="white").pack(pady=(12, 2))
        day_var = tk.StringVar(value=(existing.get("day") if existing else DAYS[0]))
        day_menu = ttk.Combobox(dialog, values=DAYS, textvariable=day_var, state="readonly")
        day_menu.pack()

        tk.Label(dialog, text="Start Time (HH:MM)", bg="#0B0A21", fg="white").pack(pady=(12, 2))
        start_var = tk.StringVar(value=(existing.get("start") if existing else DEFAULT_SLOTS[0]))
        start_entry = ttk.Combobox(dialog, values=DEFAULT_SLOTS, textvariable=start_var)
        start_entry.pack()

        tk.Label(dialog, text="End Time (HH:MM)", bg="#0B0A21", fg="white").pack(pady=(12, 2))
        # allow end time choices from DEFAULT_SLOTS + some
        end_values = DEFAULT_SLOTS + ["21:00", "22:00"]
        end_var = tk.StringVar(value=(existing.get("end") if existing else end_values[0]))
        end_entry = ttk.Combobox(dialog, values=end_values, textvariable=end_var)
        end_entry.pack()

        tk.Label(dialog, text="Subject", bg="#0B0A21", fg="white").pack(pady=(12, 2))
        subj_var = tk.StringVar(value=(existing.get("subject") if existing else ""))
        subj_entry = tk.Entry(dialog, textvariable=subj_var)
        subj_entry.pack(fill="x", padx=20)

        tk.Label(dialog, text="Color (neon)", bg="#0B0A21", fg="white").pack(pady=(12, 2))
        color_var = tk.StringVar(value=(existing.get("color") if existing else NEON_PALETTE[0]))
        color_preview = tk.Label(dialog, bg=color_var.get(), width=10, height=1)
        color_preview.pack(pady=6)

        def choose_color():
            # open color chooser starting with current
            initial = color_var.get()
            try:
                _, c = colorchooser.askcolor(color=initial, parent=dialog)
                if c:
                    color_var.set(c)
                    color_preview.configure(bg=c)
            except Exception:
                pass

        color_btn = neon_button(dialog, "Choose Color", choose_color)
        color_btn.pack(pady=(4, 10))

        tk.Label(dialog, text="Notes (optional)", bg="#0B0A21", fg="white").pack(pady=(8, 2))
        notes_text = tk.Text(dialog, height=4)
        notes_text.pack(fill="both", padx=12, pady=(0, 10))
        if existing:
            notes_text.insert("1.0", existing.get("notes", ""))

        def on_save():
            d = day_var.get()
            s = start_var.get()
            e = end_var.get()
            sub = subj_var.get().strip()
            col = color_var.get()
            notes = notes_text.get("1.0", "end").strip()

            if not sub:
                messagebox.showwarning("Missing subject", "Please enter subject name.", parent=dialog)
                return

            if existing:
                existing.update({
                    "day": d, "start": s, "end": e, "subject": sub, "color": col, "notes": notes
                })
            else:
                new_entry = {
                    "id": str(uuid.uuid4()),
                    "day": d, "start": s, "end": e, "subject": sub, "color": col, "notes": notes
                }
                entries.append(new_entry)

            save_entries(entries)
            dialog.destroy()
            refresh_grid()

        save_btn = neon_button(dialog, "Save", on_save)
        save_btn.pack(side="left", padx=20, pady=12)

        cancel_btn = neon_button(dialog, "Cancel", lambda: dialog.destroy())
        cancel_btn.pack(side="right", padx=20, pady=12)

        dialog.wait_window()
        return

    # --------------------------
    # Delete / Clear helpers
    # --------------------------
    def delete_entry_confirm(eid):
        nonlocal entries
        if messagebox.askyesno("Delete", "Delete this slot?", parent=root):
            entries = [it for it in entries if it.get("id") != eid]
            save_entries(entries)
            refresh_grid()

    def clear_all_confirm():
        if messagebox.askyesno("Clear all", "Remove all timetable entries?"):
            save_entries([])
            refresh_grid()

    def export_csv():
        # simple "export" — already stored in TIMETABLE_CSV
        if os.path.isfile(TIMETABLE_CSV):
            messagebox.showinfo("Export", f"Timetable exported to:\n{TIMETABLE_CSV}")
        else:
            messagebox.showwarning("Export", "No timetable file found.")

    def back_to_dashboard(r):
        # lazy import to avoid circular deps
        try:
            from modules.dashboard_screen import show_dashboard
            show_dashboard(r)
        except Exception:
            # fallback: just clear
            for w in r.winfo_children():
                w.destroy()

    # initial render
    refresh_grid()


# Expose an API-friendly function name
show_timetable.__doc__ = "Call show_timetable(root) to open the timetable screen."
