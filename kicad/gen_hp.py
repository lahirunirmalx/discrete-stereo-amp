"""Headphone board (release 2): sits between the amp's speaker terminals and the speakers.
A DPDT slide switch sends each channel either to the speaker terminal or, through a series resistor (120 R, the
IEC 61938 value), to the 3.5 mm jack. Solder jumpers JP1/JP2 (open) bypass the resistors for low-impedance
headphones. J5 duplicates the jack pins (T, S, R) for a panel-mount jack. The jack's switch pins (TN, RN) are
not used: one normalling contact per channel cannot both cut the speaker AND leave the series resistor out of
the speaker path, so the switch does the routing (see docs/01-theory-of-operation.md).
Test points: TP1 GND, TP2 HP L, TP3 HP R (after the resistors)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import Gen, FP

g = Gen("Headphone board (release 2) - speaker / headphone switch, series resistors, 3.5 mm jack", paper="A4")
part, W, J, L, TP = g.part, g.W, g.J, g.label, g.tp
HERE = Path(__file__).parent


def gnd(x, y):
    g.s.place(g.L["GND"], "#PWR", "GND", x * 2.54, y * 2.54, 0)


# ---- from the amp
part("H3", "J1", "FROM AMP L-G-R", 6, 10, 0, FP["H3"], mirror="y", lbl="above")
W((8, 9), (11, 9)); L(11, 9, "IN_L")
W((8, 10), (11, 10)); L(11, 10, "GND")
W((8, 11), (11, 11)); L(11, 11, "IN_R")
g.text(2, 15, "J1 from the amp speaker terminals (SPK L, GND, SPK R), short wires. The amp output caps already block DC.", 1.0)
# ---- DPDT switch: pins 2 / 5 are the commons (amp), 1 / 4 speaker, 3 / 6 headphones
part("SW_DPDT", "SW1", "SPK / HP", 24, 12, 0, FP["SW_DPDT"], lbl=(20, 4))
# SW_Slide_DPDT at rot 0: pin 1 (22,10) 2 (22,12) 3 (22,14) on the left, 6 (26,10) 5 (26,12) 4 (26,14) on the right.
# The footprint numbers its pads the way the C&K drawing does (1-2-3 in one row, 6-5-4 under them), so the pads
# at the SAME END of the slider are 1 with 6 and 3 with 4: speakers on 1 / 6, headphones on 3 / 4.
W((22, 12), (19, 12)); L(19, 12, "IN_L", 180)
W((26, 12), (29, 12)); L(29, 12, "IN_R")
W((22, 10), (19, 10)); L(19, 10, "SPK_L", 180)
W((26, 10), (29, 10)); L(29, 10, "SPK_R")
W((22, 14), (19, 14)); L(19, 14, "HP_L", 180)
W((26, 14), (29, 14)); L(29, 14, "HP_R")
g.text(14, 18, "SW1: slider towards pins 1 / 6 = speakers, towards pins 3 / 4 = headphones (pins 2 / 5 are the commons). Any DPDT slide on a 2 x 3 pattern (2.5 mm pitch) fits.", 1.0)
# ---- series resistors with bypass jumpers, to the jack
for ref, jp, tp, sfx, yy in (("R1", "JP1", "TP2", "L", 23), ("R2", "JP2", "TP3", "R", 29)):
    L(36, yy, "HP_" + sfx, 180); W((36, yy), (38.5, yy))
    part("R", ref, "120", 40, yy, 90, FP["R"], lbl=(38.5, yy + 1.5))
    W((41.5, yy), (45, yy))
    part("JPO", jp, "DIRECT", 40, yy - 2.5, 0, FP["JP_OPEN"], lbl=(38.5, yy - 4.3))
    W((38.5, yy - 2.5), (37.5, yy - 2.5), (37.5, yy), ); J((37.5, yy))
    W((41.5, yy - 2.5), (42.5, yy - 2.5), (42.5, yy)); J((42.5, yy))
    TP(tp, "HP " + sfx, 44, yy - 2); W((44, yy - 2), (44, yy)); J((44, yy))
    L(45, yy, "JACK_" + sfx)
g.text(34, 33, "R1/R2 120 R (IEC 61938): 8 mW into 32 ohm phones at full drive, 4 mW into 250 ohm. Bridge JP1/JP2 for a direct, low-impedance output (loud: turn the volume down first). 330 R for sensitive in-ear phones.", 1.0)
# ---- jack: T = left, R = right, S = ground; TN / RN unused
part("JACK", "J4", "3.5mm TRS", 56, 24, 0, FP["JACK"], lbl=(52, 17))
# AudioJack3_SwitchTR at rot 0: pins on the right at x+2: S (58,23), R (58,24), RN (58,25), T (58,26), TN (58,27)
W((58, 26), (61, 26)); L(61, 26, "JACK_L")
W((58, 24), (61, 24)); L(61, 24, "JACK_R")
W((58, 23), (61, 23)); L(61, 23, "GND")
g.s.no_connect((58 * 2.54, 25 * 2.54)); g.s.no_connect((58 * 2.54, 27 * 2.54))
# ---- panel-mount jack header in parallel with the PCB jack
part("H3", "J5", "PANEL JACK T-G-R", 66, 12, 0, FP["H3"], lbl="above")
W((64, 11), (61, 11)); L(61, 11, "JACK_L", 180)
W((64, 12), (61, 12)); L(61, 12, "GND", 180)
W((64, 13), (61, 13)); L(61, 13, "JACK_R", 180)
g.text(54, 16, "J5: wire a panel-mount jack here instead of fitting J4 (tip = L, sleeve = G, ring = R).", 1.0)
# ---- speaker terminals
part("SCREW2", "J2", "SPK L", 6, 24, 0, FP["SCREW2"], mirror="y", lbl="above")
W((8, 24), (11, 24)); L(11, 24, "SPK_L")
W((8, 25), (11, 25)); L(11, 25, "GND")
part("SCREW2", "J3", "SPK R", 6, 30, 0, FP["SCREW2"], mirror="y", lbl="above")
W((8, 30), (11, 30)); L(11, 30, "SPK_R")
W((8, 31), (11, 31)); L(11, 31, "GND")
gnd(20, 38); W((20, 38), (20, 36)); L(20, 36, "GND", 90)
g.flag(22, 36.5); W((22, 36.5), (22, 37), (20, 37)); J((20, 37))
TP("TP1", "GND", 24, 35.5); W((24, 35.5), (24, 37), (22, 37)); J((22, 37))
out = g.write("hp", HERE / "hp")
print("wrote", out)
