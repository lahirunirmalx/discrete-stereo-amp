"""Headphone board placement: 42 x 26 mm (same pocket size as the volume board). Input header and the two
speaker terminals along the top edge, the jack opening off the bottom edge (its courtyard hangs over the edge
like the volume pot), the slide switch beside it, series resistors and bypass jumpers in between."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from pcbgen import build
from common import FP, STAMP, REPO

single = "--single" in sys.argv
HERE = Path(__file__).parent
BW, BH = 42.0, 30.0
place = {"J2": (9.0, 5.6, 180), "J3": (21.0, 5.6, 180), "J1": (28.0, 2.6, 90), "J5": (28.0, 7.0, 90), "TP1": (38.5, 7.0, 0),
         "J4": (6.0, 25.5, 180), "SW1": (19.0, 21.4, 90),
         "R1": (28.7, 12.6, 0), "R2": (28.7, 16.2, 0), "JP1": (29.5, 20.0, 0), "JP2": (36.5, 20.0, 0),
         "TP2": (29.5, 26.5, 0), "TP3": (36.5, 26.5, 0)}
texts = [(9.0, 12.2, "SPK L", 0.8), (21.0, 12.2, "SPK R", 0.8), (38.3, 2.0, "AMP", 0.7), (38.3, 4.4, "JACK", 0.7), (38.5, 10.2, "GND", 0.7),
         (19.0, 13.9, "LEVER UP = SPK", 0.7), (19.0, 28.9, "DOWN = PHONES", 0.7), (33.0, 22.3, "DIRECT L / R", 0.7),
         (33.0, 26.5, "HP", 0.7), (29.5, 29.0, "L", 0.7), (36.5, 29.0, "R", 0.7)]
back_texts = [(21.0, 14.0, REPO, 0.9), (21.0, 17.0, "HEADPHONE  " + STAMP, 1.0)]
stem = "hp_1layer" if single else "hp"
bad = build(HERE / "hp/hp.net", place, BW, BH, HERE / "hp" / (stem + ".kicad_pcb"),
            "HP SW", single=single, scale=(1.5, 1.5), texts=texts, allow_offboard=("J4",), mount_holes=False, title_at=(33.0, 23.9), back_texts=back_texts)
sys.exit(1 if bad else 0)
