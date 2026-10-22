# Known issues and limitations (release 1.2)

1. **Single-sided amp board is not finished.** One copper layer, 24 auto-placed wire links, 15 DRC errors remain
   (open connections and links crowding neighbouring copper around the 3x3 jumper blocks). Open
   `kicad/amp/amp_1layer.kicad_pcb` in KiCad and finish by hand before etching, or build the amp on the 2-layer
   panel. The single-sided PSU, volume and headphone boards are DRC clean.
2. **Nothing has been built or measured.** All numbers are ngspice results with generic transistor models
   (datasheet-typical hFE, swept to the minimum); no thermal coupling, speaker modelled as a resistor, LED
   modelled as a generic red diode.
3. **Silkscreen** references sit inside the resistor / diode / ceramic outlines; electrolytics, transistors and
   test points keep theirs beside the part. Some still touch a neighbour's outline (DRC warnings).
4. **The headphone jack's switch pins are unused** by design (see docs/01, 1.4): the speaker / headphone choice is
   the slide switch. Plugging in headphones does not mute the speakers.
5. **Slide switch pin numbering** follows the C&K JS202011 drawing (1-2-3 in one row, 6-5-4 under them). A switch
   numbered the other way round still works if its commons land on the centre pads; check with a DMM.
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
11. **LED positions are not hybrid.** D10001 / D20001 (tail references) and the power LEDs (PSU D7, volume D1)
    use a plain 3 mm LED footprint: no 1206 LED twin, and the two-1N4148 substitute for the tail reference only
    fits by stacking both diodes into the LED's two holes. Planned for the next PCB revision: a hybrid
    `Custom:LED_D3_1206` footprint (3 mm pattern + 1206 twin + a third free hole between the pads so two DO-35
    diodes fit end to end). Circuit unchanged; boards, panel and release rebuild.
