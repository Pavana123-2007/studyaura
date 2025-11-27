# modules/analytics_window.py  (FINAL — neon + glassmorphism + smooth animations)
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageFont
import os
import threading

# chart functions (must exist)
from analytics.analytics_functions import (
    tasks_per_subject_chart,
    completion_progress_chart,
    priority_distribution_chart,
)

# -------------------------
# Helpers: gradient + glass
# -------------------------
def make_vert_gradient(size, top_color=(18, 12, 31), bottom_color=(12, 34, 63)):
    w, h = size
    img = Image.new("RGB", (w, h), top_color)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def make_glass_image(size, radius=20, opacity=180, blur_radius=6, tint=(255, 255, 255)):
    """Return an Image (RGBA) of a frosted glass rounded rectangle with slight blur."""
    w, h = size
    base = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    rect_fill = (tint[0], tint[1], tint[2], opacity)
    draw.rounded_rectangle((0, 0, w, h), radius=radius, fill=rect_fill)

    highlight = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    dh = ImageDraw.Draw(highlight)
    dh.rounded_rectangle((4, 4, w - 4, h - 4), radius=max(1, radius - 4), fill=(255, 255, 255, 16))

    composed = Image.alpha_composite(base, overlay)
    composed = Image.alpha_composite(composed, highlight)
    composed = composed.filter(ImageFilter.GaussianBlur(blur_radius))
    return composed


