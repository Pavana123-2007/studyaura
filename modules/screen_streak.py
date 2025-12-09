import wx

BG = wx.Colour(18, 24, 34)
FIRE = wx.Colour(255, 140, 80)

class StudyStreakScreen(wx.Panel):
    def __init__(self, parent, nav_callback=None, back_callback=None):
        super().__init__(parent)

        self.SetBackgroundColour(BG)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.current = 7
        self.best = 15

        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_paint(self, evt):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()

        dc.SetFont(wx.Font(32, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_BOLD))
        dc.SetTextForeground(FIRE)
        dc.DrawText("🔥 Study Streak", 60, 50)

        bar_w = 700
        fill = int(bar_w * (self.current / self.best))

        # background bar
        dc.SetBrush(wx.Brush(wx.Colour(40, 55, 70)))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRoundedRectangle(80, 160, bar_w, 45, 10)

        # streak bar
        dc.SetBrush(wx.Brush(FIRE))
        dc.DrawRoundedRectangle(80, 160, fill, 45, 10)

        dc.SetFont(wx.Font(18, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_NORMAL))
        dc.SetTextForeground(wx.Colour(230, 230, 240))
        dc.DrawText(f"Current Streak: {self.current} days", 80, 230)
        dc.DrawText(f"Best Streak: {self.best} days", 80, 270)
