# Known issues and limitations (release 1)

1. **Single-sided amp board is not finished.** 789 one-layer track segments and 21 auto-placed wire links,
   but 66 DRC errors remain (open connections and links crowding neighbouring copper around the 3x3 jumper
   blocks). Open `kicad/amp/amp_1layer.kicad_pcb` in KiCad and finish by hand before etching, or build the amp
   on the 2-layer panel. The single-sided volume board is DRC clean; the single-sided PSU has one open
   connection (bleeder R1 pin 1 to VRAW): solder a wire from R1 pin 1 to TP1.
2. **Nothing has been built or measured.** All numbers are ngspice results with generic transistor models
   (datasheet-typical hFE, swept to the minimum); no thermal coupling, speaker modelled as a resistor.
3. **Silkscreen is crowded on the amp** (139 "silkscreen overlap" DRC warnings): reference labels of
   neighbouring parts touch. Readable, not pretty.
4. **Terminal block orientation** was wrong in the first layout (wire entry facing inwards); fixed after the
   3D render showed it. Confirm on the first bare board before soldering the terminals.
5. **Volume pot pin convention** (pin 3 = clockwise end) follows the datasheet convention; if a substitute pot
   is wired the other way the knob works backwards. Swap the two outer wires.
6. **Mouser part numbers** in bom_mouser.csv are from memory, not stock-checked; some electrolytic case sizes
   may not match the footprint pitch exactly (see bom_mouser_notes.md).
7. **PSU load regulation is open-loop** (zener follower): 11.6 V at 0.1 A to 11.2 V at 1.1 A. Fine for this amp,
   not a lab supply.
8. **EMC rules from the check-pcb analyzer assume 150 MHz designs**; their ground-plane findings are not
   applicable to a 20 kHz audio board and were triaged as such in the design review.
9. The 2-layer boards report 4 "extra footprint" schematic-parity warnings each: the mounting holes, which
   exist only on the PCB. Expected.
