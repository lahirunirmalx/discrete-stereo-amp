"""Generate docs/02-simulation-results.md from the ngspice result files in sim/."""
from pathlib import Path
SIM = Path(__file__).resolve().parent.parent / "sim"
OUT = Path(__file__).resolve().parent / "02-simulation-results.md"


def results(path):
    rows, cur = [], None
    for l in open(path):
        if l.startswith("RESULT"):
            p = l.split(); kv = dict(x.split("=", 1) for x in p[2:]); kv["_k"] = p[1]; rows.append(kv); cur = kv
        elif "THD" in l and cur is not None:
            cur["thd"] = float(l.split("THD:")[1].split("%")[0]); cur = None
    return rows


def f(v, s=1, d=1): return "%.*f" % (d, float(v) * s)
def table(head, rows):
    return "| " + " | ".join(head) + " |\n|" + "---|" * len(head) + "\n" + "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in rows) + "\n"


A = results(SIM / "ampA.out"); B = results(SIM / "ampB.out"); B2 = results(SIM / "ampB2.out"); B3 = results(SIM / "ampB3.out"); B4 = results(SIM / "ampB4.out"); P = results(SIM / "psu.out")
C = results(SIM / "ampC.out"); P2 = results(SIM / "psu2.out"); F2 = results(SIM / "amp2_final.out")
md = ["# 2. Simulation results", "", "All runs: ngspice 42, batch mode, decks in `sim/` (see `sim/README.md`). Transistor models are generic",
      "(BC547B hFE 290, BC557B 250, BD139 120, BD140 100, swept where stated); the speaker is a resistor; no thermal coupling.", "",
      "Sections 2.1 to 2.6 are the release 1 record (the diff-pair-with-resistor-load channel and the open-loop supply).",
      "Sections 2.7 to 2.9 are release 2: the mirror-loaded front end and the closed-loop supply that the boards now carry.", "",
      "## 2.1 Choosing the front end (ampA.cir vs ampB.cir)", "",
      "Two candidates were run through the same three tests: does the output midpoint stay near half the rail for any transistor",
      "gain, does the gain stay put when the volume pot moves (source resistance 0 to 5k), and how much does it distort.", ""]
