"""Compare a KiCad netlist against an ngspice deck: same net partition.

Usage: netcheck.py board.net deck.cir map.json
map.json: {"refmap": {"R101": "Rb1", ...}            KiCad ref -> deck ref (pins keep their numbers / names)
           "pinmap": {"R": {"1": "a", "2": "b"}, ...}  per KiCad ref prefix, KiCad pin -> deck pin name
           "pins":   {"TP101.1": "Q1.B", ...}          explicit KiCad pin -> deck pin
           "ignore": ["JP", "J", "#"]                 KiCad ref prefixes with no deck counterpart
           "links":  [["JP101", "1", "JP101", "2"], ...]  bridged jumpers: these KiCad pins are one node}
Deck refs not drawn (sources, loads) are reported as 'not drawn' only, never as errors.
"""
import json, re, sys
sys.path.insert(0, "/home/lahiru/.claude/skills/circuit-sim")
from schem import spice_nodes


def kicad_nets(netfile):
    txt = open(netfile).read()
    txt = txt[txt.find("(nets"):]
    nets = {}
    for chunk in txt.split("(net (code")[1:]:
        name = re.search(r'\(name "([^"]+)"\)', chunk).group(1)
        nets[name] = re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', chunk)
    return nets


def main(netfile, deck, mapfile):
    m = json.load(open(mapfile))
    deck_nodes = spice_nodes(deck)
    knets = kicad_nets(netfile)
    # union-find over KiCad nets joined by bridged jumpers
    par = {n: n for n in knets}
    def find(a):
        while par[a] != a:
            a = par[a]
        return a
    net_of = {(r, p): n for n, pins in knets.items() for r, p in pins}
    for r1, p1, r2, p2 in m.get("links", []):
        a, b = find(net_of[(r1, p1)]), find(net_of[(r2, p2)])
        if a != b:
            par[a] = b
    # map every KiCad pin to a deck pin
    problems, seen_deck, kpin_node = [], {}, {}
    for (ref, pin), net in net_of.items():
        key = "%s.%s" % (ref, pin)
        if key in m.get("pins", {}):
            dkey = m["pins"][key]
        else:
            pre = re.match(r"[A-Za-z#]+", ref).group(0)
            if ref in m["refmap"]:
                dref = m["refmap"][ref]
            elif any(ref.startswith(x) for x in m.get("ignore", [])):
                continue
            else:
                problems.append("no mapping for %s" % ref); continue
            pm = m.get("pinmap", {}).get(pre, {})
            dkey = "%s.%s" % (dref, pm.get(pin, pin))
        if dkey not in deck_nodes:
            problems.append("%s -> %s not in deck" % (key, dkey)); continue
        kpin_node[key] = (find(net), deck_nodes[dkey])
        seen_deck[dkey] = key
    # partition check: each deck node must be exactly one KiCad net and vice versa
    k2d, d2k = {}, {}
    for key, (kn, dn) in kpin_node.items():
        k2d.setdefault(kn, set()).add(dn)
        d2k.setdefault(dn, set()).add(kn)
    for kn, dns in k2d.items():
        if len(dns) > 1:
            problems.append("KiCad net %s merges deck nodes %s" % (kn, sorted(dns)))
    for dn, kns in d2k.items():
        if len(kns) > 1:
            problems.append("deck node %s is split across KiCad nets %s" % (dn, sorted(kns)))
    missing = sorted(set(deck_nodes) - set(seen_deck))
    print("deck pins not drawn:", ", ".join(missing) or "none")
    for p in problems:
        print("PROBLEM:", p)
    print("netcheck:", "OK" if not problems else "%d problems" % len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
