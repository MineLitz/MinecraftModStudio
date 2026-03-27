from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QSpinBox, QLineEdit, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent


RECIPE_TYPES = [
    ("crafting_shaped",     "Crafting (Formato)"),
    ("crafting_shapeless",  "Crafting (Sem Formato)"),
    ("smelting",            "Fornalha (Smelting)"),
    ("blasting",            "Alto-Forno (Blasting)"),
    ("smoking",             "Fumeiro (Smoking)"),
    ("campfire_cooking",    "Fogueira"),
]

INGREDIENT_EMOJIS = {
    "": "", "air": "🌫️",
    "oak_log": "🪵", "stone": "🪨", "iron_ingot": "⚙️",
    "gold_ingot": "🥇", "diamond": "💎", "stick": "🪄",
    "planks": "🟫", "cobblestone": "🪨", "sand": "🟡",
    "gravel": "⬜", "coal": "🔲", "redstone": "🔴",
    "lapis": "🔵", "emerald": "💚", "netherite": "🔮",
    "custom": "📦",
}


class CraftCell(QFrame):
    clicked = pyqtSignal(int)

    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.ingredient = ""
        self.setFixedSize(56, 56)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build()
        self._update()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self._lbl = QLabel("")
        self._lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl.setFont(QFont("Segoe UI Emoji", 22))
        self._lbl.setStyleSheet("background:transparent; border:none;")
        lay.addWidget(self._lbl)

    def _update(self):
        emoji = INGREDIENT_EMOJIS.get(self.ingredient, "📦") if self.ingredient else ""
        self._lbl.setText(emoji)
        filled = bool(self.ingredient)
        self.setStyleSheet(f"""
            QFrame {{
                background: {'#1a2a10' if filled else '#1e1e1e'};
                border: {'2px solid #4a7a20' if filled else '1px solid #333'};
                border-radius: 5px;
            }}
            QFrame:hover {{
                background: #252525;
                border-color: #4a4a4a;
            }}
        """)

    def set_ingredient(self, ing: str):
        self.ingredient = ing
        self._update()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.index)
        elif e.button() == Qt.MouseButton.RightButton:
            self.set_ingredient("")


