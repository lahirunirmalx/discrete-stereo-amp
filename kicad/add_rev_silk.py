"""Stamp the repository URL and revision on a board's front silkscreen. Run with /usr/bin/python3.
Usage: add_rev_silk.py board.kicad_pcb x_mm y_mm size_mm "text"   (x, y relative to the board's top-left corner)"""
import sys
import pcbnew
from pcbnew import VECTOR2I, FromMM
path, x, y, size, text = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
b = pcbnew.LoadBoard(path)
for t in list(b.Drawings()):
    if t.GetClass() == "PCB_TEXT" and t.GetText().startswith(("github.com/", "discrete-stereo-amp", "v1.0 ")):
        b.Remove(t)
bb = b.GetBoardEdgesBoundingBox()
t = pcbnew.PCB_TEXT(b)
t.SetText(text); t.SetLayer(pcbnew.F_SilkS)
t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); t.SetTextThickness(FromMM(0.15 if size >= 0.9 else 0.12))
t.SetPosition(VECTOR2I(bb.GetLeft() + FromMM(x), bb.GetTop() + FromMM(y)))
b.Add(t)
pcbnew.SaveBoard(path, b)
print("stamped", path, repr(text))
