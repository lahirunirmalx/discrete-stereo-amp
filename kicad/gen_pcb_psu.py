"""PSU board placement: 90 x 45 mm. AC terminal and fuse at the left, bridge and reservoir in the middle,
TIP41C pass transistor on the top edge (heatsink room above the board), regulator parts below it,
DC in/out terminals along the right edge facing outward."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from pcbgen import pack, build
from common import FP

single = "--single" in sys.argv
HERE = Path(__file__).parent
BW, BH = 90.0, 50.0
place, texts = {}, []
R, R2W, C, CPM, CPXL, Q, TP, D201, D41 = FP["R"], FP["R_2W"], FP["C"], FP["CP_M"], FP["CP_XL"], FP["TO92"], FP["TP"], FP["D201"], FP["D41"]


def region(items, x0, y0, w, h, gap=0.8):
    out, used = pack(items, x0, y0, w, h, gap=gap, back=single)
    place.update(out)
    return used


place["J1"] = (6.0, 14.0, 270); texts.append((6.5, 7.5, "AC IN", 0.9)); texts.append((6.5, 24.0, "12-15VAC", 0.9))
place["F1"] = (14.0, 4.5, 0); texts.append((25.0, 8.5, "FUSE 1A T", 0.9))
region([("D1", D201, 0), ("D2", D201, 0), ("D3", D201, 0), ("D4", D201, 0)], 12.0, 10.0, 35.6, 14.0)
region([("C1", CPXL, 0), ("C2", CPXL, 0)], 48.0, 8.0, 28.4, 15.0)
place["Q2"] = (46.0, 4.0, 0); texts.append((48.5, 7.3, "TIP41C + HEATSINK", 0.9))
region([("TP1", TP, 0), ("R2", R, 0), ("D5", D41, 0), ("C3", CPM, 0), ("TP2", TP, 0), ("Q1", Q, 0), ("Q3", Q, 0), ("R1", R, 0),
        ("R3", R2W, 0), ("D6", D41, 0), ("TP4", TP, 0)], 13.0, 25.0, 45.0, 24.0)
region([("D8", D201, 0), ("TP3", TP, 0), ("C4", CPM, 0), ("C5", C, 90), ("R4", R, 0), ("D7", FP["LED"], 0), ("J5", FP["H2"], 90)], 58.5, 24.0, 19.0, 25.0)
place["J2"] = (83.5, 13.0, 90); texts.append((80.5, 18.0, "DC IN 12V", 0.9))
place["J3"] = (83.5, 27.0, 90); texts.append((80.5, 31.5, "DC OUT", 0.9))
place["J4"] = (83.5, 41.0, 90); texts.append((80.5, 45.5, "DC OUT", 0.9))
texts.append((36.0, 24.4, "TP1 VRAW  TP2 VZ 13V  TP3 VOUT 11.5V  TP4 GND", 0.9))
texts.append((63.0, 2.0, "discrete-stereo-amp v1.0 2026-10", 0.8))
stem = "psu_1layer" if single else "psu"
bad = build(HERE / "psu/psu.net", place, BW, BH, HERE / "psu" / (stem + ".kicad_pcb"),
            "DISCRETE 12V PSU - bridge, zener, TIP41C", single=single, scale=(1.3, 1.3), texts=texts, track=0.8)
sys.exit(1 if bad else 0)
