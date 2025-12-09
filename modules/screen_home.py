import wx

BG = wx.Colour(18, 24, 34)
TITLE = wx.Colour(180, 220, 255)

class HomeScreen(wx.Panel):
    def __init__(self, parent, nav_callback=None, back_callback=None):
        super().__init__(parent)

        self.SetBackgroundColour(BG)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.nav_callback = nav_callback
        self.back_callback = back_callback

        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_paint(self, evt):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()

        dc.SetTextForeground(TITLE)
        dc.SetFont(wx.Font(42, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_BOLD))
        dc.DrawText("🏠 Welcome to StudyAura", 60, 60)

        dc.SetFont(wx.Font(18, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_NORMAL))
        dc.SetTextForeground(wx.Colour(230, 235, 240))
        dc.DrawText("Your personal study companion.", 60, 130)
