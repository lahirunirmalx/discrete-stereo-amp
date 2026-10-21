"""Volume board: 34 x 22 mm. Headers along the top edge, the dual pot at the bottom with its shaft
pointing off the bottom edge (the courtyard hangs over the edge on purpose)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from pcbgen import build
from common import FP

single = "--single" in sys.argv
HERE = Path(__file__).parent
BW, BH = 42.0, 26.0
place = {"J1": (3.5, 3.0, 90), "J2": (19.0, 3.0, 90), "RV1": (14.0, 14.0, 90), "J3": (33.0, 3.0, 90), "D1": (33.0, 15.0, 0)}
texts = [(8.0, 7.0, "IN L G R", 0.9), (23.5, 7.0, "OUT L G R", 0.9), (17.0, 11.0, "VOL 10k LOG", 0.9), (35.5, 7.0, "LED", 0.9), (34.5, 19.0, "PWR", 0.9), (27.0, 21.5, "v1.0 2026-10", 0.8)]
stem = "vol_1layer" if single else "vol"
bad = build(HERE / "vol/vol.net", place, BW, BH, HERE / "vol" / (stem + ".kicad_pcb"),
            "VOLUME", single=single, scale=(1.0, 1.0), texts=texts, allow_offboard=("RV1",), mount_holes=False, title_at=(27.0, 23.5))
sys.exit(1 if bad else 0)
