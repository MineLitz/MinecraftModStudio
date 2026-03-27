import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter, QLinearGradient, QColor, QBrush

APP_VERSION = "0.0.1"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── Custom left panel with background art + gradient overlay ────────────────
class ArtPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(340)
        img_path = os.path.join(BASE_DIR, "resources", "icons", "alfa-art-menu.png")
        self.bg = QPixmap(img_path) if os.path.exists(img_path) else None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Dark base
        painter.fillRect(self.rect(), QColor("#0d0d0d"))

        if self.bg:
            # Scale image to fill width, aligned to top
            scaled = self.bg.scaledToWidth(
                self.width(), Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(0, 0, scaled)

        # Gradient: transparent (top 25%) → fully dark (bottom)
        grad = QLinearGradient(0, self.height() * 0.20, 0, self.height())
        grad.setColorAt(0.0, QColor(0, 0, 0, 0))
        grad.setColorAt(0.45, QColor(0, 0, 0, 220))
        grad.setColorAt(1.0, QColor(0, 0, 0, 255))
        painter.fillRect(self.rect(), QBrush(grad))


# ── Recent project card ─────────────────────────────────────────────────────
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
            QFrame { background:#222; border:1px solid #2a2a2a; border-radius:6px; }
            QFrame:hover { background:#2a2a2a; border-color:#3a4a2a; }
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(10)

        icon = QLabel("📁")
        icon.setFont(QFont("Segoe UI Emoji", 16))
        icon.setStyleSheet("background:transparent; border:none;")
        lay.addWidget(icon)

        info = QVBoxLayout()
        info.setSpacing(2)
        n_lbl = QLabel(name)
        n_lbl.setStyleSheet("background:transparent; border:none; color:#ccc; font-size:12px; font-weight:bold;")
        p_lbl = QLabel(folder)
        p_lbl.setStyleSheet("background:transparent; border:none; color:#555; font-size:10px;")
        p_lbl.setMaximumWidth(300)
        info.addWidget(n_lbl)
        info.addWidget(p_lbl)
        lay.addLayout(info)
        lay.addStretch()

        open_btn = QPushButton("Abrir →")
        open_btn.setFixedSize(80, 26)
        open_btn.setStyleSheet("""
            QPushButton { background:#1e3010; border:1px solid #3a5a20;
                border-radius:4px; color:#6ab84a; font-size:11px; }
            QPushButton:hover { background:#283e18; border-color:#4a7a28; }
        """)
        open_btn.clicked.connect(lambda: self.open_requested.emit(self.path))
        lay.addWidget(open_btn)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.open_requested.emit(self.path)


# ── Welcome screen ──────────────────────────────────────────────────────────
class WelcomeScreen(QWidget):
    open_main = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.settings = QSettings("MMS", "MinecraftModStudio")
        self.setWindowTitle("Minecraft Mod Studio")
        self.setMinimumSize(820, 540)
        self.resize(860, 560)
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── LEFT PANEL (art background) ─────────────────────────────────────
        left = ArtPanel()
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(28, 20, 28, 24)
        left_lay.setSpacing(0)

        left_lay.addStretch()

        # Features list (bottom dark area)
        tag = QLabel("Crie mods visualmente,\nsem escrever código.")
        tag.setStyleSheet("background:transparent; color:#6ab84a; font-size:12px; margin-bottom:8px;")
        left_lay.addWidget(tag)

        features = [
            ("⚔️", "Itens, blocos e mobs"),
            ("🎨", "Editor de pixel art"),
            ("📜", "Receitas de crafting"),
            ("🔌", "Sistema de plugins"),
            ("📦", "Exportação automática"),
        ]
        for icon, text in features:
            row = QHBoxLayout()
            row.setSpacing(8)
            i_lbl = QLabel(icon)
            i_lbl.setFont(QFont("Segoe UI Emoji", 12))
            i_lbl.setStyleSheet("background:transparent;")
            i_lbl.setFixedWidth(22)
            t_lbl = QLabel(text)
            t_lbl.setStyleSheet("background:transparent; color:#6a6a6a; font-size:11px;")
            row.addWidget(i_lbl)
            row.addWidget(t_lbl)
            row.addStretch()
            left_lay.addLayout(row)
            left_lay.addSpacing(4)

        left_lay.addSpacing(14)

        # Version
        ver = QLabel(f"v{APP_VERSION}  ·  Minecraft Mod Studio")
        ver.setStyleSheet("background:transparent; color:#3a3a3a; font-size:10px;")
        left_lay.addWidget(ver)

        root.addWidget(left)

        # ── RIGHT PANEL ──────────────────────────────────────────────────────
        right = QFrame()
        right.setStyleSheet("background:#1e1e1e;")
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(48, 44, 48, 32)
        right_lay.setSpacing(0)

        welcome_lbl = QLabel("Bem-vindo ao Mod Studio")
        welcome_lbl.setStyleSheet("color:#d0d0d0; font-size:20px; font-weight:bold;")
        right_lay.addWidget(welcome_lbl)

        sub_lbl = QLabel("O que você quer fazer hoje?")
        sub_lbl.setStyleSheet("color:#505050; font-size:12px; margin-top:4px;")
        right_lay.addWidget(sub_lbl)

        right_lay.addSpacing(28)

        # Action buttons
        actions = QHBoxLayout()
        actions.setSpacing(12)

        new_btn = self._action_btn(
            "➕", "Novo Projeto", "Comece um mod do zero",
            "#1e3010", "#3a5020", "#6ab84a"
        )
        new_btn.clicked.connect(self._new_project)
        actions.addWidget(new_btn)

        open_btn = self._action_btn(
            "📂", "Abrir Projeto", "Continue um mod existente",
            "#252525", "#383838", "#909090"
        )
        open_btn.clicked.connect(self._open_project)
        actions.addWidget(open_btn)

        actions.addStretch()
        right_lay.addLayout(actions)

        right_lay.addSpacing(32)

        # Recent header
        recent_hdr = QHBoxLayout()
        r_lbl = QLabel("PROJETOS RECENTES")
        r_lbl.setStyleSheet("color:#404040; font-size:10px; font-weight:bold; letter-spacing:1px;")
        recent_hdr.addWidget(r_lbl)
        recent_hdr.addStretch()
        clr_btn = QPushButton("Limpar")
        clr_btn.setStyleSheet("""
            QPushButton { background:transparent; border:none; color:#404040; font-size:10px; }
            QPushButton:hover { color:#6ab84a; }
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

        self.recent_container = QVBoxLayout()
        self.recent_container.setSpacing(6)
        right_lay.addLayout(self.recent_container)
        self._populate_recent()

        right_lay.addStretch()

        tip = QLabel("💡  Dica: Use  Ctrl+E  para adicionar elementos rapidamente")
        tip.setStyleSheet("color:#303030; font-size:11px; font-style:italic;")
        right_lay.addWidget(tip)

        root.addWidget(right)

    def _action_btn(self, icon, title, subtitle, bg, border, color):
        btn = QPushButton()
        btn.setFixedSize(185, 76)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background:{bg}; border:1px solid {border};
                border-radius:7px; text-align:left; padding:12px 14px;
            }}
            QPushButton:hover {{ border-color:{color}88; }}
            QPushButton:pressed {{ background:{bg}cc; }}
        """)
        overlay = QWidget(btn)
        overlay.setGeometry(0, 0, 185, 76)
        overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        overlay.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(overlay)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(4)
        t_lbl = QLabel(f"{icon}  {title}")
        t_lbl.setStyleSheet(f"background:transparent; color:{color}; font-size:13px; font-weight:bold;")
        s_lbl = QLabel(subtitle)
        s_lbl.setStyleSheet(f"background:transparent; color:{color}77; font-size:10px;")
        lay.addWidget(t_lbl)
        lay.addWidget(s_lbl)
        return btn

    def _populate_recent(self):
        while self.recent_container.count():
            item = self.recent_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        recents = self.settings.value("recent_projects", []) or []
        recents = [r for r in recents if isinstance(r, str) and os.path.exists(r)]

        if not recents:
            lbl = QLabel("Nenhum projeto recente")
            lbl.setStyleSheet("color:#303030; font-size:12px; padding:16px 0;")
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
                data["loader"], data["author"], data["description"],
                data["project_type"]
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
