"""Local desktop app: set PDF creation/modification dates and password."""

from __future__ import annotations

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
from pathlib import Path

from pdf_engine import IST, PdfInfo, ProcessOptions, format_display, inspect_pdf, process_pdf


APP_BG = "#101418"
PANEL = "#171d24"
PANEL_2 = "#1e262f"
LINE = "#2c3642"
TEXT = "#e8eef5"
MUTED = "#8b98a8"
ACCENT = "#3d9cf0"
ACCENT_HOVER = "#5aaff5"
GREEN = "#3ecf8e"
RED = "#ef6b6b"
INPUT_BG = "#0c1014"
FONT = "Segoe UI"
MONO = "Consolas"


class DateTimeFields:
    def __init__(self, parent, label: str):
        self.frame = tk.Frame(parent, bg=PANEL)
        tk.Label(
            self.frame,
            text=label,
            bg=PANEL,
            fg=MUTED,
            font=(FONT, 9),
            anchor="w",
        ).pack(fill="x")

        row = tk.Frame(self.frame, bg=PANEL)
        row.pack(fill="x", pady=(6, 0))

        self.boxes = []
        self.day = self._spin(row, 1, 31, 4)
        self._sep(row, "/")
        self.month = self._spin(row, 1, 12, 4)
        self._sep(row, "/")
        self.year = self._spin(row, 1990, 2100, 6)
        self._sep(row, "  ")
        self.hour = self._spin(row, 0, 23, 4)
        self._sep(row, ":")
        self.minute = self._spin(row, 0, 59, 4)
        self._sep(row, ":")
        self.second = self._spin(row, 0, 59, 4)

        now = datetime.now(IST)
        self.set(now)

    def _spin(self, parent, lo, hi, width):
        var = tk.StringVar()
        box = tk.Spinbox(
            parent,
            from_=lo,
            to=hi,
            textvariable=var,
            width=width,
            font=(MONO, 12),
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            buttonbackground=PANEL_2,
            highlightthickness=1,
            highlightbackground=LINE,
            highlightcolor=ACCENT,
            justify="center",
        )
        box.pack(side="left")
        self.boxes.append(box)
        return var

    def _sep(self, parent, text):
        tk.Label(parent, text=text, bg=PANEL, fg=MUTED, font=(FONT, 11)).pack(side="left")

    def set(self, dt: datetime | None):
        if dt is None:
            dt = datetime.now(IST)
        self.day.set(f"{dt.day:02d}")
        self.month.set(f"{dt.month:02d}")
        self.year.set(str(dt.year))
        self.hour.set(f"{dt.hour:02d}")
        self.minute.set(f"{dt.minute:02d}")
        self.second.set(f"{dt.second:02d}")

    def get(self) -> datetime:
        return datetime(
            int(self.year.get()),
            int(self.month.get()),
            int(self.day.get()),
            int(self.hour.get()),
            int(self.minute.get()),
            int(self.second.get()),
            tzinfo=IST,
        )

    def set_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for box in self.boxes:
            box.configure(state=state)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Incarnation · PDF Date & Lock")
        self.geometry("920x700")
        self.minsize(840, 640)
        self.configure(bg=APP_BG)
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.open_password = tk.StringVar()
        self.new_password = tk.StringVar()
        self.lock_pdf = tk.BooleanVar(value=True)
        self.compress = tk.BooleanVar(value=True)
        self.wipe_meta = tk.BooleanVar(value=True)
        self.strip_producer = tk.BooleanVar(value=True)
        self.blank_modified = tk.BooleanVar(value=True)
        self.same_dates = tk.BooleanVar(value=False)
        self.info: PdfInfo | None = None
        self._build()
        self._center()

    def _center(self):
        self.update_idletasks()
        w, h = 920, 700
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _card(self, parent, **pack):
        card = tk.Frame(parent, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
        card.pack(**pack)
        inner = tk.Frame(card, bg=PANEL)
        inner.pack(fill="both", expand=True, padx=16, pady=14)
        return inner

    def _entry(self, parent, var, show=None, width=None):
        e = tk.Entry(
            parent,
            textvariable=var,
            font=(FONT, 11),
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            show=show or "",
            highlightthickness=1,
            highlightbackground=LINE,
            highlightcolor=ACCENT,
        )
        if width:
            e.configure(width=width)
        return e

    def _btn(self, parent, text, command, primary=False, danger=False):
        bg = ACCENT if primary else ("#3a2224" if danger else PANEL_2)
        fg = "#061018" if primary else TEXT
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=(FONT, 10, "bold" if primary else "normal"),
            bg=bg,
            fg=fg,
            activebackground=ACCENT_HOVER if primary else LINE,
            activeforeground=fg,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=7,
            bd=0,
        )
        return btn

    def _check(self, parent, text, var):
        return tk.Checkbutton(
            parent,
            text=text,
            variable=var,
            bg=PANEL,
            fg=TEXT,
            selectcolor=INPUT_BG,
            activebackground=PANEL,
            activeforeground=TEXT,
            font=(FONT, 10),
            anchor="w",
        )

    def _build(self):
        header = tk.Frame(self, bg=APP_BG)
        header.pack(fill="x", padx=22, pady=(18, 8))
        tk.Label(
            header,
            text="PDF Date & Lock",
            bg=APP_BG,
            fg=TEXT,
            font=(FONT, 20, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Set creation date, modification date, and password without editing Python files.",
            bg=APP_BG,
            fg=MUTED,
            font=(FONT, 10),
        ).pack(anchor="w", pady=(2, 0))

        file_card = self._card(self, fill="x", padx=22, pady=8)
        tk.Label(file_card, text="SOURCE PDF", bg=PANEL, fg=MUTED, font=(FONT, 8, "bold")).pack(anchor="w")
        row = tk.Frame(file_card, bg=PANEL)
        row.pack(fill="x", pady=(8, 0))
        self._entry(row, self.input_path).pack(side="left", fill="x", expand=True, ipady=6)
        self._btn(row, "Browse", self.browse_input).pack(side="left", padx=(8, 0))
        self._btn(row, "Inspect", self.load_info).pack(side="left", padx=(8, 0))

        pw_row = tk.Frame(file_card, bg=PANEL)
        pw_row.pack(fill="x", pady=(10, 0))
        tk.Label(pw_row, text="Open password (if already locked)", bg=PANEL, fg=MUTED, font=(FONT, 9)).pack(side="left")
        self._entry(pw_row, self.open_password, show="•", width=22).pack(side="left", padx=10, ipady=4)
        self.show_open = tk.BooleanVar(value=False)
        tk.Checkbutton(
            pw_row,
            text="Show",
            variable=self.show_open,
            command=lambda: self._toggle_show(self.open_password_entry, self.show_open),
            bg=PANEL,
            fg=MUTED,
            selectcolor=INPUT_BG,
            activebackground=PANEL,
            font=(FONT, 9),
        ).pack(side="left")
        # keep a handle after packing — rebuild slightly
        for child in pw_row.winfo_children():
            if isinstance(child, tk.Entry):
                self.open_password_entry = child

        self.info_label = tk.Label(
            file_card,
            text="No file loaded.",
            bg=PANEL,
            fg=MUTED,
            font=(FONT, 10),
            justify="left",
            anchor="w",
        )
        self.info_label.pack(fill="x", pady=(12, 0))

        mid = tk.Frame(self, bg=APP_BG)
        mid.pack(fill="both", expand=True, padx=22, pady=8)

        left = self._card(mid, side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(left, text="DATES", bg=PANEL, fg=MUTED, font=(FONT, 8, "bold")).pack(anchor="w")

        self.created = DateTimeFields(left, "Date of creation")
        self.created.frame.pack(fill="x", pady=(10, 8))
        btnrow = tk.Frame(left, bg=PANEL)
        btnrow.pack(fill="x")
        self._btn(btnrow, "Now", lambda: self.created.set(datetime.now(IST))).pack(side="left")
        self._btn(btnrow, "From file", self.use_file_created).pack(side="left", padx=6)

        self.modified = DateTimeFields(left, "Date of modification")
        self.modified.frame.pack(fill="x", pady=(16, 8))
        self.mod_btnrow = tk.Frame(left, bg=PANEL)
        self.mod_btnrow.pack(fill="x")
        self._btn(self.mod_btnrow, "Now", lambda: self.modified.set(datetime.now(IST))).pack(side="left")
        self._btn(self.mod_btnrow, "From file", self.use_file_modified).pack(side="left", padx=6)
        self._btn(self.mod_btnrow, "Match creation", self.copy_created_to_mod).pack(side="left", padx=6)

        self._check(
            left,
            "Leave Modified blank (nothing in Acrobat Modified field)",
            self.blank_modified,
        ).pack(anchor="w", pady=(12, 0))
        self.same_dates_chk = self._check(
            left, "Keep both dates identical while editing creation", self.same_dates
        )
        self.same_dates_chk.pack(anchor="w", pady=(4, 0))
        self.same_dates.trace_add("write", lambda *_: self._sync_dates())
        self.blank_modified.trace_add("write", lambda *_: self._toggle_blank_modified())

        right = self._card(mid, side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(right, text="PASSWORD & OPTIONS", bg=PANEL, fg=MUTED, font=(FONT, 8, "bold")).pack(anchor="w")

        tk.Label(right, text="New file password", bg=PANEL, fg=MUTED, font=(FONT, 9)).pack(anchor="w", pady=(12, 4))
        pwbox = tk.Frame(right, bg=PANEL)
        pwbox.pack(fill="x")
        self.new_password_entry = self._entry(pwbox, self.new_password, show="•")
        self.new_password_entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.show_new = tk.BooleanVar(value=False)
        tk.Checkbutton(
            pwbox,
            text="Show",
            variable=self.show_new,
            command=lambda: self._toggle_show(self.new_password_entry, self.show_new),
            bg=PANEL,
            fg=MUTED,
            selectcolor=INPUT_BG,
            activebackground=PANEL,
            font=(FONT, 9),
        ).pack(side="left", padx=(8, 0))

        self._check(right, "Lock output with this password", self.lock_pdf).pack(anchor="w", pady=(12, 2))
        self._check(right, "Compress streams (smaller file)", self.compress).pack(anchor="w", pady=2)
        self._check(right, "Wipe title / author / extra metadata", self.wipe_meta).pack(anchor="w", pady=2)
        self._check(right, "Strip library Producer tag", self.strip_producer).pack(anchor="w", pady=2)

        tk.Label(
            right,
            text="Leave password empty and uncheck lock to save an unlocked PDF.",
            bg=PANEL,
            fg=MUTED,
            font=(FONT, 9),
            wraplength=360,
            justify="left",
        ).pack(anchor="w", pady=(12, 0))

        out_card = self._card(self, fill="x", padx=22, pady=8)
        tk.Label(out_card, text="SAVE AS", bg=PANEL, fg=MUTED, font=(FONT, 8, "bold")).pack(anchor="w")
        outrow = tk.Frame(out_card, bg=PANEL)
        outrow.pack(fill="x", pady=(8, 0))
        self._entry(outrow, self.output_path).pack(side="left", fill="x", expand=True, ipady=6)
        self._btn(outrow, "Choose…", self.browse_output).pack(side="left", padx=(8, 0))

        actions = tk.Frame(self, bg=APP_BG)
        actions.pack(fill="x", padx=22, pady=(4, 8))
        self.status = tk.Label(actions, text="Ready.", bg=APP_BG, fg=MUTED, font=(FONT, 10), anchor="w")
        self.status.pack(side="left", fill="x", expand=True)
        self._btn(actions, "Process PDF", self.run_process, primary=True).pack(side="right")

        log_wrap = tk.Frame(self, bg=APP_BG)
        log_wrap.pack(fill="both", expand=True, padx=22, pady=(0, 18))
        self.log = tk.Text(
            log_wrap,
            height=6,
            bg=INPUT_BG,
            fg=MUTED,
            font=(MONO, 9),
            relief="flat",
            highlightthickness=1,
            highlightbackground=LINE,
            insertbackground=TEXT,
        )
        self.log.pack(fill="both", expand=True)
        self.log.insert("end", "Load a PDF, set dates and password, then Process.\n")
        self.log.configure(state="disabled")

        self.created.year.trace_add("write", lambda *_: self._sync_dates())
        self.created.month.trace_add("write", lambda *_: self._sync_dates())
        self.created.day.trace_add("write", lambda *_: self._sync_dates())
        self.created.hour.trace_add("write", lambda *_: self._sync_dates())
        self.created.minute.trace_add("write", lambda *_: self._sync_dates())
        self.created.second.trace_add("write", lambda *_: self._sync_dates())
        self._toggle_blank_modified()

    def _toggle_show(self, entry: tk.Entry, flag: tk.BooleanVar):
        entry.configure(show="" if flag.get() else "•")

    def _sync_dates(self):
        if self.blank_modified.get():
            return
        if self.same_dates.get():
            try:
                self.modified.set(self.created.get())
            except Exception:
                pass

    def _toggle_blank_modified(self):
        enabled = not self.blank_modified.get()
        self.modified.set_enabled(enabled)
        btn_state = "normal" if enabled else "disabled"
        for child in self.mod_btnrow.winfo_children():
            child.configure(state=btn_state)
        self.same_dates_chk.configure(state=btn_state)
        if not enabled:
            self.same_dates.set(False)

    def log_line(self, text: str, ok: bool | None = None):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")
        if ok is True:
            self.status.configure(text=text, fg=GREEN)
        elif ok is False:
            self.status.configure(text=text, fg=RED)
        else:
            self.status.configure(text=text, fg=MUTED)

    def browse_input(self):
        path = filedialog.askopenfilename(
            title="Choose PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if path:
            self.input_path.set(path)
            self._suggest_output(path)
            self.load_info()

    def browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Save PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=os.path.basename(self.output_path.get() or "output.pdf"),
        )
        if path:
            self.output_path.set(path)

    def _suggest_output(self, path: str):
        p = Path(path)
        self.output_path.set(str(p.with_name(p.stem + "_dated.pdf")))

    def use_file_created(self):
        if self.info and self.info.creation:
            self.created.set(self.info.creation)
        else:
            messagebox.showinfo("No date", "This file has no creation date in metadata.")

    def use_file_modified(self):
        if self.info and self.info.modification:
            self.modified.set(self.info.modification)
        else:
            messagebox.showinfo("No date", "This file has no modification date in metadata.")

    def copy_created_to_mod(self):
        try:
            self.modified.set(self.created.get())
        except ValueError:
            messagebox.showerror("Invalid date", "Check the creation date fields.")

    def load_info(self):
        path = self.input_path.get().strip()
        if not path:
            messagebox.showwarning("Choose a file", "Select a PDF first.")
            return
        if not os.path.isfile(path):
            messagebox.showerror("Missing file", path)
            return
        try:
            info = inspect_pdf(path, self.open_password.get().strip())
        except Exception as exc:
            name = type(exc).__name__
            locked = name == "PasswordError" or "password" in str(exc).lower()
            if locked:
                self.info = None
                if self.open_password.get().strip():
                    msg = "That password did not open this PDF. Check it and click Inspect."
                else:
                    msg = "This PDF is locked. Enter the open password, then click Inspect."
                self.info_label.configure(text=msg, fg=RED)
                self.log_line(msg, False)
                return
            self.info = None
            self.info_label.configure(text=str(exc), fg=RED)
            self.log_line(f"Inspect failed: {exc}", False)
            return

        self.info = info
        if not self.output_path.get():
            self._suggest_output(path)
        created = format_display(info.creation)
        modified = format_display(info.modification)
        lock = "Yes" if info.encrypted else "No"
        self.info_label.configure(
            text=(
                f"{os.path.basename(path)}  ·  {info.pages} pages  ·  {info.size_kb:.1f} KB  ·  "
                f"PDF {info.pdf_version}  ·  Encrypted: {lock}\n"
                f"Current creation: {created}    Current modified: {modified}"
            ),
            fg=TEXT,
        )
        if info.creation:
            self.created.set(info.creation)
        if info.modification:
            self.modified.set(info.modification)
        self.log_line(f"Loaded {path}")

    def run_process(self):
        path = self.input_path.get().strip()
        out = self.output_path.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showwarning("Source missing", "Choose a valid source PDF.")
            return
        if not out.lower().endswith(".pdf"):
            out += ".pdf"
            self.output_path.set(out)
        if os.path.abspath(path) == os.path.abspath(out):
            messagebox.showwarning("Same file", "Save to a new filename so the original stays intact.")
            return
        if self.lock_pdf.get() and not self.new_password.get().strip():
            messagebox.showwarning("Password", "Enter a password, or uncheck lock.")
            return
        try:
            created = self.created.get()
            modified = self.modified.get()
        except Exception:
            messagebox.showerror("Invalid date", "Check day / month / year / time values.")
            return

        options = ProcessOptions(
            input_path=path,
            output_path=out,
            open_password=self.open_password.get().strip(),
            new_password=self.new_password.get().strip(),
            lock=self.lock_pdf.get(),
            creation=created,
            modification=modified,
            compress=self.compress.get(),
            wipe_other_metadata=self.wipe_meta.get(),
            strip_producer=self.strip_producer.get(),
        )
        self.log_line("Processing…")
        threading.Thread(target=self._worker, args=(options,), daemon=True).start()

    def _worker(self, options: ProcessOptions):
        try:
            result = process_pdf(options)
            msg = (
                f"Saved {result['output']}  ({result['size_kb']:.1f} KB)  "
                f"Created {result['creation']}  Modified {result['modification']}  "
                f"{'Locked' if result['locked'] else 'Unlocked'}"
            )
            self.after(0, lambda: self.log_line(msg, True))
            self.after(0, lambda: messagebox.showinfo("Done", msg))
        except Exception as exc:
            err = str(exc)
            self.after(0, lambda: self.log_line(err, False))
            self.after(0, lambda: messagebox.showerror("Failed", err))


def main():
    if hasattr(sys, "frozen"):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
