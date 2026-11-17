#!/usr/bin/env python3
"""BraviaGlass 1.3.2: DOWN on home-screen dock does not open All Apps.

Small and intentionally strict overlay for the source archive in this repo.
Keeps existing profiles, layout, scenes, app selection and update handling intact.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
java = root / "app/src/main/java/com/usman/braviaglass"

def replace_once(filename, old, new):
    path = Path(filename)
    contents = path.read_text(encoding="utf-8")
    found = contents.count(old)
    if found != 1:
        raise SystemExit(f"Expected exactly one occurrence in {path}: {old!r}; found {found}")
    path.write_text(contents.replace(old, new, 1), encoding="utf-8")

# Primary scenic / Couch home screen: keep focus on currently selected dock item.
replace_once(
    java / "GlassView.java",
    "                if(down)open(Screen.APPS);",
    "                // DOWN from the home dock intentionally does nothing.\n"
    "                // All Apps remains accessible via its dedicated tile/settings."
)
# Alternate ambient/ColorHome appearance has its own D-pad navigation logic.
replace_once(
    java / "ColorHome.java",
    "        if(down)v.open(GlassView.Screen.APPS);",
    "        // DOWN from the ambient home dock intentionally does nothing."
)
# Remove outdated guidance that would imply the old shortcut still works.
replace_once(
    java / "ColorHome.java",
    "Вниз — все приложения · удерживайте OK, чтобы добавить на панель",
    "Все приложения — через настройки · удерживайте OK, чтобы добавить на панель"
)
gradle = root / "app/build.gradle"
replace_once(gradle, "versionCode 12", "versionCode 13")
replace_once(gradle, "versionName '1.3.1'", "versionName '1.3.2'")

# Verify the change is scoped: DOWN must still work inside All Apps/settings.
glass = (java / "GlassView.java").read_text(encoding="utf-8")
ambient = (java / "ColorHome.java").read_text(encoding="utf-8")
assert "if(down)open(Screen.APPS)" not in glass
assert "if(down)v.open(GlassView.Screen.APPS)" not in ambient
assert "if(down)gridIndex=" in glass
assert "if(down)settingIndex=" in glass
assert "else open(Screen.APPS);" in glass
assert "case \"allApps\":open(Screen.APPS);" in glass

print("BraviaGlass v1.3.2 patched: DOWN no-op on home dock; All Apps and settings preserved.")
