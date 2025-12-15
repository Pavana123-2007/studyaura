import wx
import wx.lib.scrolledpanel as scrolled
import os
import json
import datetime

class ToDoListScreen(wx.Panel):
    def __init__(self, parent, nav_callback=None, back_callback=None):
        super().__init__(parent)

        self.nav_callback = nav_callback
        self.back_callback = back_callback

        # IMAGE PATHS
        self.BANNER_PATH_USER = r"D:\StudyAura-'Your Space for Smarter Learning'\assets\themes\bg1.jpg"
        self.LEAF_PATH_USER   = r"D:\StudyAura-'Your Space for Smarter Learning'\assets\themes\bg2.jpg"
        self.COFFEE_PATH_USER = r"D:\StudyAura-'Your Space for Smarter Learning'\assets\themes\bg3.jpg"

        # DATA DIRECTORY
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.data_dir = os.path.join(self.base_dir, "data")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        self.data_file = os.path.join(self.data_dir, "schedule.json")

        self.default_data = {
            "Monday":   ["7:30 Biology 🧬", "9:55 History 📖"],
            "Tuesday":  ["7:30 Literature 📚", "9:55 Math 📐"],
            "Wednesday": ["7:30 Geography 🗺️", "9:55 Science 🔬"],
            "Thursday":  ["7:30 Math ➕", "11:55 Physics ⚛️"],
            "Friday":    ["9:00 Coding 💻", "13:00 Movie Night 🎬"],
            "Saturday":  ["Revision 📝"],
            "Sunday":    ["Plan Next Week 📅"]
        }

        self.schedule_data = self.load_data()

        # COLORS
        self.colors = {
            "bg": "#191919",
            "card_bg": "#2A2A2A",
            "text_light": "#FFFFFF",
            "text_dim": "#B3B3B3",
            "accent_green": "#19B552",
            "task_green": "#24CF91",
            "checked": "#6EE7B7",
            "danger": "#EF4444"
        }

        self.init_ui()

    # ==================================================================
    # LOAD & SAVE
    # ==================================================================
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return self.default_data
        return self.default_data

    def save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.schedule_data, f, indent=4)
        except:
            pass

    # ==================================================================
    # UI SETUP
    # ==================================================================
    def init_ui(self):
        self.SetBackgroundColour(self.colors["bg"])

        root_sizer = wx.BoxSizer(wx.VERTICAL)

        # HEADER
        header = wx.Panel(self)
        header.SetBackgroundColour(self.colors["bg"])
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)

        back_btn = wx.Button(header, label="← Back to Home")
        back_btn.SetBackgroundColour("#2A2A2A")
        back_btn.SetForegroundColour("#FFFFFF")
        back_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        back_btn.Bind(wx.EVT_BUTTON, lambda e: self.back_callback() if self.back_callback else None)

        title = wx.StaticText(header, label="📖 Weekly Schedule  To-Do List")
        title.SetFont(wx.Font(22, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        title.SetForegroundColour("#FFFFFF")

        header_sizer.Add(back_btn, 0, wx.ALL, 10)
        header_sizer.Add(title, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 20)
        header.SetSizer(header_sizer)

        root_sizer.Add(header, 0, wx.EXPAND | wx.BOTTOM, 10)

        # SCROLLER
        self.scroll_win = scrolled.ScrolledPanel(self)
        self.scroll_win.SetBackgroundColour(self.colors["bg"])
        self.scroll_win.SetupScrolling(scroll_x=False, scroll_y=True)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scroll_win.SetSizer(self.main_sizer)

        self.render_banner()

        # MAIN LAYOUT (Left + Center)
        self.columns_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.Add(self.columns_sizer, 1, wx.EXPAND | wx.ALL, 20)

        self.render_left_col()

        # SCHEDULE CENTER COLUMN — WIDER (changed 3 → 5)
        self.schedule_sizer = wx.BoxSizer(wx.VERTICAL)
        self.columns_sizer.Add(self.schedule_sizer, 5, wx.EXPAND | wx.LEFT, 40)
        self.render_schedule_col()

        # NOTE: RIGHT COLUMN REMOVED

        root_sizer.Add(self.scroll_win, 1, wx.EXPAND)
        self.SetSizer(root_sizer)

    # ==================================================================
    # LOAD IMAGE
    # ==================================================================
    def load_image(self, path, w, h):
        if os.path.exists(path):
            img = wx.Image(path, wx.BITMAP_TYPE_ANY)
            img = img.Scale(w, h, wx.IMAGE_QUALITY_HIGH)
            return wx.Bitmap(img)
        return None

    # ==================================================================
    # BANNER
    # ==================================================================
    def render_banner(self):
        bmp = self.load_image(self.BANNER_PATH_USER, 1100, 200)
        if bmp:
            banner = wx.StaticBitmap(self.scroll_win, bitmap=bmp)
            self.main_sizer.Add(banner, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 15)

    # ==================================================================
    # LEFT COLUMN (Clock + Plant)
    # ==================================================================
    def render_left_col(self):
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        self.columns_sizer.Add(left_sizer, 1, wx.EXPAND)

        # CLOCK CARD
        clock_panel = wx.Panel(self.scroll_win)
        clock_panel.SetBackgroundColour("#19B552")
        clock_sizer = wx.BoxSizer(wx.VERTICAL)

        self.time_lbl = wx.StaticText(clock_panel, label="00:00")
        self.time_lbl.SetFont(wx.Font(48, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.time_lbl.SetForegroundColour("#065F46")

        self.day_lbl = wx.StaticText(clock_panel, label="DAY")
        self.day_lbl.SetFont(wx.Font(18, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.day_lbl.SetForegroundColour("#065F46")

        clock_sizer.Add(self.time_lbl, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        clock_sizer.Add(self.day_lbl, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        clock_panel.SetSizer(clock_sizer)
        left_sizer.Add(clock_panel, 0, wx.EXPAND | wx.BOTTOM, 20)

        # TIMER
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_clock, self.timer)
        self.timer.Start(1000)
        self.update_clock(None)

        # PLANT IMAGE
        bmp = self.load_image(self.LEAF_PATH_USER, 200, 230)
        if bmp:
            leaf_img = wx.StaticBitmap(self.scroll_win, bitmap=bmp)
            left_sizer.Add(leaf_img, 0, wx.ALIGN_CENTER | wx.TOP, 10)

    # ==================================================================
    # CENTER COLUMN — SCHEDULE CARDS (WIDER)
    # ==================================================================
    def render_schedule_col(self):
        self.schedule_sizer.Clear(True)

        days = list(self.schedule_data.keys())
        grid = wx.GridBagSizer(vgap=20, hgap=40)

        for i, day in enumerate(days):
            r = i // 2
            c = i % 2

            card = wx.Panel(self.scroll_win)
            card.SetBackgroundColour(self.colors["card_bg"])

            # ⬅ NEW: Force wider card width
            card.SetMinSize((480, -1))

            card_sizer = wx.BoxSizer(wx.VERTICAL)

            # Header
            header = wx.BoxSizer(wx.HORIZONTAL)

            day_title = wx.StaticText(card, label=f"💚 {day}")
            day_title.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            day_title.SetForegroundColour("#19B552")

            add_btn = wx.StaticText(card, label="+")
            add_btn.SetFont(wx.Font(22, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            add_btn.SetForegroundColour("#FFFFFF")
            add_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
            add_btn.Bind(wx.EVT_LEFT_DOWN, lambda evt, d=day: self.on_add_task(evt, d))

            header.Add(day_title, 1)
            header.Add(add_btn, 0)
            card_sizer.Add(header, 0, wx.EXPAND | wx.BOTTOM, 10)

            # Tasks
            for idx, task_text in enumerate(self.schedule_data[day]):
                row = wx.BoxSizer(wx.HORIZONTAL)

                check = wx.StaticText(card, label="☐")
                check.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                check.SetForegroundColour("#24CF91")
                check.SetCursor(wx.Cursor(wx.CURSOR_HAND))

                lbl = wx.StaticText(card, label=task_text)
                lbl.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
                lbl.SetForegroundColour("#FFFFFF")

                del_btn = wx.StaticText(card, label="×")
                del_btn.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                del_btn.SetForegroundColour("#888888")
                del_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))

                check.Bind(wx.EVT_LEFT_DOWN, lambda evt, c=check, l=lbl: self.on_toggle_check(c, l))
                del_btn.Bind(wx.EVT_LEFT_DOWN, lambda evt, d=day, ix=idx: self.on_delete_task(d, ix))

                row.Add(check, 0, wx.RIGHT, 8)
                row.Add(lbl, 1)
                row.Add(del_btn, 0, wx.LEFT, 10)

                card_sizer.Add(row, 0, wx.EXPAND | wx.BOTTOM, 6)

            # ⬅ NEW: Wider inner padding
            wrap = wx.BoxSizer(wx.VERTICAL)
            wrap.Add(card_sizer, 1, wx.ALL, 30)
            card.SetSizer(wrap)

            grid.Add(card, pos=(r, c), flag=wx.EXPAND)

        self.schedule_sizer.Add(grid, 1, wx.EXPAND)
        self.scroll_win.Layout()
        self.Layout()

    # ==================================================================
    # EVENTS
    # ==================================================================
    def update_clock(self, event):
        now = datetime.datetime.now()
        self.time_lbl.SetLabel(now.strftime("%I:%M %p"))
        self.day_lbl.SetLabel(now.strftime("%A").upper())

    def on_add_task(self, event, day):
        dlg = wx.TextEntryDialog(self, f"New task for {day}:", "Add Task")
        if dlg.ShowModal() == wx.ID_OK:
            t = dlg.GetValue()
            if t:
                self.schedule_data[day].append(t)
                self.save_data()
                self.render_schedule_col()
        dlg.Destroy()

    def on_delete_task(self, day, index):
        del self.schedule_data[day][index]
        self.save_data()
        self.render_schedule_col()

    def on_toggle_check(self, check_widget, text_widget):
        if check_widget.GetLabel() == "☐":
            check_widget.SetLabel("☑")
            check_widget.SetForegroundColour(self.colors["checked"])

            font = text_widget.GetFont()
            font.SetStrikethrough(True)
            text_widget.SetFont(font)
            text_widget.SetForegroundColour(self.colors["text_dim"])
        else:
            check_widget.SetLabel("☐")
            check_widget.SetForegroundColour(self.colors["task_green"])

            font = text_widget.GetFont()
            font.SetStrikethrough(False)
            text_widget.SetFont(font)
            text_widget.SetForegroundColour("#FFFFFF")
