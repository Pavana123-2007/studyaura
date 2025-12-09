import wx
import wx.lib.scrolledpanel as scrolled
import csv
import math
import os

# ---------------- COLORS ----------------
BG = wx.Colour(18, 24, 34)
RING_BG = wx.Colour(40, 60, 70)
NEON = wx.Colour(0, 200, 255)
GLOW = wx.Colour(0, 200, 255)
TEXT = wx.Colour(220, 230, 240)


class SubjectProgressScreen(wx.Panel):

    def __init__(self, parent, nav_callback=None, back_callback=None):
        super().__init__(parent)

        self.nav_callback = nav_callback
        self.back_callback = back_callback

        self.SetBackgroundColour(BG)

        # ---------------- BACK BUTTON ----------------
        self.back_btn = wx.StaticText(self, label="← Back")
        self.back_btn.SetForegroundColour(wx.Colour(0, 200, 255))
        self.back_btn.SetFont(wx.Font(16, wx.FONTFAMILY_SWISS,
                                    wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        self.back_btn.SetPosition((30, 30))
        self.back_btn.Bind(wx.EVT_LEFT_DOWN, self.go_back)
        self.back_btn.Bind(wx.EVT_ENTER_WINDOW,
                           lambda e: self.back_btn.SetForegroundColour(wx.Colour(255, 255, 255)))
        self.back_btn.Bind(wx.EVT_LEAVE_WINDOW,
                           lambda e: self.back_btn.SetForegroundColour(wx.Colour(0, 200, 255)))

        # ---------------- SCROLL PANEL ----------------
        self.scroll = scrolled.ScrolledPanel(self, style=wx.SUNKEN_BORDER)
        self.scroll.SetupScrolling(scroll_x=False, scroll_y=True, rate_y=35)
        self.scroll.SetBackgroundColour(BG)

        self.inner = wx.Panel(self.scroll)
        self.inner.SetBackgroundColour(BG)
        self.inner.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        # Load percentages
        self.subject_progress = self.load_subject_percentages()

        # Bind painting to INNER panel (IMPORTANT FIX)
        self.inner.Bind(wx.EVT_PAINT, self.on_paint_inner)

        # Layout
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.inner, 1, wx.EXPAND)
        self.scroll.SetSizer(s)

        # Main layout
        main = wx.BoxSizer(wx.VERTICAL)
        main.Add(self.back_btn, 0, wx.LEFT | wx.TOP, 10)
        main.Add(self.scroll, 1, wx.EXPAND)
        self.SetSizer(main)

        # Refresh
        wx.CallAfter(self.refresh_inner_size)

    def refresh_inner_size(self):
        """Resize inner panel tall enough for all subjects."""
        count = len(self.subject_progress)
        rows = math.ceil(count / 3)
        height = 400 + (rows * 350)
        self.inner.SetMinSize((self.GetSize().width, height))
        self.inner.Layout()
        self.scroll.SetupScrolling()

    def go_back(self, event):
        if self.back_callback:
            self.back_callback()

    # ---------------------------------------------------------
    # CSV READING
    # ---------------------------------------------------------
    def load_subject_percentages(self):
        base = os.path.dirname(os.path.dirname(__file__))
        csv_path = os.path.join(base, "data", "tasks.csv")

        if not os.path.exists(csv_path):
            return {"No Data": 0}

        stats = {}

        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    title = row.get("title", "").strip()
                    completed = row.get("completed", "").strip().upper() == "TRUE"

                    if not title:
                        continue

                    if title not in stats:
                        stats[title] = {"done": 0, "total": 0}

                    stats[title]["total"] += 1
                    if completed:
                        stats[title]["done"] += 1

        except Exception as e:
            print("CSV read error:", e)
            return {"No Data": 0}

        output = {}
        for title, d in stats.items():
            pct = int((d["done"] / d["total"]) * 100) if d["total"] else 0
            output[title] = pct

        return output

    # ---------------------------------------------------------
    # DRAW RING
    # ---------------------------------------------------------
    def draw_neon_ring(self, dc, cx, cy, radius, pct, label):

        gc = wx.GraphicsContext.Create(dc)

        # BACK RING
        bg_pen = gc.CreatePen(wx.GraphicsPenInfo(RING_BG).Width(18).Cap(wx.CAP_ROUND))
        gc.SetPen(bg_pen)
        pbg = gc.CreatePath()
        pbg.AddCircle(cx, cy, radius)
        gc.StrokePath(pbg)

        # GLOW
        for i in range(4):
            alpha = 50 - i * 10
            col = wx.Colour(GLOW.Red(), GLOW.Green(), GLOW.Blue(), alpha)
            pen = gc.CreatePen(wx.GraphicsPenInfo(col).Width(26 + i * 4).Cap(wx.CAP_ROUND))
            gc.SetPen(pen)
            ph = gc.CreatePath()
            ph.AddCircle(cx, cy, radius)
            gc.StrokePath(ph)

        # ARC
        angle = (pct / 100.0) * 360
        start = -90
        arc_pen = gc.CreatePen(wx.GraphicsPenInfo(NEON).Width(12).Cap(wx.CAP_ROUND))
        gc.SetPen(arc_pen)

        pa = gc.CreatePath()
        pa.AddArc(cx, cy, radius, math.radians(start), math.radians(start + angle), False)
        gc.StrokePath(pa)

        # PERCENT
        dc.SetTextForeground(TEXT)
        dc.SetFont(wx.Font(22, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        t = f"{pct}%"
        tw, th = dc.GetTextExtent(t)
        dc.DrawText(t, cx - tw // 2, cy - th // 2)

        # LABEL
        dc.SetFont(wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        lw, lh = dc.GetTextExtent(label)
        dc.DrawText(label, cx - lw // 2, cy + radius + 20)

    # ---------------------------------------------------------
    # PAINT EVENT (draw inside scroll panel)
    # ---------------------------------------------------------
    def on_paint_inner(self, evt):
        dc = wx.AutoBufferedPaintDC(self.inner)
        dc.Clear()

        w, h = self.inner.GetSize()

        # TITLE
        dc.SetTextForeground(wx.Colour(180, 220, 255))
        dc.SetFont(wx.Font(36, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        dc.DrawText("📊 Subject-Wise Progress", 40, 30)

        items = list(self.subject_progress.items())
        n = len(items)

        columns = 3
        radius = 90
        spacing_x = w // (columns + 1)

        start_y = 180
        row_gap = 320

        positions = []
        for i in range(n):
            row = i // columns
            col = i % columns
            cx = spacing_x * (col + 1)
            cy = start_y + (row * row_gap)
            positions.append((cx, cy))

        for (subject, pct), (cx, cy) in zip(items, positions):
            self.draw_neon_ring(dc, cx, cy, radius, pct, subject)
