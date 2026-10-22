"""Headphone board placement: 42 x 26 mm (same pocket size as the volume board). Input header and the two
speaker terminals along the top edge, the jack opening off the bottom edge (its courtyard hangs over the edge
like the volume pot), the slide switch beside it, series resistors and bypass jumpers in between."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from pcbgen import build
from common import FP, STAMP

single = "--single" in sys.argv
HERE = Path(__file__).parent
BW, BH = 42.0, 30.0
place = {"J2": (9.0, 5.6, 180), "J3": (21.0, 5.6, 180), "J1": (28.0, 2.6, 90), "J5": (28.0, 7.0, 90), "TP1": (38.5, 7.0, 0),
         "J4": (6.0, 25.5, 180), "SW1": (14.5, 22.5, 90),
         "R1": (24.0, 14.5, 0), "R2": (24.0, 19.0, 0), "JP1": (37.5, 14.5, 0), "JP2": (37.5, 19.0, 0),
         "TP2": (26.0, 24.5, 0), "TP3": (31.0, 24.5, 0)}
texts = [(9.0, 12.2, "SPK L", 0.8), (21.0, 12.2, "SPK R", 0.8), (38.3, 2.0, "AMP", 0.7), (38.3, 4.6, "JACK", 0.7), (38.5, 9.6, "GND", 0.7),
         (6.0, 13.5, "PHONES", 0.9), (14.0, 28.8, "SPK <-> HP", 0.7), (37.5, 12.4, "DIRECT", 0.7), (37.5, 16.9, "DIRECT", 0.7),
         (26.0, 27.2, "HP L", 0.7), (31.0, 27.2, "HP R", 0.7), (36.5, 28.5, STAMP, 0.7)]
stem = "hp_1layer" if single else "hp"
bad = build(HERE / "hp/hp.net", place, BW, BH, HERE / "hp" / (stem + ".kicad_pcb"),
            "HEADPHONE", single=single, scale=(1.0, 1.0), texts=texts, allow_offboard=("J4",), mount_holes=False, title_at=(31.0, 10.8))
sys.exit(1 if bad else 0)
