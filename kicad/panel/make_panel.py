"""Pack the amp, PSU and volume boards into one panel with mouse-bite tabs (multi-design panel).

Usage: ~/tools/kikit-venv/bin/python make_panel.py out.kicad_pcb amp.kicad_pcb psu.kicad_pcb vol.kicad_pcb
Layout: amp on top, PSU under it (both 100 mm wide), the small volume board at the right of the PSU.
2 mm gaps, 4 mm tabs, 0.5 mm mouse bites at 0.8 mm pitch, 1 mm mill fillets, no frame rails.
Run with the kikit venv python (needs pcbnew 9 + kikit 1.8).
"""
import sys
from pathlib import Path
import pcbnew
from pcbnew import VECTOR2I, FromMM
from kikit import panelize
from kikit.units import mm

GAP, TAB_W, HOLE, PITCH = 2 * mm, 4 * mm, 0.5 * mm, 0.8 * mm


def size(path):
    bb = pcbnew.LoadBoard(str(path)).GetBoardEdgesBoundingBox()
    return bb.GetWidth(), bb.GetHeight()


def main(out, amp, psu, vol):
    panel = panelize.Panel(out)
    aw, ah = size(amp); pw, ph = size(psu); vw, vh = size(vol)
    placed = []
    for path, x, y in ((amp, 0, 0), (psu, 0, ah + GAP), (vol, pw + GAP, ah + GAP)):
        panel.appendBoard(path, VECTOR2I(int(x), int(y)), origin=panelize.Origin.TopLeft, tolerance=FromMM(1))
        placed.append((Path(path).name, x / mm, y / mm))
    panel.buildPartitionLineFromBB()
    panel.buildTabAnnotationsFixed(hcount=3, vcount=2, hwidth=TAB_W, vwidth=TAB_W, minDistance=5 * mm, ghostSubstrates=[])
    cuts = panel.buildTabsFromAnnotations(fillet=0)
    panel.makeMouseBites(cuts, HOLE, PITCH, offset=int(0.2 * mm), prolongation=int(0.5 * mm))
    panel.addMillFillets(1 * mm)
    try:
        panel.save()
    except RuntimeError as e:
        # the board file is written before KiKit tries to merge the source projects' DRC rules; a
        # multi-design panel has no single rule set to merge, so the rules are set explicitly below
        print("kikit:", e)
    b = pcbnew.LoadBoard(out)
    ds = b.GetDesignSettings()
    ds.m_CopperEdgeClearance = FromMM(0.5)
    ds.m_MinResolvedSpokes = 1
    ds.m_MinClearance = FromMM(0.19)
    ds.m_NetSettings.GetDefaultNetclass().SetClearance(FromMM(0.19))
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(out, b)
    b = pcbnew.LoadBoard(out)
    bb = b.GetBoardEdgesBoundingBox()
    npth = sum(1 for f in b.GetFootprints() for p in f.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH)
    print("panel %s: %.1f x %.1f mm, %d tab cuts, %d mouse-bite holes" % (out, bb.GetWidth() / mm, bb.GetHeight() / mm, len(cuts), npth))
    for name, x, y in placed:
        print("  %-20s at (%5.1f, %5.1f)" % (name, x, y))


if __name__ == "__main__":
    main(*sys.argv[1:5])
