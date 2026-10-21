"""Amp board placement: 90 x 60 mm, two channels side by side (L: x 0..45, R: x 45..90).
Top edge: the four output devices (TO-220 pattern, BD139/BD140) with their 3x3 pinout jumper blocks
below; then the bias/bootstrap/output passives; then the input/VAS stage; connectors along the bottom."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from pcbgen import pack, build
from common import FP

single = "--single" in sys.argv
HERE = Path(__file__).parent
BW, BH = 134.0, 72.0
place, texts = {}, []
R, R2W, C, CPS, CPM, CPL, Q, TP = FP["R"], FP["R_2W"], FP["C"], FP["CP_S"], FP["CP_M"], FP["CP_L"], FP["TO92"], FP["TP"]
probs = []


def region(items, x0, y0, w, h, gap=0.8):
    out, used = pack(items, x0, y0, w, h, gap=gap, back=single)
    place.update(out)
    return used


yend = 0
for b, xo, sfx in ((100, 0.0, "L"), (200, 67.0, "R")):
    # output devices along the top edge (pad 1 at the anchor), multiplier transistor beside them
    place["Q%d4" % b] = (xo + 8.0, 4.0, 0)
    place["Q%d5" % b] = (xo + 22.0, 4.0, 0)
    texts.append((xo + 9.5, 7.2, "Q%d4 NPN" % b, 0.9)); texts.append((xo + 24.5, 7.2, "Q%d5 PNP" % b, 0.9))
    # 3x3 jumper blocks: row = device pin 1/2/3, column = net E / C / B (bridged on the diagonal for BD139/BD140)
    for q, x0, rows in ((4, xo + 6.0, [(1, 2, 3), (4, 5, 6), (7, 8, 9)]),
                        (5, xo + 21.0, [(14, 15, 16), (11, 12, 13), (17, 18, 19)])):
        for r, refs in enumerate(rows):
            for c, k in enumerate(refs):
                place["JP%d%02d" % (b, k)] = (x0 + 4.0 + c * 3.8, 10.0 + r * 3.0, 0)
            texts.append((x0 + 0.8, 10.0 + r * 3.0, "%d" % (r + 1), 0.9))
        for c, name in enumerate(("E", "C", "B")):
            texts.append((x0 + 4.0 + c * 3.8, 8.3, name, 0.9))
    # bias multiplier resistors beside the blocks
    region([("Q%d6" % b, Q, 0), ("R%d09" % b, R, 90)], xo + 35.5, 0.6, 10.0, 13.0)
    region([("RV%d" % b, FP["TRIM"], 0)], xo + 35.5, 14.0, 11.4, 6.0)
    # then rows: bootstrap / output passives, emitter resistors, input-stage resistors, transistors
    y = 20.5
    for items in ([("R%d10" % b, R, 90), ("R%d11" % b, R, 90), ("R%d12" % b, R, 90), ("R%d15" % b, R, 90), ("C%d07" % b, C, 90),
                   ("C%d05" % b, CPM, 0), ("C%d06" % b, CPL, 0), ("TP%d3" % b, TP, 0), ("TP%d2" % b, TP, 0), ("R%d13" % b, R2W, 0)],
                  [("R%d14" % b, R2W, 0), ("R%d03" % b, R, 90), ("R%d01" % b, R, 90), ("R%d02" % b, R, 90),
                   ("R%d05" % b, R, 90), ("R%d06" % b, R, 90), ("R%d07" % b, R, 90), ("R%d04" % b, R, 90), ("R%d08" % b, R, 90)],
                  [("C%d01" % b, CPS, 0), ("TP%d1" % b, TP, 0), ("Q%d1" % b, Q, 0), ("Q%d2" % b, Q, 0), ("C%d02" % b, CPS, 0),
                   ("C%d03" % b, CPM, 0), ("Q%d3" % b, Q, 0), ("C%d04" % b, C, 0)]):
        used = region(items, xo + 0.6, y, 65.8, 30.0)
        y += used + 1.0
    yend = max(yend, y)
    texts.append((xo + 25, 19.0, "CH %s" % sfx, 1.3))
# shared row along the bottom edge: terminals face outward (rot 180 = wire entry towards the bottom edge)
BH = round(yend + 14.0)
yt = BH - 6.5
# screw terminals: rot 0 puts the wire entry towards the bottom edge (verified on the 3D render; rot 180 was backwards)
place["J1"] = (11.0, yt, 0); texts.append((11.0, yt - 7.0, "12V IN", 0.9))
place["J3"] = (26.0, yt, 0); texts.append((26.0, yt - 7.0, "SPK L", 0.9))
place["J4"] = (121.0, yt, 0); texts.append((121.0, yt - 7.0, "SPK R", 0.9))
place["J2"] = (63.0, BH - 2.5, 90); texts.append((67.0, BH - 6.5, "IN L G R", 0.9))
place["C1"] = (42.0, yt - 1.5, 0)
place["C2"] = (50.0, yt + 1.5, 90)
place["TP1"] = (54.5, yt - 3.5, 0); texts.append((54.5, yt - 5.7, "+12V", 0.9))
place["TP2"] = (54.5, yt + 1.5, 0); texts.append((58.0, yt + 1.8, "GND", 0.9))
print("board height", BH)
stem = "amp_1layer" if single else "amp"
bad = build(HERE / "amp/amp.net", place, BW, BH, HERE / "amp" / (stem + ".kicad_pcb"),
            "STEREO AMP 12V", single=single, scale=(1.45, 1.45), texts=texts, title_at=(90.0, BH - 3.0))
sys.exit(1 if bad else 0)
