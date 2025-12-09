'''# ================================================================
#                       StudyAura — FINAL MAIN
#            wxPython version (transparent title + hover icons)
# ================================================================

import wx
import os
from PIL import Image

# Import animated icon class
from icon_button import AnimatedIcon, load_pil_image, pil_to_wx_bitmap
from modules.tasks_screen import TasksScreen

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------
BASE_PATH = os.path.dirname(__file__)
ICON_FOLDER = os.path.join(BASE_PATH, "assets", "icons")

ASSETS = {
    "background": "background.png",
    "Tasks": "tasks_icon.png",
    "Timetable": "timetable_icon.png",
    "Analytics": "analytics_icon.png",
    "Reports": "reports_icon.png",
    "Pomodoro": "pomodoro_icon.png",
    "Settings": "settings_icon.png"
}

DESIGN_W, DESIGN_H = 1550, 800
ICON_SIZE = (150, 150)


# ============================================================
# TRANSPARENT TITLE OVERLAY
# ============================================================
class TitleCanvas(wx.Window):
    def __init__(self, parent, pos=(0, 0), size=(900, 420)):
        super().__init__(
            parent, pos=pos, size=size,
            style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.TRANSPARENT_WINDOW
        )

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)

        self.alpha = 0.0
        self.offset_y = 40
        self.frame = 0
        self.max_frames = 35

        self.title_lines = ["     StudyAura:", "     Turn Plans", "   into Progress!"]
        self.subtitle = (
            "📘 Plan Smart   |   💪 Stay Consistent   |   🚀 Achieve Excellence"
        )

        self.title_font = wx.Font(
            50, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        )
        self.sub_font = wx.Font(
            15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        )

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

    def start(self, delay=50):
        wx.CallLater(delay, lambda: self.timer.Start(16))

    def on_timer(self, evt):
        self.frame += 1
        t = min(1.0, self.frame / self.max_frames)
        ease = 1 - (1 - t) ** 3

        self.alpha = ease
        self.offset_y = int(50 * (1 - ease))
        self.Refresh(False)

        if t >= 1.0:
            self.timer.Stop()

    def on_paint(self, evt):
        pdc = wx.AutoBufferedPaintDC(self)

        w, h = self.GetSize()
        bmp = wx.Bitmap(w, h, 32)
        mdc = wx.MemoryDC(bmp)

        mdc.SetBackground(wx.Brush(wx.Colour(0, 0, 0, 0)))
        mdc.Clear()

        gc = wx.GraphicsContext.Create(mdc)
        col = wx.Colour(255, 255, 255, int(self.alpha * 255))

        gc.SetFont(self.title_font, col)

        x = 40
        y = 10 + self.offset_y
        lh = self.title_font.GetPixelSize().y + 6

        for i, line in enumerate(self.title_lines):
            gc.DrawText(line, x, y + i * lh)

        gc.SetFont(self.sub_font, col)
        gc.DrawText(
            self.subtitle,
            x,
            y + len(self.title_lines) * lh + 25
        )

        mdc.SelectObject(wx.NullBitmap)
        pdc.DrawBitmap(bmp, 0, 0, True)


# ============================================================
# MAIN APPLICATION FRAME
# ============================================================
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(
            None,
            title="StudyAura",
            size=(DESIGN_W, DESIGN_H)
        )

        self.Centre()
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.on_paint_frame)

        # ----------------------------------------------------
        # Background
        # ----------------------------------------------------
        bg_path = os.path.join(ICON_FOLDER, ASSETS["background"])
        pil_bg = load_pil_image(bg_path, fallback_size=(DESIGN_W, DESIGN_H))
        pil_bg = pil_bg.resize((DESIGN_W, DESIGN_H), Image.LANCZOS)
        self._bg_bitmap = pil_to_wx_bitmap(pil_bg)

        # ----------------------------------------------------
        # Title Overlay
        # ----------------------------------------------------
        self.title = TitleCanvas(self, pos=(0, 200), size=(690, 300))
        self.title.Raise()
        self.title.start()

        # ----------------------------------------------------
        # Icons Row
        # ----------------------------------------------------
        names = ["Tasks", "Timetable", "Analytics",
                 "Reports", "Pomodoro", "Settings"]

        xpos = [50, 300, 560, 800, 1050, 1300]
        ypos = 550

        self.icons = []
        for i, name in enumerate(names):
            icon_path = os.path.join(ICON_FOLDER, ASSETS[name])
            pil_icon = load_pil_image(icon_path, fallback_size=ICON_SIZE)

            widget = AnimatedIcon(
                parent=self,
                name=name,
                pil_img=pil_icon,
                base_size=ICON_SIZE,
                frames=12,
                pos=(xpos[i], ypos),
                action=self.on_icon_click
            )
            widget.Raise()
            self.icons.append(widget)

        self.Show()

    # ---------------------------------------------------------
    # Paint background
    # ---------------------------------------------------------
    def on_paint_frame(self, evt):
        dc = wx.AutoBufferedPaintDC(self)
        dc.DrawBitmap(self._bg_bitmap, 0, 0, True)

    # ---------------------------------------------------------
    # Icon click handler
    # ---------------------------------------------------------
    def on_icon_click(self, name):
        if name == "Tasks":
            self.switch_to_tasks()
        else:
            wx.MessageBox(f"You clicked: {name}", "StudyAura")

    # ---------------------------------------------------------
    # Sidebar navigation handler
    # ---------------------------------------------------------
    def on_sidebar_nav(self, label):
        if label == "Home":
            self.switch_to_home()
            return

        if label == "Tasks":
            self.switch_to_tasks()
            return

        wx.MessageBox(f"You clicked: {label}", "Navigation")

    # ---------------------------------------------------------
    # Switch to TASKS screen
    # ---------------------------------------------------------
    def switch_to_tasks(self):
        self.title.Hide()
        for icon in self.icons:
            icon.Hide()

        self.tasks_screen = TasksScreen(
            parent=self,
            nav_callback=self.on_sidebar_nav,      # FIXED
            back_callback=self.switch_to_home      # FIXED
        )

        self.tasks_screen.SetPosition((0, 0))
        self.tasks_screen.SetSize((DESIGN_W, DESIGN_H))
        self.tasks_screen.Show()

    # ---------------------------------------------------------
    # Switch back to HOME screen
    # ---------------------------------------------------------
    def switch_to_home(self):
        # destroy task screen if it exists
        if hasattr(self, "tasks_screen"):
            self.tasks_screen.Hide()
            self.tasks_screen.Destroy()

        self.title.Show()
        for icon in self.icons:
            icon.Show()

        self.Refresh()


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
'''
'''# ================================================================
#                       StudyAura — FINAL MAIN
#            wxPython version (transparent title + hover icons)
# ================================================================

import wx
import os
from PIL import Image

from icon_button import AnimatedIcon, load_pil_image, pil_to_wx_bitmap
from modules.tasks_screen import TasksScreen
from modules.screen_home import HomeScreen
from modules.screen_subject_progress import SubjectProgressScreen
from modules.screen_daily_progress import DailyProgressScreen
from modules.screen_heatmap import StudyHeatmapScreen
from modules.screen_tasks_completed import TasksCompletedScreen
from modules.screen_streak import StudyStreakScreen



BASE_PATH = os.path.dirname(__file__)
ICON_FOLDER = os.path.join(BASE_PATH, "assets", "icons")

ASSETS = {
    "background": "background.png",
    "Tasks": "tasks_icon.png",
    "Timetable": "timetable_icon.png",
    "Analytics": "analytics_icon.png",
    "Reports": "reports_icon.png",
    "Pomodoro": "pomodoro_icon.png"
    # Removed: "Settings": "settings_icon.png"
}

DESIGN_W, DESIGN_H = 1550, 800
ICON_SIZE = (150, 150)


# ============================================================
# TRANSPARENT TITLE OVERLAY
# ============================================================
class TitleCanvas(wx.Window):
    def __init__(self, parent, pos=(0, 0), size=(900, 420)):
        super().__init__(
            parent, pos=pos, size=size,
            style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.TRANSPARENT_WINDOW
        )

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)

        self.alpha = 0.0
        self.offset_y = 40
        self.frame = 0
        self.max_frames = 35

        self.title_lines = ["     StudyAura:", "     Turn Plans", "   into Progress!"]
        self.subtitle = (
            "📘 Plan Smart   |   💪 Stay Consistent   |   🚀 Achieve Excellence"
        )

        self.title_font = wx.Font(
            50, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        )
        self.sub_font = wx.Font(
            15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        )

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

    def start(self, delay=50):
        wx.CallLater(delay, lambda: self.timer.Start(16))

    def on_timer(self, evt):
        self.frame += 1
        t = min(1.0, self.frame / self.max_frames)
        ease = 1 - (1 - t) ** 3

        self.alpha = ease
        self.offset_y = int(50 * (1 - ease))
        self.Refresh(False)

        if t >= 1.0:
            self.timer.Stop()

    def on_paint(self, evt):
        pdc = wx.AutoBufferedPaintDC(self)

        w, h = self.GetSize()
        bmp = wx.Bitmap(w, h, 32)
        mdc = wx.MemoryDC(bmp)

        mdc.SetBackground(wx.Brush(wx.Colour(0, 0, 0, 0)))
        mdc.Clear()

        gc = wx.GraphicsContext.Create(mdc)
        col = wx.Colour(255, 255, 255, int(self.alpha * 255))

        gc.SetFont(self.title_font, col)

        x = 40
        y = 10 + self.offset_y
        lh = self.title_font.GetPixelSize().y + 6

        for i, line in enumerate(self.title_lines):
            gc.DrawText(line, x, y + i * lh)

        gc.SetFont(self.sub_font, col)
        gc.DrawText(
            self.subtitle,
            x,
            y + len(self.title_lines) * lh + 25
        )

        mdc.SelectObject(wx.NullBitmap)
        pdc.DrawBitmap(bmp, 0, 0, True)


# ============================================================
# MAIN APPLICATION FRAME
# ============================================================
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(
            None,
            title="StudyAura",
            size=(DESIGN_W, DESIGN_H)
        )

        self.Centre()
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.on_paint_frame)

        # Load background
        bg_path = os.path.join(ICON_FOLDER, ASSETS["background"])
        pil_bg = load_pil_image(bg_path, fallback_size=(DESIGN_W, DESIGN_H))
        pil_bg = pil_bg.resize((DESIGN_W, DESIGN_H), Image.LANCZOS)
        self._bg_bitmap = pil_to_wx_bitmap(pil_bg)

        # Title
        self.title = TitleCanvas(self, pos=(0, 200), size=(690, 300))
        self.title.Raise()
        self.title.start()

        # ----------------------------------------------------
        # Icons Row (Settings REMOVED)
        # ----------------------------------------------------
        names = ["Tasks", "Timetable", "Analytics",
                 "Reports", "Pomodoro"]

        xpos = [80, 380, 700, 1000, 1300]  # shifted slightly for spacing
        ypos = 550

        self.icons = []
        for i, name in enumerate(names):
            icon_path = os.path.join(ICON_FOLDER, ASSETS[name])
            pil_icon = load_pil_image(icon_path, fallback_size=ICON_SIZE)

            widget = AnimatedIcon(
                parent=self,
                name=name,
                pil_img=pil_icon,
                base_size=ICON_SIZE,
                frames=12,
                pos=(xpos[i], ypos),
                action=self.on_icon_click
            )
            widget.Raise()
            self.icons.append(widget)

        self.Show()

    def on_paint_frame(self, evt):
        dc = wx.AutoBufferedPaintDC(self)
        dc.DrawBitmap(self._bg_bitmap, 0, 0, True)

    def on_icon_click(self, name):
        if name == "Tasks":
            self.switch_to_tasks()
        else:
            wx.MessageBox(f"You clicked: {name}", "StudyAura")

    # ---------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------
    ''''''def on_sidebar_nav(self, label):
        if label == "Home":
            self.switch_to_home()
            return

        if label == "Tasks":
            self.switch_to_tasks()
            return''''''
    def on_sidebar_nav(self, label):

        # HOME
        if label == "Home":
            self.switch_to_home()
            return

        # TASKS
        if label == "Tasks":
            self.switch_to_tasks()
            return
        if label == "Today":
            self.switch_to_today()
            return


        # TEMPORARY NAVIGATION FOR OTHER BUTTONS
        if label in [
            "Today", "Upcoming", "Schedule", "Notes",
            "Assignments", "Exams", "Projects", "Resources"
        ]:
            wx.MessageBox(f"{label} screen coming soon!", "StudyAura")
            return

        wx.MessageBox(f"You clicked: {label}", "Navigation")



    def switch_to_tasks(self):
        self.title.Hide()
        for icon in self.icons:
            icon.Hide()

        self.tasks_screen = TasksScreen(
            parent=self,
            nav_callback=self.on_sidebar_nav,
            back_callback=self.switch_to_home
        )

        self.tasks_screen.SetPosition((0, 0))
        self.tasks_screen.SetSize((DESIGN_W, DESIGN_H))
        self.tasks_screen.Show()
    def switch_to_today(self):
        # Hide home screen
        self.title.Hide()
        for icon in self.icons:
            icon.Hide()

        # Destroy tasks screen if open
        if hasattr(self, "tasks_screen"):
            try:
                self.tasks_screen.Hide()
                self.tasks_screen.Destroy()
            except:
                pass

        


    def switch_to_home(self):
        if hasattr(self, "tasks_screen"):
            self.tasks_screen.Hide()
            self.tasks_screen.Destroy()

        self.title.Show()
        for icon in self.icons:
            icon.Show()

        self.Refresh()
        def switch_to_home(self):
            self.show_screen(HomeScreen)

        def switch_to_subject_progress(self):
            self.show_screen(SubjectProgressScreen)

        def switch_to_daily_progress(self):
            self.show_screen(DailyProgressScreen)

        def switch_to_heatmap(self):
            self.show_screen(StudyHeatmapScreen)

        def switch_to_tasks_completed(self):
            self.show_screen(TasksCompletedScreen)

        def switch_to_streak(self):
            self.show_screen(StudyStreakScreen)
        def show_screen(self, screen_class):
            # Hide home UI
            self.title.Hide()
            for icon in self.icons:
                icon.Hide()

            # Destroy old screen if exists
            if hasattr(self, "current_screen") and self.current_screen:
                self.current_screen.Hide()
                self.current_screen.Destroy()

            # Create new screen
            self.current_screen = screen_class(
                parent=self,
                nav_callback=self.on_sidebar_nav,
                back_callback=self.switch_to_home
            )

            self.current_screen.SetPosition((0, 0))
            self.current_screen.SetSize((DESIGN_W, DESIGN_H))
            self.current_screen.Show()




# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
'''
# ================================================================
#                       StudyAura — FINAL MAIN (robust imports)
#            wxPython version (transparent title + hover icons)
# ================================================================

