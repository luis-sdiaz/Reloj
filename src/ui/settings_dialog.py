"""Settings dialog to change logo name and second-hand color.

Saves settings into the `settings` table using `DatabaseService`.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from typing import Optional
from datetime import datetime
import pytz

from src.services.database_service import DatabaseService


class SettingsDialog(tk.Toplevel):
    def __init__(self, master: tk.Misc, apply_callback=None) -> None:
        super().__init__(master)
        self.title('Settings')
        self.resizable(False, False)
        self.apply_callback = apply_callback

        self.db = DatabaseService()

        # load current values
        self.logo_name = tk.StringVar(value=self.db.get_setting('logo_name', 'Mebus'))
        self.second_color = tk.StringVar(value=self.db.get_setting('second_hand_color', '#04A8DB'))

        frm = ttk.Frame(self, padding=12)
        frm.grid(row=0, column=0, sticky='nsew')

        ttk.Label(frm, text='Logo name:').grid(row=0, column=0, sticky='w')
        self.logo_entry = ttk.Entry(frm, textvariable=self.logo_name, width=24)
        self.logo_entry.grid(row=0, column=1, sticky='w', padx=6, pady=6)

        ttk.Label(frm, text='Second hand color:').grid(row=1, column=0, sticky='w')
        color_frame = ttk.Frame(frm)
        color_frame.grid(row=1, column=1, sticky='w')
        self.color_display = ttk.Label(color_frame, text='      ', background=self.second_color.get())
        self.color_display.pack(side='left', padx=(0, 6))
        self.pick_btn = ttk.Button(color_frame, text='Choose...', command=self._pick_color)
        self.pick_btn.pack(side='left')

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(btn_frame, text='Save', command=self._on_save).pack(side='left', padx=6)
        ttk.Button(btn_frame, text='Cancel', command=self.destroy).pack(side='left', padx=6)

        self.protocol('WM_DELETE_WINDOW', self.destroy)

        # Accessibility: Current Time (Colombia)
        sep = ttk.Separator(frm, orient='horizontal')
        sep.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(12, 8))

        ttk.Label(frm, text='Current Time (Colombia):', font=('Segoe UI', 10, 'bold')).grid(row=4, column=0, sticky='w')
        self.time_label = ttk.Label(frm, text='--:--', font=('Segoe UI', 20))
        self.time_label.grid(row=4, column=1, sticky='w', padx=6)

        # Speak Time button
        self.speak_btn = ttk.Button(frm, text='Speak Time', command=self._speak_time)
        self.speak_btn.grid(row=5, column=0, columnspan=2, pady=(8, 0))

        # start updating the time while dialog is open
        self._running = True
        self._update_time()

    def _update_time(self) -> None:
        if not self._running:
            return
        try:
            tz = pytz.timezone('America/Bogota')
            now = datetime.now(tz)
            # format as 12-hour with AM/PM
            disp = now.strftime('%I:%M %p')
            # remove leading zero
            if disp.startswith('0'):
                disp = disp[1:]
            self.time_label.config(text=disp)
        except Exception:
            self.time_label.config(text='--:--')
        # schedule next update in 1s
        try:
            self.after(1000, self._update_time)
        except Exception:
            pass

    def destroy(self) -> None:
        # stop updater and destroy
        try:
            self._running = False
        except Exception:
            pass
        super().destroy()

    def _number_to_spanish(self, n: int) -> str:
        # simple converter for 0..59
        ones = {
            0: 'cero', 1: 'una', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis',
            7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez', 11: 'once', 12: 'doce',
            13: 'trece', 14: 'catorce', 15: 'quince', 16: 'dieciseis', 17: 'diecisiete',
            18: 'dieciocho', 19: 'diecinueve', 20: 'veinte', 21: 'veintiuno', 22: 'veintidos',
            23: 'veintitres', 24: 'veinticuatro', 25: 'veinticinco', 26: 'veintiseis',
            27: 'veintisiete', 28: 'veintiocho', 29: 'veintinueve'
        }
        tens = {30: 'treinta', 40: 'cuarenta', 50: 'cincuenta'}
        if n <= 29:
            return ones.get(n, str(n))
        t = (n // 10) * 10
        u = n % 10
        if u == 0:
            return tens.get(t, str(n))
        else:
            return f"{tens.get(t, str(t))} y {ones.get(u, str(u))}"

    def _hour_period_spanish(self, hour24: int) -> str:
        if 5 <= hour24 < 12:
            return 'de la mañana'
        if 12 <= hour24 < 18:
            return 'de la tarde'
        if 18 <= hour24 < 22:
            return 'de la noche'
        return 'de la madrugada'

    def _speak_time(self) -> None:
        # construct Spanish phrase and speak via pyttsx3
        try:
            tz = pytz.timezone('America/Bogota')
            now = datetime.now(tz)
            h = now.hour
            m = now.minute
            # Spanish hour in 12-hour form (use 12 for hour 0/12)
            h12 = h % 12
            if h12 == 0:
                h12 = 12
            h_words = self._number_to_spanish(h12)
            m_words = self._number_to_spanish(m)
            period = self._hour_period_spanish(h)
            phrase = f"La hora actual en Colombia es las {h_words} y {m_words} {period}"
        except Exception:
            messagebox.showerror('Error', 'Could not determine current time')
            return

        # try importing pyttsx3 and speak
        try:
            import pyttsx3

            engine = pyttsx3.init()
            engine.say(phrase)
            engine.runAndWait()
        except Exception:
            messagebox.showwarning('Speak Time', 'pyttsx3 not available; install it to enable speech')

    def _pick_color(self) -> None:
        initial = self.second_color.get() or '#04A8DB'
        rgb, hx = colorchooser.askcolor(initialcolor=initial, parent=self)
        if hx:
            self.second_color.set(hx)
            try:
                self.color_display.configure(background=hx)
            except Exception:
                pass

    def _on_save(self) -> None:
        logo = self.logo_name.get().strip() or 'Mebus'
        color = self.second_color.get().strip() or '#04A8DB'
        try:
            self.db.set_setting('logo_name', logo)
            self.db.set_setting('second_hand_color', color)
            self.db.save_log(f"Settings updated: logo='{logo}', second_color='{color}'")
        except Exception:
            pass
        if callable(self.apply_callback):
            try:
                self.apply_callback({'logo_name': logo, 'second_hand_color': color})
            except Exception:
                pass
        self.destroy()
