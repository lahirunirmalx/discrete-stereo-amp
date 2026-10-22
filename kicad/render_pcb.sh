#!/bin/bash
# Render the board (top view, both copper layers + silk + outline) to pcb.png
cd "$(dirname "$0")"
PCB="${1:-rat.kicad_pcb}"; OUT="${2:-pcb.png}"
D=pcbsvg_$$; rm -rf $D && mkdir $D
kicad-cli pcb export svg --layers "B.Cu,F.Cu,F.SilkS,Edge.Cuts,F.CrtYd" --page-size-mode 2 --exclude-drawing-sheet --mode-single -o $D/pcb.svg "$PCB" >/dev/null
/usr/bin/python3 - $D/pcb.svg <<'PY'
import re, sys
t = open(sys.argv[1]).read()
t = re.sub(r'width="[^"]+"', 'width="2100"', t, count=1)
t = re.sub(r'height="[^"]+"', 'height="1350"', t, count=1)
open(sys.argv[1], "w").write(t)
PY
/usr/bin/google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars --window-size=2100,1350 --screenshot="$PWD/$OUT" "file://$PWD/$D/pcb.svg" 2>/dev/null
rm -rf $D; echo "$PWD/$OUT"
