"""Board builder for the stereo amp project (run with /usr/bin/python3, needs pcbnew 9).

Builds a .kicad_pcb from a KiCad netlist + a placement description, with:
  - hybrid footprints (through-hole pattern + 1206 / SOD / SMA / SOT-23 twin on the same copper),
  - net-tie solder jumpers straight from the library (3x3 pinout blocks),
  - 2-layer (default) or single-layer (--single: copper on B.Cu, SMD twins on the back, multi-pin
    SMD twins dropped, board scaled up) variants,
  - Specctra DSN export for freerouting with the boundary pulled in by the edge clearance.
Placement is a dict ref -> (x, y, rot) in mm relative to the board origin, built by the per-board
scripts with pack() (shelf packing of a group into a rectangle, using real courtyards).
"""
import re
import sys
from pathlib import Path
import pcbnew
from pcbnew import VECTOR2I, FromMM

FPDIR = "/usr/share/kicad/footprints/"

HYBRIDS = {
    "Custom:R_Axial_1206": dict(tht=("Resistor_THT", "R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"),
                                smd=("Resistor_SMD", "R_1206_3216Metric_Pad1.30x1.75mm_HandSolder"),
                                at=(3.81, 0), oval=3.8, mirror=False),
    "Custom:C_P5_1206": dict(tht=("Capacitor_THT", "C_Disc_D5.0mm_W2.5mm_P5.00mm"),
                             smd=("Capacitor_SMD", "C_1206_3216Metric_Pad1.33x1.80mm_HandSolder"),
                             at=(2.5, 0), oval=None, mirror=False),
    "Custom:CE_P2_1206": dict(tht=("Capacitor_THT", "CP_Radial_D5.0mm_P2.00mm"),
                              smd=("Capacitor_SMD", "C_1206_3216Metric_Pad1.33x1.80mm_HandSolder"),
                              at=(1.0, 0), oval=None, mirror=False),
    "Custom:D_DO35_SOD123": dict(tht=("Diode_THT", "D_DO-35_SOD27_P7.62mm_Horizontal"),
                                 smd=("Diode_SMD", "D_SOD-123"),
                                 at=(3.81, 0), oval=3.8, mirror=False),
    "Custom:D_DO41_SMA": dict(tht=("Diode_THT", "D_DO-41_SOD81_P10.16mm_Horizontal"),
                              smd=("Diode_SMD", "D_SMA_Handsoldering"),
                              at=(5.08, 0), oval=3.8, mirror=False),
    "Custom:D_DO201_SMA": dict(tht=("Diode_THT", "D_DO-201AD_P12.70mm_Horizontal"),
                               smd=("Diode_SMD", "D_SMA_Handsoldering"),
                               at=(6.35, 0), oval=None, mirror=False),
    "Custom:TO92_SOT23": dict(tht=("Package_TO_SOT_THT", "TO-92_Inline"),
                              smd=("Package_TO_SOT_SMD", "SOT-23_Handsoldering"),
                              at=(1.27, 4.0), oval=None, mirror=True, single=False),
}


def _sexp(text):
    tokens = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    stack = [[]]
    for tok in tokens:
        if tok == "(":
            stack.append([])
        elif tok == ")":
            node = stack.pop()
            stack[-1].append(node)
        else:
            stack[-1].append(tok)
    return stack[0]


def _emit(node):
    if isinstance(node, str):
        return node
    return "(" + " ".join(_emit(x) for x in node) + ")"


def shrink_boundary(dsn_path, margin_mm=0.6):
    txt = open(dsn_path).read()
    m = re.search(r'\(boundary\s*\(path pcb 0((?:\s+-?\d+)+)\s*\)', txt)
    nums = [int(v) for v in m.group(1).split()]
    xs, ys = nums[0::2], nums[1::2]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    d = int(margin_mm * 1000)
    out = []
    for x, y in zip(xs, ys):
        out += [x - d if x > cx else x + d, y - d if y > cy else y + d]
    txt = txt[:m.start()] + "(boundary (path pcb 0 " + " ".join(str(v) for v in out) + ")" + txt[m.end():]
    txt = txt.replace("(clearance 200)", "(clearance 250)", 1)
    open(dsn_path, "w").write(txt)


