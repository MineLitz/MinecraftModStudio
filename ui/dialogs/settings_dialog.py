import os
import sys
import subprocess
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QWidget, QStackedWidget, QFileDialog, QSizePolicy,
    QCheckBox, QComboBox, QLineEdit, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal


def restart_app():
    """Reinicia o app usando o mesmo interpretador Python."""
    from PyQt6.QtWidgets import QApplication
    try:
        from core.discord_rpc import rpc
        rpc.disconnect()
    except Exception:
        pass
    QApplication.instance().quit()
    subprocess.Popen([sys.executable] + sys.argv)


class _Section(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 20)
        lay.setSpacing(0)
        lbl = QLabel(title.upper())
        lbl.setStyleSheet(
            "color:#555;font-size:10px;font-weight:bold;letter-spacing:1px;"
            "padding-bottom:6px;border-bottom:1px solid #2a2a2a;margin-bottom:10px;")
        lay.addWidget(lbl)
        self._rows = QVBoxLayout()
        self._rows.setSpacing(8)
        self._rows.setContentsMargins(0, 0, 0, 0)
        lay.addLayout(self._rows)

    def row(self, label: str, widget: QWidget, hint: str = ""):
        r = QWidget()
        r.setStyleSheet("background:transparent;")
        rl = QHBoxLayout(r)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(12)
        col = QVBoxLayout()
        col.setSpacing(2)
        l = QLabel(label)
        l.setStyleSheet("color:#b0b0b0;font-size:12px;")
        col.addWidget(l)
        if hint:
            h = QLabel(hint)
            h.setStyleSheet("color:#484848;font-size:10px;")
            col.addWidget(h)
        rl.addLayout(col)
        rl.addStretch()
        rl.addWidget(widget)
        self._rows.addWidget(r)
        return widget


