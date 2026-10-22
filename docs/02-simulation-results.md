# 2. Simulation results

All runs: ngspice 42, batch mode, decks in `sim/` (see `sim/README.md`). Transistor models are generic
(BC547B hFE 290, BC557B 250, BD139 120, BD140 100, swept where stated); the speaker is a resistor; no thermal coupling.

Sections 2.1 to 2.6 are the release 1 record (the diff-pair-with-resistor-load channel and the open-loop supply).
Sections 2.7 to 2.9 are release 2: the mirror-loaded front end and the closed-loop supply that the boards now carry.

## 2.1 Choosing the front end (ampA.cir vs ampB.cir)

Two candidates were run through the same three tests: does the output midpoint stay near half the rail for any transistor
gain, does the gain stay put when the volume pot moves (source resistance 0 to 5k), and how much does it distort.

**Candidate A, single CE stage with shunt feedback (REJECTED):**

| BC547 hFE | output hFE | midpoint (V) | supply (mA) |
|---|---|---|---|
| 110 | 40 | 7.77 | 6.8 |
| 110 | 120 | 7.77 | 7.3 |
| 110 | 250 | 7.77 | 7.4 |
| 290 | 40 | 6.91 | 9.1 |
| 290 | 120 | 6.91 | 9.8 |
| 290 | 250 | 6.91 | 10.0 |
| 450 | 40 | 6.66 | 9.8 |
| 450 | 120 | 6.66 | 10.5 |
| 450 | 250 | 6.66 | 10.8 |

| source (ohm) | gain | Zin (k) |
|---|---|---|
| 1 | 5.9 | 17.2 |
| 2500 | 5.2 | 17.2 |
| 5000 | 4.6 | 17.2 |

Midpoint moves 1.1 V with hFE, gain moves 22 percent with the pot, and the gain is only 6. Rejected.

**Candidate B, differential pair with series feedback (chosen):**

| BC547 hFE | output hFE | midpoint (V) | supply (mA) | output Iq (mA) |
|---|---|---|---|---|
| 110 | 40 | 5.90 | 21.5 | 17.5 |
| 110 | 120 | 5.90 | 23.4 | 19.1 |
| 110 | 250 | 5.90 | 24.0 | 19.6 |
| 290 | 40 | 5.96 | 21.8 | 17.7 |
| 290 | 120 | 5.96 | 23.8 | 19.4 |
| 290 | 250 | 5.96 | 24.3 | 19.8 |
| 450 | 40 | 5.97 | 21.9 | 17.8 |
| 450 | 120 | 5.97 | 23.8 | 19.4 |
| 450 | 250 | 5.97 | 24.4 | 19.9 |

| source (ohm) | gain | Zin (k) |
|---|---|---|
| 1 | 20.1 | 41.7 |
| 2500 | 19.0 | 41.7 |
| 5000 | 18.0 | 41.7 |

Midpoint 5.90 to 5.97 V for every corner, gain 20 to 18 across the pot. But with a 4 mA VAS (2 x 680 ohm bootstrap load) the 4 ohm output starved:

| load (ohm) | Vin pk (V) | P out (W) | THD % |
|---|---|---|---|
| 4 | 0.03 | 0.03 | 0.4 |
| 4 | 0.1 | 0.30 | 4.5 |
| 4 | 0.2 | 0.62 | 28.0 |
| 4 | 0.3 | 0.77 | 35.0 |

## 2.2 The channel with a 10 mA VAS (ampB2.cir, 2 x 270 ohm bootstrap load)

| BC547 hFE | output hFE | midpoint (V) | VAS current (mA) |
|---|---|---|---|
| 110 | 40 | 5.85 | 9.6 |
| 110 | 250 | 5.85 | 9.6 |
| 450 | 40 | 5.95 | 9.8 |
| 450 | 250 | 5.95 | 9.8 |

