import wx
import wx.lib.buttons as buttons
import os

class NotesPage(wx.Panel):
    def __init__(self, parent, nav_callback=None, back_callback=None):
        super().__init__(parent)

        # Save callbacks
        self.nav_callback = nav_callback
        self.back_callback = back_callback
        
        # ==========================================
        # 🎨 THEME COLORS
        # ==========================================
        self.colors = {
            "bg": "#020617",
            "sidebar": "#020617",
            "neon": "#00F5FF",
            "purple": "#A855F7",
            "danger": "#FF2D55",
            "white": "#FFFFFF",
            "text": "#E5E7EB",
            "btn_text": "#000000"
        }
        
        self.SetBackgroundColour(self.colors["bg"])

        # ==========================================
        # 📂 FILE SETUP
        # ==========================================
        self.folder = os.path.join(os.getcwd(), "data")
        os.makedirs(self.folder, exist_ok=True)
        self.current_file = None

        # ==========================================
        # 📐 LAYOUTS
        # ==========================================
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create Left Sidebar and Right Editor
        self.create_sidebar()
        self.create_editor()

        self.SetSizer(self.main_sizer)

        # Initial load
        self.refresh_notes()

    # -------------------------------------------------------------
    # LEFT SIDEBAR
    # -------------------------------------------------------------
    def create_sidebar(self):
        left_panel = wx.Panel(self, size=(260, -1))
        left_panel.SetBackgroundColour(self.colors["sidebar"])
        
        left_sizer = wx.BoxSizer(wx.VERTICAL)

        lbl_title = wx.StaticText(left_panel, label="📁  MY NOTES")
        lbl_title.SetFont(wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        lbl_title.SetForegroundColour(self.colors["neon"])
        left_sizer.Add(lbl_title, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 15)

        # Notes list
        self.notes_list = wx.ListBox(left_panel, style=wx.LB_SINGLE)
        self.notes_list.SetBackgroundColour("#0B1120")
        self.notes_list.SetForegroundColour(self.colors["white"])
        self.notes_list.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.notes_list.Bind(wx.EVT_LISTBOX, self.load_note)
        left_sizer.Add(self.notes_list, 1, wx.EXPAND | wx.ALL, 10)

        # Helper to create neon buttons
        def make_btn(label, bg_col, txt_col, handler):
            btn = buttons.GenButton(left_panel, label=label)
            btn.SetBackgroundColour(bg_col)
            btn.SetForegroundColour(txt_col)
            btn.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            btn.Bind(wx.EVT_BUTTON, handler)
            return btn

        btn_new = make_btn("➕ New Note", self.colors["neon"], "BLACK", self.new_note)
        btn_rename = make_btn("✏ Rename", self.colors["purple"], "WHITE", self.rename_note)
        btn_delete = make_btn("🗑 Delete", self.colors["danger"], "WHITE", self.delete_note)
        btn_refresh = make_btn("🔄 Refresh", "#111827", "WHITE", self.refresh_notes)

        left_sizer.Add(btn_new, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        left_sizer.Add(btn_rename, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        left_sizer.Add(btn_delete, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        left_sizer.Add(btn_refresh, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # -----------------------------------------
        # ⭐ ADDED BACK BUTTON (ONLY NEW FEATURE)
        # -----------------------------------------
        btn_back = make_btn("⬅  Back", "#0EA5E9", "BLACK", self.go_back)
        left_sizer.Add(btn_back, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        left_panel.SetSizer(left_sizer)

        self.main_sizer.Add(left_panel, 0, wx.EXPAND | wx.RIGHT, 2)

    # -------------------------------------------------------------
    # RIGHT NOTE EDITOR
    # -------------------------------------------------------------
    def create_editor(self):
        right_panel = wx.Panel(self)
        right_panel.SetBackgroundColour(self.colors["bg"])
        
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        lbl_editor = wx.StaticText(right_panel, label="✨  NOTES")
        lbl_editor.SetFont(wx.Font(26, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        lbl_editor.SetForegroundColour(self.colors["neon"])
        right_sizer.Add(lbl_editor, 0, wx.ALL, 15)

        self.title_entry = wx.TextCtrl(right_panel, style=wx.TE_PROCESS_ENTER)
        self.title_entry.SetBackgroundColour("#0B1120")
        self.title_entry.SetForegroundColour(self.colors["white"])
        self.title_entry.SetFont(wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        right_sizer.Add(self.title_entry, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)

        self.text_box = wx.TextCtrl(right_panel, style=wx.TE_MULTILINE)
        self.text_box.SetBackgroundColour("#0B1120")
        self.text_box.SetForegroundColour(self.colors["white"])
        self.text_box.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        right_sizer.Add(self.text_box, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)

        self.save_btn = buttons.GenButton(right_panel, label="💾  SAVE NOTE")
        self.save_btn.SetBackgroundColour(self.colors["neon"])
        self.save_btn.SetForegroundColour("BLACK")
        self.save_btn.SetFont(wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.save_btn.SetMinSize((-1, 60))
        self.save_btn.Bind(wx.EVT_BUTTON, self.save_note)
        right_sizer.Add(self.save_btn, 0, wx.ALIGN_CENTER | wx.ALL, 20)

        right_panel.SetSizer(right_sizer)
        self.main_sizer.Add(right_panel, 1, wx.EXPAND)

    # -------------------------------------------------------------
    # NOTE LOGIC
    # -------------------------------------------------------------
    def refresh_notes(self, event=None):
        self.notes_list.Clear()
        if os.path.exists(self.folder):
            for file in os.listdir(self.folder):
                if file.endswith(".txt"):
                    self.notes_list.Append(file.replace(".txt", ""))

    def new_note(self, event):
        self.current_file = None
        self.title_entry.SetValue("")
        self.text_box.SetValue("")

    def save_note(self, event):
        title = self.title_entry.GetValue().strip()
        content = self.text_box.GetValue().strip()

        if not title:
            wx.MessageBox("Enter a title!", "Missing", wx.OK | wx.ICON_WARNING)
            return

        filename = title.replace(" ", "_") + ".txt"
        path = os.path.join(self.folder, filename)

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            self.current_file = filename
            self.refresh_notes()
            wx.MessageBox("Note saved successfully!", "Saved", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"Error saving note: {e}", "Error", wx.OK | wx.ICON_ERROR)

    def load_note(self, event):
        selection = self.notes_list.GetStringSelection()
        if not selection:
            return

        self.current_file = selection.replace(" ", "_") + ".txt"
        path = os.path.join(self.folder, self.current_file)

        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            self.title_entry.SetValue(selection)
            self.text_box.SetValue(content)

    def delete_note(self, event):
        if not self.current_file:
            return

        path = os.path.join(self.folder, self.current_file)
        if os.path.exists(path):
            os.remove(path)
            self.new_note(None)
            self.refresh_notes()

    def rename_note(self, event):
        if not self.current_file:
            return

        dlg = wx.TextEntryDialog(self, "New name:", "Rename Note", self.title_entry.GetValue())
        if dlg.ShowModal() == wx.ID_OK:
            new_name = dlg.GetValue().strip()
            if new_name:
                new_filename = new_name.replace(" ", "_") + ".txt"
                old_path = os.path.join(self.folder, self.current_file)
                new_path = os.path.join(self.folder, new_filename)

                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                    self.current_file = new_filename
                    self.title_entry.SetValue(new_name)
                    self.refresh_notes()
        dlg.Destroy()

    # -------------------------------------------------------------
    # ⭐ BACK BUTTON HANDLER
    # -------------------------------------------------------------
    def go_back(self, event):
        if self.back_callback:
            self.back_callback()
