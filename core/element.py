from dataclasses import dataclass, field
from typing import Any
import uuid


ELEMENT_TYPES = {
    "item":    {"label": "Item",      "icon": "⚔️",  "color": "#7ec850", "desc": "Armas, ferramentas, comidas e itens gerais"},
    "block":   {"label": "Bloco",     "icon": "🧱",  "color": "#f0a020", "desc": "Blocos colocáveis no mundo"},
    "mob":     {"label": "Mob",       "icon": "👾",  "color": "#e04040", "desc": "Criaturas, monstros e animais"},
    "recipe":  {"label": "Receita",   "icon": "📜",  "color": "#4a9af0", "desc": "Receitas de crafting e smelting"},
    "biome":   {"label": "Bioma",     "icon": "🌍",  "color": "#20c0a0", "desc": "Biomas personalizados"},
    "enchant": {"label": "Encanto",   "icon": "✨",  "color": "#c060f0", "desc": "Encantamentos para itens"},
    "potion":  {"label": "Poção",     "icon": "🧪",  "color": "#20a0e0", "desc": "Efeitos e poções customizadas"},
    "command": {"label": "Comando",   "icon": "📟",  "color": "#aaaaaa", "desc": "Blocos de comando e eventos"},
}


def default_props(etype: str) -> dict:
    base = {"max_stack": 64}
    if etype == "item":
        return {**base, "damage": 1.0, "durability": 0, "rarity": "common",
                "enchantable": True, "fireproof": False, "food": False,
                "food_nutrition": 0, "food_saturation": 0.0}
    if etype == "block":
        return {**base, "hardness": 1.5, "resistance": 6.0, "flammable": False,
                "transparent": False, "luminance": 0, "tool": "pickaxe",
                "tool_level": "wood", "drops": "self", "gravity": False}
    if etype == "mob":
        return {"hp": 20.0, "armor": 0.0, "damage": 3.0, "speed": 0.35,
                "follow_range": 16.0, "hostile": False, "flying": False,
                "tameable": False, "fire_immune": False, "xp_drop": 5}
    if etype == "recipe":
        return {"recipe_type": "crafting_shaped", "result_count": 1,
                "ingredients": {}, "pattern": ["   ", "   ", "   "]}
    if etype == "enchant":
        return {"max_level": 3, "rarity": "common", "compatible_items": ["weapon"],
                "treasure": False, "curse": False}
    if etype == "potion":
        return {"duration": 200, "amplifier": 0, "effect": "speed",
                "color": "#FF8800", "instant": False}
    return base


@dataclass
class ModElement:
    etype: str
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    registry_name: str = ""
    description: str = ""
    props: dict = field(default_factory=dict)
    tags: list = field(default_factory=list)

    def __post_init__(self):
        if not self.registry_name:
            self.registry_name = self.name.lower().replace(" ", "_")
        if not self.props:
            self.props = default_props(self.etype)

    @property
    def icon(self):
        return ELEMENT_TYPES.get(self.etype, {}).get("icon", "📦")

    @property
    def color(self):
        return ELEMENT_TYPES.get(self.etype, {}).get("color", "#aaaaaa")

    @property
    def type_label(self):
        return ELEMENT_TYPES.get(self.etype, {}).get("label", self.etype.upper())

    def to_dict(self):
        return {
            "id": self.id,
            "etype": self.etype,
            "name": self.name,
            "registry_name": self.registry_name,
            "description": self.description,
            "props": self.props,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            etype=data["etype"],
            name=data["name"],
            id=data.get("id", str(uuid.uuid4())[:8]),
            registry_name=data.get("registry_name", ""),
            description=data.get("description", ""),
            props=data.get("props", {}),
            tags=data.get("tags", []),
        )
