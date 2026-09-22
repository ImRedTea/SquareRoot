"""tkinter/ttk desktop GUI for the SquareRoot complex-square-root calculator."""

import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, ttk

import squareroot
from squareroot.ui.logic import build_variables, compute

IS_MAC = sys.platform == "darwin"

ACCENT = "#0f766e"
ACCENT_ACTIVE = "#0d9488"
ACCENT_PRESSED = "#115e59"
ERROR_COLOR = "#a5382f"
SYMBOLIC_COLOR = "#7c8a38"

MIN_PRECISION = 1
MAX_PRECISION = 100


def _configure_style(root):
    style = ttk.Style(root)
    available = style.theme_names()
    for preferred in ("clam", "alt", "default"):
        if preferred in available:
            style.theme_use(preferred)
            break

    style.configure(
        "Accent.TButton",
        background=ACCENT,
        foreground="white",
        padding=(14, 7),
        relief="flat",
        borderwidth=0,
    )
    style.map(
        "Accent.TButton",
        background=[("pressed", ACCENT_PRESSED), ("active", ACCENT_ACTIVE), ("disabled", "#9ca3af")],
        foreground=[("disabled", "#e5e7eb")],
    )

    style.configure("Flat.TButton", padding=(6, 3), relief="flat", borderwidth=1)
    style.map("Flat.TButton", background=[("pressed", "#e5e7eb"), ("active", "#f3f4f6")])

    style.configure("RowRemove.TButton", padding=(2, 0), relief="flat", borderwidth=0)
    style.map("RowRemove.TButton", background=[("pressed", "#e5e7eb"), ("active", "#f3f4f6")])

    return style


def _build_fonts():
    default_font = tkfont.nametofont("TkDefaultFont")
    fixed_font = tkfont.nametofont("TkFixedFont")

    result_font = tkfont.Font(font=fixed_font)
    result_font.configure(size=int(fixed_font.actual("size")) + 8, weight="bold")

    expr_font = tkfont.Font(font=fixed_font)
    expr_font.configure(size=int(fixed_font.actual("size")) + 1)

    header_font = tkfont.Font(font=default_font)
    header_font.configure(weight="bold")

    section_font = tkfont.Font(font=default_font)
    section_font.configure(size=int(default_font.actual("size")) - 1)

    return {
        "default": default_font,
        "fixed": fixed_font,
        "result": result_font,
        "expr": expr_font,
        "header": header_font,
        "section": section_font,
    }


class VariablesTable(ttk.Frame):
    """A Name | Value table with per-row delete, rows keyed by a stable id."""

    def __init__(self, parent, fonts):
        super().__init__(parent)
        self._fonts = fonts
        self._rows = {}
        self._next_id = 1
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

    def add_row(self, name="", value=""):
        row_id = self._next_id
        self._next_id += 1

        name_var = tk.StringVar(value=name)
        value_var = tk.StringVar(value=value)
        name_entry = ttk.Entry(self, textvariable=name_var, font=self._fonts["fixed"])
        value_entry = ttk.Entry(self, textvariable=value_var, font=self._fonts["fixed"])
        remove_btn = ttk.Button(
            self,
            text="×",
            width=2,
            style="RowRemove.TButton",
            command=lambda rid=row_id: self.remove_row(rid),
        )

        self._rows[row_id] = (name_var, value_var, name_entry, value_entry, remove_btn)
        self._relayout()
        return row_id

    def remove_row(self, row_id):
        _, _, name_entry, value_entry, remove_btn = self._rows.pop(row_id)
        name_entry.destroy()
        value_entry.destroy()
        remove_btn.destroy()
        self._relayout()

    def clear(self):
        for row_id in list(self._rows):
            _, _, name_entry, value_entry, remove_btn = self._rows.pop(row_id)
            name_entry.destroy()
            value_entry.destroy()
            remove_btn.destroy()
        self._relayout()

    def raw_rows(self):
        return [(nv.get(), vv.get()) for nv, vv, *_ in self._rows.values()]

    def _relayout(self):
        for grid_row, widgets in enumerate(self._rows.values()):
            _, _, name_entry, value_entry, remove_btn = widgets
            name_entry.grid(row=grid_row, column=0, sticky="ew", padx=(0, 4), pady=2)
            value_entry.grid(row=grid_row, column=1, sticky="ew", padx=(0, 4), pady=2)
            remove_btn.grid(row=grid_row, column=2, pady=2)


class SquareRootApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SquareRoot")
        self.root.minsize(560, 620)

        _configure_style(root)
        self.fonts = _build_fonts()

        self._last_result = None

        self.expression_var = tk.StringVar(value="")
        self.precision_var = tk.IntVar(value=squareroot.DEFAULT_PRECISION)
        self.status_var = tk.StringVar(value="Ready")
        self.precision_status_var = tk.StringVar(value=f"decimal · precision {squareroot.DEFAULT_PRECISION}")

        self._build_menu()
        self._build_widgets()
        self._show_ready()

    # -- construction -----------------------------------------------------

    def _build_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(
            label="Quit",
            command=self.root.destroy,
            accelerator="Cmd+Q" if IS_MAC else "Ctrl+Q",
        )
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(label="Copy Result", command=self._copy_result)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="About SquareRoot", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def _build_widgets(self):
        # Pack the status bar (side=BOTTOM, no expand) before the body: pack()
        # carves up space in call order, so an expand=True/fill=BOTH child
        # packed first would otherwise claim the whole cavity and leave the
        # status bar no room.
        self._build_status_bar(self.root)

        body = ttk.Frame(self.root, padding=16)
        body.pack(fill=tk.BOTH, expand=True)

        self._build_expression_row(body)
        self._build_precision_row(body)
        self._build_variables_section(body)
        self._build_result_panel(body)

    def _build_expression_row(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(
            frame, text="EXPRESSION (UNDER THE SQUARE ROOT)", font=self.fonts["section"]
        ).pack(anchor="w")

        row = ttk.Frame(frame)
        row.pack(fill=tk.X, pady=(4, 0))

        glyph = tk.Label(
            row,
            text="√",
            font=self.fonts["expr"],
            fg=ACCENT,
            bg="#e2e2de",
            relief="solid",
            borderwidth=1,
            width=2,
        )
        glyph.pack(side=tk.LEFT, fill=tk.Y)

        entry = ttk.Entry(row, textvariable=self.expression_var, font=self.fonts["expr"])
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
        entry.bind("<Return>", self._on_evaluate)

    def _build_precision_row(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 12))

        precision_col = ttk.Frame(frame)
        precision_col.pack(side=tk.LEFT)
        ttk.Label(precision_col, text="PRECISION", font=self.fonts["section"]).pack(anchor="w")
        ttk.Spinbox(
            precision_col,
            from_=MIN_PRECISION,
            to=MAX_PRECISION,
            textvariable=self.precision_var,
            width=6,
            wrap=False,
        ).pack(anchor="w", pady=(4, 0))

        ttk.Button(
            frame,
            text="Take Square Root",
            style="Accent.TButton",
            command=self._on_evaluate,
        ).pack(side=tk.LEFT, padx=(14, 0), anchor="s")

    def _build_variables_section(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 12))

        header = ttk.Frame(frame)
        header.pack(fill=tk.X)
        ttk.Label(header, text="VARIABLES", font=self.fonts["section"]).pack(side=tk.LEFT)
        ttk.Label(
            header,
            text="substituted into the simplified result",
            font=self.fonts["section"],
            foreground="#85857f",
        ).pack(side=tk.LEFT, padx=(8, 0))

        table_border = ttk.Frame(frame, relief="solid", borderwidth=1)
        table_border.pack(fill=tk.X, pady=(4, 4))
        self.table = VariablesTable(table_border, self.fonts)
        self.table.pack(fill=tk.X, padx=6, pady=6)

        ttk.Button(
            frame, text="+", width=3, style="Flat.TButton", command=self.table.add_row
        ).pack(anchor="w")

    def _build_result_panel(self, parent):
        outer = ttk.Frame(parent, relief="solid", borderwidth=1)
        outer.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        self.result_accent = tk.Frame(outer, width=4, bg="#f0f0ee")
        self.result_accent.pack(side=tk.LEFT, fill=tk.Y)

        content = ttk.Frame(outer, padding=12)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.result_header_label = ttk.Label(content, font=self.fonts["section"], foreground="#85857f")
        self.result_header_label.pack(anchor="w")

        # error badge / value / hint are re-packed in the right order on every
        # render (see _pack_result_body) rather than packed once here, since
        # which of them appear -- and in what order -- depends on the state.
        self.result_error_badge = ttk.Label(
            content, font=self.fonts["header"], foreground=ERROR_COLOR
        )
        self.result_value_label = ttk.Label(content, font=self.fonts["result"])
        self.result_hint_label = ttk.Label(
            content, font=self.fonts["section"], foreground="#85857f", wraplength=480
        )

    def _build_status_bar(self, parent):
        bar = ttk.Frame(parent, relief="solid", borderwidth=1)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Label(bar, textvariable=self.status_var, font=self.fonts["section"]).pack(
            side=tk.LEFT, padx=10, pady=3
        )
        ttk.Label(bar, textvariable=self.precision_status_var, font=self.fonts["section"]).pack(
            side=tk.RIGHT, padx=10, pady=3
        )

    # -- behavior -----------------------------------------------------------

    def _read_precision(self):
        try:
            value = self.precision_var.get()
        except tk.TclError:
            value = None
        if value is None or not (MIN_PRECISION <= value <= MAX_PRECISION):
            messagebox.showerror(
                "Invalid precision",
                f"Precision must be a whole number between {MIN_PRECISION} and {MAX_PRECISION}.",
            )
            return None
        return value

    def _on_evaluate(self, event=None):
        precision = self._read_precision()
        if precision is None:
            return

        radicand = self.expression_var.get().strip()
        variables = build_variables(self.table.raw_rows())
        result = compute(radicand, variables, precision)
        self._last_result = result
        self._render_result(result, precision)

    def _pack_result_body(self, show_badge, show_hint):
        # Re-pack header/[badge]/value/[hint] together, in this fixed order,
        # every render -- pack() stacks in call order, so toggling a widget
        # back on with a bare .pack() after another was already packed would
        # otherwise append it at the bottom regardless of intended position.
        self.result_error_badge.pack_forget()
        self.result_value_label.pack_forget()
        self.result_hint_label.pack_forget()
        if show_badge:
            self.result_error_badge.pack(anchor="w", pady=(2, 0))
        self.result_value_label.pack(anchor="w", pady=(2, 0))
        if show_hint:
            self.result_hint_label.pack(anchor="w", pady=(4, 0))

    def _show_ready(self):
        self._last_result = None
        self.result_accent.configure(bg="#f0f0ee")
        self.result_header_label.configure(text="")
        self.result_value_label.configure(text="Ready.", foreground="#85857f")
        self._pack_result_body(show_badge=False, show_hint=False)
        self.status_var.set("Ready")
        self.precision_status_var.set(f"decimal · precision {self.precision_var.get()}")

    def _render_result(self, result, precision):
        if result.state == "numeric":
            self.result_accent.configure(bg=ACCENT)
            self.result_header_label.configure(text=result.header)
            self.result_value_label.configure(text=result.value, foreground="#1e1e1c")
            self._pack_result_body(show_badge=False, show_hint=False)
            self.status_var.set("OK")
        elif result.state == "symbolic":
            self.result_accent.configure(bg=SYMBOLIC_COLOR)
            self.result_header_label.configure(text=result.header)
            self.result_value_label.configure(text=result.value, foreground="#1e1e1c")
            self.result_hint_label.configure(text=result.hint)
            self._pack_result_body(show_badge=False, show_hint=True)
            self.status_var.set("Symbolic")
        else:
            self.result_accent.configure(bg=ERROR_COLOR)
            self.result_header_label.configure(text=result.header)
            self.result_error_badge.configure(text=result.error_type)
            self.result_value_label.configure(text=result.error_message, foreground="#1e1e1c")
            self._pack_result_body(show_badge=True, show_hint=False)
            self.status_var.set(result.error_type)

        self.precision_status_var.set(f"decimal · precision {precision}")

    def _copy_result(self):
        result = self._last_result
        if result is None:
            return
        text = f"{result.error_type}: {result.error_message}" if result.state == "error" else result.value
        if not text:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    def _show_about(self):
        messagebox.showinfo(
            "About SquareRoot",
            "SquareRoot — complex square root calculator\n"
            "Exact decimal arithmetic and analytical simplification, Python standard library only.",
        )


def main():
    root = tk.Tk()
    SquareRootApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
