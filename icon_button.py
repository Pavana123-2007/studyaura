# ---------------------------------------------------------
# icon_button.py — Animated Icon Button for StudyAura
# Smooth Hover Animation (A2 pre-rendered frames)
# ---------------------------------------------------------

import wx
from PIL import Image

# --------------------------------------------------------------------
# Helper: Convert PIL Image → wx.Bitmap
# --------------------------------------------------------------------
def pil_to_wx_bitmap(pil_img):
    if pil_img.mode != "RGBA":
        pil_img = pil_img.convert("RGBA")

    w, h = pil_img.size
    wx_img = wx.Image(w, h)
    wx_img.SetData(pil_img.convert("RGB").tobytes())
    wx_img.SetAlpha(pil_img.split()[-1].tobytes())
    return wx.Bitmap(wx_img)


# --------------------------------------------------------------------
# Helper: Safe PIL loader
# --------------------------------------------------------------------
def load_pil_image(path, fallback_size=(150,150)):
    try:
        return Image.open(path).convert("RGBA")
    except:
        return Image.new("RGBA", fallback_size, (40,40,40,255))


# ---------------------------------------------------------
# CLASS: AnimatedIcon
# ---------------------------------------------------------
class AnimatedIcon(wx.Panel):
    """
    Smooth hover-animated dashboard icon:
      - Pre-rendered frames (A2)
      - Grows on hover
      - Shrinks on leave
      - Click event callback
    """

    def __init__(self, parent, name, pil_img,
                 base_size=(150,150), frames=10,
                 pos=(0,0), action=None):
        
        super().__init__(parent)
        self.name = name
        self.action = action

        self.hover = False
        base_w, base_h = base_size

        # -----------------------------------------------------
        # Pre-render frames: 100% → 115% (smooth scaling)
        # -----------------------------------------------------
        self.frames = []
        for i in range(frames):
            t = i / (frames - 1)
            scale = 1.0 + 0.15 * t
            w = int(base_w * scale)
            h = int(base_h * scale)
            scaled_img = pil_img.resize((w, h), Image.LANCZOS)
            self.frames.append(pil_to_wx_bitmap(scaled_img))

        self.frame_index = 0
        self.max_frame = frames - 1

        # -----------------------------------------------------
        # Panel Size — large enough for full-scale + label
        # -----------------------------------------------------
        self.SetSize((int(base_w*1.25), int(base_h*1.30)))
        self.SetPosition(pos)
        self.SetBackgroundColour(wx.BLACK)

        # -----------------------------------------------------
        # Icon Image
        # -----------------------------------------------------
        self.bmp = wx.StaticBitmap(self, bitmap=self.frames[0])
        self.center_bitmap(self.frames[0])

        # -----------------------------------------------------
        # Label
        # -----------------------------------------------------
        self.label = wx.StaticText(self, label=name)
        self.label.SetForegroundColour(wx.WHITE)
        self.label.SetFont(wx.Font(
            11,
            wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD
        ))

        # Center label under the icon
        self.label.SetPosition((
            (self.GetSize()[0]-self.label.GetSize()[0])//2,
            base_h + 8
        ))

        # -----------------------------------------------------
        # Timer for animation
        # -----------------------------------------------------
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

        # -----------------------------------------------------
        # Bind Events (Panel + Image + Label)
        # -----------------------------------------------------
        for obj in (self, self.bmp, self.label):
            obj.Bind(wx.EVT_ENTER_WINDOW, self.on_enter)
            obj.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
            obj.Bind(wx.EVT_LEFT_DOWN, self.on_click)

    # ---------------------------------------------------------
    # Event Handlers
    # ---------------------------------------------------------
    def on_enter(self, evt):
        self.hover = True
        if not self.timer.IsRunning():
            self.timer.Start(15)

    def on_leave(self, evt):
        self.hover = False
        if not self.timer.IsRunning():
            self.timer.Start(15)

    def on_click(self, evt):
        if callable(self.action):
            self.action(self.name)

    # ---------------------------------------------------------
    # Timer: Move animation forward/backward
    # ---------------------------------------------------------
    def on_timer(self, evt):
        if self.hover:
            if self.frame_index < self.max_frame:
                self.frame_index += 1
            else:
                self.timer.Stop()
        else:
            if self.frame_index > 0:
                self.frame_index -= 1
            else:
                self.timer.Stop()

        bmp = self.frames[self.frame_index]
        self.bmp.SetBitmap(bmp)
        self.center_bitmap(bmp)

    # ---------------------------------------------------------
    # Helper: Re-center bitmap on growth/shrink
    # ---------------------------------------------------------
    def center_bitmap(self, bmp):
        self.bmp.SetPosition((
            (self.GetSize()[0] - bmp.GetWidth())//2,
            0
        ))
