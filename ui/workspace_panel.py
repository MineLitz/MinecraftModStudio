from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QGridLayout, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor
from core.element import ModElement, ELEMENT_TYPES


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
    element_selected = pyqtSignal(object)
    element_deleted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards: dict[str, ElementCard] = {}
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

        # Empty state
        self.empty_state = QLabel(
            "Nenhum elemento ainda\n\n"
            "Clique em  ➕ Novo Elemento  na barra de ferramentas\n"
            "para começar a criar seu mod"
        )
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state.setStyleSheet("color: #333; font-size: 13px; padding: 60px;")
        self.empty_state.setWordWrap(True)

    def add_element(self, element: ModElement):
        card = ElementCard(element, self.container)
        card.clicked.connect(self._on_card_click)
        card.double_clicked.connect(self._on_card_dbl)
        card.delete_requested.connect(self._on_delete)
        self.cards[element.id] = card
        self._relayout()

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

    def _relayout(self):
        # Remove all from grid
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        visible = [c for c in self.cards.values()
                   if self._current_filter in ("all", c.element.etype)]

        if not visible:
            self.grid.addWidget(self.empty_state, 0, 0, 1, 5)
            self.empty_state.show()
            return

        self.empty_state.hide()
        cols = max(1, self.scroll.viewport().width() // 148)
        for i, card in enumerate(visible):
            self.grid.addWidget(card, i // cols, i % cols)
            card.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
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