# -------------------------
# Neon Button (Canvas-based)
# -------------------------
class NeonButton(tk.Canvas):
    """
    Neon-style rounded button with hover/click animations.
    Non-blocking animations with `after`.
    """
    def __init__(self, master, text, command=None, bg="#08192b", fg="#e9f5ff", neon="#7cf7ff",
                 width=200, height=48, radius=12, glow_strength=12, font=("Segoe UI", 11, "bold")):
        parent_bg = master.cget("bg") if hasattr(master, "cget") else ""
        if not parent_bg:
            parent_bg = "#0f1724"
        super().__init__(master, width=width, height=height, highlightthickness=0, bg=parent_bg)
        self._width, self._height = width, height
        self.radius = radius
        self.text = text
        self.command = command
        self.base_bg = bg
        self.fg = fg
        self.neon = neon
        self.glow_strength = glow_strength
        self.font = font
        self._scale = 1.0
        self._hover = False
        self._pressed = False
        self._draw()  # initial draw

        # event bindings
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _draw(self, scale=1.0, glow_alpha=120):
        """Draw button using canvas primitives. scale is float; glow_alpha controls glow opacity."""
        self.delete("all")
        w, h = int(self._width * scale), int(self._height * scale)
        x0 = (self._width - w) // 2
        y0 = (self._height - h) // 2
        x1 = x0 + w
        y1 = y0 + h
        r = int(self.radius * scale)

        # glow: approximate by drawing an outline
        try:
            self.create_rounded_rect(x0 - 3, y0 - 3, x1 + 3, y1 + 3, r + 3, fill="", outline=self.neon, width=2)
        except Exception:
            self.create_rectangle(x0 - 3, y0 - 3, x1 + 3, y1 + 3, outline=self.neon)

        # main rounded rect (button background)
        self.create_rounded_rect(x0, y0, x1, y1, r, fill=self.base_bg, outline="")

        # inner neon border (thin)
        self.create_rounded_rect(x0 + 2, y0 + 2, x1 - 2, y1 - 2, max(1, r - 2), fill="", outline=self.neon, width=1)

        # text
        self.create_text(self._width // 2, self._height // 2, text=self.text, fill=self.fg, font=self.font)

    def create_rounded_rect(self, x0, y0, x1, y1, r, **kwargs):
        """Draw a rounded rectangle with rectangles + ovals (portable)."""
        try:
            self.create_rectangle(x0 + r, y0, x1 - r, y1, **kwargs)
            self.create_rectangle(x0, y0 + r, x1, y1 - r, **kwargs)
            self.create_oval(x0, y0, x0 + 2 * r, y0 + 2 * r, **kwargs)
            self.create_oval(x1 - 2 * r, y0, x1, y0 + 2 * r, **kwargs)
            self.create_oval(x0, y1 - 2 * r, x0 + 2 * r, y1, **kwargs)
            self.create_oval(x1 - 2 * r, y1 - 2 * r, x1, y1, **kwargs)
        except Exception:
            self.create_rectangle(x0, y0, x1, y1, **kwargs)

    # ---- animation logic (non-blocking) ----
    def _on_enter(self, e=None):
        self._hover = True
        self._animate_scale(target=1.04, steps=6)

    def _on_leave(self, e=None):
        self._hover = False
        self._animate_scale(target=1.0, steps=6)

    def _on_press(self, e=None):
        self._pressed = True
        self._animate_scale(target=0.97, steps=4)
        self._animate_glow(glow_alpha=200, steps=4)

    def _on_release(self, e=None):
        if self._pressed and callable(self.command):
            threading.Thread(target=self.command, daemon=True).start()
        self._pressed = False
        target = 1.04 if self._hover else 1.0
        self._animate_scale(target=target, steps=6)
        self._animate_glow(glow_alpha=120, steps=6)

    def _animate_scale(self, target=1.0, steps=6):
        start = self._scale
        delta = (target - start) / max(1, steps)
        def step(i=0):
            nonlocal start
            if i >= steps:
                self._scale = target
                self._draw(scale=self._scale)
                return
            start += delta
            self._scale = start
            self._draw(scale=self._scale)
            self.after(12, lambda: step(i + 1))
        step(0)

    def _animate_glow(self, glow_alpha=120, steps=6):
        def step(i=0):
            if i >= steps:
                self._draw(scale=self._scale, glow_alpha=glow_alpha)
                return
            a = int(glow_alpha * (i + 1) / steps)
            self._draw(scale=self._scale, glow_alpha=a)
            self.after(10, lambda: step(i + 1))
        step(0)


# -------------------------
# Analytics Window (Main)
# -------------------------
class AnalyticsWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("📊 StudyAura — Analytics")
        self.geometry("980x660")
        self.resizable(False, False)

        # create gradient background image and set
        grad_img = make_vert_gradient((980, 660), top_color=(18, 12, 31), bottom_color=(12, 34, 63))
        self._bg_photo = ImageTk.PhotoImage(grad_img)
        bg_label = tk.Label(self, image=self._bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # floating animated light bar (neon accent)
        self._create_light_bar()

        # Title & subtitle (use semi-transparent panel for readability)
        self._create_header()

        # left column for neon buttons
        self.left_frame = tk.Frame(self, bg="#0f1724", width=240, height=520)
        self.left_frame.place(x=20, y=120)

        # create glass panel for display area
        self._create_display_panel()

        # button palette (neon colors)
        palette = [
            ("Tasks per Subject", {"bg": "#08192b", "fg": "#e9f5ff", "neon": "#7cf7ff"}),
            ("Completion Progress", {"bg": "#082012", "fg": "#eaffef", "neon": "#7bffca"}),
            ("Priority Distribution", {"bg": "#120824", "fg": "#f0f2ff", "neon": "#a7caff"}),
            ("Save Latest Charts", {"bg": "#2a0b0b", "fg": "#fff0f0", "neon": "#ff9aa2"}),
        ]

        self.buttons = []
        for i, (label_text, color_spec) in enumerate(palette):
            btn = NeonButton(
                self.left_frame,
                text=label_text,
                command=lambda t=label_text: self.on_action(t),
                bg=color_spec["bg"],
                fg=color_spec["fg"],
                neon=color_spec["neon"],
                width=200,
                height=50,
                radius=14,
                glow_strength=14,
                font=("Segoe UI", 11, "bold"),
            )
            # place with staggered y and small slide-in animation
            y = 10 + i * 64
            btn.place(x=320, y=y)  # start off-screen (to the right)
            self.buttons.append(btn)
            self.after(80 * i, lambda b=btn, yy=y: self._slide_in(b, target_x=20, y=yy))

        # thumbnail frame inside display panel
        self.thumb_frame = tk.Frame(self.display_panel, bg="#ffffff", width=660, height=64)
        self.thumb_frame.place(x=10, y=440)

        # image cache to keep PhotoImage references
        self._img_cache = {}

        # initial placeholder
        self.show_placeholder("Click a neon button to generate a chart")

    # -------------------------
    # UI creation helpers
    # -------------------------
    def _create_light_bar(self):
        # a thin animated gradient bar at top (neon accent)
        bar = tk.Canvas(self, width=900, height=6, bg="#0f1724", highlightthickness=0)
        bar.place(x=40, y=96)
        colors = ["#7cf7ff", "#a7caff", "#ff9aa2", "#7bffca"]
        rects = []
        w = 220
        for i, c in enumerate(colors):
            rect = bar.create_rectangle(i * w, 0, i * w + w, 6, fill=c, outline=c)
            rects.append(rect)

        def animate_shift():
            for r in rects:
                bar.move(r, -6, 0)
            coords = bar.coords(rects[0])
            if coords and coords[2] <= 0:
                bar.move(rects[0], len(colors) * w, 0)
                rects.append(rects.pop(0))
            bar.after(60, animate_shift)

        bar.after(100, animate_shift)

    def _create_header(self):
        # glass header panel
        header_img = make_glass_image((860, 84), radius=18, opacity=140, blur_radius=6, tint=(255, 255, 255))
        self._header_photo = ImageTk.PhotoImage(header_img)
        header_lbl = tk.Label(self, image=self._header_photo, bd=0)
        header_lbl.place(x=80, y=18)

        title = tk.Label(self, text="📊 Study Analytics", font=("Segoe UI", 18, "bold"), bg="#0f1724", fg="#f8fafc")
        title.place(x=120, y=30)
        subtitle = tk.Label(self, text="Neon + Glassmorphism · Smooth animations", font=("Segoe UI", 10), bg="#0f1724", fg="#dfe7f3")
        subtitle.place(x=120, y=56)

    def _create_display_panel(self):
        # create a glass image for the main display area and place it
        glass_img = make_glass_image((700, 520), radius=20, opacity=190, blur_radius=8, tint=(255, 255, 255))
        self._glass_photo = ImageTk.PhotoImage(glass_img)
        self.display_panel = tk.Label(self, image=self._glass_photo, bd=0)
        self.display_panel.place(x=240, y=110)

        # inner frame to host the chart and thumbnails
        self.chart_holder = tk.Frame(self.display_panel, bg="#ffffff", width=660, height=420)
        self.chart_holder.place(x=20, y=10)

        # label that will show the chart (PhotoImage)
        self.chart_label = tk.Label(self.chart_holder, bg="#ffffff", bd=0)
        self.chart_label.place(x=0, y=0, width=660, height=420)

    # -------------------------
    # Animations
    # -------------------------
    def _slide_in(self, widget, target_x=20, y=10, steps=10):
        start_x = widget.winfo_x()
        dx = (target_x - start_x) / max(1, steps)
        def step(i=0):
            if i >= steps:
                widget.place_configure(x=target_x, y=y)
                return
            widget.place_configure(x=int(start_x + dx * i), y=y)
            widget.after(14, lambda: step(i + 1))
        step(0)

    def _fade_in_image(self, pil_img, duration=220, steps=12):
        base = pil_img.convert("RGBA").resize((660, 420))
        blank = Image.new("RGBA", base.size, (255, 255, 255, 0))
        frames = []
        for i in range(steps):
            alpha = int(255 * (i + 1) / steps)
            frame = Image.new("RGBA", base.size, (255, 255, 255, 0))
            overlay = base.copy()
            overlay.putalpha(alpha)
            frame = Image.alpha_composite(blank, overlay)
            frames.append(ImageTk.PhotoImage(frame))

        def play(i=0):
            if i >= len(frames):
                final = ImageTk.PhotoImage(base.convert("RGB"))
                self._img_cache["last"] = final
                self.chart_label.config(image=final)
                return
            self.chart_label.config(image=frames[i])
            self._img_cache[f"fade_{i}"] = frames[i]
            self.chart_label.update_idletasks()
            self.chart_label.after(int(duration / steps), lambda: play(i + 1))

        play(0)

    # -------------------------
    # Placeholders & thumbnails
    # -------------------------
    def show_placeholder(self, text):
        w, h = 660, 420
        img = Image.new("RGB", (w, h), (245, 247, 250))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((6, 6, w - 6, h - 6), radius=14, fill=(255, 255, 255))
        try:
            f = ImageFont.truetype("arial.ttf", 18)
        except Exception:
            f = ImageFont.load_default()
        d.multiline_text((w // 2, h // 2), text, fill=(90, 95, 105), anchor="mm", align="center", font=f)
        tk_img = ImageTk.PhotoImage(img)
        self._img_cache["placeholder"] = tk_img
        self.chart_label.config(image=tk_img)

    def _add_thumbnail(self, path):
        try:
            img = Image.open(path)
            img.thumbnail((100, 64))
            thumb = ImageTk.PhotoImage(img)
            key = f"thumb_{len(self._img_cache)}"
            self._img_cache[key] = thumb
            lbl = tk.Label(self.thumb_frame, image=thumb, bd=1, relief="solid", cursor="hand2")
            lbl.pack(side="left", padx=6)
            lbl.bind("<Button-1>", lambda e, p=path: self._display_chart(p))
        except Exception:
            pass

    # -------------------------
    # Chart generation + display
    # -------------------------
    def on_action(self, action_text):
        if action_text == "Tasks per Subject":
            self._run_chart(tasks_per_subject_chart)
        elif action_text == "Completion Progress":
            self._run_chart(completion_progress_chart)
        elif action_text == "Priority Distribution":
            self._run_chart(priority_distribution_chart)
        elif action_text == "Save Latest Charts":
            threading.Thread(target=self._regen_all, daemon=True).start()

    def _regen_all(self):
        for b in self.buttons:
            b._animate_glow(glow_alpha=200, steps=4)
        tasks_per_subject_chart()
        completion_progress_chart()
        priority_distribution_chart()
        for b in self.buttons:
            b._animate_glow(glow_alpha=120, steps=4)

    def _run_chart(self, chart_func):
        def worker():
            try:
                path = chart_func()
                self.after(0, lambda p=path: self._display_chart(p))
            except Exception as e:
                print("Chart generation error:", e)
        threading.Thread(target=worker, daemon=True).start()

    def _display_chart(self, path):
        try:
            pil_img = Image.open(path).convert("RGB").resize((660, 420))
            self._fade_in_image(pil_img, duration=240, steps=10)
            self._add_thumbnail(path)
        except Exception:
            # fallback quick display
            try:
                tkimg = ImageTk.PhotoImage(Image.open(path).resize((660, 420)))
                self._img_cache[path] = tkimg
                self.chart_label.config(image=tkimg)
                self._add_thumbnail(path)
            except Exception as e:
                print("Display chart error:", e)
