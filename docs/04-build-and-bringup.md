# 4. Build and bring-up (release 2)

## 4.0 Build only what you need

The boards are independent. The minimum listening setup is the amp alone: 12 V DC from any 1 A adapter
into "12V IN" (centre + to pin 1, the square pad), a phone or PC into the "IN L G R" header (tip = L, ring = R,
sleeve = G of a 3.5 mm plug), speakers on the terminals. The source's volume control sets the level; a phone
at full volume (about 1 Vrms) overdrives the amp (full power at 0.14 Vrms), so start low. Add the volume
board when you want a knob, the PSU when you want to run from a transformer or want the clamp and the
front-panel LED, and the headphone board when you want a jack. The VU header on the amp does nothing until a
meter hangs on it. Sections 4.3 (PSU alone) and 4.4 (amp) still apply in whatever order you build.

## 4.1 Before soldering

1. Read [ORDER_GUIDE.md](../ORDER_GUIDE.md) for substitutes, matching and tolerances.
2. Measure the four output transistors' hFE (DMM hFE socket). Pair the closest NPN and PNP in each channel;
   what matters most is that both channels get the same part numbers and grade.
3. Pick the two PNP input pairs (Q1/Q2) and the two NPN mirror pairs (Q7/Q8) from one strip each; a DMM hFE
   match within 10 percent is plenty.
4. Decide where the power LED lives: PSU (D7) or front panel (volume board D1 via PSU J5). Fit one.
5. Decide the output transistor type and set the 3x3 jumper blocks before fitting anything near them
   (BD139/BD140: nothing to do, the diagonal is pre-bridged).
6. Headphone board: decide 120 ohm (default), 330 ohm (sensitive in-ear phones) or bridged JP1/JP2 (direct).

## 4.2 Assembly order (per board)

1. Solder jumpers first if any need changing (amp pinout blocks, headphone DIRECT jumpers).
2. Low parts: resistors, diodes (band = cathode = the pad with the bar on the silkscreen), test point loops.
3. Small signal transistors: flat face matches the silkscreen D-shape. 2N3904/2N3906 go in turned round.
   The amp has nine per channel now: Q1, Q2, Q9 are PNP (BC557), Q3, Q6, Q7, Q8 are NPN (BC547). Do not mix
   them up; the silkscreen value says which.
4. The tail LED D10001 / D20001: RED, flat side (cathode) to the pad with the bar.
5. Trimmers, ceramic capacitors (C0G for the 220 pF and 47 pF), headers, screw terminals, the slide switch.
6. Electrolytics: the long lead is + and goes to the pad marked +. On the amp every + faces the higher
   voltage: Cin (2.2 uF) + towards the transistor side, Cboot + towards the bootstrap resistors, output caps +
   towards the amp.
7. Output transistors and the TIP41C last, with heatsinks fitted before soldering so the legs are not stressed.
8. Single-sided boards: solder the JLn wire links (bare wire between the two holes) before the parts that
   cover them.

## 4.3 First power-up, PSU alone

Set RV1 to mid travel. Use a bench supply if you have one: feed 12 V DC into "DC IN" first (no transformer).
The LED should light and TP3 should read 11.7 V (the diode path; the regulator is idle). Then connect the
transformer and remove the DC: TP1 (VRAW) 14 to 19 V, TP2 (VZ) 5.6 V, TP5 (FB) 6.2 to 6.4 V, TP3 (VOUT) 11.4 to
12.7 V depending on the trimmer. Set TP3 to 12.0 V (11.5 V with a 12 VAC transformer). Load the output with a
22 ohm 10 W resistor (0.5 A) for a minute: TP3 should move by less than 0.1 V from 15 VAC and stay above 11.5 V
from 12 VAC. Do not short the output on purpose: the clamp limits to 2.1 A, but the secondary then draws
about 3.7 A and the 1 A T fuse opens. The clamp's job is to keep the TIP41C alive until the fuse does. Keep a
spare fuse.

