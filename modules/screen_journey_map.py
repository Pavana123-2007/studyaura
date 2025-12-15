# modules/screen_journey_map.py
import wx
import csv
import os
import math
import time
from datetime import datetime, date, timedelta

# ---------------- Theme colours ----------------
BG = wx.Colour(12, 16, 22)
ISLAND = wx.Colour(22, 28, 36)
WATER = wx.Colour(6, 18, 30)
NEON = wx.Colour(0, 200, 255)
GLOW = wx.Colour(0, 200, 255)
LOCKED = wx.Colour(80, 90, 100)
COMPLETED = wx.Colour(120, 220, 140)
OVERLAY = wx.Colour(255, 255, 255, 20)
TEXT = wx.Colour(220, 230, 240)
BRIDGE = wx.Colour(60, 80, 100)
RAIN_COL = wx.Colour(140, 200, 255, 180)
STAR_COL = wx.Colour(255, 245, 200, 200)
XP_BAR_BG = wx.Colour(25, 30, 36)
XP_BAR_FG = wx.Colour(0, 200, 220)

# ---------------- Animation constants ----------------
TIMER_MS = 30
FLOAT_AMPLITUDE = 6
FIREWORK_LIFETIME = 1.4
FIREWORK_PARTICLES = 12

# ---------------- XP thresholds ----------------
LEVEL_THRESHOLDS = [0, 50, 150, 350, 700, 1200, 2000]

# ---------------- CSV helpers ----------------
def tasks_csv_path():
    base = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base, "data", "tasks.csv")

def milestones_csv_path():
    base = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base, "data", "milestones.csv")

def parse_date(s):
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            pass
    return None

def parse_time(s):
    s = (s or "").strip()
    try:
        h, m = map(int, s.split(":"))
        return h * 60 + m
    except Exception:
        return None

# ---------------- compute stats ----------------
def compute_stats():
    path = tasks_csv_path()
    stats = {
        "total_tasks": 0,
        "completed_tasks": 0,
        "dates_with_completed": set(),
        "total_minutes": 0,
        "per_day": {},
    }
    if not os.path.exists(path):
        return stats

    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                stats["total_tasks"] += 1
                completed = str(r.get("completed","")).strip().upper() == "TRUE"
                d = parse_date(r.get("date",""))
                if completed:
                    stats["completed_tasks"] += 1
                    if d:
                        stats["dates_with_completed"].add(d)
                        stats["per_day"][d] = stats["per_day"].get(d, 0) + 1
                start = parse_time(r.get("start",""))
                end = parse_time(r.get("end",""))
                if start is not None and end is not None and end > start:
                    stats["total_minutes"] += max(0, end - start)
    except Exception as e:
        print("compute_stats CSV error:", e)
    return stats

def compute_streak(dates_set):
    if not dates_set:
        return 0
    streak = 0
    today = date.today()
    cur = today
    while cur in dates_set:
        streak += 1
        cur -= timedelta(days=1)
    return streak

