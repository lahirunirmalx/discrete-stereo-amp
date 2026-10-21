# Changelog

## 2026-10-21, release 1 (prototype, unbuilt)

- Reviewed the original one_transister_amp (speaker-in-collector, 2k collector feedback): bias set by hFE,
  DC through the speaker, 11 ohm input, clipping above 50 mVpk. Report: ~/electronics-notes/one-transistor-amp.html.
- Designed the replacement: two class-AB channels (diff pair, VAS, Vbe multiplier, BD139/BD140), a discrete
  12 V supply with DC-in bypass and 2 A clamp, a dual-pot volume board with optional front-panel LED.
- Simulated in ngspice: candidate comparison, hFE sweeps, bias network, stability, output power, supply regulation.
- Generated KiCad 9 schematics (ERC clean, netlist checked against the decks) and boards (2-layer, DRC clean),
  a multi-design panel (134 x 137 mm, DRC clean) and single-sided variants (PSU and volume clean; amp routed
  but with 66 DRC errors, needs hand finishing).
- BOMs: per board, combined, shopping list, Mouser upload format.
- Hybrid footprints now start from the library part, so diode bars, + marks and TO-92 flat sides are on the silkscreen.
- 3D renders (kicad-cli pcb render) of every board and the panel in docs/images.
- Licensed CC BY-NC-SA 4.0.
- Screw terminals rotated 180 degrees on amp and PSU (wire entry now faces the board edge); amp board grew to 100 x 85 mm.
- Known issues: see KNOWN_ISSUES.md.
