"""Shared helpers for the stereo amp KiCad generators (schematic side).

Grid: u(n) = n x 2.54 mm. Orientation facts (verified with kicad-cli netlists
on the proco-rat project, see kisch.py):
  2-pin vertical part (R/C/CP/Fuse) rot 0:   pin 1 top    (y-1.5u), pin 2 bottom (y+1.5u)
  2-pin horizontal, rot 90:                  pin 1 left   (x-1.5u), pin 2 right  (x+1.5u)
  diode rot 0: K left, A right.   rot 90: A top, K bottom.   rot 270: K top, A bottom
  BC547/BD139 rot 0: B left (x-2u), C top (x+1u, y-2u), E bottom (x+1u, y+2u)
  PNP drawn with mirror="x": E top, C bottom
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from kisch import Sch

FP = {
    "R": "Custom:R_Axial_1206",
    "R_2W": "Resistor_THT:R_Axial_DIN0414_L11.9mm_D4.5mm_P15.24mm_Horizontal",
    "C": "Custom:C_P5_1206",
    "CP_S": "Custom:CE_P2_1206",      # up to 47u/25V
    "CP_M": "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm",      # 100u-220u/16V
    "CP_L": "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm",      # 470u-1000u/16V
    "CP_XL": "Capacitor_THT:CP_Radial_D13.0mm_P5.00mm",    # 2200u/25V
    "TO92": "Custom:TO92_SOT23",
    "TO220": "Package_TO_SOT_THT:TO-220-3_Vertical",       # accepts TO-126 and TO-92 too
    "D35": "Custom:D_DO35_SOD123",
    "D41": "Custom:D_DO41_SMA",
    "D201": "Custom:D_DO201_SMA",
    "LED": "LED_THT:LED_D3.0mm",
    "TRIM": "Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical",
    "POT2": "Potentiometer_THT:Potentiometer_Alps_RK097_Dual_Horizontal",
    "SCREW2": "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
    "H3": "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
    "H2": "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
    "TP": "TestPoint:TestPoint_Loop_D2.50mm_Drill1.0mm",
    "JP_OPEN": "Jumper:SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm",
    "JP_BRIDGED": "Jumper:SolderJumper-2_P1.3mm_Bridged_Pad1.0x1.5mm",
    "FUSE": "Fuse:Fuseholder_Clip-5x20mm_Littelfuse_100_Inline_P20.50x4.60mm_D1.30mm_Horizontal",
}


def u(n):
    return round(n * 2.54, 3)


class Gen:
    """Thin layer over kisch.Sch: grid coordinates, label helpers, power symbols."""

    def __init__(self, title, paper="A3"):
        self.s = Sch(title, paper)
        s = self.s
        self.L = {
            "R": s.lib("Device", "R"), "C": s.lib("Device", "C"), "CP": s.lib("Device", "C_Polarized"),
            "D": s.lib("Device", "D"), "DZ": s.lib("Device", "D_Zener"), "DS": s.lib("Device", "D_Schottky"),
            "LED": s.lib("Device", "LED"), "FUSE": s.lib("Device", "Fuse"),
            "TRIM": s.lib("Device", "R_Potentiometer_Trim"), "POT2": s.lib("Device", "R_Potentiometer_Dual"),
            "BC547": s.lib("Transistor_BJT", "BC547"), "BC557": s.lib("Transistor_BJT", "BC557"),
            "BD139": s.lib("Transistor_BJT", "BD139"), "BD140": s.lib("Transistor_BJT", "BD140"),
            "TIP41C": s.lib("Transistor_BJT", "TIP41C"),
            "TP": s.lib("Connector", "TestPoint"), "SCREW2": s.lib("Connector", "Screw_Terminal_01x02"),
            "H3": s.lib("Connector_Generic", "Conn_01x03"), "H2": s.lib("Connector_Generic", "Conn_01x02"),
            "JPO": s.lib("Jumper", "SolderJumper_2_Open"), "JPB": s.lib("Jumper", "SolderJumper_2_Bridged"),
            "GND": s.lib("power", "GND"), "V12": s.lib("power", "+12V"), "FLAG": s.lib("power", "PWR_FLAG"),
        }

    def part(self, lib, ref, val, gx, gy, rot=0, fp="", mirror=None, lbl="right"):
        x, y = u(gx), u(gy)
        if lbl == "right":
            ra, va = (x + 2.0, y - 1.9), (x + 2.0, y + 0.6)
        elif lbl == "above":
            ra, va = (x - 2.5, y - 5.4), (x - 2.5, y - 3.4)
        elif lbl == "below":
            ra, va = (x - 2.5, y + 3.2), (x - 2.5, y + 5.2)
        elif lbl == "left":
            ra, va = (x - 10.0, y - 1.9), (x - 10.0, y + 0.6)
        else:
            gx2, gy2 = lbl                      # grid units: reference here, value 1 grid lower
            ra, va = (u(gx2), u(gy2)), (u(gx2), u(gy2) + 2.0)
        return self.s.place(self.L[lib], ref, val, x, y, rot, mirror=mirror, footprint=fp, ref_at=ra, val_at=va)

    def P(self, name):
        """pin position in grid units"""
        x, y = self.s.pin(name)
        return (round(x / 2.54, 3), round(y / 2.54, 3))

    def W(self, *pts):
        self.s.wire(*[(u(a), u(b)) for a, b in pts])

    def J(self, gx, gy=None):
        if gy is None:
            gx, gy = gx
        self.s.junction((u(gx), u(gy)))

    def label(self, gx, gy, name, rot=0):
        self.s.label((u(gx), u(gy)), name, rot)

    def text(self, gx, gy, s, size=1.27):
        self.s.text((u(gx), u(gy)), s, size)

    def gnd(self, gx, gy):
        self.s.place(self.L["GND"], "#PWR", "GND", u(gx), u(gy), 0)

    def v12(self, gx, gy):
        self.s.place(self.L["V12"], "#PWR", "+12V", u(gx), u(gy), 0)

    def flag(self, gx, gy):
        self.s.place(self.L["FLAG"], "#FLG", "PWR_FLAG", u(gx), u(gy), 0)

    def tp(self, ref, net, gx, gy):
        """Test point: pin at (gx, gy); the loop symbol points up. Value = what to expect."""
        self.part("TP", ref, net, gx, gy, 0, FP["TP"], lbl="above")

    def write(self, stem, outdir):
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        self.s.write(outdir / (stem + ".kicad_sch"))
        pro = outdir / (stem + ".kicad_pro")
        if not pro.exists():
            pro.write_text('{\n  "meta": {"filename": "%s.kicad_pro", "version": 1},\n  "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []}\n}\n' % stem)
        return outdir / (stem + ".kicad_sch")