md.append("**Candidate A, single CE stage with shunt feedback (REJECTED):**\n")
md.append(table(["BC547 hFE", "output hFE", "midpoint (V)", "supply (mA)"], [(r["bf1"], r["bfo"], f(r["vout"], 1, 2), f(r["isupply"], -1e3, 1)) for r in A if r["_k"] == "op"]))
md.append(table(["source (ohm)", "gain", "Zin (k)"], [(r["rs"], f(r["gain"], 1, 1), f(r["zin"], 1e-3, 1)) for r in A if r["_k"] == "ac"]))
md.append("Midpoint moves 1.1 V with hFE, gain moves 22 percent with the pot, and the gain is only 6. Rejected.\n")
md.append("**Candidate B, differential pair with series feedback (chosen):**\n")
md.append(table(["BC547 hFE", "output hFE", "midpoint (V)", "supply (mA)", "output Iq (mA)"], [(r["bf1"], r["bfo"], f(r["vout"], 1, 2), f(r["isupply"], -1e3, 1), f(r["iqout"], 1e3, 1)) for r in B if r["_k"] == "op"]))
md.append(table(["source (ohm)", "gain", "Zin (k)"], [(r["rs"], f(r["gain"], 1, 1), f(r["zin"], 1e-3, 1)) for r in B if r["_k"] == "ac"]))
md.append("Midpoint 5.90 to 5.97 V for every corner, gain 20 to 18 across the pot. But with a 4 mA VAS (2 x 680 ohm bootstrap load) the 4 ohm output starved:\n")
md.append(table(["load (ohm)", "Vin pk (V)", "P out (W)", "THD %"], [(r["rl"], r["amp"], f(r["pout"], 1, 2), "%.1f" % r["thd"]) for r in B if r["_k"] == "tran" and r["rl"] == "4"]))
md += ["## 2.2 The channel with a 10 mA VAS (ampB2.cir, 2 x 270 ohm bootstrap load)", ""]
md.append(table(["BC547 hFE", "output hFE", "midpoint (V)", "VAS current (mA)"], [(r["bf1"], r["bfo"], f(r["vout"], 1, 2), f(r["ivas"], 1e3, 1)) for r in B2 if r["_k"] == "op"]))
md.append(table(["source (ohm)", "gain at 1 kHz", "Zin (k)"], [(r["rs"], f(r["gain"], 1, 1), f(r["zin"], 1e-3, 1)) for r in B2 if r["_k"] == "ac"]))
md.append(table(["load (ohm)", "-3 dB low (Hz)", "-3 dB high (kHz)"], [(r["rl"], f(r["f3"], 1, 0), f(r["fh"], 1e-3, 0)) for r in B2 if r["_k"] == "f3"]))
md.append("Square wave, 1 kHz, +-0.1 V in, 8 ohm load (ampB_sq.cir): overshoot 5.6 percent with no capacitance, 5.5 percent with 100 nF, 6.9 percent with 470 nF across the speaker.\n")
md += ["## 2.3 Output bias network (ampB3.cir, ampB4.cir)", "", "One 1N4148 plus a resistor (ampB3, REJECTED):", ""]
md.append(table(["resistor (ohm)", "temp (C)", "Iq (mA)"], [(r["rb"], r["t"], f(r["iqout"], 1e3, 3)) for r in B3 if r["_k"] == "bias"]))
md.append(table(["resistor (ohm)", "load", "P out (mW)", "THD % at 50 mW"], [(r["rb"], r["rl"], f(r["pout"], 1e3, 0), "%.2f" % r["thd"]) for r in B3 if r["_k"] == "tran"]))
md.append("Vbe multiplier (ampB4, chosen; Rm1 is the 470 ohm plus trimmer total, 820 shipped):\n")
md.append(table(["Rm1 (ohm)", "temp (C)", "Iq (mA)", "V across (V)", "midpoint (V)"], [(r["rm"], r["t"], f(r["iqout"], 1e3, 1), f(r["vbias"], 1, 3), f(r["vout"], 1, 2)) for r in B4 if r["_k"] == "bias"]))
md.append(table(["Rm1 (ohm)", "load", "P out (mW)", "THD % at 50 mW"], [(r["rm"], r["rl"], f(r["pout"], 1e3, 0), "%.2f" % r["thd"]) for r in B4 if r["_k"] == "tran"]))
md += ["## 2.4 Output power vs load and output-device hFE (ampB4.cir, Rm1 820, 2.5k source)", ""]
md.append(table(["output hFE", "load (ohm)", "Vin pk (mV)", "P out (W)", "I supply (mA)", "P Q4 (W)", "THD %"],
                [(r["bfo"], r["rl"], f(r["amp"], 1e3, 0), f(r["pout"], 1, 2), f(r["isupply"], -1e3, 0), f(r["pq4"], 1, 2), "%.2f" % r["thd"]) for r in B4 if r["_k"] == "power"]))
md.append("At 9 V (ampB2.cir, hFE 120, 4 ohm): " + "; ".join("%s mVpk -> %s W at %.1f%% THD" % (f(r["amp"], 1e3, 0), f(r["pout"], 1, 2), r["thd"]) for r in B2 if r["_k"] == "tran9") + ".\n")
md += ["## 2.5 Power supply (psu.cir)", "", "50 Hz, 0.8 ohm winding resistance, 0.02 ohm fuse, 2 x 2200 uF, 13 V zener, BC547 + TIP41C, 0.33 ohm clamp.", ""]
md.append(table(["VAC", "I load (A)", "raw trough (V)", "V out (V)", "ripple (mV)", "I secondary (A rms)", "P pass (W)"],
                [({"16.97": "12", "21.21": "15"}[r["vs"]], f(r["iload"], 1, 2), f(r["vraw_trough"], 1, 1), f(r["vout"], 1, 2), f(r["ripple_mV"], 1, 0), f(r["iac_rms"], 1, 2), f(r["pq2"], 1, 1)) for r in P if r["_k"] == "ac"]))
