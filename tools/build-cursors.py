#!/usr/bin/env python3
"""Build the bundle's cursor theme into the icon theme directory.

Xcursor files (cursors/) carry the genuine Windows XP bitmaps at 24/32 px from
xfce-winxp-tc plus renders of the modernXP SVG redraws at 48/64/96 px, so the
pointer is pixel-authentic at 1x and crisp at 2x/3x. The SVGs are also shipped
in KDE's cursors_scalable/ layout. Symlinks are never used: the bundle importer
rejects them, so every alias is a real file.

usage: build-cursors.py <xfce-winxp-tc cursors/with-shadow/standard> <modernXP src> <icon theme dir>
needs: xcursorgen, resvg
"""
import json, pathlib, shutil, subprocess, sys, tempfile

xfce, modern, out = (pathlib.Path(a) for a in sys.argv[1:4])
MODERN_SIZES = (32, 48, 64, 96)

# xfce: X name -> (png, size, hx, hy)
xf = {}
for line in (xfce / "mappings").read_text().splitlines():
    if "-->" not in line: continue
    xname, src = (s.strip() for s in line.split("-->"))
    size, hx, hy, png = (xfce / "cfg" / f"{src}.cfg").read_text().split()[:4]
    xf[xname] = (xfce / "res" / png, int(size), int(hx), int(hy))

# modernXP: X name -> base; base -> {size: (hx, hy)}
md_base = {p.stem: p.stem for p in (modern / "config").glob("*.cursor")}
for line in (modern / "cursorList").read_text().splitlines():
    parts = line.split()
    if len(parts) == 2 and parts[1] in md_base: md_base.setdefault(parts[0], parts[1])
md_hot = {}   # base -> {size: (hx, hy)}, hotspots scaled from the smallest size upstream provides
for p in (modern / "config").glob("*.cursor"):
    given = {int(s): (int(x), int(y)) for s, x, y in (l.split()[:3] for l in p.read_text().splitlines() if l.strip())}
    ref = min(given); rx, ry = given[ref]
    md_hot[p.stem] = {s: given.get(s, (round(rx * s / ref), round(ry * s / ref))) for s in MODERN_SIZES}

tmp = pathlib.Path(tempfile.mkdtemp(prefix="xp-cursors-"))
def render(base, size):
    png = tmp / f"{base}-{size}.png"
    if not png.exists():
        subprocess.run(["resvg", "--width", str(size), "--height", str(size), modern / "svg" / f"{base}.svg", png], check=True)
    return png

cur, scal = out / "cursors", out / "cursors_scalable"
shutil.rmtree(cur, ignore_errors=True); shutil.rmtree(scal, ignore_errors=True)
cur.mkdir(parents=True); scal.mkdir()
built = {"authentic+svg": 0, "authentic": 0, "svg": 0}
for xname in sorted(set(xf) | set(md_base)):
    frames = []
    if xname in xf:
        png, size, hx, hy = xf[xname]; frames.append((size, hx, hy, png))
    base = md_base.get(xname)
    if base and not (modern / "svg" / f"{base}.svg").exists():   # a few upstream configs have no artwork of their own
        alt = {"left_ptr": "default", "watch": "wait", "left": "left-arrow"}.get(base, base.replace("_", "-"))
        if (modern / "svg" / f"{alt}.svg").exists(): md_hot[alt] = md_hot[base]; base = alt
        else: base = None
    if base:
        for size in MODERN_SIZES:
            if size == 32 and xname in xf: continue   # keep the genuine 32px pixels
            hx, hy = md_hot[base][size]; frames.append((size, hx, hy, render(base, size)))
        d = scal / xname; d.mkdir(); shutil.copyfile(modern / "svg" / f"{base}.svg", d / f"{base}.svg")
        hx, hy = md_hot[base][32]
        (d / "metadata.json").write_text(json.dumps([{"filename": f"{base}.svg", "hotspot_x": hx, "hotspot_y": hy, "nominal_size": 32}], indent=4) + "\n")
    if not frames: continue   # nothing from either source
    cfg = tmp / f"{xname}.cfg"
    cfg.write_text("".join(f"{s} {x} {y} {p}\n" for s, x, y, p in sorted(frames)))
    subprocess.run(["xcursorgen", cfg, cur / xname], check=True)
    built["authentic+svg" if xname in xf and base else "authentic" if xname in xf else "svg"] += 1
shutil.rmtree(tmp)
print(f"{out.name}: {sum(built.values())} cursors ({built}), {len(list(scal.iterdir()))} scalable")
