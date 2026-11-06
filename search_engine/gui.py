"""Module 7: Frontend GUI (Tkinter).

A search box, a Search button, and a read-only results area.
"""

import tkinter as tk
from tkinter import scrolledtext, ttk

from .query_processor import QueryProcessor, QuerySyntaxError

HELP_TEXT = (
    "Operators: AND, OR, NOT, parentheses. Adjacent words are ANDed.\n"
    "Wildcards: * matches any characters, e.g.  retriev*   *tion   comp*r"
)


class SearchApp:
    def __init__(self, root: tk.Tk, processor: QueryProcessor, snippet_len: int = 160):
        self.root = root
        self.processor = processor
        self.snippet_len = snippet_len

        index = processor.index
        root.title("WSM Search Engine")
        root.geometry("760x520")
        root.minsize(480, 320)

        frame = ttk.Frame(root, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(3, weight=1)

        self.query_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=self.query_var, font=("Segoe UI", 11))
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        entry.bind("<Return>", lambda _e: self.on_search())
        entry.focus_set()

        ttk.Button(frame, text="Search", command=self.on_search).grid(row=0, column=1)

        ttk.Label(frame, text=HELP_TEXT, foreground="#555").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(6, 2))
        ttk.Label(
            frame,
            text=f"Indexed {len(index.documents)} documents, {len(index)} terms.",
            foreground="#555",
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 6))

        self.results = scrolledtext.ScrolledText(
            frame, wrap=tk.WORD, font=("Consolas", 10), state=tk.DISABLED)
        self.results.grid(row=3, column=0, columnspan=2, sticky="nsew")

        ttk.Label(
            frame,
            text="Made by Karthikeya",
            font=("Segoe UI", 10, "bold"),
            foreground="#1a5fb4",
        ).grid(row=4, column=0, columnspan=2, sticky="e", pady=(8, 0))

    def on_search(self) -> None:
        query = self.query_var.get().strip()
        if not query:
            self._show("Please enter a query.")
            return
        try:
            result = self.processor.search(query)
        except QuerySyntaxError as exc:
            self._show(f"Query error: {exc}")
            return
        self._show(self._format(query, result))

    def _format(self, query, result) -> str:
        lines = [f'Query: {query}']
        for pattern, terms in result.expansions.items():
            shown = ", ".join(terms) if terms else "(no matching terms)"
            lines.append(f"  {pattern} -> {shown}")
        lines.append(f"{len(result.doc_ids)} matching document(s)\n")

        for doc_id in result.doc_ids:
            doc = self.processor.index.documents[doc_id]
            text = " ".join(doc.text.split())
            snippet = text[: self.snippet_len] + ("..." if len(text) > self.snippet_len else "")
            lines.append(f"[{doc_id}] {doc.name}")
            lines.append(f"    {snippet}\n")
        return "\n".join(lines)

    def _show(self, text: str) -> None:
        # The widget stays DISABLED (read-only); enable just long enough to write.
        self.results.configure(state=tk.NORMAL)
        self.results.delete("1.0", tk.END)
        self.results.insert(tk.END, text)
        self.results.configure(state=tk.DISABLED)


def run_gui(processor: QueryProcessor) -> None:
    root = tk.Tk()
    SearchApp(root, processor)
    root.mainloop()