c = [r for r in P if r["_k"] == "clamp"][0]; dc = [r for r in P if r["_k"] == "dconly"]; bo = [r for r in P if r["_k"] == "both"][0]
md.append("Short circuit (0.5 ohm load, 15 VAC): %s A, %s V out, %s W in the pass transistor until the fuse opens.\n" % (f(c["iload"], 1, 2), f(c["vout"], 1, 2), f(c["pq2"], 1, 0)))
md.append(table(["DC-in only, load (ohm)", "V out", "raw rail", "pass transistor B-E reverse (V)", "driver B-E (V)"], [(r["rl"], f(r["vout"], 1, 2), f(r["vraw"], 1, 2), f(r["q2_veb_rev"], 1, 2), f(r["q1_veb_rev"], 1, 2)) for r in dc]))
md.append("Both sources (15 VAC and 12 V DC, 15 ohm load): V out %s V, %s A of the load comes from the DC input.\n" % (f(bo["vout"], 1, 2), f(bo["i_from_dcin"], -1, 2)))
md += ["## 2.6 The release 1 channel as drawn (amp_final.cir)", "", "Operating point: output 5.93 V, output idle current 21.6 mA. 0.2 Vpk in, 8 ohm: 0.93 W at 0.76 percent THD.", ""]
md += ["## 2.7 Release 2 front end: PNP pair, current-mirror load, current-source tail, NPN VAS (ampC.cir)", "",
       "Same output stage, bias spreader and feedback network as release 1. The input pair is now PNP (BC557) with an NPN",
       "current-mirror load (100 ohm emitters), the tail is a BC557 current source referenced to a red LED (about 1 mA), the",
       "VAS is an NPN with a 47 ohm emitter resistor and a bootstrapped 2 x 270 ohm load from +12 V, and the compensation is",
       "220 pF Miller plus 47 pF across the 22k feedback resistor.", ""]
md.append(table(["BC557 hFE", "output hFE", "midpoint (V)", "supply (mA)", "output Iq (mA)", "VAS (mA)", "tail (mA)"],
                [(r["bf1"], r["bfo"], f(r["vout"], 1, 2), f(r["isupply"], 1e3, 1), f(r["iqout"], 1e3, 1), f(r["ivas"], 1e3, 1), f(r["itail"], 1e3, 2)) for r in C if r["_k"] == "op"]))
md.append(table(["Rm1 + RV (ohm)", "Iq (mA)"], [(r["rm"], f(r["iqout"], 1e3, 1)) for r in C if r["_k"] == "bias"]))
md.append(table(["source (ohm)", "gain at 1 kHz", "Zin (k)"], [(r["rs"], f(r["gain"], 1, 1), f(r["zin"], 1e-3, 1)) for r in C if r["_k"] == "ac"]))
f3 = [r for r in C if r["_k"] == "f3"][0]
md.append("Bandwidth (8 ohm, 2.5k source): -3 dB at %s Hz and %s kHz.\n" % (f(f3["f3"], 1, 0), f(f3["fh"], 1e-3, 0)))
md.append(table(["load (ohm)", "Vin pk (mV)", "P out (W)", "THD % (BD139 / BD140 hFE 120 / 120)"], [(r["rl"], f(r["amp"], 1e3, 0), f(r["pout"], 1, 3), "%.3f" % r["thd"]) for r in C if r["_k"] == "tran"]))
md.append("For comparison the release 1 channel gave 0.03 percent at 50 mW and 0.18 percent at 50 mW into 4 ohm, 0.76 percent at 0.93 W into 8 ohm.\n")
md.append("Compensation sweep (ampC_comp runs, 1 kHz square wave +-0.1 V, 100 nF across 8 ohm): 100p / no lead cap: 34 percent overshoot and 1.3 dB peaking at 1 MHz; 220p / 22p: 12.7 percent; 220p / 47p: 5.7 percent, no peaking, -3 dB 119 kHz (chosen); 330p / 47p: 5.6 percent, 107 kHz; 470p / 100p: 5.7 percent, 55 kHz. With the chosen values: 5.6 percent with no capacitance, 14.4 percent with 470 nF, 16.0 percent with 2.2 uF across the speaker (release 1: 6.9 percent at 470 nF). Stable in every case.\n")
md.append("Temperature (ampC_misc): output Iq 21.1 mA at 25 C, 30.3 mA at 70 C with the spreader held at 25 C; midpoint 6.12 to 6.14 V. BC547 hFE 110 to 450: midpoint 6.12 to 6.14 V.\n")
md += ["## 2.8 The release 2 channel as drawn (amp2_final.cir, default models BD139 hFE 120 / BD140 hFE 100)", ""]
op = [r for r in F2 if r["_k"] == "op"][0]; ac = [r for r in F2 if r["_k"] == "ac"][0]
md.append("Operating point: output %s V, Q1 base %s V, LED reference %s V, output Iq %s mA, VAS %s mA, tail %s mA, supply %s mA per channel. Gain %s, Zin %sk; VU header %s V per volt of speaker signal (open).\n" % (
    f(op["vout"], 1, 2), f(op["vb1"], 1, 2), f(op["vled"], 1, 2), f(op["iqout"], 1e3, 1), f(op["ivas"], 1e3, 1), f(op["itail"], 1e3, 2), f(op["isupply"], -1e3, 1), f(ac["gain"], 1, 1), f(ac["zin"], 1e-3, 0), f(ac["vu"], 1 / float(ac["gain"]), 2)))