## 4.4 First power-up, amp

1. Both trimmers fully anticlockwise (minimum bias).
2. No speakers, no input. Power from the PSU (or a bench supply at 12 V, current limit 300 mA).
3. TP1 (+12V) 11.5 to 12 V. Per channel: TPx4 (LED) 10.0 to 10.3 V and the LED glowing faintly, TPx2 (OUT)
   5.8 to 6.4 V, TPx1 (B1) within 0.1 V of TPx2. If TPx4 is near 12 V the LED is backwards or missing; if OUT is
   near 0 V or near 12 V, check the output transistor pinout / jumper block of that channel first, then Q3
   and the mirror pair.
4. Set bias: DMM in mV between TPx3 (E4) and TPx2 (OUT). Turn the trimmer clockwise slowly until it reads 7 to
   10 mV (15 to 20 mA through the output pair). Let it warm for 10 minutes and re-check; it should rise by no
   more than 2 to 3 mV. Repeat for the other channel.
5. Idle current from the supply: 65 to 75 mA for both channels (about 34 mA each). More than 120 mA means
   a bias problem.
6. Connect speakers and a source. Clockwise on the pot = louder; if backwards, swap the two outer wires of
   that gang on the volume board.

## 4.5 Headphone board

Wire the amp's speaker terminals to "FROM AMP" (L, G, R), the speakers to the two terminals. With the slider
towards pins 1 / 6 the speakers play; towards pins 3 / 4 the speakers go silent and the jack is live. TP2 / TP3
read the jack signal; with nothing plugged in they read the full speaker voltage (there is no load). If a
substitute switch has a different numbering, find the two commons with a DMM (each common connects to one
of its neighbours in each slider position) and wire the amp to those.

## 4.6 What the test points tell you

| Test point | Expect | If not |
|---|---|---|
| PSU TP1 VRAW | 14 to 19 V | transformer, fuse, bridge diode orientation |
| PSU TP2 VZ | 5.6 V | R2 open, zener backwards (reads 0.7 V) or shorted; 0 V with VOUT at 0 V means the loop never started: check R7 and Q1/Q2 pinouts |
| PSU TP5 FB | 6.2 to 6.4 V | divider (R5, RV1, R6) or Q4 pinout |
| PSU TP3 VOUT | 11.4 to 12.7 V, trimmer sets | at the raw rail: Q4 missing or backwards; low: clamp transistor Q3 fitted backwards or RV1 at an end |
| Amp TP1 +12V | 11.5 to 12 V | wiring, reversed DC |
| Amp TPx4 LED | 10.0 to 10.3 V | LED backwards (12 V), wrong colour (9 V or lower), R5 open |
| Amp TPx1 B1 | 6.1 V | R1/R2 divider, C2 shorted |
| Amp TPx2 OUT | 6.1 V | output pair pinout / jumper block, Q3, mirror pair, Q6 shorted (OUT high) or open (OUT low) |
| TPx3 minus TPx2 | 7 to 10 mV after adjustment | trimmer at an end stop, Q6 pinout |
| Headphone TP2 / TP3 | the speaker signal when switched to phones | switch pin numbering, R1/R2 |

## 4.7 Troubleshooting sounds

- Buzz that changes with volume: input ground; check the GND pin of the L-G-R headers.
- Hum independent of volume: supply ripple; measure TP1 ripple with the scope, add transformer current.
- Distorted at any level: bias not set (crossover) or one output transistor not conducting.
- One channel quiet: compare TPx2 and TPx4 of both channels, then the pot gang.
- Gets hot at idle: bias too high; check Q6 is next to the outputs and the trimmer setting.
- Headphones very loud or very quiet: JP1/JP2 bridged by mistake, or 330 ohm fitted with low-impedance phones.
- Faint hiss at full volume with no source: normal (simulated 100 dB below 1 W); if loud, check the input
  cable shield and the 47k divider.
