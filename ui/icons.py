"""
Centralized icon management — qtawesome (Font Awesome 5).
All functions return QIcon. Failures return empty QIcon silently.
"""
_cache: dict = {}

def _ic(name: str, color: str = "#909090"):
    key = f"{name}:{color}"
    if key not in _cache:
        try:
            import qtawesome as qta
            _cache[key] = qta.icon(name, color=color)
        except Exception:
            from PyQt6.QtGui import QIcon
            _cache[key] = QIcon()
    return _cache[key]

# ── Toolbar ────────────────────────────────────────────────────────────────
def toolbar_open():           return _ic("fa5s.folder-open",    "#909090")
def toolbar_save():           return _ic("fa5s.save",           "#909090")
def toolbar_new_element():    return _ic("fa5s.plus-circle",    "#6ab84a")
def toolbar_build():          return _ic("fa5s.hammer",         "#c89040")
def toolbar_export():         return _ic("fa5s.box-open",       "#5880c8")
def toolbar_settings():       return _ic("fa5s.cog",            "#707070")

# ── Menu — Arquivo ─────────────────────────────────────────────────────────
def menu_new():               return _ic("fa5s.file",           "#909090")
def menu_open():              return _ic("fa5s.folder-open",    "#909090")
def menu_save():              return _ic("fa5s.save",           "#909090")
def menu_save_as():           return _ic("fa5s.save",           "#707070")
def menu_back():              return _ic("fa5s.arrow-left",     "#707070")
def menu_quit():              return _ic("fa5s.sign-out-alt",   "#c04040")

# ── Menu — Editar ──────────────────────────────────────────────────────────
def menu_new_element():       return _ic("fa5s.plus",           "#6ab84a")
def menu_preferences():       return _ic("fa5s.sliders-h",     "#909090")

# ── Menu — Build ───────────────────────────────────────────────────────────
def menu_build():             return _ic("fa5s.hammer",         "#c89040")
def menu_export_struct():     return _ic("fa5s.file-archive",   "#5880c8")
def menu_export_java():       return _ic("fa5s.coffee",         "#c89040")
def menu_export_json():       return _ic("fa5s.file-code",      "#707070")

# ── Menu — Ferramentas ─────────────────────────────────────────────────────
def menu_validate():          return _ic("fa5s.search",         "#909090")
def menu_plugins():           return _ic("fa5s.plug",           "#909090")

# ── Menu — Ajuda ───────────────────────────────────────────────────────────
def menu_docs():              return _ic("fa5s.book",           "#909090")
def menu_about():             return _ic("fa5s.info-circle",    "#909090")

# ── Tabs ───────────────────────────────────────────────────────────────────
def tab_workspace():          return _ic("fa5s.th-large",       "#909090")
def tab_pixel_art():          return _ic("fa5s.paint-brush",    "#909090")
def tab_recipe():             return _ic("fa5s.utensils",       "#909090")

# ── Element types ───────────────────────────────────────────────────────────
def el_item():                return _ic("fa5s.fist-raised",    "#6ab84a")
def el_block():               return _ic("fa5s.cube",           "#c89040")
def el_mob():                 return _ic("fa5s.skull",          "#c04040")
def el_recipe():              return _ic("fa5s.scroll",         "#5880c8")
def el_biome():               return _ic("fa5s.mountain",       "#20c0a0")
def el_enchant():             return _ic("fa5s.magic",          "#c060f0")
def el_potion():              return _ic("fa5s.flask",          "#20a0e0")
def el_command():             return _ic("fa5s.terminal",       "#aaaaaa")

def el_icon(etype: str):
    return {
        "item":    el_item,
        "block":   el_block,
        "mob":     el_mob,
        "recipe":  el_recipe,
        "biome":   el_biome,
        "enchant": el_enchant,
        "potion":  el_potion,
        "command": el_command,
    }.get(etype, lambda: _ic("fa5s.cube", "#707070"))()

# ── Settings sidebar ────────────────────────────────────────────────────────
def settings_appearance():    return _ic("fa5s.palette",        "#909090")
def settings_language():      return _ic("fa5s.globe",          "#909090")
def settings_projects():      return _ic("fa5s.folder",         "#909090")
def settings_discord():       return _ic("fa5b.discord",        "#909090")

# ── Misc ────────────────────────────────────────────────────────────────────
def delete():                 return _ic("fa5s.trash-alt",      "#c04040")
def warning():                return _ic("fa5s.exclamation-triangle", "#c89040")
def error_ic():               return _ic("fa5s.times-circle",   "#c04040")
def info_ic():                return _ic("fa5s.info-circle",    "#5880c8")
def success():                return _ic("fa5s.check-circle",   "#6ab84a")
def undo():                   return _ic("fa5s.undo",           "#909090")
def clear():                  return _ic("fa5s.eraser",         "#909090")
def export_png():             return _ic("fa5s.file-image",     "#6ab84a")