md.append(table(["load (ohm)", "Vin pk (mV)", "P out (W)", "THD %"], [(r["rl"], f(r["amp"], 1e3, 0), f(r["pout"], 1, 2), "%.3f" % r["thd"]) for r in F2 if r["_k"] == "tran"]))
md.append("The 0.045 percent at 0.29 W (vs 0.019 percent in 2.7) is the BD139 / BD140 hFE mismatch of the default models; matched outputs give the 2.7 figure. The KiCad netlist of both channels was checked against this deck (same net partition) with kicad/netcheck.py.\n")
md += ["## 2.9 Release 2 power supply, closed loop (psu2.cir)", "", "Bridge and reservoir as before. The pass pair (BC547 + TIP41C) is driven from the raw rail through 2.2k; a BC547 error",
       "amplifier compares a divider of VOUT (8.2k + 2k trimmer over 10k) with a 5.6 V zener fed from the regulated output and",
       "pulls the driver base down; 47 nF across the error amplifier sets the loop speed, 100 nF from VOUT to the divider feeds",
       "fast steps through. The clamp (0.33 ohm, Q3 on the driver base) and the DC-in path are unchanged.", ""]
md.append(table(["VAC", "I load (A)", "raw trough (V)", "V out (V)", "ripple (mV)", "I secondary (A rms)", "P pass (W)"],
                [({"16.97": "12", "21.21": "15"}[r["vs"]], f(r["iload"], 1, 2), f(r["vraw_trough"], 1, 1), f(r["vout"], 1, 2), f(r["ripple_mV"], 1, 0), f(r["iac_rms"], 1, 2), f(r["pq2"], 1, 1)) for r in P2 if r["_k"] == "ac"]))
s = [r for r in P2 if r["_k"] == "step"][0]; c = [r for r in P2 if r["_k"] == "clamp"][0]; dc = [r for r in P2 if r["_k"] == "dconly"]; bo = [r for r in P2 if r["_k"] == "both"][0]
md.append("Load step 0.1 A to 1 A to 0.1 A (15 VAC): %s V before, %s V during, dip to %s V, overshoot to %s V, no ringing (release 1 dropped 0.4 V). Compensation sweep (psu2_step runs, 0.2 ohm ESR on the output capacitor): 22n, 47n and 100n all settle without ringing; with the slowest transistors (BC547 hFE 110, TIP41C hFE 25) the 1 A ripple is 90 mV, with typical parts 40 mV; 1 ohm ESR costs a 0.8 V dip (ESR times the step), nothing else.\n" % (f(s["vbefore"], 1, 2), f(s["vduring"], 1, 2), f(s["dip"], 1, 2), f(s["overshoot"], 1, 2)))
md.append("Short circuit (0.5 ohm load, 15 VAC): %s A, %s V out, %s W in the pass transistor until the fuse opens.\n" % (f(c["iload"], 1, 2), f(c["vout"], 1, 2), f(c["pq2"], 1, 0)))
md.append(table(["DC-in only, load (ohm)", "V out", "raw rail", "pass transistor B-E reverse (V)", "driver B-E (V)"], [(r["rl"], f(r["vout"], 1, 2), f(r["vraw"], 1, 2), f(r["q2_veb_rev"], 1, 2), f(r["q1_veb_rev"], 1, 2)) for r in dc]))
md.append("Both sources (15 VAC and 12 V DC, 15 ohm load): V out %s V, %s mA of the load comes from the DC input (the regulator at 12.0 V sits just above the 11.6 V the diode path can supply).\n" % (f(bo["vout"], 1, 2), "%.2f" % abs(float(bo["i_from_dcin"]) * 1e3)))
md.append("Set point (psu2_dc.cir): with the trimmer at 900 ohm the output is 12.0 V; line regulation 11.9 to 12.0 V for a raw rail of 13 to 19 V. With a 12 VAC transformer the raw rail is only 1.3 V above the output at 0.4 A, so set 11.5 V there.\n")
OUT.write_text("\n".join(md))
print("wrote", OUT, len("\n".join(md)), "chars")
