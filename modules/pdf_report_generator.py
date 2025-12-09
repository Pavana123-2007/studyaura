import wx
import math
import time 

# --- Configuration Constants ---
RING_RADIUS = 50
RING_WIDTH = 8
ANIMATION_DURATION = 2000 # 2 seconds in milliseconds
FPS = 30
TIMER_INTERVAL = 1000 // FPS # Timer event every ~33ms

# Define Enhanced Neon Colors
NEON_PURPLE = wx.Colour(220, 0, 255) # Max saturation/brightness
NEON_BLUE = wx.Colour(0, 180, 255)   # Max saturation/brightness
NEON_WHITE = wx.Colour(255, 255, 255) # Pure white for progress
SUCCESS_GREEN = wx.Colour(50, 255, 50) # Very bright success color
# -----------------------------

class AnimatedPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.BLACK)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        
        # Refinement 1: Enable Double Buffering to prevent flicker during redraws
        self.SetDoubleBuffered(True)
        
        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.start_time = 0
        self.progress_percent = 0
        self.is_complete = False

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.start_animation()

    def start_animation(self):
        self.start_time = int(time.time() * 1000)
        self.progress_percent = 0
        self.is_complete = False
        self.timer.Start(TIMER_INTERVAL)

    def on_timer(self, event):
        current_time = int(time.time() * 1000)
        elapsed_time = current_time - self.start_time

        if elapsed_time < ANIMATION_DURATION:
            self.progress_percent = min(100, int((elapsed_time / ANIMATION_DURATION) * 100))
        else:
            self.progress_percent = 100
            self.timer.Stop()
            self.is_complete = True 
            wx.CallLater(1500, self.GetParent().Close)

        self.Refresh()

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        
        width, height = self.GetSize() 
        center_x = width // 2
        center_y = height // 2
        
        if self.is_complete:
            self.draw_checkmark(dc, center_x, center_y)
        else:
            self.draw_progress_ring(dc, center_x, center_y)

    def draw_progress_ring(self, dc, cx, cy):
        gc = wx.GraphicsContext.Create(dc)
        gc.SetAntialiasMode(wx.ANTIALIAS_DEFAULT) 
        
        # --- Neon Effect Drawing (Simulating Glow) ---

        # 1. Draw a dark base ring 
        gc.SetPen(wx.Pen(wx.Colour(50, 50, 50), RING_WIDTH + 2))
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.DrawEllipse(cx - (RING_RADIUS + 5), cy - (RING_RADIUS + 5), 
                       (RING_RADIUS + 5) * 2, (RING_RADIUS + 5) * 2)

        # 2. Draw the two 'Neon' color rings slightly offset and thin
        
        # Neon Blue Ring (Outer glow layer)
        gc.SetPen(wx.Pen(NEON_BLUE, 2))
        gc.DrawEllipse(cx - (RING_RADIUS + 8), cy - (RING_RADIUS + 8), 
                       (RING_RADIUS + 8) * 2, (RING_RADIUS + 8) * 2)

        # Neon Purple Ring (Inner glow layer)
        gc.SetPen(wx.Pen(NEON_PURPLE, 1))
        gc.DrawEllipse(cx - (RING_RADIUS + 6), cy - (RING_RADIUS + 6), 
                       (RING_RADIUS + 6) * 2, (RING_RADIUS + 6) * 2)
        
        # --- Progress Arc Drawing ---

        progress_angle = (self.progress_percent / 100) * 360
        start_angle_rad = math.radians(90)
        end_angle_rad = math.radians(90 - progress_angle) 

        gc.SetPen(wx.Pen(NEON_WHITE, RING_WIDTH)) # Use NEON_WHITE for progress
        
        path = gc.CreatePath()
        path.AddArc(
            cx, cy, RING_RADIUS,
            start_angle_rad, end_angle_rad,
            True 
        )
        gc.StrokePath(path)

        # 3. Draw the percentage text in the center
        font = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
        dc.SetTextForeground(NEON_WHITE) # Use NEON_WHITE for text
        text = str(self.progress_percent)
        tw, th = dc.GetTextExtent(text)
        
        dc.DrawText(text, cx - tw // 2, cy - th // 2)


    def draw_checkmark(self, dc, cx, cy):
        # 1. Draw the success circle
        gc = wx.GraphicsContext.Create(dc)
        gc.SetAntialiasMode(wx.ANTIALIAS_DEFAULT) 
        
        # Draw a slightly glowing success circle
        gc.SetPen(wx.Pen(SUCCESS_GREEN, 4))
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.DrawEllipse(cx - RING_RADIUS, cy - RING_RADIUS, RING_RADIUS * 2, RING_RADIUS * 2)

        # 2. Draw the checkmark inside
        gc.SetPen(wx.Pen(NEON_WHITE, 6)) # Draw checkmark in bright white for contrast
        
        # Refinement 3: Slightly smaller scale for checkmark
        scale = RING_RADIUS * 0.5 
        p1 = (cx - scale * 0.4, cy)               
        p2 = (cx - scale * 0.4 + scale * 0.4, cy + scale * 0.4) 
        p3 = (cx - scale * 0.4 + scale * 1.0, cy - scale * 0.4) 

        path = gc.CreatePath()
        path.MoveToPoint(p1[0], p1[1])
        path.AddLineToPoint(p2[0], p2[1])
        path.AddLineToPoint(p3[0], p3[1])
        gc.StrokePath(path)


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="wxPython Progress Animation", size=(400, 400),
                          style=wx.CAPTION | wx.SYSTEM_MENU | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        
        # Crucial step: Ensure the frame's background is also black
        self.SetBackgroundColour(wx.BLACK) 
        
        self.panel = AnimatedPanel(self)
        self.Center()
        self.Show()


if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()