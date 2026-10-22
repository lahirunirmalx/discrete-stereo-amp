"""Stereo amp board schematic (release 2): two identical class-AB channels + shared power/IO.

Per channel (b = 100 for L, 200 for R), deck names in brackets (sim/amp2_final.cir):
  C{b}01 in cap [Cin], R{b}01/02 bias divider [Rb1/Rb2], C{b}02 [Cbias], R{b}03 base feed [R3],
  Q{b}1/Q{b}2 BC557 PNP diff pair, Q{b}9 BC557 current-source tail with R{b}04 1.2k [Rt] and the red LED
  D{b}01 [Dled] fed by R{b}05 4.7k [Rled]; Q{b}7/Q{b}8 BC547 current-mirror load with R{b}16/R{b}17 100 R [Re7/Re8];
  Q{b}3 BC547 NPN VAS with R{b}08 47 R [Re3], C{b}04 220p Miller [Cm]; R{b}06/R{b}07/C{b}03 feedback [Rf/Rg/Cg]
  (gain 23) with C{b}08 47p lead cap [Cf]; Q{b}6 Vbe multiplier with R{b}09 + RV{b} + R{b}10 [Rm1/RV/Rm2];
  R{b}11/R{b}12/C{b}05 bootstrapped VAS load from +12V [R5a/R5b/Cboot]; Q{b}4 BD139 / Q{b}5 BD140 outputs through
  3x3 solder-jumper pinout blocks JP{b}01-09 / JP{b}11-19, R{b}13/14 emitter resistors [Re4/Re5], C{b}06 output
  cap [Cout], R{b}15/C{b}07 Zobel [Rzob/Czob], R{b}18 1k VU meter tap [Rvu] to the shared header J5.
  Test points TP{b}1 (base), TP{b}2 (out), TP{b}3 (E4, bias set), TP{b}4 (LED reference).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import Gen, FP

g = Gen("Stereo class-AB amplifier (release 2) - mirror-loaded PNP input, NPN VAS, BD139/BD140 outputs, 12 V")
part, W, J, L, TP = g.part, g.W, g.J, g.label, g.tp
HERE = Path(__file__).parent


def gnd(x, y, rot=0):
    g.s.place(g.L["GND"], "#PWR", "GND", x * 2.54, y * 2.54, rot)


def v12(x, y):
    g.v12(x, y)


def channel(b, oy, sfx, xoff=8):
    def y(v):
        return v + oy
    def part(lib, ref, val, gx, gy, rot=0, fp="", mirror=None, lbl="right"):
        if isinstance(lbl, tuple):
            lbl = (lbl[0] + xoff, lbl[1])
        return g.part(lib, ref, val, gx + xoff, gy, rot, fp, mirror, lbl)
    def W(*pts):
        g.W(*[(a + xoff, bb) for a, bb in pts])
    def J(p):
        g.J((p[0] + xoff, p[1]))
    def L(gx, gy, name, rot=0):
        g.label(gx + xoff, gy, name, rot)
    def TP(ref, net, gx, gy):
        g.tp(ref, net, gx + xoff, gy)
    def gnd(x, yy, rot=0):
        g.s.place(g.L["GND"], "#PWR", "GND", (x + xoff) * 2.54, yy * 2.54, rot)
    def v12(x, yy):
        g.v12(x + xoff, yy)
    def text(gx, gy, s, size=1.27):
        g.text(gx + xoff, gy, s, size)
    # ---- input, bias divider, base feed
    L(2, y(20), "IN_" + sfx, 180)
    W((2, y(20)), (4.5, y(20)))
    part("CP", "C%d01" % b, "2.2u", 6, y(20), 270, FP["CP_S"], lbl=(4.5, y(22.5)))       # + to the base
    W((7.5, y(20)), (13, y(20)))
    part("R", "R%d03" % b, "47k", 10, y(16.5), 0, FP["R"], lbl=(10.8, y(16)))
    W((10, y(18)), (10, y(20))); J((10, y(20)))
    W((10, y(15)), (10, y(11)), (1.5, y(11)))
    part("R", "R%d01" % b, "47k", 1.5, y(7), 0, FP["R"], lbl=(2.3, y(5.5)))
    v12(1.5, y(4)); W((1.5, y(4)), (1.5, y(5.5))); W((1.5, y(8.5)), (1.5, y(11)))
    part("R", "R%d02" % b, "47k", 4, y(14), 0, FP["R"], lbl=(2.2, y(17.3)))
    W((4, y(11)), (4, y(12.5))); J((4, y(11))); W((4, y(15.5)), (4, y(18))); gnd(4, y(18))
    part("CP", "C%d02" % b, "47u", 6.5, y(14), 0, FP["CP_S"], lbl=(5.2, y(10)))
    W((6.5, y(11)), (6.5, y(12.5))); J((6.5, y(11))); W((6.5, y(15.5)), (6.5, y(18.5))); gnd(6.5, y(18.5))
    part("TP", "TP%d1" % b, "B1 6.1V", 8, y(18), 0, FP["TP"], lbl=(8.8, y(21))); W((8, y(18)), (8, y(20))); J((8, y(20)))
    # ---- PNP differential pair, emitters up to the current-source tail
    part("BC557", "Q%d1" % b, "BC557", 15, y(20), 0, FP["TO92"], mirror="x", lbl=(16.5, y(23.3)))   # B left, E top, C bottom
    part("BC557", "Q%d2" % b, "BC557", 23, y(20), 180, FP["TO92"], lbl=(23.0, y(23.3)))             # B right, E top, C bottom
    W((16, y(18)), (16, y(16)), (22, y(16)), (22, y(18)))
    # tail: Q9 with a red LED reference (10.2 V), 1.2k emitter resistor -> about 1 mA
    part("BC557", "Q%d9" % b, "BC557", 19, y(12), 0, FP["TO92"], mirror="x", lbl=(20.5, y(14.5)))     # B left, E top, C bottom
    W((20, y(14)), (20, y(16))); J((20, y(16)))
    part("R", "R%d04" % b, "1.2k", 20, y(7), 0, FP["R"], lbl=(20.8, y(6.5)))
    v12(20, y(4)); W((20, y(4)), (20, y(5.5))); W((20, y(8.5)), (20, y(10)))
    part("LED", "D%d01" % b, "LED red", 14, y(8), 90, FP["LED"], lbl=(14.8, y(7)))                   # A top, K bottom
    v12(14, y(5)); W((14, y(5)), (14, y(6.5)))
    W((14, y(9.5)), (14, y(12)), (17, y(12))); J((14, y(12)))
    part("R", "R%d05" % b, "4.7k", 14, y(14.5), 0, FP["R"], lbl=(14.8, y(14)))
    W((14, y(12)), (14, y(13))); W((14, y(16)), (14, y(17))); gnd(14, y(17))
    TP("TP%d4" % b, "LED 10.2V", 11, y(12)); W((11, y(12)), (14, y(12)))
    # current-mirror load: Q8 diode side under Q2, Q7 output under Q1 -> VAS base
    part("BC547", "Q%d7" % b, "BC547", 15, y(27), 0, FP["TO92"], mirror="y", lbl=(10.5, y(28.5)))    # B right, C top, E bottom
    part("BC547", "Q%d8" % b, "BC547", 23, y(27), 0, FP["TO92"], lbl=(24.5, y(29.5)))                # B left, C top, E bottom
    W((16, y(22)), (16, y(24)), (10, y(24))); W((14, y(24)), (14, y(25))); J((14, y(24)))
    W((22, y(22)), (22, y(23)), (24, y(23)), (24, y(25)))
    W((22, y(23)), (19, y(23)), (19, y(27))); J((22, y(23)))
    W((17, y(27)), (21, y(27))); J((19, y(27)))
    part("R", "R%d16" % b, "100", 14, y(31.5), 0, FP["R"], lbl=(14.8, y(31)))
    W((14, y(29)), (14, y(30))); W((14, y(33)), (14, y(34))); gnd(14, y(34))
    part("R", "R%d17" % b, "100", 24, y(31.5), 0, FP["R"], lbl=(24.8, y(31)))
    W((24, y(29)), (24, y(30))); W((24, y(33)), (24, y(34))); gnd(24, y(34))
    # feedback with lead capacitor
    W((25, y(20)), (27.5, y(20)))
    part("R", "R%d06" % b, "22k", 29, y(20), 90, FP["R"], lbl=(27.5, y(21.5)))
    W((30.5, y(20)), (32, y(20))); L(32, y(20), "OUT_" + sfx)
    part("C", "C%d08" % b, "47p", 29, y(17), 90, FP["C"], lbl=(27.5, y(14.5)))
    W((27.5, y(17)), (27.5, y(20))); J((27.5, y(20))); W((30.5, y(17)), (30.5, y(20))); J((30.5, y(20)))
    part("R", "R%d07" % b, "1k", 26, y(24), 0, FP["R"])
    W((26, y(20)), (26, y(22.5))); J((26, y(20)))
    part("CP", "C%d03" % b, "220u", 26, y(29), 0, FP["CP_M"])
    W((26, y(25.5)), (26, y(27.5))); W((26, y(30.5)), (26, y(32))); gnd(26, y(32))
    # ---- NPN VAS: base from the mirror output (c1), collector = B5 (PNP output base), Miller cap b5-c1
    part("BC547", "Q%d3" % b, "BC547", 7, y(27), 0, FP["TO92"], mirror="y", lbl=(2.5, y(28.5)))      # B right, C top, E bottom
    W((10, y(24)), (11, y(24)), (11, y(27)), (9, y(27))); J((11, y(24)))
    W((6, y(25)), (6, y(24)), (3, y(24))); L(3, y(24), "B5_" + sfx, 180); J((6, y(24)))
    part("C", "C%d04" % b, "220p", 8, y(24), 90, FP["C"], lbl=(6.8, y(22)))
    W((6, y(24)), (6.5, y(24))); W((9.5, y(24)), (10, y(24))); J((10, y(24)))
    part("R", "R%d08" % b, "47", 6, y(31.5), 0, FP["R"], lbl=(6.8, y(31)))
    W((6, y(29)), (6, y(30))); W((6, y(33)), (6, y(34))); gnd(6, y(34))
    # ---- Vbe multiplier
    L(89, y(9), "VAS_" + sfx, 0)
    part("BC547", "Q%d6" % b, "BC547", 84, y(14), 0, FP["TO92"], mirror="y", lbl=(79, y(12.5)))
    W((83, y(12)), (83, y(9)), (90, y(9))); J((89, y(9)))
    part("R", "R%d09" % b, "470", 90, y(11.5), 0, FP["R"])
    W((90, y(9)), (90, y(10)))
    part("TRIM", "RV%d" % b, "1k", 90, y(16), 0, FP["TRIM"])
    W((90, y(13)), (90, y(14.5))); W((91.5, y(16)), (91.5, y(17.5)), (90, y(17.5))); J((90, y(17.5)))
    W((90, y(17.5)), (90, y(19)), (87.5, y(19)), (87.5, y(14)), (86, y(14))); J((90, y(19)))
    part("R", "R%d10" % b, "1k", 90, y(21.5), 0, FP["R"])
    W((90, y(19)), (90, y(20))); W((90, y(23)), (90, y(25)), (83, y(25)), (83, y(16)))
    W((83, y(25)), (81, y(25))); L(81, y(25), "B5_" + sfx, 180); J((83, y(25)))
    # bootstrapped VAS load from +12V: R11 to the boot node, R12 from boot to the VAS node, C05 boot -> OUT
    W((90, y(9)), (93, y(9)))
    part("R", "R%d12" % b, "270", 94.5, y(9), 270, FP["R"], lbl=(92.5, y(11)))      # pin 1 on the boot side, like the deck
    part("R", "R%d11" % b, "270", 96, y(6), 0, FP["R"], lbl=(96.8, y(5.5)))
    v12(96, y(3)); W((96, y(3)), (96, y(4.5))); W((96, y(7.5)), (96, y(9))); J((96, y(9)))
    part("CP", "C%d05" % b, "100u", 99.5, y(9), 90, FP["CP_M"], lbl=(99.5, y(11)))      # + on the boot side
    W((96, y(9)), (98, y(9))); W((101, y(9)), (103, y(9))); L(103, y(9), "OUT_" + sfx)
    # ---- output devices with 3x3 jumper blocks
    part("BD139", "Q%d4" % b, "BD139", 46, y(10), 0, FP["TO220"], lbl=(44.0, y(6.0)))
    part("BD140", "Q%d5" % b, "BD140", 46, y(30), 0, FP["TO220"], mirror="x", lbl=(44.0, y(34.0)))
    text(38, y(3.5), "Q%d4 pins: 1=E 2=C 3=B (BD139). Bridged jumpers sit on the diagonal; for a B-C-E part (TIP41C) move the bridges of pad 1 and pad 3." % b, 1.0)
    _jblock(b, 0, y, sfx, (46 + xoff, 10), npn=True, xoff=xoff)
    _jblock(b, 1, y, sfx, (46 + xoff, 30), npn=False, xoff=xoff)
    # ---- emitter resistors, output cap, Zobel
    L(108, y(19), "E4_" + sfx, 90)
    part("R", "R%d13" % b, "0.47", 108, y(22), 0, FP["R_2W"])
    W((108, y(19)), (108, y(20.5))); W((108, y(19)), (110, y(19))); TP("TP%d3" % b, "E4 bias", 110, y(19))
    part("R", "R%d14" % b, "0.47", 108, y(30), 0, FP["R_2W"])
    W((108, y(23.5)), (108, y(28.5))); W((108, y(31.5)), (108, y(33))); L(108, y(33), "E5_" + sfx, 270)
    W((108, y(26)), (112.5, y(26))); J((108, y(26)))
    W((108, y(26)), (105, y(26))); L(105, y(26), "OUT_" + sfx, 180)
    TP("TP%d2" % b, "OUT 5.9V", 106, y(24.5)); W((106, y(24.5)), (106, y(26))); J((106, y(26)))
    part("CP", "C%d06" % b, "1000u", 114, y(26), 90, FP["CP_L"], lbl="above")
    W((115.5, y(26)), (118, y(26))); L(118, y(26), "SPK_" + sfx)
    part("R", "R%d18" % b, "1k", 117, y(30), 0, FP["R"], lbl=(117.8, y(29.5)))
    W((117, y(26)), (117, y(28.5))); J((117, y(26)))
    W((117, y(31.5)), (117, y(33))); L(117, y(33), "VU_" + sfx, 270)
    part("R", "R%d15" % b, "10", 111, y(29.5), 0, FP["R"])
    W((111, y(26)), (111, y(28))); J((111, y(26)))
    part("C", "C%d07" % b, "100n", 111, y(34), 0, FP["C"])
    W((111, y(31)), (111, y(32.5))); W((111, y(35.5)), (111, y(37))); gnd(111, y(37))


def _jblock(b, n, y, sfx, q, npn, xoff=0):
    """3x3 jumper block beside output device at grid q. Columns are the three pads
    (E, C, B order = BD139 pins 1,2,3) and rows the three circuit nets."""
    qx, qy = q
    base = (qx - 2, y(qy))
    top, bot = (qx + 1, y(qy - 2)), (qx + 1, y(qy + 2))
    if npn:
        pinE, pinC = bot, top
        nets = [("E4_" + sfx, "E"), ("+12V", "C"), ("VAS_" + sfx, "B")]
        rows = [y(16), y(18), y(20)]
        routes = {"E": [pinE, (qx + 1, y(13)), (50 + xoff, y(13))],
                  "C": [pinC, (qx + 1, y(5)), (58 + xoff, y(5))],
                  "B": [base, (qx - 4, y(10)), (qx - 4, y(24)), (66 + xoff, y(24))]}
        k0 = 1
    else:
        pinE, pinC = top, bot
        nets = [("E5_" + sfx, "E"), ("GND", "C"), ("B5_" + sfx, "B")]
        rows = [y(36), y(38), y(40)]
        routes = {"C": [pinC, (qx + 1, y(34)), (50 + xoff, y(34))],
                  "E": [pinE, (qx + 1, y(26)), (58 + xoff, y(26))],
                  "B": [base, (qx - 4, y(30)), (qx - 4, y(44)), (66 + xoff, y(44))]}
        k0 = 11
    cols = [(50 + xoff, "E"), (58 + xoff, "C"), (66 + xoff, "B")] if npn else [(50 + xoff, "C"), (58 + xoff, "E"), (66 + xoff, "B")]
    k = k0
    for cx, pad in cols:
        r = routes[pad]
        W(*r)
        lo, hi = min(rows[0], r[-1][1]), max(rows[-1], r[-1][1])
        W((cx, lo), (cx, hi))
        for ry, (net, netpad) in zip(rows, nets):
            br = (pad == netpad)
            ref = "JP%d%02d" % (b, k)
            part("JPB" if br else "JPO", ref, pad + ">" + net.split("_")[0], cx + 2.5, ry, 0,
                 FP["JP_BRIDGED"] if br else FP["JP_OPEN"], lbl=(cx + 1.2, ry - 0.9))
            W((cx, ry), (cx + 1, ry))
            if lo < ry < hi:
                J((cx, ry))
            W((cx + 4, ry), (cx + 5, ry))
            L(cx + 5, ry, net)
            k += 1


channel(100, 0, "L")
channel(200, 46, "R")

# ---- shared: power in, decoupling, input header, speaker terminals
oy = 92
g.text(2, oy - 2, "Shared: DC in, reservoir, input header (L G R), speaker terminals, VU meter header (1k series from each speaker node). Test points TP1 +12V, TP2 GND.", 1.27)
part("SCREW2", "J1", "DC 12V IN", 6, oy + 4, 0, FP["SCREW2"], lbl="above")
W((4, oy + 4), (2, oy + 4), (2, oy + 1)); v12(2, oy + 1)
W((2, oy + 2), (3, oy + 2)); g.flag(3, oy + 2); J((2, oy + 2))
W((4, oy + 5), (2, oy + 5), (2, oy + 9)); gnd(2, oy + 9)
W((2, oy + 8), (3, oy + 8)); g.flag(3, oy + 8); J((2, oy + 8))
part("CP", "C1", "1000u", 12, oy + 5, 0, FP["CP_L"])
v12(12, oy + 1); W((12, oy + 1), (12, oy + 3.5)); W((12, oy + 6.5), (12, oy + 9)); gnd(12, oy + 9)
part("C", "C2", "100n", 16, oy + 5, 0, FP["C"])
v12(16, oy + 1); W((16, oy + 1), (16, oy + 3.5)); W((16, oy + 6.5), (16, oy + 9)); gnd(16, oy + 9)
W((12, oy + 3.5), (14, oy + 3.5)); J((12, oy + 3.5)); TP("TP1", "+12V", 14, oy + 3.5)
W((12, oy + 6.5), (14, oy + 6.5)); J((12, oy + 6.5)); TP("TP2", "GND", 14, oy + 6.5)
part("H3", "J2", "IN L-G-R", 24, oy + 5, 0, FP["H3"], mirror="y", lbl="above")
W((26, oy + 4), (29, oy + 4)); L(29, oy + 4, "IN_L")
W((26, oy + 5), (29, oy + 5)); L(29, oy + 5, "GND")
W((26, oy + 6), (29, oy + 6)); L(29, oy + 6, "IN_R")
part("SCREW2", "J3", "SPK L", 40, oy + 4, 0, FP["SCREW2"], mirror="y", lbl="above")
W((42, oy + 4), (45, oy + 4)); L(45, oy + 4, "SPK_L")
W((42, oy + 5), (45, oy + 5)); L(45, oy + 5, "GND")
part("SCREW2", "J4", "SPK R", 52, oy + 4, 0, FP["SCREW2"], mirror="y", lbl="above")
W((54, oy + 4), (57, oy + 4)); L(57, oy + 4, "SPK_R")
W((54, oy + 5), (57, oy + 5)); L(57, oy + 5, "GND")
part("H3", "J5", "VU L-G-R", 64, oy + 5, 0, FP["H3"], mirror="y", lbl="above")
W((66, oy + 4), (69, oy + 4)); L(69, oy + 4, "VU_L")
W((66, oy + 5), (69, oy + 5)); L(69, oy + 5, "GND")
W((66, oy + 6), (69, oy + 6)); L(69, oy + 6, "VU_R")
g.text(60, oy + 10, "J5: VU meter tap, 1k in series with each speaker node (2.8 Vrms at 1 W / 8 ohm, no DC). Leave open if unused.", 1.0)

out = g.write("amp", HERE / "amp")
print("wrote", out)
