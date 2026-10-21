"""Summarise a kicad-cli DRC json. Wire-link covered gaps (single-sided boards) are not errors."""
import json, re, sys
from collections import Counter
import pcbnew
d = json.load(open(sys.argv[1]))
b = pcbnew.LoadBoard(sys.argv[2])
links = {f.GetReference(): [(p.GetPosition().x / 1e6, p.GetPosition().y / 1e6) for p in f.Pads()]
         for f in b.GetFootprints() if f.GetReference().startswith("JL")}
pads = {(f.GetReference(), p.GetNumber()): (p.GetPosition().x / 1e6, p.GetPosition().y / 1e6) for f in b.GetFootprints() for p in f.Pads()}
def pos_of(item):
    m = re.match(r"(?:PTH |NPTH )?[Pp]ad (\S+) \[[^\]]*\] of (\S+)", item.get("description", ""))
    if m and (m.group(2), m.group(1)) in pads:
        return pads[(m.group(2), m.group(1))]
    return (item["pos"]["x"], item["pos"]["y"])
def covered(items):
    a, c = pos_of(items[0]), pos_of(items[1])
    for ref, pts in links.items():
        hit = lambda p: any(abs(p[0] - q[0]) < 0.06 and abs(p[1] - q[1]) < 0.06 for q in pts)
        if hit(a) and hit(c):
            return ref
    return None
bad = 0; needed = set()
for key in ["violations", "unconnected_items", "schematic_parity"]:
    items = d.get(key, [])
    for (sev, desc), n in sorted(Counter((v["severity"], v["description"]) for v in items).items()):
        print("DRC %-18s %-7s x%-3d %s" % (key, sev, n, desc))
    for v in items:
        if v["severity"] != "error":
            continue
        if key == "unconnected_items" and links:
            descs = [i.get("description") or "" for i in v["items"]]
            if all(x.startswith("Zone [GND]") for x in descs):
                needed.add("GND pour pieces: JL links"); continue
            ref = covered(v["items"])
            if ref:
                needed.add(ref); continue
        bad += 1
        if bad <= 12:
            print("   ", v["description"], [(i.get("description"), i["pos"]) for i in v["items"]][:2])
if links:
    print("wire links to solder:", len(links), sorted(links)[:40])
print("DRC errors:", bad)
sys.exit(1 if bad else 0)
