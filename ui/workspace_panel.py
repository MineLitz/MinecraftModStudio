from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QGridLayout, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QPixmap, QImage
from core.element import ModElement, ELEMENT_TYPES


class TextureCard(QFrame):
    """Card for a modified texture in a Resource Pack project."""
    clicked = pyqtSignal(str)  # emits key "mc_folder/tex_name"

    def __init__(self, key: str, display_name: str, img: QImage, parent=None):
        super().__init__(parent)
        self.key          = key
        self.display_name = display_name
        self.selected     = False
        self.setFixedSize(130, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build(img)
        self._update_style()

    def _build(self, img: QImage):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 6)
        lay.setSpacing(4)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Texture preview
        self._img_lbl = QLabel()
        self._img_lbl.setFixedSize(64, 64)
        self._img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._img_lbl.setStyleSheet(
            "background:#141414;border:1px solid #2a2a2a;border-radius:4px;")
        self.update_image(img)
        lay.addWidget(self._img_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        # Name
        parts = self.key.split("/")
        short = parts[-1].replace("_", " ")
        name_lbl = QLabel(short[:16] + "…" if len(short) > 16 else short)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setStyleSheet(
            "background:transparent;border:none;font-size:10px;color:#aaa;")
        lay.addWidget(name_lbl)

        # Category badge
        cat = parts[0] if len(parts) > 1 else "texture"
        badge = QLabel(cat.upper())
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(
            "background:transparent;border:none;"
            "color:#6ab84a;font-size:8px;font-weight:bold;letter-spacing:0.5px;")
        lay.addWidget(badge)

    def update_image(self, img: QImage):
        px = QPixmap.fromImage(img).scaled(
            64, 64,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self._img_lbl.setPixmap(px)

    def set_selected(self, v: bool):
        self.selected = v
        self._update_style()

    def _update_style(self):
        if self.selected:
            self.setStyleSheet(
                "QFrame{background:#1a2a10;border:2px solid #6ab84a;border-radius:8px;}")
        else:
            self.setStyleSheet(
                "QFrame{background:#1e1e1e;border:1px solid #252525;border-radius:8px;}"
                "QFrame:hover{background:#222;border-color:#363636;}")

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.key)


class ElementCard(QFrame):
    clicked = pyqtSignal(str)
    double_clicked = pyqtSignal(str)
    delete_requested = pyqtSignal(str)

    def __init__(self, element: ModElement, parent=None):
        super().__init__(parent)
        self.element = element
        self.selected = False
        self.setFixedSize(130, 110)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build()
        self._update_style()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 10, 8, 8)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_lbl = QLabel(self.element.icon)
        self.icon_lbl.setFont(QFont("Segoe UI Emoji", 28))
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_lbl.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.icon_lbl)

        self.name_lbl = QLabel(self.element.name)
        self.name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_lbl.setWordWrap(True)
        self.name_lbl.setStyleSheet("background: transparent; border: none; font-size: 10px; color: #aaa;")
        layout.addWidget(self.name_lbl)

        # Badge
        badge = QLabel(self.element.type_label.upper())
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"""
            background: transparent;
            border: none;
            color: {self.element.color};
            font-size: 9px;
            font-weight: bold;
            letter-spacing: 1px;
        """)
        layout.addWidget(badge)

    def _update_style(self):
        color = self.element.color
        if self.selected:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: #1a2a12;
                    border: 2px solid {color};
                    border-radius: 8px;
                }}
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #222;
                    border: 1px solid #333;
                    border-radius: 8px;
                }
                QFrame:hover {
                    background-color: #282828;
                    border-color: #484848;
                }
            """)

    def set_selected(self, val: bool):
        self.selected = val
        self._update_style()

    def update_element(self, element: ModElement):
        self.element = element
        self.name_lbl.setText(element.name)
        self.icon_lbl.setText(element.icon)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.element.id)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.element.id)

    def contextMenuEvent(self, event):
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.addAction("✏️  Renomear").triggered.connect(
            lambda: self._rename())
        menu.addSeparator()
        menu.addAction("🗑️  Excluir").triggered.connect(
            lambda: self.delete_requested.emit(self.element.id))
        menu.exec(event.globalPos())

    def _rename(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Renomear", "Novo nome:", text=self.element.name)
        if ok and name.strip():
            self.element.name = name.strip()
            self.name_lbl.setText(name.strip())
            self.clicked.emit(self.element.id)


class WorkspacePanel(QWidget):
    element_selected     = pyqtSignal(object)
    element_deleted      = pyqtSignal(str)
    texture_card_clicked = pyqtSignal(str)  # key "mc_folder/tex_name"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards: dict[str, ElementCard] = {}
        self._tex_cards: dict[str, TextureCard] = {}
        self._rp_mode = False
        self.selected_id: str | None = None
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Filter bar
        filter_bar = QFrame()
        filter_bar.setStyleSheet("background: #1e1e1e; border-bottom: 1px solid #2a2a2a;")
        filter_bar.setFixedHeight(36)
        fb_lay = QHBoxLayout(filter_bar)
        fb_lay.setContentsMargins(12, 0, 12, 0)
        fb_lay.setSpacing(4)

        lbl = QLabel("WORKSPACE")
        lbl.setStyleSheet("color: #444; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
        fb_lay.addWidget(lbl)
        fb_lay.addStretch()

        self.filter_btns: dict[str, QPushButton] = {}
        for label, key in [("Todos", "all"), ("Itens", "item"), ("Blocos", "block"),
                            ("Mobs", "mob"), ("Receitas", "recipe")]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setFixedHeight(24)
            btn.setStyleSheet("""
                QPushButton { background: transparent; border: 1px solid transparent;
                    border-radius: 3px; color: #666; padding: 0 8px; font-size: 11px; }
                QPushButton:hover { color: #aaa; border-color: #444; }
                QPushButton:checked { background: #1e3010; border-color: #3a6a20; color: #7ec850; }
            """)
            btn.clicked.connect(lambda checked, k=key: self._filter(k))
            fb_lay.addWidget(btn)
            self.filter_btns[key] = btn
        self.filter_btns["all"].setChecked(True)
        outer.addWidget(filter_bar)

        # Scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(self.scroll)

        self.container = QWidget()
        self.container.setStyleSheet("background: #181818;")
        self.grid = QGridLayout(self.container)
        self.grid.setContentsMargins(16, 16, 16, 16)
        self.grid.setSpacing(12)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.scroll.setWidget(self.container)

        # Empty state — parented to container so Qt manages its lifetime
        self.empty_state = QLabel(
            "Nenhum elemento ainda\n\n"
            "Clique em  ➕ Novo Elemento  na barra de ferramentas\n"
            "para começar a criar seu mod",
            self.container
        )
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state.setStyleSheet("color: #333; font-size: 13px; padding: 60px;")
        self.empty_state.setWordWrap(True)
        self.empty_state.hide()

    def add_element(self, element: ModElement):
        card = ElementCard(element, self.container)
        card.clicked.connect(self._on_card_click)
        card.double_clicked.connect(self._on_card_dbl)
        card.delete_requested.connect(self._on_delete)
        self.cards[element.id] = card
        self._relayout()

    def add_texture_card(self, key: str, display_name: str, img: "QImage"):
        """Add or update a texture card for resource pack mode."""
        if key in self._tex_cards:
            self._tex_cards[key].update_image(img)
        else:
            card = TextureCard(key, display_name, img, self.container)
            card.clicked.connect(self.texture_card_clicked)
            self._tex_cards[key] = card
        self._relayout_textures()

    def clear_texture_cards(self):
        for card in self._tex_cards.values():
            card.deleteLater()
        self._tex_cards.clear()
        self._relayout_textures()

    def set_rp_mode(self, active: bool):
        """Switch between mod-element mode and resource-pack texture mode."""
        self._rp_mode = active
        # Show/hide filter bar (not needed for RP)
        for btn in self.filter_btns.values():
            btn.parentWidget().setVisible(not active)
        self._update_empty_state()
        if active:
            self._relayout_textures()
        else:
            self._relayout()

    def _update_empty_state(self):
        if self._rp_mode:
            self.empty_state.setText(
                "Nenhuma textura editada ainda\n\n"
                "Vá para a aba  🎨 Resource Pack,\n"
                "edite uma textura e clique  💾 Salvar no Projeto")
        else:
            self.empty_state.setText(
                "Nenhum elemento ainda\n\n"
                "Clique em  ➕ Novo Elemento  na barra de ferramentas\n"
                "para começar a criar seu mod")

    def remove_element(self, element_id: str):
        if element_id in self.cards:
            card = self.cards.pop(element_id)
            card.deleteLater()
        if self.selected_id == element_id:
            self.selected_id = None
        self._relayout()

    def update_element(self, element: ModElement):
        if element.id in self.cards:
            self.cards[element.id].update_element(element)

    def _relayout_textures(self):
        """Layout texture cards for resource pack mode."""
        while self.grid.count():
            self.grid.takeAt(0)

        if not self._tex_cards:
            self.empty_state.show()
            self.grid.addWidget(self.empty_state, 0, 0, 1, 5)
            return

        self.empty_state.hide()
        cols = max(1, max(self.scroll.viewport().width(), 148) // 148)
        for i, card in enumerate(self._tex_cards.values()):
            self.grid.addWidget(card, i // cols, i % cols)
            card.show()

    def _relayout(self):
        # Remove widgets from layout WITHOUT destroying them (no setParent)
        while self.grid.count():
            self.grid.takeAt(0)

        visible = [c for c in self.cards.values()
                   if self._current_filter in ("all", c.element.etype)]

        if not visible:
            self.empty_state.show()
            self.grid.addWidget(self.empty_state, 0, 0, 1, 5)
            for card in self.cards.values():
                card.hide()
            return

        self.empty_state.hide()
        cols = max(1, max(self.scroll.viewport().width(), 148) // 148)
        for i, card in enumerate(visible):
            self.grid.addWidget(card, i // cols, i % cols)
            card.show()
        for card in self.cards.values():
            if card not in visible:
                card.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._rp_mode:
            self._relayout_textures()
        else:
            self._relayout()

    @property
    def _current_filter(self):
        for k, btn in self.filter_btns.items():
            if btn.isChecked():
                return k
        return "all"

    def _filter(self, key: str):
        for k, btn in self.filter_btns.items():
            btn.setChecked(k == key)
        self._relayout()

    def _on_card_click(self, eid: str):
        if self.selected_id and self.selected_id in self.cards:
            self.cards[self.selected_id].set_selected(False)
        self.selected_id = eid
        if eid in self.cards:
            self.cards[eid].set_selected(True)
            self.element_selected.emit(self.cards[eid].element)

    def _on_card_dbl(self, eid: str):
        self._on_card_click(eid)

    def _on_delete(self, eid: str):
        from PyQt6.QtWidgets import QMessageBox
        name = self.cards[eid].element.name if eid in self.cards else "elemento"
        reply = QMessageBox.question(
            self, "Excluir Elemento",
            f"Deseja excluir '{name}'?\nEsta ação não pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.element_deleted.emit(eid)

    # ── Resource Pack texture cards ───────────────────────────────────────────
    def set_mode_resource_pack(self):
        """Switch workspace to resource pack mode — show textures instead of elements."""
        for btn in self.filter_btns.values():
            btn.hide()
        self.empty_state.setText(
            "Nenhuma textura modificada ainda\n\n"
            "Edite texturas na aba Resource Pack\n"
            "e clique 'Salvar no Projeto'")
        self._rp_mode = True
        self._tex_cards: dict[str, TextureCard] = {}

    def set_mode_mod(self):
        """Switch back to mod mode."""
        for btn in self.filter_btns.values():
            btn.show()
        self.empty_state.setText(
            "Nenhum elemento ainda\n\n"
            "Clique em  ➕ Novo Elemento  na barra de ferramentas\n"
            "para começar a criar seu mod")
        self._rp_mode = False

    def add_texture_card(self, key: str, display_name: str, img: QImage):
        """Add or update a texture card in RP mode."""
        if not hasattr(self, "_tex_cards"):
            self._tex_cards = {}
        if key in self._tex_cards:
            self._tex_cards[key].update_image(img)
        else:
            card = TextureCard(key, display_name, img, self.container)
            card.clicked.connect(self.texture_card_clicked)
            self._tex_cards[key] = card
        self._relayout_rp()

    def _relayout_rp(self):
        while self.grid.count():
            self.grid.takeAt(0)
        tex_cards = getattr(self, "_tex_cards", {})
        if not tex_cards:
            self.empty_state.show()
            self.grid.addWidget(self.empty_state, 0, 0, 1, 5)
            return
        self.empty_state.hide()
        cols = max(1, max(self.scroll.viewport().width(), 148) // 148)
        for i, card in enumerate(tex_cards.values()):
            self.grid.addWidget(card, i // cols, i % cols)
            card.show()

    texture_card_clicked = pyqtSignal(str)  # key
