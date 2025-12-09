'''# modules/tasks_screen.py

import wx
import wx.adv
from datetime import datetime, timedelta, date, time
from modules.database_handler import load_tasks, save_tasks

# -------------------------
# Theme / Colors
# -------------------------
BG_COLOR = "#081024"         # deep navy
SIDEBAR_COLOR = "#0e1622"    # sidebar base
SIDEBAR_COLLAPSED_W = 72
SIDEBAR_EXPANDED_W = 260
CONTENT_BG = "#0b1120"
GRID_LINE = "#1f2a36"
HOUR_LABEL = "#9FB7C9"
TEXT_COLOR = "#E6EEF6"
ACCENT = "#3EE0F0"
EVENT_COLORS = [
    "#A7F3D0", "#C7B3FF", "#FFD1DC", "#BEE3FF", "#FDE68A"
]  # pastel palette

# Calendar layout
LEFT_GUTTER = 60
TOP_HEADER = 110
DAY_COL_WIDTH = 180
HOUR_ROW_HEIGHT = 48
HOURS = list(range(24))  # 00..23


# -------------------------
# Helpers
# -------------------------
def start_of_week(dt: date):
    return dt - timedelta(days=dt.weekday())


def parse_deadline(deadline_str: str):
    """Parse 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM'"""
    if not deadline_str or deadline_str in ("-", ""):
        return None, None

    try:
        if " " in deadline_str:
            dt = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
            return dt.date(), dt.time()
        else:
            d = datetime.strptime(deadline_str, "%Y-%m-%d").date()
            return d, time(hour=9, minute=0)  # default time
    except:
        return None, None


def date_to_col_idx(base_monday: date, d: date):
    delta = (d - base_monday).days
    return delta if 0 <= delta < 7 else None


# -------------------------
# Glow Effect (Safe)
# -------------------------
def draw_rounded_rect_with_glow(gc, x, y, w, h, radius, fill_colour, glow=False):
    # main rectangle
    path = gc.CreatePath()
    path.AddRoundedRectangle(x, y, w, h, radius)
    gc.SetBrush(wx.Brush(fill_colour))
    gc.SetPen(wx.TRANSPARENT_PEN)
    gc.DrawPath(path)

    if glow:
        # soft cyan glow
        for i, alpha in enumerate((60, 30, 12), start=1):
            gpath = gc.CreatePath()
            expand = i * 3
            gpath.AddRoundedRectangle(
                x - expand, y - expand,
                w + expand * 2, h + expand * 2,
                radius + i * 1.5
            )
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.SetPen(wx.Pen(wx.Colour(62, 224, 240, alpha), width=4 + i * 2))
            gc.DrawPath(gpath)


# -------------------------
# Collapsible Sidebar
# -------------------------
class CollapsibleSidebar(wx.Panel):
    def __init__(self, parent, width_expanded, switch_callback_map=None):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.expanded_w = width_expanded
        self.collapsed_w = SIDEBAR_COLLAPSED_W
        self.is_collapsed = False
        self.switch_map = switch_callback_map or {}
        self.SetBackgroundColour(SIDEBAR_COLOR)

        self.title_font = wx.Font(
            20, wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        )
        self.item_font = wx.Font(
            10, wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        )

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.build_expanded()

    def build_expanded(self):
        self.sizer.Clear(True)
        self.SetMinSize((self.expanded_w, -1))

        # Top bar
        top = wx.BoxSizer(wx.HORIZONTAL)
        logo = wx.StaticText(self, label="S")
        logo.SetFont(self.title_font)
        logo.SetForegroundColour(ACCENT)
        top.Add(logo, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 12)

        collapse = wx.Button(self, label="⟨", size=(36, 28))
        collapse.SetBackgroundColour(CONTENT_BG)
        collapse.SetForegroundColour(TEXT_COLOR)
        collapse.Bind(wx.EVT_BUTTON, self.toggle)
        top.AddStretchSpacer()
        top.Add(collapse, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 8)
        self.sizer.Add(top, 0, wx.EXPAND)

        menu_items = [
            "Home", "Today", "Upcoming", "Schedule", "Notes",
            "Tasks", "Assignments", "Exams", "Projects", "Resources"
        ]

        for label in menu_items:
            btn = wx.Button(self, label=label, style=wx.NO_BORDER)
            btn.SetFont(self.item_font)
            btn.SetForegroundColour(TEXT_COLOR)
            btn.SetBackgroundColour(SIDEBAR_COLOR)

            btn.Bind(wx.EVT_ENTER_WINDOW, lambda e, b=btn: b.SetBackgroundColour("#16202a"))
            btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e, b=btn: b.SetBackgroundColour(SIDEBAR_COLOR))

            self.sizer.Add(btn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        self.sizer.AddStretchSpacer()
        self.Layout()

    def build_collapsed(self):
        self.sizer.Clear(True)
        self.SetMinSize((self.collapsed_w, -1))

        top = wx.BoxSizer(wx.VERTICAL)
        logo = wx.StaticText(self, label="S")
        logo.SetFont(self.title_font)
        logo.SetForegroundColour(ACCENT)
        top.Add(logo, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 12)

        expand = wx.Button(self, label="⟩", size=(36, 28))
        expand.SetBackgroundColour(CONTENT_BG)
        expand.SetForegroundColour(TEXT_COLOR)
        expand.Bind(wx.EVT_BUTTON, self.toggle)
        top.Add(expand, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 6)
        self.sizer.Add(top, 0, wx.EXPAND)

        icons = ["H", "T", "U", "S", "N", "Tk", "A", "E", "P", "R"]
        for letter in icons:
            b = wx.Button(self, label=letter, size=(44, 36))
            b.SetBackgroundColour(SIDEBAR_COLOR)
            b.SetForegroundColour(TEXT_COLOR)
            self.sizer.Add(b, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 6)

        self.sizer.AddStretchSpacer()
        self.Layout()

    def toggle(self, evt):
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.build_collapsed()
        else:
            self.build_expanded()
        self.parent.Layout()


# -------------------------
# New Event Dialog
# -------------------------
class NewEventDialog(wx.Dialog):
    def __init__(self, parent, default_date=None):
        super().__init__(parent, title="New Event", size=(460, 260))
        self.SetBackgroundColour(BG_COLOR)
        self.default_date = default_date or date.today()
        self.build_ui()

    def build_ui(self):
        s = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridBagSizer(6, 10)

        lbl_title = wx.StaticText(self, label="Title")
        self.txt_title = wx.TextCtrl(self)
        grid.Add(lbl_title, pos=(0, 0))
        grid.Add(self.txt_title, pos=(0, 1), span=(1, 3), flag=wx.EXPAND)

        lbl_date = wx.StaticText(self, label="Date")
        self.date_ctrl = wx.adv.DatePickerCtrl(self)
        d = self.default_date
        self.date_ctrl.SetValue(wx.DateTime.FromDMY(d.day, d.month - 1, d.year))
        grid.Add(lbl_date, pos=(1, 0))
        grid.Add(self.date_ctrl, pos=(1, 1))

        lbl_time = wx.StaticText(self, label="Time (24h)")
        self.time_ctrl = wx.TextCtrl(self, value="09:00")
        grid.Add(lbl_time, pos=(1, 2))
        grid.Add(self.time_ctrl, pos=(1, 3))

        lbl_sub = wx.StaticText(self, label="Subject")
        self.txt_sub = wx.TextCtrl(self)
        grid.Add(lbl_sub, pos=(2, 0))
        grid.Add(self.txt_sub, pos=(2, 1), span=(1, 3), flag=wx.EXPAND)

        btns = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        s.Add(grid, 1, wx.ALL | wx.EXPAND, 12)
        s.Add(btns, 0, wx.ALL | wx.ALIGN_RIGHT, 10)
        self.SetSizer(s)

    def get_data(self):
        title = self.txt_title.GetValue().strip() or "Untitled"

        dt = self.date_ctrl.GetValue()
        year = dt.GetYear()
        month = dt.GetMonth() + 1
        day = dt.GetDay()

        raw_time = self.time_ctrl.GetValue().strip() or "09:00"
        try:
            hh, mm = map(int, raw_time.split(":"))
            hh = max(0, min(23, hh))
            mm = max(0, min(59, mm))
        except:
            hh, mm = 9, 0

        deadline = f"{year:04d}-{month:02d}-{day:02d} {hh:02d}:{mm:02d}"

        subject = self.txt_sub.GetValue().strip() or "-"

        return {
            "task": title,
            "subject": subject,
            "deadline": deadline,
            "priority": "Medium",
            "status": "Pending"
        }


# -------------------------
# Weekly Calendar Renderer
# -------------------------
class WeekCalendar(wx.Panel):
    def __init__(self, parent, week_start: date):
        wx.Panel.__init__(self, parent)
        self.week_start = week_start
        self.SetBackgroundColour(CONTENT_BG)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.reload_events()

    def reload_events(self):
        raw = load_tasks()
        self.events = []

        for i, t in enumerate(raw):
            d, tm = parse_deadline(t.get("deadline", ""))
            if d:
                self.events.append({
                    "title": t.get("task", "Untitled"),
                    "subject": t.get("subject", "-"),
                    "date": d,
                    "time": tm or time(9),
                    "idx": i
                })
        self.Refresh()

    def on_paint(self, evt):
        w, h = self.GetSize()
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        gc.SetBrush(wx.Brush(CONTENT_BG))
        gc.DrawRectangle(0, 0, w, h)

        # --- HEADER (days) ---
        gc.SetFont(wx.Font(14, wx.FONTFAMILY_SWISS,
                           wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        for c in range(7):
            x = LEFT_GUTTER + c * DAY_COL_WIDTH
            dy = self.week_start + timedelta(days=c)
            label = f"{dy.strftime('%a')} {dy.day}"
            gc.DrawText(label, x + 10, 20)

        # --- GRID ---
        gc.SetFont(wx.Font(9, wx.FONTFAMILY_SWISS,
                           wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        for hour in HOURS:
            y = TOP_HEADER + hour * HOUR_ROW_HEIGHT
            gc.SetPen(wx.Pen(GRID_LINE))
            gc.DrawLine(LEFT_GUTTER, y, w, y)
            gc.DrawText(f"{hour:02d}:00", 6, y + HOUR_ROW_HEIGHT // 2 - 6)

        for c in range(7):
            x = LEFT_GUTTER + c * DAY_COL_WIDTH
            gc.DrawLine(x, TOP_HEADER, x, h)

        # --- EVENTS ---
        for ev in self.events:
            col = date_to_col_idx(self.week_start, ev["date"])
            if col is None:
                continue

            start = ev["time"].hour + ev["time"].minute / 60
            y = TOP_HEADER + start * HOUR_ROW_HEIGHT
            x = LEFT_GUTTER + col * DAY_COL_WIDTH + 8
            wbox = DAY_COL_WIDTH - 16
            hbox = HOUR_ROW_HEIGHT - 10

            color = EVENT_COLORS[ev["idx"] % len(EVENT_COLORS)]
            draw_rounded_rect_with_glow(gc, x, y + 5, wbox, hbox, 10, color, glow=True)

            gc.SetFont(wx.Font(9, wx.FONTFAMILY_SWISS,
                               wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            gc.DrawText(f"{ev['title']} • {ev['time'].strftime('%H:%M')}", x + 8, y + 12)


# -------------------------
# MAIN SCREEN (renamed to TasksScreen)
# -------------------------
class TasksScreen(wx.Panel):
    def __init__(self, parent, switch_to_home):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.switch_to_home = switch_to_home

        self.current_monday = start_of_week(date.today())

        main = wx.BoxSizer(wx.VERTICAL)

        # ----- HEADER -----
        header = wx.BoxSizer(wx.HORIZONTAL)

        self.lbl_month = wx.StaticText(self, label=self.current_monday.strftime("%B %Y"))
        self.lbl_month.SetForegroundColour(TEXT_COLOR)
        self.lbl_month.SetFont(wx.Font(
            20, wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        ))

        prev = wx.Button(self, label="◀")
        nxt = wx.Button(self, label="▶")
        prev.Bind(wx.EVT_BUTTON, lambda e: self.change_week(-1))
        nxt.Bind(wx.EVT_BUTTON, lambda e: self.change_week(1))

        search = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        search.SetMinSize((200, 30))

        add_btn = wx.Button(self, label="+ New Event")
        add_btn.SetBackgroundColour(ACCENT)
        add_btn.SetForegroundColour("#00141A")
        add_btn.Bind(wx.EVT_BUTTON, self.create_event)

        header.Add(self.lbl_month, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 20)
        header.Add(prev, 0, wx.LEFT | wx.RIGHT, 12)
        header.Add(nxt, 0, wx.RIGHT, 24)
        header.AddStretchSpacer()
        header.Add(search, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 12)
        header.Add(add_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 20)

        main.Add(header, 0, wx.EXPAND | wx.TOP, 12)
        main.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 6)

        # ----- CONTENT (SIDEBAR + CALENDAR) -----
        content = wx.BoxSizer(wx.HORIZONTAL)

        # Sidebar
        self.sidebar = CollapsibleSidebar(self, SIDEBAR_EXPANDED_W)
        content.Add(self.sidebar, 0, wx.EXPAND)

        # Calendar area
        self.calendar_panel = wx.Panel(self)
        csz = wx.BoxSizer(wx.VERTICAL)

        week_lbl = wx.StaticText(self.calendar_panel, label="Week View")
        week_lbl.SetForegroundColour(HOUR_LABEL)
        week_lbl.SetFont(wx.Font(
            10, wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
        ))
        csz.Add(week_lbl, 0, wx.LEFT | wx.TOP, 8)

        self.week_cal = WeekCalendar(self.calendar_panel, self.current_monday)
        csz.Add(self.week_cal, 1, wx.EXPAND | wx.ALL, 8)

        self.calendar_panel.SetSizer(csz)
        content.Add(self.calendar_panel, 1, wx.EXPAND)

        main.Add(content, 1, wx.EXPAND)
        self.SetSizer(main)

    # ---------------- Week Navigation ----------------
    def change_week(self, delta):
        self.current_monday += timedelta(weeks=delta)
        self.lbl_month.SetLabel(self.current_monday.strftime("%B %Y"))
        self.week_cal.week_start = self.current_monday
        self.week_cal.reload_events()
        self.week_cal.Refresh()

    # ---------------- Create Event ----------------
    def create_event(self, evt):
        dlg = NewEventDialog(self, default_date=self.current_monday)
        if dlg.ShowModal() == wx.ID_OK:
            ev = dlg.get_data()
            tasks = load_tasks()
            tasks.append(ev)
            save_tasks(tasks)
            self.week_cal.reload_events()
        dlg.Destroy()'''
