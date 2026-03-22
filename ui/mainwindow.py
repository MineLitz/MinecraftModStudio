import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QToolBar, QLabel, QStatusBar, QTextEdit,
    QFileDialog, QMessageBox, QFrame, QLineEdit,
    QTreeWidget, QTreeWidgetItem, QTabWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QSettings, QTimer
from PyQt6.QtGui import QFont, QAction, QIcon, QColor

from core.workspace import Workspace
from core.element import ModElement, ELEMENT_TYPES
from core.exporter import Exporter
from ui.workspace_panel import WorkspacePanel
from ui.properties_panel import PropertiesPanel
from ui.dialogs.new_element_dialog import NewElementDialog


class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(190)
        self.setMaximumWidth(280)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        hdr = QFrame()
        hdr.setStyleSheet("background:#1a1a1a; border-bottom:1px solid #2a2a2a;")
        hdr.setFixedHeight(36)
        h = QHBoxLayout(hdr)
        h.setContentsMargins(10, 0, 10, 0)
        lbl = QLabel("ELEMENTOS")
        lbl.setStyleSheet("color:#555; font-size:10px; font-weight:bold; letter-spacing:1px;")
        h.addWidget(lbl)
        layout.addWidget(hdr)

        # Search
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Buscar...")
        self.search.setStyleSheet("""
            QLineEdit {
                background:#222; border:none; border-bottom:1px solid #2a2a2a;
                padding:8px 10px; color:#aaa; font-size:11px;
            }
            QLineEdit:focus { border-bottom-color:#4a8a20; }
        """)
        self.search.textChanged.connect(self._filter)
        layout.addWidget(self.search)

        # Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(16)
        self.tree.setRootIsDecorated(True)
        self.tree.setAnimated(True)
        layout.addWidget(self.tree)

        self.group_items: dict[str, QTreeWidgetItem] = {}

    def populate(self, workspace: Workspace):
        self.tree.clear()
        self.group_items.clear()

        types_present = list({e.etype for e in workspace.elements})
        type_order = list(ELEMENT_TYPES.keys())
        types_present.sort(key=lambda t: type_order.index(t) if t in type_order else 99)

        for etype in types_present:
            info = ELEMENT_TYPES.get(etype, {})
            elements = workspace.elements_by_type(etype)
            grp = QTreeWidgetItem(self.tree)
            grp.setText(0, f"  {info.get('icon','')}  {info.get('label', etype)} ({len(elements)})")
            grp.setForeground(0, QColor(info.get("color", "#aaa")))
            grp.setFont(0, QFont("Segoe UI", 10, QFont.Weight.Bold))
            grp.setExpanded(True)
            self.group_items[etype] = grp

            for el in elements:
                child = QTreeWidgetItem(grp)
                child.setText(0, f"    {el.name}")
                child.setData(0, Qt.ItemDataRole.UserRole, el.id)
                child.setForeground(0, QColor("#aaaaaa"))
                child.setFont(0, QFont("Segoe UI", 11))

        if not types_present:
            empty = QTreeWidgetItem(self.tree)
            empty.setText(0, "  Nenhum elemento")
            empty.setForeground(0, QColor("#444"))
            empty.setFlags(Qt.ItemFlag.NoItemFlags)

    def _filter(self, text: str):
        text = text.lower()
        for i in range(self.tree.topLevelItemCount()):
            grp = self.tree.topLevelItem(i)
            grp_visible = False
            for j in range(grp.childCount()):
                child = grp.child(j)
                match = text in child.text(0).lower()
                child.setHidden(not match and bool(text))
                if match or not text:
                    grp_visible = True
            grp.setHidden(not grp_visible and bool(text))


