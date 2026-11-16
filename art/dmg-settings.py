# Configuración de dmgbuild para Wick.dmg (la usa build.sh --dmg)
import os
app = defines.get("app", "Wick.app")  # noqa: F821
here = os.path.dirname(os.path.abspath(app))
format = "ULFO"            # comprimido (LZFSE), macOS 10.11+
filesystem = "APFS"
files = [app]
symlinks = {"Applications": "/Applications"}
icon = os.path.join(here, "Resources", "AppIcon.icns")
background = os.path.join(here, "art", "dmg", "background.tiff")
window_rect = ((200, 160), (660, 400))
icon_size = 112
text_size = 13
show_status_bar = False
show_tab_view = False
show_toolbar = False
show_pathbar = False
show_sidebar = False
icon_locations = {"Wick.app": (170, 215), "Applications": (490, 215)}
