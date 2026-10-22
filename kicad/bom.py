"""Production BOM from the four netlists: one CSV per board plus a combined one.
Columns: tolerance / rating, at least three substitutes for every transistor (with pinout caveats),
and a matching note. Hybrid footprints list both the through-hole part and the SMD alternative."""
import csv, re
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).parent
ALT = {"Custom:R_Axial_1206": ("axial 1/4 W", "1206"), "Custom:C_P5_1206": ("ceramic disc 5 mm", "1206"),
       "Custom:CE_P2_1206": ("electrolytic 5 mm radial", "1206 MLCC"), "Custom:D_DO35_SOD123": ("DO-35", "SOD-123"),
       "Custom:D_DO41_SMA": ("DO-41", "SMA"), "Custom:D_DO201_SMA": ("DO-201AD", "SMA (3 A part, e.g. S3M)"),
       "Custom:TO92_SOT23": ("TO-92", "SOT-23 (2-layer board only)")}

# TO-92 pinouts, flat face towards you, leads down, left to right:
#   BC546..BC550, BC556..BC560, BC337/BC327: C-B-E  (what the board expects)
#   2N3904/2N3906, PN2222A/PN2907A:          E-B-C  (fits only turned round, flat face away from the silk outline)
# TO-126 BD135..BD140: E-C-B. TO-220 TIP29..TIP42, BD243/BD244, MJE3055T/MJE2955T: B-C-E.
SMALL_NPN = "BC547B/C (fitted); BC548B/C; BC549C or BC550C (lower noise); BC337-25 (800 mA); 2N3904 or PN2222A only turned 180 deg (E-B-C pinout)"
SMALL_PNP = "BC557B/C (fitted); BC558B/C; BC559C or BC560C; BC327-25; 2N3906 or PN2907A only turned 180 deg (E-B-C pinout)"
OUT_NPN = "BD139-16 (fitted, E-C-B, bridges on the diagonal); BD135 or BD137 (E-C-B, same bridges); TIP41C or TIP31C (B-C-E: move the pad-1 and pad-3 bridges); BD243C (B-C-E, same move); BC337-40 for low power only (C-B-E: bridges 1->C 2->B 3->E)"
OUT_PNP = "BD140-16 (fitted, E-C-B); BD136 or BD138 (E-C-B); TIP42C or TIP32C (B-C-E: move pad-1/pad-3 bridges); BD244C (B-C-E); BC327-40 low power only (C-B-E)"
PASS_NPN = "TIP41C (fitted, B-C-E); TIP31C (3 A); BD243C; MJE3055T; TIP41A/B (lower voltage grade is fine at 20 V). All B-C-E: this position has no jumper block"

