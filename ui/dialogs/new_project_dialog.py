from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QFormLayout, QFrame, QTextEdit,
    QWidget, QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

MC_VERSIONS = ["1.21.4", "1.21.1", "1.20.6", "1.20.4", "1.20.2", "1.19.4", "1.18.2"]
LOADERS = ["NeoForge", "Forge", "Fabric", "Quilt"]


# ── Step 1: project type card ────────────────────────────────────────────────
class TypeCard(QFrame):
    def __init__(self, icon, title, subtitle, tag, tag_color, card_type, parent=None):
        super().__init__(parent)
        self.card_type = card_type
        self.setFixedSize(210, 140)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.selected = False
        self._sel_color = tag_color

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 14)
        lay.setSpacing(6)

        top = QHBoxLayout()
        i_lbl = QLabel(icon)
        i_lbl.setFont(QFont("Segoe UI Emoji", 24))
        i_lbl.setStyleSheet("background:transparent; border:none;")
        top.addWidget(i_lbl)
        top.addStretch()

        badge = QLabel(tag)
        badge.setStyleSheet(f"""
            background: transparent;
            border: 1px solid {tag_color};
            border-radius: 3px;
            color: {tag_color};
            font-size: 9px;
            font-weight: bold;
            padding: 2px 6px;
            letter-spacing: 0.5px;
        """)
        top.addWidget(badge)
        lay.addLayout(top)

        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("background:transparent; border:none; color:#d0d0d0; font-size:14px; font-weight:bold;")
        lay.addWidget(t_lbl)

        s_lbl = QLabel(subtitle)
        s_lbl.setWordWrap(True)
        s_lbl.setStyleSheet("background:transparent; border:none; color:#585858; font-size:11px;")
        lay.addWidget(s_lbl)

        self._update_style()

    def _update_style(self):
        if self.selected:
            self.setStyleSheet(f"""
                QFrame {{
                    background: #1e2a1a;
                    border: 2px solid {self._sel_color};
                    border-radius: 8px;
                }}
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background: #222;
                    border: 1px solid #2e2e2e;
                    border-radius: 8px;
                }
                QFrame:hover {
                    background: #272727;
                    border-color: #3a3a3a;
                }
            """)

    def set_selected(self, val: bool):
        self.selected = val
        self._update_style()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            p = self.parent()
            while p and not isinstance(p, NewProjectDialog):
                p = p.parent()
            if p:
                p.select_type(self.card_type)


