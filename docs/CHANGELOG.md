# Changelog

## 2026-10-21, release 1.1 (prototype, unbuilt)

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
