"""Render both halves of every interface and check each one.

usage: python3 tests/test_ports.py [OPENSCAD]

For bayonet_std, mini, midi, large and xl, the pin and lock halves each render
with --hardwarnings and no WARNING or ERROR line (a failed assert leaves the exit
status at 0, so the output decides), as one solid. The pin is as wide as its
flange: 2 x bayonet_flange_radius() across.
"""

import json
import os
import struct
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPES = ["bayonet_std", "bayonet_mini", "bayonet_midi", "bayonet_large", "bayonet_xl"]
results = []


def check(label, ok, got):
    results.append(bool(ok))
    print(f"{'ok  ' if ok else 'FAIL'} {label}: {got}")


def run(openscad, body, out, tmp):
    path = os.path.join(tmp, "probe.scad")
    with open(path, "w") as f:
        f.write(f"include <{ROOT}/custom/bayonet_interfaces.scad>\nuse <{ROOT}/custom/bayonet_port.scad>\n{body}\n")
    cmd = [openscad, "--hardwarnings", "-o", out]
    if out.endswith(".stl"):
        cmd += ["--export-format", "binstl"]
    r = subprocess.run(cmd + [path], capture_output=True, text=True)
    bad = [l for l in r.stderr.splitlines() if l.startswith(("WARNING", "ERROR"))]
    return r, bad


def solids(path):
    data = open(path, "rb").read()
    (n,) = struct.unpack_from("<I", data, 80)
    parent = {}

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    for i in range(n):
        t = struct.unpack_from("<9f", data, 84 + i * 50 + 12)
        corners = [t[0:3], t[3:6], t[6:9]]
        for c in corners:
            parent.setdefault(c, c)
        root = find(corners[0])
        for c in corners[1:]:
            parent[find(c)] = root
    size = [max(p[i] for p in parent) - min(p[i] for p in parent) for i in range(3)]
    return len({find(v) for v in parent}), size


def main():
    openscad = sys.argv[1] if len(sys.argv) > 1 else "openscad"
    with tempfile.TemporaryDirectory() as tmp:
        stl = os.path.join(tmp, "out.stl")
        csg = os.path.join(tmp, "out.csg")
        for t in TYPES:
            r, _ = run(openscad, f"echo(bayonet_flange_radius({t}));", csg, tmp)
            echoes = [l for l in r.stderr.splitlines() if l.startswith("ECHO: ")]
            flange = json.loads(echoes[0].split("ECHO: ", 1)[1]) if echoes else None
            for part in ("pin", "lock"):
                r, bad = run(openscad, f'bayonet_port(type={t}, part="{part}", panel_thickness=18);', stl, tmp)
                if r.returncode != 0 or bad:
                    check(f"{t} {part}", False, bad[:1] or f"exit {r.returncode}")
                    continue
                n, size = solids(stl)
                check(f"{t} {part} is one solid", n == 1, f"{n} solid(s)")
                if part == "pin":
                    want = 2 * flange
                    # A faceted circle reaches its full diameter only where a vertex sits on the axis.
                    ok = abs(max(size[:2]) - want) < 0.05
                    check(f"{t} pin is as wide as its flange", ok,
                          f"{size[0]:.2f} x {size[1]:.2f} mm; want {want:g}")
    print(f"{sum(results)} of {len(results)} checks passed")


if __name__ == "__main__":
    main()
    sys.exit(0 if results and all(results) else 1)
