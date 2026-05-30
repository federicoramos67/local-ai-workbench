from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from database import WorkbenchDatabase
from exporter import export_library_json, export_prompt_markdown
from models import Prompt


THEMES = {
    "bg": "#101318",
    "panel": "#171b22",
    "panel_alt": "#1d232d",
    "line": "#2c3441",
    "text": "#edf2f7",
    "muted": "#9ba8b7",
    "accent": "#2fbf9f",
    "accent_hover": "#27a98c",
    "danger": "#d84f5f",
}


EN = {
    "app_title": "Local AI Workbench",
    "all": "All",
    "favorites": "Favorites",
    "new_prompt": "New Prompt",
    "delete": "Delete",
    "save": "Save",
    "copy_prompt": "Copy Prompt",
    "copy_full": "Copy Prompt + Notes",
    "export_md": "Export .md",
    "export_json": "Export JSON",
    "import_json": "Import JSON",
    "search": "Search prompts, tags, categories...",
    "categories": "Categories",
    "prompt_library": "Prompt Library",
    "editor": "Editor",
    "title": "Title",
    "category": "Category",
    "tags": "Tags",
    "prompt_body": "Prompt Body",
    "notes": "Notes",
    "notes_hint": "Observations, results, and reuse notes...",
    "empty": "No prompts match your filters.",
    "untitled": "Untitled prompt",
    "saved": "Saved",
    "saved_detail": "Prompt and notes saved.",
    "deleted": "Deleted",
    "delete_confirm": "Delete this prompt?",
    "select_prompt": "Select or create a prompt first.",
    "copied": "Copied to clipboard.",
    "exported": "Exported",
    "imported": "Imported {count} prompts.",
    "error": "Error",
    "json_files": "JSON files",
    "markdown_folder": "Choose a folder for the markdown file",
}


ES = {
    "app_title": "Banco IA",
    "all": "Todas",
    "favorites": "Favoritos",
    "new_prompt": "Nuevo prompt",
    "delete": "Eliminar",
    "save": "Guardar",
    "copy_prompt": "Copiar prompt",
    "copy_full": "Copiar prompt + notas",
    "export_md": "Exportar .md",
    "export_json": "Exportar JSON",
    "import_json": "Importar JSON",
    "search": "Buscar prompts, etiquetas, categorias...",
    "categories": "Categorias",
    "prompt_library": "Biblioteca",
    "editor": "Editor",
    "title": "Titulo",
    "category": "Categoria",
    "tags": "Etiquetas",
    "prompt_body": "Cuerpo del prompt",
    "notes": "Notas",
    "notes_hint": "Observaciones, resultados y notas de reutilizacion...",
    "empty": "No hay prompts con esos filtros.",
    "untitled": "Prompt sin titulo",
    "saved": "Guardado",
    "saved_detail": "Prompt y notas guardados.",
    "deleted": "Eliminado",
    "delete_confirm": "Eliminar este prompt?",
    "select_prompt": "Selecciona o crea un prompt primero.",
    "copied": "Copiado al portapapeles.",
    "exported": "Exportado",
    "imported": "Se importaron {count} prompts.",
    "error": "Error",
    "json_files": "Archivos JSON",
    "markdown_folder": "Elige una carpeta para el archivo markdown",
}


