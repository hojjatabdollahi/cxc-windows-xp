# Windows XP for COSMIC

A COSMIC theme bundle: Luna Blue colours, Tahoma, Bliss and an XP icon theme.
Grab `windows-xp.zip` from the [latest release](https://github.com/hojjatabdollahi/cxc-windows-xp/releases/latest)
and import it in Settings → Desktop → Appearance.

## Firefox

A matching Firefox theme that also colours the sidebar, so vertical tabs stay readable:

```
firefox https://github.com/hojjatabdollahi/cxc-windows-xp/releases/latest/download/windows-xp-firefox.xpi
```

The XPI is unsigned. It installs on builds that do not enforce add-on signing, such as the
Pop!_OS package; Mozilla's own release builds will refuse it until it is signed through AMO.
Source is in `firefox/`.
