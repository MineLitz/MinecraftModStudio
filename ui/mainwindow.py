import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QToolBar, QLabel, QStatusBar, QTextEdit,
    QFileDialog, QMessageBox, QFrame, QLineEdit,
    QTreeWidget, QTreeWidgetItem, QTabWidget, QSizePolicy,
    QPushButton
)
from PyQt6.QtCore import Qt, QSettings, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QAction, QIcon, QColor

from core.workspace import Workspace
from core.element import ModElement, ELEMENT_TYPES
from core.exporter import Exporter
from core.discord_rpc import rpc as discord_rpc
import core.logger as log
from ui.workspace_panel import WorkspacePanel
from ui.properties_panel import PropertiesPanel
from ui.dialogs.new_element_dialog import NewElementDialog
import ui.icons as ic


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
            grp.setText(0, f"  {info.get('label', etype)} ({len(elements)})")
            try:
                import ui.icons as ic
                grp.setIcon(0, ic.el_icon(etype))
            except Exception:
                pass
            grp.setForeground(0, QColor(info.get("color", "#aaa")))
            grp.setFont(0, QFont("Segoe UI", 10, QFont.Weight.Bold))
            grp.setExpanded(True)
            self.group_items[etype] = grp

            for el in elements:
                child = QTreeWidgetItem(grp)
                child.setText(0, f"    {el.name}")
                child.setData(0, Qt.ItemDataRole.UserRole, el.id)
                try:
                    child.setIcon(0, ic.el_icon(etype))
                except Exception:
                    pass
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
    return_to_welcome = pyqtSignal()
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
        self.resize(1100, 680)
        self._restore_geometry()
        self._center_window()
        # Discord RPC — connect in background thread
        QTimer.singleShot(2000, self._init_discord)

    def _init_discord(self):
        discord_rpc.connect()
        discord_rpc.update(
            self.workspace.project_name,
            self.workspace.project_type if self.workspace.project_name else "mod"
        )

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

        # CENTER: Tab widget (workspace / pixel art / recipe) + console
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        self.center_tabs = QTabWidget()
        self.center_tabs.setTabsClosable(True)
        self.center_tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab { padding: 6px 14px 6px 14px; font-size: 11px; }
            QTabBar::close-button {
                subcontrol-position: right;
                margin: 3px 2px 3px 4px;
            }
            QTabBar::close-button:hover {
                background: #c04040;
                border-radius: 3px;
            }
        """)
        self.center_tabs.tabCloseRequested.connect(self._on_tab_close)

        # Tab 0: Workspace (Mod mode)
        self.workspace_panel = WorkspacePanel()
        self.workspace_panel.element_selected.connect(self._on_element_selected)
        self.workspace_panel.element_deleted.connect(self._on_element_deleted)
        self.center_tabs.addTab(self.workspace_panel, "Workspace")
        try: self.center_tabs.setTabIcon(0, ic.tab_workspace())
        except Exception: pass

        # Tab 1: Pixel Art Editor (16×16 / 32×32)
        from ui.pixel_editor import PixelArtEditor
        self.pixel_editor = PixelArtEditor()
        self.pixel_editor.texture_exported.connect(
            lambda p: self.log(f"Textura exportada: {p}", "#6ab84a"))
        self.center_tabs.addTab(self.pixel_editor, "Pixel Art")
        try: self.center_tabs.setTabIcon(1, ic.tab_pixel_art())
        except Exception: pass

        # Tab 2: Recipe Editor
        from ui.recipe_editor import RecipeEditor
        self.recipe_editor = RecipeEditor()
        self.recipe_editor.recipe_changed.connect(self._on_recipe_changed)
        self.center_tabs.addTab(self.recipe_editor, "Receita")
        try: self.center_tabs.setTabIcon(2, ic.tab_recipe())
        except Exception: pass

        # Tab 3: Resource Pack Editor
        from ui.resource_pack_panel import ResourcePackPanel
        self.rp_panel = ResourcePackPanel()
        self.rp_panel.texture_modified.connect(self._on_rp_texture_modified)
        self.rp_panel.open_texture.connect(self._open_texture_in_editor)
        self.center_tabs.addTab(self.rp_panel, "Resource Pack")
        try: self.center_tabs.setTabIcon(3, ic.tab_pixel_art())
        except Exception: pass

        self.workspace_panel.texture_card_clicked.connect(
            self._on_workspace_texture_click)

        center_layout.addWidget(self.center_tabs, 4)

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

        def action(menu, text, callback, icon_fn=None, shortcut=None):
            a = QAction(text, self)
            if icon_fn:
                try: a.setIcon(icon_fn())
                except Exception: pass
            if shortcut:
                a.setShortcut(shortcut)
            a.triggered.connect(callback)
            menu.addAction(a)
            return a

        # File
        file_menu = mb.addMenu("Arquivo")
        action(file_menu, "Novo Projeto",    self.new_project,    ic.menu_new,      "Ctrl+N")
        action(file_menu, "Abrir Projeto",   self.open_project,   ic.menu_open,     "Ctrl+O")
        file_menu.addSeparator()
        action(file_menu, "Salvar",          self.save_project,   ic.menu_save,     "Ctrl+S")
        action(file_menu, "Salvar Como...",  self.save_project_as,ic.menu_save_as)
        file_menu.addSeparator()
        action(file_menu, "Voltar ao Menu",  self._go_to_menu,    ic.menu_back)
        file_menu.addSeparator()
        action(file_menu, "Sair",            self.close,          ic.menu_quit)

        # Edit
        edit_menu = mb.addMenu("Editar")
        action(edit_menu, "Novo Elemento",   self.new_element,    ic.menu_new_element, "Ctrl+E")
        edit_menu.addSeparator()
        action(edit_menu, "Preferências...", self.open_settings,  ic.menu_preferences)

        # Exibir
        view_menu = mb.addMenu("Exibir")

        self._act_sidebar = view_menu.addAction("Sidebar")
        self._act_sidebar.setCheckable(True)
        self._act_sidebar.setChecked(True)
        self._act_sidebar.triggered.connect(
            lambda checked: self._toggle_panel("sidebar", checked))

        self._act_props = view_menu.addAction("Propriedades")
        self._act_props.setCheckable(True)
        self._act_props.setChecked(True)
        self._act_props.triggered.connect(
            lambda checked: self._toggle_panel("props", checked))

        self._act_console = view_menu.addAction("Console")
        self._act_console.setCheckable(True)
        self._act_console.setChecked(True)
        self._act_console.triggered.connect(
            lambda checked: self._toggle_panel("console", checked))

        view_menu.addSeparator()

        # Tab visibility actions — stored so we can sync checkmarks on close
        self._tab_actions: dict[int, QAction] = {}
        tab_defs = [
            (0, "Workspace",     "Ctrl+1"),
            (1, "Pixel Art",     "Ctrl+2"),
            (2, "Receita",       "Ctrl+3"),
            (3, "Resource Pack", "Ctrl+4"),
        ]
        for idx, label, key in tab_defs:
            a = QAction(label, self)
            a.setShortcut(key)
            a.setCheckable(True)
            a.setChecked(True)
            a.triggered.connect(lambda checked, i=idx: self._set_tab_visible(i, checked))
            view_menu.addAction(a)
            self._tab_actions[idx] = a

        # Build
        build_menu = mb.addMenu("Build")
        action(build_menu, "Build Mod",            self.build_mod,      ic.menu_build,         "Ctrl+B")
        action(build_menu, "Exportar Estrutura",   self.export_mod,     ic.menu_export_struct, "Ctrl+Shift+E")
        action(build_menu, "Gerar Código Java",    self.generate_java,  ic.menu_export_java)
        build_menu.addSeparator()
        action(build_menu, "Exportar JSON",        self.export_json,    ic.menu_export_json)

        # Tools
        tools_menu = mb.addMenu("Ferramentas")
        action(tools_menu, "Validar Mod",          self.validate_mod,   ic.menu_validate, "Ctrl+Shift+V")
        action(tools_menu, "Gerenciador de Plugins",
               lambda: self._show_coming_soon("Gerenciador de Plugins"), ic.menu_plugins)
        tools_menu.addSeparator()
        action(tools_menu, "Preferências",         self.open_settings,  ic.menu_preferences)

        # Plugins
        plugins_menu = mb.addMenu("Plugins")
        action(plugins_menu, "Instalar Plugin...",
               lambda: self._show_coming_soon("Sistema de Plugins"), ic.menu_plugins)
        action(plugins_menu, "Gerenciar Plugins",
               lambda: self._show_coming_soon("Sistema de Plugins"), ic.menu_plugins)
        plugins_menu.addSeparator()
        action(plugins_menu, "Explorar Marketplace",
               lambda: self._show_coming_soon("Plugin Marketplace"), ic.menu_plugins)

        # Help
        help_menu = mb.addMenu("Ajuda")
        action(help_menu, "Documentação",
               lambda: self._show_coming_soon("Documentação"), ic.menu_docs)
        action(help_menu, "Atalhos de Teclado",
               lambda: self._show_coming_soon("Atalhos de Teclado"), ic.menu_about)
        help_menu.addSeparator()
        help_menu.addAction("🔄  Reiniciar App", self._restart_app)
        help_menu.addAction("📋  Ver Arquivo de Log", self._open_log)
        help_menu.addSeparator()
        action(help_menu, "Sobre Minecraft Mod Studio", self._show_about, ic.menu_about)

    def _build_toolbar(self):
        tb = QToolBar("Principal")
        tb.setMovable(False)
        tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(tb)

        def tbtn(text, icon_fn, name=None, tooltip="", callback=None):
            from PyQt6.QtWidgets import QToolButton
            btn = QToolButton()
            btn.setText(f"  {text}")
            try: btn.setIcon(icon_fn())
            except Exception: pass
            if name: btn.setObjectName(name)
            if tooltip: btn.setToolTip(tooltip)
            if callback: btn.clicked.connect(callback)
            tb.addWidget(btn)
            return btn

        tbtn("Abrir",        ic.toolbar_open,        tooltip="Abrir Projeto (Ctrl+O)",    callback=self.open_project)
        tbtn("Salvar",       ic.toolbar_save,        tooltip="Salvar Projeto (Ctrl+S)",   callback=self.save_project)
        tb.addSeparator()
        tbtn("Novo Elemento",ic.toolbar_new_element, name="btn_new_element",
             tooltip="Criar Novo Elemento (Ctrl+E)",  callback=self.new_element)
        tb.addSeparator()
        tbtn("Build",        ic.toolbar_build,       name="btn_build",
             tooltip="Build do Mod (Ctrl+B)",          callback=self.build_mod)
        tbtn("Exportar",     ic.toolbar_export,      name="btn_export",
             tooltip="Exportar Estrutura do Mod",      callback=self.export_mod)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(spacer)

        self.proj_label = QLabel("Nenhum projeto aberto")
        self.proj_label.setStyleSheet("""
            color: #444; font-size: 11px; padding: 4px 10px;
            background: #222; border: 1px solid #333;
            border-radius: 3px; margin-right: 4px;
        """)
        tb.addWidget(self.proj_label)

        # Settings button
        from PyQt6.QtWidgets import QToolButton
        settings_btn = QToolButton()
        settings_btn.setToolTip("Configurações")
        try: settings_btn.setIcon(ic.toolbar_settings())
        except Exception: settings_btn.setText("⚙")
        settings_btn.clicked.connect(self.open_settings)
        tb.addWidget(settings_btn)

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

    def _go_to_menu(self):
        if self.workspace.dirty:
            reply = QMessageBox.question(
                self, "Voltar ao Menu",
                "Há alterações não salvas. Deseja salvar antes de voltar ao menu?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Save:
                self.save_project()
                if self.workspace.dirty:
                    return  # save was cancelled
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        self.return_to_welcome.emit()

    def new_project(self):
        from ui.dialogs.new_project_dialog import NewProjectDialog
        dlg = NewProjectDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            self.workspace.new_project(
                data["name"], data["mod_id"], data["mc_version"],
                data["loader"], data["author"], data["description"],
                data["project_type"]
            )
            self._refresh_all()
            ptype = "Resource Pack" if data["project_type"] == "resource_pack" else "Mod"
            self.log(f"✦ {ptype} '{data['name']}' criado com sucesso!", "#6ab84a")

    def open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Projeto", "", "Minecraft Mod Studio (*.mms);;JSON (*.json)"
        )
        if path:
            try:
                self.workspace.load(path)
                self._refresh_all()
                log.info(f"Projeto aberto: {path}")
                self.log(f"✦ Projeto '{self.workspace.project_name}' carregado.", "#6ab84a")
            except Exception as e:
                log.exception(f"Erro ao abrir projeto: {path}")
                QMessageBox.critical(self, "Erro", f"Não foi possível abrir o arquivo:\n{e}")

    def save_project(self):
        if not self.workspace.project_name:
            QMessageBox.warning(self, "Aviso", "Crie um projeto primeiro.")
            return
        if not self.workspace.file_path:
            self.save_project_as()
            return
        try:
            self.workspace.save(self.workspace.file_path)
            self.setWindowTitle(self._window_title())
            log.info(f"Projeto salvo: {self.workspace.file_path}")
            self.log("Projeto salvo.", "#6ab84a")
        except Exception as e:
            log.exception("Erro ao salvar projeto")
            QMessageBox.critical(self, "Erro ao salvar", str(e))

    def save_project_as(self):
        if not self.workspace.project_name:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Salvar Como", f"{self.workspace.mod_id}.mms",
            "Minecraft Mod Studio (*.mms)"
        )
        if path:
            try:
                self.workspace.save(path)
                self.setWindowTitle(self._window_title())
                log.info(f"Projeto salvo como: {path}")
                self.log(f"Salvo em: {path}", "#6ab84a")
            except Exception as e:
                log.exception("Erro ao salvar projeto como")
                QMessageBox.critical(self, "Erro ao salvar", str(e))

    def _on_rp_texture_modified(self, mc_folder: str, tex_name: str):
        """When a texture is saved to memory, add/update its card in the workspace."""
        key = f"{mc_folder}/{tex_name}"
        img = self.rp_panel.modified.get(key)
        if img is None:
            return
        display = tex_name.split("/")[-1].replace("_", " ")
        self.workspace_panel.add_texture_card(key, display, img)
        self.log(f"Textura modificada: {key}.png", "#6ab84a")

    def _on_workspace_texture_click(self, key: str):
        """Clicking a texture card in workspace selects it in the RP panel and opens editor."""
        # Switch to RP tab first
        self.center_tabs.setCurrentIndex(3)
        # Find and click the matching tile in rp_panel
        parts = key.split("/", 1)
        if len(parts) == 2:
            mc_folder, tex_name = parts
            tile = next((t for t in self.rp_panel.tiles
                         if t.mc_folder == mc_folder and t.tex_name == tex_name), None)
            if tile:
                tile.clicked.emit(tile.display_name, tile.mc_folder,
                                  tile.tex_name, tile.custom_path or tile.local_path)
            else:
                # Tile not visible in current category — open editor directly from memory
                img = self.rp_panel.modified.get(key)
                if img is not None:
                    import tempfile
                    tmp = os.path.join(tempfile.gettempdir(),
                                       f"mms_ws_{tex_name.replace('/','_')}.png")
                    img.save(tmp, "PNG")
                    native = max(img.width(), img.height())
                    self._open_texture_in_editor(tmp, native)

    def _open_texture_in_editor(self, path: str, native_size: int):
        """Route texture to pixel editor (≤32) or open ImageEditor popup (≥64)."""
        if native_size <= 32:
            self.pixel_editor.canvas.clear()
            self.rp_panel._png_to_canvas(path)
            self.center_tabs.setTabVisible(1, True)
            self.center_tabs.setCurrentIndex(1)
            if 1 in self._tab_actions:
                self._tab_actions[1].setChecked(True)
        else:
            from ui.image_editor import ImageEditor
            tex_name = os.path.splitext(os.path.basename(path))[0]
            # Keep reference so window isn't garbage collected
            if not hasattr(self, "_img_editor_windows"):
                self._img_editor_windows = []
            # Reuse existing window for same texture
            for w in self._img_editor_windows:
                if w.isVisible() and w._tex_name == tex_name:
                    w.raise_()
                    w.activateWindow()
                    return
            dlg = ImageEditor(parent=self, path=path, tex_name=tex_name)
            # texture_exported → user chose "Exportar PNG" (writes to file they picked)
            dlg.texture_exported.connect(
                lambda p: self.log(f"Textura exportada: {p}", "#6ab84a"))
            # texture_saved → user chose "Salvar no Projeto" (QImage in memory, no disk)
            dlg.texture_saved.connect(
                lambda img: self.rp_panel._on_image_saved_from_editor(img))
            dlg.destroyed.connect(
                lambda: self._img_editor_windows.remove(dlg)
                if dlg in self._img_editor_windows else None)
            self._img_editor_windows.append(dlg)
            dlg.show()
            dlg.raise_()
            self.log(f"Abrindo editor: {tex_name} ({native_size}×{native_size})", "#6ab84a")

    def _on_tab_close(self, index: int):
        self.center_tabs.setTabVisible(index, False)
        if index in self._tab_actions:
            self._tab_actions[index].setChecked(False)

    def _set_tab_visible(self, index: int, visible: bool):
        self.center_tabs.setTabVisible(index, visible)
        if visible:
            self.center_tabs.setCurrentIndex(index)

    def _toggle_panel(self, which: str, checked: bool = None):
        if which == "sidebar":
            w = self.splitter.widget(0)
            visible = checked if checked is not None else not w.isVisible()
            w.setVisible(visible)
        elif which == "props":
            w = self.splitter.widget(2)
            visible = checked if checked is not None else not w.isVisible()
            w.setVisible(visible)
        elif which == "console":
            center = self.splitter.widget(1)
            lay = center.layout()
            if lay and lay.count() >= 2:
                item = lay.itemAt(lay.count() - 1)
                if item and item.widget():
                    visible = checked if checked is not None else not item.widget().isVisible()
                    item.widget().setVisible(visible)

    def _center_window(self):
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        self.move((screen.width() - self.width()) // 2,
                  (screen.height() - self.height()) // 2)

    def new_element(self):
        if not self.workspace.project_name:
            QMessageBox.information(self, "Info", "Crie ou abra um projeto primeiro.")
            return
        if self.workspace.project_type == "resource_pack":
            QMessageBox.information(self, "Info",
                "Elementos não são usados em Resource Packs.\n"
                "Use o editor de texturas na aba Resource Pack.")
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
            QMessageBox.information(self, "Info", "Abra ou crie um projeto primeiro.")
            return

        # 1. Validate first
        from core.validator import ModValidator
        issues = ModValidator(self.workspace).validate()
        errors = [i for i in issues if i.level == "error"]
        if errors:
            msg = "\n".join(f"• {i.element_name}: {i.message}" for i in errors)
            reply = QMessageBox.warning(
                self, "Erros de Validação",
                f"O mod tem {len(errors)} erro(s):\n\n{msg}\n\n"
                "Deseja continuar mesmo assim?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # 2. Check Java
        from core.java_checker import check_java_for_minecraft, check_java
        java_ok, java_msg = check_java_for_minecraft()
        if not java_ok:
            reply = QMessageBox.warning(
                self, "Java não encontrado",
                java_msg + "\n\nDeseja apenas gerar o código sem compilar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.generate_java()
            return

        # 3. Choose output folder
        out_dir = QFileDialog.getExistingDirectory(
            self, "Pasta para gerar e compilar o mod")
        if not out_dir:
            return

        try:
            from core.java_generator import JavaGenerator
            gen = JavaGenerator(self.workspace)
            zip_path = gen.generate(out_dir)
            self.log(f"☕ Código gerado: {zip_path}", "#6ab84a")

            # Extract project
            import zipfile as zf
            with zf.ZipFile(zip_path, "r") as z:
                z.extractall(out_dir)

            loader = self.ws.loader.lower()
            suffix = "fabric" if "fabric" in loader or "quilt" in loader else \
                     "forge"  if "forge" in loader and "neo" not in loader else "neoforge"
            project_dir = os.path.join(out_dir, f"{self.ws.mod_id}_{suffix}")

            if not os.path.exists(project_dir):
                QMessageBox.warning(self, "Erro",
                    f"Pasta do projeto não encontrada:\n{project_dir}")
                return

            java_info = check_java()
            from ui.dialogs.build_dialog import BuildDialog
            dlg = BuildDialog(
                project_dir=project_dir,
                project_name=self.ws.project_name,
                loader=self.ws.loader,
                java_path=java_info.path or "java",
                parent=self
            )
            dlg.start_build()
            if dlg.exec():
                self.log("✅ Build concluído com sucesso!", "#6ab84a")
            else:
                self.log("❌ Build falhou ou foi cancelado.", "#c04040")

        except Exception as e:
            QMessageBox.critical(self, "Erro no Build", str(e))
            self.log(f"❌ Erro: {e}", "#c04040")

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
        # Switch to relevant tab
        if element.etype in ("item", "block"):
            self.pixel_editor.load_element(element)
            self.center_tabs.setCurrentIndex(1)
        elif element.etype == "recipe":
            self.recipe_editor.load_element(element)
            self.center_tabs.setCurrentIndex(2)

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
            ptype = "Resource Pack" if self.workspace.project_type == "resource_pack" else "Mod"
            if self.workspace.project_type == "resource_pack":
                label_text = f"{name}  ·  {ptype}  ·  MC {mc}"
            else:
                loader = self.workspace.loader
                label_text = f"{name}  ·  {ptype}  ·  {mc}  ·  {loader}"
            self.proj_label.setText(label_text)
            self.proj_label.setStyleSheet("""
                color: #6ab84a; font-size: 11px; padding: 4px 10px;
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
        discord_rpc.update(
            self.workspace.project_name,
            getattr(self.workspace, "project_type", "mod")
        )
        # Auto-switch tabs based on project type
        if not hasattr(self, "rp_panel"):
            return
        is_rp = self.workspace.project_type == "resource_pack"

        # Switch workspace panel mode
        self.workspace_panel.set_rp_mode(is_rp)

        if is_rp and self.workspace.project_name:
            pack_dir = ""
            if self.workspace.file_path:
                pack_dir = os.path.dirname(self.workspace.file_path)
            self.rp_panel.load_pack(
                pack_dir,
                self.workspace.project_name,
                self.workspace.mc_version
            )
            self.center_tabs.setCurrentIndex(3)
        else:
            self.center_tabs.setCurrentIndex(0)

    def _update_status(self):
        n = len(self.workspace.elements)
        self.status_count.setText(f"  {n} elemento{'s' if n != 1 else ''}  ")
        if self.workspace.project_name:
            if self.workspace.project_type == "resource_pack":
                self.status_version.setText(
                    f"  MC {self.workspace.mc_version}  ")
            else:
                self.status_version.setText(
                    f"  {self.workspace.mc_version} · {self.workspace.loader}  "
                )
        self.status_main.setText("Pronto")

    def log(self, msg: str, color: str = "#7a9a6a"):
        self.console.append(f'<span style="color:{color};">&gt;  {msg}</span>')

    def _on_recipe_changed(self, data: dict):
        el = self.props_panel.current_element
        if el and el.etype == "recipe":
            el.props.update(data)
            self.workspace.dirty = True
            self.setWindowTitle(self._window_title())

    def validate_mod(self):
        if not self.workspace.project_name:
            QMessageBox.information(self, "Info", "Abra um projeto primeiro.")
            return
        from ui.dialogs.validator_dialog import ValidatorDialog
        dlg = ValidatorDialog(self.workspace, self)
        dlg.exec()

    def generate_java(self):
        if not self.workspace.project_name:
            QMessageBox.information(self, "Info", "Abra um projeto primeiro.")
            return
        path = QFileDialog.getExistingDirectory(self, "Pasta para gerar o código")
        if not path:
            return
        try:
            from core.java_generator import JavaGenerator
            gen = JavaGenerator(self.workspace)
            zip_path = gen.generate(path)
            self.log(f"☕ Código Java gerado: {zip_path}", "#6ab84a")
            QMessageBox.information(self, "Código Gerado",
                f"Projeto Java gerado com sucesso!\n\n{zip_path}\n\n"
                "Extraia o ZIP e abra no IntelliJ IDEA ou Eclipse.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def _open_log(self):
        log_path = log.get_log_path()
        if os.path.exists(log_path):
            os.startfile(log_path)
        else:
            QMessageBox.information(self, "Log", "Nenhum arquivo de log encontrado.")

    def _restart_app(self):
        if self.workspace.dirty:
            reply = QMessageBox.question(
                self, "Reiniciar",
                "Há alterações não salvas. Deseja salvar antes de reiniciar?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Save:
                self.save_project()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        from ui.dialogs.settings_dialog import restart_app
        restart_app()

    def open_settings(self):
        from ui.dialogs.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self)
        dlg.settings_changed.connect(self._on_settings_changed)
        dlg.exec()

    def _on_settings_changed(self):
        from PyQt6.QtWidgets import QApplication
        from ui.theme import build_theme
        from ui.font_loader import load_fonts
        s = QSettings("MMS", "MinecraftModStudio")
        theme   = s.value("appearance/theme", "dark")
        fsize   = s.value("appearance/font_size", "medium")
        fname   = load_fonts()
        QApplication.instance().setStyleSheet(build_theme(theme, fname, fsize))
        self.log("⚙ Configurações aplicadas.", "#6ab84a")

    def _show_coming_soon(self, feature: str):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout
        dlg = QDialog(self)
        dlg.setWindowTitle("Em Breve")
        dlg.setFixedSize(380, 220)
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(36, 36, 36, 28)
        lay.setSpacing(12)

        icon = QLabel("🚧")
        icon.setFont(QFont("Segoe UI Emoji", 36))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("background:transparent;")
        lay.addWidget(icon)

        title = QLabel(feature)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color:#d0d0d0; font-size:15px; font-weight:600; background:transparent;")
        lay.addWidget(title)

        sub = QLabel("Esta funcionalidade está em desenvolvimento\ne chegará em breve.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)
        sub.setStyleSheet("color:#606060; font-size:12px; background:transparent;")
        lay.addWidget(sub)

        lay.addStretch()

        btn = QPushButton("OK")
        btn.setFixedWidth(100)
        btn.clicked.connect(dlg.accept)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn)
        btn_row.addStretch()
        lay.addLayout(btn_row)
        dlg.exec()

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
        # Restore tab visibility
        if self.settings.value("projects/remember_tabs", True, type=bool):
            for idx, act in self._tab_actions.items():
                visible = self.settings.value(f"ui/tab_{idx}_visible", True, type=bool)
                self.center_tabs.setTabVisible(idx, visible)
                act.setChecked(visible)
        log.info("MainWindow geometry restored")

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
        # Save tab visibility state
        for idx in self._tab_actions:
            self.settings.setValue(
                f"ui/tab_{idx}_visible",
                self.center_tabs.isTabVisible(idx))
        discord_rpc.disconnect()
        log.info("MainWindow closed")
        event.accept()
