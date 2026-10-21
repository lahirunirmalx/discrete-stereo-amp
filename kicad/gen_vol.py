"""Volume board: dual-gang 10k log pot between the input header and the amp input header.
Pin 3 (clockwise end) takes the input, pin 1 (counter-clockwise end) is ground, pin 2 is the wiper -> clockwise = louder."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import Gen, FP

g = Gen("Stereo volume control - dual 10k log pot", paper="A4")
part, W, J, L = g.part, g.W, g.J, g.label
HERE = Path(__file__).parent

part("H3", "J1", "IN L-G-R", 6, 10, 0, FP["H3"], mirror="y", lbl="above")
W((8, 9), (11, 9)); L(11, 9, "IN_L")
W((8, 10), (11, 10)); L(11, 10, "GND")
W((8, 11), (11, 11)); L(11, 11, "IN_R")
part("POT2", "RV1", "10k log dual", 22, 10, 0, FP["POT2"], lbl=(17, 5))
W((18, 11), (18, 13)); L(18, 13, "GND", 270)
W((21, 11), (21, 13)); L(21, 13, "IN_L", 270)
W((19.5, 9), (19.5, 7)); L(19.5, 7, "OUT_L", 90)
W((23, 11), (23, 13)); L(23, 13, "GND", 270)
W((26, 11), (26, 13)); L(26, 13, "IN_R", 270)
W((24.5, 9), (24.5, 7)); L(24.5, 7, "OUT_R", 90)
part("H3", "J2", "OUT L-G-R", 38, 10, 0, FP["H3"], lbl="above")
W((36, 9), (33, 9)); L(33, 9, "OUT_L", 180)
W((36, 10), (33, 10)); L(33, 10, "GND", 180)
W((36, 11), (33, 11)); L(33, 11, "OUT_R", 180)
part("H2", "J3", "LED IN", 6, 22, 0, FP["H2"], mirror="y", lbl="above")
part("LED", "D1", "POWER LED", 13, 22, 0, FP["LED"], lbl="above")        # K left, A right
W((8, 22), (9, 22), (9, 19), (16, 19), (16, 22), (14.5, 22)); W((8, 23), (11.5, 23), (11.5, 22))
g.text(2, 27, "J3 pin 1 (+) and pin 2 from PSU J5: the PSU resistor R4 sets the LED current.", 1.0)
g.s.place(g.L["GND"], "#PWR", "GND", 2.54 * 14, 2.54 * 16, 0); W((14, 10), (14, 16)); L(14, 10, "GND")
g.flag(16, 14); W((14, 14), (16, 14)); J((14, 14))
g.text(2, 18, "Pot pins: 1 = CCW end (GND), 2 = wiper (OUT), 3 = CW end (IN). Alps RK097 dual, 9 mm, or any 6-pin dual 10k log.", 1.0)
out = g.write("vol", HERE / "vol")
print("wrote", out)
