"""Add (or refresh) a GND copper pour on B.Cu and fill it. Run with /usr/bin/python3."""
import sys
import pcbnew
from pcbnew import VECTOR2I, FromMM

path = sys.argv[1]
b = pcbnew.LoadBoard(path)
for z in list(b.Zones()):
    b.Remove(z)
gnd = b.FindNet("GND")
bb = b.GetBoardEdgesBoundingBox()
z = pcbnew.ZONE(b)
z.SetLayer(pcbnew.B_Cu)
z.SetNet(gnd)
z.SetAssignedPriority(0)
z.SetLocalClearance(FromMM(0.3))
z.SetMinThickness(FromMM(0.3))
z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
z.SetThermalReliefGap(FromMM(0.4))
z.SetThermalReliefSpokeWidth(FromMM(0.5))
z.SetIsFilled(False)
z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)   # a GND island is a gap to bridge, not copper
pts = [(bb.GetLeft(), bb.GetTop()), (bb.GetRight(), bb.GetTop()),
       (bb.GetRight(), bb.GetBottom()), (bb.GetLeft(), bb.GetBottom())]
outline = z.Outline()
outline.NewOutline()
for x, y in pts:
    outline.Append(x, y)
b.Add(z)
filler = pcbnew.ZONE_FILLER(b)
filler.Fill(b.Zones())
pcbnew.SaveBoard(path, b)
print("GND zone on B.Cu filled:", z.GetFilledArea() / 1e12 * 1e6 if hasattr(z, "GetFilledArea") else "ok")
