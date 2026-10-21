"""PSU board schematic: 12-15 VAC in -> fuse -> 4x 1N5401 bridge -> 2x 2200u -> 13 V zener reference ->
BC547 + TIP41C Darlington pass with 0.33 R current clamp (about 2 A) -> VOUT about 11.5 V.
D6 protects the pass transistor when 12 V DC is fed in at J2 (via D8 Schottky, bypassing regulator and clamp).
Test points: TP1 VRAW, TP2 VZ (zener), TP3 VOUT, TP4 GND."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import Gen, FP

g = Gen("Discrete 12 V power supply - bridge, zener reference, TIP41C pass, DC-in bypass", paper="A4")
part, W, J, L, TP = g.part, g.W, g.J, g.label, g.tp
HERE = Path(__file__).parent


def gnd(x, y, rot=0):
    g.s.place(g.L["GND"], "#PWR", "GND", x * 2.54, y * 2.54, rot)


VR, GR = 4, 34          # VRAW rail and GND rail rows
# ---- AC input and fuse
part("SCREW2", "J1", "AC IN 12-15V", 4, 10, 0, FP["SCREW2"], mirror="y", lbl="above")
part("FUSE", "F1", "1A T 5x20", 10, 10, 90, FP["FUSE"], lbl="above")
W((6, 10), (8.5, 10)); W((11.5, 10), (13, 10)); L(13, 10, "AC1")
W((6, 11), (7, 11), (7, 13), (9, 13)); L(9, 13, "AC2")
g.text(2, 6, "Transformer secondary 12-15 VAC, 1.5 A or more for full stereo power (12 VAC: regulated to 0.35 A).", 1.0)
# ---- bridge: two columns between the rails, labels AC1 / AC2 at the midpoints
for x, ac, top, bot in ((16, "AC1", "D1", "D3"), (22, "AC2", "D2", "D4")):
    part("D", top, "1N5401", x, 7, 270, FP["D201"])        # K top -> VRAW, A bottom -> AC
    part("D", bot, "1N5401", x, 13, 270, FP["D201"])       # K top -> AC, A bottom -> GND
    W((x, VR), (x, 5.5)); W((x, 8.5), (x, 10)); W((x, 10), (x, 11.5)); W((x, 14.5), (x, GR))
    W((x, 10), (x - 2, 10)); L(x - 2, 10, ac, 180); J((x, 10))
W((16, VR), (70, VR)); W((16, GR), (103, GR))
# ---- reservoir, bleeder
part("CP", "C1", "2200u", 28, 8, 0, FP["CP_XL"]); W((28, VR), (28, 6.5)); W((28, 9.5), (28, GR)); J((28, VR)); J((28, GR))
part("CP", "C2", "2200u", 33, 8, 0, FP["CP_XL"]); W((33, VR), (33, 6.5)); W((33, 9.5), (33, GR)); J((33, VR)); J((33, GR))
part("R", "R1", "4.7k", 37, 8, 0, FP["R"]); W((37, VR), (37, 6.5)); W((37, 9.5), (37, GR)); J((37, VR)); J((37, GR))
TP("TP1", "VRAW 14-19V", 40, 2.5); W((40, 2.5), (40, VR)); J((40, VR))
g.flag(44, 2.5); W((44, 2.5), (44, VR)); J((44, VR))
# ---- zener reference
part("R", "R2", "1k", 42, 8, 0, FP["R"]); W((42, VR), (42, 6.5)); J((42, VR)); W((42, 9.5), (42, 12))
part("DZ", "D5", "13V 1W", 42, 15, 270, FP["D41"]); W((42, 12), (42, 13.5)); W((42, 16.5), (42, GR)); J((42, GR))
part("CP", "C3", "100u", 46, 15, 0, FP["CP_M"]); W((42, 12), (46, 12), (46, 13.5)); W((46, 16.5), (46, GR)); J((46, GR)); J((42, 12))
W((42, 12), (40, 12)); L(40, 12, "VZ", 180)
TP("TP2", "VZ 13V", 44, 10.5); W((44, 10.5), (44, 12)); J((44, 12))
# ---- Darlington pass and current clamp
part("BC547", "Q1", "BC547", 52, 12, 0, FP["TO92"], lbl=(49, 15))
W((46, 12), (50, 12)); J((46, 12))
W((53, 10), (53, VR)); J((53, VR))
part("TIP41C", "Q2", "TIP41C", 58, 16, 0, FP["TO220"], lbl=(55, 19.5))
W((53, 14), (53, 16), (56, 16))
W((59, 14), (59, VR)); J((59, VR))
part("R", "R3", "0.33 2W", 59, 21, 0, FP["R_2W"], lbl="right")
W((59, 18), (59, 19.5)); W((59, 22.5), (59, 24))
part("BC547", "Q3", "BC547", 64, 21, 0, FP["TO92"], lbl=(66, 22.5))
W((62, 21), (61, 21), (61, 19.5), (59, 19.5)); J((59, 19.5))
W((65, 23), (65, 24)); J((59, 24))
W((65, 19), (65, 17.5)); L(65, 17.5, "VZ", 90)
# ---- reverse protection across the pass device, VOUT rail
part("D", "D6", "1N4007", 70, 14, 270, FP["D41"]); W((70, VR), (70, 12.5)); W((70, 15.5), (70, 24)); J((70, 24))
W((59, 24), (95, 24))
TP("TP3", "VOUT 11.5V", 73, 22.5); W((73, 22.5), (73, 24)); J((73, 24))
part("CP", "C4", "220u", 77, 27, 0, FP["CP_M"]); W((77, 24), (77, 25.5)); W((77, 28.5), (77, GR)); J((77, 24)); J((77, GR))
part("C", "C5", "100n", 81, 27, 0, FP["C"]); W((81, 24), (81, 25.5)); W((81, 28.5), (81, GR)); J((81, 24)); J((81, GR))
part("R", "R4", "1k", 85, 27, 0, FP["R"]); W((85, 24), (85, 25.5)); J((85, 24))
part("LED", "D7", "LED", 85, 31, 90, FP["LED"], lbl="right"); W((85, 28.5), (85, 29.5)); W((85, 32.5), (85, GR)); J((85, GR))
# the LED can instead live on the front panel / volume board: 2-pin header in parallel with D7 (fit one or the other)
part("H2", "J5", "LED REMOTE", 91, 29.5, 0, FP["H2"], lbl="above")
W((89, 29.5), (85, 29.5)); J((85, 29.5)); W((89, 30.5), (88, 30.5), (88, 32.5), (85, 32.5)); J((85, 32.5))
g.text(86, 36.5, "J5: LED on the volume board via 2 wires (pin 1 = anode/+). Fit D7 or J5, not both.", 1.0)
TP("TP4", "GND", 50, 32.5); W((50, 32.5), (50, GR)); J((50, GR))
gnd(103, GR); g.flag(100, 36); W((100, GR), (100, 36)); J((100, GR))
# ---- DC outputs and DC input
part("SCREW2", "J3", "DC OUT 1", 90, 14, 0, FP["SCREW2"], mirror="y", lbl="above")
W((92, 14), (95, 14), (95, 24)); J((95, 24)); W((92, 15), (92, 16)); L(92, 16, "GND", 270)
part("SCREW2", "J4", "DC OUT 2", 90, 19, 0, FP["SCREW2"], mirror="y", lbl="above")
W((92, 19), (95, 19)); J((95, 19)); W((92, 20), (92, 21)); L(92, 21, "GND", 270)
part("DS", "D8", "SB540", 98, 24, 0, FP["D201"], lbl="above")          # K left (VOUT), A right (DC in)
W((95, 24), (96.5, 24)); W((99.5, 24), (101, 24))
part("SCREW2", "J2", "DC IN 12V", 103, 24, 0, FP["SCREW2"], lbl="above")
W((101, 25), (101, 26)); L(101, 26, "GND", 270)
g.text(88, 29, "J2: 12 V DC straight to VOUT through D8 (0.4 V drop). Bypasses the regulator and the current clamp.", 1.0)
g.text(2, 38, "Pass transistor Q2 needs a heatsink: 1.6 W at 12 VAC / 1 A, 4.9 W at 15 VAC / 1.1 A (psu.cir).", 1.0)
out = g.write("psu", HERE / "psu")
print("wrote", out)
