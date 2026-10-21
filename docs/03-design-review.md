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
| PCB DRC, single-sided | kicad-cli | 62 errors (open) | 0 errors | 0 errors | |
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
   one copper layer; 22 wire links and 62 DRC errors remain. Build the amp on the 2-layer panel, or finish
   the single-sided board by hand.
8. freerouting 1.9 once wrote the same track into two nets through a tight corridor between a TO-220 and a
   mounting hole; the layout was changed to remove the corridor. Always read "Items shorting two nets" in a
   DRC report produced from an autorouter.

## 3.3 Risks before the first build

| Risk | Likelihood | What to do |
|---|---|---|
| Output transistor substitute with a different pinout fitted without moving the bridges | medium | the 3x3 block silkscreen says E C B / 1 2 3; check with a DMM before power |
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
- Pot direction, Mouser part numbers and electrolytic case sizes. (Terminal-block orientation was wrong in the first
  layout, caught on the 3D render and fixed: wire entry now faces the board edge on all seven terminals.)
- Figures on the notes page were checked by netlist, not visually proofread.
- CircuitJS links were generated from the decks and machine-checked (`connectivity.py --deck`, 0 findings) but not
  opened in a browser by the author. Open them yourself:
  - [Amp channel in CircuitJS](https://www.falstad.com/circuit/circuitjs.html?cct=$%201%200.000005%2010.20027730826997%2050%205%2050%0Av%2064%20480%2064%2064%200%200%2040%2012%200%200%200.5%0Ag%2064%20480%2064%20512%200%0Aw%2064%2064%20208%2064%200%0Aw%20208%2064%20288%2064%200%0Aw%20288%2064%20352%2064%200%0Aw%20352%2064%20528%2064%200%0Aw%20528%2064%20816%2064%200%0Av%20128%20480%20128%20368%200%201%201000%200.1%200%200%200.5%0Ag%20128%20480%20128%20512%200%0Ar%20128%20368%20192%20368%200%202500%0Ac%20192%20368%20256%20368%200%202.2e-06%200%200%0Ar%20208%2064%20208%20176%200%2047000%0Ar%20208%20176%20208%20480%200%2047000%0Ag%20208%20480%20208%20512%200%0Ac%20240%20176%20240%20480%200%204.7e-05%200%200%0Ag%20240%20480%20240%20512%200%0Aw%20208%20176%20240%20176%200%0Aw%20240%20176%20272%20176%200%0Ar%20272%20176%20272%20368%200%2047000%0Aw%20256%20368%20272%20368%200%0Aw%20272%20368%20304%20368%200%0At%20304%20368%20352%20368%200%201%200%200%20290%0At%20496%20368%20448%20368%200%201%200%200%20290%0Aw%20352%20384%20352%20416%200%0Aw%20352%20416%20400%20416%200%0Aw%20400%20416%20448%20416%200%0Aw%20448%20384%20448%20416%200%0Ar%20400%20416%20400%20480%200%2010000%0Ag%20400%20480%20400%20512%200%0Aw%20448%20352%20448%20320%200%0Aw%20448%20320%20528%20320%200%0Aw%20528%20320%20528%2064%200%0Ar%20288%2064%20288%20160%200%204700%0Aw%20288%20160%20288%20192%200%0Aw%20288%20192%20288%20240%200%0Aw%20288%20240%20352%20240%200%0Aw%20352%20240%20352%20352%200%0Aw%20496%20368%20528%20368%200%0Aw%20528%20368%20544%20368%200%0Ar%20544%20368%20608%20368%200%2022000%0A207%20608%20368%20640%20368%204%20out%0Ar%20528%20368%20528%20416%200%201000%0Ac%20528%20416%20528%20480%200%200.00022%200%200%0Ag%20528%20480%20528%20512%200%0At%20320%20192%20368%20192%200%20-1%200%200%20250%0Aw%20288%20192%20320%20192%200%0Ar%20352%2064%20352%20128%200%2047%0Aw%20352%20128%20368%20128%200%0Aw%20368%20128%20368%20176%200%0Aw%20368%20208%20368%20256%200%0Aw%20368%20256%20400%20256%200%0Aw%20400%20256%20608%20256%200%0Aw%20608%20256%20624%20256%200%0Aw%20624%20256%20736%20256%200%0Ac%20400%20192%20400%20256%200%201e-10%200%200%0A207%20400%20192%20432%20192%204%20c1%0A207%20288%20160%20256%20160%204%20c1%0Ar%20624%20256%20624%20304%200%20820%0At%20560%20304%20608%20304%200%201%200%200%20290%0Aw%20608%20288%20608%20256%200%0Aw%20560%20304%20560%20336%200%0Aw%20560%20336%20624%20336%200%0Aw%20624%20304%20624%20336%200%0Ar%20624%20336%20624%20400%200%201000%0Aw%20608%20320%20608%20400%200%0Aw%20608%20400%20624%20400%200%0Aw%20624%20400%20688%20400%200%0Aw%20688%20400%20736%20400%200%0Ar%20688%20400%20688%20448%200%20270%0Ar%20688%20448%20688%20480%200%20270%0Ag%20688%20480%20688%20512%200%0Ac%20688%20448%20752%20448%200%200.0001%200%200%0A207%20752%20448%20784%20448%204%20out%0At%20736%20256%20784%20256%200%201%200%200%20120%0Aw%20784%20240%20816%20240%200%0Aw%20816%20240%20816%2064%200%0At%20736%20400%20784%20400%200%20-1%200%200%20100%0Ag%20784%20416%20784%20448%200%0Ar%20784%20272%20784%20320%200%200.47%0Ar%20784%20384%20784%20320%200%200.47%0Aw%20784%20320%20848%20320%200%0Aw%20848%20320%20880%20320%200%0Aw%20880%20320%20912%20320%200%0A207%20848%20320%20848%20288%204%20out%0Ar%20880%20320%20880%20400%200%2010%0Ac%20880%20400%20880%20480%200%201e-07%200%200%0Ag%20880%20480%20880%20512%200%0Ac%20912%20320%20976%20320%200%200.001%200%200%0Ar%20976%20320%20976%20480%200%208%0Ag%20976%20480%20976%20512%200%0Ax%2064%20544%2064%20544%204%2016%20Stereo%20amp%20channel%20%28ngspice%20amp_final.cir%29:%20diff%20pair,%20VAS,%20Vbe%20multiplier,%20BD139/BD140.%2012%20V,%20Iq%2021%20mA,%201%20W%20into%208R%20at%200.5%25%20THD%0A)
  - [Power supply in CircuitJS](https://www.falstad.com/circuit/circuitjs.html?cct=$%201%200.00002%2010.20027730826997%2050%205%2050%0Av%2064%20352%2064%20160%200%201%2050%2021.2%200%200%200.5%0Ar%2064%20160%20144%20160%200%200.02%0Ar%2064%20352%20144%20352%200%200.8%0Aw%20144%20160%20160%20160%200%0Aw%20144%20352%20240%20352%200%0Ad%20160%20160%20160%2096%200%20default%0Ad%20160%20256%20160%20160%200%20default%0Ag%20160%20256%20160%20288%200%0Ad%20240%20352%20240%2096%200%20default%0Ad%20240%20416%20240%20352%200%20default%0Ag%20240%20416%20240%20448%200%0Aw%20160%2096%20240%2096%200%0Aw%20240%2096%20320%2096%200%0Aw%20320%2096%20368%2096%200%0Aw%20368%2096%20416%2096%200%0Aw%20416%2096%20480%2096%200%0Aw%20480%2096%20624%2096%200%0Aw%20624%2096%20720%2096%200%0Aw%20720%2096%20768%2096%200%0Ac%20320%2096%20320%20416%200%200.0022%200%200%0Ag%20320%20416%20320%20448%200%0Ac%20368%2096%20368%20416%200%200.0022%200%200%0Ag%20368%20416%20368%20448%200%0Ar%20416%2096%20416%20416%200%204700%0Ag%20416%20416%20416%20448%200%0Ar%20480%2096%20480%20192%200%201000%0Az%20480%20320%20480%20192%202%20default-zener%0Ag%20480%20320%20480%20352%200%0Ac%20528%20192%20528%20416%200%200.0001%200%200%0Ag%20528%20416%20528%20448%200%0Aw%20480%20192%20528%20192%200%0Aw%20528%20192%20576%20192%200%0A207%20480%20192%20448%20224%204%20vz%0At%20576%20192%20624%20192%200%201%200%200%20290%0Aw%20624%20176%20624%2096%200%0Aw%20624%20208%20624%20256%200%0Aw%20624%20256%20672%20256%200%0At%20672%20256%20720%20256%200%201%200%200%2060%0Aw%20720%20240%20720%2096%200%0Ar%20720%20272%20720%20352%200%200.33%0Aw%20720%20272%20768%20272%200%0At%20768%20272%20816%20272%200%201%200%200%20290%0A207%20816%20256%20848%20240%204%20vz%0Aw%20816%20288%20816%20352%200%0Aw%20816%20352%20768%20352%200%0Aw%20768%20352%20720%20352%200%0Ad%20768%20352%20768%2096%200%20default%0Aw%20816%20352%20864%20352%200%0Aw%20864%20352%20912%20352%200%0Aw%20912%20352%20960%20352%200%0Aw%20960%20352%201056%20352%200%0Ac%20864%20352%20864%20416%200%200.00022%200%200%0Ag%20864%20416%20864%20448%200%0Ar%20912%20352%20912%20384%200%201000%0A162%20912%20384%20912%20416%202%20default-led%201%200%200%200.01%0Ag%20912%20416%20912%20448%200%0Ad%201040%20352%20960%20352%200%20default%0As%201072%20352%201040%20352%200%201%20false%0Av%201072%20416%201072%20352%200%200%2040%2012%200%200%200.5%0Ag%201072%20416%201072%20448%200%0Ar%201056%20352%201056%20416%200%2015%0Ag%201056%20416%201056%20448%200%0Ax%2064%20480%2064%20480%204%2016%20Discrete%2012%20V%20PSU%20%28ngspice%20psu.cir%29.%20Zener%20drawn%20with%20the%20default%205.6%20V%20model:%20double-click%20it%20and%20set%2013%20V.%20Close%20the%20switch%20to%20test%20the%20DC-in%20path.%0A) (set the zener to 13 V after loading; close the switch to test the DC input)
  - Fallback: File > Import From Text with `docs/circuitjs/stereo-amp-channel.txt` or `stereo-amp-psu.txt`.