import wx
import os
from PIL import Image

from icon_button import AnimatedIcon, load_pil_image, pil_to_wx_bitmap

# TasksScreen is required (you have it). If it's missing, we'll let the exception bubble.
from modules.tasks_screen import TasksScreen

# Try to import the other screens; if import fails create a lightweight placeholder class
def _make_placeholder(name):
    class Placeholder(wx.Panel):
        def __init__(self, parent, nav_callback=None, back_callback=None):
            super().__init__(parent)
            self.SetBackgroundColour(wx.Colour(20, 24, 30))
            s = wx.BoxSizer(wx.VERTICAL)
            lbl = wx.StaticText(self, label=f"{name}\n\n(Placeholder — module missing or class name changed)")
            lbl.SetFont(wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            lbl.SetForegroundColour(wx.Colour(220, 220, 220))
            s.AddStretchSpacer(1)
            s.Add(lbl, 0, wx.ALIGN_CENTER)
            s.AddStretchSpacer(1)

            # small back button for convenience
            back = wx.Button(self, label="Back to Home")
            back.Bind(wx.EVT_BUTTON, lambda e: back_callback() if back_callback else None)
            s.Add(back, 0, wx.ALIGN_CENTER | wx.TOP, 10)

            self.SetSizer(s)

    return Placeholder

# Safe imports with placeholders fallback
try:
    from modules.screen_home import HomeScreen
except Exception as e:
    print("Import warning: HomeScreen import failed:", e)
    HomeScreen = _make_placeholder("HomeScreen")

try:
    from modules.screen_subject_progress import SubjectProgressScreen
except Exception as e:
    print("Import warning: SubjectProgressScreen import failed:", e)
    SubjectProgressScreen = _make_placeholder("SubjectProgressScreen")

try:
    from modules.screen_daily_progress import DailyProgressScreen
except Exception as e:
    print("Import warning: DailyProgressScreen import failed:", e)
    DailyProgressScreen = _make_placeholder("DailyProgressScreen")

try:
    from modules.screen_heatmap import StudyHeatmapScreen
except Exception as e:
    print("Import warning: StudyHeatmapScreen import failed:", e)
    StudyHeatmapScreen = _make_placeholder("StudyHeatmapScreen")

try:
    from modules.screen_journey_map import JourneyMapScreen
except Exception as e:
    print("Import warning: TasksCompletedScreen import failed:", e)
    JourneyMapScreen = _make_placeholder("TasksCompletedScreen")

try:
    from modules.screen_streak import StudyStreakScreen
except Exception as e:
    print("Import warning: StudyStreakScreen import failed:", e)
    StudyStreakScreen = _make_placeholder("StudyStreakScreen")


BASE_PATH = os.path.dirname(__file__)
ICON_FOLDER = os.path.join(BASE_PATH, "assets", "icons")

ASSETS = {
    "background": "background.png",
    "Tasks": "tasks_icon.png",
    "To-do List": "todolist_icon.png",
    "Analytics": "analytics_icon.png",
    "Notes": "notes_icon.png",          # UPDATED ✔
    "Pomodoro": "pomodoro_icon.png"
}

DESIGN_W, DESIGN_H = 1550, 800
ICON_SIZE = (150, 150)


# ============================================================
# TRANSPARENT TITLE OVERLAY
# ============================================================
class TitleCanvas(wx.Window):
    def __init__(self, parent, pos=(0, 0), size=(900, 420)):
        super().__init__(
            parent, pos=pos, size=size,
            style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.TRANSPARENT_WINDOW
        )

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)

        self.alpha = 0.0
        self.offset_y = 40
        self.frame = 0
        self.max_frames = 35

        self.title_lines = ["     StudyAura:", "     Turn Plans", "   into Progress!"]
        self.subtitle = (
            "📘 Plan Smart   |   💪 Stay Consistent   |   🚀 Achieve Excellence"
        )

        self.title_font = wx.Font(
            50, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        )
        self.sub_font = wx.Font(
            15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        )

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

    def start(self, delay=50):
        wx.CallLater(delay, lambda: self.timer.Start(16))

    def on_timer(self, evt):
        self.frame += 1
        t = min(1.0, self.frame / self.max_frames)
        ease = 1 - (1 - t) ** 3

        self.alpha = ease
        self.offset_y = int(50 * (1 - ease))
        self.Refresh(False)

        if t >= 1.0:
            self.timer.Stop()

    def on_paint(self, evt):
        pdc = wx.AutoBufferedPaintDC(self)

        w, h = self.GetSize()
        bmp = wx.Bitmap(w, h, 32)
        mdc = wx.MemoryDC(bmp)

        mdc.SetBackground(wx.Brush(wx.Colour(0, 0, 0, 0)))
        mdc.Clear()

        gc = wx.GraphicsContext.Create(mdc)
        col = wx.Colour(255, 255, 255, int(self.alpha * 255))

        gc.SetFont(self.title_font, col)

        x = 40
        y = 10 + self.offset_y
        lh = self.title_font.GetPixelSize().y + 6

        for i, line in enumerate(self.title_lines):
            gc.DrawText(line, x, y + i * lh)

        gc.SetFont(self.sub_font, col)
        gc.DrawText(
            self.subtitle,
            x,
            y + len(self.title_lines) * lh + 25
        )

        mdc.SelectObject(wx.NullBitmap)
        pdc.DrawBitmap(bmp, 0, 0, True)


