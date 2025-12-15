import wx
import math

class NeonButton(wx.Panel):
    def __init__(self, parent, label, bg_color, command):
        super().__init__(parent)
        self.SetBackgroundColour(bg_color)
        self.command = command
        self.SetMinSize((120, 50))

        sizer = wx.BoxSizer(wx.VERTICAL)
        font = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        
        self.lbl = wx.StaticText(self, label=label)
        self.lbl.SetFont(font)
        self.lbl.SetForegroundColour("BLACK")

        sizer.AddStretchSpacer()
        sizer.Add(self.lbl, 0, wx.ALIGN_CENTER)
        sizer.AddStretchSpacer()
        self.SetSizer(sizer)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.lbl.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.lbl.SetCursor(wx.Cursor(wx.CURSOR_HAND))

    def on_click(self, event):
        if self.command:
            self.command()


class PomodoroPage(wx.Panel):
    def __init__(self, parent, nav_callback=None, back_callback=None):
        super().__init__(parent)
        self.nav_callback = nav_callback
        self.back_callback = back_callback

        self.SetBackgroundColour("#050510")
        self.running = False
        self.time_left = 25 * 60
        self.total_time = 25 * 60
        self.is_break = False

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_tick, self.timer)

        self.create_ui()

    def create_ui(self):

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # -------------------------------------------------------
        # ⭐ ADD BACK BUTTON (TOP LEFT)
        # -------------------------------------------------------
        back_btn = wx.StaticText(self, label="⬅  Back")
        back_btn.SetFont(wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        back_btn.SetForegroundColour("#00F5FF")
        back_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        back_btn.Bind(wx.EVT_LEFT_DOWN, self.go_back)

        main_sizer.Add(back_btn, 0, wx.LEFT | wx.TOP, 20)
        # -------------------------------------------------------

        title = wx.StaticText(self, label="⏳ Pomodoro Timer")
        title.SetFont(wx.Font(32, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        title.SetForegroundColour("#00F5FF")
        main_sizer.Add(title, 0, wx.ALIGN_CENTER | wx.TOP, 10)

        self.canvas = wx.Panel(self, size=(320, 320))
        self.canvas.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)
        main_sizer.Add(self.canvas, 0, wx.ALIGN_CENTER | wx.TOP, 20)

        self.status_label = wx.StaticText(self, label="Focus Time")
        self.status_label.SetFont(wx.Font(20, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        self.status_label.SetForegroundColour("#A855F7")
        main_sizer.Add(self.status_label, 0, wx.ALIGN_CENTER | wx.TOP, 15)

        main_sizer.AddStretchSpacer(1)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.start_btn = NeonButton(self, "▶︎ Start", "#00F5FF", self.start_timer)
        self.reset_btn = NeonButton(self, "⏹ Reset", "#FF2E63", self.reset_timer)

        btn_sizer.Add(self.start_btn, 0, wx.RIGHT, 20)
        btn_sizer.Add(self.reset_btn, 0, wx.LEFT, 20)

        main_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 40)

        self.SetSizer(main_sizer)

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self.canvas)
        dc.SetBackground(wx.Brush("#050510"))
        dc.Clear()

        gc = wx.GraphicsContext.Create(dc)
        if gc:
            w, h = self.canvas.GetSize()
            cx, cy = w / 2, h / 2
            radius = 140

            gc.SetPen(wx.Pen(wx.Colour("#1F2933"), 18))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)

            progress = (self.total_time - self.time_left) / self.total_time
            if progress > 0:
                start_angle = -math.pi / 2
                sweep = 2 * math.pi * progress
                end_angle = start_angle + sweep

                color = "#22C55E" if self.is_break else "#00F5FF"
                gc.SetPen(wx.Pen(wx.Colour(color), 18))
                path = gc.CreatePath()
                path.AddArc(cx, cy, radius, start_angle, end_angle, True)
                gc.StrokePath(path)

            mins, secs = divmod(self.time_left, 60)
            time_str = f"{mins:02d}:{secs:02d}"

            font = wx.Font(42, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
            gc.SetFont(font, wx.Colour("#00F5FF"))
            tw, th = gc.GetTextExtent(time_str)
            gc.DrawText(time_str, cx - tw / 2, cy - th / 2)

    def start_timer(self):
        if not self.running:
            self.running = True
            self.timer.Start(1000)

    def reset_timer(self):
        self.running = False
        self.timer.Stop()
        self.is_break = False
        self.time_left = 25 * 60
        self.total_time = 25 * 60
        self.update_ui_state()
        self.canvas.Refresh()

    def on_tick(self, event):
        if self.time_left > 0:
            self.time_left -= 1
        else:
            self.switch_mode()
        self.canvas.Refresh()

    def switch_mode(self):
        self.running = False
        self.timer.Stop()

        if self.is_break:
            self.is_break = False
            self.time_left = 25 * 60
            self.total_time = 25 * 60
        else:
            self.is_break = True
            self.time_left = 5 * 60
            self.total_time = 5 * 60

        self.update_ui_state()

    def update_ui_state(self):
        if self.is_break:
            self.status_label.SetLabel("Break Time")
            self.status_label.SetForegroundColour("#22C55E")
        else:
            self.status_label.SetLabel("Focus Time")
            self.status_label.SetForegroundColour("#A855F7")

        self.Layout()

    # -------------------------------------------------------
    # ⭐ BACK BUTTON HANDLER
    # -------------------------------------------------------
    def go_back(self, event):
        if self.back_callback:
            self.back_callback()
