# Stereo amp - ordering and build guide

Three boards, generated from `kicad/gen_*.py` (schematics) and `kicad/gen_pcb_*.py` (layouts),
simulated in `sim/` with ngspice. Two fab packages:

| Package | What | Where it goes |
|---|---|---|
| `panel_2layer_gerbers/` + `stereo-panel-gerbers.zip` | ONE 2-layer square panel, 144.2 x 144.2 mm with 3 mm rails, holding the amp (134 x 71) above the PSU (90 x 50) and the volume board (42 x 26) side by side, joined to each other and to the rails by 4 mm mouse-bite tabs | JLCPCB / PCBWay |
| `single_boards_2layer/<board>-2layer-gerbers.zip` | one zip per board: amp 134 x 71 (wide), amp_compact 100 x 85, PSU 90 x 50, volume 42 x 26; 2 layers | JLCPCB / PCBWay, boards ordered separately |
| `single_layer/` | the same three boards as single-sided (copper on the bottom only), scaled up: amp 194 x 100, PSU 117 x 65, volume 42 x 26 mm, with mirrored 1:1 PDFs for toner transfer | home etching (or a 1-layer fab order) |

## Which package to upload

- **Cheapest per board at JLCPCB:** the $2 tier is one design, up to 100 x 100 mm, 5 or 10 pieces, default
  options. PSU, volume and the compact amp (`amp_compact-2layer-gerbers.zip`, 100 x 85 mm) all qualify: three
  $2 orders in one cart. The wide amp (134 x 71 mm) is quoted per area; it exists to match the panel row.
- **One order, fewest steps:** the panel zip. It is above 100 x 100 mm and holds three designs, so it is
  priced per area plus JLCPCB's "different design" fee. Fine for a one-off; more per board than three
  separate $2 orders.
- **Home etching:** `single_layer/` (see below).

## Ordering the panel at JLCPCB or PCBWay

1. Upload `stereo-panel-gerbers.zip`.
2. Layers 2, thickness 1.6 mm, 1 oz copper, any colour, HASL or ENIG.
3. **Panel settings:** this is a multi-design panel delivered as ONE board ("panel by customer").
   JLCPCB: choose "Panel by Customer", set "Different Design" = 3 (both fabs charge a small
   extra for 2+ designs in one panel). Break-off tabs are already in the gerbers.
4. Board size at checkout: 144.2 x 144.2 mm (square, 3 mm rails) (above the cheapest 100 x 100 tier; a 5-piece order
   is typically 10 to 25 USD). If you only need one board type, order `kicad_projects/<board>/`
   separately instead.
5. The solder jumpers on the amp (the 3x3 pinout blocks) are plain SMD pads: no stencil needed.

## Single-sided boards (home etch)

- `single_layer/<board>_1layer_etch_mirrored.pdf` prints 1:1, mirrored, bottom copper only.
- Parts go on the top, SMD twins (1206, SOD-123, SMA) on the copper side.
- Solder jumpers (the pinout blocks) are on the copper side too.
- Where one layer was not enough, the build added wire-link footprints **JLn**: solder a bare
  wire between the two holes. Count per board is printed by `kicad/build.sh <board> --single`
  (PSU: 0, volume: 1, amp: see KNOWN_ISSUES.md).