SPEC = {
    # (board, ref regex): (tolerance / rating, substitutes, matching or usage note)
    ("amp", r"Q[12]00[12]$"): ("hFE 200-450 (B or C grade)", SMALL_PNP, "PNP differential pair: fit the SAME part number AND grade for Q1 and Q2 of a channel, ideally from one strip. 10 mV Vbe mismatch only shifts the midpoint 0.23 V, so a DMM hFE match within 10 percent is plenty."),
    ("amp", r"Q[12]003$"): ("hFE 200-450", SMALL_NPN, "NPN voltage amplifier (VAS). No matching needed."),
    ("amp", r"Q[12]00[78]$"): ("hFE 200-450 (B or C grade)", SMALL_NPN, "Current-mirror pair: same part number and grade for Q7 and Q8 of a channel, from one strip; the 100 ohm emitter resistors hide the rest."),
    ("amp", r"Q[12]009$"): ("hFE 200-450", SMALL_PNP, "Tail current source. No matching."),
    ("amp", r"Q[12]006$"): ("hFE 200-450", SMALL_NPN, "Vbe multiplier: any of the BC547 family. Mount it touching or next to the output transistors so it tracks their temperature."),
    ("amp", r"Q[12]004$"): ("hFE 100-250 (-16 grade), 1.5 A, 80 V", OUT_NPN, "Complementary pair: use the same hFE grade for Q4 and Q5 (both -16, or both -10). Feedback corrects up to about 30 percent hFE difference; the trimmer corrects the Vbe difference. At hFE 40 the 4 ohm channel clips at 0.2 W, at 120 it makes 1.3 W."),
    ("amp", r"Q[12]005$"): ("hFE 100-250 (-16 grade), 1.5 A, 80 V", OUT_PNP, "See Q4. Fit both channels with the same four part numbers so L and R sound the same."),
    ("amp", r"D[12]001$"): ("3 mm RED LED, Vf 1.7-1.9 V at 2 mA", "any red 3 mm or 5 mm LED (fitted); two 1N4148 in series with R4 changed to 680 ohm; a red 0805/1206 LED soldered across the pads", "Tail current reference: tail = (Vf - 0.65 V) / 1.2k, about 1 mA. RED only: a green or blue LED (Vf 2 to 3 V) doubles the tail current. It also shows the channel is alive (glows faintly)."),
    ("amp", r"R[12]0004$"): ("1.2k, 1 percent, 1/4 W", "1.2k metal film; 1206 1 percent", "Sets the tail current with the LED (1 mA). 1k gives 1.15 mA, 1.5k gives 0.8 mA; both fine."),
    ("amp", r"R[12]00(16|17)$"): ("100 ohm, 1 percent, 1/4 W", "100R metal film; 1206 1 percent", "Mirror emitter degeneration: same value for R16 and R17 of a channel."),
    ("amp", r"R[12]0018$"): ("1k, 5 percent, 1/4 W", "1k; 2.2k if the VU meter is too sensitive", "VU meter tap: 1k in series with the speaker node to header J5. No effect when J5 is unused."),
    ("amp", r"C[12]0008$"): ("47 pF C0G/NP0, 10 percent, 50 V", "47p C0G; 33p to 68p; 1206 C0G", "Lead capacitor across the 22k feedback resistor: sets the -3 dB point (120 kHz) and the square-wave overshoot (5.7 percent). Not optional."),
    ("psu", r"Q[134]$"): ("hFE 200-450", SMALL_NPN, "Driver (Q1), clamp (Q3) and error amplifier (Q4). No matching."),
    ("psu", r"Q2$"): ("6 A, 100 V, TO-220 on a heatsink", PASS_NPN, "Pass transistor. Dissipates up to 4.9 W: heatsink of 10 C/W or better."),
    ("amp", r"R[12]0006$"): ("1 percent, 1/4 W", "22k metal film; 1206 1 percent", "Sets the gain with R7 (1 + 22k/1k = 23). Use 1 percent so left and right match within 2 percent."),
    ("amp", r"R[12]0007$"): ("1 percent, 1/4 W", "1k metal film; 1206 1 percent", "Gain-setting partner of R6: 1 percent."),
    ("amp", r"R[12]00(01|02|03)$"): ("5 percent, 1/4 W", "47k", "Bias divider and base feed: 5 percent moves the midpoint less than 0.3 V."),
    ("amp", r"R[12]00(05|08|11|12|15)$"): ("5 percent, 1/4 W", "same value, any type", ""),
    ("amp", r"R[12]00(09|10)$"): ("1 percent, 1/4 W", "470 / 1k metal film", "Vbe multiplier ratio; the trimmer covers the rest."),
    ("amp", r"RV[12]00$"): ("1k, multi-turn preferred (3296W / 3386P)", "1k 10-turn 3296W; 1k single-turn 3386P; 2k2 if you want more range (start at minimum)", "Set each channel to 7-10 mV across its 0.47 ohm emitter resistor (TP3 to TP2)."),
    ("amp", r"R[12]00(13|14)$"): ("5 percent, 2 W, 0.47 ohm", "0.47R 2 W metal oxide or wirewound; 0.5R or 0.39R also fine (both channels the same)", "Emitter resistors: match within 5 percent between Q4 and Q5 of one channel."),
    ("amp", r"C[12]0004$"): ("220 pF C0G/NP0, 10 percent, 50 V", "220p C0G; 1206 C0G; 330p also stable", "Miller compensation, works together with the 47p lead capacitor C8. Keep 220 to 330 pF, C0G only, never Y5V."),
    ("amp", r"C[12]0007$"): ("100 nF X7R, 50 V", "100n X7R or film", "Zobel."),
    ("amp", r"C[12]0001$"): ("2.2 uF, 25 V, 20 percent", "2.2u electrolytic (+ to the base side) or 2.2u film / 1206 X7R", "Input coupling; -3 dB with the 46k input is 1.6 Hz, value is not critical."),
    ("amp", r"C[12]0002$"): ("47 uF, 16 V", "22u to 100u electrolytic", "Bias decoupling."),
    ("amp", r"C[12]0003$"): ("220 uF, 16 V", "100u to 470u", "Feedback return: sets the low-frequency gain roll-off (0.7 Hz at 220u)."),
    ("amp", r"C[12]0005$"): ("100 uF, 16 V", "47u to 220u", "Bootstrap."),
    ("amp", r"C[12]0006$"): ("1000 uF, 16 V, low ESR preferred", "1000u to 2200u 16 V", "Output coupling: -3 dB at 34 Hz into 4 ohm, 20 Hz into 8 ohm; 2200u halves those."),
    ("amp", r"C1$"): ("1000 uF, 16 V", "1000u to 2200u", "Rail reservoir."),
    ("amp", r"C2$"): ("100 nF X7R", "100n", "Rail decoupling."),
    ("psu", r"C[12]$"): ("2200 uF, 25 V (35 V if the transformer is 15 VAC)", "2200u to 4700u", "Reservoir: raw rail peaks at 21 V no-load from 15 VAC, 23 V at mains +10 percent."),
    ("psu", r"C3$"): ("10 uF, 16 V", "4.7u to 47u", "Reference filter across the 5.6 V zener."),
    ("psu", r"C6$"): ("47 nF X7R or film, 50 V", "22n to 100n", "Loop compensation (Q4 collector to base). 22n is faster, 100n slower; all three are stable."),
    ("psu", r"C7$"): ("100 nF X7R, 50 V", "100n", "Feeds fast output steps to the error amplifier."),
    ("psu", r"R5$"): ("8.2k, 1 percent, 1/4 W", "8.2k", "Top of the output divider (with RV1)."),
    ("psu", r"R6$"): ("10k, 1 percent, 1/4 W", "10k", "Bottom of the output divider. FB = 6.3 V (zener + Vbe) when VOUT is 12.0 V."),
    ("psu", r"R7$"): ("2.2k, 0.5 W", "2.2k 0.5 W (dissipates 15 mW normally, 0.1 W with the output shorted)", "Driver base pull-up from the raw rail; the error amplifier pulls it down."),
    ("psu", r"RV1$"): ("2k trimmer, multi-turn preferred (3296W)", "2k 3296W (fitted); 2.2k; 1k (range 11.4 to 12.1 V); 5k with R5 = 6.8k (10.6 to 13.7 V)", "Sets VOUT: 11.4 to 12.7 V. Set 12.0 V, or 11.5 V with a 12 VAC transformer."),
    ("psu", r"C4$"): ("220 uF, 16 V", "100u to 470u", ""),
    ("psu", r"C5$"): ("100 nF X7R", "100n", ""),
    ("psu", r"D[1-4]$"): ("3 A, 100 V or more", "1N5401 (fitted); 1N5402 / 1N5404 / 1N5408 (same package, higher voltage); SB540 Schottky (less drop, runs cooler); S3M in SMA", "All four the same type."),
    ("psu", r"D5$"): ("5.6 V, 0.5 W, 5 percent", "1N5232B (fitted); BZX55C5V6; BZX79C5V6; BZX85C5V6 (1 W); 1N4734A", "Reference. 5.6 V has near-zero tempco and its +2 mV/C cancels Q4's -2 mV/C Vbe; 5.1 V or 6.2 V also work, the trimmer absorbs the difference."),
    ("psu", r"D6$"): ("1 A, 100 V or more", "1N4007 (fitted); 1N4004; UF4007; SMA S1M", "Reverse protection of the pass transistor."),
    ("psu", r"D8$"): ("5 A Schottky, 40 V", "SB540 (fitted); 1N5822 (3 A); SR540; MBR540; SS54 in SMA", "DC-in path, 0.4 V drop."),
    ("psu", r"R1$"): ("4.7k, 0.5 W", "4.7k", "Bleeder."),
    ("psu", r"R2$"): ("1k, 1/4 W, 5 percent", "1k", "Zener feed from the regulated output: 6 mA."),
    ("psu", r"R3$"): ("0.33 ohm, 3 W, 5 percent", "0.33R 2-3 W; 0.47R gives a 1.4 A clamp; 0.22R gives 3 A", "Clamp current = 0.65 V / R3."),
    ("psu", r"R4$"): ("1k, 1/4 W", "470R to 2k2", "LED current 10 mA at 1k."),
    ("psu", r"F1$"): ("1 A slow-blow (T) 5x20 mm + 2 clips", "1 A T (fitted); 1.6 A T for a 15 VAC 2 A transformer", "On the transformer secondary."),
    ("psu", r"D7$"): ("3 mm LED, any colour", "any 3 mm or 5 mm LED", "Fit D7 here OR D1 on the volume board, not both."),
    ("vol", r"D1$"): ("3 mm LED, any colour", "any 3 mm or 5 mm LED", "Front-panel power LED, fed from PSU J5 by two wires (pin 1 = +)."),
    ("hp", r"R[12]$"): ("120 ohm, 1 percent, 1/4 W", "120R (IEC 61938, fitted); 33R to 68R for a louder low-impedance drive; 330R for sensitive in-ear phones; 0R or bridge JP1/JP2 for direct drive", "Same value for both channels. 8 mW into 32 ohm at full drive with 120 R."),
    ("hp", r"SW1$"): ("DPDT slide switch, 2 x 3 pins, 2.5 mm pitch", "C&K JS202011CQN (fitted); any DPDT slide on a 2x3 2.5 mm pattern; a DPDT toggle on flying leads to the six pads", "Speakers on pins 1 / 6, headphones on pins 3 / 4, commons 2 / 5."),
    ("hp", r"J4$"): ("3.5 mm TRS jack, through-hole, CUI SJ1-3535NG pattern", "SJ1-3535NG (fitted); SJ1-3535N; SJ1-3525N (same T/R/S pins); or any panel-mount jack wired to J5", "Only T, R and S are used; the switch pins TN / RN stay open."),
    ("hp", r"J[1235]$"): ("2.54 mm header or 5.08 mm screw terminal", "", ""),
    ("vol", r"RV1$"): ("10k log (A103) dual, 6 pins, 9 mm", "Alps RK097 dual 10k A (fitted); any RK09-style 6-pin dual 10k log; 20k log (slight gain loss at mid travel); 10k linear works but the law feels wrong", "Pin 3 = clockwise end = input, pin 1 = ground, pin 2 = wiper. Clockwise should be louder; if not, swap the outer two wires."),
    ("amp", r"J[1-4]$"): ("5.08 mm screw terminal or 2.54 mm header", "Phoenix MKDS 1.5/2; any 5.08 mm 2-pin block", ""),
    ("psu", r"J[1-4]$"): ("5.08 mm screw terminal", "Phoenix MKDS 1.5/2; any 5.08 mm 2-pin block", ""),
}


