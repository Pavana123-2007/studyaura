import wx
import os
import csv
import calendar
from datetime import date, datetime

# ---------------- COLORS ----------------
BG = wx.Colour(18, 24, 34)
LOW = wx.Colour(40, 60, 70)
MED = wx.Colour(80, 150, 200)
HIGH = wx.Colour(120, 220, 255)
TEXT = wx.Colour(200, 220, 255)

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class StudyHeatmapScreen(wx.Panel):
    """
    Month-wise Heatmap (Mon–Sun horizontally, weeks vertically)
    Features:
    - Title + Month Navigation (layout-based, no overlap!)
    - Real task-based heatmap from tasks.csv
    - Perfect responsive sizing (never exceeds screen)
    - Clean StudyAura styling
    """

    def __init__(self, parent, nav_callback=None, back_callback=None):
        super().__init__(parent)

        self.SetBackgroundColour(BG)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        # -----------------------------------------------------
        # BACK BUTTON (Top-left)
        # -----------------------------------------------------
        self.back_callback = back_callback

        self.back_btn = wx.StaticText(self, label="← Back")
        self.back_btn.SetForegroundColour(wx.Colour(120, 220, 255))
        self.back_btn.SetFont(wx.Font(
            16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        ))
        self.back_btn.SetPosition((20, 15))

        # Hover effects
        self.back_btn.Bind(wx.EVT_ENTER_WINDOW,
                        lambda e: self.back_btn.SetForegroundColour(wx.Colour(255, 255, 255)))
        self.back_btn.Bind(wx.EVT_LEAVE_WINDOW,
                        lambda e: self.back_btn.SetForegroundColour(wx.Colour(120, 220, 255)))

        # Click → Go Back
        self.back_btn.Bind(wx.EVT_LEFT_DOWN, self.go_back)


        today = date.today()
        self.view_year = today.year
        self.view_month = today.month

        self.day_counts = {}
        self.grid_map = []

        # UI SETUP
        self._setup_ui()
        self._bind_events()

        self.load_all_task_counts()
        self.Refresh()


    # -----------------------------------------------------
    # UI SETUP (FIXED TITLE + NAV PANEL)
    # -----------------------------------------------------
    def _setup_ui(self):

        # ---------- TITLE ----------
        self.lbl_title = wx.StaticText(self, label="🔥 Study Heatmap — Month View")
        self.lbl_title.SetForegroundColour(TEXT)
        self.lbl_title.SetFont(wx.Font(
            24, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        ))

        # ---------- NAVIGATION PANEL ----------
        nav_panel = wx.Panel(self)
        nav_panel.SetBackgroundColour(BG)

        self.btn_prev = wx.Button(nav_panel, label="<")
        self.lbl_month = wx.StaticText(nav_panel, label="")
        self.btn_next = wx.Button(nav_panel, label=">")

        self.lbl_month.SetForegroundColour(TEXT)
        self.lbl_month.SetFont(wx.Font(
            18, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        ))

        nav_sizer = wx.BoxSizer(wx.HORIZONTAL)
        nav_sizer.Add(self.btn_prev, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 25)
        nav_sizer.AddStretchSpacer(1)
        nav_sizer.Add(self.lbl_month, 0, wx.ALIGN_CENTER_VERTICAL)
        nav_sizer.AddStretchSpacer(1)
        nav_sizer.Add(self.btn_next, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 25)

        nav_panel.SetSizer(nav_sizer)

        # ---------- MAIN LAYOUT ----------
        main = wx.BoxSizer(wx.VERTICAL)
        main.Add(self.lbl_title, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
        main.Add(nav_panel, 0, wx.EXPAND | wx.BOTTOM, 10)
        main.AddStretchSpacer(1)

        self.SetSizer(main)


    # -----------------------------------------------------
    # EVENTS
    # -----------------------------------------------------
    def _bind_events(self):
        self.btn_prev.Bind(wx.EVT_BUTTON, lambda e: self.change_month(-1))
        self.btn_next.Bind(wx.EVT_BUTTON, lambda e: self.change_month(1))

        self.Bind(wx.EVT_SIZE, lambda e: (self.Refresh(), e.Skip()))
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.Bind(wx.EVT_SHOW, self.on_show)

        # -----------------------------------------------------
        # BACK NAVIGATION
        # -----------------------------------------------------
    def go_back(self, event):
        if self.back_callback:
            self.back_callback()   # Return to tasks_screen.py


    # -----------------------------------------------------
    # CSV LOADING
    # -----------------------------------------------------
    def tasks_csv_path(self):
        base = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(base, "data", "tasks.csv")

    def load_all_task_counts(self):
        self.day_counts.clear()
        path = self.tasks_csv_path()

        if not os.path.exists(path):
            return

        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    dt = None
                    for key in ("date", "Date", "day"):
                        if key in row and row[key].strip():
                            s = row[key].strip()
                            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
                                try:
                                    dt = datetime.strptime(s, fmt).date()
                                    break
                                except:
                                    continue
                            break

                    if dt:
                        k = (dt.year, dt.month, dt.day)
                        self.day_counts[k] = self.day_counts.get(k, 0) + 1

        except Exception as e:
            print("Heatmap CSV Error:", e)


    # -----------------------------------------------------
    # MONTH NAVIGATION
    # -----------------------------------------------------
    def change_month(self, delta):
        m = self.view_month + delta
        y = self.view_year

        if m < 1:
            m = 12
            y -= 1
        elif m > 12:
            m = 1
            y += 1

        self.view_month = m
        self.view_year = y

        self.load_all_task_counts()
        self.Refresh()

    def on_show(self, evt):
        if evt.IsShown():
            self.load_all_task_counts()
            self.Refresh()
        evt.Skip()


    # -----------------------------------------------------
    # PAINT — DRAW HEATMAP
    # -----------------------------------------------------
    def on_paint(self, evt):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
            # Ensure Back button updates on repaint
        self.back_btn.Refresh()

        w, h = self.GetSize()

        # Month header text (set in UI)
        month_name = calendar.month_name[self.view_month]
        self.lbl_month.SetLabel(f"{month_name} {self.view_year}")

        # Compute month layout
        first_wd, days_in_month = calendar.monthrange(self.view_year, self.view_month)
        dates = [date(self.view_year, self.view_month, d) for d in range(1, days_in_month + 1)]

        cols = 7
        rows = (first_wd + days_in_month + 6) // 7

        header_height = 140  # space under title + nav panel

        # ------------------ RESPONSIVE GRID SIZING ------------------
        available_width = w * 0.85
        available_height = h - header_height - 120

        width_per_col = available_width // cols
        height_per_row = available_height // rows

        cell_size = int(min(width_per_col, height_per_row))
        cell_size = max(35, min(cell_size, 120))

        gap = max(4, int(cell_size * 0.15))
        # -------------------------------------------------------------

        total_width = cols * (cell_size + gap)
        x0 = int((w - total_width) // 2)
        y0 = header_height

        # Draw day labels
        dc.SetFont(wx.Font(13, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_BOLD))
        dc.SetTextForeground(TEXT)

        for c, day in enumerate(DAYS):
            dc.DrawText(day, x0 + c * (cell_size + gap) + 5, y0 - 25)

        # Count tasks
        month_counts = [self.day_counts.get((d.year, d.month, d.day), 0) for d in dates]
        max_count = max(month_counts) if month_counts else 0

        def get_color(count):
            if max_count == 0:
                return LOW
            if count == 0:
                return LOW
            threshold = max(1, int(max_count * 0.4))
            return MED if count <= threshold else HIGH

        self.grid_map = []
        pos = first_wd

        # Draw heatmap squares
        for d in dates:
            col = pos % 7
            row = pos // 7

            x = x0 + col * (cell_size + gap)
            y = y0 + row * (cell_size + gap)

            cnt = self.day_counts.get((d.year, d.month, d.day), 0)
            color = get_color(cnt)

            dc.SetBrush(wx.Brush(color))
            dc.SetPen(wx.Pen(color))
            dc.DrawRectangle(x, y, cell_size, cell_size)

            dc.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_NORMAL))
            dc.SetTextForeground(TEXT)
            dc.DrawText(str(d.day), x + 4, y + 4)

            self.grid_map.append((wx.Rect(x, y, cell_size, cell_size), d))
            pos += 1

        # Legend
        legend_x = x0 + total_width + 30
        ly = y0

        dc.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_NORMAL))
        dc.DrawText("Legend:", legend_x, ly)
        ly += 24

        for label, col in [("0 tasks", LOW), ("1..mid tasks", MED), ("> mid tasks", HIGH)]:
            dc.SetBrush(wx.Brush(col))
            dc.SetPen(wx.Pen(col))
            dc.DrawRectangle(legend_x, ly, 18, 18)
            dc.DrawText(label, legend_x + 28, ly)
            ly += 28


    # -----------------------------------------------------
    # CLICK EVENT
    # -----------------------------------------------------
    def on_click(self, evt):
        pt = evt.GetPosition()

        for rect, d in self.grid_map:
            if rect.Contains(pt):
                cnt = self.day_counts.get((d.year, d.month, d.day), 0)
                wx.MessageBox(
                    f"{d.strftime('%A, %d %B %Y')}\nTasks scheduled: {cnt}",
                    "Day Details"
                )
                return