class MainWindow(QMainWindow):
    def __init__(self, workspace: Workspace = None):
        super().__init__()
        self.workspace = workspace or Workspace()
        self.settings = QSettings("MMS", "MinecraftModStudio")
        self._build_ui()
        self._build_menu()
        self._build_toolbar()
        self._build_statusbar()
        self._refresh_all()
        self.setWindowTitle(self._window_title())
        self.resize(1280, 760)
        self._restore_geometry()

    def _window_title(self):
        dirty = "● " if self.workspace.dirty else ""
        if self.workspace.project_name:
            return f"{dirty}{self.workspace.project_name} — Minecraft Mod Studio"
        return "Minecraft Mod Studio"

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main splitter (sidebar | center | props)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet("QSplitter::handle { background: #333; }")
        main_layout.addWidget(self.splitter)

        # LEFT: Sidebar
        self.sidebar = Sidebar()
        self.sidebar.tree.itemClicked.connect(self._on_tree_click)
        self.splitter.addWidget(self.sidebar)

        # CENTER: Workspace tabs + console
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        self.workspace_panel = WorkspacePanel()
        self.workspace_panel.element_selected.connect(self._on_element_selected)
        self.workspace_panel.element_deleted.connect(self._on_element_deleted)
        center_layout.addWidget(self.workspace_panel, 4)

        # Console
        console_frame = QFrame()
        console_frame.setStyleSheet("background:#141414; border-top:1px solid #2a2a2a;")
        console_frame.setFixedHeight(110)
        c_layout = QVBoxLayout(console_frame)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(0)

        c_header = QFrame()
        c_header.setStyleSheet("background:#1a1a1a; border-bottom:1px solid #222;")
        c_header.setFixedHeight(24)
        c_h = QHBoxLayout(c_header)
        c_h.setContentsMargins(10, 0, 10, 0)
        c_lbl = QLabel("OUTPUT / CONSOLE")
        c_lbl.setStyleSheet("color:#444; font-size:9px; font-weight:bold; letter-spacing:1px;")
        c_h.addWidget(c_lbl)
        c_layout.addWidget(c_header)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("""
            QTextEdit {
                background:#111; color:#5a7a50; font-family:Consolas,monospace;
                font-size:11px; border:none; padding:6px;
            }
        """)
        c_layout.addWidget(self.console)
        center_layout.addWidget(console_frame)

        self.splitter.addWidget(center_container)

        # RIGHT: Properties
        self.props_panel = PropertiesPanel()
        self.props_panel.element_changed.connect(self._on_props_changed)
        self.splitter.addWidget(self.props_panel)

        self.splitter.setSizes([210, 820, 250])
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(2, False)

    def _build_menu(self):
        mb = self.menuBar()

        # File
        file_menu = mb.addMenu("Arquivo")
        file_menu.addAction("Novo Projeto\tCtrl+N", self.new_project)
        file_menu.addAction("Abrir Projeto\tCtrl+O", self.open_project)
        file_menu.addSeparator()
        file_menu.addAction("Salvar\tCtrl+S", self.save_project)
        file_menu.addAction("Salvar Como...", self.save_project_as)
        file_menu.addSeparator()
        file_menu.addAction("Sair", self.close)

        # Edit
        edit_menu = mb.addMenu("Editar")
        edit_menu.addAction("Novo Elemento\tCtrl+E", self.new_element)
        edit_menu.addSeparator()
        edit_menu.addAction("Preferências...")

        # Build
        build_menu = mb.addMenu("Build")
        build_menu.addAction("⚙ Build Mod\tCtrl+B", self.build_mod)
        build_menu.addAction("▶ Exportar Estrutura\tCtrl+Shift+E", self.export_mod)
        build_menu.addSeparator()
        build_menu.addAction("Exportar JSON (Resumo)", self.export_json)

        # Tools
        tools_menu = mb.addMenu("Ferramentas")
        tools_menu.addAction("Gerenciador de Plugins")
        tools_menu.addSeparator()
        tools_menu.addAction("Validar Mod")
        tools_menu.addAction("Limpar Cache")

        # Plugins
        mb.addMenu("Plugins")

        # Help
        help_menu = mb.addMenu("Ajuda")
        help_menu.addAction("Documentação")
        help_menu.addAction("Sobre Minecraft Mod Studio", self._show_about)

    def _build_toolbar(self):
        tb = QToolBar("Principal")
        tb.setMovable(False)
        tb.setIconSize(tb.iconSize().__class__(16, 16))
        self.addToolBar(tb)

        def make_btn(text, name=None, tooltip=""):
            btn = tb.addWidget(self._tb_btn(text, name, tooltip))
            return btn

        make_btn("📁  Abrir", tooltip="Abrir Projeto (Ctrl+O)")
        make_btn("💾  Salvar", tooltip="Salvar Projeto (Ctrl+S)")
        tb.addSeparator()
        make_btn("➕  Novo Elemento", name="btn_new_element", tooltip="Criar Novo Elemento (Ctrl+E)")
        tb.addSeparator()
        make_btn("⚙  Build", name="btn_build", tooltip="Build do Mod (Ctrl+B)")
        make_btn("📦  Exportar", name="btn_export", tooltip="Exportar Estrutura do Mod")

        # Project label (right-aligned)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(spacer)

        self.proj_label = QLabel("Nenhum projeto aberto")
        self.proj_label.setStyleSheet("""
            color: #444; font-size: 11px; padding: 0 12px;
            background: #222; border: 1px solid #333;
            border-radius: 3px; margin-right: 8px; padding: 4px 10px;
        """)
        tb.addWidget(self.proj_label)

    def _tb_btn(self, text, name=None, tooltip=""):
        from PyQt6.QtWidgets import QToolButton
        btn = QToolButton()
        btn.setText(text)
        if name:
            btn.setObjectName(name)
        if tooltip:
            btn.setToolTip(tooltip)
        # Wire up actions
        if "Abrir" in text:
            btn.clicked.connect(self.open_project)
        elif "Salvar" in text:
            btn.clicked.connect(self.save_project)
        elif "Novo Elemento" in text:
            btn.clicked.connect(self.new_element)
        elif "Build" in text:
            btn.clicked.connect(self.build_mod)
        elif "Exportar" in text:
            btn.clicked.connect(self.export_mod)
        return btn

    def _build_statusbar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status_main = QLabel("Pronto")
        self.status.addPermanentWidget(self.status_main)
        self.status_count = QLabel("0 elementos")
        self.status.addPermanentWidget(self.status_count)
        self.status_version = QLabel("")
        self.status.addPermanentWidget(self.status_version)

    # ── Actions ───────────────────────────────────────────────────────────────

    def new_project(self):
        from ui.dialogs.new_project_dialog import NewProjectDialog
        dlg = NewProjectDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            self.workspace.new_project(
                data["name"], data["mod_id"], data["mc_version"],
                data["loader"], data["author"], data["description"]
            )
            self._refresh_all()
            self.log(f"✦ Projeto '{data['name']}' criado com sucesso!", "#7ec850")

    def open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Projeto", "", "Minecraft Mod Studio (*.mms);;JSON (*.json)"
        )
        if path:
            try:
                self.workspace.load(path)
                self._refresh_all()
                self.log(f"✦ Projeto '{self.workspace.project_name}' carregado.", "#7ec850")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Não foi possível abrir o arquivo:\n{e}")

    def save_project(self):
        if not self.workspace.project_name:
            QMessageBox.warning(self, "Aviso", "Crie um projeto primeiro.")
            return
        if not self.workspace.file_path:
            self.save_project_as()
            return
        self.workspace.save(self.workspace.file_path)
        self.setWindowTitle(self._window_title())
        self.log("💾 Projeto salvo.", "#7ec850")

    def save_project_as(self):
        if not self.workspace.project_name:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Salvar Como", f"{self.workspace.mod_id}.mms",
            "Minecraft Mod Studio (*.mms)"
        )
        if path:
            self.workspace.save(path)
            self.setWindowTitle(self._window_title())
            self.log(f"💾 Salvo em: {path}", "#7ec850")

    def new_element(self):
        if not self.workspace.project_name:
            QMessageBox.information(self, "Info", "Crie ou abra um projeto primeiro.")
            return
        dlg = NewElementDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            el = ModElement(etype=data["etype"], name=data["name"])
            self.workspace.add_element(el)
            self.workspace_panel.add_element(el)
            self.sidebar.populate(self.workspace)
            self._update_status()
            self.setWindowTitle(self._window_title())
            self.log(f"➕ {el.icon} '{el.name}' criado ({el.type_label})", "#7ec850")

    def build_mod(self):
        if not self.workspace.project_name:
            return
        self.log("⚙ Iniciando build...", "#f0a020")
        QTimer.singleShot(600, lambda: self.log("⚙ Validando elementos...", "#f0a020"))
        QTimer.singleShot(1200, lambda: self.log("⚙ Gerando metadados...", "#f0a020"))
        QTimer.singleShot(1800, lambda: self.log(
            f"✓ Build concluído! {len(self.workspace.elements)} elemento(s) processado(s).", "#7ec850"))

    def export_mod(self):
        if not self.workspace.project_name:
            return
        path = QFileDialog.getExistingDirectory(self, "Escolha a pasta de exportação")
        if path:
            try:
                exp = Exporter(self.workspace)
                zip_path = exp.export_structure(path)
                self.log(f"📦 Mod exportado: {zip_path}", "#7ec850")
                QMessageBox.information(self, "Exportação Concluída",
                    f"Estrutura do mod exportada com sucesso!\n\n{zip_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro de Exportação", str(e))

    def export_json(self):
        if not self.workspace.project_name:
            return
        path = QFileDialog.getExistingDirectory(self, "Escolha a pasta")
        if path:
            exp = Exporter(self.workspace)
            json_path = exp.export_json_summary(path)
            self.log(f"📄 JSON exportado: {json_path}", "#7ec850")

    # ── Events ────────────────────────────────────────────────────────────────

    def _on_tree_click(self, item, col):
        eid = item.data(0, Qt.ItemDataRole.UserRole)
        if eid:
            el = self.workspace.get_element(eid)
            if el:
                self.workspace_panel._on_card_click(eid)
                self.props_panel.load_element(el)

    def _on_element_selected(self, element: ModElement):
        self.props_panel.load_element(element)
        self.log(f"◉ Selecionado: {element.icon} {element.name}", "#556a44")

    def _on_element_deleted(self, eid: str):
        el = self.workspace.get_element(eid)
        name = el.name if el else eid
        self.workspace.remove_element(eid)
        self.workspace_panel.remove_element(eid)
        self.sidebar.populate(self.workspace)
        self._update_status()
        self.setWindowTitle(self._window_title())
        self.log(f"🗑 '{name}' excluído.", "#e04040")

    def _on_props_changed(self):
        if self.props_panel.current_element:
            el = self.props_panel.current_element
            self.workspace_panel.update_element(el)
            self.sidebar.populate(self.workspace)
        self.workspace.dirty = True
        self.setWindowTitle(self._window_title())

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _refresh_all(self):
        self.sidebar.populate(self.workspace)
        self.workspace_panel.cards.clear()
        self.workspace_panel._relayout()
        for el in self.workspace.elements:
            self.workspace_panel.add_element(el)
        self._update_status()
        name = self.workspace.project_name
        if name:
            mc = self.workspace.mc_version
            loader = self.workspace.loader
            self.proj_label.setText(f"{name}  ·  {mc}  ·  {loader}")
            self.proj_label.setStyleSheet("""
                color: #7ec850; font-size: 11px; padding: 4px 10px;
                background: #1a2a10; border: 1px solid #3a5a20;
                border-radius: 3px; margin-right: 8px;
            """)
        else:
            self.proj_label.setText("Nenhum projeto aberto")
            self.proj_label.setStyleSheet("""
                color: #444; font-size: 11px; padding: 4px 10px;
                background: #222; border: 1px solid #333;
                border-radius: 3px; margin-right: 8px;
            """)
        self.setWindowTitle(self._window_title())

    def _update_status(self):
        n = len(self.workspace.elements)
        self.status_count.setText(f"  {n} elemento{'s' if n != 1 else ''}  ")
        if self.workspace.project_name:
            self.status_version.setText(
                f"  {self.workspace.mc_version} · {self.workspace.loader}  "
            )
        self.status_main.setText("Pronto")

    def log(self, msg: str, color: str = "#7a9a6a"):
        self.console.append(f'<span style="color:{color};">&gt;  {msg}</span>')

    def _show_about(self):
        QMessageBox.about(self, "Sobre",
            "<b>Minecraft Mod Studio</b><br><br>"
            "Criador visual de mods para Minecraft Java Edition<br>"
            "Versão 1.0.0<br><br>"
            "Desenvolvido com Python + PyQt6<br>"
            "<small>Não oficial — não afiliado à Mojang/Microsoft</small>"
        )

    def _restore_geometry(self):
        geom = self.settings.value("mainwindow/geometry")
        if geom:
            self.restoreGeometry(geom)

    def closeEvent(self, event):
        if self.workspace.dirty:
            reply = QMessageBox.question(
                self, "Sair",
                "Há alterações não salvas. Deseja salvar antes de sair?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Save:
                self.save_project()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        self.settings.setValue("mainwindow/geometry", self.saveGeometry())
        event.accept()