class _NavBtn(QPushButton):
    def __init__(self, label: str, parent=None):
        super().__init__(f"  {label}", parent)
        self.setFixedHeight(36)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background:transparent; border:none;
                border-left:2px solid transparent;
                color:#606060; font-size:12px; text-align:left;
                padding-left:12px; border-radius:0;
            }
            QPushButton:hover { color:#a0a0a0; background:#222; }
            QPushButton:checked {
                background:#1e1e1e; border-left-color:#6ab84a; color:#d0d0d0;
            }
        """)


class SettingsDialog(QDialog):
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações — Minecraft Mod Studio")
        self.setMinimumSize(640, 520)
        self.resize(660, 540)
        self.setModal(True)
        self.settings = QSettings("MMS", "MinecraftModStudio")
        self._restart_needed = False
        self._build_ui()
        self._load_values()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Nav sidebar ───────────────────────────────────────────────────────
        nav = QFrame()
        nav.setFixedWidth(160)
        nav.setStyleSheet("background:#1a1a1a;border-right:1px solid #222;")
        nl = QVBoxLayout(nav)
        nl.setContentsMargins(0, 12, 0, 12)
        nl.setSpacing(2)
        lbl = QLabel("CONFIGURAÇÕES")
        lbl.setStyleSheet(
            "color:#404040;font-size:9px;font-weight:bold;"
            "letter-spacing:1px;padding:0 14px 8px;")
        nl.addWidget(lbl)

        self._nav: list[_NavBtn] = []
        for i, name in enumerate(["Aparência","Idioma","Projetos","Discord"]):
            b = _NavBtn(name)
            b.clicked.connect(lambda _, idx=i: self._switch(idx))
            nl.addWidget(b)
            self._nav.append(b)
        nl.addStretch()
        root.addWidget(nav)

        # ── Content area ──────────────────────────────────────────────────────
        right = QFrame()
        right.setStyleSheet("background:#222;")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._pg_appearance())
        self._stack.addWidget(self._pg_language())
        self._stack.addWidget(self._pg_projects())
        self._stack.addWidget(self._pg_discord())
        rl.addWidget(self._stack)

        # Button bar
        bar = QFrame()
        bar.setStyleSheet("background:#1e1e1e;border-top:1px solid #2a2a2a;")
        bar.setFixedHeight(52)
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(16, 0, 16, 0)
        bl.setSpacing(10)
        bl.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.setObjectName("btn_secondary")
        cancel.setFixedWidth(100)
        cancel.clicked.connect(self.reject)
        save = QPushButton("Salvar")
        save.setObjectName("btn_primary")
        save.setFixedWidth(100)
        save.setDefault(True)
        save.clicked.connect(self._save)
        bl.addWidget(cancel)
        bl.addWidget(save)
        rl.addWidget(bar)
        root.addWidget(right)

        self._switch(0)

    def _scrolled(self, inner: QWidget) -> QScrollArea:
        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sc.setStyleSheet("QScrollArea{border:none;background:#222;}")
        inner.setStyleSheet("background:#222;")
        sc.setWidget(inner)
        return sc

    # ── Pages ─────────────────────────────────────────────────────────────────
    def _pg_appearance(self) -> QScrollArea:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        sec = _Section("Aparência")

        self._theme = QComboBox()
        self._theme.addItems(["Escuro", "Claro"])
        self._theme.setFixedWidth(160)
        sec.row("Tema da interface", self._theme, "Requer reinicialização")

        self._font_size = QComboBox()
        self._font_size.addItems(["Pequeno (11px)", "Médio (12px)", "Grande (14px)"])
        self._font_size.setFixedWidth(160)
        sec.row("Tamanho da fonte", self._font_size, "Aplicado imediatamente")

        lay.addWidget(sec)
        lay.addStretch()
        return self._scrolled(w)

    def _pg_language(self) -> QScrollArea:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        sec = _Section("Idioma")
        self._lang = QComboBox()
        self._lang.addItem("Português (Brasil)", "pt_BR")
        self._lang.addItem("English",            "en_US")
        self._lang.setFixedWidth(200)
        sec.row("Idioma da interface", self._lang, "Requer reinicialização")
        lay.addWidget(sec)

        info = QFrame()
        info.setStyleSheet(
            "QFrame{background:#1e2a1e;border:1px solid #2a4a2a;border-radius:6px;}")
        il = QHBoxLayout(info)
        il.setContentsMargins(14, 10, 14, 10)
        il.setSpacing(10)
        i_icon = QLabel("ℹ")
        i_icon.setStyleSheet("background:transparent;color:#6ab84a;font-size:14px;")
        i_icon.setFixedWidth(18)
        i_text = QLabel(
            "A tradução completa estará disponível em breve.\n"
            "Atualmente o app está em Português.")
        i_text.setStyleSheet("background:transparent;color:#4a7a30;font-size:11px;")
        i_text.setWordWrap(True)
        il.addWidget(i_icon)
        il.addWidget(i_text)
        lay.addWidget(info)
        lay.addStretch()
        return self._scrolled(w)

    def _pg_projects(self) -> QScrollArea:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        sec = _Section("Projetos")

        folder_row = QWidget()
        folder_row.setStyleSheet("background:transparent;")
        fr = QHBoxLayout(folder_row)
        fr.setContentsMargins(0, 0, 0, 0)
        fr.setSpacing(6)
        self._folder = QLineEdit()
        self._folder.setPlaceholderText("Pasta padrão do usuário")
        self._folder.setReadOnly(True)
        self._folder.setMinimumWidth(180)
        browse = QPushButton("Procurar...")
        browse.setFixedWidth(90)
        browse.clicked.connect(self._browse)
        fr.addWidget(self._folder)
        fr.addWidget(browse)
        sec.row("Pasta padrão", folder_row, "Onde os projetos são salvos por padrão")

        self._autosave = QCheckBox("Ativar")
        self._autosave.setStyleSheet("color:#b0b0b0;")
        sec.row("Auto-save", self._autosave, "Salva automaticamente a cada 5 minutos")

        self._remember_tabs = QCheckBox("Ativar")
        self._remember_tabs.setStyleSheet("color:#b0b0b0;")
        sec.row("Lembrar abas abertas", self._remember_tabs,
                "Restaura as abas ao reabrir o projeto")

        lay.addWidget(sec)
        lay.addStretch()
        return self._scrolled(w)

    def _pg_discord(self) -> QScrollArea:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        sec = _Section("Discord Rich Presence")
        self._discord = QCheckBox("Ativar Rich Presence")
        self._discord.setStyleSheet("color:#b0b0b0;font-size:12px;")
        sec._rows.addWidget(self._discord)

        # Preview card
        card = QFrame()
        card.setStyleSheet(
            "QFrame{background:#18191c;border:1px solid #2a2a2e;border-radius:8px;}")
        card.setFixedHeight(90)
        cl = QHBoxLayout(card)
        cl.setContentsMargins(14, 12, 14, 12)
        cl.setSpacing(12)
        thumb = QFrame()
        thumb.setFixedSize(52, 52)
        thumb.setStyleSheet(
            "background:#1e3010;border:1px solid #3a5020;border-radius:6px;")
        cl.addWidget(thumb)
        info_col = QVBoxLayout()
        info_col.setSpacing(3)
        for text, style in [
            ("Minecraft Mod Studio", "color:#fff;font-size:12px;font-weight:bold;"),
            ("Editing MeuPack",      "color:#b9bbbe;font-size:11px;"),
            ("Resource Pack",        "color:#72767d;font-size:11px;"),
        ]:
            l = QLabel(text)
            l.setStyleSheet(f"background:transparent;{style}")
            info_col.addWidget(l)
        cl.addLayout(info_col)
        cl.addStretch()

        hint = QLabel("Aparece no seu perfil do Discord enquanto o app estiver aberto.")
        hint.setStyleSheet("color:#484848;font-size:10px;")
        hint.setWordWrap(True)

        sec._rows.addWidget(card)
        sec._rows.addWidget(hint)
        lay.addWidget(sec)
        lay.addStretch()
        return self._scrolled(w)

    # ── Nav ───────────────────────────────────────────────────────────────────
    def _switch(self, idx: int):
        self._stack.setCurrentIndex(idx)
        for i, b in enumerate(self._nav):
            b.setChecked(i == idx)

    def _browse(self):
        path = QFileDialog.getExistingDirectory(self, "Pasta padrão de projetos")
        if path:
            self._folder.setText(path)

    # ── Load / Save ───────────────────────────────────────────────────────────
    def _load_values(self):
        s = self.settings
        self._theme.setCurrentIndex(0 if s.value("appearance/theme","dark") == "dark" else 1)
        sizes = {"small":0,"medium":1,"large":2}
        self._font_size.setCurrentIndex(
            sizes.get(s.value("appearance/font_size","medium"), 1))
        self._lang.setCurrentIndex(
            0 if s.value("language","pt_BR") == "pt_BR" else 1)
        self._folder.setText(s.value("projects/default_folder",""))
        self._autosave.setChecked(s.value("projects/auto_save",False,type=bool))
        self._remember_tabs.setChecked(s.value("projects/remember_tabs",True,type=bool))
        self._discord.setChecked(s.value("discord_rpc/enabled",True,type=bool))

    def _save(self):
        s = self.settings
        old_theme = s.value("appearance/theme","dark")
        old_lang  = s.value("language","pt_BR")

        # Aparência
        new_theme = "dark" if self._theme.currentIndex() == 0 else "light"
        s.setValue("appearance/theme", new_theme)
        sz_map = {0:"small",1:"medium",2:"large"}
        s.setValue("appearance/font_size", sz_map[self._font_size.currentIndex()])

        # Idioma
        new_lang = self._lang.currentData()
        s.setValue("language", new_lang)

        # Projetos
        s.setValue("projects/default_folder", self._folder.text())
        s.setValue("projects/auto_save",      self._autosave.isChecked())
        s.setValue("projects/remember_tabs",  self._remember_tabs.isChecked())

        # Discord
        discord_on = self._discord.isChecked()
        try:
            from core.discord_rpc import rpc
            if discord_on != s.value("discord_rpc/enabled",True,type=bool):
                rpc.set_enabled(discord_on)
        except Exception:
            pass
        s.setValue("discord_rpc/enabled", discord_on)

        self.settings_changed.emit()
        self.accept()

        # Apply font size immediately
        self._apply_font_size(sz_map[self._font_size.currentIndex()])

        # Restart prompt if needed
        if new_theme != old_theme or new_lang != old_lang:
            self._prompt_restart()

    def _apply_font_size(self, size_key: str):
        sizes = {"small":"11px","medium":"12px","large":"14px"}
        px = sizes.get(size_key,"12px")
        from PyQt6.QtWidgets import QApplication
        from ui.theme import build_theme
        from ui.font_loader import load_fonts
        s = self.settings
        fname = load_fonts()
        theme = s.value("appearance/theme","dark")
        QApplication.instance().setStyleSheet(build_theme(theme, fname, size_key))

    def _prompt_restart(self):
        msg = QMessageBox(self.parent() or self)
        msg.setWindowTitle("Reiniciar necessário")
        msg.setText("Algumas configurações requerem reinicialização para serem aplicadas.")
        msg.setInformativeText("Deseja reiniciar o app agora?")
        msg.setIcon(QMessageBox.Icon.Question)
        restart_btn = msg.addButton("Reiniciar agora", QMessageBox.ButtonRole.AcceptRole)
        msg.addButton("Depois",                        QMessageBox.ButtonRole.RejectRole)
        msg.exec()
        if msg.clickedButton() == restart_btn:
            restart_app()
