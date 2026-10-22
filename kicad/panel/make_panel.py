"""Square panel with rails: amp (134 mm wide) on top, PSU below it on the left, headphone board and volume board
stacked on the right (30 + 2 + 26 = 58 mm = PSU height); 3 mm rails all round stretched so the outline is square;
mouse-bite tabs between boards and to the rails.

Usage: ~/tools/kikit-venv/bin/python make_panel.py out.kicad_pcb amp.kicad_pcb psu.kicad_pcb vol.kicad_pcb hp.kicad_pcb
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import STAMP, REPO
import pcbnew
from pcbnew import VECTOR2I, FromMM
from shapely.geometry import box
from kikit import panelize
from kikit.substrate import Substrate
from kikit.units import mm

GAP, RAIL, TAB_W, HOLE, PITCH = 2 * mm, 3 * mm, 4 * mm, 0.5 * mm, 0.8 * mm


def size(path):
    bb = pcbnew.LoadBoard(str(path)).GetBoardEdgesBoundingBox()
    return bb.GetWidth(), bb.GetHeight()


def main(out, amp, psu, vol, hp):
    panel = panelize.Panel(out)
    aw, ah = size(amp); pw, ph = size(psu); vw, vh = size(vol); hw, hh = size(hp)
    # amp on top; PSU and volume board side by side below it (their widths add up to the amp's)
    panel.appendBoard(amp, VECTOR2I(0, 0), origin=panelize.Origin.TopLeft, tolerance=FromMM(1))
    panel.appendBoard(psu, VECTOR2I(0, int(ah + GAP)), origin=panelize.Origin.TopLeft, tolerance=FromMM(1))
    # headphone board above the volume board: the pot shaft hangs off the bottom rail, the jack nose stays inside the gap
    panel.appendBoard(hp, VECTOR2I(int(pw + GAP), int(ah + GAP)), origin=panelize.Origin.TopLeft, tolerance=FromMM(1))
    panel.appendBoard(vol, VECTOR2I(int(pw + GAP), int(ah + GAP + hh + GAP)), origin=panelize.Origin.TopLeft, tolerance=FromMM(1))
    bb = panel.boardSubstrate.bounds()
    inner_w, inner_h = bb[2] - bb[0], bb[3] - bb[1]
    side = int(max(inner_w, inner_h) + 2 * (GAP + RAIL))
    # ghost rails so the tab builder attaches every board to the frame; makeFrame draws the real ones
    x0, y0 = bb[0] - GAP - RAIL, bb[1] - GAP - RAIL
    x1, y1 = x0 + side, y0 + side
    rails = [box(x0, y0, x1, y0 + RAIL), box(x0, y1 - RAIL, x1, y1), box(x0, y0, x0 + RAIL, y1), box(x1 - RAIL, y0, x1, y1)]
    ghosts = []
    for r in rails:
        s = Substrate([]); s.union(r); ghosts.append(s)
    panel.buildPartitionLineFromBB(ghosts)
    panel.buildTabAnnotationsFixed(hcount=3, vcount=2, hwidth=TAB_W, vwidth=TAB_W, minDistance=5 * mm, ghostSubstrates=ghosts)
    cuts = panel.buildTabsFromAnnotations(fillet=0)
    frame_cuts = panel.makeFrame(RAIL, RAIL, GAP, GAP, minWidth=side, minHeight=side)
    panel.makeMouseBites(cuts, HOLE, PITCH, offset=int(0.2 * mm), prolongation=int(0.5 * mm))
    panel.addMillFillets(1 * mm)
    try:
        panel.save()
    except RuntimeError as e:
        print("kikit:", e)
    b = pcbnew.LoadBoard(out)
    ds = b.GetDesignSettings()
    ds.m_CopperEdgeClearance = FromMM(0.5); ds.m_MinResolvedSpokes = 1
    ds.m_MinClearance = FromMM(0.19); ds.m_NetSettings.GetDefaultNetclass().SetClearance(FromMM(0.19))
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    # rail texts: project name on the top rail, repository and revision on the bottom rail
    bb = b.GetBoardEdgesBoundingBox()
    for text, y in (("STEREO AMP + PSU + VOLUME + HEADPHONE  " + STAMP + "  CC BY-NC-SA 4.0", 1.5), (REPO + "  " + STAMP, bb.GetHeight() / 1e6 - 1.5)):
        tx = pcbnew.PCB_TEXT(b); tx.SetText(text); tx.SetLayer(pcbnew.F_SilkS)
        tx.SetTextSize(VECTOR2I(FromMM(1.5), FromMM(1.5))); tx.SetTextThickness(FromMM(0.15))
        tx.SetPosition(VECTOR2I(bb.GetLeft() + bb.GetWidth() // 2, bb.GetTop() + FromMM(y))); b.Add(tx)
    pcbnew.SaveBoard(out, b)
    b = pcbnew.LoadBoard(out)
    bb = b.GetBoardEdgesBoundingBox()
    npth = sum(1 for f in b.GetFootprints() for p in f.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH)
    print("panel %s: %.1f x %.1f mm, %d tab cuts, %d mouse-bite holes" % (out, bb.GetWidth() / mm, bb.GetHeight() / mm, len(cuts), npth))


if __name__ == "__main__":
    main(*sys.argv[1:6])
