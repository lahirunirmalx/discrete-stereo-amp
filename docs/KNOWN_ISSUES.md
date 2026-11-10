# Known issues and limitations (revision 1.3)

1. **Single-sided amp board is not finished, and got worse with the six extra parts.** One copper layer, 27
   auto-placed wire links, 42 DRC errors remain, 18 of them shorts (links crowding neighbouring copper around the 3x3
   jumper blocks). Do not etch it as generated. Open
   `kicad/amp/amp_1layer.kicad_pcb` in KiCad and finish by hand before etching, or build the amp on the 2-layer
   panel. The single-sided PSU, volume and headphone boards are DRC clean.
2. **Nothing has been built or measured.** All numbers are ngspice results with generic transistor models
   (datasheet-typical hFE, swept to the minimum); no thermal coupling, speaker modelled as a resistor, LED
   modelled as a generic red diode.
3. **Silkscreen** references sit inside the resistor / diode / ceramic outlines; electrolytics, transistors and
   test points keep theirs beside the part. Some still touch a neighbour's outline (DRC warnings).
4. **The headphone jack's switch pins are unused** by design (see docs/01, 1.4): the speaker / headphone choice is
   the toggle switch. Plugging in headphones does not mute the speakers.
5. **Toggle switch pad pattern** (two rows of three, 4.7 mm along the rows, 4.8 mm between them, 2.2 mm holes) is
   the common MTS-202 pattern taken from memory, not from a datasheet. Check your switch against the bare board
   before soldering; any DPDT can be wired to the six pads. A slide switch on these pads works the other way round
   from the "LEVER UP = SPK" mark.
6. **12 VAC transformers** only hold the 12.0 V set point up to about 0.4 A; set 11.5 V on the trimmer and expect
   the output to follow the raw rail above that. Full power needs 15 VAC.
7. **Volume pot pin convention** (pin 3 = clockwise end) follows the datasheet convention; if a substitute pot
   is wired the other way the knob works backwards. Swap the two outer wires.
8. **Mouser part numbers** in bom_mouser.csv are from memory, not stock-checked; some electrolytic case sizes
   may not match the footprint pitch exactly (see bom_mouser_notes.md).
9. **The analyzers (check-schematic / check-pcb), the EMC and thermal runs, the CircuitJS links and the notes
   page** still describe the release 1 circuits; they have not been re-run for release 2.
10. The 2-layer boards report 4 "extra footprint" schematic-parity warnings each: the mounting holes, which
    exist only on the PCB. Expected. The amp also reports 36 "exclude from BOM" attribute warnings on the solder
    jumpers, also expected.
11. **The PSU is short-circuit tolerant for seconds, not indefinitely.** The clamp holds 2.1 A and the 1.6 A
    slow-blow fuse then opens; until it does the TIP41C dissipates 25 W. Use the specified fuse, not a larger one,
    and a heatsink of 10 C/W or better. The 12 V DC input path has no fuse or clamp at all on the PSU board (the
    amp board has its own resettable fuse).
12. **Output inductor current rating.** Small axial 2.2 uH chokes vary from 0.3 A to 2 A; the part must carry 1 A.
    If in doubt wind the coil on the resistor (docs/04, 4.2).
13. **Supply rejection is 53 dB at 100 Hz.** Fine behind the PSU board (under 70 mV ripple gives under 0.2 mV at
    the speaker); a noisy unregulated 12 V adapter may hum.