def strip_front_layer(dsn_path):
    raw = open(dsn_path).read().replace('(string_quote ")', '(string_quote QUOTEMARK)')
    tree = _sexp(raw)

    def keep(node):
        if not isinstance(node, list) or not node:
            return True
        if node[0] == "layer" and len(node) > 1 and node[1] == "F.Cu":
            return False
        if node[0] == "shape" and len(node) > 1 and isinstance(node[1], list) and len(node[1]) > 1 and node[1][1] == "F.Cu":
            return False
        if node[0] in ("circle", "rect", "polygon", "path") and len(node) > 1 and node[1] == "F.Cu":
            return False
        return True

    def walk(node):
        if isinstance(node, list):
            node[:] = [x for x in node if keep(x)]
            for x in node:
                walk(x)
            node[:] = [x for x in node if not (isinstance(x, list) and x and x[0] == "keepout"
                                               and not any(isinstance(y, list) for y in x))]
    walk(tree)
    txt = _emit(tree[0]).replace("(index 1)", "(index 0)", 1).replace("(string_quote QUOTEMARK)", '(string_quote ")')
    open(dsn_path, "w").write(txt)


def make_hybrid(board, name, back):
    """Library through-hole footprint (keeps its silkscreen: diode bar, + mark, TO-92 D-shape, and its
    rectangular pin-1 pad) plus the SMD twin's pads numbered "<n>S" on the same net. Round THT pads become
    3.8 mm ovals so the 1206 / SOD / SMA pads overlap them and need no routing; rectangular (pin 1) pads
    keep their shape. On the single-sided board the SMD pads go to the back and multi-pin twins are dropped."""
    spec = HYBRIDS[name]
    tlib, tname = spec["tht"]
    slib, sname = spec["smd"]
    fp = pcbnew.FootprintLoad(FPDIR + tlib + ".pretty", tname)
    fp.SetFPIDAsString(name)
    smd = pcbnew.FootprintLoad(FPDIR + slib + ".pretty", sname)
    for q in fp.Pads():
        if spec["oval"] and q.GetShape() != pcbnew.PAD_SHAPE_RECT and q.GetShape() != pcbnew.PAD_SHAPE_ROUNDRECT:
            q.SetShape(pcbnew.PAD_SHAPE_OVAL)
            q.SetSize(VECTOR2I(FromMM(spec["oval"]), FromMM(1.6)))
    ax, ay = spec["at"]
    back_set = pcbnew.LSET()
    for l in (pcbnew.B_Cu, pcbnew.B_Mask, pcbnew.B_Paste):
        back_set.AddLayer(l)
    for p in (smd.Pads() if (spec.get("single", True) or not back) else []):
        q = pcbnew.PAD(fp)
        q.SetAttribute(pcbnew.PAD_ATTRIB_SMD); q.SetShape(p.GetShape()); q.SetSize(p.GetSize())
        q.SetLayerSet(back_set if back else p.GetLayerSet())
        q.SetNumber(p.GetNumber() + "S")
        q.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
        px, py = p.GetPosition().x / 1e6, p.GetPosition().y / 1e6
        if back and spec["mirror"]:
            px = -px
        q.SetPosition(VECTOR2I(FromMM(ax + px), FromMM(ay + py)))
        fp.Add(q)
    # courtyard: the library one plus every pad, so pack() keeps neighbours clear of the SMD twin
    xs, ys = [], []
    for item in fp.GraphicalItems():
        if item.GetLayer() == pcbnew.F_CrtYd:
            bb = item.GetBoundingBox()
            xs += [bb.GetLeft() / 1e6, bb.GetRight() / 1e6]; ys += [bb.GetTop() / 1e6, bb.GetBottom() / 1e6]
            item.SetLayer(pcbnew.Cmts_User)      # park it: Remove() on a board-less footprint corrupts memory in the 9.0 bindings
    for q in fp.Pads():
        cx, cy = q.GetPosition().x / 1e6, q.GetPosition().y / 1e6
        hx, hy = q.GetSize().x / 2e6 + 0.5, q.GetSize().y / 2e6 + 0.5
        xs += [cx - hx, cx + hx]; ys += [cy - hy, cy + hy]
    r = pcbnew.PCB_SHAPE(fp, pcbnew.SHAPE_T_RECT)
    r.SetStart(VECTOR2I(FromMM(min(xs)), FromMM(min(ys)))); r.SetEnd(VECTOR2I(FromMM(max(xs)), FromMM(max(ys))))
    r.SetLayer(pcbnew.F_CrtYd); r.SetWidth(FromMM(0.05)); fp.Add(r)
    for item in fp.GraphicalItems():
        if item.GetLayer() == pcbnew.Edge_Cuts:
            item.SetLayer(pcbnew.Cmts_User)
    return fp


