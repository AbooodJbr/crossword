# Crossword Solver

Constraint-satisfaction crossword generator that can run from the command line or a small Tkinter GUI.

## Prerequisites
- Python 3.9+
- Pillow for saving rendered images: `pip install pillow`

## CLI Usage
```bash
python generate.py data/structure0.txt data/words0.txt           # print solution to terminal
python generate.py data/structure0.txt data/words0.txt output.png # also save rendered image
```
Structures use `_` for open cells and any other character for blocks. Word lists should contain one word per line.

## GUI Usage
```bash
python gui.py
```
- Choose a structure file and word list.
- Optionally set an output path to save a PNG image (requires Pillow).
- Click **Solve** to view the solution in the window.

## Project Files
- `crossword.py` — grid parsing, variable setup, and overlap computation.
- `generate.py` — CSP solver (node/arc consistency + backtracking) and image rendering.
- `gui.py` — minimal Tkinter interface for solving/previewing.
- `data/` — sample structures and word lists.
- `assets/fonts/` — OpenSans font for rendered images.

## Notes
- All words in a solution are unique and must fit both the slot length and the overlap constraints.
- If the solver reports no solution, verify the structure/word list pairing or try a different dataset.
