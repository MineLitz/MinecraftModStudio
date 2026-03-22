import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QLinearGradient, QBrush, QPen

APP_VERSION = "1.0.0"


class RecentProjectCard(QFrame):
    open_requested = pyqtSignal(str)

    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self.path = path
        name = os.path.splitext(os.path.basename(path))[0]
        folder = os.path.dirname(path)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(58)
        self.setStyleSheet("""
            QFrame { background:#1e1e1e; border:1px solid #2a2a2a; border-radius:6px; }
            QFrame:hover { background:#252525; border-color:#3a4a2a; }
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(12)

        icon = QLabel("📁")
        icon.setFont(QFont("Segoe UI Emoji", 18))
        icon.setStyleSheet("background:transparent; border:none;")
        lay.addWidget(icon)

        info = QVBoxLayout()
        info.setSpacing(2)
        n_lbl = QLabel(name)
        n_lbl.setStyleSheet("background:transparent; border:none; color:#ccc; font-size:12px; font-weight:bold;")
        p_lbl = QLabel(folder)
        p_lbl.setStyleSheet("background:transparent; border:none; color:#555; font-size:10px;")
        p_lbl.setMaximumWidth(320)
        info.addWidget(n_lbl)
        info.addWidget(p_lbl)
        lay.addLayout(info)
        lay.addStretch()

        open_btn = QPushButton("Abrir →")
        open_btn.setFixedSize(80, 28)
        open_btn.setStyleSheet("""
            QPushButton { background:#1a3010; border:1px solid #3a6a20;
                border-radius:4px; color:#7ec850; font-size:11px; }
            QPushButton:hover { background:#253a18; border-color:#5aaa20; }
        """)
        open_btn.clicked.connect(lambda: self.open_requested.emit(self.path))
        lay.addWidget(open_btn)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.open_requested.emit(self.path)


class WelcomeScreen(QWidget):
    open_main = pyqtSignal(object)  # workspace or None

    def __init__(self):
        super().__init__()
        self.settings = QSettings("MMS", "MinecraftModStudio")
        self.setWindowTitle("Minecraft Mod Studio")
        self.setMinimumSize(900, 620)
        self.resize(960, 660)
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── LEFT PANEL (branding) ──────────────────────────────────────────
        left = QFrame()
        left.setFixedWidth(340)
        left.setStyleSheet("background: #141a0e;")
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(40, 50, 36, 36)
        left_lay.setSpacing(0)

        # Logo area
        logo_lbl = QLabel("⛏")
        logo_lbl.setFont(QFont("Segoe UI Emoji", 52))
        logo_lbl.setStyleSheet("background:transparent; color:#7ec850;")
        left_lay.addWidget(logo_lbl)

        left_lay.addSpacing(16)

        title = QLabel("Minecraft\nMod Studio")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet("background:transparent; color:#e8f8d0; line-height:1.2;")
        left_lay.addWidget(title)

        left_lay.addSpacing(10)

        tag = QLabel("Crie mods visualmente,\nsem escrever código.")
        tag.setStyleSheet("background:transparent; color:#4a6a30; font-size:13px; line-height:1.5;")
        left_lay.addWidget(tag)

        left_lay.addStretch()

        # Features list
        features = [
            ("⚔️", "Itens, blocos e mobs"),
            ("🎨", "Editor de pixel art"),
            ("📜", "Receitas de crafting"),
            ("🔌", "Sistema de plugins"),
            ("📦", "Exportação automática"),
        ]
        for icon, text in features:
            row = QHBoxLayout()
            row.setSpacing(10)
            i_lbl = QLabel(icon)
            i_lbl.setFont(QFont("Segoe UI Emoji", 13))
            i_lbl.setStyleSheet("background:transparent;")
            i_lbl.setFixedWidth(24)
            t_lbl = QLabel(text)
            t_lbl.setStyleSheet("background:transparent; color:#4a7a30; font-size:12px;")
            row.addWidget(i_lbl)
            row.addWidget(t_lbl)
            row.addStretch()
            left_lay.addLayout(row)
            left_lay.addSpacing(6)

        left_lay.addStretch()

        ver_lbl = QLabel(f"v{APP_VERSION}  ·  Python + PyQt6")
        ver_lbl.setStyleSheet("background:transparent; color:#2a4020; font-size:10px;")
        left_lay.addWidget(ver_lbl)

        root.addWidget(left)

        # ── RIGHT PANEL ────────────────────────────────────────────────────
        right = QFrame()
        right.setStyleSheet("background:#1a1a1a;")
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(48, 50, 48, 36)
        right_lay.setSpacing(0)

        welcome_lbl = QLabel("Bem-vindo ao Mod Studio")
        welcome_lbl.setStyleSheet("color:#cccccc; font-size:20px; font-weight:bold;")
        right_lay.addWidget(welcome_lbl)

        sub_lbl = QLabel("O que você quer fazer hoje?")
        sub_lbl.setStyleSheet("color:#555; font-size:13px; margin-top:4px;")
        right_lay.addWidget(sub_lbl)

        right_lay.addSpacing(30)

        # Action buttons
        actions = QHBoxLayout()
        actions.setSpacing(12)

        new_btn = self._action_btn(
            "➕", "Novo Projeto",
            "Comece um mod do zero",
            "#1e4a10", "#4a8a20", "#7ec850"
        )
        new_btn.clicked.connect(self._new_project)
        actions.addWidget(new_btn)

        open_btn = self._action_btn(
            "📂", "Abrir Projeto",
            "Continue um mod existente",
            "#2a2a2a", "#444444", "#aaaaaa"
        )
        open_btn.clicked.connect(self._open_project)
        actions.addWidget(open_btn)

        right_lay.addLayout(actions)

        right_lay.addSpacing(36)

        # Recent projects
        recent_hdr = QHBoxLayout()
        r_lbl = QLabel("PROJETOS RECENTES")
        r_lbl.setStyleSheet("color:#444; font-size:10px; font-weight:bold; letter-spacing:1px;")
        recent_hdr.addWidget(r_lbl)
        recent_hdr.addStretch()
        clr_btn = QPushButton("Limpar")
        clr_btn.setStyleSheet("""
            QPushButton { background:transparent; border:none; color:#444; font-size:10px; }
            QPushButton:hover { color:#7ec850; }
        """)
        clr_btn.clicked.connect(self._clear_recent)
        recent_hdr.addWidget(clr_btn)
        right_lay.addLayout(recent_hdr)

        right_lay.addSpacing(10)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#252525; max-height:1px;")
        right_lay.addWidget(sep)
        right_lay.addSpacing(12)

        # Recent list
        self.recent_container = QVBoxLayout()
        self.recent_container.setSpacing(6)
        right_lay.addLayout(self.recent_container)
        self._populate_recent()

        right_lay.addStretch()

        # Bottom tip
        tip = QLabel("💡  Dica: Use  Ctrl+E  para adicionar elementos rapidamente")
        tip.setStyleSheet("color:#333; font-size:11px; font-style:italic;")
        right_lay.addWidget(tip)

        root.addWidget(right)

    def _action_btn(self, icon, title, subtitle, bg, border, color):
        btn = QPushButton()
        btn.setFixedSize(190, 80)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background:{bg};
                border:1px solid {border};
                border-radius:8px;
                text-align:left;
                padding:12px 16px;
            }}
            QPushButton:hover {{
                background-color: {bg};
                border-color:{color};
            }}
            QPushButton:pressed {{
                background-color: {bg};
            }}
        """)

        # Build content as a widget overlaid on the button
        overlay = QWidget(btn)
        overlay.setGeometry(0, 0, 190, 80)
        overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        overlay.setStyleSheet("background:transparent;")

        lay = QVBoxLayout(overlay)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(4)

        top = QHBoxLayout()
        top.setSpacing(8)
        i_lbl = QLabel(icon)
        i_lbl.setFont(QFont("Segoe UI Emoji", 18))
        i_lbl.setStyleSheet("background:transparent; border:none; color:transparent;")
        # Use text directly since emoji on label inside transparent widget can be tricky
        t_lbl = QLabel(f"{icon}  {title}")
        t_lbl.setStyleSheet(f"background:transparent; border:none; color:{color}; font-size:13px; font-weight:bold;")
        top.addWidget(t_lbl)
        top.addStretch()
        lay.addLayout(top)

        s_lbl = QLabel(subtitle)
        s_lbl.setStyleSheet(f"background:transparent; border:none; color:{color}88; font-size:10px;")
        lay.addWidget(s_lbl)

        return btn

    def _populate_recent(self):
        # Clear
        while self.recent_container.count():
            item = self.recent_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        recents = self.settings.value("recent_projects", []) or []
        recents = [r for r in recents if isinstance(r, str) and os.path.exists(r)]

        if not recents:
            lbl = QLabel("Nenhum projeto recente")
            lbl.setStyleSheet("color:#333; font-size:12px; padding:20px 0;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.recent_container.addWidget(lbl)
            return

        for path in recents[:5]:
            card = RecentProjectCard(path)
            card.open_requested.connect(self._open_path)
            self.recent_container.addWidget(card)

    def _clear_recent(self):
        self.settings.setValue("recent_projects", [])
        self._populate_recent()

    def _new_project(self):
        from ui.dialogs.new_project_dialog import NewProjectDialog
        from core.workspace import Workspace
        dlg = NewProjectDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            ws = Workspace()
            ws.new_project(
                data["name"], data["mod_id"], data["mc_version"],
                data["loader"], data["author"], data["description"]
            )
            self.open_main.emit(ws)

    def _open_project(self):
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Projeto", "",
            "Minecraft Mod Studio (*.mms);;JSON (*.json)"
        )
        if path:
            self._open_path(path)

    def _open_path(self, path: str):
        from core.workspace import Workspace
        try:
            ws = Workspace()
            ws.load(path)
            recents = self.settings.value("recent_projects", []) or []
            if path in recents:
                recents.remove(path)
            recents.insert(0, path)
            self.settings.setValue("recent_projects", recents[:10])
            self.open_main.emit(ws)
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Não foi possível abrir:\n{e}")