def parse_netlist(path):
    txt = Path(path).read_text()
    comps = {}
    ctxt = txt[txt.find("(components"):txt.find("(libparts")]
    for chunk in ctxt.split("(comp (ref ")[1:]:
        ref = re.match(r'"([^"]+)"', chunk).group(1)
        val = re.search(r'\(value "([^"]*)"\)', chunk).group(1)
        fp = re.search(r'\(footprint "([^"]*)"\)', chunk).group(1)
        ts = re.findall(r'\(tstamps "([^"]+)"\)', chunk)[-1]
        comps[ref] = (val, fp, ts)
    nets = {}
    ntxt = txt[txt.find("(nets"):]
    for chunk in ntxt.split("(net (code")[1:]:
        name = re.search(r'\(name "([^"]+)"\)', chunk).group(1)
        nets[name] = re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', chunk)
    return comps, nets


_fp_cache = {}


def _pads_to_back(fp):
    """Single-layer board: an SMD-only part (solder jumper) lives on the copper side. Rather than flipping
    the footprint (the DSN exporter then describes its pads as top-side padstacks with a 'back' placement,
    which the front-layer strip destroys), keep it front-placed and move every pad and copper graphic to
    the back layers, exactly like the hybrid footprints' SMD twins."""
    back = pcbnew.LSET()
    for l in (pcbnew.B_Cu, pcbnew.B_Mask, pcbnew.B_Paste):
        back.AddLayer(l)
    for pad in fp.Pads():
        pad.SetLayerSet(back)
    swap = {pcbnew.F_Cu: pcbnew.B_Cu, pcbnew.F_Mask: pcbnew.B_Mask, pcbnew.F_SilkS: pcbnew.B_SilkS,
            pcbnew.F_CrtYd: pcbnew.B_CrtYd, pcbnew.F_Fab: pcbnew.B_Fab}
    for item in fp.GraphicalItems():
        if item.GetLayer() in swap:
            item.SetLayer(swap[item.GetLayer()])


def _place_reference(fp, cy, ref):
    """Readable silkscreen: the reference sits INSIDE the part outline, along its long axis, as large as
    the outline allows (0.7 to 1.0 mm). Parts with no room (TO-92, test points, headers, jumpers) keep
    the label just outside the courtyard, alternating above / below so neighbours do not collide."""
    r = fp.Reference()
    w, h = cy.GetWidth() / 1e6, cy.GetHeight() / 1e6
    along, across = max(w, h), min(w, h)
    chars = len(ref)
    size = min(1.0, max(0.7, (along - 1.0) / (chars * 0.85)))
    fpid = fp.GetFPIDAsString()
    round_body = "CP_Radial" in fpid or "CE_P2" in fpid or "LED" in fpid
    if across >= 2.6 and along >= chars * 0.7 * 0.85 + 1.0 and not round_body and not ref.startswith(("Q", "TP", "J", "RV", "F")):
        r.SetTextSize(VECTOR2I(FromMM(size), FromMM(size)))
        r.SetTextThickness(FromMM(0.15 if size >= 0.9 else 0.12))
        r.SetPosition(VECTOR2I(cy.GetCenter().x, cy.GetCenter().y))
        r.SetTextAngleDegrees(90 if h > w else 0)
        return
    r.SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8)))
    r.SetTextThickness(FromMM(0.12))
    n = getattr(_place_reference, "_n", 0) + 1
    _place_reference._n = n
    if n % 2 == 0:
        r.SetPosition(VECTOR2I(cy.GetCenter().x, cy.GetBottom() + FromMM(0.6)))
    else:
        r.SetPosition(VECTOR2I(cy.GetCenter().x, cy.GetTop() - FromMM(0.6)))
    r.SetTextAngleDegrees(0)


