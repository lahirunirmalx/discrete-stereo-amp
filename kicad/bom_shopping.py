"""Shopping list: one line per part value and package, quantities summed over all three boards."""
import csv
from collections import OrderedDict
from pathlib import Path
HERE = Path(__file__).parent
KIND = {"R": "resistor", "C": "capacitor", "D": "diode / LED", "Q": "transistor", "RV": "potentiometer / trimmer",
        "J": "connector", "F": "fuse", "TP": "test point"}
agg = OrderedDict()
for r in csv.DictReader(open(HERE / "panel" / "bom_all.csv")):
    ref0 = r["refs"].split()[0]
    pre = "RV" if ref0.startswith("RV") else ("TP" if ref0.startswith("TP") else ref0[0])
    kind = KIND.get(pre, "other")
    value, spec = r["value"], r["tolerance_rating"]
    if kind in ("connector", "test point"):
        # buy these by package, not by what the silkscreen says
        pk = r["through_hole"]
        value = {"TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal": "2-pin screw terminal 5.08 mm",
                 "PinHeader_1x03_P2.54mm_Vertical": "1x3 pin header 2.54 mm", "PinHeader_1x02_P2.54mm_Vertical": "1x2 pin header 2.54 mm",
                 "TestPoint_Loop_D2.50mm_Drill1.0mm": "test point loop (or a bare wire loop)"}.get(pk, pk)
        spec = ""
    if spec.startswith("5 percent / 20 percent"):
        spec = ""
    key = (kind, value, r["through_hole"])
    if key not in agg:
        agg[key] = {"kind": kind, "value": value, "package": r["through_hole"], "qty": 0, "boards": set(),
                    "spec": spec, "smd_alternative": r["smd_alternative"]}
    agg[key]["qty"] += int(r["qty"]); agg[key]["boards"].add(r["board"])
rows = sorted(agg.values(), key=lambda x: (x["kind"], x["value"]))
for x in rows:
    x["boards"] = " ".join(sorted(x["boards"]))
with open(HERE / "panel" / "bom_shopping.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["kind", "value", "qty", "package", "spec", "smd_alternative", "boards"]); w.writeheader(); w.writerows(rows)
md = ["# Shopping list (all three boards, one set)", "", "| Kind | Value | Qty | Package | Spec |", "|---|---|---|---|---|"]
for x in rows:
    md.append("| %s | %s | %d | %s | %s |" % (x["kind"], x["value"], x["qty"], x["package"], x["spec"]))
md += ["", "Plus 36 solder jumpers (copper pads only, no part), 2.5 mm M2.5 screws for the 8 mounting holes, a 12-15 VAC transformer, hook-up wire.",
       "Fit ONE power LED (PSU D7 or volume D1), so the LED count can drop by one."]
(HERE / "panel" / "bom_shopping.md").write_text("\n".join(md) + "\n")
print("lines:", len(rows), "parts:", sum(x["qty"] for x in rows))
print("\n".join(md[2:]))