class LocalAIWorkbench(ctk.CTk):
    def __init__(self, lang: dict[str, str]) -> None:
        super().__init__()
        self.lang = lang
        self.db = WorkbenchDatabase()
        self.db.seed_if_empty()
        self.current_prompt_id: int | None = None
        self.prompt_buttons: dict[int, ctk.CTkButton] = {}
        self.category_buttons: dict[str, ctk.CTkButton] = {}
        self.category_filter = lang["all"]
        self.favorite_filter = ctk.BooleanVar(value=False)
        self.search_var = ctk.StringVar()
        self.favorite_var = ctk.BooleanVar(value=False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        self.title(lang["app_title"])
        self.geometry("1280x780")
        self.minsize(1200, 750)
        self.configure(fg_color=THEMES["bg"])

        self._build_layout()
        self.refresh_all()

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, minsize=230, weight=0)
        self.grid_columnconfigure(1, minsize=360, weight=1)
        self.grid_columnconfigure(2, minsize=560, weight=2)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, minsize=66, weight=0)

        self.sidebar = ctk.CTkFrame(self, fg_color=THEMES["panel"], corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 1), pady=0)
        self.sidebar.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self.sidebar,
            text=self.lang["app_title"],
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=THEMES["text"],
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(22, 8))

        ctk.CTkButton(
            self.sidebar,
            text=self.lang["new_prompt"],
            command=self.new_prompt,
            height=40,
            fg_color=THEMES["accent"],
            hover_color=THEMES["accent_hover"],
        ).grid(row=1, column=0, sticky="ew", padx=18, pady=(6, 18))

        category_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        category_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=0)
        category_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            category_frame,
            text=self.lang["categories"].upper(),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEMES["muted"],
        ).grid(row=0, column=0, sticky="w", padx=8, pady=(0, 8))
        self.category_list = ctk.CTkScrollableFrame(category_frame, fg_color="transparent")
        self.category_list.grid(row=1, column=0, sticky="nsew")
        category_frame.grid_rowconfigure(1, weight=1)

        self.center = ctk.CTkFrame(self, fg_color=THEMES["bg"], corner_radius=0)
        self.center.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.center.grid_columnconfigure(0, weight=1)
        self.center.grid_rowconfigure(2, weight=1)

        top_bar = ctk.CTkFrame(self.center, fg_color=THEMES["bg"])
        top_bar.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))
        top_bar.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            top_bar,
            text=self.lang["prompt_library"],
            font=ctk.CTkFont(size=19, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self.search_entry = ctk.CTkEntry(
            self.center,
            textvariable=self.search_var,
            placeholder_text=self.lang["search"],
            height=38,
            fg_color=THEMES["panel"],
            border_color=THEMES["line"],
        )
        self.search_entry.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
        self.search_var.trace_add("write", lambda *_: self.refresh_prompts())

        self.prompt_list = ctk.CTkScrollableFrame(self.center, fg_color=THEMES["bg"])
        self.prompt_list.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))

        self.editor = ctk.CTkFrame(self, fg_color=THEMES["panel"], corner_radius=0)
        self.editor.grid(row=0, column=2, sticky="nsew")
        self.editor.grid_columnconfigure(0, weight=1)
        self.editor.grid_rowconfigure(9, weight=3)
        self.editor.grid_rowconfigure(11, weight=2)

        ctk.CTkLabel(
            self.editor,
            text=self.lang["editor"],
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(18, 12))

        self.title_entry = self._entry(1, self.lang["title"])
        self.category_entry = self._entry(3, self.lang["category"])
        self.tags_entry = self._entry(5, self.lang["tags"])

        favorite_row = ctk.CTkFrame(self.editor, fg_color="transparent")
        favorite_row.grid(row=7, column=0, sticky="ew", padx=22, pady=(6, 8))
        ctk.CTkCheckBox(
            favorite_row,
            text=self.lang["favorites"],
            variable=self.favorite_var,
            fg_color=THEMES["accent"],
            hover_color=THEMES["accent_hover"],
        ).pack(anchor="w")

        ctk.CTkLabel(self.editor, text=self.lang["prompt_body"], text_color=THEMES["muted"]).grid(
            row=8, column=0, sticky="w", padx=22, pady=(6, 4)
        )
        self.body_text = ctk.CTkTextbox(
            self.editor,
            wrap="word",
            fg_color=THEMES["panel_alt"],
            border_width=1,
            border_color=THEMES["line"],
        )
        self.body_text.grid(row=9, column=0, sticky="nsew", padx=22, pady=(0, 10))

        ctk.CTkLabel(self.editor, text=self.lang["notes"], text_color=THEMES["muted"]).grid(
            row=10, column=0, sticky="w", padx=22, pady=(4, 4)
        )
        self.notes_text = ctk.CTkTextbox(
            self.editor,
            wrap="word",
            fg_color=THEMES["panel_alt"],
            border_width=1,
            border_color=THEMES["line"],
        )
        self.notes_text.grid(row=11, column=0, sticky="nsew", padx=22, pady=(0, 18))

        self.action_bar = ctk.CTkFrame(self, fg_color=THEMES["panel_alt"], corner_radius=0, height=66)
        self.action_bar.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self.action_bar.grid_columnconfigure(0, weight=1)
        self.status_label = ctk.CTkLabel(self.action_bar, text="", text_color=THEMES["muted"])
        self.status_label.grid(row=0, column=0, sticky="w", padx=20)
        actions = ctk.CTkFrame(self.action_bar, fg_color="transparent")
        actions.grid(row=0, column=1, sticky="e", padx=14, pady=12)

        self._bar_button(actions, self.lang["import_json"], self.import_json, 0)
        self._bar_button(actions, self.lang["export_json"], self.export_json, 1)
        self._bar_button(actions, self.lang["export_md"], self.export_md, 2)
        self._bar_button(actions, self.lang["copy_full"], self.copy_full, 3)
        self._bar_button(actions, self.lang["copy_prompt"], self.copy_prompt, 4)
        self._bar_button(actions, self.lang["delete"], self.delete_prompt, 5, danger=True)
        self._bar_button(actions, self.lang["save"], self.save_current, 6, primary=True)

    def _entry(self, row: int, label: str) -> ctk.CTkEntry:
        ctk.CTkLabel(self.editor, text=label, text_color=THEMES["muted"]).grid(
            row=row, column=0, sticky="w", padx=22, pady=(0 if row == 1 else 8, 4)
        )
        entry = ctk.CTkEntry(
            self.editor,
            height=36,
            fg_color=THEMES["panel_alt"],
            border_color=THEMES["line"],
        )
        entry.grid(row=row + 1, column=0, sticky="ew", padx=22, pady=(0, 2))
        return entry

    def _bar_button(
        self,
        parent: ctk.CTkFrame,
        text: str,
        command,
        column: int,
        primary: bool = False,
        danger: bool = False,
    ) -> None:
        fg = THEMES["accent"] if primary else THEMES["danger"] if danger else THEMES["panel"]
        hover = THEMES["accent_hover"] if primary else "#b94654" if danger else THEMES["line"]
        ctk.CTkButton(parent, text=text, command=command, width=116, height=36, fg_color=fg, hover_color=hover).grid(
            row=0, column=column, padx=4
        )

    def refresh_all(self) -> None:
        self.refresh_categories()
        self.refresh_prompts()

    def selected_category_for_db(self) -> str:
        return "All" if self.category_filter == self.lang["all"] else self.category_filter

    def refresh_categories(self) -> None:
        for child in self.category_list.winfo_children():
            child.destroy()
        categories = [self.lang["all"], self.lang["favorites"], *self.db.list_categories()]
        for index, category in enumerate(categories):
            selected = category == self.category_filter
            button = ctk.CTkButton(
                self.category_list,
                text=category,
                anchor="w",
                height=34,
                fg_color=THEMES["accent"] if selected else "transparent",
                hover_color=THEMES["line"],
                command=lambda c=category: self.set_category(c),
            )
            button.grid(row=index, column=0, sticky="ew", padx=4, pady=3)
            self.category_list.grid_columnconfigure(0, weight=1)

    def set_category(self, category: str) -> None:
        self.category_filter = category
        self.favorite_filter.set(category == self.lang["favorites"])
        self.refresh_all()

    def refresh_prompts(self) -> None:
        for child in self.prompt_list.winfo_children():
            child.destroy()
        category = self.selected_category_for_db()
        favorites_only = self.category_filter == self.lang["favorites"]
        prompts = self.db.search_prompts(self.search_var.get(), category, favorites_only)
        if not prompts:
            ctk.CTkLabel(self.prompt_list, text=self.lang["empty"], text_color=THEMES["muted"]).pack(padx=20, pady=24)
            return
        for prompt in prompts:
            self._prompt_card(prompt)

    def _prompt_card(self, prompt: Prompt) -> None:
        selected = prompt.id == self.current_prompt_id
        card = ctk.CTkButton(
            self.prompt_list,
            text="",
            height=86,
            fg_color=THEMES["panel_alt"] if selected else THEMES["panel"],
            hover_color=THEMES["line"],
            command=lambda pid=prompt.id: self.load_prompt(pid or 0),
        )
        card.pack(fill="x", padx=6, pady=6)
        card.grid_columnconfigure(0, weight=1)
        star = "*" if prompt.favorite else " "
        title = ctk.CTkLabel(card, text=f"{star} {prompt.title}", font=ctk.CTkFont(size=15, weight="bold"), anchor="w")
        title.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 0))
        meta = ctk.CTkLabel(
            card,
            text=f"{prompt.category}  |  {prompt.tags}",
            text_color=THEMES["muted"],
            anchor="w",
        )
        meta.grid(row=1, column=0, sticky="ew", padx=14, pady=(2, 10))

    def new_prompt(self) -> None:
        self.current_prompt_id = None
        self.clear_editor()
        self.title_entry.insert(0, self.lang["untitled"])
        self.category_entry.insert(0, "General")
        self.set_status("")
        self.refresh_prompts()

    def clear_editor(self) -> None:
        for entry in (self.title_entry, self.category_entry, self.tags_entry):
            entry.delete(0, "end")
        self.body_text.delete("1.0", "end")
        self.notes_text.delete("1.0", "end")
        self.favorite_var.set(False)

    def load_prompt(self, prompt_id: int) -> None:
        prompt = self.db.get_prompt(prompt_id)
        if not prompt:
            return
        note = self.db.get_note(prompt_id)
        self.current_prompt_id = prompt_id
        self.clear_editor()
        self.title_entry.insert(0, prompt.title)
        self.category_entry.insert(0, prompt.category)
        self.tags_entry.insert(0, prompt.tags)
        self.body_text.insert("1.0", prompt.body)
        if note:
            self.notes_text.insert("1.0", note.content)
        self.favorite_var.set(prompt.favorite)
        self.refresh_prompts()

    def current_prompt_from_editor(self) -> Prompt:
        return Prompt(
            id=self.current_prompt_id,
            title=self.title_entry.get(),
            category=self.category_entry.get(),
            tags=self.tags_entry.get(),
            body=self.body_text.get("1.0", "end").strip(),
            favorite=self.favorite_var.get(),
        )

    def save_current(self) -> None:
        prompt = self.current_prompt_from_editor()
        self.current_prompt_id = self.db.save_prompt(prompt)
        self.db.save_note(self.current_prompt_id, self.notes_text.get("1.0", "end").strip())
        self.refresh_all()
        self.set_status(self.lang["saved_detail"])

    def delete_prompt(self) -> None:
        if not self.current_prompt_id:
            self.warn_select()
            return
        if not messagebox.askyesno(self.lang["delete"], self.lang["delete_confirm"]):
            return
        self.db.delete_prompt(self.current_prompt_id)
        self.current_prompt_id = None
        self.clear_editor()
        self.refresh_all()
        self.set_status(self.lang["deleted"])

    def copy_prompt(self) -> None:
        body = self.body_text.get("1.0", "end").strip()
        if not body:
            self.warn_select()
            return
        self.clipboard_clear()
        self.clipboard_append(body)
        self.set_status(self.lang["copied"])

    def copy_full(self) -> None:
        prompt = self.current_prompt_from_editor()
        if not prompt.body.strip():
            self.warn_select()
            return
        notes = self.notes_text.get("1.0", "end").strip()
        text = f"{prompt.body.strip()}\n\nNotes:\n{notes}" if notes else prompt.body.strip()
        self.clipboard_clear()
        self.clipboard_append(text)
        self.set_status(self.lang["copied"])

    def export_md(self) -> None:
        if not self.current_prompt_id:
            self.warn_select()
            return
        directory = filedialog.askdirectory(title=self.lang["markdown_folder"])
        if not directory:
            return
        try:
            path = export_prompt_markdown(self.db, self.current_prompt_id, Path(directory))
            self.set_status(f"{self.lang['exported']}: {path}")
        except Exception as exc:
            messagebox.showerror(self.lang["error"], str(exc))

    def export_json(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[(self.lang["json_files"], "*.json")],
            initialfile="local_ai_workbench_library.json",
        )
        if not path:
            return
        try:
            export_library_json(self.db, Path(path))
            self.set_status(f"{self.lang['exported']}: {path}")
        except Exception as exc:
            messagebox.showerror(self.lang["error"], str(exc))

    def import_json(self) -> None:
        path = filedialog.askopenfilename(filetypes=[(self.lang["json_files"], "*.json")])
        if not path:
            return
        try:
            count = self.db.import_json_file(Path(path))
            self.refresh_all()
            self.set_status(self.lang["imported"].format(count=count))
        except Exception as exc:
            messagebox.showerror(self.lang["error"], str(exc))

    def warn_select(self) -> None:
        self.set_status(self.lang["select_prompt"])

    def set_status(self, text: str) -> None:
        self.status_label.configure(text=text)


def run_app(language: str = "en") -> None:
    app = LocalAIWorkbench(ES if language == "es" else EN)
    app.mainloop()