def _flip_dir():
    """KiCad 9 wants a FLIP_DIRECTION enum; older bindings took a bool."""
    for n in dir(pcbnew):
        if n.startswith("FLIP_DIRECTION") and "TOP" in n.upper():
            return getattr(pcbnew, n)
    return False


def load_fp(board, fpname, back=False):
    if fpname in HYBRIDS:
        return make_hybrid(board, fpname, back)
    lib, name = fpname.split(":")
    fp = pcbnew.FootprintLoad(FPDIR + lib + ".pretty", name)
    if fp is None:
        sys.exit("footprint not found: " + fpname)
    fp.SetFPIDAsString(fpname)
    # a footprint may carry Edge.Cuts graphics (the RK097 pot does): they would break the board outline
    for item in fp.GraphicalItems():
        if item.GetLayer() == pcbnew.Edge_Cuts:
            item.SetLayer(pcbnew.Cmts_User)
    return fp


def courtyard_size(fpname, rot=0, back=False):
    """(w, h, dx, dy): courtyard extent and the offset of its centre from the anchor, after rotation."""
    key = (fpname, rot, back)
    if key in _fp_cache:
        return _fp_cache[key]
    b = pcbnew.BOARD()
    fp = load_fp(b, fpname, back)
    fp.SetOrientationDegrees(rot)
    if hasattr(fp, "BuildCourtyardCaches"):
        fp.BuildCourtyardCaches()
    bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
    r = (bb.GetWidth() / 1e6, bb.GetHeight() / 1e6, bb.GetCenter().x / 1e6, bb.GetCenter().y / 1e6)
    _fp_cache[key] = r
    return r


def pack(items, x0, y0, w, h, gap=0.8, back=False, align="left"):
    """Shelf-pack [(ref, fpname, rot), ...] into the rectangle. Returns {ref: (x, y, rot)} of anchors
    and the used height. Items are placed in order, rows top to bottom."""
    out = {}
    x, y, row_h = x0, y0, 0
    for ref, fpname, rot in items:
        cw, ch, cx, cy = courtyard_size(fpname, rot, back)
        if x + cw > x0 + w + 1e-6 and x > x0:
            x, y, row_h = x0, y + row_h + gap, 0
        if cw > w + 1e-6:
            print("pack: %s (%.1f mm) wider than its region (%.1f mm)" % (ref, cw, w))
        # anchor so the courtyard's top-left lands at (x, y)
        ax, ay = x + cw / 2 - cx, y + ch / 2 - cy
        out[ref] = (round(ax, 2), round(ay, 2), rot)
        x += cw + gap
        row_h = max(row_h, ch)
    used = y + row_h - y0
    if used > h + 1e-6:
        print("pack: region (%g,%g %gx%g) overflows: needs %.1f mm height" % (x0, y0, w, h, used))
    return out, used


