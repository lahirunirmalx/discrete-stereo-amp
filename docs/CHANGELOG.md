# Changelog

## 2026-10-22, release 1.2 (prototype, unbuilt)

Circuit:
- Amp front end rebuilt for distortion: PNP input pair (BC557) with an NPN current-mirror load (100 ohm emitters),
  a BC557 current-source tail referenced to a red LED (1 mA), an NPN VAS (47 ohm emitter) with the bootstrapped
  load moved to +12 V, 220 pF Miller plus a 47 pF lead capacitor across the 22k feedback resistor. Simulated THD
  0.004 percent at 26 mW and 0.019 percent at 0.29 W into 8 ohm (was 0.03 / 0.2), 0.013 percent at 52 mW into
  4 ohm (was 0.18). Output stage, bias spreader and feedback network unchanged, so the pinout blocks, the trimmer
  procedure and the output power are as before. -3 dB bandwidth is now 120 kHz (was 250 kHz); midpoint 6.1 V.
- PSU regulation loop closed: BC547 error amplifier compares a divider of VOUT (8.2k + 2k trimmer over 10k) with a
  5.6 V zener fed from the regulated output and pulls the driver base down through a 2.2k pull-up from the raw
  rail; 47 nF loop compensation, 100 nF feed-forward. 12.0 V set point (trimmer 11.4 to 12.7 V), 12.10 to 11.96 V
  from 0.1 to 1.2 A (was 11.6 to 11.2), 4 to 70 mV ripple, 0.14 V dip on a 1 A step, no ringing. Clamp, DC-in
  bypass and reverse protection unchanged. The 13 V zener, 1k feed and 100 uF filter are gone.
- VU meter tap on the amp: 1k from each speaker node to a new 1x3 header J5 "VU L G R".
- New headphone board (42 x 30 mm): 3-pin input from the amp speaker terminals, two speaker terminals, DPDT slide
  switch (speakers / phones), 120 ohm series resistors with "DIRECT" bypass jumpers, 3.5 mm jack (CUI SJ1-3535NG
  pattern, switch pins unused) plus a 3-pin header for a panel-mount jack. The jack's own switch cannot both mute
  the speakers and keep a series resistor out of the speaker path, hence the switch (docs/01, 1.4).

Boards:
- Amp wide 134 x 85 mm (was 71), compact 100 x 98 mm (still inside the 100 x 100 tier), PSU 90 x 58 mm (was 50),
  volume 42 x 26 mm, headphone 42 x 30 mm; panel 155 x 155 mm square with the headphone board above the volume
  board on the right (30 + 2 + 26 = 58 = PSU height). All 2-layer boards and the panel are DRC clean.
- Single-sided: PSU, volume and headphone boards clean (1, 1 and 3 wire links); amp 24 links and 15 DRC errors
  (was 62), still unfinished.
- Test points: TPx4 (LED reference, 10.1 V) per amp channel, TP5 (FB, 6.3 V) on the PSU, TP1 to TP3 on the
  headphone board. Every expected voltage is printed on the silkscreen or in the schematic value.
- Version stamp now comes from one constant (kicad/common.py STAMP) used by every board, the panel rails and the
  release name. A second autorouter pass runs automatically when the first leaves connections open.

Documents and BOM:
- Theory, simulation results (new sections 2.7 to 2.9), design review, build guide, order guide and README
  rewritten for the new circuits; the figures are now the generated KiCad schematics.
- BOM: substitutes and notes for the nine new amp positions per channel, the five new PSU positions and the
  headphone board; Mouser map extended. 145 parts + 38 solder jumpers.

How this honours the three standing rules:
- Modular: the amp still runs alone from 12 V DC; the headphone board is a pass-through that can be left out;
  the VU header is open by default; the PSU works with or without the trimmer touched (mid travel gives 12 V).
- Hybrid / multi-part: every new resistor and capacitor has the through-hole plus 1206 twin, every new TO-92
  position has the SOT-23 twin, the LED reference lists a two-diode alternative, the jack has a panel-mount
  alternative on a header, the switch is any DPDT on a 2x3 pattern, and at least three substitutes are listed per
  transistor position.
- Test points for beginners: four per amp channel, five on the PSU, three on the headphone board, each with its
  expected voltage, and the bring-up guide walks through them in order.

## 2026-10-21, release 1.1 (prototype, unbuilt), updated 2026-10-22

- Compact amp layout (100 x 85 mm, `kicad/amp/amp_compact.kicad_pcb`, `build.sh amp --compact`) next to the wide one; per-board gerber zips in the release.
- Modular build paths documented (amp alone from 12 V DC works; volume board and PSU optional).
- Preamp study (docs/05).

- Screw terminals rotated so the wire entry faces the board edge (was backwards in 1.0).
- Amp board 134 x 71 mm (was 100 x 83): three wider rows, same width as PSU plus volume board.
- Square 144 x 144 mm panel with 3 mm rails; PSU and volume board side by side under the amp; tabs to the rails.
- Hybrid footprints built from the library parts: diode bars, + marks and TO-92 flat sides on the silkscreen.
- Silkscreen references inside resistor / diode / ceramic outlines, larger text; board titles carry the revision.
- Repository URL and revision stamped on every board and on the panel rails.
- Logo (knob ring, clipped sine trace, NPN symbol) and a 1280 x 640 social banner in docs/images.
- README shows 3D renders, schematics and layouts; CircuitJS links in the review; license CC BY-NC-SA 4.0.
- Single-sided PSU now routes without wire links. Single-sided amp still unfinished (see KNOWN_ISSUES.md).

## 2026-10-21, release 1.0 (prototype, unbuilt)

- Reviewed the original one_transister_amp (speaker-in-collector, 2k collector feedback): bias set by hFE,
  DC through the speaker, 11 ohm input, clipping above 50 mVpk. Report: ~/electronics-notes/one-transistor-amp.html.
- Designed the replacement: two class-AB channels (diff pair, VAS, Vbe multiplier, BD139/BD140), a discrete
  12 V supply with DC-in bypass and 2 A clamp, a dual-pot volume board with optional front-panel LED.
- Simulated in ngspice: candidate comparison, hFE sweeps, bias network, stability, output power, supply regulation.
- Generated KiCad 9 schematics (ERC clean, netlist checked against the decks) and boards (2-layer, DRC clean),
  a multi-design panel (144 x 144 mm, DRC clean) and single-sided variants (PSU and volume clean; amp routed
  but with 62 DRC errors, needs hand finishing).
- BOMs: per board, combined, shopping list, Mouser upload format.
- Panel re-arranged into a 144 x 144 mm square with rails (volume board rotated beside the amp); silkscreen
  references moved inside the resistor, diode and ceramic-capacitor outlines, larger text.
- Known issues: see KNOWN_ISSUES.md.
