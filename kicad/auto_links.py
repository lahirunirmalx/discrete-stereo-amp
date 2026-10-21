"""Turn every connection the single-sided router could not finish into a wire link.

Usage: /usr/bin/python3 auto_links.py board.kicad_pcb drc.json

Each "Missing connection" pair in the DRC report becomes a 2-hole footprint JLn
(net-tie pads on that net) with one hole on each unconnected item: a short wire
soldered between the holes closes the net. Pads are resolved to their real
centre; tracks use the DRC position (a point on that track). A pair that
involves the GND pour is handled by linking the nearest pads of two separate
pour fragments. A link hole may coincide with a component hole (the wire then
shares the hole with the lead). Run with /usr/bin/python3.
"""
import json
import math
import re
import sys
import pcbnew
from pcbnew import VECTOR2I, FromMM

board_path, drc_path = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard(board_path)
d = json.load(open(drc_path))
proto = pcbnew.FootprintLoad("/usr/share/kicad/footprints/Resistor_THT.pretty",
                             "R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal").Pads()[0]
n_links = sum(1 for f in b.GetFootprints() if f.GetReference().startswith("JL"))
added = 0
pads_by = {(f.GetReference(), p.GetNumber()): p for f in b.GetFootprints() for p in f.Pads()}


def add_link(net, a, c):
    global n_links, added
    n_links += 1
    fp = pcbnew.FOOTPRINT(b)
    fp.SetFPIDAsString("Custom:WireLink")
    fp.SetReference("JL%d" % n_links)
    fp.SetValue("wire link")
    fp.SetPosition(VECTOR2I(*a))
    for n, pt in enumerate((a, c), start=1):
        pad = pcbnew.PAD(fp)
        pad.SetAttribute(proto.GetAttribute()); pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        pad.SetSize(proto.GetSize()); pad.SetDrillSize(proto.GetDrillSize()); pad.SetLayerSet(proto.GetLayerSet())
        # a hole shared with a component lead keeps that pad's size: a wider annulus would short the
        # neighbouring pin on a 1.27 mm pitch part (TO-92)
        for q in pads_by.values():
            if abs(q.GetPosition().x - pt[0]) < 50000 and abs(q.GetPosition().y - pt[1]) < 50000 and q.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                pad.SetSize(q.GetSize()); pad.SetDrillSize(q.GetDrillSize()); pad.SetShape(q.GetShape())
        pad.SetNumber(str(n))
        pad.SetPosition(VECTOR2I(*pt))
        pad.SetNet(net)
        fp.Add(pad)
    fp.Reference().SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8)))
    fp.Reference().SetTextThickness(FromMM(0.12))
    fp.Reference().SetPosition(VECTOR2I(a[0], a[1] - FromMM(1.6)))
    b.Add(fp)
    added += 1
    print("link %s on %s: (%.1f, %.1f) -> (%.1f, %.1f)  %.1f mm" % (
        fp.GetReference(), net.GetNetname(), a[0] / 1e6, a[1] / 1e6, c[0] / 1e6, c[1] / 1e6, math.dist(a, c) / 1e6))


def resolve(item):
    desc = item.get("description", "")
    m = re.match(r"(?:PTH |NPTH )?[Pp]ad (\S+) \[([^\]]*)\] of (\S+)", desc)
    if m:
        pad = pads_by.get((m.group(3), m.group(1)))
        if pad is not None:
            return "pad", (pad.GetPosition().x, pad.GetPosition().y), m.group(2)
    m = re.match(r"Track \[([^\]]*)\]", desc)
    if m:
        return "track", (FromMM(item["pos"]["x"]), FromMM(item["pos"]["y"])), m.group(1)
    m = re.match(r"Zone \[([^\]]*)\]", desc)
    if m:
        return "zone", None, m.group(1)
    return None, None, None


