"""freerouting 1.9 occasionally writes one wire path into two nets whose names look like Net-(R10009-Pad2).
Route with plain names instead: `netrename.py dsn file.dsn` rewrites the net names to N<n> and saves the map;
`netrename.py ses file.ses` puts the original names back."""
import json, re, sys
mode, path = sys.argv[1], sys.argv[2]
mapfile = path.rsplit(".", 1)[0] + ".netmap.json"
txt = open(path).read()
if mode == "dsn":
    names = sorted(set(re.findall(r'\(net ("[^"]+"|[^\s()]+)\s*\(pins', txt)), key=len, reverse=True)
    m = {}
    for i, n in enumerate(names, start=1):
        m[n] = "N%d" % i
    # net names appear in (net X (pins ...)) and in the class list; replace exact tokens only
    def repl(mo):
        tok = mo.group(0)
        return m.get(tok, tok)
    pat = "|".join(re.escape(n) for n in names)
    txt = re.sub(pat, repl, txt)
    json.dump(m, open(mapfile, "w"))
    open(path, "w").write(txt)
    print("renamed", len(m), "nets")
else:
    m = json.load(open(mapfile.replace(".ses", ".dsn") if False else mapfile))
    inv = {v: k for k, v in m.items()}
    txt = re.sub(r'\(net (N\d+)\b', lambda mo: "(net " + inv.get(mo.group(1), mo.group(1)), txt)
    open(path, "w").write(txt)
    print("restored", len(inv), "nets")
