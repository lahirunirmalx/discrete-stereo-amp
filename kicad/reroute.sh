#!/bin/bash
# Second autorouter pass on a board that still has unrouted connections: export the DSN from the routed board
# (existing tracks and vias are kept as a starting point), run freerouting again, re-import, re-pour, DRC, render.
# Usage: ./reroute.sh <board.kicad_pcb> [passes]
set -e
cd "$(dirname "$0")"
PCB=$1; P=${2:-200}; STEM=${PCB%.kicad_pcb}; DIR=${PCB%/*}; NAME=${STEM#*/}
/usr/bin/python3 - $PCB $STEM.r2.dsn <<'PY'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
for z in list(b.Zones()):
    b.Remove(z)
pcbnew.ExportSpecctraDSN(b, sys.argv[2])
PY
/usr/bin/python3 -c "
import sys; sys.path.insert(0, '.')
from pcbgen import shrink_boundary; shrink_boundary('$STEM.r2.dsn')"
rm -f $STEM.r2.ses
~/.local/bin/freerouting -de $STEM.r2.dsn -do $STEM.r2.ses -mp $P -oit 0.3 2>&1 | grep -vE "New version|Gtk|^\s*$" | tail -2
/usr/bin/python3 - $PCB $STEM.r2.ses <<'PY'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
for t in list(b.GetTracks()):
    b.Remove(t)
assert pcbnew.ImportSpecctraSES(b, sys.argv[2])
pcbnew.SaveBoard(sys.argv[1], b)
PY
/usr/bin/python3 add_gnd_zone.py $PCB
PARITY=--schematic-parity; case $NAME in *_1layer|amp_compact) PARITY="";; esac
kicad-cli pcb drc $PARITY --format json -o $DIR/drc_$NAME.json $PCB >/dev/null
/usr/bin/python3 drc_summary.py $DIR/drc_$NAME.json $PCB
./render_pcb.sh $PCB $DIR/pcb_$NAME.png
