import wx
import csv
import os
import math
from datetime import datetime, date, timedelta

# -------------------- THEME --------------------
BG = wx.Colour(18, 24, 34)
BAR_BG = wx.Colour(40, 55, 70)
NEON = wx.Colour(0, 200, 255)
TIMELINE_BG = wx.Colour(30, 40, 50)
TIMELINE_BORDER = wx.Colour(0, 180, 255)
TEXT = wx.Colour(220, 230, 240)
OVERDUE_RED = wx.Colour(255, 80, 80)
INCOMPLETE_GREY = wx.Colour(120, 130, 150)

# Animation constants
ANIM_TIMER_MS = 16        # ~60 FPS
ANIM_INCREMENT = 0.01     # progress bar increment per tick
PULSE_SPEED = 0.12        # pulse phase increment per tick
PULSE_AMPLITUDE = 0.12    # how much the pulse changes glow/size


# -------------------- UTIL --------------------
def parse_date_str(s: str):
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            pass
    return None


def parse_time_str(s: str):
    s = (s or "").strip()
    try:
        hh, mm = map(int, s.split(":"))
        return hh * 60 + mm
    except Exception:
        return None


# ============================================================
#                      DailyProgressScreen
# ============================================================
class DailyProgressScreen(wx.Panel):
    def __init__(self, parent, nav_callback=None, back_callback=None):
        super().__init__(parent)

        self.nav_callback = nav_callback
        self.back_callback = back_callback

        self.SetBackgroundColour(BG)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        # -----------------------------------------------------
        # BACK BUTTON (top-left)
        # -----------------------------------------------------
        self.back_btn = wx.StaticText(self, label="← Back")
        self.back_btn.SetForegroundColour(wx.Colour(120, 220, 255))
        self.back_btn.SetFont(wx.Font(
            16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        ))
        self.back_btn.SetPosition((20, 15))

        # Hover effects
        self.back_btn.Bind(wx.EVT_ENTER_WINDOW,
                        lambda e: self.back_btn.SetForegroundColour(wx.Colour(255, 255, 255)))
        self.back_btn.Bind(wx.EVT_LEAVE_WINDOW,
                        lambda e: self.back_btn.SetForegroundColour(wx.Colour(120, 220, 255)))

        # Click event
        self.back_btn.Bind(wx.EVT_LEFT_DOWN, self.go_back)


        self.view_day = date.today()

        # tasks loaded from CSV as list of dicts (keeps raw fields)
        self.tasks = self._load_tasks_csv()

        # animation state
        self.animated_frac = 0.0   # 0..1 for progress bar
        self.target_frac = 0.0
        self.pulse_phase = 0.0     # for overdue pulse

        # clickable session rects: list of (wx.Rect, session_dict)
        self.session_rects = []

        # hitboxes for navigation arrows
        self.prev_rect = wx.Rect()
        self.next_rect = wx.Rect()

        # timer for both progress fill and pulse
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer, self.timer)
        self.timer.Start(ANIM_TIMER_MS)

        # events
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_SIZE, lambda e: (self.Refresh(), e.Skip()))

        # init target fraction
        self._recompute_target_frac()

    # ---------------- CSV IO ----------------
    def _tasks_csv_path(self):
        base = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(base, "data", "tasks.csv")

    def _load_tasks_csv(self):
        path = self._tasks_csv_path()
        tasks = []
        if not os.path.exists(path):
            return tasks
        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Normalize keys and preserve raw row
                    r = {k.strip(): (v.strip() if v is not None else "") for k, v in row.items()}
                    tasks.append(r)
        except Exception as e:
            print("DailyProgress: CSV read error:", e)
        return tasks

    def _write_tasks_csv(self):
        path = self._tasks_csv_path()
        if not os.path.exists(path):
            return False
        try:
            # read original header order
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames or ["title", "date", "start", "end", "completed"]

            # write self.tasks back (they contain cleaned keys)
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in self.tasks:
                    # ensure all fields exist
                    row = {k: r.get(k, "") for k in fieldnames}
                    writer.writerow(row)
            return True
        except Exception as e:
            print("DailyProgress: CSV write error:", e)
            return False

    # ---------------- session helpers ----------------
    def _sessions_for_day(self, d: date):
        out = []
        for r in self.tasks:
            dt = parse_date_str(r.get("date", ""))
            if dt != d:
                continue
            start_m = parse_time_str(r.get("start", ""))
            end_m = parse_time_str(r.get("end", ""))
            if start_m is None or end_m is None:
                continue
            out.append({
                "raw": r,
                "title": r.get("title", "Untitled"),
                "start_m": start_m,
                "end_m": end_m,
                "completed": str(r.get("completed", "")).strip().upper() == "TRUE",
            })
        out.sort(key=lambda x: x["start_m"])
        return out

    def _recompute_target_frac(self):
        # recompute today totals and set target_frac
        sessions = self._sessions_for_day(self.view_day)
        total = sum(max(0, s["end_m"] - s["start_m"]) for s in sessions)
        done = sum(max(0, s["end_m"] - s["start_m"]) for s in sessions if s["completed"])
        self.target_frac = 0.0 if total == 0 else min(1.0, done / total)

    # ----------------- timer -----------------
    def _on_timer(self, evt):
        # progress bar easing toward target_frac
        if self.animated_frac < self.target_frac:
            self.animated_frac = min(self.target_frac, self.animated_frac + ANIM_INCREMENT)
        elif self.animated_frac > self.target_frac:
            # rare case when target decreased
            self.animated_frac = max(self.target_frac, self.animated_frac - ANIM_INCREMENT)

        # advance pulse (wrap)
        self.pulse_phase = (self.pulse_phase + PULSE_SPEED) % (2 * math.pi)

        # refresh
        self.Refresh()

    # ----------------- clicks -----------------
    def on_left_down(self, evt):
        pt = evt.GetPosition()
        # nav
        if self.prev_rect.Contains(pt):
            self.view_day = self.view_day - timedelta(days=1)
            # reload tasks (in case CSV changed) and recompute animation
            self.tasks = self._load_tasks_csv()
            self._recompute_target_frac()
            return
        if self.next_rect.Contains(pt):
            self.view_day = self.view_day + timedelta(days=1)
            self.tasks = self._load_tasks_csv()
            self._recompute_target_frac()
            return

        # sessions
        for rect, sess in self.session_rects:
            if rect.Contains(pt):
                self._on_session_click(sess)
                return

    def _on_session_click(self, sess):
        # Show details and allow "Mark Completed"
        title = sess["title"]
        start = f"{sess['start_m'] // 60:02d}:{sess['start_m'] % 60:02d}"
        end = f"{sess['end_m'] // 60:02d}:{sess['end_m'] % 60:02d}"
        completed = sess["completed"]
        msg = f"{title}\n{start} → {end}\nCompleted: {'Yes' if completed else 'No'}"
        dlg = wx.MessageDialog(self, msg + "\n\nMark as completed?", "Session", style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION)
        res = dlg.ShowModal()
        dlg.Destroy()
        if res == wx.ID_YES and not completed:
            # find matching row in self.tasks (match by title,date,start,end)
            raw = sess["raw"]
            for r in self.tasks:
                if (r.get("title","").strip() == raw.get("title","").strip() and
                    r.get("date","").strip() == raw.get("date","").strip() and
                    r.get("start","").strip() == raw.get("start","").strip() and
                    r.get("end","").strip() == raw.get("end","").strip()):
                    r["completed"] = "TRUE"
                    break
            # write back csv
            ok = self._write_tasks_csv()
            if not ok:
                wx.MessageBox("Failed to save changes to CSV.", "Error", wx.OK | wx.ICON_ERROR)
            else:
                # reload tasks and update animation target
                self.tasks = self._load_tasks_csv()
                self._recompute_target_frac()
    # -----------------------------------------------------
    # BACK NAVIGATION
    # -----------------------------------------------------
    def go_back(self, event):
        if self.back_callback:
            self.back_callback()  # Return to tasks_screen.py


    # ----------------- drawing -----------------
    def on_paint(self, evt):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        # Keep back button visible during repaints
        self.back_btn.Refresh()

        w, h = self.GetSize()

        # Title
        title_font = wx.Font(34, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_BOLD)
        dc.SetFont(title_font)
        dc.SetTextForeground(TEXT)
        dc.DrawText("⏳ Daily Study Time Progress", 40, 26)

        # Date & arrows
        date_font = wx.Font(18, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_BOLD)
        arrow_font = wx.Font(28, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_BOLD)

        dc.SetFont(arrow_font)
        prev_x = 40
        next_x = w - 60
        dc.SetTextForeground(TEXT)
        dc.DrawText("<", prev_x, 100)
        dc.DrawText(">", next_x, 100)
        self.prev_rect = wx.Rect(prev_x, 100, 36, 36)
        self.next_rect = wx.Rect(next_x, 100, 36, 36)

        dc.SetFont(date_font)
        date_str = self.view_day.strftime("%A, %d %B %Y")
        dc.DrawText(date_str, prev_x + 56, 106)

        # Progress bar
        bar_x = 72
        bar_w = w - bar_x - 72
        bar_y = 170
        bar_h = 48

        dc.SetBrush(wx.Brush(BAR_BG))
        dc.SetPen(wx.Pen(BAR_BG))
        dc.DrawRoundedRectangle(bar_x, bar_y, bar_w, bar_h, 12)

        # Animated fill (neon)
        fill_w = int(bar_w * self.animated_frac)
        if fill_w > 0:
            # glow layers behind fill
            for i, pad in enumerate((18, 12, 6), start=0):
                alpha = int(80 / (i + 1))
                g = wx.Colour(NEON.Red(), NEON.Green(), NEON.Blue(), alpha)
                gc = wx.GraphicsContext.Create(dc)
                pen = gc.CreatePen(wx.GraphicsPenInfo(g).Width(12).Cap(wx.CAP_ROUND))
                gc.SetPen(pen)
                brush = gc.CreateBrush(wx.Brush(g))
                gc.SetBrush(brush)
                path = gc.CreatePath()
                path.AddRoundedRectangle(bar_x - pad//2, bar_y - pad//2, fill_w + pad, bar_h + pad, (bar_h+pad)/2)
                gc.FillPath(path)

            dc.SetBrush(wx.Brush(NEON))
            dc.SetPen(wx.Pen(NEON))
            dc.DrawRoundedRectangle(bar_x, bar_y, fill_w, bar_h, 10)

        # percentage text
        pct_text = f"{int(self.animated_frac * 100)}% completed"
        txt_font = wx.Font(16, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_BOLD)
        dc.SetFont(txt_font)
        dc.SetTextForeground(TEXT)
        dc.DrawText(pct_text, bar_x, bar_y + bar_h + 12)

        # Timeline box
        tl_y = bar_y + bar_h + 86
        tl_h = 140
        dc.SetBrush(wx.Brush(TIMELINE_BG))
        dc.SetPen(wx.Pen(TIMELINE_BORDER, 2))
        dc.DrawRoundedRectangle(bar_x, tl_y, bar_w, tl_h, 10)

        # draw hour ticks
        hour_font = wx.Font(11, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_NORMAL)
        dc.SetFont(hour_font)
        dc.SetTextForeground(wx.Colour(170, 190, 205))
        start_hour = 6
        end_hour = 22
        total_minutes = (end_hour - start_hour) * 60

        for hr in range(start_hour, end_hour + 1):
            rel = (hr - start_hour) / (end_hour - start_hour)
            x = int(bar_x + rel * bar_w)
            dc.SetPen(wx.Pen(wx.Colour(50, 65, 80)))
            dc.DrawLine(x, tl_y + tl_h, x, tl_y + tl_h + 8)
            if (hr - start_hour) % 2 == 0:
                s = f"{hr:02d}:00"
                tw, th = dc.GetTextExtent(s)
                dc.DrawText(s, x - tw//2, tl_y + tl_h + 10)

        # Draw sessions
        sessions = self._sessions_for_day(self.view_day)
        self.session_rects = []

        if not sessions:
            dc.SetFont(wx.Font(13, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_NORMAL))
            dc.SetTextForeground(wx.Colour(170, 190, 205))
            dc.DrawText("No sessions scheduled for this day. Add tasks from Tasks screen.", bar_x + 8, tl_y + 24)
            return

        now = datetime.now()
        now_minutes = now.hour * 60 + now.minute

        session_y = tl_y + 12
        session_h = 40

        for s in sessions:
            sm = s["start_m"]
            em = s["end_m"]
            if em <= sm:
                continue

            rel_s = (sm - start_hour * 60) / total_minutes
            rel_e = (em - start_hour * 60) / total_minutes
            sx = int(bar_x + rel_s * bar_w)
            ex = int(bar_x + rel_e * bar_w)
            sw = max(8, ex - sx)

            # determine state
            is_completed = s["completed"]
            is_overdue = (not is_completed) and (em < now_minutes)

            # colors & effects
            if is_completed:
                main_color = NEON
            elif is_overdue:
                # pulse factor from sine wave (0..1)
                pulse = (math.sin(self.pulse_phase) + 1.0) / 2.0  # 0..1
                pulse_factor = 1.0 + PULSE_AMPLITUDE * pulse
                main_color = OVERDUE_RED
            else:
                main_color = INCOMPLETE_GREY

            # Draw glow for overdue (multi-layer translucent rounded rects scaled by pulse)
            if is_overdue:
                pulse = (math.sin(self.pulse_phase) + 1.0) / 2.0  # 0..1
                # draw 3 halo layers with increasing blur and decreasing alpha
                for i, (pad, alpha_factor) in enumerate(((12, 0.14), (8, 0.24), (4, 0.36))):
                    a = int(255 * alpha_factor * (0.7 + 0.3 * pulse))
                    glow = wx.Colour(OVERDUE_RED.Red(), OVERDUE_RED.Green(), OVERDUE_RED.Blue(), a)
                    gc = wx.GraphicsContext.Create(dc)
                    pen = gc.CreatePen(wx.GraphicsPenInfo(glow).Width(12 + i*6).Cap(wx.CAP_ROUND))
                    gc.SetPen(pen)
                    brush = gc.CreateBrush(wx.Brush(glow))
                    gc.SetBrush(brush)
                    path = gc.CreatePath()
                    # expand the rect slightly using pad and pulse_factor
                    pad_scale = int(pad * (1.0 + PULSE_AMPLITUDE * pulse))
                    path.AddRoundedRectangle(sx - pad_scale//2, session_y - pad_scale//2,
                                             int(sw + pad_scale), int(session_h + pad_scale), (session_h + pad_scale)/2)
                    gc.FillPath(path)

            # Draw main rounded rectangle
            dc.SetBrush(wx.Brush(main_color))
            dc.SetPen(wx.Pen(main_color))
            dc.DrawRoundedRectangle(sx, session_y, sw, session_h, int(session_h/2))

            # draw mini clock icon for overdue (small circle + hands) on left edge of bar
            if is_overdue:
                clk_r = 10
                clk_cx = sx + 8
                clk_cy = session_y + session_h//2
                # outer circle (white border)
                dc.SetPen(wx.Pen(wx.Colour(255, 255, 255, 200)))
                dc.SetBrush(wx.Brush(wx.Colour(255, 255, 255, 40)))
                dc.DrawCircle(clk_cx, clk_cy, clk_r + 2)
                # inner circle (red)
                dc.SetPen(wx.Pen(OVERDUE_RED))
                dc.SetBrush(wx.Brush(OVERDUE_RED))
                dc.DrawCircle(clk_cx, clk_cy, clk_r)
                # clock hands (hour and minute)
                hand_len1 = 6
                hand_len2 = 9
                # hour hand (points slightly up-left)
                dc.SetPen(wx.Pen(wx.Colour(255, 255, 255), 2))
                dc.DrawLine(clk_cx, clk_cy, clk_cx - 3, clk_cy - hand_len1)
                # minute hand (points right)
                dc.DrawLine(clk_cx, clk_cy, clk_cx + hand_len2, clk_cy)

            # title label centered in bar
            dc.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_BOLD))
            dc.SetTextForeground(wx.Colour(230, 235, 240))
            title = s["title"]
            tw, th = dc.GetTextExtent(title)
            tx = sx + max(6, (sw - tw)//2)
            ty = session_y + (session_h - th)//2
            dc.DrawText(title, tx, ty)

            # clickable region (expand a bit vertically)
            rect = wx.Rect(sx - 4, session_y - 4, sw + 8, session_h + 12)
            self.session_rects.append((rect, s))

        # done painting

    # ----------------- public helpers -----------------
    def show(self):
        # keep API consistent — nothing special needed
        self.Refresh()
