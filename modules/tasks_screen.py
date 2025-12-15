# ============================================================
# StudyAura — Calendar View Tasks Screen (FINAL + CSV + ColorPicker + DatePicker)
# ============================================================

import wx
import wx.adv
import wx.lib.scrolledpanel as scrolled
import datetime
import csv
import os

# ============================
# CONFIGURATION
# ============================
LEFT_PANEL_W = 220
HEADER_H = 100
DAY_BAR_H = 48

HOUR_START = 0
HOUR_END = 24
HOUR_HEIGHT = 72

GRID_COL_GAP = 30
DAY_COL_COUNT = 7

# Colors
BG = wx.Colour(18, 24, 34)
PANEL = wx.Colour(28, 36, 48)
NEON = wx.Colour(180, 220, 255)
TEXT_LIGHT = wx.Colour(230, 235, 240)

EVENT_COLORS = [
    wx.Colour(150, 190, 255),
    wx.Colour(235, 170, 255),
    wx.Colour(150, 220, 180),
    wx.Colour(255, 190, 150),
    wx.Colour(120, 255, 220),
]

CSV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "tasks.csv")
)


# ============================================================
# ColorPicker Widget — small circular color bubbles
# ============================================================
class ColorPicker(wx.Panel):
    def __init__(self, parent, initial_index=0):
        super().__init__(parent)
        self.selected = initial_index if initial_index is not None else 0

        try:
            self.SetBackgroundColour(parent.GetBackgroundColour())
        except Exception:
            pass

        s = wx.BoxSizer(wx.HORIZONTAL)
        self.btns = []

        for i, col in enumerate(EVENT_COLORS):
            btn = wx.Panel(self, size=(28, 28))
            btn.SetBackgroundColour(col)
            btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
            btn.SetToolTip(f"Color {i + 1}")

            btn.Bind(wx.EVT_PAINT, lambda e, b=btn: self.paint_circle(e, b))
            btn.Bind(wx.EVT_LEFT_DOWN, lambda e, idx=i: self.on_select(idx))

            s.Add(btn, 0, wx.ALL, 4)
            self.btns.append(btn)

        self.SetSizer(s)
        self.refresh_selection()

    def paint_circle(self, event, panel):
        dc = wx.PaintDC(panel)
        w, h = panel.GetSize()
        dc.Clear()
        col = panel.GetBackgroundColour()
        dc.SetBrush(wx.Brush(col))
        dc.SetPen(wx.Pen(wx.Colour(60, 60, 60)))
        radius = min(w, h) // 2 - 2
        dc.DrawCircle(w // 2, h // 2, radius)

        idx = self.btns.index(panel)
        if idx == self.selected:
            dc.SetPen(wx.Pen(wx.Colour(255, 255, 255), 2))
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawCircle(w // 2, h // 2, radius + 2)

    def on_select(self, index):
        self.selected = index
        self.refresh_selection()

    def refresh_selection(self):
        for btn in self.btns:
            btn.Refresh()

    def get(self):
        return int(self.selected)


# ============================================================
# MAIN TASKS SCREEN
# ============================================================
class TasksScreen(wx.Panel):
    def __init__(self, parent, nav_callback=None, back_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.nav_callback = nav_callback
        self.back_callback = back_callback

        self.SetBackgroundColour(BG)

        today = datetime.date.today()
        self.week_start = today - datetime.timedelta(days=today.weekday())

        self.events = self.load_tasks_from_csv()

        self.build_ui()
        wx.CallAfter(self.recalc_grid_size)

    # ======================================================
    # CSV LOADING / SAVING
    # ======================================================
    def load_tasks_from_csv(self):
        events = []

        if not os.path.exists(CSV_PATH):
            return events

        try:
            with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        raw_date = row.get("date", "").strip()
                        date = None
                        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                            try:
                                date = datetime.datetime.strptime(raw_date, fmt).date()
                                break
                            except:
                                pass
                        if date is None:
                            continue

                        try:
                            start = datetime.datetime.strptime(row["start"], "%H:%M").time()
                            end = datetime.datetime.strptime(row["end"], "%H:%M").time()
                        except:
                            continue

                        events.append(
                            {
                                "title": row["title"],
                                "date": date,
                                "start": start,
                                "end": end,
                                "color_index": int(row.get("color_index", 0)),
                                "completed": row.get("completed", "False") == "True",
                            }
                        )
                    except Exception as e:
                        print("Error reading row:", e)
        except Exception as e:
            print("CSV load error:", e)

        return events

    def save_tasks_to_csv(self):
        try:
            os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
            with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["title", "date", "start", "end", "color_index", "completed"])

                for ev in self.events:
                    writer.writerow(
                        [
                            ev["title"],
                            ev["date"].strftime("%Y-%m-%d"),
                            ev["start"].strftime("%H:%M"),
                            ev["end"].strftime("%H:%M"),
                            ev.get("color_index", 0),
                            ev.get("completed", False),
                        ]
                    )
        except Exception as e:
            print("CSV save error:", e)

    # ======================================================
    # UI STRUCTURE
    # ======================================================
    def build_ui(self):
        main = wx.BoxSizer(wx.HORIZONTAL)

        sidebar = self.build_sidebar()
        content = self.build_content()

        main.Add(sidebar, 0, wx.EXPAND)
        main.Add(content, 1, wx.EXPAND)

        self.SetSizer(main)

    # ======================================================
    # SIDEBAR  (Study Streak removed)
    # ======================================================
    def build_sidebar(self):
        p = wx.Panel(self, size=(LEFT_PANEL_W, -1))
        p.SetBackgroundColour(wx.Colour(24, 32, 44))

        s = wx.BoxSizer(wx.VERTICAL)

        items = [
            ("Home", "Home"),
            ("Subject Progress", "SubjectProgress"),
            ("Study Heatmap", "Heatmap"),
            ("Daily Progress", "DailyProgress"),
            #("Tasks Completed", "TasksCompleted"),
            # ("Study Streak", "Streak")  ❌ REMOVED
        ]

        for label, value in items:
            btn = wx.Button(
                p,
                label=label,
                style=wx.BORDER_NONE,
                size=(200, 50)
            )

            btn.SetForegroundColour(TEXT_LIGHT)
            btn.SetBackgroundColour(wx.Colour(0, 0, 0, 0))
            btn.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_BOLD))

            btn.Bind(wx.EVT_BUTTON, lambda evt, v=value: self.on_nav_click(v))

            s.Add(btn, 0, wx.LEFT | wx.TOP | wx.EXPAND, 10)

        s.AddStretchSpacer()
        p.SetSizer(s)
        return p

    def on_nav_click(self, label):
        if self.nav_callback:
            self.nav_callback(label)

    # ======================================================
    # CONTENT AREA
    # ======================================================
    def build_content(self):
        p = wx.Panel(self)
        p.SetBackgroundColour(BG)

        s = wx.BoxSizer(wx.VERTICAL)

        header = self.build_header(p)
        daybar = self.build_daybar(p)

        scroll = scrolled.ScrolledPanel(p, style=wx.SUNKEN_BORDER)
        scroll.SetupScrolling(True, True)
        scroll.SetBackgroundColour(BG)

        self.grid_panel = wx.Panel(scroll)
        self.grid_panel.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.grid_panel.SetBackgroundColour(BG)

        self.grid_panel.Bind(wx.EVT_PAINT, self.on_paint_grid)
        self.grid_panel.Bind(wx.EVT_LEFT_DOWN, self.on_grid_click)

        scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        scroll_sizer.Add(self.grid_panel, 1, wx.EXPAND)
        scroll.SetSizer(scroll_sizer)

        s.Add(header, 0, wx.EXPAND | wx.TOP, 5)
        s.Add(daybar, 0, wx.EXPAND | wx.TOP, 5)
        s.Add(scroll, 1, wx.EXPAND | wx.ALL, 10)

        p.SetSizer(s)
        return p

    # ======================================================
    # HEADER (Dark Mode Toggle Removed)
    # ======================================================
    def build_header(self, parent):
        p = wx.Panel(parent, size=(-1, HEADER_H))
        p.SetBackgroundColour(BG)

        s = wx.BoxSizer(wx.HORIZONTAL)

        prev_btn = wx.Button(p, label="◀", size=(44, 34), style=wx.BORDER_NONE)
        next_btn = wx.Button(p, label="▶", size=(44, 34), style=wx.BORDER_NONE)

        btn_font = wx.Font(14, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_BOLD)
        prev_btn.SetFont(btn_font)
        next_btn.SetFont(btn_font)
        prev_btn.SetForegroundColour(TEXT_LIGHT)
        next_btn.SetForegroundColour(TEXT_LIGHT)
        prev_btn.SetBackgroundColour(wx.Colour(0, 0, 0, 0))
        next_btn.SetBackgroundColour(wx.Colour(0, 0, 0, 0))

        prev_btn.Bind(wx.EVT_BUTTON, self.on_prev_week)
        next_btn.Bind(wx.EVT_BUTTON, self.on_next_week)

        self.month_label = wx.StaticText(p, label=self.week_start.strftime("%B %Y"))
        self.month_label.SetFont(wx.Font(28, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_BOLD))
        self.month_label.SetForegroundColour(TEXT_LIGHT)

        s.Add(prev_btn, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        s.Add(self.month_label, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 10)
        s.Add(next_btn, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 10)

        s.AddStretchSpacer()

        add_btn = wx.Button(p, label="+ New Event")
        add_btn.Bind(wx.EVT_BUTTON, self.on_new_event)
        s.Add(add_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 20)

        prof = wx.StaticBitmap(p, bitmap=self.circle_bitmap(36, NEON))
        s.Add(prof, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)

        p.SetSizer(s)
        return p

    # ======================================================
    # DAY BAR
    # ======================================================
    def build_daybar(self, parent):
        p = wx.Panel(parent, size=(-1, DAY_BAR_H))
        p.SetBackgroundColour(wx.Colour(24, 30, 40))

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        positions = [90, 260, 420, 600, 800, 950, 1150]

        for i, d in enumerate(days):
            lbl = wx.StaticText(p, label=d)
            lbl.SetFont(wx.Font(18, wx.FONTFAMILY_DECORATIVE, 0, wx.FONTWEIGHT_BOLD, False, "Lucida Handwriting"))
            lbl.SetForegroundColour(TEXT_LIGHT)
            lbl.SetPosition((positions[i], 12))

        return p

    # ======================================================
    # GRID SIZING
    # ======================================================
    def recalc_grid_size(self):
        total_hours = HOUR_END - HOUR_START
        height = total_hours * HOUR_HEIGHT + 40
        width = (140 + GRID_COL_GAP) * DAY_COL_COUNT + 200

        self.grid_panel.SetMinSize((width, height))
        self.grid_panel.GetParent().FitInside()
        self.grid_panel.Refresh()

    # ======================================================
    # GRID PAINTING
    # ======================================================
    def on_paint_grid(self, evt):
        dc = wx.AutoBufferedPaintDC(self.grid_panel)

        dc.SetBackground(wx.Brush(BG))
        dc.Clear()

        w, h = self.grid_panel.GetSize()

        left_margin = 40
        top_margin = 10
        col_w = 150

        # Draw day columns
        for col in range(DAY_COL_COUNT):
            x = left_margin + col * (col_w + GRID_COL_GAP)

            dc.SetBrush(wx.Brush(wx.Colour(22, 28, 38)))
            dc.SetPen(wx.Pen(wx.Colour(44, 54, 68)))
            dc.DrawRoundedRectangle(x, top_margin, col_w, h - 20, 6)

            date = self.week_start + datetime.timedelta(days=col)
            dc.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_BOLD))
            dc.SetTextForeground(TEXT_LIGHT)
            dc.DrawText(str(date.day), x + 10, top_margin + 5)

        # Draw hour lines
        for i in range(HOUR_END - HOUR_START + 1):
            y = top_margin + i * HOUR_HEIGHT

            dc.SetPen(wx.Pen(wx.Colour(34, 42, 54)))
            dc.DrawLine(left_margin, y, left_margin + (col_w + GRID_COL_GAP) * DAY_COL_COUNT, y)

            hour = HOUR_START + i
            label = f"{(hour - 1) % 12 + 1} {'AM' if hour < 12 else 'PM'}"

            dc.SetFont(wx.Font(9, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_NORMAL))
            dc.SetTextForeground(wx.Colour(150, 160, 170))
            dc.DrawText(label, left_margin - 40, y - 6)

        # Draw events
        for ev in self.events:
            self.draw_event(dc, ev, col_w, left_margin, top_margin)

    def draw_event(self, dc, ev, col_w, left_margin, top_margin):
        day_idx = (ev["date"] - self.week_start).days
        if day_idx < 0 or day_idx >= DAY_COL_COUNT:
            return

        s_minutes = ev["start"].hour * 60 + ev["start"].minute
        e_minutes = ev["end"].hour * 60 + ev["end"].minute
        offset = HOUR_START * 60

        y1 = top_margin + int((s_minutes - offset) / 60 * HOUR_HEIGHT)
        y2 = top_margin + int((e_minutes - offset) / 60 * HOUR_HEIGHT)

        x = left_margin + day_idx * (col_w + GRID_COL_GAP) + 6
        w = col_w - 12
        h = max(16, y2 - y1)

        if ev.get("completed"):
            color = wx.Colour(120, 124, 130)
            text_col = wx.Colour(200, 200, 205)
        else:
            color = EVENT_COLORS[ev["color_index"] % len(EVENT_COLORS)]
            text_col = wx.Colour(10, 10, 10)

        dc.SetBrush(wx.Brush(color))
        dc.SetPen(wx.Pen(color))
        dc.DrawRoundedRectangle(x, y1 + 2, w, h - 4, 6)

        dc.SetTextForeground(text_col)
        dc.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_BOLD))

        title = ev["title"]
        max_chars = 18
        if len(title) > max_chars:
            title = title[: max_chars - 1] + "…"

        dc.DrawText(title, x + 6, y1 + 8)

        if ev.get("completed"):
            dc.SetFont(wx.Font(8, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_NORMAL))
            dc.SetTextForeground(wx.Colour(170, 170, 175))
            dc.DrawText("(Completed)", x + 6, y1 + 24)

    # ======================================================
    # EVENT CLICK
    # ======================================================
    def on_grid_click(self, evt):
        pos = evt.GetPosition()

        col_w = 150
        left_margin = 40
        top_margin = 10

        clicked = None
        for ev in self.events:
            day_idx = (ev["date"] - self.week_start).days
            if day_idx < 0 or day_idx >= DAY_COL_COUNT:
                continue

            s_minutes = ev["start"].hour * 60 + ev["start"].minute
            e_minutes = ev["end"].hour * 60 + ev["end"].minute
            offset = HOUR_START * 60

            y1 = top_margin + int((s_minutes - offset) / 60 * HOUR_HEIGHT)
            y2 = top_margin + int((e_minutes - offset) / 60 * HOUR_HEIGHT)

            x = left_margin + day_idx * (col_w + GRID_COL_GAP) + 6
            w = col_w - 12
            h = max(16, y2 - y1)

            if wx.Rect(x, y1 + 2, w, h - 4).Contains(pos):
                clicked = ev
                break

        if clicked:
            self.open_edit_dialog(clicked)

    def open_edit_dialog(self, ev):
        dlg = EditEventDialog(self, ev)
        res = dlg.ShowModal()

        if dlg.deleted:
            try:
                self.events.remove(ev)
            except ValueError:
                pass
            self.save_tasks_to_csv()
            self.grid_panel.Refresh()

        elif dlg.saved:
            updated = dlg.get_event()
            ev["title"] = updated["title"]
            ev["date"] = updated["date"]
            ev["start"] = updated["start"]
            ev["end"] = updated["end"]
            ev["color_index"] = updated.get("color_index", ev.get("color_index", 0))
            ev["completed"] = updated.get("completed", False)

            self.save_tasks_to_csv()

            event_week_start = ev["date"] - datetime.timedelta(days=ev["date"].weekday())
            if event_week_start != self.week_start:
                self.week_start = event_week_start
                self.month_label.SetLabel(self.week_start.strftime("%B %Y"))
                self.recalc_grid_size()

            self.grid_panel.Refresh()

        dlg.Destroy()

    # ======================================================
    # ADD EVENT
    # ======================================================
    def on_new_event(self, evt):
        dlg = AddEventDialog(self, self.week_start + datetime.timedelta(days=1))
        if dlg.ShowModal() == wx.ID_OK:
            new_event = dlg.get_event()
            self.events.append(new_event)

            self.save_tasks_to_csv()

            event_date = new_event["date"]
            event_week_start = event_date - datetime.timedelta(days=event_date.weekday())

            if event_week_start != self.week_start:
                self.week_start = event_week_start
                self.month_label.SetLabel(self.week_start.strftime("%B %Y"))
                self.recalc_grid_size()

            self.grid_panel.Refresh()
        dlg.Destroy()

    # ======================================================
    # WEEK NAVIGATION
    # ======================================================
    def on_prev_week(self, evt):
        self.week_start -= datetime.timedelta(days=7)
        self.month_label.SetLabel(self.week_start.strftime("%B %Y"))
        self.recalc_grid_size()
        self.grid_panel.Refresh()

    def on_next_week(self, evt):
        self.week_start += datetime.timedelta(days=7)
        self.month_label.SetLabel(self.week_start.strftime("%B %Y"))
        self.recalc_grid_size()
        self.grid_panel.Refresh()

    # ======================================================
    def close(self):
        if self.back_callback:
            self.back_callback()

    # ======================================================
    def circle_bitmap(self, size, color):
        bmp = wx.Bitmap(size, size)
        dc = wx.MemoryDC(bmp)
        dc.SetBackground(wx.Brush(BG))
        dc.Clear()
        dc.SetBrush(wx.Brush(color))
        dc.SetPen(wx.Pen(color))
        dc.DrawCircle(size // 2, size // 2, size // 2)
        dc.SelectObject(wx.NullBitmap)
        return bmp


# ============================================================
# ADD EVENT DIALOG
# ============================================================
class AddEventDialog(wx.Dialog):
    def __init__(self, parent, date):
        super().__init__(parent, title="Add Event", size=(460, 300))

        self.date = date

        pnl = wx.Panel(self)
        s = wx.BoxSizer(wx.VERTICAL)

        h1 = wx.BoxSizer(wx.HORIZONTAL)
        h1.Add(wx.StaticText(pnl, label="Title:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.title_txt = wx.TextCtrl(pnl, value="New Event")
        h1.Add(self.title_txt, 1)
        s.Add(h1, 0, wx.ALL | wx.EXPAND, 10)

        h2 = wx.BoxSizer(wx.HORIZONTAL)
        h2.Add(wx.StaticText(pnl, label="Date (dd/mm/yyyy):"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.date_picker = wx.adv.DatePickerCtrl(pnl, style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        self.date_picker.SetValue(wx.DateTime.FromDMY(date.day, date.month - 1, date.year))
        h2.Add(self.date_picker, 1)
        s.Add(h2, 0, wx.ALL | wx.EXPAND, 10)

        h3 = wx.BoxSizer(wx.HORIZONTAL)
        h3.Add(wx.StaticText(pnl, label="Start Time:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

        self.start_hour = wx.SpinCtrl(pnl, min=0, max=23, initial=9, size=(60, -1))
        self.start_minute = wx.SpinCtrl(pnl, min=0, max=59, initial=0, size=(60, -1))

        h3.Add(self.start_hour, 0, wx.RIGHT, 5)
        h3.Add(self.start_minute, 0)
        s.Add(h3, 0, wx.ALL, 10)

        h4 = wx.BoxSizer(wx.HORIZONTAL)
        h4.Add(wx.StaticText(pnl, label="Duration (hrs):"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.duration = wx.SpinCtrl(pnl, min=1, max=12, initial=1)
        h4.Add(self.duration)
        s.Add(h4, 0, wx.ALL, 10)

        h5 = wx.BoxSizer(wx.HORIZONTAL)
        h5.Add(wx.StaticText(pnl, label="Color:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.color_picker = ColorPicker(pnl, initial_index=0)
        h5.Add(self.color_picker, 0, wx.ALIGN_CENTER_VERTICAL)
        s.Add(h5, 0, wx.ALL, 10)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(pnl, wx.ID_OK, "OK", size=(90, 32))
        cancel_btn = wx.Button(pnl, wx.ID_CANCEL, "Cancel", size=(90, 32))

        btn_sizer.AddStretchSpacer(1)
        btn_sizer.Add(ok_btn, 0, wx.RIGHT, 10)
        btn_sizer.Add(cancel_btn, 0)

        s.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)

        pnl.SetSizer(s)

    def get_event(self):
        title = self.title_txt.GetValue()

        dt = self.date_picker.GetValue()
        date = datetime.date(dt.GetYear(), dt.GetMonth() + 1, dt.GetDay())

        start_hour = self.start_hour.GetValue()
        start_minute = self.start_minute.GetValue()
        start_time = datetime.time(start_hour, start_minute)

        duration = self.duration.GetValue()
        end_dt = datetime.datetime.combine(date, start_time) + datetime.timedelta(hours=duration)

        return {
            "title": title,
            "date": date,
            "start": start_time,
            "end": end_dt.time(),
            "color_index": self.color_picker.get(),
            "completed": False,
        }


# ============================================================
# EDIT EVENT DIALOG
# ============================================================
class EditEventDialog(wx.Dialog):
    def __init__(self, parent, event):
        super().__init__(parent, title="Edit Event", size=(480, 360))
        self.event = event.copy()
        self.saved = False
        self.deleted = False

        pnl = wx.Panel(self)
        s = wx.BoxSizer(wx.VERTICAL)

        h1 = wx.BoxSizer(wx.HORIZONTAL)
        h1.Add(wx.StaticText(pnl, label="Title:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.title_txt = wx.TextCtrl(pnl, value=self.event.get("title", ""))
        h1.Add(self.title_txt, 1)
        s.Add(h1, 0, wx.ALL | wx.EXPAND, 10)

        h2 = wx.BoxSizer(wx.HORIZONTAL)
        h2.Add(wx.StaticText(pnl, label="Date (dd/mm/yyyy):"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.date_picker = wx.adv.DatePickerCtrl(pnl, style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        dt = self.event["date"]
        self.date_picker.SetValue(wx.DateTime.FromDMY(dt.day, dt.month - 1, dt.year))
        h2.Add(self.date_picker, 1)
        s.Add(h2, 0, wx.ALL | wx.EXPAND, 10)

        h3 = wx.BoxSizer(wx.HORIZONTAL)
        h3.Add(wx.StaticText(pnl, label="Start Time:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

        self.start_hour = wx.SpinCtrl(pnl, min=0, max=23, initial=self.event["start"].hour, size=(60, -1))
        self.start_minute = wx.SpinCtrl(pnl, min=0, max=59, initial=self.event["start"].minute, size=(60, -1))

        h3.Add(self.start_hour, 0, wx.RIGHT, 5)
        h3.Add(self.start_minute, 0)
        s.Add(h3, 0, wx.ALL, 10)

        h4 = wx.BoxSizer(wx.HORIZONTAL)
        h4.Add(wx.StaticText(pnl, label="Duration (hrs):"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

        start = datetime.datetime.combine(datetime.date.today(), self.event["start"])
        end = datetime.datetime.combine(datetime.date.today(), self.event["end"])
        dur_hours = int((end - start).total_seconds() // 3600) or 1

        self.duration = wx.SpinCtrl(pnl, min=1, max=24, initial=dur_hours)
        h4.Add(self.duration)
        s.Add(h4, 0, wx.ALL, 10)

        h5 = wx.BoxSizer(wx.HORIZONTAL)
        h5.Add(wx.StaticText(pnl, label="Color:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.color_picker = ColorPicker(pnl, initial_index=self.event.get("color_index", 0))
        h5.Add(self.color_picker, 0, wx.ALIGN_CENTER_VERTICAL)
        s.Add(h5, 0, wx.ALL, 10)

        h6 = wx.BoxSizer(wx.HORIZONTAL)
        self.completed_cb = wx.CheckBox(pnl, label="Mark as completed")
        self.completed_cb.SetValue(bool(self.event.get("completed", False)))
        h6.Add(self.completed_cb, 0, wx.ALIGN_CENTER_VERTICAL)
        s.Add(h6, 0, wx.ALL, 10)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        save_btn = wx.Button(pnl, wx.ID_OK, "Save")
        delete_btn = wx.Button(pnl, label="Delete")
        cancel_btn = wx.Button(pnl, wx.ID_CANCEL, "Cancel")

        btn_sizer.AddStretchSpacer(1)
        btn_sizer.Add(save_btn, 0, wx.RIGHT, 8)
        btn_sizer.Add(delete_btn, 0, wx.RIGHT, 8)
        btn_sizer.Add(cancel_btn, 0)

        s.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)

        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        delete_btn.Bind(wx.EVT_BUTTON, self.on_delete)
        cancel_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))

        pnl.SetSizer(s)

    def on_save(self, evt):
        title = self.title_txt.GetValue().strip()
        if not title:
            wx.MessageBox("Please enter a title.", "Validation", wx.OK | wx.ICON_WARNING)
            return
        self.saved = True
        self.EndModal(wx.ID_OK)

    def on_delete(self, evt):
        dlg = wx.MessageDialog(self, "Delete this event?", "Confirm", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
        if dlg.ShowModal() == wx.ID_YES:
            self.deleted = True
            self.EndModal(wx.ID_OK)
        dlg.Destroy()

    def get_event(self):
        title = self.title_txt.GetValue()

        dt = self.date_picker.GetValue()
        date = datetime.date(dt.GetYear(), dt.GetMonth() + 1, dt.GetDay())

        start_hour = self.start_hour.GetValue()
        start_minute = self.start_minute.GetValue()
        start_time = datetime.time(start_hour, start_minute)

        duration = self.duration.GetValue()
        end_time = (datetime.datetime.combine(date, start_time) + datetime.timedelta(hours=duration)).time()

        return {
            "title": title,
            "date": date,
            "start": start_time,
            "end": end_time,
            "color_index": self.color_picker.get(),
            "completed": bool(self.completed_cb.GetValue()),
        }


# ============================================================
# TEST HARNESS
# ============================================================
if __name__ == "__main__":
    app = wx.App(False)
    f = wx.Frame(None, size=(1400, 800))
    t = TasksScreen(f, nav_callback=lambda x: print("Nav:", x))
    f.Show()
    app.MainLoop()