# ============================================================
# MAIN APPLICATION FRAME
# ============================================================
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(
            None,
            title="StudyAura",
            size=(DESIGN_W, DESIGN_H)
        )

        self.Centre()
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.on_paint_frame)

        # Load background (safe fallback)
        bg_path = os.path.join(ICON_FOLDER, ASSETS.get("background", "background.png"))
        pil_bg = load_pil_image(bg_path, fallback_size=(DESIGN_W, DESIGN_H))
        pil_bg = pil_bg.resize((DESIGN_W, DESIGN_H), Image.LANCZOS)
        self._bg_bitmap = pil_to_wx_bitmap(pil_bg)

        # Title overlay (home)
        self.title = TitleCanvas(self, pos=(0, 200), size=(690, 300))
        self.title.Raise()
        self.title.start()

        # Icons Row
        names = ["Tasks", "To-do List", "Analytics", "Notes", "Pomodoro"]   # UPDATED ✔
        xpos = [80, 380, 700, 1000, 1300]
        ypos = 550

        self.icons = []
        for i, name in enumerate(names):
            icon_path = os.path.join(ICON_FOLDER, ASSETS.get(name, ""))
            pil_icon = load_pil_image(icon_path, fallback_size=ICON_SIZE)

            widget = AnimatedIcon(
                parent=self,
                name=name,
                pil_img=pil_icon,
                base_size=ICON_SIZE,
                frames=12,
                pos=(xpos[i], ypos),
                action=self.on_icon_click
            )
            widget.Raise()
            self.icons.append(widget)

        # container for currently displayed screen (other than home)
        self.current_screen = None

        self.Show()

    def on_paint_frame(self, evt):
        dc = wx.AutoBufferedPaintDC(self)
        dc.DrawBitmap(self._bg_bitmap, 0, 0, True)

    def on_icon_click(self, name):
        if name == "Tasks":
            self.show_screen(TasksScreen)

        elif name == "Notes":   # ADDED ✔
            wx.MessageBox("Notes Clicked!", "StudyAura")

        else:
            wx.MessageBox(f"You clicked: {name}", "StudyAura")

    # ---------------------------------------------------------
    # Navigation callback from child screens (sidebar etc.)
    # ---------------------------------------------------------
    def on_sidebar_nav(self, label):

        if label == "Home":
            self.switch_to_home()
            return

        if label == "Tasks":
            self.show_screen(TasksScreen)
            return

        if label in ["Subject Progress", "SubjectProgress", "Subjects"]:
            self.show_screen(SubjectProgressScreen)
            return

        if label in ["Study Heatmap", "Heatmap"]:
            self.show_screen(StudyHeatmapScreen)
            return

        if label in ["Daily Progress", "DailyProgress", "Today"]:
            self.show_screen(DailyProgressScreen)
            return

        if label in ["Tasks Completed", "TasksCompleted", "Completed"]:
            self.show_screen(JourneyMapScreen)
            return

        if label in ["Study Streak", "Streak"]:
            self.show_screen(StudyStreakScreen)
            return

        wx.MessageBox(f"You clicked: {label}", "Navigation")

    # ---------------------------------------------------------
    # Screen management helpers
    # ---------------------------------------------------------
    def _destroy_current_screen(self):
        if hasattr(self, "current_screen") and self.current_screen:
            try:
                self.current_screen.Hide()
                self.current_screen.Destroy()
            except Exception:
                pass
            self.current_screen = None

        if hasattr(self, "tasks_screen"):
            try:
                self.tasks_screen.Hide()
                self.tasks_screen.Destroy()
            except Exception:
                pass

    def show_screen(self, screen_class):
        try:
            self.title.Hide()
        except Exception:
            pass
        for icon in getattr(self, "icons", []):
            try:
                icon.Hide()
            except Exception:
                pass

        if self.current_screen:
            self._destroy_current_screen()

        try:
            self.current_screen = screen_class(
                parent=self,
                nav_callback=self.on_sidebar_nav,
                back_callback=self.switch_to_home
            )
        except TypeError:
            self.current_screen = screen_class(self)
            try:
                setattr(self.current_screen, "nav_callback", self.on_sidebar_nav)
                setattr(self.current_screen, "back_callback", self.switch_to_home)
            except Exception:
                pass

        self.current_screen.SetPosition((0, 0))
        self.current_screen.SetSize((DESIGN_W, DESIGN_H))
        self.current_screen.Show()
        self.Refresh()

    # ---------------------------------------------------------
    # Convenience named switches
    # ---------------------------------------------------------
    def switch_to_home(self):
        self._destroy_current_screen()
        try:
            self.title.Show()
        except Exception:
            pass
        for icon in getattr(self, "icons", []):
            try:
                icon.Show()
            except Exception:
                pass
        self.Refresh()


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
