# modules/neon_base_wx.py
"""
Neon helpers for wxPython screens.
Produces a centered neon panel PNG using Pillow and provides NeonScreen base class.
"""

import io, os
from PIL import Image, ImageDraw, ImageFilter
import wx

# Theme
DARK_BG = "#0e1125"
PANEL_RATIO = (0.62, 0.78)  # panel width ratio, panel height ratio
CACHE = {}

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0,2,4))

def make_neon_panel_pil(width, height, neon_hex="#00C8FF", radius=28, glow=36):
    key = (width, height, neon_hex, radius, glow)
    if key in CACHE:
        return CACHE[key].copy()

    base = Image.new("RGBA", (width, height), (14,17,37,255))
    panel_w = int(width * PANEL_RATIO[0])
    panel_h = int(height * PANEL_RATIO[1])
    panel_x = int((width - panel_w) * 0.1)
    panel_y = int(height * 0.12)

    # panel
    panel = Image.new("RGBA", (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(panel)
    draw.rounded_rectangle([panel_x, panel_y, panel_x+panel_w, panel_y+panel_h], radius, fill=(18,20,30,230))

    # glow layer
    glow_layer = Image.new("RGBA", (width, height), (0,0,0,0))
    gd = ImageDraw.Draw(glow_layer)
    rgb = hex_to_rgb(neon_hex)
    for i in range(int(glow/2), glow, 2):
        alpha = int(max(6, 110 * (1 - i / (glow+2))))
        bbox = [panel_x - i, panel_y - i, panel_x + panel_w + i, panel_y + panel_h + i]
        gd.rounded_rectangle(bbox, radius + i, outline=(rgb[0], rgb[1], rgb[2], alpha), width=2)
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=glow/2))

    highlight = Image.new("RGBA", (width, height), (0,0,0,0))
    hd = ImageDraw.Draw(highlight)
    hd.rounded_rectangle([panel_x+6, panel_y+6, panel_x+panel_w-6, panel_y+panel_h-6], radius-6, fill=(255,255,255,12))

    composed = Image.alpha_composite(base, glow_layer)
    composed = Image.alpha_composite(composed, panel)
    composed = Image.alpha_composite(composed, highlight)

    CACHE[key] = composed.copy()
    return composed

def pil_to_wx_bitmap(pil_img):
    with io.BytesIO() as b:
        pil_img.save(b, format="PNG")
        b.seek(0)
        wx_img = wx.Image(b)
        return wx.Bitmap(wx_img)

class NeonScreen(wx.Panel):
    """
    Base neon screen panel. Draws neon panel background and exposes `content` panel inside.
    Use by subclassing or creating an instance and populating `self.content`.
    """

    def __init__(self, parent, neon_color="#00C8FF"):
        super().__init__(parent, style=wx.BORDER_NONE)
        self.neon_color = neon_color
        self.SetBackgroundColour(wx.Colour(DARK_BG))

        self.canvas = wx.StaticBitmap(self)
        self.content = wx.Panel(self)
        self.content.SetBackgroundColour(wx.Colour(0,0,0,0))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        self.sizer.Add(self.content, 0, wx.EXPAND)  # content will be positioned manually on size
        self.SetSizer(self.sizer)

        self.Bind(wx.EVT_SIZE, self.on_size)
        self._current_bitmap = None

    def on_size(self, evt):
        w, h = self.GetClientSize()
        if w <= 0 or h <= 0:
            return
        pil = make_neon_panel_pil(w, h, self.neon_color)
        bmp = pil_to_wx_bitmap(pil)
        self.canvas.SetBitmap(bmp)
        # compute panel geometry like base generator
        panel_w = int(w * PANEL_RATIO[0])
        panel_h = int(h * PANEL_RATIO[1])
        panel_x = int((w - panel_w) * 0.1)
        panel_y = int(h * 0.12)
        # place content inside the panel with padding
        pad = 22
        cx, cy, cw, ch = panel_x + pad, panel_y + pad, panel_w - pad*2, panel_h - pad*2
        self.content.SetPosition((cx, cy))
        self.content.SetSize((cw, ch))
        self.Layout()
        if evt:
            evt.Skip()
