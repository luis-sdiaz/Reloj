"""Clock face "Mebus" — vector drawing with pycairo.

Clean vector clock: bezel, dial, subdials and three hands. Render at
2x and downsample to keep output crisp. Comments shortened.
"""
from __future__ import annotations

import math
import time
import random
import tkinter as tk
from typing import Optional, Tuple, Iterable

import cairo
from PIL import Image, ImageTk
from datetime import datetime
import pytz


def _surface_to_pil(surface: cairo.ImageSurface) -> Image.Image:
    buf = surface.get_data()
    w = surface.get_width()
    h = surface.get_height()
    return Image.frombuffer("RGBA", (w, h), buf, "raw", "BGRA", 0, 1)


class ClockFace(tk.Frame):
    def __init__(self, master: tk.Misc, settings=None, hands: Optional[Iterable] = None, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self.settings = settings

        # Canvas size
        self.width = 640
        self.height = 640
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, highlightthickness=0, bg="#ffffff")
        self.canvas.pack(expand=True, fill=tk.BOTH)

        # Geometry
        self.center_x = self.width / 2.0
        self.center_y = self.height / 2.0
        self._global_scale = 0.82
        self.clock_radius = min(self.width, self.height) * 0.5 * self._global_scale

        # Subdial state
        self._h_value = 50.0
        self._t_value = 20.0

        # Image refs for Tk
        self._image_id: Optional[int] = None
        self.image_ref: Optional[ImageTk.PhotoImage] = None

        # compute positions
        self._compute_subdial_positions()

        # Start animation loop
        self.after(50, self._anim_tick)

    def _compute_subdial_positions(self) -> None:
        cx, cy = self.center_x, self.center_y
        r = self.clock_radius
        # I position subdials slightly inward for spacing
        offset = r * 0.55 * 0.90 * 0.90
        # angles for 8 and 4 o'clock
        self._left_ang = math.radians(240 - 90)
        self._right_ang = math.radians(120 - 90)
        self._sub_r = r * 0.165
        self._h_cx = cx + math.cos(self._left_ang) * offset
        # nudge up to avoid rim collision
        y_nudge = r * 0.06
        self._h_cy = cy + math.sin(self._left_ang) * offset - y_nudge
        self._t_cx = cx + math.cos(self._right_ang) * offset
        self._t_cy = cy + math.sin(self._right_ang) * offset - y_nudge

    # value mappings (smooth oscillation)
    def _map_time_to_humidity(self, now: float) -> float:
        # soft oscillation 20..80
        period = 14.0
        return 50.0 + 30.0 * math.sin(2.0 * math.pi * (now / period))

    def _map_time_to_temp(self, now: float) -> float:
        # soft oscillation 15..28
        period = 18.0
        mean = (15.0 + 28.0) / 2.0
        amp = (28.0 - 15.0) / 2.0
        return mean + amp * math.sin(2.0 * math.pi * (now / period) + 0.7)

    def _draw_baton_hand(self, ctx: cairo.Context, length: float, half_width: float) -> None:
        # simple baton along +X; uses current source for fill/stroke
        back = max(2.0, length * 0.02)
        ctx.new_path()
        ctx.move_to(-back, -half_width)
        ctx.line_to(length, -half_width)
        ctx.arc(length, 0, half_width, -math.pi / 2.0, math.pi / 2.0)
        ctx.line_to(-back, half_width)
        ctx.close_path()
        ctx.fill_preserve()
        # use a smaller stroke relative to half_width
        ctx.set_line_width(max(0.35, half_width * 0.10))
        ctx.stroke()

    def _hex_to_rgb(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert #RRGGBB to normalized 0..1 RGB tuple."""
        if not hex_color:
            return (0.04, 0.66, 0.86)
        c = hex_color.lstrip('#')
        try:
            r = int(c[0:2], 16) / 255.0
            g = int(c[2:4], 16) / 255.0
            b = int(c[4:6], 16) / 255.0
            return (r, g, b)
        except Exception:
            return (0.04, 0.66, 0.86)

    def _draw_center_cap(self, ctx: cairo.Context, radius: float) -> None:
        grad = cairo.RadialGradient(-radius * 0.15, -radius * 0.15, 1, 0, 0, radius)
        grad.add_color_stop_rgb(0.0, 0.96, 0.96, 0.96)
        grad.add_color_stop_rgb(1.0, 0.78, 0.78, 0.79)
        ctx.set_source(grad)
        ctx.arc(0, 0, radius, 0, 2 * math.pi)
        ctx.fill()

    def _draw_bezel_and_dial(self, ctx: cairo.Context, cx: float, cy: float, r: float) -> None:
        ctx.save()
        ctx.translate(cx, cy)
        bezel = cairo.RadialGradient(-r * 0.05, -r * 0.05, r * 0.02, 0, 0, r * 1.08)
        bezel.add_color_stop_rgb(0.0, 0.98, 0.98, 0.99)
        bezel.add_color_stop_rgb(0.4, 0.78, 0.79, 0.81)
        bezel.add_color_stop_rgb(0.8, 0.56, 0.57, 0.59)
        bezel.add_color_stop_rgb(1.0, 0.88, 0.89, 0.90)
        ctx.set_source(bezel)
        ctx.arc(0, 0, r * 1.06, 0, 2 * math.pi)
        ctx.fill()
        # thin dark contour for depth
        ctx.set_source_rgb(0.14, 0.14, 0.14)
        ctx.set_line_width(max(1.0, r * 0.009))
        ctx.arc(0, 0, r * 1.06, 0, 2 * math.pi)
        ctx.stroke()
        # dial fill
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.arc(0, 0, r * 0.92, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()

    def _draw_main_ticks_and_numerals(self, ctx: cairo.Context, cx: float, cy: float, r: float) -> None:
        ctx.save()
        ctx.translate(cx, cy)
        # ticks
        for i in range(60):
            deg = i * 6
            th = math.radians(deg - 90)
            outer = r * 0.86
            inner = r * (0.78 if (i % 5 == 0) else 0.81)
            if i % 5 == 0:
                ctx.set_source_rgb(0.06, 0.06, 0.06)
                ctx.set_line_width(max(1.0, r * 0.012))
            else:
                ctx.set_source_rgb(0.12, 0.12, 0.12)
                ctx.set_line_width(max(0.5, r * 0.003))
            ctx.move_to(math.cos(th) * inner, math.sin(th) * inner)
            ctx.line_to(math.cos(th) * outer, math.sin(th) * outer)
            ctx.stroke()
        # numerals 1..12 using serif
        try:
            ctx.select_font_face("Times New Roman", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        except Exception:
            ctx.select_font_face("Serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        for n in range(1, 13):
            # remove numerals 4 and 8 to avoid collision with subdials
            if n in (4, 8):
                continue
            angle = math.radians(n * 30 - 90)
            nx = math.cos(angle) * r * 0.66
            ny = math.sin(angle) * r * 0.66
            if n in (12, 3, 6, 9):
                ctx.set_font_size(r * 0.12)
            else:
                ctx.set_font_size(r * 0.095)
            s = str(n)
            xb, yb, wtxt, htxt, xa, ya = ctx.text_extents(s)
            ctx.set_source_rgb(0.06, 0.06, 0.06)
            ctx.move_to(nx - wtxt / 2.0, ny + htxt / 2.0)
            ctx.show_text(s)
        ctx.restore()

    def _draw_subdial(self, ctx: cairo.Context, cx: float, cy: float, radius: float, display_min: float, display_max: float, step: int, label: str) -> None:
        # deprecated generic subdial; no-op
        ctx.save()
        ctx.translate(cx, cy)
        # draw a subtle placeholder ring (very thin)
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.0)
        ctx.arc(0, 0, radius, 0, 2 * math.pi)
        ctx.new_path()
        ctx.restore()

    def _draw_thermo(self, ctx: cairo.Context, cx: float, cy: float, radius: float) -> None:
        """I draw the thermometer as an upper semicircle with 60 ticks."""
        ctx.save()
        ctx.translate(cx, cy)
        # background semicircle
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.new_path()
        ctx.arc(0, 0, radius, math.pi, 2.0 * math.pi)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.9, 0.9, 0.9)
        ctx.set_line_width(max(0.8, radius * 0.02))
        ctx.stroke()
        ctx.new_path()

        ticks = 60
        outer = radius * 0.92
        inner_long = radius * 0.68
        inner_short = radius * 0.76
        ctx.set_source_rgb(0.06, 0.06, 0.06)
        ctx.set_line_cap(cairo.LINE_CAP_BUTT)
        # iterate values 0..60 inclusive so we can place a long tick at 0
        for val in range(0, ticks + 1):
            frac = val / float(ticks)
            th = math.pi + frac * math.pi  # from pi (9 o'clock) to 2pi (3 o'clock)
            if val % 10 == 0:
                iw = inner_long
                lw = 1.0
            else:
                iw = inner_short
                lw = 0.5
            ctx.set_line_width(lw)
            ctx.new_sub_path()
            ctx.move_to(math.cos(th) * iw, math.sin(th) * iw)
            ctx.line_to(math.cos(th) * outer, math.sin(th) * outer)
            ctx.stroke()
            ctx.new_path()

        # numeric labels every 10 (10..60)
        try:
            ctx.select_font_face("Times New Roman", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        except Exception:
            ctx.select_font_face("Serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(max(10.0, radius * 0.11))
        ctx.set_source_rgb(0.02, 0.02, 0.02)
        for val in range(0, 61, 10):
            frac = val / 60.0
            th = math.pi + frac * math.pi
            tx = math.cos(th) * radius * 0.62
            ty = math.sin(th) * radius * 0.62
            s = str(val)
            xb, yb, wtxt, htxt, xa, ya = ctx.text_extents(s)
            ctx.save()
            ctx.translate(tx, ty)
            # draw centered horizontal text
            ctx.move_to(-wtxt / 2.0, htxt / 2.0)
            ctx.show_text(s)
            ctx.restore()

        # label below the semicircle
        try:
            ctx.select_font_face("Times New Roman", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        except Exception:
            ctx.select_font_face("Serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(max(9.0, radius * 0.10))
        ctx.set_source_rgb(0.02, 0.02, 0.02)
        xb, yb, wlbl, hlbl, xa, ya = ctx.text_extents('THERMO °C')
        # move label slightly up inside the subdial area (just below the arc)
        ctx.move_to(-wlbl / 2.0, radius * 0.45)
        ctx.show_text('THERMO °C')
        ctx.new_path()
        ctx.restore()

    def _draw_hygro(self, ctx: cairo.Context, cx: float, cy: float, radius: float) -> None:
        """I draw the hygrometer as an upper semicircle covering 30..100."""
        ctx.save()
        ctx.translate(cx, cy)
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.new_path()
        ctx.arc(0, 0, radius, math.pi, 2.0 * math.pi)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.9, 0.9, 0.9)
        ctx.set_line_width(max(0.8, radius * 0.02))
        ctx.stroke()
        ctx.new_path()

        disp_min = 30
        disp_max = 100
        ticks = disp_max - disp_min  # one tick per unit
        outer = radius * 0.92
        inner_long = radius * 0.68
        inner_short = radius * 0.76
        ctx.set_source_rgb(0.06, 0.06, 0.06)
        ctx.set_line_cap(cairo.LINE_CAP_BUTT)
        for i in range(ticks + 1):
            val = disp_min + i
            frac = (val - disp_min) / float(disp_max - disp_min)
            th = math.pi + frac * math.pi
            if val % 10 == 0:
                iw = inner_long
                lw = 1.0
            else:
                iw = inner_short
                lw = 0.5
            ctx.set_line_width(lw)
            ctx.new_sub_path()
            ctx.move_to(math.cos(th) * iw, math.sin(th) * iw)
            ctx.line_to(math.cos(th) * outer, math.sin(th) * outer)
            ctx.stroke()
            ctx.new_path()

        # numeric labels from 40..100 every 10
        try:
            ctx.select_font_face("Times New Roman", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        except Exception:
            ctx.select_font_face("Serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(max(10.0, radius * 0.11))
        ctx.set_source_rgb(0.02, 0.02, 0.02)
        for val in range(30, 101, 10):
            frac = (val - disp_min) / float(disp_max - disp_min)
            th = math.pi + frac * math.pi
            tx = math.cos(th) * radius * 0.62
            ty = math.sin(th) * radius * 0.62
            s = str(val)
            xb, yb, wtxt, htxt, xa, ya = ctx.text_extents(s)
            ctx.save()
            ctx.translate(tx, ty)
            ctx.move_to(-wtxt / 2.0, htxt / 2.0)
            ctx.show_text(s)
            ctx.restore()

        # label below semicircle
        try:
            ctx.select_font_face("Times New Roman", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        except Exception:
            ctx.select_font_face("Serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(max(9.0, radius * 0.10))
        ctx.set_source_rgb(0.02, 0.02, 0.02)
        xb, yb, wlbl, hlbl, xa, ya = ctx.text_extents('HYGRO %')
        # place label inside the subdial region (just under arc)
        ctx.move_to(-wlbl / 2.0, radius * 0.45)
        ctx.show_text('HYGRO %')
        ctx.new_path()
        ctx.restore()

    def update_clock_graphics(self) -> None:
        # I query canvas size to keep clock centered
        w = max(1, self.canvas.winfo_width())
        h = max(1, self.canvas.winfo_height())
        # update stored sizes
        self.width, self.height = float(w), float(h)
        self.center_x = self.width / 2.0
        self.center_y = self.height / 2.0
        # dynamic radius: 38% of the smaller dimension
        r = min(self.width, self.height) * 0.38
        self.clock_radius = r
        # recompute subdial positions after geometry change
        self._compute_subdial_positions()

        scale = 2
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(w * scale), int(h * scale))
        ctx = cairo.Context(surf)
        ctx.scale(scale, scale)
        ctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

        # background
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.rectangle(0, 0, w, h)
        ctx.fill()

        # bezel and dial
        self._draw_bezel_and_dial(ctx, self.center_x, self.center_y, r)

        # main ticks and numerals
        self._draw_main_ticks_and_numerals(ctx, self.center_x, self.center_y, r)
        # ensure no lingering path from ticks/numerals
        ctx.new_path()

        # subdials (semicircles)
        # Thermometer left: 0..60 semicircle
        self._draw_thermo(ctx, self._h_cx, self._h_cy, self._sub_r)
        # Hygrometer right: 30..100 semicircle
        self._draw_hygro(ctx, self._t_cx, self._t_cy, self._sub_r)

        # clear path before drawing central elements/hands
        ctx.new_path()

        # central logo
        try:
            ctx.select_font_face("Times New Roman", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        except Exception:
            ctx.select_font_face("Serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(r * 0.08)
        # allow logo override from DB
        try:
            from src.services.database_service import DatabaseService

            db = DatabaseService()
            logo_txt = db.get_setting('logo_name')
        except Exception:
            logo_txt = None
        if not logo_txt and getattr(self, 'settings', None):
            try:
                logo_txt = getattr(self.settings, 'get_default_theme', lambda: {})().get('logo_name')
            except Exception:
                logo_txt = None
        if not logo_txt:
            logo_txt = 'Mebus'
        xb, yb, wlogo, hlogo, xa, ya = ctx.text_extents(logo_txt)
        ctx.set_source_rgb(0.06, 0.06, 0.06)
        ctx.move_to(self.center_x - wlogo / 2.0, self.center_y - r * 0.18)
        ctx.show_text(logo_txt)
        # tagline removed for a cleaner look

        # animated subdial hands
        now = time.time()
        # humidity 0..100
        current_h = max(0.0, min(100.0, self._map_time_to_humidity(now) + random.uniform(-1.0, 1.0)))
        # temp around 15..28
        current_t = max(-20.0, min(60.0, self._map_time_to_temp(now) + random.uniform(-0.6, 0.6)))

        # left: thermometer 0..60
        try:
            disp_min, disp_max = 0.0, 60.0
            frac = (current_t - disp_min) / (disp_max - disp_min)
            frac = max(0.0, min(1.0, frac))
            ang = math.pi + frac * math.pi
            ctx.save()
            ctx.translate(self._h_cx, self._h_cy)
            ctx.rotate(ang)
            ctx.set_source_rgb(0.02, 0.02, 0.02)  # black thin hand
            hand_len = self._sub_r * 0.52
            half_w = max(0.8, self._sub_r * 0.022)
            self._draw_baton_hand(ctx, hand_len, half_w)
            # pivot
            ctx.arc(0, 0, max(1.0, self._sub_r * 0.035), 0, 2 * math.pi)
            ctx.fill()
            ctx.restore()
        except Exception:
            pass

        # right: hygrometer 30..100
        try:
            disp_min, disp_max = 30.0, 100.0
            frac = (current_h - disp_min) / (disp_max - disp_min)
            frac = max(0.0, min(1.0, frac))
            ang = math.pi + frac * math.pi
            ctx.save()
            ctx.translate(self._t_cx, self._t_cy)
            ctx.rotate(ang)
            ctx.set_source_rgb(0.02, 0.02, 0.02)
            hand_len = self._sub_r * 0.52
            half_w = max(0.8, self._sub_r * 0.022)
            self._draw_baton_hand(ctx, hand_len, half_w)
            ctx.arc(0, 0, max(1.0, self._sub_r * 0.035), 0, 2 * math.pi)
            ctx.fill()
            ctx.restore()
        except Exception:
            pass

        # central hands
        # use timezone-aware America/Bogota time
        tz = pytz.timezone('America/Bogota')
        now_dt = datetime.now(tz)
        sec = now_dt.second + now_dt.microsecond / 1_000_000
        minute = now_dt.minute + sec / 60.0
        hour = (now_dt.hour % 12) + minute / 60.0

        def time_to_angle(unit, span):
            return (unit / span) * 2.0 * math.pi

        # hour hand
        ang_h = time_to_angle(hour, 12.0) - math.pi / 2.0
        ctx.save()
        ctx.translate(self.center_x, self.center_y)
        ctx.rotate(ang_h)
        ctx.set_source_rgb(0.02, 0.02, 0.02)
        # thinner hour baton
        self._draw_baton_hand(ctx, r * 0.48, max(2.0, r * 0.015))
        ctx.restore()

        # minute hand
        ang_m = time_to_angle(minute, 60.0) - math.pi / 2.0
        ctx.save()
        ctx.translate(self.center_x, self.center_y)
        ctx.rotate(ang_m)
        ctx.set_source_rgb(0.02, 0.02, 0.02)
        # slimmer minute baton
        self._draw_baton_hand(ctx, r * 0.76, max(1.2, r * 0.012))
        ctx.restore()

        # second hand: cyan tick movement
        sec_int = int(sec)  # use integer seconds for tick behavior
        ang_s = time_to_angle(sec_int, 60.0) - math.pi / 2.0
        ctx.save()
        ctx.translate(self.center_x, self.center_y)
        ctx.rotate(ang_s)
        # allow override from database or settings
        try:
            from src.services.database_service import DatabaseService

            db = DatabaseService()
            hex_col = db.get_setting('second_hand_color')
        except Exception:
            hex_col = None
        if not hex_col and getattr(self, 'settings', None):
            hex_col = getattr(self.settings, 'HAND_COLORS', {}).get('second')
        rcol, gcol, bcol = self._hex_to_rgb(hex_col)
        ctx.set_source_rgb(rcol, gcol, bcol)
        # second hand line width
        ctx.set_line_width(max(0.6, r * 0.003))
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(0, 0)
        ctx.line_to(r * 0.88, 0)
        ctx.stroke()
        ctx.restore()

        # center cap (drawn last)
        ctx.save()
        ctx.translate(self.center_x, self.center_y)
        self._draw_center_cap(ctx, max(5, r * 0.03))
        ctx.restore()

        # finalize
        pil = _surface_to_pil(surf)
        pil_small = pil.resize((w, h), Image.LANCZOS)
        photo = ImageTk.PhotoImage(pil_small)
        self.image_ref = photo
        cx_img, cy_img = int(self.center_x), int(self.center_y)
        if self._image_id is None:
            self._image_id = self.canvas.create_image(cx_img, cy_img, image=photo, anchor=tk.CENTER)
        else:
            self.canvas.coords(self._image_id, cx_img, cy_img)
            self.canvas.itemconfig(self._image_id, image=photo)

    def _anim_tick(self) -> None:
        self.update_clock_graphics()
        # update at ~20fps for smooth second-hand motion
        self.after(50, self._anim_tick)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Mebus - Vector Clock')
    cf = ClockFace(root)
    cf.pack(expand=True, fill=tk.BOTH)
    root.mainloop()