# ---------------- XP / Level helpers ----------------
def compute_xp(stats):
    return int(stats["completed_tasks"] * 10 + stats["total_minutes"] // 6)

def xp_to_level(xp):
    lvl = 0
    for i, t in enumerate(LEVEL_THRESHOLDS):
        if xp >= t:
            lvl = i
    next_thr = LEVEL_THRESHOLDS[min(len(LEVEL_THRESHOLDS)-1, lvl+1)]
    progress = (
        (xp - LEVEL_THRESHOLDS[lvl]) / max(1, next_thr - LEVEL_THRESHOLDS[lvl])
        if lvl < len(LEVEL_THRESHOLDS)-1 else 1.0
    )
    return lvl, next_thr, progress

# ---------------- Milestones CSV loader (Option B/C) ----------------
def ensure_default_milestones_file(path):
    default = [
        {"id":"m1","title":"First Steps","desc":"Complete 5 tasks","goal":"5","streak":"","minutes":""},
        {"id":"m2","title":"Getting Warm","desc":"Complete 10 tasks","goal":"10","streak":"","minutes":""},
        {"id":"m3","title":"Consistency","desc":"7-day streak","goal":"","streak":"7","minutes":""},
        {"id":"m4","title":"Committed","desc":"Complete 20 tasks","goal":"20","streak":"","minutes":""},
        {"id":"m5","title":"Time Master","desc":"Accumulate 30 study hours","goal":"","streak":"","minutes":"1800"},
        {"id":"m6","title":"Champion","desc":"Complete 50 tasks","goal":"50","streak":"","minutes":""},
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["id","title","desc","goal","streak","minutes"]
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in default:
                w.writerow(r)
    except Exception as e:
        print("Could not create default milestones.csv:", e)

def load_milestones_from_csv():
    path = milestones_csv_path()
    if not os.path.exists(path):
        ensure_default_milestones_file(path)
    milestones = []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                goal = None
                streak = None
                minutes = None
                g = str(r.get("goal","")).strip()
                s = str(r.get("streak","")).strip()
                m = str(r.get("minutes","")).strip()
                try:
                    if g != "":
                        goal = int(g)
                except Exception:
                    goal = None
                try:
                    if s != "":
                        streak = int(s)
                except Exception:
                    streak = None
                try:
                    if m != "":
                        minutes = int(m)
                except Exception:
                    minutes = None
                milestones.append({
                    "id": r.get("id") or f"m{len(milestones)+1}",
                    "title": r.get("title") or ("Milestone " + str(len(milestones)+1)),
                    "desc": r.get("desc") or "",
                    "goal": goal,
                    "streak": streak,
                    "minutes": minutes
                })
    except Exception as e:
        print("load_milestones_from_csv error:", e)
    return milestones

# ---------------- Journey Map Screen ----------------
class JourneyMapScreen(wx.Panel):
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


        # ---------- dynamic data ----------
        self.milestones = load_milestones_from_csv()
        self.stats = compute_stats()
        self.stats["streak"] = compute_streak(self.stats["dates_with_completed"])
        self.xp = compute_xp(self.stats)
        self.level, self.next_xp_thr, self.level_progress = xp_to_level(self.xp)

        # ---------- layout & state ----------
        self.nodes = []
        self.left_margin = 120
        self.node_spacing = 420
        self.zig_vertical = 120
        self.map_height = 700

        # view / pan
        self.view_x = 0
        self.dragging = False
        self.drag_start = None
        self.view_x_start = 0

        # ---------- effects (must initialize BEFORE building nodes) ----------
        self.fireworks = []
        self.weather = "none"

        # prepare nodes from milestones (safe to append fireworks now)
        self._build_nodes_from_milestones()

        # map width
        self.map_width = max(1800, len(self.nodes) * self.node_spacing + self.left_margin*2)

        # rain and avatar
        self._prepare_rain_particles()
        self.avatar_t = min(1.0, (self.xp / max(1, LEVEL_THRESHOLDS[-1])))

        # timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer, self.timer)
        self.timer.Start(TIMER_MS)

        # event bindings
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.SetFocus()

        # optional sounds
        self.sounds = {}
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sounds")
        try:
            if os.path.exists(assets_dir):
                self.sounds["levelup"] = self._load_sound(os.path.join(assets_dir, "levelup.wav"))
                self.sounds["unlock"] = self._load_sound(os.path.join(assets_dir, "unlock.wav"))
        except Exception:
            pass

    def _load_sound(self, path):
        if os.path.exists(path):
            try:
                s = wx.Sound(path)
                if s.IsOk():
                    return s
            except Exception:
                pass
        return None

    # ---------------- Build nodes from milestones ----------------
    def _build_nodes_from_milestones(self):
        self.nodes = []
        center_y = self.map_height // 2
        comp = self.stats.get("completed_tasks", 0)
        streak = self.stats.get("streak", 0)
        minutes = self.stats.get("total_minutes", 0)
        now = time.time()

        for i, m in enumerate(self.milestones):
            state = "locked"
            if m.get("goal") is not None:
                if comp >= m["goal"]:
                    state = "completed"
                elif comp > 0:
                    state = "unlocked"
            if m.get("streak") is not None:
                if streak >= m["streak"]:
                    state = "completed"
                elif streak > 0 and state != "completed":
                    state = "unlocked"
            if m.get("minutes") is not None:
                if minutes >= m["minutes"]:
                    state = "completed"
                elif minutes > 0 and state != "completed":
                    state = "unlocked"

            x = self.left_margin + i * self.node_spacing
            y_offset = -self.zig_vertical if (i % 2 == 0) else self.zig_vertical
            y = center_y + y_offset

            skin = ["tropical", "lava", "ice", "forest", "desert", "cloud"][i % 6]

            just_unlocked = False
            if state == "completed":
                if m.get("goal") and comp == m["goal"]:
                    just_unlocked = True
                if m.get("streak") and streak == m["streak"]:
                    just_unlocked = True
                if m.get("minutes") and minutes == m["minutes"]:
                    just_unlocked = True

            node = {
                "id": m.get("id"),
                "title": m.get("title"),
                "desc": m.get("desc"),
                "goal": m.get("goal"),
                "streak": m.get("streak"),
                "minutes": m.get("minutes"),
                "state": state,
                "just_unlocked": just_unlocked,
                "x": x,
                "y": y,
                "skin": skin
            }
            self.nodes.append(node)

            if just_unlocked:
                # safe: self.fireworks already exists
                self.fireworks.append({"x": x, "y": y - 30, "t": now})

    # ---------------- Rain prep ----------------
    def _prepare_rain_particles(self):
        self.rain = []
        w = max(600, int(self.map_width // 3))
        h = max(400, self.map_height)
        for i in range(80):
            self.rain.append({
                "x": int((i * 37) % max(200, w)),
                "y": int((i * 29) % max(200, h)),
                "speed": 200 + (i % 5) * 40
            })

    # ---------------- Timer tick ----------------
    def _on_timer(self, evt):
        dt = TIMER_MS / 1000.0
        if self.weather == "rain":
            w, h = self.GetSize()
            for p in self.rain:
                p["y"] += int(p["speed"] * dt)
                if p["y"] > h:
                    p["y"] = -10
                    p["x"] = int(time.time() * 31) % max(200, w)
        target_t = min(1.0, (self.xp / max(1, LEVEL_THRESHOLDS[-1])))
        self.avatar_t += (target_t - self.avatar_t) * 0.08
        self.Refresh()

    # ---------------- Mouse / keyboard ----------------
    def on_left_down(self, evt):
        self.dragging = True
        self.drag_start = evt.GetPosition()
        self.view_x_start = self.view_x
        self.CaptureMouse()

    def on_left_up(self, evt):
        if self.dragging:
            pos = evt.GetPosition()
            if self.HasCapture():
                self.ReleaseMouse()
            self.dragging = False
            if self.drag_start and (pos.x == self.drag_start.x and pos.y == self.drag_start.y):
                self._check_node_click(pos)

    def on_mouse_move(self, evt):
        if self.dragging and evt.Dragging() and evt.LeftIsDown():
            dx = evt.GetPosition().x - self.drag_start.x
            self.view_x = int(self.view_x_start - dx)
            self._clamp_view()
            self.Refresh()

    def on_mouse_wheel(self, evt):
        rot = evt.GetWheelRotation()
        delta = -rot // 120 * 80
        self.view_x += delta
        self._clamp_view()
        self.Refresh()

    def on_key_down(self, evt):
        k = evt.GetKeyCode()
        if k == wx.WXK_LEFT:
            self.view_x -= 200
        elif k == wx.WXK_RIGHT:
            self.view_x += 200
        elif k == ord('R'):
            self.weather = "rain" if self.weather != "rain" else "none"
        elif k == ord('S'):
            self.weather = "stars" if self.weather != "stars" else "none"
        self._clamp_view()
        self.Refresh()

    def _clamp_view(self):
        w, _ = self.GetSize()
        max_x = max(0, self.map_width - w + 80)
        if self.view_x < 0:
            self.view_x = 0
        if self.view_x > max_x:
            self.view_x = max_x

    def _check_node_click(self, pos):
        mx = pos.x + self.view_x
        my = pos.y
        for n in self.nodes:
            nx, ny = n["x"], n["y"]
            r = 66
            if (mx - nx) ** 2 + (my - ny) ** 2 <= r * r:
                self._on_node_activated(n)
                return

    def _on_node_activated(self, node):
        state = node["state"]
        dlg = wx.MessageDialog(
            self,
            f"{node['title']}\n\n{node['desc']}\n\nState: {state.upper()}",
            "Milestone",
            wx.OK | wx.CANCEL | wx.ICON_INFORMATION
        )
        res = dlg.ShowModal()
        dlg.Destroy()
        if state == "completed":
            if self.sounds.get("levelup"):
                self.sounds["levelup"].Play(wx.SOUND_ASYNC)
            wx.MessageBox(f"Congratulations — {node['title']} completed! 🎉", "Celebration", wx.OK | wx.ICON_INFORMATION)

    # ---------------- Drawing helpers ----------------
    def _skin_colors(self, skin):
        mapping = {
            "tropical": (wx.Colour(22,28,36), wx.Colour(24,40,56)),
            "lava": (wx.Colour(36,18,18), wx.Colour(56,22,22)),
            "ice": (wx.Colour(18,28,36), wx.Colour(34,44,66)),
            "forest": (wx.Colour(20,34,22), wx.Colour(32,50,36)),
            "desert": (wx.Colour(38,34,20), wx.Colour(56,48,24)),
            "cloud": (wx.Colour(28,30,36), wx.Colour(44,44,50)),
        }
        return mapping.get(skin, (ISLAND, ISLAND))

    def _draw_island(self, dc, x, y, wbox=220, hbox=120, float_offset=0, glow_alpha=0, skin="tropical"):
        # shadow
        dc.SetBrush(wx.Brush(wx.Colour(0,0,0,30)))
        dc.SetPen(wx.Pen(wx.Colour(0,0,0,40)))
        dc.DrawEllipse(int(x - wbox//2 - 8), int(y + hbox//2 + 6), int(wbox + 20), 32)

        # island body
        col1, col2 = self._skin_colors(skin)
        dc.SetBrush(wx.Brush(col1))
        dc.SetPen(wx.Pen(wx.Colour(0,0,0,40)))
        dc.DrawRoundedRectangle(int(x - wbox//2), int(y - hbox//2 + float_offset), int(wbox), int(hbox), 28)

        # overlay
        dc.SetBrush(wx.Brush(OVERLAY))
        dc.SetPen(wx.Pen(wx.Colour(0,0,0,0)))
        dc.DrawRoundedRectangle(int(x - wbox//2 + 10), int(y - hbox//2 + 10 + float_offset), int(wbox - 20), int(hbox - 30), 18)

        # little palm
        px = int(x + wbox//2 - 30)
        py = int(y - hbox//2 + 10 + float_offset)
        dc.SetPen(wx.Pen(wx.Colour(30, 180, 80)))
        dc.SetBrush(wx.Brush(wx.Colour(30, 180, 80)))
        dc.DrawCircle(px, py, 6)
        dc.DrawCircle(px+8, py-6, 5)
        dc.DrawCircle(px-8, py-6, 5)

        # animated wave ring (try GraphicsContext, fallback to DC)
        t = time.time() - getattr(self, "time0", time.time())
        g = wx.GraphicsContext.Create(dc)
        if g:
            wave_alpha = int(60 + 60 * (0.5 + 0.5 * math.sin(t*1.2 + x*0.01)))
            info = wx.GraphicsPenInfo(wx.Colour(0, 120, 160, wave_alpha)).Width(2).Cap(wx.CAP_ROUND)
            try:
                pen = g.CreatePen(info)
                g.SetPen(pen)
                path = g.CreatePath()
                path.AddCircle(x, y + hbox//2 - 6, int(wbox//2 + 6 + 6 * math.sin(t*1.8 + x*0.02)))
                g.StrokePath(path)
            except Exception:
                dc.SetPen(wx.Pen(wx.Colour(0, 120, 160, wave_alpha), 2))
                dc.SetBrush(wx.TRANSPARENT_BRUSH)
                dc.DrawCircle(x, y + hbox//2 - 6, int(wbox//2 + 6 + 6 * math.sin(t*1.8 + x*0.02)))
        else:
            dc.SetPen(wx.Pen(wx.Colour(0, 120, 160, 120), 2))
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawCircle(x, y + hbox//2 - 6, int(wbox//2 + 6 + 6 * math.sin(t*1.8 + x*0.02)))

    def _draw_bridge(self, dc, x1, y1, x2, y2):
        # straight bridge between islands, leaving margins so bridge meets island edges nicely
        dc.SetPen(wx.Pen(BRIDGE, 6))
        dc.SetBrush(wx.Brush(BRIDGE))
        start_x = int(x1 + 80)
        end_x = int(x2 - 80)
        dc.DrawLine(start_x, int(y1), end_x, int(y2))
        # draw simple planks
        if end_x > start_x + 6:
            segments = 4
            segw = (end_x - start_x) / segments
            for i in range(segments):
                px = int(start_x + i * segw)
                dc.DrawRectangle(px, int((y1 + y2) / 2 - 6), 6, 12)

    def _draw_trophy(self, dc, cx, cy, level="bronze", scale=1.0):
        if level == "bronze":
            col = wx.Colour(205, 127, 50)
        elif level == "silver":
            col = wx.Colour(192,192,192)
        else:
            col = wx.Colour(255, 215, 0)
        cw, ch = int(36*scale), int(28*scale)
        dc.SetBrush(wx.Brush(col))
        dc.SetPen(wx.Pen(wx.Colour(0,0,0,30)))
        dc.DrawRoundedRectangle(int(cx - cw//2), int(cy - ch//2 - 6), cw, ch, 8)
        dc.SetBrush(wx.Brush(wx.Colour(40,40,40)))
        dc.DrawRectangle(int(cx - 18*scale), int(cy + 10*scale), int(36*scale), int(10*scale))
        dc.SetPen(wx.Pen(col, 4))
        dc.DrawLine(int(cx - cw//2), int(cy - 6), int(cx - cw//2 - 12*scale), int(cy + 6*scale))
        dc.DrawLine(int(cx + cw//2), int(cy - 6), int(cx + cw//2 + 12*scale), int(cy + 6*scale))
    # -----------------------------------------------------
    # BACK NAVIGATION
    # -----------------------------------------------------
    def go_back(self, event):
        if self.back_callback:
            self.back_callback()  # Return to tasks_screen.py

    # ---------------- Main paint ----------------
    def on_paint(self, evt):
        if not hasattr(self, "time0"):
            self.time0 = time.time()

        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        w, h = self.GetSize()
        # Keep the back button updated during all repaints
        self.back_btn.Refresh()


        # background
        dc.SetBrush(wx.Brush(WATER))
        dc.SetPen(wx.Pen(WATER))
        dc.DrawRectangle(0, 0, w, h)

        # title & summary
        title_font = wx.Font(22, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_BOLD)
        dc.SetFont(title_font)
        dc.SetTextForeground(TEXT)
        dc.DrawText("🗺️ Study Journey — Floating Islands", 24, 45)

        sub_font = wx.Font(10, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_NORMAL)
        dc.SetFont(sub_font)
        stats_str = f"Completed tasks: {self.stats['completed_tasks']}  •  Streak: {self.stats['streak']} days  •  Study hours: {int(self.stats['total_minutes']//60)}  •  XP: {self.xp}  •  Level: {self.level}"
        dc.DrawText(stats_str, 24, 78)

        ox = -self.view_x

        # draw bridges first to appear under islands
        for i in range(len(self.nodes)-1):
            n1 = self.nodes[i]
            n2 = self.nodes[i+1]
            x1, y1 = int(n1["x"] + ox), int(n1["y"])
            x2, y2 = int(n2["x"] + ox), int(n2["y"])
            if x2 < -300 or x1 > w + 300:
                continue
            self._draw_bridge(dc, x1, y1, x2, y2)

        # draw islands and UI elements
        t = time.time() - self.time0
        self.session_rects = []
        for i, n in enumerate(self.nodes):
            float_offset = int(math.sin(t*0.9 + i*0.5) * FLOAT_AMPLITUDE)
            x = int(n["x"] + ox)
            y = int(n["y"] + float_offset)
            if x < -300 or x > w + 300:
                continue

            glow_alpha = 0
            if n["state"] == "unlocked":
                glow_alpha = int(100 + 100 * (0.5 + 0.5 * math.sin(t*1.6 + i)))
            elif n["state"] == "completed":
                glow_alpha = 160

            self._draw_island(dc, x, y, wbox=240, hbox=120, float_offset=float_offset, glow_alpha=glow_alpha, skin=n.get("skin","tropical"))

            base_r = 44
            if n["state"] == "locked":
                base_col = LOCKED
            elif n["state"] == "completed":
                base_col = COMPLETED
            else:
                base_col = NEON

            if n["state"] != "locked":
                pulse = (math.sin(t*1.8 + i) + 1.0) / 2.0
                glow_w = 12 + int(6 * pulse)
                gc = wx.GraphicsContext.Create(dc)
                if gc:
                    gcol = wx.Colour(base_col.Red(), base_col.Green(), base_col.Blue(), int(90 * (0.6 + 0.4 * pulse)))
                    info = wx.GraphicsPenInfo(gcol).Width(glow_w).Cap(wx.CAP_ROUND)
                    try:
                        pen = gc.CreatePen(info)
                        gc.SetPen(pen)
                        path = gc.CreatePath()
                        path.AddCircle(x, int(y - 24), base_r + glow_w//3)
                        gc.StrokePath(path)
                    except Exception:
                        dc.SetPen(wx.Pen(gcol, glow_w))
                        dc.SetBrush(wx.TRANSPARENT_BRUSH)
                        dc.DrawCircle(x, int(y - 24), base_r + glow_w//3)

            dc.SetBrush(wx.Brush(base_col))
            dc.SetPen(wx.Pen(wx.Colour(0,0,0,30)))
            dc.DrawCircle(x, int(y - 24), base_r)

            # trophy + label
            lvl = "gold" if n["state"] == "completed" else "bronze"
            self._draw_trophy(dc, x, int(y - 28), level=("silver" if i%3==1 else lvl), scale=1.0 if n["state"]=="completed" else 0.9)

            txt_font = wx.Font(11, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_BOLD)
            dc.SetFont(txt_font)

            # Always purple for all milestone titles
            dc.SetTextForeground(wx.Colour(170, 80, 255))

            title = n["title"]
            tw, th = dc.GetTextExtent(title)
            dc.DrawText(title, int(x - tw//2), int(y + 30))

            badge = n.get("goal") or n.get("streak") or (n.get("minutes") and f"{int(n['minutes']//60)}h")
            if badge:
                btxt = str(badge)
                bw, bh = dc.GetTextExtent(btxt)
                dc.SetBrush(wx.Brush(wx.Colour(20,24,32)))
                dc.SetPen(wx.Pen(wx.Colour(70,70,80)))
                dc.DrawRoundedRectangle(int(x - 28), int(y + 8), int(bw + 12), int(bh + 8), 6)
                dc.SetTextForeground(wx.Colour(170,190,210))
                dc.DrawText(btxt, int(x - 28 + 6), int(y + 10))

            if n.get("goal"):
                completed = self.stats["completed_tasks"]
                prog = min(1.0, completed / max(1, n["goal"]))
                pbw = 120
                pbx = x - pbw//2
                pby = y + 56
                dc.SetBrush(wx.Brush(wx.Colour(40,48,56)))
                dc.SetPen(wx.Pen(wx.Colour(50,60,70)))
                dc.DrawRoundedRectangle(int(pbx), int(pby), pbw, 12, 6)
                dc.SetBrush(wx.Brush(wx.Colour(0,200,220)))
                dc.SetPen(wx.Pen(wx.Colour(0,200,220)))
                dc.DrawRoundedRectangle(int(pbx+2), int(pby+2), int((pbw-4)*prog), 8, 4)
                pct_txt = f"{int(prog*100)}%"
                dtw, dth = dc.GetTextExtent(pct_txt)
                dc.SetTextForeground(TEXT)
                dc.DrawText(pct_txt, int(x - dtw//2), int(pby - dth - 2))

            rect = wx.Rect(int(x - base_r), int(y - 24 - base_r), int(base_r*2), int(base_r*2 + 40))
            self.session_rects.append((rect, n))

        # avatar along path
        avatar_x, avatar_y = self._avatar_position(ox)
        self._draw_avatar(dc, avatar_x, avatar_y)

        # fireworks
        nowt = time.time()
        new_f = []
        for f in self.fireworks:
            age = nowt - f["t"]
            if age > FIREWORK_LIFETIME:
                continue
            prog = age / FIREWORK_LIFETIME
            for p in range(FIREWORK_PARTICLES):
                ang = p * (2*math.pi / FIREWORK_PARTICLES) + prog * 4.0
                r = 6 + prog * 40
                px = int(f["x"] + math.cos(ang) * r - self.view_x)
                py = int(f["y"] + math.sin(ang) * r)
                alpha = int(255 * (1 - prog))
                col = wx.Colour(255, 200, 80, max(40, alpha))
                dc.SetPen(wx.Pen(col))
                dc.SetBrush(wx.Brush(col))
                dc.DrawCircle(px, py, max(2, int(3*(1-prog))))
            new_f.append(f)
        self.fireworks = new_f

        # weather overlay
        if self.weather == "rain":
            for p in self.rain:
                dc.SetPen(wx.Pen(RAIN_COL, 2))
                dc.DrawLine(p["x"], p["y"], p["x"]+4, p["y"]+12)
        elif self.weather == "stars":
            for i in range(80):
                sx = (i * 43 + int(time.time()*40)) % (w+200) - 50
                sy = (i * 73) % (h//2)
                dc.SetPen(wx.Pen(STAR_COL, 1))
                dc.SetBrush(wx.Brush(STAR_COL))
                dc.DrawCircle(int(sx), int(sy), (i%3==0 and 2) or 1)

        # bottom UI
        self._draw_weekly_timeline(dc, w, h)
        self._draw_xp_bar(dc, 24, h - 48, w - 48)

    def _avatar_position(self, ox):
        if not self.nodes:
            return 200, 200
        total = len(self.nodes) - 1
        pos = self.avatar_t * total
        idx = int(pos)
        frac = pos - idx
        idx = min(idx, len(self.nodes)-2)
        n1 = self.nodes[idx]
        n2 = self.nodes[idx+1]
        x = int((n1["x"]*(1-frac) + n2["x"]*frac) - self.view_x)
        y = int((n1["y"]*(1-frac) + n2["y"]*frac) - 40 + math.sin(time.time()*2 + idx)*6)
        return x, y

    def _draw_avatar(self, dc, x, y):
        dc.SetBrush(wx.Brush(wx.Colour(255,210,160)))
        dc.SetPen(wx.Pen(wx.Colour(0,0,0,30)))
        dc.DrawCircle(int(x), int(y), 16)
        dc.SetBrush(wx.Brush(wx.Colour(40,120,170)))
        dc.DrawRoundedRectangle(int(x-10), int(y+10), 20, 14, 6)

    def _draw_weekly_timeline(self, dc, w, h):
        base_x = 24
        base_y = h - 140
        dc.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_NORMAL))
        dc.SetTextForeground(wx.Colour(170,180,190))
        dc.DrawText("Last 7 days", base_x, base_y - 20)
        arr = []
        today = date.today()
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            arr.append(self.stats["per_day"].get(d, 0))
        maxv = max(1, max(arr))
        bw = 28
        gap = 10
        for i, v in enumerate(arr):
            bx = base_x + i*(bw+gap)
            bh = int((v / maxv) * 60)
            dc.SetBrush(wx.Brush(wx.Colour(30,40,50)))
            dc.SetPen(wx.Pen(wx.Colour(40,50,60)))
            dc.DrawRoundedRectangle(bx, base_y, bw, 60, 6)
            dc.SetBrush(wx.Brush(wx.Colour(0,200,220)))
            dc.DrawRoundedRectangle(bx+4, base_y+60-bh+4, bw-8, bh-8 if bh>8 else 0, 4)
            daytxt = (today - timedelta(days=6-i)).strftime("%a")
            dc.SetTextForeground(wx.Colour(150,160,170))
            dc.DrawText(daytxt, bx, base_y + 66)

    def _draw_xp_bar(self, dc, x, y, full_w):
        bar_h = 18
        dc.SetBrush(wx.Brush(XP_BAR_BG))
        dc.SetPen(wx.Pen(XP_BAR_BG))
        dc.DrawRoundedRectangle(int(x), int(y), int(full_w), bar_h, 8)
        fill_w = int(full_w * (self.level_progress if self.level < len(LEVEL_THRESHOLDS)-1 else 1.0))
        dc.SetBrush(wx.Brush(XP_BAR_FG))
        dc.SetPen(wx.Pen(XP_BAR_FG))
        dc.DrawRoundedRectangle(int(x+2), int(y+2), int(max(4, fill_w-4)), int(bar_h-4), 6)
        txt = f"Level {self.level}  •  XP {self.xp}/{self.next_xp_thr}"
        dc.SetTextForeground(TEXT)
        dc.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, 0, wx.FONTWEIGHT_BOLD))
        tw, th = dc.GetTextExtent(txt)
        dc.DrawText(txt, int(x + 8), int(y - th - 4))

    # ---------------- public refresh API ----------------
    def refresh_stats_and_nodes(self):
        # reload stats
        self.stats = compute_stats()
        self.stats["streak"] = compute_streak(self.stats["dates_with_completed"])
        self.xp = compute_xp(self.stats)
        self.level, self.next_xp_thr, self.level_progress = xp_to_level(self.xp)

        # reload milestones (dynamic)
        self.milestones = load_milestones_from_csv()

        # rebuild nodes (keeps visual layout consistent)
        self._build_nodes_from_milestones()

        # recompute map width and rain
        self.map_width = max(1800, len(self.nodes) * self.node_spacing + self.left_margin*2)
        self._prepare_rain_particles()

        # schedule fireworks for completed nodes
        now = time.time()
        for n in self.nodes:
            if n["state"] == "completed":
                self.fireworks.append({"x": n["x"], "y": n["y"] - 30, "t": now})
        self.Refresh()