- **Status of the single-sided amp: NOT clean.** 194 x 100 mm, 22 wire
  links, but DRC still reports 62 errors: some connections still open and auto-placed wire links crowding
  neighbouring copper (the 3x3 jumper blocks' interleaved pads do not suit one-layer routing). Open `kicad_projects/amp/amp_1layer.kicad_pcb` in KiCad,
  run DRC and fix those spots by hand before etching. The single-sided PSU and volume boards are DRC clean.

## Parts (bom_all.csv, 107 parts + 36 solder jumpers)

Every R, small C and diode has a through-hole pattern AND a 1206 / SOD-123 / SMA twin on the same
pads: fit whichever you have. BC547/BC557 positions also take SOT-23 (2-layer board only).
Output devices: BD139/BD140 are the baseline (pins E-C-B). To fit a B-C-E part (TIP41C/TIP42C) or
a TO-92 (BC337/BC327, C-B-E, low power only), move the three solder bridges of that device's 3x3
block: row = device pin 1/2/3, column = where it goes (E, C, B). BD139 = diagonal (pre-bridged).

## Transistor substitutes (at least three per position)

TO-92 pinout, flat face towards you, leads down, left to right: BC546-BC550, BC556-BC560, BC337/BC327 are
C-B-E, which is what every TO-92 position on these boards expects. 2N3904/2N3906 and PN2222A/PN2907A are
E-B-C: they fit only turned 180 degrees (flat face away from the silkscreen outline). Japanese 2SC/2SA
parts (E-C-B) do not fit the TO-92 positions.

| Position | Fitted | Substitutes | Pinout handling |
|---|---|---|---|
| Amp Q1, Q2 (diff pair), Q6 (bias) | BC547B/C | BC548B/C, BC549C, BC550C, BC337-25; 2N3904 / PN2222A | C-B-E direct; 2N3904 turned round |
| Amp Q3 (VAS) | BC557B/C | BC558B/C, BC559C, BC560C, BC327-25; 2N3906 / PN2907A | C-B-E direct; 2N3906 turned round |
| Amp Q4 (NPN output) | BD139-16 | BD135, BD137 (E-C-B); TIP41C, TIP31C, BD243C (B-C-E); BC337-40 low power (C-B-E) | 3x3 block: E-C-B = diagonal as shipped; B-C-E = move the pad-1 and pad-3 bridges; C-B-E = 1->C, 2->B, 3->E |
| Amp Q5 (PNP output) | BD140-16 | BD136, BD138 (E-C-B); TIP42C, TIP32C, BD244C (B-C-E); BC327-40 low power | same as Q4 |
| PSU Q1 (driver), Q3 (clamp) | BC547B/C | BC548, BC549, BC337-25; 2N3904 turned round | C-B-E |
| PSU Q2 (pass) | TIP41C | TIP31C, BD243C, MJE3055T, TIP41A/B | B-C-E only: this position has no jumper block |

Output power follows the output devices' hFE (simulated, ampB4.cir): hFE 40 clips at 0.2 W into 4 ohm,
hFE 120 makes 1.3 W, hFE 250 makes 1.8 W. Buy the -16 grade (hFE 100 to 250) or the -25/-40 grade of the
BC337/BC327 family; avoid ungraded BD139/BD140.

## Matching pairs

- **Q1 and Q2 (one channel's differential pair):** same part number and grade, ideally two from the same
  strip. Check with a DMM hFE socket: within 10 percent is enough. A 10 mV Vbe mismatch shifts the output
  midpoint by only 0.23 V (23 x 10 mV), which the circuit tolerates. Tighter matching buys nothing audible.
- **Q4 and Q5 (complementary outputs):** same hFE grade for both (both -16, or both -10). The feedback loop
  hides up to about 30 percent hFE difference; the trimmer removes the Vbe difference. Fit both channels
  with the same four part numbers so L and R behave alike.
- **Q6 (Vbe multiplier):** any BC547-family part, but it must sit next to the output transistors (it does on
  the layout) so the bias tracks their temperature. If you add a heatsink bar, let Q6 touch it.
- **R6/R7 (22k/1k, gain):** 1 percent parts so the two channels match within 2 percent. Nothing else in the
  amp needs better than 5 percent.
- **Emitter resistors R13/R14 (0.47 ohm):** same value and type for Q4 and Q5 of a channel.
- **PSU:** nothing needs matching. The four bridge diodes should be the same type.

## Tolerances and ratings (also in bom_all.csv, columns tolerance_rating / matching_note)

| Part | Spec | Why |
|---|---|---|
| R6 22k, R7 1k, R9 470, R10 1k | 1 percent metal film | gain balance, bias ratio |
| all other amp resistors | 5 percent 1/4 W | 5 percent moves the midpoint under 0.3 V |
| R13, R14 0.47 ohm | 5 percent, 2 W | carry the peak speaker current |
| RV 1k trimmer | multi-turn (3296W) preferred | bias set to 7-10 mV is easier with 10 turns |
| C4 100 pF | C0G/NP0, 50 V, 68 to 150 pF only | stability: larger loses bandwidth, smaller rings |
| C7 100 nF, C2 100 nF | X7R | Zobel / decoupling |
| amp electrolytics | 16 V, 20 percent; C6 1000 uF low ESR preferred | 12 V rail; C6 sets the 20-34 Hz corner |
| C1 1000 uF (rail) | 16 V | |
| PSU C1, C2 2200 uF | 25 V with a 12 VAC transformer, 35 V with 15 VAC | raw rail peaks at 21 V, 23 V at mains +10 percent |
| PSU C3 100 uF | 25 V | sits at 13 V |
| D5 13 V zener | 1 W, 5 percent (1N4743A) | VOUT = Vz - 1.3 V |
| D1-D4 1N5401 | 3 A, 100 V or more | 2 A rms secondary current at full power |
| R3 0.33 ohm | 3 W, 5 percent | clamp current 0.65 V / R3 = 2 A |
| F1 | 1 A slow-blow 5x20 (1.6 A for a 15 VAC 2 A transformer) | |
| RV1 volume | 10k log (A103) dual 6-pin; 20k log also fine | the amp's 43k input loads a 20k pot by 10 percent at mid travel |

## Power

- Transformer: 12 to 15 VAC secondary, 1.5 A or more for full stereo power (30 VA). A 250 mA
  transformer only supports quiet listening (about 0.13 A).
- Or feed 12 V DC into the PSU's "DC IN" terminal: it goes straight to the output through a
  Schottky diode and bypasses the regulator and the current clamp.
- Heatsinks: TIP41C on the PSU (up to 4.9 W at 15 VAC, 1.1 A); clip-on heatsinks on the four
  output transistors if you drive 4 ohm speakers hard (0.85 W each at clipping).

## First power-up (use the test points)

1. PSU alone, no load: TP1 VRAW 14 to 19 V, TP2 VZ 13 V, TP3 VOUT 11.5 to 11.7 V. LED on.
2. Amp: trimmers RV100/RV200 fully anticlockwise first (lowest bias). Power on. TP2 (OUT) of each
   channel reads about 5.9 V (half the rail). TP1 (B1) about 5.9 V.
3. Set bias: measure between TP3 (E4) and TP2 (OUT) of a channel: adjust that channel's trimmer
   until it reads 7 to 10 mV (15 to 20 mA quiescent). Re-check after 10 minutes warm.
4. Volume board: clockwise = louder. If it works backwards, swap the two outer pot pins.
5. The power LED can sit on the PSU (D7) or on the volume board (D1) via PSU header J5 -> volume
   header J3, two wires, pin 1 = +. Fit one LED, not both.
