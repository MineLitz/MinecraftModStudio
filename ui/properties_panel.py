from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox,
    QDoubleSpinBox, QSpinBox, QCheckBox, QScrollArea,
    QFrame, QHBoxLayout, QTextEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from core.element import ModElement


class PropSection(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 8)
        self.content_layout.setSpacing(4)

        lbl = QLabel(title.upper())
        lbl.setStyleSheet("""
            color: #666; font-size: 10px; letter-spacing: 1px;
            font-weight: bold; padding: 8px 10px 4px;
            border-bottom: 1px solid #2a2a2a;
            background: #1a1a1a;
        """)
        layout.addWidget(lbl)
        layout.addWidget(self.content)

    def add_row(self, label: str, widget: QWidget):
        row = QHBoxLayout()
        row.setContentsMargins(10, 3, 10, 3)
        row.setSpacing(8)
        lbl = QLabel(label)
        lbl.setFixedWidth(88)
        lbl.setStyleSheet("color: #888; font-size: 11px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(lbl)
        row.addWidget(widget)
        container = QWidget()
        container.setLayout(row)
        self.content_layout.addWidget(container)
        return widget


class PropertiesPanel(QWidget):
    element_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_element: ModElement | None = None
        self._widgets: dict = {}
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("background: #222; border-bottom: 1px solid #333;")
        header.setFixedHeight(36)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(10, 0, 10, 0)
        self.header_lbl = QLabel("PROPRIEDADES")
        self.header_lbl.setStyleSheet("color: #666; font-size: 10px; letter-spacing: 1px; font-weight: bold;")
        h_lay.addWidget(self.header_lbl)
        outer.addWidget(header)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.content_layout.addStretch()
        scroll.setWidget(self.content)

        # Empty state
        self.empty_lbl = QLabel("Selecione um elemento\npara ver suas propriedades")
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_lbl.setStyleSheet("color: #444; font-size: 12px; padding: 40px;")
        self.empty_lbl.setWordWrap(True)
        self.content_layout.insertWidget(0, self.empty_lbl)

    def load_element(self, element: ModElement):
        self.current_element = element
        self._clear()
        self.header_lbl.setText(f"{element.icon}  {element.name.upper()[:22]}")
        self.header_lbl.setStyleSheet(f"color: {element.color}; font-size: 10px; letter-spacing: 1px; font-weight: bold;")
        self.empty_lbl.hide()

        # General section
        gen = PropSection("Geral")
        self._add_text(gen, "name", "Nome", element.name)
        self._add_text(gen, "registry_name", "Registry ID", element.registry_name)
        self._insert_section(gen)

        # Type-specific
        if element.etype == "item":
            self._build_item_props(element)
        elif element.etype == "block":
            self._build_block_props(element)
        elif element.etype == "mob":
            self._build_mob_props(element)
        elif element.etype == "recipe":
            self._build_recipe_props(element)
        elif element.etype == "enchant":
            self._build_enchant_props(element)
        elif element.etype == "potion":
            self._build_potion_props(element)

    def _build_item_props(self, el: ModElement):
        sec = PropSection("Atributos do Item")
        p = el.props
        self._add_double(sec, "damage", "Dano", p.get("damage", 1.0), 0, 2000)
        self._add_int(sec, "durability", "Durabilidade", p.get("durability", 0), 0, 10000)
        self._add_int(sec, "max_stack", "Stack Máx.", p.get("max_stack", 64), 1, 64)
        self._add_combo(sec, "rarity", "Raridade", ["common", "uncommon", "rare", "epic"], p.get("rarity", "common"))
        self._add_check(sec, "enchantable", "Encantável", p.get("enchantable", True))
        self._add_check(sec, "fireproof", "Resistente ao fogo", p.get("fireproof", False))
        self._add_check(sec, "food", "É comida", p.get("food", False))
        self._insert_section(sec)

        food = PropSection("Comida (se ativado)")
        self._add_int(food, "food_nutrition", "Nutrição", p.get("food_nutrition", 0), 0, 20)
        self._add_double(food, "food_saturation", "Saturação", p.get("food_saturation", 0.0), 0.0, 10.0)
        self._insert_section(food)

    def _build_block_props(self, el: ModElement):
        sec = PropSection("Atributos do Bloco")
        p = el.props
        self._add_double(sec, "hardness", "Dureza", p.get("hardness", 1.5), -1, 50)
        self._add_double(sec, "resistance", "Resistência", p.get("resistance", 6.0), 0, 999)
        self._add_int(sec, "luminance", "Luminosidade", p.get("luminance", 0), 0, 15)
        self._add_combo(sec, "tool", "Ferramenta", ["pickaxe", "axe", "shovel", "hoe", "hand"], p.get("tool", "pickaxe"))
        self._add_combo(sec, "tool_level", "Nível", ["wood", "stone", "iron", "diamond", "netherite"], p.get("tool_level", "wood"))
        self._add_check(sec, "flammable", "Inflamável", p.get("flammable", False))
        self._add_check(sec, "transparent", "Transparente", p.get("transparent", False))
        self._add_check(sec, "gravity", "Afetado por gravidade", p.get("gravity", False))
        self._insert_section(sec)

    def _build_mob_props(self, el: ModElement):
        sec = PropSection("Atributos do Mob")
        p = el.props
        self._add_double(sec, "hp", "HP", p.get("hp", 20.0), 1, 2000)
        self._add_double(sec, "armor", "Armadura", p.get("armor", 0.0), 0, 30)
        self._add_double(sec, "damage", "Dano", p.get("damage", 3.0), 0, 100)
        self._add_double(sec, "speed", "Velocidade", p.get("speed", 0.35), 0, 2)
        self._add_double(sec, "follow_range", "Alcance", p.get("follow_range", 16.0), 0, 64)
        self._add_int(sec, "xp_drop", "XP Dropado", p.get("xp_drop", 5), 0, 1000)
        self._add_check(sec, "hostile", "Hostil (ataca jogador)", p.get("hostile", False))
        self._add_check(sec, "flying", "Voa", p.get("flying", False))
        self._add_check(sec, "tameable", "Domesticável", p.get("tameable", False))
        self._add_check(sec, "fire_immune", "Imune ao fogo", p.get("fire_immune", False))
        self._insert_section(sec)

    def _build_recipe_props(self, el: ModElement):
        sec = PropSection("Receita")
        p = el.props
        self._add_combo(sec, "recipe_type", "Tipo", [
            "crafting_shaped", "crafting_shapeless", "smelting", "blasting", "smoking", "campfire_cooking"
        ], p.get("recipe_type", "crafting_shaped"))
        self._add_text(sec, "result_item", "Item Resultado", p.get("result_item", ""))
        self._add_int(sec, "result_count", "Quantidade", p.get("result_count", 1), 1, 64)
        self._insert_section(sec)

    def _build_enchant_props(self, el: ModElement):
        sec = PropSection("Encantamento")
        p = el.props
        self._add_int(sec, "max_level", "Nível Máximo", p.get("max_level", 3), 1, 10)
        self._add_combo(sec, "rarity", "Raridade", ["common", "uncommon", "rare", "very_rare"], p.get("rarity", "common"))
        self._add_check(sec, "treasure", "Tesouro", p.get("treasure", False))
        self._add_check(sec, "curse", "Maldição", p.get("curse", False))
        self._insert_section(sec)

    def _build_potion_props(self, el: ModElement):
        sec = PropSection("Poção / Efeito")
        p = el.props
        effects = ["speed", "slowness", "haste", "mining_fatigue", "strength", "weakness",
                   "instant_health", "instant_damage", "jump_boost", "nausea", "regeneration",
                   "resistance", "fire_resistance", "water_breathing", "invisibility",
                   "blindness", "night_vision", "hunger", "poison", "wither", "levitation"]
        self._add_combo(sec, "effect", "Efeito", effects, p.get("effect", "speed"))
        self._add_int(sec, "duration", "Duração (ticks)", p.get("duration", 200), 1, 100000)
        self._add_int(sec, "amplifier", "Amplificador", p.get("amplifier", 0), 0, 255)
        self._add_check(sec, "instant", "Instantâneo", p.get("instant", False))
        self._insert_section(sec)

    # ── Widget helpers ────────────────────────────────────────────────────────
    def _add_text(self, sec, key, label, value):
        w = QLineEdit(str(value))
        w.setMinimumHeight(28)
        w.textChanged.connect(lambda v, k=key: self._on_change(k, v))
        self._widgets[key] = w
        return sec.add_row(label, w)

    def _add_int(self, sec, key, label, value, min_v=0, max_v=9999):
        w = QSpinBox()
        w.setRange(min_v, max_v)
        w.setValue(int(value))
        w.setMinimumHeight(28)
        w.valueChanged.connect(lambda v, k=key: self._on_change(k, v))
        self._widgets[key] = w
        return sec.add_row(label, w)

    def _add_double(self, sec, key, label, value, min_v=0.0, max_v=9999.0):
        w = QDoubleSpinBox()
        w.setRange(min_v, max_v)
        w.setValue(float(value))
        w.setSingleStep(0.1)
        w.setMinimumHeight(28)
        w.valueChanged.connect(lambda v, k=key: self._on_change(k, v))
        self._widgets[key] = w
        return sec.add_row(label, w)

    def _add_combo(self, sec, key, label, options, value):
        w = QComboBox()
        w.addItems(options)
        if value in options:
            w.setCurrentText(value)
        w.setMinimumHeight(28)
        w.currentTextChanged.connect(lambda v, k=key: self._on_change(k, v))
        self._widgets[key] = w
        return sec.add_row(label, w)

    def _add_check(self, sec, key, label, value):
        w = QCheckBox("Sim")
        w.setChecked(bool(value))
        w.stateChanged.connect(lambda v, k=key: self._on_change(k, bool(v)))
        self._widgets[key] = w
        return sec.add_row(label, w)

    def _insert_section(self, sec):
        idx = self.content_layout.count() - 1  # before stretch
        self.content_layout.insertWidget(idx, sec)

    def _on_change(self, key: str, value):
        if not self.current_element:
            return
        if key == "name":
            self.current_element.name = value
            if "registry_name" in self._widgets:
                auto = value.lower().replace(" ", "_")
                self.current_element.registry_name = auto
                w = self._widgets["registry_name"]
                w.blockSignals(True)
                w.setText(auto)
                w.blockSignals(False)
        elif key == "registry_name":
            self.current_element.registry_name = value
        else:
            self.current_element.props[key] = value
        self.element_changed.emit()

    def _clear(self):
        self._widgets.clear()
        while self.content_layout.count() > 1:  # keep stretch
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.content_layout.insertWidget(0, self.empty_lbl)
        self.empty_lbl.show()