def spec(board, ref):
    for (b, pat), v in SPEC.items():
        if b == board and re.match(pat, ref):
            return v
    return ("5 percent / 20 percent, standard", "", "")


def rows(netfile, board):
    txt = Path(netfile).read_text()
    groups = defaultdict(list)
    for chunk in txt[txt.find("(components"):txt.find("(libparts")].split("(comp (ref ")[1:]:
        ref = re.match(r'"([^"]+)"', chunk).group(1)
        val = re.search(r'\(value "([^"]*)"\)', chunk).group(1)
        fp = re.search(r'\(footprint "([^"]*)"\)', chunk).group(1)
        if ref.startswith("JP"):
            continue
        groups[(val, fp, spec(board, ref))].append(ref)
    out = []
    for (val, fp, (tol, alts, note)), refs in sorted(groups.items(), key=lambda kv: (kv[1][0][0], kv[0][0])):
        tht, smd = ALT.get(fp, (fp.split(":")[-1], ""))
        out.append({"board": board, "qty": len(refs),
                    "refs": " ".join(sorted(refs, key=lambda r: (re.sub(r"\d", "", r), int(re.sub(r"\D", "", r) or 0)))),
                    "value": val, "through_hole": tht, "smd_alternative": smd, "tolerance_rating": tol,
                    "substitutes": alts, "matching_note": note})
    return out


allrows = []
for b in ("amp", "psu", "vol", "hp"):
    r = rows(HERE / b / (b + ".net"), b)
    allrows += r
    with open(HERE / b / ("bom_%s.csv" % b), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(r[0].keys())); w.writeheader(); w.writerows(r)
with open(HERE / "panel" / "bom_all.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(allrows[0].keys())); w.writeheader(); w.writerows(allrows)
nq = sum(1 for r in allrows if r["refs"].startswith("Q"))
print("BOM lines:", len(allrows), "total parts:", sum(r["qty"] for r in allrows), "+ 38 solder jumpers; transistor lines:", nq)
for r in allrows:
    if r["refs"].startswith("Q"):
        print("  %-4s %-14s %-9s %s" % (r["board"], r["refs"], r["value"], r["substitutes"][:90]))
