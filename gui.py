"""Minimal Tkinter GUI for solving and previewing crossword assignments."""

import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from crossword import Crossword
from generate import CrosswordCreator

DEFAULT_STRUCTURE = "data/structure0.txt"
DEFAULT_WORDS = "data/words0.txt"


class CrosswordApp:
    """Simple interface to choose inputs, solve, and view a crossword."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Crossword Solver")

        self.structure_path = tk.StringVar(value=DEFAULT_STRUCTURE)
        self.words_path = tk.StringVar(value=DEFAULT_WORDS)
        self.output_path = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Idle")

        self._build_layout()

    def _build_layout(self) -> None:
        """Create and arrange widgets."""
        form = tk.Frame(self.root, padx=12, pady=12)
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="Structure file:").grid(row=0, column=0, sticky=tk.W)
        tk.Entry(form, textvariable=self.structure_path, width=40).grid(
            row=0, column=1, sticky=tk.EW, padx=6
        )
        tk.Button(form, text="Browse", command=self._choose_structure).grid(
            row=0, column=2
        )

        tk.Label(form, text="Words file:").grid(row=1, column=0, sticky=tk.W)
        tk.Entry(form, textvariable=self.words_path, width=40).grid(
            row=1, column=1, sticky=tk.EW, padx=6
        )
        tk.Button(form, text="Browse", command=self._choose_words).grid(row=1, column=2)

        tk.Label(form, text="Save image (optional):").grid(row=2, column=0, sticky=tk.W)
        tk.Entry(form, textvariable=self.output_path, width=40).grid(
            row=2, column=1, sticky=tk.EW, padx=6
        )
        tk.Button(form, text="Choose", command=self._choose_output).grid(
            row=2, column=2
        )

        self.solve_button = tk.Button(form, text="Solve", command=self._solve)
        self.solve_button.grid(
            row=3, column=0, columnspan=3, pady=(10, 6), sticky=tk.EW
        )

        tk.Label(form, textvariable=self.status_var, fg="blue").grid(
            row=4, column=0, columnspan=3, sticky=tk.W
        )

        self.output = tk.Text(
            form, height=15, width=60, state=tk.DISABLED, font=("Consolas", 12)
        )
        self.output.grid(row=5, column=0, columnspan=3, pady=(10, 0), sticky=tk.NSEW)

        # Allow the grid to expand nicely
        form.columnconfigure(1, weight=1)
        form.rowconfigure(5, weight=1)

    def _choose_structure(self) -> None:
        path = filedialog.askopenfilename(
            title="Choose structure file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            self.structure_path.set(path)

    def _choose_words(self) -> None:
        path = filedialog.askopenfilename(
            title="Choose words file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            self.words_path.set(path)

    def _choose_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save crossword image",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("All files", "*.*")],
        )
        if path:
            self.output_path.set(path)

    def _solve(self) -> None:
        self._set_status("Solving...")
        self.solve_button.config(state=tk.DISABLED)
        worker = threading.Thread(target=self._solve_in_thread, daemon=True)
        worker.start()

    def _solve_in_thread(self) -> None:
        try:
            crossword = Crossword(self.structure_path.get(), self.words_path.get())
            creator = CrosswordCreator(crossword)
            assignment = creator.solve()
        except Exception as exc:  # Broad catch to surface errors in the UI
            self._notify_error(f"Error while solving: {exc}")
            self._set_status("Error")
            self._enable_button()
            return

        if assignment is None:
            self._set_status("No solution found")
            self._notify_info("No solution could be generated for the chosen files.")
            self._clear_output()
            self._enable_button()
            return

        # Render the solution to the text box
        grid_text = self._format_assignment(creator, assignment)
        self._set_output(grid_text)
        self._set_status("Solved")

        if self.output_path.get():
            try:
                creator.save(assignment, self.output_path.get())
                self._notify_info(f"Image saved to {self.output_path.get()}")
            except ImportError:
                self._notify_error(
                    "Pillow is required to save an image. Install it with 'pip install pillow'."
                )
            except Exception as exc:
                self._notify_error(f"Could not save image: {exc}")

        self._enable_button()

    def _format_assignment(self, creator: CrosswordCreator, assignment) -> str:
        """Return a printable grid for the solved crossword."""
        letters = creator.letter_grid(assignment)
        lines = []
        for i in range(creator.crossword.height):
            row_chars = []
            for j in range(creator.crossword.width):
                if creator.crossword.structure[i][j]:
                    row_chars.append(letters[i][j] or " ")
                else:
                    row_chars.append("#")
            lines.append("".join(row_chars))
        return "\n".join(lines)

    def _set_output(self, text: str) -> None:
        self.root.after(0, self._write_output, text)

    def _write_output(self, text: str) -> None:
        self.output.config(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text)
        self.output.config(state=tk.DISABLED)

    def _clear_output(self) -> None:
        self._set_output("")

    def _notify_info(self, message: str) -> None:
        self.root.after(0, lambda: messagebox.showinfo("Crossword Solver", message))

    def _notify_error(self, message: str) -> None:
        self.root.after(0, lambda: messagebox.showerror("Crossword Solver", message))

    def _set_status(self, text: str) -> None:
        self.root.after(0, self.status_var.set, text)

    def _enable_button(self) -> None:
        self.root.after(0, lambda: self.solve_button.config(state=tk.NORMAL))


def main() -> None:
    root = tk.Tk()
    CrosswordApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