def build(netfile, place, bw, bh, out_path, title, single=False, scale=(1.0, 1.0), texts=(), bx=50.0, by=50.0,
          allow_offboard=(), track=0.4, clearance=0.19, mount_holes=True, title_at=None, back_texts=()):
    """place: {ref: (x, y, rot)} relative to the board origin (bx, by)."""
    sx, sy = scale if single else (1.0, 1.0)
    BW, BH = round(bw * sx, 1), round(bh * sy, 1)
    comps, nets = parse_netlist(netfile)
    board = pcbnew.BOARD()
    ds = board.GetDesignSettings()
    ds.SetCustomTrackWidth(FromMM(track)); ds.SetCustomViaSize(FromMM(0.9)); ds.SetCustomViaDrill(FromMM(0.5))
    ds.UseCustomTrackViaSize(True)
    ds.m_MinClearance = FromMM(0.15 if single else clearance)
    ds.m_CopperEdgeClearance = FromMM(0.5)
    ds.m_MinResolvedSpokes = 1
    dflt = ds.m_NetSettings.GetDefaultNetclass()
    dflt.SetClearance(FromMM(0.15 if single else clearance))
    dflt.SetTrackWidth(FromMM(track)); dflt.SetViaDiameter(FromMM(0.9)); dflt.SetViaDrill(FromMM(0.5))
    pts = [(bx, by), (bx + BW, by), (bx + BW, by + BH), (bx, by + BH)]
    for a, b in zip(pts, pts[1:] + pts[:1]):
        seg = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(VECTOR2I(FromMM(a[0]), FromMM(a[1]))); seg.SetEnd(VECTOR2I(FromMM(b[0]), FromMM(b[1])))
        seg.SetLayer(pcbnew.Edge_Cuts); seg.SetWidth(FromMM(0.1)); board.Add(seg)
    netitems = {}
    for name in nets:
        ni = pcbnew.NETINFO_ITEM(board, name); board.Add(ni); netitems[name] = ni
    pin_net = {(ref, pin): name for name, nodes in nets.items() for ref, pin in nodes}
    missing = [r for r in comps if r not in place]
    extra = [r for r in place if r not in comps]
    if missing or extra:
        sys.exit("placement table mismatch: missing %s extra %s" % (missing, extra))
    bridged = {}
    for ref, (val, fpname, ts) in comps.items():
        if fpname.endswith("Bridged_Pad1.0x1.5mm"):
            bridged[ref] = fpname
            fpname = fpname.replace("Bridged", "Open")
        fp = load_fp(board, fpname, back=single)
        fp.SetReference(ref); fp.SetValue(val); fp.SetPath(pcbnew.KIID_PATH("/" + ts))
        x, y, rot = place[ref]
        fp.SetPosition(VECTOR2I(FromMM(bx + x * sx), FromMM(by + y * sy)))
        fp.SetOrientationDegrees(rot)
        for pad in fp.Pads():
            num = pad.GetNumber()
            key = (ref, num[:-1] if num.endswith("S") else num)
            if key in pin_net:
                pad.SetNet(netitems[pin_net[key]])
                if single and pin_net[key] == "GND":
                    pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
        fp.Reference().SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8)))
        fp.Reference().SetTextThickness(FromMM(0.12))
        if ref.startswith("JP"):
            fp.Reference().SetVisible(False)
        board.Add(fp)
        if single and fpname.startswith("Jumper:"):
            _pads_to_back(fp)
        if hasattr(fp, "BuildCourtyardCaches"):
            fp.BuildCourtyardCaches()
        cy = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
        if cy.GetWidth() == 0:
            cy = fp.GetCourtyard(pcbnew.B_CrtYd).BBox()
        _place_reference(fp, cy, ref)
    for (x, y, s, size) in texts:
        t = pcbnew.PCB_TEXT(board)
        t.SetText(s); t.SetPosition(VECTOR2I(FromMM(bx + x * sx), FromMM(by + y * sy)))
        t.SetLayer(pcbnew.F_SilkS); t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); t.SetTextThickness(FromMM(0.15))
        board.Add(t)
    for (x, y, s, size) in back_texts:
        # readable from the back: KiCad mirrors text on B.SilkS when asked to
        t = pcbnew.PCB_TEXT(board)
        t.SetText(s); t.SetPosition(VECTOR2I(FromMM(bx + x * sx), FromMM(by + y * sy)))
        t.SetLayer(pcbnew.B_SilkS); t.SetMirrored(True)
        t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); t.SetTextThickness(FromMM(0.15))
        board.Add(t)
    if mount_holes:
        for i, (hx, hy) in enumerate([(bx + 2.5, by + 2.5), (bx + BW - 2.5, by + 2.5), (bx + 2.5, by + BH - 2.5), (bx + BW - 2.5, by + BH - 2.5)], start=1):
            fp = pcbnew.FOOTPRINT(board); fp.SetFPIDAsString("Custom:Hole_2.5mm"); fp.SetReference("H%d" % i); fp.SetValue("M2.5")
            pad = pcbnew.PAD(fp); pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH); pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
            pad.SetSize(VECTOR2I(FromMM(2.5), FromMM(2.5))); pad.SetDrillSize(VECTOR2I(FromMM(2.5), FromMM(2.5))); pad.SetNumber(""); fp.Add(pad)
            c = pcbnew.PCB_SHAPE(fp, pcbnew.SHAPE_T_CIRCLE); c.SetCenter(VECTOR2I(0, 0)); c.SetEnd(VECTOR2I(FromMM(2.0), 0))
            c.SetLayer(pcbnew.F_CrtYd); c.SetWidth(FromMM(0.05)); fp.Add(c)
            fp.Reference().SetVisible(False); fp.SetPosition(VECTOR2I(FromMM(hx), FromMM(hy))); board.Add(fp)
    tx, ty = title_at or (BW / 2, BH - 1.6)
    t = pcbnew.PCB_TEXT(board); t.SetText(title); t.SetPosition(VECTOR2I(FromMM(bx + tx * sx), FromMM(by + ty * sy)))
    t.SetLayer(pcbnew.F_SilkS); t.SetTextSize(VECTOR2I(FromMM(1.5), FromMM(1.5))); t.SetTextThickness(FromMM(0.2)); board.Add(t)
    # courtyard overlap / edge check
    boxes = []
    for fp in board.GetFootprints():
        if hasattr(fp, "BuildCourtyardCaches"):
            fp.BuildCourtyardCaches()
        cyb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
        if cyb.GetWidth() == 0:
            cyb = fp.GetCourtyard(pcbnew.B_CrtYd).BBox()
        boxes.append((fp.GetReference(), cyb))
    bad = 0
    for i, (r, b) in enumerate(boxes):
        if r not in allow_offboard and (b.GetLeft() < FromMM(bx) or b.GetRight() > FromMM(bx + BW) or b.GetTop() < FromMM(by) or b.GetBottom() > FromMM(by + BH)):
            print("OFF BOARD:", r, "x %.1f..%.1f y %.1f..%.1f" % (b.GetLeft() / 1e6 - bx, b.GetRight() / 1e6 - bx, b.GetTop() / 1e6 - by, b.GetBottom() / 1e6 - by)); bad += 1
        for r2, b2 in boxes[i + 1:]:
            if b.Intersects(b2):
                print("OVERLAP:", r, r2); bad += 1
    dsn = str(Path(out_path).with_suffix(".dsn"))
    pcbnew.ExportSpecctraDSN(board, dsn)
    shrink_boundary(dsn)
    if single:
        lset = pcbnew.LSET()
        for l in board.GetEnabledLayers().Seq():
            if l != pcbnew.F_Cu:
                lset.AddLayer(l)
        board.SetEnabledLayers(lset); board.SetCopperLayerCount(1)
        strip_front_layer(dsn)
    for fp in list(board.GetFootprints()):
        ref = fp.GetReference()
        if ref in bridged:
            nb = load_fp(board, bridged[ref], back=single)
            nb.SetReference(ref); nb.SetValue(fp.GetValue()); nb.SetPath(fp.GetPath())
            nb.SetPosition(fp.GetPosition()); nb.SetOrientation(fp.GetOrientation())
            flipped = single
            for pad in nb.Pads():
                old_pad = [p for p in fp.Pads() if p.GetNumber() == pad.GetNumber()][0]
                pad.SetNet(old_pad.GetNet())
            nb.Reference().SetVisible(False)
            board.Remove(fp); board.Add(nb)
            if flipped:
                _pads_to_back(nb)
    pcbnew.SaveBoard(str(out_path), board)
    print("wrote", out_path, "%gx%g mm" % (BW, BH), "footprints:", len(comps), "nets:", len(nets), "placement problems:", bad)
    return bad