class RecipeEditor(QWidget):
    recipe_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cells: list[CraftCell] = []
        self._element = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        # Recipe type selector
        type_row = QHBoxLayout()
        type_row.setSpacing(10)
        type_lbl = QLabel("Tipo de receita:")
        type_lbl.setStyleSheet("color:#a0a0a0; font-size:12px;")
        self._type_combo = QComboBox()
        for value, label in RECIPE_TYPES:
            self._type_combo.addItem(label, value)
        self._type_combo.setFixedWidth(220)
        self._type_combo.currentIndexChanged.connect(self._on_type_change)
        type_row.addWidget(type_lbl)
        type_row.addWidget(self._type_combo)
        type_row.addStretch()
        root.addLayout(type_row)

        # Main area
        main_row = QHBoxLayout()
        main_row.setSpacing(24)

        # Crafting grid
        grid_col = QVBoxLayout()
        grid_col.setSpacing(8)
        grid_lbl = QLabel("GRADE DE CRAFTING")
        grid_lbl.setStyleSheet("color:#505050; font-size:10px; font-weight:bold; letter-spacing:1px;")
        grid_col.addWidget(grid_lbl)

        self._grid_frame = QFrame()
        self._grid_frame.setStyleSheet("background:#181818; border:1px solid #2a2a2a; border-radius:6px;")
        self._grid_frame.setFixedSize(200, 200)
        g = QGridLayout(self._grid_frame)
        g.setContentsMargins(12, 12, 12, 12)
        g.setSpacing(8)

        for i in range(9):
            cell = CraftCell(i)
            cell.clicked.connect(self._on_cell_click)
            self._cells.append(cell)
            g.addWidget(cell, i // 3, i % 3)

        grid_col.addWidget(self._grid_frame)

        # Clear all button
        clear_btn = QPushButton("Limpar Grade")
        clear_btn.setFixedHeight(28)
        clear_btn.clicked.connect(self._clear_grid)
        grid_col.addWidget(clear_btn)
        grid_col.addStretch()

        main_row.addLayout(grid_col)

        # Arrow
        arr = QLabel("→")
        arr.setStyleSheet("color:#404040; font-size:28px;")
        arr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_row.addWidget(arr)

        # Result + ingredient picker
        right_col = QVBoxLayout()
        right_col.setSpacing(10)

        result_lbl = QLabel("RESULTADO")
        result_lbl.setStyleSheet("color:#505050; font-size:10px; font-weight:bold; letter-spacing:1px;")
        right_col.addWidget(result_lbl)

        self._result_cell = CraftCell(-1)
        self._result_cell.setStyleSheet("""
            QFrame {
                background: #1e1e1e;
                border: 2px solid #c89040;
                border-radius: 5px;
            }
        """)
        right_col.addWidget(self._result_cell)

        count_row = QHBoxLayout()
        count_row.setSpacing(8)
        count_lbl = QLabel("Quantidade:")
        count_lbl.setStyleSheet("color:#888; font-size:11px;")
        self._count_spin = QSpinBox()
        self._count_spin.setRange(1, 64)
        self._count_spin.setValue(1)
        self._count_spin.setFixedWidth(70)
        self._count_spin.valueChanged.connect(self._emit_change)
        count_row.addWidget(count_lbl)
        count_row.addWidget(self._count_spin)
        count_row.addStretch()
        right_col.addLayout(count_row)

        right_col.addSpacing(10)

        # Ingredient picker
        ing_lbl = QLabel("ADICIONAR INGREDIENTE")
        ing_lbl.setStyleSheet("color:#505050; font-size:10px; font-weight:bold; letter-spacing:1px;")
        right_col.addWidget(ing_lbl)

        ing_hint = QLabel("Clique em uma célula da grade\ndepois escolha o ingrediente abaixo")
        ing_hint.setStyleSheet("color:#404040; font-size:10px; font-style:italic;")
        right_col.addWidget(ing_hint)

        self._ing_combo = QComboBox()
        for key, emoji in INGREDIENT_EMOJIS.items():
            if key:
                self._ing_combo.addItem(f"{emoji}  {key}", key)
        self._ing_combo.setFixedWidth(200)
        right_col.addWidget(self._ing_combo)

        set_btn = QPushButton("Definir Ingrediente")
        set_btn.setObjectName("btn_primary")
        set_btn.setFixedHeight(32)
        set_btn.clicked.connect(self._set_selected_ingredient)
        right_col.addWidget(set_btn)

        right_col.addStretch()

        result_item_lbl = QLabel("ITEM RESULTADO (ID)")
        result_item_lbl.setStyleSheet("color:#505050; font-size:10px; font-weight:bold; letter-spacing:1px;")
        right_col.addWidget(result_item_lbl)

        self._result_input = QLineEdit()
        self._result_input.setPlaceholderText("Ex: espada_obsidiana")
        self._result_input.setFixedWidth(200)
        self._result_input.textChanged.connect(self._on_result_change)
        right_col.addWidget(self._result_input)

        main_row.addLayout(right_col)
        main_row.addStretch()
        root.addLayout(main_row)

        self._selected_cell_idx = None

    def _on_cell_click(self, idx: int):
        self._selected_cell_idx = idx
        for i, cell in enumerate(self._cells):
            if i == idx:
                cell.setStyleSheet(cell.styleSheet().replace("border-color: #4a4a4a", "border-color: #6ab84a"))
                cell.setStyleSheet("background:#1e3010; border:2px solid #6ab84a; border-radius:5px;")

    def _set_selected_ingredient(self):
        if self._selected_cell_idx is None:
            return
        ing = self._ing_combo.currentData()
        self._cells[self._selected_cell_idx].set_ingredient(ing)
        self._selected_cell_idx = None
        self._emit_change()

    def _on_type_change(self):
        is_crafting = "crafting" in (self._type_combo.currentData() or "")
        self._grid_frame.setVisible(is_crafting)
        self._emit_change()

    def _on_result_change(self, text: str):
        self._result_cell.set_ingredient("custom" if text.strip() else "")
        self._emit_change()

    def _clear_grid(self):
        for cell in self._cells:
            cell.set_ingredient("")
        self._emit_change()

    def _emit_change(self):
        data = self.get_data()
        self.recipe_changed.emit(data)

    def get_data(self) -> dict:
        return {
            "recipe_type": self._type_combo.currentData() or "crafting_shaped",
            "ingredients": {str(i): c.ingredient for i, c in enumerate(self._cells) if c.ingredient},
            "result_item": self._result_input.text().strip(),
            "result_count": self._count_spin.value(),
        }

    def load_element(self, element):
        self._element = element
        p = element.props
        # Restore recipe type
        rtype = p.get("recipe_type", "crafting_shaped")
        for i in range(self._type_combo.count()):
            if self._type_combo.itemData(i) == rtype:
                self._type_combo.setCurrentIndex(i)
                break
        # Restore ingredients
        ingredients = p.get("ingredients", {})
        for i, cell in enumerate(self._cells):
            cell.set_ingredient(ingredients.get(str(i), ""))
        # Restore result
        self._result_input.setText(p.get("result_item", ""))
        self._count_spin.setValue(p.get("result_count", 1))
