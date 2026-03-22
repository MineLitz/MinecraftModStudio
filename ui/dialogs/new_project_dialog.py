from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QFormLayout, QFrame, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


MC_VERSIONS = ["1.21.4", "1.21.1", "1.20.6", "1.20.4", "1.20.2", "1.19.4", "1.18.2"]
LOADERS = ["NeoForge", "Forge", "Fabric", "Quilt"]


class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo Projeto — Minecraft Mod Studio")
        self.setFixedSize(500, 460)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(16)

        # Header
        title = QLabel("Criar Novo Projeto")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #7ec850; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        sub = QLabel("Configure o seu mod Minecraft")
        sub.setStyleSheet("color: #666; font-size: 12px; margin-bottom: 4px;")
        layout.addWidget(sub)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #333; max-height: 1px;")
        layout.addWidget(sep)

        # Form
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: Meu Mod Incrível")
        self.name_input.textChanged.connect(self._auto_fill_id)
        form.addRow("Nome do Mod:", self.name_input)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Ex: meu_mod (sem espaços)")
        form.addRow("Mod ID:", self.id_input)

        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Seu nome")
        form.addRow("Autor:", self.author_input)

        self.version_input = QLineEdit("1.0.0")
        form.addRow("Versão:", self.version_input)

        self.mc_combo = QComboBox()
        self.mc_combo.addItems(MC_VERSIONS)
        form.addRow("Minecraft:", self.mc_combo)

        self.loader_combo = QComboBox()
        self.loader_combo.addItems(LOADERS)
        form.addRow("Loader:", self.loader_combo)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Descrição do seu mod (opcional)...")
        self.desc_input.setMaximumHeight(70)
        form.addRow("Descrição:", self.desc_input)

        layout.addLayout(form)
        layout.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setObjectName("btn_secondary")
        cancel_btn.setFixedWidth(110)
        cancel_btn.clicked.connect(self.reject)

        self.create_btn = QPushButton("✦ Criar Projeto")
        self.create_btn.setObjectName("btn_primary")
        self.create_btn.setFixedWidth(150)
        self.create_btn.clicked.connect(self._validate_and_accept)
        self.create_btn.setDefault(True)

        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(self.create_btn)
        layout.addLayout(btn_row)

    def _auto_fill_id(self, text: str):
        auto = text.lower().replace(" ", "_").replace("-", "_")
        auto = "".join(c for c in auto if c.isalnum() or c == "_")
        self.id_input.setText(auto)

    def _validate_and_accept(self):
        if not self.name_input.text().strip():
            self.name_input.setStyleSheet("border-color: #e04040;")
            return
        if not self.id_input.text().strip():
            self.id_input.setStyleSheet("border-color: #e04040;")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "name": self.name_input.text().strip(),
            "mod_id": self.id_input.text().strip(),
            "author": self.author_input.text().strip(),
            "version": self.version_input.text().strip() or "1.0.0",
            "mc_version": self.mc_combo.currentText(),
            "loader": self.loader_combo.currentText(),
            "description": self.desc_input.toPlainText().strip(),
        }
