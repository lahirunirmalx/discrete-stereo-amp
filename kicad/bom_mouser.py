"""Mouser BOM-tool upload (their template columns). Only 'Mfr Part Number (Input)', 'Order Quantity' and
'Description' are filled; Mouser's tool fills the rest when you upload it. Quantities come from
bom_shopping.csv; the MPN mapping is below and is NOT stock-checked: let the Mouser tool confirm each
match and swap any line it cannot find for the equivalent it offers."""
import csv
from pathlib import Path
HERE = Path(__file__).parent
HEADER = ["Mfr Part Number (Input)", "Manufacturer Part Number", "Mouser Part Number", "Manufacturer Name", "Description",
          "Quantity 1", "Unit Price 1", "Quantity 2", "Unit Price 2", "Quantity 3", "Unit Price 3", "Quantity 4", "Unit Price 4",
          "Quantity 5", "Unit Price 5", "Order Quantity", "Order Unit Price", "Min./Mult.", "Availability", "Lead Time in Days",
          "Lifecycle", "NCNR", "RoHS", "Pb Free", "Package Type", "Datasheet URL", "Product Image", "Design Risk"]
# (kind, value) -> (MPN, manufacturer, description, note)
MPN = {
    ("transistor", "BC547"): ("BC547BTA", "onsemi", "NPN TO-92 BC547B, hFE 200-450", ""),
    ("transistor", "BC557"): ("BC557BTA", "onsemi", "PNP TO-92 BC557B", ""),
    ("transistor", "BD139"): ("BD139-16", "STMicroelectronics", "NPN TO-126 1.5 A 80 V, hFE 100-250", "or BD139 ungraded + sort by hFE"),
    ("transistor", "BD140"): ("BD140-16", "STMicroelectronics", "PNP TO-126 1.5 A 80 V, hFE 100-250", ""),
    ("transistor", "TIP41C"): ("TIP41C", "STMicroelectronics", "NPN TO-220 6 A 100 V pass transistor", "needs a TO-220 heatsink, e.g. Aavid 577202B00000G"),
    ("resistor", "47k"): ("MFR-25FBF52-47K", "Yageo", "47k 1% 0.25 W metal film", ""),
    ("resistor", "1k"): ("MFR-25FBF52-1K", "Yageo", "1k 1% 0.25 W metal film", ""),
    ("resistor", "270"): ("MFR-25FBF52-270R", "Yageo", "270 R 1% 0.25 W", ""),
    ("resistor", "4.7k"): ("MFR-25FBF52-4K7", "Yageo", "4.7k 1% 0.25 W", ""),
    ("resistor", "22k"): ("MFR-25FBF52-22K", "Yageo", "22k 1% 0.25 W", ""),
    ("resistor", "470"): ("MFR-25FBF52-470R", "Yageo", "470 R 1% 0.25 W", ""),
    ("resistor", "47"): ("MFR-25FBF52-47R", "Yageo", "47 R 1% 0.25 W", ""),
    ("resistor", "10"): ("MFR-25FBF52-10R", "Yageo", "10 R 1% 0.25 W", ""),
    ("resistor", "10k"): ("MFR-25FBF52-10K", "Yageo", "10k 1% 0.25 W", ""),
    ("resistor", "0.47"): ("KNP200JR-73-0R47", "Yageo", "0.47 R 5% 2 W wirewound, emitter resistors", "any 0.47 R 2 W axial"),
    ("resistor", "0.33 2W"): ("KNP300JR-73-0R33", "Yageo", "0.33 R 5% 3 W wirewound, current sense", "any 0.33 R 2-3 W axial"),
    ("capacitor", "100n"): ("C320C104K5R5TA", "KEMET", "100 nF X7R 50 V radial 2.5 mm", ""),
    ("capacitor", "100p"): ("C315C101J1G5TA", "KEMET", "100 pF C0G 100 V radial 2.5 mm", "Miller cap: C0G only"),
    ("capacitor", "1000u"): ("UVR1C102MED", "Nichicon", "1000 uF 16 V radial 8x11.5 mm, 3.5 mm pitch", "check case 8 mm / pitch 3.5 mm"),
    ("capacitor", "100u"): ("UVR1C101MDD", "Nichicon", "100 uF 16 V radial 5x11 mm, 2.0 mm pitch", "footprint pitch 2.5 mm: bend leads"),
    ("capacitor", "220u"): ("UVR1C221MED", "Nichicon", "220 uF 16 V radial 6.3x11 mm, 2.5 mm pitch", ""),
    ("capacitor", "2200u"): ("UVR1E222MHD", "Nichicon", "2200 uF 25 V radial 12.5x20 mm, 5 mm pitch", "use a 35 V part with a 15 VAC transformer"),
    ("capacitor", "47u"): ("UVR1C470MDD", "Nichicon", "47 uF 16 V radial 5x11 mm, 2.0 mm pitch", ""),
    ("capacitor", "2.2u"): ("UVR1E2R2MDD", "Nichicon", "2.2 uF 25 V radial 5x11 mm, 2.0 mm pitch", ""),
    ("diode / LED", "1N5401"): ("1N5401-E3/54", "Vishay", "3 A 100 V rectifier DO-201AD", ""),
    ("diode / LED", "1N4007"): ("1N4007-E3/54", "Vishay", "1 A 1000 V rectifier DO-41", ""),
    ("diode / LED", "SB540"): ("SB540-E3/54", "Vishay", "5 A 40 V Schottky DO-201AD", ""),
    ("diode / LED", "13V 1W"): ("1N4743A-TAP", "Vishay", "13 V 1 W zener DO-41", ""),
    ("diode / LED", "LED"): ("WP7104ID", "Kingbright", "3 mm red LED", ""),
    ("diode / LED", "POWER LED"): ("WP7104ID", "Kingbright", "3 mm red LED (front panel, fit one of the two)", ""),
    ("potentiometer / trimmer", "10k log dual"): ("PTD902-2015K-A103", "Bourns", "9 mm dual-gang 10k audio taper, PC pins", "check pin pattern against the RK097 footprint before buying"),
    ("potentiometer / trimmer", "1k"): ("3296W-1-102LF", "Bourns", "1k 25-turn trimmer, bias set", ""),
    ("connector", "2-pin screw terminal 5.08 mm"): ("1715022", "Phoenix Contact", "MKDS 1,5/ 2-5,08 screw terminal", ""),
    ("connector", "1x3 pin header 2.54 mm"): ("PRPC003SAAN-RC", "Sullins", "1x3 pin header 2.54 mm", ""),
    ("connector", "1x2 pin header 2.54 mm"): ("PRPC002SAAN-RC", "Sullins", "1x2 pin header 2.54 mm", ""),
    ("test point", "test point loop (or a bare wire loop)"): ("5001", "Keystone", "PCB test point loop, white", "optional: a bent resistor lead works"),
    ("fuse", "1A T 5x20"): ("0218001.MXP", "Littelfuse", "5x20 mm 1 A time-lag fuse", "plus 2 clips, next line"),
}
EXTRA = [("3517", "Keystone", "5x20 mm fuse clip, PCB mount (2 per fuse)", 2, "footprint is the Littelfuse 100-series clip pattern; any 5x20 PCB clip at 20.5 mm spacing"),
         ("577202B00000G", "Aavid", "TO-220 clip-on heatsink for the PSU pass transistor", 1, ""),
         ("574502B00000G", "Aavid", "TO-220/TO-126 clip-on heatsink for the four output transistors (optional, for 4 ohm speakers)", 4, "")]