| source (ohm) | gain at 1 kHz | Zin (k) |
|---|---|---|
| 1 | 21.2 | 43.4 |
| 2500 | 20.1 | 43.4 |
| 5000 | 19.0 | 43.4 |

| load (ohm) | -3 dB low (Hz) | -3 dB high (kHz) |
|---|---|---|
| 4 | 34 | 256 |
| 8 | 20 | 283 |

Square wave, 1 kHz, +-0.1 V in, 8 ohm load (ampB_sq.cir): overshoot 5.6 percent with no capacitance, 5.5 percent with 100 nF, 6.9 percent with 470 nF across the speaker.

## 2.3 Output bias network (ampB3.cir, ampB4.cir)

One 1N4148 plus a resistor (ampB3, REJECTED):

| resistor (ohm) | temp (C) | Iq (mA) |
|---|---|---|
| 10 | 25 | 0.002 |
| 10 | 70 | 0.031 |
| 22 | 25 | 0.020 |
| 22 | 70 | 0.230 |
| 33 | 25 | 0.154 |
| 33 | 70 | 1.394 |
| 47 | 25 | 1.958 |
| 47 | 70 | 10.554 |

| resistor (ohm) | load | P out (mW) | THD % at 50 mW |
|---|---|---|---|
| 10 | 4 | 27 | 5.36 |
| 10 | 8 | 17 | 5.05 |
| 22 | 4 | 30 | 3.83 |
| 22 | 8 | 18 | 3.55 |
| 33 | 4 | 31 | 2.58 |
| 33 | 8 | 19 | 2.31 |
| 47 | 4 | 34 | 1.25 |
| 47 | 8 | 21 | 0.96 |

Vbe multiplier (ampB4, chosen; Rm1 is the 470 ohm plus trimmer total, 820 shipped):

| Rm1 (ohm) | temp (C) | Iq (mA) | V across (V) | midpoint (V) |
|---|---|---|---|---|
| 560 | 25 | 0.9 | 1.117 | 5.93 |
| 560 | 70 | 3.0 | 1.003 | 5.94 |
| 680 | 25 | 4.3 | 1.205 | 5.93 |
| 680 | 70 | 10.0 | 1.082 | 5.94 |
| 820 | 25 | 21.2 | 1.306 | 5.93 |
| 820 | 70 | 30.6 | 1.172 | 5.94 |
| 1000 | 25 | 74.4 | 1.432 | 5.93 |
| 1000 | 70 | 79.3 | 1.285 | 5.94 |
| 1200 | 25 | 157.0 | 1.565 | 5.93 |
| 1200 | 70 | 150.2 | 1.404 | 5.94 |

| Rm1 (ohm) | load | P out (mW) | THD % at 50 mW |
|---|---|---|---|
| 560 | 4 | 33 | 1.70 |
| 560 | 8 | 20 | 1.43 |
| 680 | 4 | 34 | 0.85 |
| 680 | 8 | 21 | 0.59 |
| 820 | 4 | 36 | 0.49 |
| 820 | 8 | 22 | 0.21 |
| 1000 | 4 | 37 | 0.18 |
| 1000 | 8 | 22 | 0.04 |
| 1200 | 4 | 37 | 0.04 |
| 1200 | 8 | 22 | 0.01 |

## 2.4 Output power vs load and output-device hFE (ampB4.cir, Rm1 820, 2.5k source)

