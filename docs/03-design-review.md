# 3. Design review (release 1.2, unbuilt prototype)

Reviewer: the design was generated and checked by machine; this is the record of every check that ran, what
it found, and what it cannot tell you. Read it before ordering. The release 1.1 review is kept below (3.5) for
the checks that have not been re-run.

## 3.1 Checks that ran for release 1.2

| Check | Tool | Amp (wide / compact) | PSU | Volume | Headphone | Panel |
|---|---|---|---|---|---|---|
| Schematic ERC | kicad-cli 9.0.8 | 0 errors | 0 errors | 0 errors | 0 errors | |
| Netlist vs simulated deck (same net partition) | kicad/netcheck.py | OK, both channels vs amp2_final.cir | OK vs psu2.cir | by inspection (7 nets) | by inspection (11 nets, listed in the build log) | |
| PCB DRC with schematic parity, 2-layer | kicad-cli | 0 errors / 0 errors | 0 errors | 0 errors | 0 errors | 0 errors |
| PCB DRC, single-sided | kicad-cli | 15 errors (24 wire links; open) | 0 errors, 1 link | 0 errors, 1 link | 0 errors, 2 links | |
| Autorouter shorts ("Items shorting two nets") | read in every DRC JSON | none | none | none | none (one during development, fixed in auto_links.py) | none |
| Circuit simulation | ngspice 42, 5 new decks | ampC, ampC_sq, ampC_misc, amp2_final | psu2, psu2_dc, psu2_step | | | |

## 3.2 Findings from simulation (release 2)

1. CORRECTED, front end: the first mirror-loaded deck put the NPN VAS collector on the wrong node (the spreader
   top instead of the PNP base) and the output stage sat at zero bias. Fixed before any board was drawn; the
   netlist check would have caught the drawn version.
2. CORRECTED, compensation: the mirror load raises the loop gain so much that the release 1 compensation (100 pF
   Miller, nothing else) gave 34 percent square-wave overshoot and 1.3 dB of peaking at 1 MHz. Sixteen
   combinations were run; 220 pF Miller plus 47 pF across the feedback resistor gives 5.7 percent overshoot,
   no peaking and 120 kHz bandwidth. Larger Miller values do not reduce the capacitive-load overshoot (14 percent
   at 470 nF for 220 to 470 pF), so the Zobel network stays as the capacitive-load defence.
3. CORRECTED, PSU set point: the first closed-loop deck had the trimmer in the lower leg of the divider and
   settled at 11.0 V; the trimmer now sits in the upper leg (8.2k + 2k over 10k) and the range is 11.4 to 12.7 V.
4. CORRECTED, PSU drive: with 4.7k from the raw rail the driver base starved with low-gain transistors (BC547
   hFE 110 and TIP41C hFE 25 gave 11.8 V and 280 mV ripple at 1 A). 2.2k holds 12.0 V with 90 mV ripple in that
   corner. The error amplifier now sinks up to 2.6 mA at light load: fine for a BC547.
5. LIMIT, 12 VAC transformers: the 12.0 V set point leaves 1.3 V of headroom at 0.4 A from 12 VAC; above that
   the output follows the raw rail (10.1 V at 1 A). Set 11.5 V with a 12 VAC transformer; use 15 VAC for full
   power.
6. LIMIT, output hFE mismatch: the as-drawn deck with the generic BD139 (hFE 120) and BD140 (hFE 100) models
   gives 0.045 percent at 0.29 W into 8 ohm; with matched outputs it is 0.019 percent. Buy the -16 grade of both.
7. CONFIRMED: midpoint 6.08 to 6.25 V over every hFE corner, idle 20 to 22 mA, tail 1.03 mA, gain 22.8, Zin 46k,
   -3 dB 20 Hz and 119 kHz, clipping at 1.2 W into 8 ohm and 1.5 W into 4 ohm. PSU: 2.07 A clamp, 11.7 V from
   the DC input alone, no interaction when both sources are connected.
8. NOT SIMULATED: the headphone board (passive, resistors and a switch) and the VU tap (1k into an open header).

## 3.3 Findings from layout (release 2)

