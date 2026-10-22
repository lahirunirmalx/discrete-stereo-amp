# Simulation decks (ngspice 42, run with `ngspice -b <deck>.cir`)

| Deck | What it answers | Result file |
|---|---|---|
| models.inc | BC547B/BC557B/BD139/BD140/1N4148 models used by every amp deck | |
| ampA.cir | Candidate A: single CE stage + shunt feedback. Midpoint vs hFE, gain vs source resistance. REJECTED | ampA.out |
| ampB.cir | Candidate B: diff pair + VAS (4 mA) + 2 diodes. Midpoint, Zin, power. Starved at 4 ohm | ampB.out |
| ampB2.cir | B with a 10 mA VAS (2 x 270 ohm load): hFE corners, 25/70 C, gain vs source, -3 dB points, power and THD vs load and hFE, 9 V rail | ampB2.out |
| ampB3.cir | Bias with one diode + resistor (10 to 47 ohm): Iq and THD. REJECTED | ampB3.out |
| ampB4.cir | Bias with Vbe multiplier (Rm1 560 to 1200): Iq at 25/70 C, THD at 50 mW, power vs load and output hFE | ampB4.out |
| ampB_sq.cir | Release 1: 1 kHz square wave into 8 ohm with 0, 100 n, 470 n in parallel: overshoot | (stdout) |
| amp_final.cir | The RELEASE 1 channel exactly as drawn in KiCad. Operating point and one 1 W run | (stdout) |
| amp_noise2.cir | The release 1 channel: gain, sensitivity and 20 Hz-20 kHz noise vs source resistance (pot position) | wrdata spectra |
| preamp.cir, preamp_noise.cir | Preamp study: bootstrapped follower buffer and a +15 dB gain stage, gain / Zin / THD / noise | (stdout) |
| psu.cir | RELEASE 1 supply (open-loop zener follower): 12 and 15 VAC at 0.1 to 1.1 A, short circuit, DC-in only, DC-in plus AC | psu.out |
| ampC.cir | RELEASE 2 front end: PNP pair, mirror load, LED current-source tail, NPN VAS, 220p + 47p compensation. hFE corners, bias, Zin, -3 dB, power and THD vs load | ampC.out |
| ampC_sq.cir, ampC_misc.cir, ampC_comp.cir | Release 2: square-wave overshoot vs load capacitance, response peaking, 25/70 C, NPN hFE; the 4 x 4 compensation sweep (run per combination, see the transcript in docs/02) | (stdout) |
| amp2_final.cir | The RELEASE 2 channel exactly as drawn in KiCad (netlist-checked), with the VU tap. Operating point, gain, two 8 ohm runs | amp2_final.out |
| psu2.cir | RELEASE 2 supply (closed loop): 12 and 15 VAC at 0.1 to 1.2 A, 1 A load step, short circuit, DC-in only, DC-in plus AC | psu2.out |
| psu2_dc.cir, psu2_step*.cir | Release 2 supply: set point and line regulation (DC sweep); load step vs compensation capacitor, output ESR and transistor gain | (stdout) |
| amp_line.cir, amp_sweep.cir, amp_tran.cir (in ~/electronics-notes/one-transistor-amp/) | The ORIGINAL one-transistor amp review | |

RESULT lines in the .out files are `key=value` pairs; THD lines follow their RESULT line. `docs/02-simulation-results.md`
is generated from these files by `docs/gen_sim_results.py`.
