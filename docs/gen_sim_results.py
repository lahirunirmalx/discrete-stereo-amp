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
md = ["# 2. Simulation results", "", "All runs: ngspice 42, batch mode, decks in `sim/` (see `sim/README.md`). Transistor models are generic",
      "(BC547B hFE 290, BC557B 250, BD139 120, BD140 100, swept where stated); the speaker is a resistor; no thermal coupling.", "",
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
md += ["## 2.6 The channel as drawn (amp_final.cir)", "", "Operating point: output 5.93 V, output idle current 21.6 mA. 0.2 Vpk in, 8 ohm: 0.93 W at 0.76 percent THD.",
       "The KiCad netlist of both channels was checked against this deck (same net partition) with kicad/netcheck.py.", ""]
OUT.write_text("\n".join(md))
print("wrote", OUT, len("\n".join(md)), "chars")