9. The extra front-end parts made the wide amp 134 x 85 mm (was 71) and the compact amp 100 x 98 mm (was 85);
   the compact board still fits the 100 x 100 mm fab tier. The panel grew to 155 x 155 mm.
10. freerouting left one or two connections open on three boards no matter how many passes it ran. The causes
    were placement, not router settings: a pocket in the top-left corner of each channel that only the +12 V
    net needed to enter (fixed with a 2 mm corridor along each channel's left edge), the VU resistor far from
    its header on the compact board (moved next to the header), and a slide switch too close to the board edge
    (rotated). `build.sh` now runs a second routing pass from the routed board when the first leaves gaps.
11. The single-sided amp improved from 62 to 15 DRC errors (24 wire links) but is still not clean; same advice
    as before, finish it by hand or build on the 2-layer panel.
12. The jack on the headphone board hangs 1.3 mm over the board edge (its nose); on the panel it faces the
    volume board across the 2 mm gap, so the volume board sits below it and the pot shaft hangs off the rail.

## 3.4 Risks before the first build

| Risk | Likelihood | What to do |
|---|---|---|
| Output transistor substitute with a different pinout fitted without moving the bridges | medium | the 3x3 block silkscreen says E C B / 1 2 3; check with a DMM before power |
| Wrong LED colour in the tail reference (green or blue doubles the tail current) | medium | red only; TPx4 should read 10.0 to 10.3 V |
| Slide switch with a different pin numbering | low | pins 2 / 5 must be the commons; check with a DMM in both positions before wiring speakers |
| Pot wired backwards (pin 3 convention) | medium | swap the two outer wires |
| Idle current runaway if Q6 is not thermally near the outputs | low | the layout places Q6 beside Q4/Q5; keep it there if you re-place |
| PSU trimmer at the wrong end at first power-up | low | start mid-travel; TP3 then reads about 12 V; never above 12.7 V |
| Reservoir capacitor voltage rating with a 15 VAC transformer (23 V peak at mains +10 percent) | low | fit 35 V parts |
| Oscillation with a very capacitive load | low | Zobel fitted; 2.2 uF simulated stable (16 percent overshoot); Cm 220p and Cf 47p must both be C0G |

## 3.5 Release 1.1 record (checks not re-run)

The check-schematic / check-pcb analyzers, the thermal and EMC pre-compliance runs and the CircuitJS links were
produced for release 1.1 and have not been re-run on the release 2 circuits. Their triage still applies:

- DS-001 / SS-001 (no datasheets directory, no MPNs in the schematic): true, MPNs live in bom_mouser.csv.
- LR-001 on the volume board ("LED without series resistor"): the resistor is R4 on the PSU.
- SJ-DET warnings: the open jumpers of the 3x3 pinout blocks are open on purpose.
- PM-002: the volume pot's courtyard hangs 13 mm over the board edge; that is the shaft.
- EMC GP-001 / RP-001 / VS-001 / VS-002 assume 150 MHz digital signals; not applicable to 20 kHz audio on a
  ground pour.
- EMC IO-001: 100 pF to 1 nF from the amp input header to ground would stop RF pickup on a long cable. Still an
  improvement, not done.
- The CircuitJS links in docs/ and the notes page draw the release 1 channel and supply.

## 3.6 Improvements for release 3

- 1 nF from the amp input header to ground (RF filter).
- A second heatsink bar across the four output transistors, with Q6 clamped under it.
- Hand-route the single-sided amp, or offer a single-sided amp without the jumper blocks.
- Add MPNs to the schematic symbols so the sourcing audit passes.
- Re-run the analyzers and regenerate the CircuitJS links for the release 2 circuits.
- Build one and measure.

## 3.7 Not verified

- Nothing built, measured or listened to.
- Transistor models are generic; no thermal coupling or self-heating; the LED is a generic red diode model.
- Pot direction, slide-switch pin numbering (taken from the C&K drawing), Mouser part numbers and electrolytic
  case sizes.
- Figures are the generated KiCad schematics; they were checked by netlist and looked at once, not proofread
  symbol by symbol.
