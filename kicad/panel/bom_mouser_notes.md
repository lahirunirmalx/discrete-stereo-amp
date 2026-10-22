# Mouser BOM notes

The MPNs in bom_mouser.csv were chosen from memory and are NOT stock- or price-checked. Upload the CSV to Mouser's BOM tool, let it match each line, and replace any line it rejects with the equivalent it suggests.

- UVR1C102MED: check case 8 mm / pitch 3.5 mm
- UVR1C101MDD: footprint pitch 2.5 mm: bend leads
- UVR1C100MDD: zener filter
- UVR1E222MHD: use a 35 V part with a 15 VAC transformer
- C315C221J1G5TA: Miller cap: C0G only
- C320C473K5R5TA: PSU loop compensation
- C315C470J1G5TA: feedback lead cap: C0G only
- 0218001.MXP: plus 2 clips, next line
- PTD902-2015K-A103: check pin pattern against the RK097 footprint before buying
- KNP300JR-73-0R33: any 0.33 R 2-3 W axial
- KNP200JR-73-0R47: any 0.47 R 2 W axial
- 5001: optional: a bent resistor lead works
- BD139-16: or BD139 ungraded + sort by hFE
- TIP41C: needs a TO-220 heatsink, e.g. Aavid 577202B00000G
- 3517: footprint is the Littelfuse 100-series clip pattern; any 5x20 PCB clip at 20.5 mm spacing
