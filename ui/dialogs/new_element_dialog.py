from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGridLayout, QFrame, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.element import ELEMENT_TYPES


class ElementTypeCard(QFrame):
    def __init__(self, etype: str, info: dict, parent=None):
        super().__init__(parent)
        self.etype = etype
        self.selected = False
        self.setFixedSize(120, 100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build(info)
        self._update_style()

    def _build(self, info: dict):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 8)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_lbl = QLabel(info["icon"])
        icon_lbl.setFont(QFont("Segoe UI Emoji", 26))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("background: transparent;")
        layout.addWidget(icon_lbl)

        name_lbl = QLabel(info["label"])
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setStyleSheet("background: transparent; font-size: 11px; font-weight: bold;")
        layout.addWidget(name_lbl)

    def _update_style(self):
        if self.selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #1a3a10;
                    border: 2px solid #5aaa20;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #252525;
                    border: 1px solid #3a3a3a;
                    border-radius: 8px;
                }
                QFrame:hover {
                    background-color: #2d2d2d;
                    border-color: #4a4a4a;
                }
            """)

    def set_selected(self, val: bool):
        self.selected = val
        self._update_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent().parent().select_type(self.etype)


class NewElementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo Elemento")
        self.setFixedSize(560, 400)
        self.setModal(True)
        self.selected_type = None
        self.type_cards: dict[str, ElementTypeCard] = {}
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(14)

        title = QLabel("Escolha o Tipo de Elemento")
        title.setStyleSheet("color: #7ec850; font-size: 15px; font-weight: bold;")
        layout.addWidget(title)

        sub = QLabel("Selecione o que você quer criar no seu mod")
        sub.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(sub)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #333; max-height: 1px;")
        layout.addWidget(sep)

        # Type grid
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(10)
        grid.setContentsMargins(0, 0, 0, 0)

        for i, (etype, info) in enumerate(ELEMENT_TYPES.items()):
            card = ElementTypeCard(etype, info, grid_widget)
            self.type_cards[etype] = card
            grid.addWidget(card, i // 4, i % 4)

        layout.addWidget(grid_widget)

        # Description
        self.desc_label = QLabel("Selecione um tipo acima")
        self.desc_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)

        # Name input
        name_row = QHBoxLayout()
        name_label = QLabel("Nome:")
        name_label.setFixedWidth(50)
        name_label.setStyleSheet("color: #aaa; font-size: 12px;")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome do elemento...")
        self.name_input.setMinimumHeight(34)
        name_row.addWidget(name_label)
        name_row.addWidget(self.name_input)
        layout.addLayout(name_row)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setObjectName("btn_secondary")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)

        self.create_btn = QPushButton("➕ Criar")
        self.create_btn.setObjectName("btn_primary")
        self.create_btn.setFixedWidth(120)
        self.create_btn.setEnabled(False)
        self.create_btn.clicked.connect(self._accept)

        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(self.create_btn)
        layout.addLayout(btn_row)

    def select_type(self, etype: str):
        for t, card in self.type_cards.items():
            card.set_selected(t == etype)
        self.selected_type = etype
        info = ELEMENT_TYPES.get(etype, {})
        self.desc_label.setText(info.get("desc", ""))
        self.desc_label.setStyleSheet(f"color: {info.get('color','#aaa')}; font-size: 11px;")
        if not self.name_input.text():
            self.name_input.setPlaceholderText(f"Ex: {info.get('label','')} Especial")
        self.create_btn.setEnabled(True)

    def _accept(self):
        if not self.selected_type:
            return
        name = self.name_input.text().strip()
        if not name:
            info = ELEMENT_TYPES.get(self.selected_type, {})
            self.name_input.setText(f"Novo {info.get('label','Elemento')}")
        self.accept()

    def get_data(self) -> dict:
        return {
            "etype": self.selected_type,
            "name": self.name_input.text().strip() or f"Novo {ELEMENT_TYPES[self.selected_type]['label']}",
        }
