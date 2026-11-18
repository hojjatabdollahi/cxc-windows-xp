#!/usr/bin/env python3
"""Copy icons the XP theme already has to the names COSMIC asks for.

COSMIC's apps use their own icon names, and libcosmic checks the Cosmic theme
before it tries anything else, so without these copies COSMIC's icons show up
instead. Rasters are copied at every size the source has; image handles are
not recoloured, so they keep their colours. The monochrome SVGs in tools/icons
go to scalable/actions next to the window buttons. Run it again after
changing the icon theme.
"""
import shutil
from pathlib import Path

RASTER = {
    "camera-video-symbolic": "camera-video",
    "format-justify-left-symbolic": "format-justify-left",
    "format-justify-right-symbolic": "format-justify-right",
    "format-justify-center-symbolic": "format-justify-fill",
    "format-text-bold-symbolic": "format-text-bold",
    "format-text-italic-symbolic": "format-text-italic",
    "format-text-underline-symbolic": "format-text-underline",
    "folder-new-symbolic": "folder-new",
    "preferences-other-symbolic": "preferences-other",
    "tablet-symbolic": "tablet",
    "speaker-symbolic": "audio-speakers-symbolic",
    "application-default": "application-x-executable",
    "applications-accessibility-symbolic": "preferences-desktop-accessibility-symbolic",
    "airplane-mode-disabled-symbolic": "airplane-mode-symbolic",
    "window-stack-symbolic": "window-new",
    "window-swap-symbolic": "preferences-window-management-symbolic",
    "view-fit-symbolic": "zoom-fit-best-symbolic",
    "view-actual-size-symbolic": "zoom-original",
    "object-rotate-left-symbolic": "edit-undo",
    "object-rotate-right-symbolic": "edit-redo",
    "insert-drawing-symbolic": "x-office-drawing-symbolic",
    "checkbox-checked-symbolic": "checkbox",
    # XP's Display Properties icon for the Desktop page; Displays keeps the plain monitor
    "video-display-symbolic": "preferences-desktop",
}
# Second names for SVGs already in scalable/actions (drawn ones included).
SVG_ALIASES = {
    "application-menu-symbolic": "open-menu-symbolic",
    "emblem-ok-symbolic": "object-select-symbolic",
    "view-sort-ascending-symbolic": "pan-up-symbolic",
    "view-sort-descending-symbolic": "pan-down-symbolic",
}

for theme in sorted((Path(__file__).resolve().parent.parent / "data/icons").glob("*.icons")):
    copies = 0
    for alias, source in RASTER.items():
        # <size>/<context>/<name>.png only; B00merang left a few stray subfolders
        hits = [p for p in theme.rglob(f"{source}.png") if len(p.relative_to(theme).parts) == 3]
        assert hits, f"{theme.name}: no {source}.png"
        # Drop earlier copies first, so a renamed source leaves no stale sizes behind
        for old in theme.rglob(f"{alias}.png"):
            if len(old.relative_to(theme).parts) == 3:
                old.unlink()
        for p in hits:
            shutil.copyfile(p, p.with_name(f"{alias}.png"))
            copies += 1
    scalable = theme / "scalable/actions"
    drawn = sorted((Path(__file__).resolve().parent / "icons").glob("*.svg"))
    for icon in drawn:
        shutil.copyfile(icon, scalable / icon.name)
    for alias, source in SVG_ALIASES.items():
        shutil.copyfile(scalable / f"{source}.svg", scalable / f"{alias}.svg")
    print(f"{theme.name}: {copies} raster copies for {len(RASTER)} names, {len(drawn)} drawn, {len(SVG_ALIASES)} svg aliases")
