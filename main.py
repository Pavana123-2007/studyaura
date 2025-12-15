# ================================================================
#             StudyAura —MAIN screen(wxPython version) 
# ================================================================
import wx
import os
from PIL import Image
from icon_button import AnimatedIcon, load_pil_image, pil_to_wx_bitmap
from modules.tasks_screen import TasksScreen
from modules.todo_list import ToDoListScreen
from modules.screen_home import HomeScreen
from modules.screen_subject_progress import SubjectProgressScreen
from modules.screen_daily_progress import DailyProgressScreen
from modules.screen_heatmap import StudyHeatmapScreen
from modules.pomodoro import PomodoroPage
from modules.notes import NotesPage
from modules.screen_journey_map import JourneyMapScreen

# ICONS + DIMENSIONS
BASE_PATH = os.path.dirname(__file__)
ICON_FOLDER = os.path.join(BASE_PATH, "assets", "icons")
ASSETS = {
    "background": "background.png",
    "Tasks": "tasks_icon.png",
    "To-do List": "todolist_icon.png",
    "Study Journey Map": "analytics_icon.png",
    "Notes": "notes_icon.png",
    "Pomodoro": "pomodoro_icon.png",
}
DESIGN_W, DESIGN_H = 1550, 800
ICON_SIZE = (150, 150)
# TRANSPARENT TITLE CANVAS
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
        self.subtitle = "📘 Plan Smart   |   💪 Stay Consistent   |   🚀 Achieve Excellence"

        self.title_font = wx.Font(50, wx.FONTFAMILY_SWISS,
                                  wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.sub_font = wx.Font(15, wx.FONTFAMILY_SWISS,
                                wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

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

        if t >= 1:
            self.timer.Stop()

    def on_paint(self, evt):
        pdc = wx.AutoBufferedPaintDC(self)
        w, h = self.GetSize()

        bmp = wx.Bitmap(w, h, 32)
        mem = wx.MemoryDC(bmp)
        mem.SetBackground(wx.Brush(wx.Colour(0, 0, 0, 0)))
        mem.Clear()

        gc = wx.GraphicsContext.Create(mem)
        col = wx.Colour(255, 255, 255, int(self.alpha * 255))
        gc.SetFont(self.title_font, col)

        x = 40
        y = 10 + self.offset_y
        lh = self.title_font.GetPixelSize().y + 6

        for i, line in enumerate(self.title_lines):
            gc.DrawText(line, x, y + i * lh)

        gc.SetFont(self.sub_font, col)
        gc.DrawText(self.subtitle, x, y + len(self.title_lines) * lh + 25)

        mem.SelectObject(wx.NullBitmap)
        pdc.DrawBitmap(bmp, 0, 0, True)

# MAIN FRAME
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="StudyAura", size=(DESIGN_W, DESIGN_H))

        self.Center()
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.on_paint_frame)

        # Load background
        bg_path = os.path.join(ICON_FOLDER, ASSETS["background"])
        pil_bg = load_pil_image(bg_path, fallback_size=(DESIGN_W, DESIGN_H))
        pil_bg = pil_bg.resize((DESIGN_W, DESIGN_H), Image.LANCZOS)
        self._bg_bitmap = pil_to_wx_bitmap(pil_bg)

        # Title
        self.title = TitleCanvas(self, pos=(0, 200), size=(690, 300))
        self.title.start()

        # Home icons
        names = ["Tasks", "To-do List", "Study Journey Map", "Notes", "Pomodoro"]
        xpos = [80, 380, 700, 1000, 1300]
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

        self.current_screen = None
        self.Show()

    
    def on_paint_frame(self, evt):
        dc = wx.AutoBufferedPaintDC(self)
        dc.DrawBitmap(self._bg_bitmap, 0, 0, True)
    
    # ICON CLICK HANDLER
    def on_icon_click(self, name):

        if name == "Tasks":
            self.show_screen(TasksScreen)
        elif name == "To-do List":
            self.show_screen(ToDoListScreen)
        elif name == "Study Journey Map":
            self.show_screen(JourneyMapScreen)
        elif name == "Notes":
            self.show_screen(NotesPage)
        elif name == "Pomodoro":
            self.show_screen(PomodoroPage)
        else:
            wx.MessageBox(f"You clicked: {name}", "StudyAura")
    
    # SIDEBAR NAVIGATION HANDLER
    def on_sidebar_nav(self, label):

        if label == "Home":
            self.switch_to_home()
            return
        if label == "Tasks":
            self.show_screen(TasksScreen)
            return
        if label in ["Subject Progress", "SubjectProgress"]:
            self.show_screen(SubjectProgressScreen)
            return
        if label in ["Study Heatmap", "Heatmap"]:
            self.show_screen(StudyHeatmapScreen)
            return
        if label in ["Daily Progress", "DailyProgress"]:
            self.show_screen(DailyProgressScreen)
            return
    # SCREEN MANAGEMENT
    def _destroy_current_screen(self):
        if self.current_screen:
            try:
                self.current_screen.Destroy()
            except:
                pass
            self.current_screen = None

    def show_screen(self, screen_class):

        # Hide home screen
        self.title.Hide()
        for icon in self.icons:
            icon.Hide()

        self._destroy_current_screen()

        # Try to init screen with callbacks
        try:
            self.current_screen = screen_class(
                parent=self,
                nav_callback=self.on_sidebar_nav,
                back_callback=self.switch_to_home
            )
        except TypeError:
            # Screen doesn't support callbacks
            self.current_screen = screen_class(self)

        self.current_screen.SetPosition((0, 0))
        self.current_screen.SetSize((DESIGN_W, DESIGN_H))
        self.current_screen.Show()
        self.Refresh()

    def switch_to_home(self):
        self._destroy_current_screen()

        self.title.Show()
        for icon in self.icons:
            icon.Show()

        self.Refresh()
# ENTRY POINT
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