def bridge_zone_fragments(net):
    """Link nearest pads of separate fill fragments until the pour is one piece."""
    zones = [z for z in b.Zones() if z.GetNetCode() == net.GetNetCode()]
    if not zones:
        return
    z = zones[0]
    polys = z.GetFilledPolysList(pcbnew.B_Cu)
    pads = [p for f in b.GetFootprints() for p in f.Pads()
            if p.GetNetCode() == net.GetNetCode() and p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
    frags = {}
    for p in pads:
        for i in range(polys.OutlineCount()):
            if polys.Contains(p.GetPosition(), i):
                frags.setdefault(i, []).append(p)
                break
    keys = sorted(frags, key=lambda k: -len(frags[k]))
    while len(keys) > 1:
        main, other = keys[0], keys[1]
        best = min(((math.dist((p.GetPosition().x, p.GetPosition().y), (q.GetPosition().x, q.GetPosition().y)), p, q)
                    for p in frags[main] for q in frags[other]), key=lambda t: t[0])
        add_link(net, (best[1].GetPosition().x, best[1].GetPosition().y), (best[2].GetPosition().x, best[2].GetPosition().y))
        frags[main] += frags.pop(other)
        keys = sorted(frags, key=lambda k: -len(frags[k]))


existing_links = set()
for f in b.GetFootprints():
    if f.GetReference().startswith("JL"):
        pts = tuple(sorted((p.GetPosition().x, p.GetPosition().y) for p in f.Pads()))
        existing_links.add(pts)
_add = add_link


def add_link(net, a, c):
    def same(p, q):
        return abs(p[0] - q[0]) < 50000 and abs(p[1] - q[1]) < 50000      # 50 um
    for pts in existing_links:
        if (same(pts[0], a) and same(pts[1], c)) or (same(pts[0], c) and same(pts[1], a)):
            return
    existing_links.add((a, c))
    _add(net, a, c)


conn = b.GetConnectivity()
tracks = [tr for tr in b.GetTracks() if tr.GetClass() == "PCB_TRACK"]


def pth_pads_near(kind, pos, netname, item_desc):
    """PTH pads of this net electrically joined to the item (a pad: itself; a track: every pad its
    copper cluster reaches). A hole shared with a pad adds no copper, so links between pads never
    collide with neighbouring tracks the way holes dropped on a track midpoint do."""
    if kind == "pad":
        here = [p for f in b.GetFootprints() for p in f.Pads()
                if abs(p.GetPosition().x - pos[0]) < 50000 and abs(p.GetPosition().y - pos[1]) < 50000]
        pth = [p for p in here if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
        if pth:
            return pth
        # an SMD twin pad: use the through-hole pads its copper cluster reaches instead of drilling through it
        out = []
        for p in here:
            out += [q for q in conn.GetConnectedPads(p) if q.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
        return out
    best = None
    for tr in tracks:
        if tr.GetNetname() == netname and tr.HitTest(VECTOR2I(*pos), FromMM(0.3)):
            best = tr; break
    if best is None:
        return []
    return [p for p in conn.GetConnectedPads(best) if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]


done_zone_nets = set()
for v in d.get("unconnected_items", []):
    items = v["items"]
    if len(items) != 2:
        continue
    refs = [re.search(r"of (J[LP]\d+)$", it.get("description", "")) for it in items]
    if all(refs) and refs[0].group(1) == refs[1].group(1):
        continue                      # the two ends of a wire link: the wire closes it
    (k1, p1, n1), (k2, p2, n2) = resolve(items[0]), resolve(items[1])
    netname = n1 or n2
    net = b.FindNet(netname) if netname else None
    if net is None:
        print("skip:", [it.get("description") for it in items])
        continue
    if "zone" in (k1, k2):
        if netname not in done_zone_nets:
            done_zone_nets.add(netname)
            bridge_zone_fragments(net)
        continue
    if p1 and p2:
        pa = pth_pads_near(k1, p1, netname, items[0]) or []
        pb = pth_pads_near(k2, p2, netname, items[1]) or []
        if pa and pb:
            pairs = [(math.dist((x.GetPosition().x, x.GetPosition().y), (y.GetPosition().x, y.GetPosition().y)), x, y)
                     for x in pa for y in pb if x is not y]
            if pairs:
                _, x, y = min(pairs, key=lambda q: q[0])
                p1, p2 = (x.GetPosition().x, x.GetPosition().y), (y.GetPosition().x, y.GetPosition().y)
        add_link(net, p1, p2)
pcbnew.SaveBoard(board_path, b)
print("added", added, "wire links")
