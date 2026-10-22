#!/bin/bash
# Fab package: gerbers + drill for the 2-layer panel (amp + PSU + volume + headphone), per-board zips, single-layer boards, schematic PDFs,
# BOMs, board pictures, ORDER_GUIDE.md -> release/stereo-amp-release-<date>.zip
set -e
cd "$(dirname "$0")"
OUT=../release/pkg; rm -rf $OUT; mkdir -p $OUT/panel_2layer_gerbers $OUT/single_layer $OUT/schematics $OUT/pictures $OUT/kicad_projects
kicad-cli pcb export gerbers --layers "F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts" --no-protel-ext -o $OUT/panel_2layer_gerbers/ panel/stereo-panel.kicad_pcb >/dev/null
kicad-cli pcb export drill --format excellon --excellon-separate-th -o $OUT/panel_2layer_gerbers/ panel/stereo-panel.kicad_pcb >/dev/null
(cd $OUT/panel_2layer_gerbers && zip -q ../stereo-panel-gerbers.zip *)
# one gerber zip per 2-layer board, for ordering boards separately (each PSU and volume fit JLCPCB's 100 x 100 tier)
mkdir -p $OUT/single_boards_2layer
for b in amp amp_compact psu vol hp; do
  src=$b; [ $b = amp_compact ] && src=amp
  d=$OUT/single_boards_2layer/${b}_gerbers; mkdir -p $d
  kicad-cli pcb export gerbers --layers "F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts" --no-protel-ext -o $d/ $src/$b.kicad_pcb >/dev/null
  kicad-cli pcb export drill --format excellon --excellon-separate-th -o $d/ $src/$b.kicad_pcb >/dev/null
  (cd $d && zip -q ../${b}-2layer-gerbers.zip *)
done
for b in amp psu vol hp; do
  d=$OUT/single_layer/${b}_1layer; mkdir -p $d
  kicad-cli pcb export gerbers --layers "B.Cu,B.Mask,F.SilkS,Edge.Cuts" --no-protel-ext -o $d/ $b/${b}_1layer.kicad_pcb >/dev/null
  kicad-cli pcb export drill --format excellon --excellon-separate-th -o $d/ $b/${b}_1layer.kicad_pcb >/dev/null
  # 1:1 mirrored bottom copper for toner transfer / photoresist
  kicad-cli pcb export pdf --layers "B.Cu,Edge.Cuts" --mirror --black-and-white -o $OUT/single_layer/${b}_1layer_etch_mirrored.pdf $b/${b}_1layer.kicad_pcb >/dev/null
  kicad-cli sch export pdf -o $OUT/schematics/${b}_schematic.pdf $b/$b.kicad_sch >/dev/null
  cp $b/bom_$b.csv $OUT/
  cp $b/pcb_$b.png $OUT/pictures/${b}_2layer.png; cp $b/pcb_${b}_1layer.png $OUT/pictures/${b}_1layer.png 2>/dev/null || true
  mkdir -p $OUT/kicad_projects/$b; cp $b/$b.kicad_pro $b/$b.kicad_sch $b/$b.kicad_pcb $b/${b}_1layer.kicad_pcb $OUT/kicad_projects/$b/
  if [ $b = amp ]; then cp amp/amp_compact.kicad_pcb $OUT/kicad_projects/amp/; cp amp/pcb_amp_compact.png $OUT/pictures/amp_compact_2layer.png; fi
done
cp panel/bom_all.csv panel/bom_shopping.csv panel/bom_shopping.md panel/bom_mouser.csv panel/bom_mouser_notes.md panel/panel.png $OUT/; cp panel/panel.png $OUT/pictures/panel_2layer.png; cp panel/stereo-panel.kicad_pcb $OUT/kicad_projects/
cp ../ORDER_GUIDE.md ../README.md ../LICENSE $OUT/; mkdir -p $OUT/docs; cp -r ../docs/*.md ../docs/images $OUT/docs/; cp ../sim/*.cir ../sim/*.out ../sim/*.inc ../sim/README.md $OUT/sim/ 2>/dev/null || (mkdir -p $OUT/sim && cp ../sim/*.cir ../sim/*.out ../sim/*.inc ../sim/README.md $OUT/sim/)
STAMP=v1.2-$(date +%Y-%m-%d)
(cd ../release && rm -f stereo-amp-release-$STAMP.zip && zip -qr stereo-amp-release-$STAMP.zip pkg)
echo "release/stereo-amp-release-$STAMP.zip"; du -sh ../release/stereo-amp-release-$STAMP.zip