'''# ============================================================
# StudyAura — Calendar View Tasks Screen (FINAL VERSION - PATCHED)
# Compatible with older wxPython versions (FONTSTYLE fix)
# ============================================================

import wx
import wx.adv
import wx.lib.scrolledpanel as scrolled
import datetime

# ============================
# CONFIGURATION
# ============================
LEFT_PANEL_W = 220
HEADER_H = 100
DAY_BAR_H = 48

HOUR_START = 8
HOUR_END = 22
HOUR_HEIGHT = 72

GRID_COL_GAP = 12
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
]


# ============================
# SAMPLE EVENTS
# ============================
def sample_events(week_start):
    def add(day_offset, hour, title, dur=1, color=0):
        date = week_start + datetime.timedelta(days=day_offset)
        start = datetime.time(hour, 0)
        end_dt = datetime.datetime.combine(date, start) + datetime.timedelta(hours=dur)
        return {
            "title": title,
            "date": date,
            "start": start,
            "end": end_dt.time(),
            "color_index": color
        }

    return [
        add(1, 9, "Math Quiz", 1, 1),
        add(2, 13, "Physics Lab", 1, 0),
        add(2, 19, "Revision: Ch5", 1, 2),
        add(4, 15, "History Essay", 2, 1),
        add(6, 18, "Group Study", 1, 3),
        add(0, 10, "Chemistry Pract", 1, 0),
    ]


# ============================================================
# MAIN TASKS SCREEN
# ============================================================
class TasksScreen(wx.Panel):
    def __init__(self, parent, back_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.back_callback = back_callback

        self.SetBackgroundColour(BG)

        today = datetime.date.today()
        self.week_start = today - datetime.timedelta(days=today.weekday())

        self.events = sample_events(self.week_start)

        self.build_ui()
        wx.CallAfter(self.recalc_grid_size)

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
    # SIDEBAR
    # ======================================================
    def build_sidebar(self):
        p = wx.Panel(self, size=(LEFT_PANEL_W, -1))
        p.SetBackgroundColour(wx.Colour(24, 32, 44))

        s = wx.BoxSizer(wx.VERTICAL)

        logo = wx.StaticText(p, label="S")
        logo.SetFont(wx.Font(34, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        logo.SetForegroundColour(NEON)

        s.AddSpacer(20)
        s.Add(logo, 0, wx.LEFT, 20)
        s.AddSpacer(20)

        items = ["Home", "Today", "Upcoming", "Schedule", "Notes", "Tasks", "Assignments", "Exams", "Projects", "Resources"]

        for it in items:
            b = wx.Button(p, label=it, style=wx.BORDER_NONE)
            b.SetForegroundColour(TEXT_LIGHT)
            b.SetBackgroundColour(wx.Colour(0, 0, 0, 0))
            b.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            s.Add(b, 0, wx.LEFT | wx.TOP | wx.EXPAND, 15)

        s.AddStretchSpacer()
        s.Add(wx.StaticLine(p), 0, wx.EXPAND | wx.ALL, 10)

        settings = wx.Button(p, label="Settings", style=wx.BORDER_NONE)
        settings.SetForegroundColour(TEXT_LIGHT)
        settings.SetBackgroundColour(wx.Colour(0, 0, 0, 0))
        s.Add(settings, 0, wx.LEFT | wx.BOTTOM, 15)

        p.SetSizer(s)
        return p

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
    # HEADER
    # ======================================================
    def build_header(self, parent):
        p = wx.Panel(parent, size=(-1, HEADER_H))
        p.SetBackgroundColour(BG)

        s = wx.BoxSizer(wx.HORIZONTAL)

        self.month_label = wx.StaticText(p, label=self.week_start.strftime("%B %Y"))
        self.month_label.SetFont(wx.Font(28, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.month_label.SetForegroundColour(TEXT_LIGHT)

        s.Add(self.month_label, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        s.AddStretchSpacer()

        self.toggle = wx.ToggleButton(p, label="Dark mode is on")
        self.toggle.SetValue(True)
        self.toggle.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle)
        s.Add(self.toggle, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 20)

        b = wx.Button(p, label="+ New Event")
        b.Bind(wx.EVT_BUTTON, self.on_new_event)
        s.Add(b, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 20)

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

        s = wx.BoxSizer(wx.HORIZONTAL)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        for d in days:
            lbl = wx.StaticText(p, label=d)
            lbl.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            lbl.SetForegroundColour(TEXT_LIGHT)
            s.Add(lbl, 1, wx.ALIGN_CENTER | wx.TOP, 10)

        p.SetSizer(s)
        return p

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

    # ======================================================
    def recalc_grid_size(self):
        total_hours = HOUR_END - HOUR_START
        height = total_hours * HOUR_HEIGHT + 40
        width = (140 + GRID_COL_GAP) * DAY_COL_COUNT
        self.grid_panel.SetMinSize((width, height))
        self.grid_panel.GetParent().FitInside()
        self.grid_panel.Refresh()

    # ======================================================
    # GRID PAINT
    # ======================================================
    def on_paint_grid(self, evt):
        dc = wx.AutoBufferedPaintDC(self.grid_panel)

        dc.SetBackground(wx.Brush(BG))
        dc.Clear()

        w, h = self.grid_panel.GetSize()

        left_margin = 40
        top_margin = 10
        col_w = 140

        # Day columns
        for col in range(DAY_COL_COUNT):
            x = left_margin + col * (col_w + GRID_COL_GAP)
            dc.SetBrush(wx.Brush(wx.Colour(22, 28, 38)))
            dc.SetPen(wx.Pen(wx.Colour(44, 54, 68)))
            dc.DrawRoundedRectangle(x, top_margin, col_w, h - 20, 6)

            date = self.week_start + datetime.timedelta(days=col)

            dc.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            dc.SetTextForeground(TEXT_LIGHT)
            dc.DrawText(str(date.day), x + 10, top_margin + 5)

        # Hour lines
        for i in range(HOUR_END - HOUR_START + 1):
            y = top_margin + i * HOUR_HEIGHT

            dc.SetPen(wx.Pen(wx.Colour(34, 42, 54)))
            dc.DrawLine(left_margin, y, left_margin + (col_w + GRID_COL_GAP) * DAY_COL_COUNT, y)

            hour = HOUR_START + i
            label = f"{(hour - 1) % 12 + 1} {'AM' if hour < 12 else 'PM'}"

            dc.SetFont(wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            dc.SetTextForeground(wx.Colour(150, 160, 170))
            dc.DrawText(label, left_margin - 40, y - 6)

        # Draw events
        for ev in self.events:
            self.draw_event(dc, ev, col_w, left_margin, top_margin)

    # ======================================================
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

        color = EVENT_COLORS[ev["color_index"]]

        dc.SetBrush(wx.Brush(color))
        dc.SetPen(wx.Pen(color))
        dc.DrawRoundedRectangle(x, y1 + 2, w, h - 4, 6)

        dc.SetTextForeground(wx.Colour(10, 10, 10))
        dc.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        dc.DrawText(ev["title"], x + 6, y1 + 8)

    # ======================================================
    # CLICK HANDLER
    # ======================================================
    def on_grid_click(self, evt):
        pos = evt.GetPosition()

        col_w = 140
        left_margin = 40
        top_margin = 10

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
                self.show_event(ev)
                return

    def show_event(self, ev):
        info = f"{ev['title']}\n\nDate: {ev['date']}\nStart: {ev['start']}\nEnd: {ev['end']}"
        dlg = wx.MessageDialog(self, info, "Event Details", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    # ======================================================
    # NEW EVENT
    # ======================================================
    def on_new_event(self, evt):
        dlg = AddEventDialog(self, self.week_start + datetime.timedelta(days=1))
        if dlg.ShowModal() == wx.ID_OK:
            self.events.append(dlg.get_event())
            self.grid_panel.Refresh()
        dlg.Destroy()

    # ======================================================
    def on_toggle(self, evt):
        if self.toggle.GetValue():
            self.toggle.SetLabel("Dark mode is on")
        else:
            self.toggle.SetLabel("Dark mode is off")

    # ======================================================
    def close(self):
        if self.back_callback:
            self.back_callback()


# ============================================================
# ADD EVENT DIALOG
# ============================================================
class AddEventDialog(wx.Dialog):
    def __init__(self, parent, date):
        super().__init__(parent, title="Add Event", size=(420, 260))

        pnl = wx.Panel(self)
        s = wx.BoxSizer(wx.VERTICAL)

        # Title
        h1 = wx.BoxSizer(wx.HORIZONTAL)
        h1.Add(wx.StaticText(pnl, label="Title:"), 0, wx.RIGHT, 6)
        self.title_txt = wx.TextCtrl(pnl, value="New Event")
        h1.Add(self.title_txt, 1)
        s.Add(h1, 0, wx.ALL | wx.EXPAND, 10)

        # Date
        h2 = wx.BoxSizer(wx.HORIZONTAL)
        h2.Add(wx.StaticText(pnl, label="Date:"), 0, wx.RIGHT, 6)
        self.date_picker = wx.adv.DatePickerCtrl(pnl, style=wx.adv.DP_DROPDOWN)
        self.date_picker.SetValue(wx.DateTime.FromDMY(date.day, date.month - 1, date.year))
        h2.Add(self.date_picker, 1)
        s.Add(h2, 0, wx.ALL | wx.EXPAND, 10)

        # Start hour
        h3 = wx.BoxSizer(wx.HORIZONTAL)
        h3.Add(wx.StaticText(pnl, label="Start Hour:"), 0, wx.RIGHT, 6)
        self.start_hour = wx.SpinCtrl(pnl, min=0, max=23, initial=9)
        h3.Add(self.start_hour)
        s.Add(h3, 0, wx.ALL, 10)

        # Duration
        h4 = wx.BoxSizer(wx.HORIZONTAL)
        h4.Add(wx.StaticText(pnl, label="Duration (hrs):"), 0, wx.RIGHT, 6)
        self.duration = wx.SpinCtrl(pnl, min=1, max=12, initial=1)
        h4.Add(self.duration)
        s.Add(h4, 0, wx.ALL, 10)

        # ------------------------------
        # FIXED BUTTONS
        # ------------------------------
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(pnl, wx.ID_OK, "OK")
        cancel_btn = wx.Button(pnl, wx.ID_CANCEL, "Cancel")

        btn_sizer.AddStretchSpacer(1)
        btn_sizer.Add(ok_btn, 0, wx.RIGHT, 10)
        btn_sizer.Add(cancel_btn, 0)

        s.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)
        # ------------------------------

        pnl.SetSizer(s)

    def get_event(self):
        title = self.title_txt.GetValue()

        dt = self.date_picker.GetValue()
        date = datetime.date(dt.GetYear(), dt.GetMonth() + 1, dt.GetDay())

        start_hour = self.start_hour.GetValue()
        duration = self.duration.GetValue()

        start_time = datetime.time(start_hour, 0)
        end_time = (datetime.datetime.combine(date, start_time)
                    + datetime.timedelta(hours=duration)).time()

        return {
            "title": title,
            "date": date,
            "start": start_time,
            "end": end_time,
            "color_index": 0
        }
'''
'''# ============================================================
# StudyAura — Calendar View Tasks Screen (FINAL STABLE VERSION)
# Fully compatible with user main.py
# Includes:
#  - Week auto-switch (Option B)
#  - Sunday visibility fix
#  - AddEventDialog parent fix
#  - Font constant fixes
#  - No wx assertions
# ============================================================

import wx
import wx.adv
import wx.lib.scrolledpanel as scrolled
import datetime

# ============================
# CONFIGURATION
# ============================
LEFT_PANEL_W = 220
HEADER_H = 100
DAY_BAR_H = 48

HOUR_START = 8
HOUR_END = 22
HOUR_HEIGHT = 72

GRID_COL_GAP = 12
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
]


# ============================
# SAMPLE EVENTS
# ============================
def sample_events(week_start):
    def add(day_offset, hour, title, dur=1, color=0):
        date = week_start + datetime.timedelta(days=day_offset)
        start = datetime.time(hour, 0)
        end_dt = datetime.datetime.combine(date, start) + datetime.timedelta(hours=dur)
        return {
            "title": title,
            "date": date,
            "start": start,
            "end": end_dt.time(),
            "color_index": color
        }

    return [
        add(1, 9, "Math Quiz", 1, 1),
        add(2, 13, "Physics Lab", 1, 0),
        add(2, 19, "Revision: Ch5", 1, 2),
        add(4, 15, "History Essay", 2, 1),
        add(6, 18, "Group Study", 1, 3),
        add(0, 10, "Chemistry Pract", 1, 0),
    ]


# ============================================================
# MAIN TASKS SCREEN
# ============================================================
class TasksScreen(wx.Panel):
    def __init__(self, parent, back_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.back_callback = back_callback

        self.SetBackgroundColour(BG)

        today = datetime.date.today()
        self.week_start = today - datetime.timedelta(days=today.weekday())

        self.events = sample_events(self.week_start)

        self.build_ui()
        wx.CallAfter(self.recalc_grid_size)

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
    # SIDEBAR
    # ======================================================
    def build_sidebar(self):
        p = wx.Panel(self, size=(LEFT_PANEL_W, -1))
        p.SetBackgroundColour(wx.Colour(24, 32, 44))

        s = wx.BoxSizer(wx.VERTICAL)

        logo = wx.StaticText(p, label="S")
        logo.SetFont(wx.Font(34, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        logo.SetForegroundColour(NEON)

        s.AddSpacer(20)
        s.Add(logo, 0, wx.LEFT, 20)
        s.AddSpacer(20)

        items = ["Home", "Today", "Upcoming", "Schedule", "Notes", "Tasks", "Assignments", "Exams", "Projects", "Resources"]

        for it in items:
            b = wx.Button(p, label=it, style=wx.BORDER_NONE)
            b.SetForegroundColour(TEXT_LIGHT)
            b.SetBackgroundColour(wx.Colour(0, 0, 0, 0))
            b.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            s.Add(b, 0, wx.LEFT | wx.TOP | wx.EXPAND, 15)

        s.AddStretchSpacer()
        s.Add(wx.StaticLine(p), 0, wx.EXPAND | wx.ALL, 10)

        settings = wx.Button(p, label="Settings", style=wx.BORDER_NONE)
        settings.SetForegroundColour(TEXT_LIGHT)
        settings.SetBackgroundColour(wx.Colour(0, 0, 0, 0))
        s.Add(settings, 0, wx.LEFT | wx.BOTTOM, 15)

        p.SetSizer(s)
        return p

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
    # HEADER
    # ======================================================
    def build_header(self, parent):
        p = wx.Panel(parent, size=(-1, HEADER_H))
        p.SetBackgroundColour(BG)

        s = wx.BoxSizer(wx.HORIZONTAL)

        self.month_label = wx.StaticText(p, label=self.week_start.strftime("%B %Y"))
        self.month_label.SetFont(wx.Font(28, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.month_label.SetForegroundColour(TEXT_LIGHT)

        s.Add(self.month_label, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        s.AddStretchSpacer()

        self.toggle = wx.ToggleButton(p, label="Dark mode is on")
        self.toggle.SetValue(True)
        self.toggle.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle)
        s.Add(self.toggle, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 20)

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

        s = wx.BoxSizer(wx.HORIZONTAL)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        for d in days:
            lbl = wx.StaticText(p, label=d)
            lbl.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            lbl.SetForegroundColour(TEXT_LIGHT)
            s.Add(lbl, 1, wx.ALIGN_CENTER | wx.TOP, 10)

        p.SetSizer(s)
        return p

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

    # ======================================================
    def recalc_grid_size(self):
        total_hours = HOUR_END - HOUR_START
        height = total_hours * HOUR_HEIGHT + 40

        # Sunday visibility fix
        width = (140 + GRID_COL_GAP) * DAY_COL_COUNT + 200

        self.grid_panel.SetMinSize((width, height))
        self.grid_panel.GetParent().FitInside()
        self.grid_panel.Refresh()

    # ======================================================
    # GRID PAINT
    # ======================================================
    def on_paint_grid(self, evt):
        dc = wx.AutoBufferedPaintDC(self.grid_panel)

        dc.SetBackground(wx.Brush(BG))
        dc.Clear()

        w, h = self.grid_panel.GetSize()

        left_margin = 40
        top_margin = 10
        col_w = 140

        # Day columns
        for col in range(DAY_COL_COUNT):
            x = left_margin + col * (col_w + GRID_COL_GAP)
            dc.SetBrush(wx.Brush(wx.Colour(22, 28, 38)))
            dc.SetPen(wx.Pen(wx.Colour(44, 54, 68)))
            dc.DrawRoundedRectangle(x, top_margin, col_w, h - 20, 6)

            date = self.week_start + datetime.timedelta(days=col)

            dc.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            dc.SetTextForeground(TEXT_LIGHT)
            dc.DrawText(str(date.day), x + 10, top_margin + 5)

        # Hour lines
        for i in range(HOUR_END - HOUR_START + 1):
            y = top_margin + i * HOUR_HEIGHT

            dc.SetPen(wx.Pen(wx.Colour(34, 42, 54)))
            dc.DrawLine(left_margin, y, left_margin + (col_w + GRID_COL_GAP) * DAY_COL_COUNT, y)

            hour = HOUR_START + i
            label = f"{(hour - 1) % 12 + 1} {'AM' if hour < 12 else 'PM'}"

            dc.SetFont(wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            dc.SetTextForeground(wx.Colour(150, 160, 170))
            dc.DrawText(label, left_margin - 40, y - 6)

        # Draw events
        for ev in self.events:
            self.draw_event(dc, ev, col_w, left_margin, top_margin)

    # ======================================================
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

        color = EVENT_COLORS[ev["color_index"]]

        dc.SetBrush(wx.Brush(color))
        dc.SetPen(wx.Pen(color))
        dc.DrawRoundedRectangle(x, y1 + 2, w, h - 4, 6)

        dc.SetTextForeground(wx.Colour(10, 10, 10))
        dc.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        dc.DrawText(ev["title"], x + 6, y1 + 8)

    # ======================================================
    # CLICK HANDLER
    # ======================================================
    def on_grid_click(self, evt):
        pos = evt.GetPosition()

        col_w = 140
        left_margin = 40
        top_margin = 10

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
                self.show_event(ev)
                return

    def show_event(self, ev):
        info = f"{ev['title']}\n\nDate: {ev['date']}\nStart: {ev['start']}\nEnd: {ev['end']}"
        dlg = wx.MessageDialog(self, info, "Event Details", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    # ======================================================
    # NEW EVENT (Option B: Auto Switch Week)
    # ======================================================
    def on_new_event(self, evt):
        dlg = AddEventDialog(self, self.week_start + datetime.timedelta(days=1))

        if dlg.ShowModal() == wx.ID_OK:
            new_event = dlg.get_event()
            self.events.append(new_event)

            # Auto-switch to event's week
            event_date = new_event["date"]
            event_week_start = event_date - datetime.timedelta(days=event_date.weekday())

            if event_week_start != self.week_start:
                self.week_start = event_week_start
                self.month_label.SetLabel(self.week_start.strftime("%B %Y"))
                self.recalc_grid_size()

            self.grid_panel.Refresh()

        dlg.Destroy()

    # ======================================================
    def on_toggle(self, evt):
        if self.toggle.GetValue():
            self.toggle.SetLabel("Dark mode is on")
        else:
            self.toggle.SetLabel("Dark mode is off")

    # ======================================================
    def close(self):
        if self.back_callback:
            self.back_callback()


# ============================================================
# ADD EVENT DIALOG (fixed parent bug)
# ============================================================
class AddEventDialog(wx.Dialog):
    def __init__(self, parent, date):
        super().__init__(parent, title="Add Event", size=(420, 260))

        pnl = wx.Panel(self)
        s = wx.BoxSizer(wx.VERTICAL)

        # Title
        h1 = wx.BoxSizer(wx.HORIZONTAL)
        h1.Add(wx.StaticText(pnl, label="Title:"), 0, wx.RIGHT, 6)
        self.title_txt = wx.TextCtrl(pnl, value="New Event")
        h1.Add(self.title_txt, 1)
        s.Add(h1, 0, wx.ALL | wx.EXPAND, 10)

        # Date
        h2 = wx.BoxSizer(wx.HORIZONTAL)
        h2.Add(wx.StaticText(pnl, label="Date:"), 0, wx.RIGHT, 6)
        self.date_picker = wx.adv.DatePickerCtrl(pnl, style=wx.adv.DP_DROPDOWN)
        self.date_picker.SetValue(wx.DateTime.FromDMY(date.day, date.month - 1, date.year))
        h2.Add(self.date_picker, 1)
        s.Add(h2, 0, wx.ALL | wx.EXPAND, 10)

        # Start hour
        h3 = wx.BoxSizer(wx.HORIZONTAL)
        h3.Add(wx.StaticText(pnl, label="Start Hour:"), 0, wx.RIGHT, 6)
        self.start_hour = wx.SpinCtrl(pnl, min=0, max=23, initial=9)
        h3.Add(self.start_hour)
        s.Add(h3, 0, wx.ALL, 10)

        # Duration
        h4 = wx.BoxSizer(wx.HORIZONTAL)
        h4.Add(wx.StaticText(pnl, label="Duration (hrs):"), 0, wx.RIGHT, 6)
        self.duration = wx.SpinCtrl(pnl, min=1, max=12, initial=1)
        h4.Add(self.duration)
        s.Add(h4, 0, wx.ALL, 10)

        # Buttons (fixed parent)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(pnl, wx.ID_OK, "OK")
        cancel_btn = wx.Button(pnl, wx.ID_CANCEL, "Cancel")
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(ok_btn, 0, wx.RIGHT, 10)
        btn_sizer.Add(cancel_btn, 0)

        s.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)

        pnl.SetSizer(s)

    def get_event(self):
        title = self.title_txt.GetValue()

        dt = self.date_picker.GetValue()
        date = datetime.date(dt.GetYear(), dt.GetMonth() + 1, dt.GetDay())

        start_hour = self.start_hour.GetValue()
        duration = self.duration.GetValue()

        start_time = datetime.time(start_hour, 0)
        end_time = (datetime.datetime.combine(date, start_time)
                    + datetime.timedelta(hours=duration)).time()

        return {
            "title": title,
            "date": date,
            "start": start_time,
            "end": end_time,
            "color_index": 0
        }
'''
'''# ============================================================
# StudyAura — Calendar View Tasks Screen (FINAL with Icon Week Nav)
# Paste PART 1, PART 2, PART 3 in order into modules/tasks_screen.py
# ============================================================

import wx
import wx.adv
import wx.lib.scrolledpanel as scrolled
import datetime

# ============================
# CONFIGURATION
# ============================
LEFT_PANEL_W = 220
HEADER_H = 100
DAY_BAR_H = 48

HOUR_START = 8
HOUR_END = 22
HOUR_HEIGHT = 72

GRID_COL_GAP = 12
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
]


# ============================
# SAMPLE EVENTS
# ============================
def sample_events(week_start):
    def add(day_offset, hour, title, dur=1, color=0):
        date = week_start + datetime.timedelta(days=day_offset)
        start = datetime.time(hour, 0)
        end_dt = datetime.datetime.combine(date, start) + datetime.timedelta(hours=dur)
        return {
            "title": title,
            "date": date,
            "start": start,
            "end": end_dt.time(),
            "color_index": color
        }

    return [
        add(1, 9, "Math Quiz", 1, 1),
        add(2, 13, "Physics Lab", 1, 0),
        add(2, 19, "Revision: Ch5", 1, 2),
        add(4, 15, "History Essay", 2, 1),
        add(6, 18, "Group Study", 1, 3),
        add(0, 10, "Chemistry Pract", 1, 0),
    ]


# ============================================================
# MAIN TASKS SCREEN
# ============================================================
class TasksScreen(wx.Panel):
    def __init__(self, parent, back_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.back_callback = back_callback

        self.SetBackgroundColour(BG)

        today = datetime.date.today()
        self.week_start = today - datetime.timedelta(days=today.weekday())

        self.events = sample_events(self.week_start)

        self.build_ui()
        wx.CallAfter(self.recalc_grid_size)

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
    # SIDEBAR
    # ======================================================
    def build_sidebar(self):
        p = wx.Panel(self, size=(LEFT_PANEL_W, -1))
        p.SetBackgroundColour(wx.Colour(24, 32, 44))

        s = wx.BoxSizer(wx.VERTICAL)

        logo = wx.StaticText(p, label="S")
        logo.SetFont(wx.Font(34, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        logo.SetForegroundColour(NEON)

        s.AddSpacer(20)
        s.Add(logo, 0, wx.LEFT, 20)
        s.AddSpacer(20)

        items = ["Home", "Today", "Upcoming", "Schedule", "Notes", "Tasks", "Assignments", "Exams", "Projects", "Resources"]

        for it in items:
            b = wx.Button(p, label=it, style=wx.BORDER_NONE)
            b.SetForegroundColour(TEXT_LIGHT)
            b.SetBackgroundColour(wx.Colour(0, 0, 0, 0))
            b.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            s.Add(b, 0, wx.LEFT | wx.TOP | wx.EXPAND, 15)

        s.AddStretchSpacer()
        s.Add(wx.StaticLine(p), 0, wx.EXPAND | wx.ALL, 10)

        settings = wx.Button(p, label="Settings", style=wx.BORDER_NONE)
        settings.SetForegroundColour(TEXT_LIGHT)
        settings.SetBackgroundColour(wx.Colour(0, 0, 0, 0))
        s.Add(settings, 0, wx.LEFT | wx.BOTTOM, 15)

        p.SetSizer(s)
        return p

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
    # HEADER (with Icon-style week nav buttons)
    # ======================================================
    def build_header(self, parent):
        p = wx.Panel(parent, size=(-1, HEADER_H))
        p.SetBackgroundColour(BG)

        s = wx.BoxSizer(wx.HORIZONTAL)

        # --- nav (icon buttons) + month label ---
        nav_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # icon-style buttons using glyphs
        prev_btn = wx.Button(p, label="◀", size=(44, 34), style=wx.BORDER_NONE)
        next_btn = wx.Button(p, label="▶", size=(44, 34), style=wx.BORDER_NONE)

        # make them look more "icon-like"
        btn_font = wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        prev_btn.SetFont(btn_font)
        next_btn.SetFont(btn_font)
        prev_btn.SetForegroundColour(TEXT_LIGHT)
        next_btn.SetForegroundColour(TEXT_LIGHT)
        prev_btn.SetBackgroundColour(wx.Colour(0, 0, 0, 0))
        next_btn.SetBackgroundColour(wx.Colour(0, 0, 0, 0))

        prev_btn.Bind(wx.EVT_BUTTON, self.on_prev_week)
        next_btn.Bind(wx.EVT_BUTTON, self.on_next_week)

        self.month_label = wx.StaticText(p, label=self.week_start.strftime("%B %Y"))
        self.month_label.SetFont(wx.Font(28, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.month_label.SetForegroundColour(TEXT_LIGHT)

        nav_sizer.Add(prev_btn, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 6)
        nav_sizer.Add(self.month_label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 6)
        nav_sizer.Add(next_btn, 0)

        s.Add(nav_sizer, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        s.AddStretchSpacer()

        self.toggle = wx.ToggleButton(p, label="Dark mode is on")
        self.toggle.SetValue(True)
        self.toggle.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle)
        s.Add(self.toggle, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 20)

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

        s = wx.BoxSizer(wx.HORIZONTAL)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        for d in days:
            lbl = wx.StaticText(p, label=d)
            lbl.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            lbl.SetForegroundColour(TEXT_LIGHT)
            s.Add(lbl, 1, wx.ALIGN_CENTER | wx.TOP, 10)

        p.SetSizer(s)
        return p

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

    # ======================================================
    def recalc_grid_size(self):
        total_hours = HOUR_END - HOUR_START
        height = total_hours * HOUR_HEIGHT + 40

        # Sunday visibility fix (extra padding)
        width = (140 + GRID_COL_GAP) * DAY_COL_COUNT + 200

        self.grid_panel.SetMinSize((width, height))
        self.grid_panel.GetParent().FitInside()
        self.grid_panel.Refresh()

    # ======================================================
    # GRID PAINT
    # ======================================================
    def on_paint_grid(self, evt):
        dc = wx.AutoBufferedPaintDC(self.grid_panel)

        dc.SetBackground(wx.Brush(BG))
        dc.Clear()

        w, h = self.grid_panel.GetSize()

        left_margin = 40
        top_margin = 10
        col_w = 140

        # Day columns
        for col in range(DAY_COL_COUNT):
            x = left_margin + col * (col_w + GRID_COL_GAP)
            dc.SetBrush(wx.Brush(wx.Colour(22, 28, 38)))
            dc.SetPen(wx.Pen(wx.Colour(44, 54, 68)))
            dc.DrawRoundedRectangle(x, top_margin, col_w, h - 20, 6)

            date = self.week_start + datetime.timedelta(days=col)

            dc.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            dc.SetTextForeground(TEXT_LIGHT)
            dc.DrawText(str(date.day), x + 10, top_margin + 5)

        # Hour lines
        for i in range(HOUR_END - HOUR_START + 1):
            y = top_margin + i * HOUR_HEIGHT

            dc.SetPen(wx.Pen(wx.Colour(34, 42, 54)))
            dc.DrawLine(left_margin, y, left_margin + (col_w + GRID_COL_GAP) * DAY_COL_COUNT, y)

            hour = HOUR_START + i
            label = f"{(hour - 1) % 12 + 1} {'AM' if hour < 12 else 'PM'}"

            dc.SetFont(wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            dc.SetTextForeground(wx.Colour(150, 160, 170))
            dc.DrawText(label, left_margin - 40, y - 6)

        # Draw events
        for ev in self.events:
            self.draw_event(dc, ev, col_w, left_margin, top_margin)

    # ======================================================
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

        color = EVENT_COLORS[ev["color_index"] % len(EVENT_COLORS)]

        dc.SetBrush(wx.Brush(color))
        dc.SetPen(wx.Pen(color))
        dc.DrawRoundedRectangle(x, y1 + 2, w, h - 4, 6)

        dc.SetTextForeground(wx.Colour(10, 10, 10))
        dc.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        dc.DrawText(ev["title"], x + 6, y1 + 8)

    # ======================================================
    # CLICK HANDLER
    # ======================================================
    def on_grid_click(self, evt):
        pos = evt.GetPosition()

        col_w = 140
        left_margin = 40
        top_margin = 10

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
                self.show_event(ev)
                return

    def show_event(self, ev):
        info = f"{ev['title']}\n\nDate: {ev['date']}\nStart: {ev['start']}\nEnd: {ev['end']}"
        dlg = wx.MessageDialog(self, info, "Event Details", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
    # ======================================================
    # NEW EVENT (Option B: Auto Switch Week)
    # ======================================================
    def on_new_event(self, evt):
        dlg = AddEventDialog(self, self.week_start + datetime.timedelta(days=1))

        if dlg.ShowModal() == wx.ID_OK:
            new_event = dlg.get_event()
            self.events.append(new_event)

            # Auto-switch to event's week
            event_date = new_event["date"]
            event_week_start = event_date - datetime.timedelta(days=event_date.weekday())

            if event_week_start != self.week_start:
                self.week_start = event_week_start
                self.month_label.SetLabel(self.week_start.strftime("%B %Y"))
                self.recalc_grid_size()

            self.grid_panel.Refresh()

        dlg.Destroy()

    # ======================================================
    # WEEK NAVIGATION HANDLERS
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
    def on_toggle(self, evt):
        if self.toggle.GetValue():
            self.toggle.SetLabel("Dark mode is on")
        else:
            self.toggle.SetLabel("Dark mode is off")

    # ======================================================
    def close(self):
        if self.back_callback:
            self.back_callback()


# ============================================================
# ADD EVENT DIALOG (fixed parent bug)
# ============================================================
class AddEventDialog(wx.Dialog):
    def __init__(self, parent, date):
        super().__init__(parent, title="Add Event", size=(420, 260))

        pnl = wx.Panel(self)
        s = wx.BoxSizer(wx.VERTICAL)

        # Title
        h1 = wx.BoxSizer(wx.HORIZONTAL)
        h1.Add(wx.StaticText(pnl, label="Title:"), 0, wx.RIGHT, 6)
        self.title_txt = wx.TextCtrl(pnl, value="New Event")
        h1.Add(self.title_txt, 1)
        s.Add(h1, 0, wx.ALL | wx.EXPAND, 10)

        # Date
        h2 = wx.BoxSizer(wx.HORIZONTAL)
        h2.Add(wx.StaticText(pnl, label="Date:"), 0, wx.RIGHT, 6)
        self.date_picker = wx.adv.DatePickerCtrl(pnl, style=wx.adv.DP_DROPDOWN)
        self.date_picker.SetValue(wx.DateTime.FromDMY(date.day, date.month - 1, date.year))
        h2.Add(self.date_picker, 1)
        s.Add(h2, 0, wx.ALL | wx.EXPAND, 10)

        # Start hour
        h3 = wx.BoxSizer(wx.HORIZONTAL)
        h3.Add(wx.StaticText(pnl, label="Start Hour:"), 0, wx.RIGHT, 6)
        self.start_hour = wx.SpinCtrl(pnl, min=0, max=23, initial=9)
        h3.Add(self.start_hour)
        s.Add(h3, 0, wx.ALL, 10)

        # Duration
        h4 = wx.BoxSizer(wx.HORIZONTAL)
        h4.Add(wx.StaticText(pnl, label="Duration (hrs):"), 0, wx.RIGHT, 6)
        self.duration = wx.SpinCtrl(pnl, min=1, max=12, initial=1)
        h4.Add(self.duration)
        s.Add(h4, 0, wx.ALL, 10)

        # Buttons (fixed parent)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(pnl, wx.ID_OK, "OK")
        cancel_btn = wx.Button(pnl, wx.ID_CANCEL, "Cancel")
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(ok_btn, 0, wx.RIGHT, 10)
        btn_sizer.Add(cancel_btn, 0)

        s.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)

        pnl.SetSizer(s)

    def get_event(self):
        title = self.title_txt.GetValue()

        dt = self.date_picker.GetValue()
        date = datetime.date(dt.GetYear(), dt.GetMonth() + 1, dt.GetDay())

        start_hour = self.start_hour.GetValue()
        duration = self.duration.GetValue()

        start_time = datetime.time(start_hour, 0)
        end_time = (datetime.datetime.combine(date, start_time)
                    + datetime.timedelta(hours=duration)).time()

        return {
            "title": title,
            "date": date,
            "start": start_time,
            "end": end_time,
            "color_index": 0
        }


# ============================================================
# Optional test harness (run module directly)
# ============================================================
if __name__ == "__main__":
    app = wx.App(False)
    f = wx.Frame(None, size=(1400, 800))
    t = TasksScreen(f)
    f.Show()
    app.MainLoop()
'''
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
            ("Tasks Completed", "TasksCompleted"),
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
