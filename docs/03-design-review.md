# 3. Design review (release 1, unbuilt prototype)

Reviewer: the design was generated and checked by machine; this is the record of every check that ran, what
it found, and what it cannot tell you. Read it before ordering.

## 3.1 Checks that ran

| Check | Tool | Amp | PSU | Volume | Panel |
|---|---|---|---|---|---|
| Schematic ERC | kicad-cli 9.0.8 | 0 errors | 0 errors | 0 errors | |
| Netlist vs simulated deck (same net partition) | kicad/netcheck.py | OK, both channels vs amp_final.cir | OK vs psu.cir | by inspection (7 nets) | |
| Schematic analyzer (check-schematic skill) | analyze_schematic.py | 2 errors, 8 warnings, see 3.2 | 2 errors | 3 errors | |
| PCB DRC with schematic parity, 2-layer | kicad-cli | 0 errors | 0 errors | 0 errors | 0 errors |
| PCB DRC, single-sided | kicad-cli | 44 errors (open) | 1 open connection (R1 pin 1 to VRAW, add a wire to TP1) | 0 errors | |
| PCB analyzer (check-pcb skill) | analyze_pcb.py --full | 0 errors, 18 warnings | 0 errors, 8 warnings | 1 error, 1 warning | |
| Schematic-PCB cross analysis | cross_analysis.py | 0 | 1 warning | 0 | |
| Thermal | analyze_thermal.py | no components assessed (no power data in the schematic) | same | same | |
| EMC pre-compliance | analyze_emc.py | 29 errors, 24 warnings | 13 errors, 2 warnings | 5 errors | |
| Circuit simulation | ngspice 42, 9 decks | see 02-simulation-results.md | | | |

## 3.2 Findings and how they were triaged

**Analyzer errors that are not design errors**

- DS-001 and SS-001 on every board: no datasheets directory and no manufacturer part numbers in the
  schematic. True; this is a hobby project, the MPNs live in bom_mouser.csv. Not fixed.
- LR-001 on the volume board: "LED D1 has no series resistor". The resistor is R4 on the PSU, in series
  through the two-wire link. Correct as designed; the analyzer cannot see across boards.
- SJ-DET warnings (amp): open solder jumpers between unnamed nets. These are the 3x3 pinout blocks; open is
  the intended state for the off-diagonal jumpers.
- PM-002 (PCB analyzer): the volume pot's courtyard hangs 13 mm over the board edge. Intended: that is the
  shaft, and the board edge is the panel.
- EMC GP-001 / RP-001 / VS-001 / VS-002: reference-plane gaps, stitching vias, via stitching. The rule set
  assumes 150 MHz digital signals. These boards carry 20 kHz audio and 50 Hz power on a bottom-side ground
  pour; the findings are not applicable (same triage as on the earlier proco-rat audio board).
- EMC IO-001: "no EMC filtering near J1 (amp input) / J4 (PSU DC out)". Partly valid: a 100 pF to 1 nF
  capacitor from the amp input to ground would stop RF pickup on a long cable. Listed as an improvement.
- Schematic parity "extra footprint" x4 per board: the mounting holes. Expected.
- "Silkscreen overlap" warnings (139 on the amp): reference labels touch. Cosmetic.

**Design findings from simulation** (details and tables in 02-simulation-results.md)

1. CORRECTED, bias network: two diodes gave 50 mA idle, one diode plus resistor gave crossover distortion;
   the Vbe multiplier with trimmer is the fix. Iq rises from 21 mA at 25 C to 31 mA at 70 C with the
   multiplier at one temperature; in practice Q6 sits next to the outputs and tracks them.
2. CORRECTED, VAS current: 4 mA (2 x 680 ohm bootstrap load) starved the 4 ohm output (0.3 W); about 10 mA
   (2 x 270 ohm) gives 1.3 W.
3. CORRECTED, PSU clamp placement: on the pass transistor's base it did not limit (3 A); on the driver's base
   it limits at 2.1 A. The 0.47 ohm sense became 0.33 ohm to save 0.5 V at 1 A.
4. LIMIT, output hFE: power tracks the output devices' gain (0.2 W at hFE 40, 1.3 W at 120, 1.8 W at 250 into
   4 ohm). Specify BD139-16 / BD140-16.
5. LIMIT, transformer: 12 VAC regulates to 0.38 A only; 15 VAC at 1.5 A for full stereo power, with a heatsink
   on the TIP41C (4.9 W).
6. CONFIRMED: midpoint 5.93 V (hand 5.95), Zin 43k, -3 dB 34 Hz into 4 ohm (hand 34 Hz), square-wave overshoot
   under 7 percent with 470 nF across the speaker.

**Design findings from layout**

7. The single-sided amp cannot be routed cleanly by freerouting: the 36 interleaved jumper pads block the
   one copper layer; 14 wire links and 44 DRC errors remain. Build the amp on the 2-layer panel, or finish
   the single-sided board by hand.
8. freerouting 1.9 once wrote the same track into two nets through a tight corridor between a TO-220 and a
   mounting hole; the layout was changed to remove the corridor. Always read "Items shorting two nets" in a
   DRC report produced from an autorouter.

## 3.3 Risks before the first build

| Risk | Likelihood | What to do |
|---|---|---|
| Output transistor substitute with a different pinout fitted without moving the bridges | medium | the 3x3 block silkscreen says E C B / 1 2 3; check with a DMM before power |
| Terminal block wire entry facing into the board (orientation inferred from the courtyard) | medium | check the first board; a 180 degree rotation in gen_pcb_*.py fixes it |
| Pot wired backwards (pin 3 convention) | medium | swap the two outer wires |
| Idle current runaway if Q6 is not thermally near the outputs | low | the layout places Q6 beside Q4/Q5; keep it there if you re-place |
| Reservoir capacitor voltage rating with a 15 VAC transformer (23 V peak at mains +10 percent) | low | fit 35 V parts |
| Oscillation with a very capacitive load | low | Zobel fitted; 470 nF simulated stable; Cm must stay 68 to 150 pF C0G |

## 3.4 Improvements for release 2

- 1 nF from the amp input header to ground (RF filter, IO-001).
- A second heatsink bar across the four output transistors, with Q6 clamped under it.
- Replace the open-loop zener follower with a one-transistor feedback regulator for 0.1 V load regulation.
- Hand-route the single-sided amp, or offer a single-sided amp without the jumper blocks (fixed BD139/BD140).
- Space the amp reference designators (silkscreen overlaps).
- Add MPNs to the schematic symbols so the sourcing audit passes.

## 3.5 Not verified

- Nothing built, measured or listened to.
- Transistor models are generic; no thermal coupling or self-heating.
- Terminal orientation, pot direction, Mouser part numbers and electrolytic case sizes.
- Figures on the notes page were checked by netlist, not visually proofread.
- CircuitJS links never opened in a browser.
