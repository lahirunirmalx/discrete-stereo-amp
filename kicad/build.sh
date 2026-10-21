#!/bin/bash
# Usage: ./build.sh <amp|psu|vol> [--single]
# place -> freerouting -> import SES -> GND pour -> DRC (schematic parity on the 2-layer board) -> render
set -e
cd "$(dirname "$0")"
B=$1; SINGLE=$2
STEM=$B; [ "$SINGLE" = "--single" ] && STEM=${B}_1layer
/usr/bin/python3 gen_pcb_$B.py $SINGLE
rm -f $B/$STEM.ses
/usr/bin/python3 netrename.py dsn $B/$STEM.dsn
PASSES=120; [ "$SINGLE" = "--single" ] && PASSES=120
~/.local/bin/freerouting -de $B/$STEM.dsn -do $B/$STEM.ses -mp $PASSES -oit 0.3 2>&1 | grep -vE "New version|Gtk|^\s*$" | tail -4
cp $B/$STEM.netmap.json $B/$STEM.netmap.json.bak 2>/dev/null; /usr/bin/python3 netrename.py ses $B/$STEM.ses
/usr/bin/python3 - $B/$STEM.kicad_pcb $B/$STEM.ses <<'PY'
import sys, pcbnew
from collections import Counter
b = pcbnew.LoadBoard(sys.argv[1])
assert pcbnew.ImportSpecctraSES(b, sys.argv[2])
tr = list(b.GetTracks())
print("routed:", dict(Counter(b.GetLayerName(t.GetLayer()) for t in tr)), "vias:", sum(1 for t in tr if t.GetClass() == "PCB_VIA"))
pcbnew.SaveBoard(sys.argv[1], b)
PY
/usr/bin/python3 add_gnd_zone.py $B/$STEM.kicad_pcb
if [ "$SINGLE" = "--single" ]; then
  kicad-cli pcb drc --format json -o $B/drc_$STEM.json $B/$STEM.kicad_pcb >/dev/null
  for round in 1 2 3; do
    grep -q "Missing connection" $B/drc_$STEM.json || break
    /usr/bin/python3 auto_links.py $B/$STEM.kicad_pcb $B/drc_$STEM.json | tail -1
    /usr/bin/python3 add_gnd_zone.py $B/$STEM.kicad_pcb >/dev/null
    kicad-cli pcb drc --format json -o $B/drc_$STEM.json $B/$STEM.kicad_pcb >/dev/null
  done
else
  kicad-cli pcb drc --schematic-parity --format json -o $B/drc_$STEM.json $B/$STEM.kicad_pcb >/dev/null
fi
/usr/bin/python3 drc_summary.py $B/drc_$STEM.json $B/$STEM.kicad_pcb
./render_pcb.sh $B/$STEM.kicad_pcb $B/pcb_$STEM.png
