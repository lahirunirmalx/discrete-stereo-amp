# 4. Build and bring-up

## 4.0 Build only what you need

The boards are independent. The minimum listening setup is the amp alone: 12 V DC from any 1 A adapter
into "12V IN" (centre + to pin 1, the square pad), a phone or PC into the "IN L G R" header (tip = L, ring = R,
sleeve = G of a 3.5 mm plug), speakers on the terminals. The source's volume control sets the level; a phone
at full volume (about 1 Vrms) overdrives the amp (full power at 0.14 Vrms), so start low. Add the volume
board when you want a knob, and the PSU when you want to run from a transformer or want the clamp and the
front-panel LED. Section 4.3 (PSU alone) and 4.4 (amp) still apply in whatever order you build.

## 4.1 Before soldering

1. Read [ORDER_GUIDE.md](../ORDER_GUIDE.md) for substitutes, matching and tolerances.
2. Measure the four output transistors' hFE (DMM hFE socket). Put the two NPNs with the closest values in
   different channels only if all four are close; otherwise pair the closest NPN and PNP in each channel.
   What matters most is that both channels get the same part numbers and grade.
3. Decide where the power LED lives: PSU (D7) or front panel (volume board D1 via PSU J5). Fit one.
4. Decide the output transistor type and set the 3x3 jumper blocks before fitting anything near them
   (BD139/BD140: nothing to do, the diagonal is pre-bridged).

## 4.2 Assembly order (per board)

1. Solder jumpers first if any need changing (amp only).
2. Low parts: resistors, diodes (band = cathode = the pad with the bar on the silkscreen), test point loops.
3. Small signal transistors: flat face matches the silkscreen D-shape (flat side). 2N3904/2N3906 go in turned round.
4. Trimmers, ceramic capacitors, headers, screw terminals.
5. Electrolytics: the long lead is + and goes to the pad marked +. On the amp every + faces the higher
   voltage: C1 (2.2 uF) + towards the transistor side, output caps + towards the amp.
6. Output transistors and the TIP41C last, with heatsinks fitted before soldering so the legs are not stressed.
7. Single-sided boards: solder the JLn wire links (bare wire between the two holes) before the parts that
   cover them.

## 4.3 First power-up, PSU alone

Use a bench supply if you have one: feed 12 V DC into "DC IN" first (no transformer). The LED should light and
TP3 should read 11.7 V. Then connect the transformer and remove the DC: TP1 (VRAW) 14 to 19 V, TP2 (VZ) 13 V,
TP3 (VOUT) 11.5 to 11.7 V with no load. Load the output with a 22 ohm 10 W resistor (0.5 A) for a minute: VOUT should stay above 11 V from a 12 VAC
transformer and above 11.3 V from 15 VAC. Do not short the output on purpose: the clamp limits to 2.1 A, but
the secondary then draws about 3.7 A and the 1 A T fuse opens. The clamp's job is to keep the TIP41C alive
until the fuse does. Keep a spare fuse.

## 4.4 First power-up, amp

1. Both trimmers fully anticlockwise (minimum bias).
2. No speakers, no input. Power from the PSU (or a bench supply at 12 V, current limit 300 mA).
3. TP1 (+12V) 11.5 to 12 V. Per channel: TPx2 (OUT) 5.6 to 6.2 V, TPx1 (B1) within 0.1 V of TPx2. If OUT is
   near 0 V or near 12 V, check the output transistor pinout / jumper block of that channel first, then Q3.
4. Set bias: DMM in mV between TPx3 (E4) and TPx2 (OUT). Turn the trimmer clockwise slowly until it reads 7 to
   10 mV (15 to 20 mA through the output pair). Let it warm for 10 minutes and re-check; it should rise by no
   more than 2 to 3 mV. Repeat for the other channel.
5. Idle current from the supply: 60 to 70 mA for both channels (about 32 mA each). More than 120 mA means
   a bias problem.
6. Connect speakers and a source. Clockwise on the pot = louder; if backwards, swap the two outer wires of
   that gang on the volume board.

## 4.5 What the test points tell you

| Test point | Expect | If not |
|---|---|---|
| PSU TP1 VRAW | 14 to 19 V | transformer, fuse, bridge diode orientation |
| PSU TP2 VZ | 13 V | R2 open, zener backwards (reads 0.7 V) or shorted |
| PSU TP3 VOUT | 11.5 to 11.7 V | Q1/Q2 pinout, clamp transistor Q3 fitted backwards (output low) |
| Amp TP1 +12V | 11.5 to 12 V | wiring, reversed DC |
| Amp TPx1 B1 | 5.9 V | R1/R2 divider, C2 shorted |
| Amp TPx2 OUT | 5.9 V | output pair pinout / jumper block, Q3, Q6 shorted (OUT high) or open (OUT low) |
| TPx3 minus TPx2 | 7 to 10 mV after adjustment | trimmer at an end stop, Q6 pinout |

## 4.6 Troubleshooting sounds

- Buzz that changes with volume: input ground; check the GND pin of the L-G-R headers.
- Hum independent of volume: supply ripple; measure TP1 ripple with the scope, add transformer current.
- Distorted at any level: bias not set (crossover) or one output transistor not conducting.
- One channel quiet: compare TPx2 of both channels, then the pot gang.
- Gets hot at idle: bias too high; check Q6 is next to the outputs and the trimmer setting.
