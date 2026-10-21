#!/bin/bash
# Regenerate everything from the generators: schematics -> netlists -> checks -> boards -> panel -> docs -> release.
set -e
cd "$(dirname "$0")/kicad"
for b in amp psu vol; do
  /usr/bin/python3 gen_$b.py
  kicad-cli sch export netlist --format kicadsexpr -o $b/$b.net $b/$b.kicad_sch
done
for b in 100 200; do /usr/bin/python3 netcheck.py amp/amp.net ../sim/amp_final.cir amp/netmap_$b.json; done
/usr/bin/python3 netcheck.py psu/psu.net ../sim/psu.cir psu/netmap.json
for b in amp psu vol; do ./build.sh $b; done
(cd panel && ~/tools/kikit-venv/bin/python make_panel.py stereo-panel.kicad_pcb ../amp/amp.kicad_pcb ../psu/psu.kicad_pcb ../vol/vol.kicad_pcb)
for b in vol psu; do ./build.sh $b --single; done
./build.sh amp --single || echo "single-sided amp: expected DRC errors, see docs/KNOWN_ISSUES.md"
/usr/bin/python3 bom.py && /usr/bin/python3 bom_shopping.py && /usr/bin/python3 bom_mouser.py
/usr/bin/python3 ../docs/gen_sim_results.py
./release.sh
