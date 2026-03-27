from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.validator import ModValidator


class ValidatorDialog(QDialog):
    def __init__(self, workspace, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Validador de Mod")
        self.setFixedSize(520, 460)
        self.setModal(True)
        self.workspace = workspace
        self._build_ui()
        self._run()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("background:#1e1e1e; border-bottom:1px solid #2a2a2a;")
        header.setFixedHeight(56)
        h = QHBoxLayout(header)
        h.setContentsMargins(20, 0, 20, 0)
        h.setSpacing(12)

        title_icon = QLabel("🔍")
        title_icon.setFont(QFont("Segoe UI Emoji", 20))
        title_icon.setStyleSheet("background:transparent;")
        h.addWidget(title_icon)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        t = QLabel("Validador de Mod")
        t.setStyleSheet("background:transparent; color:#d0d0d0; font-size:14px; font-weight:bold;")
        title_col.addWidget(t)
        self._summary_lbl = QLabel("Analisando...")
        self._summary_lbl.setStyleSheet("background:transparent; color:#505050; font-size:11px;")
        title_col.addWidget(self._summary_lbl)
        h.addLayout(title_col)
        h.addStretch()

        rerun_btn = QPushButton("↺ Validar novamente")
        rerun_btn.setFixedHeight(28)
        rerun_btn.clicked.connect(self._run)
        h.addWidget(rerun_btn)
        lay.addWidget(header)

        # Issue list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: #222; }")

        self._list_widget = QWidget()
        self._list_widget.setStyleSheet("background: #222;")
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(16, 16, 16, 16)
        self._list_layout.setSpacing(8)
        self._list_layout.addStretch()
        scroll.setWidget(self._list_widget)
        lay.addWidget(scroll)

        # Footer
        footer = QFrame()
        footer.setStyleSheet("background:#1e1e1e; border-top:1px solid #2a2a2a;")
        footer.setFixedHeight(52)
        f = QHBoxLayout(footer)
        f.setContentsMargins(16, 0, 16, 0)
        f.addStretch()
        close_btn = QPushButton("Fechar")
        close_btn.setObjectName("btn_secondary")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.accept)
        f.addWidget(close_btn)
        lay.addWidget(footer)

    def _run(self):
        # Clear list
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        validator = ModValidator(self.workspace)
        issues = validator.validate()

        errors   = sum(1 for i in issues if i.level == "error")
        warnings = sum(1 for i in issues if i.level == "warning")

        if errors:
            summary = f"{errors} erro{'s' if errors > 1 else ''}  ·  {warnings} aviso{'s' if warnings != 1 else ''}"
            color = "#c04040"
        elif warnings:
            summary = f"0 erros  ·  {warnings} aviso{'s' if warnings != 1 else ''}"
            color = "#c89040"
        else:
            summary = "Nenhum problema encontrado"
            color = "#6ab84a"

        self._summary_lbl.setText(summary)
        self._summary_lbl.setStyleSheet(f"background:transparent; color:{color}; font-size:11px;")

        for issue in issues:
            row = self._make_row(issue)
            self._list_layout.insertWidget(self._list_layout.count() - 1, row)

    def _make_row(self, issue) -> QFrame:
        row = QFrame()
        row.setStyleSheet(f"""
            QFrame {{
                background: #1e1e1e;
                border-left: 3px solid {issue.color};
                border-radius: 0px;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }}
        """)
        row.setMinimumHeight(52)

        lay = QHBoxLayout(row)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(12)

        icon_lbl = QLabel(issue.icon)
        icon_lbl.setFixedWidth(18)
        icon_lbl.setStyleSheet(f"background:transparent; color:{issue.color}; font-size:14px; font-weight:bold;")
        lay.addWidget(icon_lbl)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        name_lbl = QLabel(issue.element_name)
        name_lbl.setStyleSheet(f"background:transparent; color:{issue.color}; font-size:10px; font-weight:bold; letter-spacing:0.5px;")
        text_col.addWidget(name_lbl)

        msg_lbl = QLabel(issue.message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("background:transparent; color:#b0b0b0; font-size:12px;")
        text_col.addWidget(msg_lbl)

        lay.addLayout(text_col)
        return row