# ── Main dialog ──────────────────────────────────────────────────────────────
class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo Projeto — Minecraft Mod Studio")
        self.setFixedSize(520, 500)
        self.setModal(True)
        self._selected_type = "mod"
        self._build_ui()

    def _build_ui(self):
        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(0, 0, 0, 0)
        self._outer.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("background: #1e1e1e; border-bottom: 1px solid #2a2a2a;")
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(28, 20, 28, 16)
        h_lay.setSpacing(4)
        self._header_title = QLabel("Novo Projeto")
        self._header_title.setStyleSheet("color:#d0d0d0; font-size:16px; font-weight:bold;")
        self._header_sub = QLabel("Escolha o tipo de projeto")
        self._header_sub.setStyleSheet("color:#505050; font-size:12px;")
        h_lay.addWidget(self._header_title)
        h_lay.addWidget(self._header_sub)
        self._outer.addWidget(header)

        # Step indicator
        steps_bar = QFrame()
        steps_bar.setStyleSheet("background:#1a1a1a; border-bottom:1px solid #222;")
        steps_bar.setFixedHeight(32)
        s_lay = QHBoxLayout(steps_bar)
        s_lay.setContentsMargins(28, 0, 28, 0)
        s_lay.setSpacing(8)
        self._step_labels = []
        for i, txt in enumerate(["1  Tipo", "2  Configuração"]):
            lbl = QLabel(txt)
            lbl.setStyleSheet("color:#666; font-size:10px; font-weight:bold; letter-spacing:0.5px;")
            self._step_labels.append(lbl)
            s_lay.addWidget(lbl)
            if i < 1:
                sep = QLabel("›")
                sep.setStyleSheet("color:#333; font-size:14px;")
                s_lay.addWidget(sep)
        s_lay.addStretch()
        self._outer.addWidget(steps_bar)

        # Stacked pages
        self._stack = QStackedWidget()
        self._stack.addWidget(self._build_step1())
        self._stack.addWidget(self._build_step2())
        self._outer.addWidget(self._stack)

        self._update_step_indicator(0)

    def _build_step1(self):
        page = QWidget()
        page.setStyleSheet("background: #222;")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 20)
        lay.setSpacing(16)

        desc = QLabel("O que você quer criar?")
        desc.setStyleSheet("color:#888; font-size:12px;")
        lay.addWidget(desc)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(14)

        self._card_mod = TypeCard(
            "🧩", "Mod Java",
            "Adicione itens, blocos,\nmobs e mecânicas novas",
            "EM BREVE", "#505050", "mod"
        )
        self._card_rp = TypeCard(
            "🎨", "Resource Pack",
            "Altere texturas, sons\ne modelos do jogo",
            "DISPONÍVEL", "#6ab84a", "resource_pack"
        )
        self._card_rp.set_selected(True)
        self._selected_type = "resource_pack"

        cards_row.addWidget(self._card_mod)
        cards_row.addWidget(self._card_rp)
        cards_row.addStretch()
        lay.addLayout(cards_row)

        # Resource pack notice
        self._rp_notice = QFrame()
        self._rp_notice.setStyleSheet("""
            QFrame {
                background: #2a2010;
                border: 1px solid #3a3010;
                border-radius: 6px;
            }
        """)
        self._rp_notice.hide()
        n_lay = QHBoxLayout(self._rp_notice)
        n_lay.setContentsMargins(14, 10, 14, 10)
        n_lay.setSpacing(10)
        n_icon = QLabel("⚠")
        n_icon.setStyleSheet("background:transparent; color:#c89040; font-size:14px;")
        n_text = QLabel(
            "Resource Pack estará disponível em breve.\n"
            "Será necessário importar os assets do Minecraft."
        )
        n_text.setStyleSheet("background:transparent; color:#887040; font-size:11px;")
        n_text.setWordWrap(True)
        n_lay.addWidget(n_icon)
        n_lay.addWidget(n_text)
        lay.addWidget(self._rp_notice)

        lay.addStretch()

        # Nav buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        cancel = QPushButton("Cancelar")
        cancel.setObjectName("btn_secondary")
        cancel.setFixedWidth(100)
        cancel.clicked.connect(self.reject)

        self._next_btn = QPushButton("Próximo →")
        self._next_btn.setObjectName("btn_primary")
        self._next_btn.setFixedWidth(130)
        self._next_btn.clicked.connect(self._go_step2)

        btn_row.addStretch()
        btn_row.addWidget(cancel)
        btn_row.addWidget(self._next_btn)
        lay.addLayout(btn_row)

        return page

    def _build_step2(self):
        page = QWidget()
        page.setStyleSheet("background: #222;")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 20)
        lay.setSpacing(0)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setContentsMargins(0, 0, 0, 16)

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Ex: Meu Resource Pack")
        self._name_input.setMinimumHeight(32)
        self._name_input.textChanged.connect(self._auto_fill_id)
        form.addRow("Nome:", self._name_input)

        self._id_input = QLineEdit()
        self._id_input.setPlaceholderText("Ex: meu_pack")
        self._id_input.setMinimumHeight(32)
        form.addRow("ID:", self._id_input)

        self._author_input = QLineEdit()
        self._author_input.setPlaceholderText("Seu nome")
        self._author_input.setMinimumHeight(32)
        form.addRow("Autor:", self._author_input)

        self._version_input = QLineEdit("1.0.0")
        self._version_input.setMinimumHeight(32)
        form.addRow("Versão:", self._version_input)

        self._mc_combo = QComboBox()
        self._mc_combo.addItems(MC_VERSIONS)
        self._mc_combo.setMinimumHeight(32)
        form.addRow("Minecraft:", self._mc_combo)

        # Loader row — hidden for Resource Packs
        self._loader_combo = QComboBox()
        self._loader_combo.addItems(LOADERS)
        self._loader_combo.setMinimumHeight(32)
        self._loader_row_label = QLabel("Loader:")
        form.addRow(self._loader_row_label, self._loader_combo)

        self._desc_input = QTextEdit()
        self._desc_input.setPlaceholderText("Descrição (opcional)...")
        self._desc_input.setMaximumHeight(62)
        form.addRow("Descrição:", self._desc_input)

        lay.addLayout(form)

        # Resource pack info banner (shown for RP projects)
        self._rp_info = QFrame()
        self._rp_info.setStyleSheet(
            "QFrame{background:#1a2a10;border:1px solid #2a4a18;"
            "border-radius:6px;}")
        ri = QHBoxLayout(self._rp_info)
        ri.setContentsMargins(12, 8, 12, 8)
        ri.setSpacing(8)
        ri_icon = QLabel("ℹ")
        ri_icon.setStyleSheet("background:transparent;color:#6ab84a;font-size:14px;")
        ri_text = QLabel(
            "As texturas disponíveis para edição serão filtradas\n"
            "de acordo com a versão do Minecraft selecionada.")
        ri_text.setStyleSheet(
            "background:transparent;color:#4a7a30;font-size:11px;")
        ri.addWidget(ri_icon)
        ri.addWidget(ri_text)
        lay.addWidget(self._rp_info)

        lay.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        back_btn = QPushButton("← Voltar")
        back_btn.setObjectName("btn_secondary")
        back_btn.setFixedWidth(100)
        back_btn.clicked.connect(lambda: self._go_step(0))

        self._create_btn = QPushButton("Criar Projeto")
        self._create_btn.setObjectName("btn_primary")
        self._create_btn.setFixedWidth(140)
        self._create_btn.clicked.connect(self._validate_and_accept)
        self._create_btn.setDefault(True)

        btn_row.addStretch()
        btn_row.addWidget(back_btn)
        btn_row.addWidget(self._create_btn)
        lay.addLayout(btn_row)

        return page

    # ── Navigation ────────────────────────────────────────────────────────────
    def _go_step2(self):
        self._go_step(1)
        is_rp = self._selected_type == "resource_pack"
        self._loader_combo.setVisible(not is_rp)
        self._loader_row_label.setVisible(not is_rp)
        self._rp_info.setVisible(is_rp)
        if is_rp:
            self._name_input.setPlaceholderText("Ex: Meu Resource Pack")
            self._id_input.setPlaceholderText("Ex: meu_pack")
        else:
            self._name_input.setPlaceholderText("Ex: Meu Mod Incrível")
            self._id_input.setPlaceholderText("Ex: meu_mod")

    def _go_step(self, idx: int):
        self._stack.setCurrentIndex(idx)
        self._update_step_indicator(idx)
        if idx == 1:
            self._header_sub.setText("Configure seu projeto")
            # Hide loader row for resource packs (future)
        else:
            self._header_sub.setText("Escolha o tipo de projeto")

    def _update_step_indicator(self, idx: int):
        for i, lbl in enumerate(self._step_labels):
            lbl.setStyleSheet(
                "color:#6ab84a; font-size:10px; font-weight:bold; letter-spacing:0.5px;"
                if i == idx else
                "color:#404040; font-size:10px; font-weight:bold; letter-spacing:0.5px;"
            )

    def select_type(self, t: str):
        if t == "mod":
            # Mod disabled for now
            return
        self._selected_type = t
        self._card_mod.set_selected(False)
        self._card_rp.set_selected(t == "resource_pack")
        self._rp_notice.setVisible(False)
        self._next_btn.setEnabled(True)
        self._next_btn.setText("Próximo →")

    def _auto_fill_id(self, text: str):
        auto = "".join(
            c for c in text.lower().replace(" ", "_").replace("-", "_")
            if c.isalnum() or c == "_"
        )
        self._id_input.setText(auto)

    def _validate_and_accept(self):
        if not self._name_input.text().strip():
            self._name_input.setStyleSheet(
                self._name_input.styleSheet() + "border-color:#c04040;"
            )
            return
        if not self._id_input.text().strip():
            self._id_input.setStyleSheet(
                self._id_input.styleSheet() + "border-color:#c04040;"
            )
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "project_type": self._selected_type,
            "name": self._name_input.text().strip(),
            "mod_id": self._id_input.text().strip(),
            "author": self._author_input.text().strip(),
            "version": self._version_input.text().strip() or "1.0.0",
            "mc_version": self._mc_combo.currentText(),
            "loader": self._loader_combo.currentText(),
            "description": self._desc_input.toPlainText().strip(),
        }