rows, notes = [], []
for r in csv.DictReader(open(HERE / "panel" / "bom_shopping.csv")):
    key = (r["kind"], r["value"])
    if key not in MPN:
        notes.append("no MPN for %s %s" % key); continue
    mpn, mfr, desc, note = MPN[key]
    row = {k: "" for k in HEADER}
    row.update({"Mfr Part Number (Input)": mpn, "Manufacturer Name": mfr, "Description": "%s [%s]" % (desc, r["value"]), "Order Quantity": r["qty"]})
    rows.append(row)
    if note: notes.append("%s: %s" % (mpn, note))
for mpn, mfr, desc, qty, note in EXTRA:
    row = {k: "" for k in HEADER}
    row.update({"Mfr Part Number (Input)": mpn, "Manufacturer Name": mfr, "Description": desc, "Order Quantity": qty})
    rows.append(row)
    if note: notes.append("%s: %s" % (mpn, note))
with open(HERE / "panel" / "bom_mouser.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=HEADER); w.writeheader(); w.writerows(rows)
(HERE / "panel" / "bom_mouser_notes.md").write_text("# Mouser BOM notes\n\nThe MPNs in bom_mouser.csv were chosen from memory and are NOT stock- or price-checked. "
    "Upload the CSV to Mouser's BOM tool, let it match each line, and replace any line it rejects with the equivalent it suggests.\n\n" +
    "\n".join("- " + n for n in notes) + "\n")
print("mouser lines:", len(rows), "qty:", sum(int(r["Order Quantity"]) for r in rows)); print("\n".join(notes))