| output hFE | load (ohm) | Vin pk (mV) | P out (W) | I supply (mA) | P Q4 (W) | THD % |
|---|---|---|---|---|---|---|
| 40 | 4 | 100 | 0.22 | 117 | 0.54 | 3.73 |
| 40 | 4 | 200 | 0.42 | 164 | 0.62 | 23.37 |
| 40 | 4 | 300 | 0.52 | 187 | 0.62 | 30.38 |
| 40 | 8 | 100 | 0.18 | 80 | 0.34 | 0.69 |
| 40 | 8 | 200 | 0.56 | 134 | 0.43 | 10.73 |
| 40 | 8 | 300 | 0.79 | 162 | 0.39 | 21.36 |
| 40 | 10 | 100 | 0.16 | 70 | 0.29 | 0.44 |
| 40 | 10 | 200 | 0.57 | 121 | 0.37 | 5.29 |
| 40 | 10 | 300 | 0.81 | 147 | 0.34 | 17.53 |
| 120 | 4 | 100 | 0.39 | 153 | 0.65 | 0.69 |
| 120 | 4 | 200 | 1.28 | 269 | 0.82 | 8.23 |
| 120 | 4 | 300 | 1.71 | 317 | 0.75 | 20.04 |
| 120 | 8 | 100 | 0.24 | 92 | 0.37 | 0.16 |
| 120 | 8 | 200 | 0.95 | 169 | 0.46 | 0.52 |
| 120 | 8 | 300 | 1.70 | 223 | 0.48 | 10.61 |
| 120 | 10 | 100 | 0.20 | 78 | 0.31 | 0.10 |
| 120 | 10 | 200 | 0.80 | 142 | 0.37 | 0.32 |
| 120 | 10 | 300 | 1.45 | 187 | 0.38 | 10.48 |
| 250 | 4 | 100 | 0.46 | 166 | 0.69 | 0.26 |
| 250 | 4 | 200 | 1.77 | 314 | 0.85 | 0.99 |
| 250 | 4 | 300 | 2.74 | 396 | 0.88 | 13.42 |
| 250 | 8 | 100 | 0.26 | 96 | 0.38 | 0.05 |
| 250 | 8 | 200 | 1.05 | 178 | 0.45 | 0.19 |
| 250 | 8 | 300 | 1.83 | 232 | 0.46 | 11.20 |
| 250 | 10 | 100 | 0.22 | 81 | 0.31 | 0.03 |
| 250 | 10 | 200 | 0.87 | 147 | 0.37 | 0.11 |
| 250 | 10 | 300 | 1.52 | 192 | 0.37 | 10.93 |

At 9 V (ampB2.cir, hFE 120, 4 ohm): 100 mVpk -> 0.33 W at 1.7% THD; 200 mVpk -> 0.84 W at 14.0% THD; 300 mVpk -> 1.00 W at 24.5% THD.

## 2.5 Power supply (psu.cir)

50 Hz, 0.8 ohm winding resistance, 0.02 ohm fuse, 2 x 2200 uF, 13 V zener, BC547 + TIP41C, 0.33 ohm clamp.

| VAC | I load (A) | raw trough (V) | V out (V) | ripple (mV) | I secondary (A rms) | P pass (W) |
|---|---|---|---|---|---|---|
| 12 | 0.10 | 14.7 | 11.62 | 2 | 0.27 | 0.3 |
| 12 | 0.38 | 13.4 | 11.41 | 8 | 0.78 | 0.8 |
| 12 | 0.73 | 12.2 | 10.96 | 22 | 1.33 | 1.1 |
| 12 | 1.01 | 11.3 | 10.13 | 21 | 1.75 | 1.6 |
| 15 | 0.10 | 18.8 | 11.67 | 1 | 0.29 | 0.8 |
| 15 | 0.38 | 17.4 | 11.48 | 5 | 0.83 | 2.4 |
| 15 | 0.75 | 16.1 | 11.29 | 10 | 1.43 | 3.9 |
| 15 | 1.11 | 15.0 | 11.12 | 16 | 1.97 | 4.8 |

Short circuit (0.5 ohm load, 15 VAC): 2.14 A, 1.07 V out, 25 W in the pass transistor until the fuse opens.

| DC-in only, load (ohm) | V out | raw rail | pass transistor B-E reverse (V) | driver B-E (V) |
|---|---|---|---|---|
| 120 | 11.71 | 11.25 | 0.65 | -0.19 |
| 15 | 11.60 | 11.14 | 0.65 | -0.19 |

