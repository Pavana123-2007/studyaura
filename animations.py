import wx


class TextAnimator:
    """Simple slide-in text animator."""

    def __init__(
        self,
        widget: wx.StaticText,
        start_pos,
        end_pos,
        duration_ms=600,
        interval_ms=15,
    ):
        self.widget = widget
        self.start_x, self.start_y = start_pos
        self.end_x, self.end_y = end_pos

        self.widget.Move(self.start_x, self.start_y)

        self.duration_ms = max(1, duration_ms)
        self.interval_ms = max(1, interval_ms)

        self.steps = max(1, self.duration_ms // self.interval_ms)
        self.current_step = 0

        self.dx = (self.end_x - self.start_x) / float(self.steps)
        self.dy = (self.end_y - self.start_y) / float(self.steps)

        parent = widget.GetParent()
        self.timer = wx.Timer(parent)
        parent.Bind(wx.EVT_TIMER, self._on_timer, self.timer)

    def start(self):
        self.current_step = 0
        self.widget.Move(self.start_x, self.start_y)
        self.timer.Start(self.interval_ms)

    def _on_timer(self, event):
        if event.GetTimer() is not self.timer:
            # Ignore other timers
            event.Skip()
            return

        if self.current_step >= self.steps:
            self.widget.Move(self.end_x, self.end_y)
            self.timer.Stop()
            return

        new_x = self.start_x + self.dx * self.current_step
        new_y = self.start_y + self.dy * self.current_step
        self.widget.Move(int(new_x), int(new_y))

        self.current_step += 1


class PageTransition:
    """Panel-based slide transition (covers screen right→left→off)."""

    def __init__(self, parent_panel: wx.Panel, size):
        self.parent = parent_panel
        self.width, self.height = size

        self.panel = wx.Panel(parent_panel, size=size)
        self.panel.SetBackgroundColour(wx.BLACK)
        self.panel.Hide()

        self.state = "idle"
        self.callback = None

        self.x = self.width
        self.speed = 40  # pixels per frame

        self.timer = wx.Timer(parent_panel)
        parent_panel.Bind(wx.EVT_TIMER, self._on_timer, self.timer)

    def start(self, callback):
        """Start transition and call callback in the middle."""
        if self.state != "idle":
            return

        self.callback = callback
        self.state = "enter"
        self.x = self.width  # start just outside right
        self.panel.SetPosition((self.x, 0))
        self.panel.Show()
        self.timer.Start(16)

    def _on_timer(self, event):
        if event.GetTimer() is not self.timer:
            event.Skip()
            return

        if self.state == "enter":
            self.x -= self.speed
            if self.x <= 0:
                self.x = 0
                self.panel.SetPosition((self.x, 0))
                # Call the provided callback once fully covered
                if callable(self.callback):
                    self.callback()
                self.state = "exit"
            else:
                self.panel.SetPosition((self.x, 0))

        elif self.state == "exit":
            self.x -= self.speed
            if self.x <= -self.width:
                self.x = -self.width
                self.panel.Hide()
                self.timer.Stop()
                self.state = "idle"
                self.callback = None
            else:
                self.panel.SetPosition((self.x, 0))
