# Simulation decks (ngspice 42, run with `ngspice -b <deck>.cir`)

| Deck | What it answers | Result file |
|---|---|---|
| models.inc | BC547B/BC557B/BD139/BD140/1N4148 models used by every amp deck | |
| ampA.cir | Candidate A: single CE stage + shunt feedback. Midpoint vs hFE, gain vs source resistance. REJECTED | ampA.out |
| ampB.cir | Candidate B: diff pair + VAS (4 mA) + 2 diodes. Midpoint, Zin, power. Starved at 4 ohm | ampB.out |
| ampB2.cir | B with a 10 mA VAS (2 x 270 ohm load): hFE corners, 25/70 C, gain vs source, -3 dB points, power and THD vs load and hFE, 9 V rail | ampB2.out |
| ampB3.cir | Bias with one diode + resistor (10 to 47 ohm): Iq and THD. REJECTED | ampB3.out |
| ampB4.cir | Bias with Vbe multiplier (Rm1 560 to 1200): Iq at 25/70 C, THD at 50 mW, power vs load and output hFE | ampB4.out |
| ampB_sq.cir | 1 kHz square wave into 8 ohm with 0, 100 n, 470 n in parallel: overshoot | (stdout) |
| amp_final.cir | The channel exactly as drawn in KiCad (netlist-checked). Operating point and one 1 W run | (stdout) |
| psu.cir | Supply: 12 and 15 VAC at 0.1 to 1.1 A, short circuit, DC-in only, DC-in plus AC | psu.out |
| amp_line.cir, amp_sweep.cir, amp_tran.cir (in ~/electronics-notes/one-transistor-amp/) | The ORIGINAL one-transistor amp review | |

RESULT lines in the .out files are `key=value` pairs; THD lines follow their RESULT line. `docs/02-simulation-results.md`
is generated from these files by `docs/gen_sim_results.py`.