Both sources (15 VAC and 12 V DC, 15 ohm load): V out 11.62 V, 0.62 A of the load comes from the DC input.

## 2.6 The release 1 channel as drawn (amp_final.cir)

Operating point: output 5.93 V, output idle current 21.6 mA. 0.2 Vpk in, 8 ohm: 0.93 W at 0.76 percent THD.

## 2.7 Release 2 front end: PNP pair, current-mirror load, current-source tail, NPN VAS (ampC.cir)

Same output stage, bias spreader and feedback network as release 1. The input pair is now PNP (BC557) with an NPN
current-mirror load (100 ohm emitters), the tail is a BC557 current source referenced to a red LED (about 1 mA), the
VAS is an NPN with a 47 ohm emitter resistor and a bootstrapped 2 x 270 ohm load from +12 V, and the compensation is
220 pF Miller plus 47 pF across the 22k feedback resistor.

| BC557 hFE | output hFE | midpoint (V) | supply (mA) | output Iq (mA) | VAS (mA) | tail (mA) |
|---|---|---|---|---|---|---|
| 110 | 40 | 6.25 | 32.5 | 20.2 | 9.5 | 1.03 |
| 110 | 250 | 6.25 | 33.8 | 21.1 | 9.5 | 1.03 |
| 450 | 40 | 6.08 | 33.5 | 20.9 | 9.8 | 1.03 |
| 450 | 250 | 6.08 | 34.9 | 21.9 | 9.8 | 1.03 |

| Rm1 + RV (ohm) | Iq (mA) |
|---|---|
| 680 | 4.5 |
| 820 | 21.5 |
| 1000 | 74.8 |

| source (ohm) | gain at 1 kHz | Zin (k) |
|---|---|---|
| 1 | 22.8 | 46.2 |
| 2500 | 21.6 | 46.2 |
| 5000 | 20.6 | 46.2 |

Bandwidth (8 ohm, 2.5k source): -3 dB at 20 Hz and 119 kHz.

| load (ohm) | Vin pk (mV) | P out (W) | THD % (BD139 / BD140 hFE 120 / 120) |
|---|---|---|---|
| 4 | 30 | 0.052 | 0.013 |
| 4 | 100 | 0.573 | 0.072 |
| 4 | 200 | 1.571 | 15.284 |
| 4 | 300 | 1.833 | 25.391 |
| 8 | 30 | 0.026 | 0.004 |
| 8 | 100 | 0.292 | 0.019 |
| 8 | 200 | 1.159 | 0.837 |
| 8 | 300 | 1.843 | 13.570 |

For comparison the release 1 channel gave 0.03 percent at 50 mW and 0.18 percent at 50 mW into 4 ohm, 0.76 percent at 0.93 W into 8 ohm.

Compensation sweep (ampC_comp runs, 1 kHz square wave +-0.1 V, 100 nF across 8 ohm): 100p / no lead cap: 34 percent overshoot and 1.3 dB peaking at 1 MHz; 220p / 22p: 12.7 percent; 220p / 47p: 5.7 percent, no peaking, -3 dB 119 kHz (chosen); 330p / 47p: 5.6 percent, 107 kHz; 470p / 100p: 5.7 percent, 55 kHz. With the chosen values: 5.6 percent with no capacitance, 14.4 percent with 470 nF, 16.0 percent with 2.2 uF across the speaker (release 1: 6.9 percent at 470 nF). Stable in every case.

Temperature (ampC_misc): output Iq 21.1 mA at 25 C, 30.3 mA at 70 C with the spreader held at 25 C; midpoint 6.12 to 6.14 V. BC547 hFE 110 to 450: midpoint 6.12 to 6.14 V.

## 2.8 The release 2 channel as drawn (amp2_final.cir, default models BD139 hFE 120 / BD140 hFE 100)

Operating point: output 6.12 V, Q1 base 6.17 V, LED reference 10.12 V, output Iq 21.5 mA, VAS 9.7 mA, tail 1.03 mA, supply 34.3 mA per channel. Gain 21.6, Zin 46k; VU header 1.00 V per volt of speaker signal (open).

| load (ohm) | Vin pk (mV) | P out (W) | THD % |
|---|---|---|---|
| 8 | 100 | 0.29 | 0.045 |
| 8 | 150 | 0.66 | 0.063 |

The 0.045 percent at 0.29 W (vs 0.019 percent in 2.7) is the BD139 / BD140 hFE mismatch of the default models; matched outputs give the 2.7 figure. The KiCad netlist of both channels was checked against this deck (same net partition) with kicad/netcheck.py.

## 2.9 Release 2 power supply, closed loop (psu2.cir)

Bridge and reservoir as before. The pass pair (BC547 + TIP41C) is driven from the raw rail through 2.2k; a BC547 error
amplifier compares a divider of VOUT (8.2k + 2k trimmer over 10k) with a 5.6 V zener fed from the regulated output and
pulls the driver base down; 47 nF across the error amplifier sets the loop speed, 100 nF from VOUT to the divider feeds
fast steps through. The clamp (0.33 ohm, Q3 on the driver base) and the DC-in path are unchanged.

| VAC | I load (A) | raw trough (V) | V out (V) | ripple (mV) | I secondary (A rms) | P pass (W) |
|---|---|---|---|---|---|---|
| 12 | 0.10 | 14.6 | 11.96 | 8 | 0.28 | 0.3 |
| 12 | 0.39 | 13.3 | 11.82 | 163 | 0.82 | 0.7 |
| 12 | 0.73 | 12.2 | 10.90 | 976 | 1.34 | 1.2 |
| 12 | 1.01 | 11.4 | 10.06 | 1249 | 1.74 | 1.7 |
| 15 | 0.10 | 18.8 | 12.10 | 4 | 0.31 | 0.8 |
| 15 | 0.40 | 17.3 | 12.06 | 15 | 0.87 | 2.3 |
| 15 | 0.80 | 15.9 | 12.01 | 34 | 1.51 | 3.5 |
| 15 | 1.20 | 14.7 | 11.96 | 70 | 2.10 | 3.9 |

Load step 0.1 A to 1 A to 0.1 A (15 VAC): 12.10 V before, 12.01 V during, dip to 11.96 V, overshoot to 12.14 V, no ringing (release 1 dropped 0.4 V). Compensation sweep (psu2_step runs, 0.2 ohm ESR on the output capacitor): 22n, 47n and 100n all settle without ringing; with the slowest transistors (BC547 hFE 110, TIP41C hFE 25) the 1 A ripple is 90 mV, with typical parts 40 mV; 1 ohm ESR costs a 0.8 V dip (ESR times the step), nothing else.

Short circuit (0.5 ohm load, 15 VAC): 2.07 A, 1.03 V out, 25 W in the pass transistor until the fuse opens.

| DC-in only, load (ohm) | V out | raw rail | pass transistor B-E reverse (V) | driver B-E (V) |
|---|---|---|---|---|
| 120 | 11.71 | 11.24 | 0.37 | 0.11 |
| 15 | 11.60 | 11.14 | 0.36 | 0.09 |

Both sources (15 VAC and 12 V DC, 15 ohm load): V out 12.01 V, 0.00 mA of the load comes from the DC input (the regulator at 12.0 V sits just above the 11.6 V the diode path can supply).

Set point (psu2_dc.cir): with the trimmer at 900 ohm the output is 12.0 V; line regulation 11.9 to 12.0 V for a raw rail of 13 to 19 V. With a 12 VAC transformer the raw rail is only 1.3 V above the output at 0.4 A, so set 11.5 V there.
