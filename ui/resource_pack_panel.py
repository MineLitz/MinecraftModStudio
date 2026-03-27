import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSplitter, QLineEdit, QComboBox,
    QGridLayout, QProgressBar, QTabWidget, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap

from core.asset_fetcher import (
    get_texture_path_async, get_category_items,
    get_category_names, prefetch_category
)

THUMB = 48


class TextureTile(QFrame):
    clicked = pyqtSignal(str, str, str, str)   # display_name, mc_folder, tex_name, path
    _ready  = pyqtSignal(str)                  # path — QueuedConnection → main thread

    def __init__(self, display_name: str, mc_folder: str, tex_name: str,
                 mc_version: str, parent=None):
        super().__init__(parent)
        self.display_name = display_name
        self.mc_folder    = mc_folder
        self.tex_name     = tex_name
        self.mc_version   = mc_version
        self.local_path   = ""
        self.custom_path  = ""
        self.selected     = False
        self._alive       = True

        self._ready.connect(self._apply, Qt.ConnectionType.QueuedConnection)
        self.setFixedSize(84, 90)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build()
        self._update_style()
        get_texture_path_async(mc_version, mc_folder, tex_name, self._cb)

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 5, 4, 4)
        lay.setSpacing(2)

        self._img = QLabel("…")
        self._img.setFixedSize(THUMB, THUMB)
        self._img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._img.setStyleSheet(
            "background:#141414;border:1px solid #2a2a2a;"
            "border-radius:3px;color:#444;font-size:16px;")
        lay.addWidget(self._img, alignment=Qt.AlignmentFlag.AlignCenter)

        n = self.display_name
        self._lbl = QLabel(n[:13] + "…" if len(n) > 13 else n)
        self._lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl.setStyleSheet(
            "background:transparent;border:none;color:#777;font-size:9px;")
        lay.addWidget(self._lbl)

        self._dot = QLabel("● editada")
        self._dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._dot.setStyleSheet(
            "background:transparent;color:#6ab84a;font-size:8px;")
        self._dot.hide()
        lay.addWidget(self._dot)

    def _cb(self, name: str, path: str):
        if self._alive:
            try:
                if path:
                    self._ready.emit(path)
                else:
                    self._ready.emit("")   # empty = not found
            except RuntimeError: pass

    def _apply(self, path: str):
        if not self._alive: return
        try:
            if not path:
                # Texture not found in repo — show warning
                self._img.setText("?")
                self._img.setStyleSheet(
                    "background:#1a1010;border:1px solid #3a2020;"
                    "border-radius:3px;color:#604040;font-size:13px;")
                self._lbl.setStyleSheet(
                    "background:transparent;border:none;color:#504040;font-size:9px;")
                return
            self.local_path = path
            px = QPixmap(path).scaled(
                THUMB, THUMB,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation)
            self._img.setPixmap(px)
            self._img.setText("")
            self._img.setStyleSheet(
                "background:transparent;border:none;")
        except RuntimeError: pass

    def set_custom(self, path: str):
        self.custom_path = path
        if path and os.path.exists(path):
            px = QPixmap(path).scaled(
                THUMB, THUMB,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)  # smooth for custom
            self._img.setPixmap(px)
            self._img.setText("")
            self._dot.show()
        self._update_style()

    def set_selected(self, v: bool):
        self.selected = v
        self._update_style()

    def _update_style(self):
        if self.selected:
            self.setStyleSheet(
                "QFrame{background:#1a2a10;border:2px solid #6ab84a;border-radius:6px;}")
        elif self.custom_path:
            self.setStyleSheet(
                "QFrame{background:#1a2010;border:1px solid #3a5a20;border-radius:6px;}"
                "QFrame:hover{border-color:#4a7a28;}")
        else:
            self.setStyleSheet(
                "QFrame{background:#1e1e1e;border:1px solid #252525;border-radius:6px;}"
                "QFrame:hover{background:#242424;border-color:#363636;}")

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.display_name, self.mc_folder,
                              self.tex_name, self.custom_path or self.local_path)

    def deleteLater(self):
        self._alive = False
        super().deleteLater()


class ResourcePackPanel(QWidget):
    texture_modified = pyqtSignal(str, str)
    open_texture     = pyqtSignal(str, int)  # path, native_size → routed by mainwindow

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mc_version  = "1.21.4"
        self.pack_name   = ""
        self.pack_dir    = ""
        self.pack_icon   = ""
        self.tiles: list[TextureTile] = []
        self.selected_tile: TextureTile | None = None
        # In-memory: "mc_folder/tex_name" → QImage — nothing written to disk until export
        from PyQt6.QtGui import QImage
        self.modified: dict[str, QImage] = {}
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0)
        root.setSpacing(0)

        # ── Top bar ───────────────────────────────────────────────────────────
        top = QFrame()
        top.setStyleSheet("background:#1e1e1e;border-bottom:1px solid #2a2a2a;")
        top.setFixedHeight(42)
        tl = QHBoxLayout(top)
        tl.setContentsMargins(10,0,10,0)
        tl.setSpacing(8)

        cat_lbl = QLabel("Categoria:")
        cat_lbl.setStyleSheet("color:#666;font-size:11px;")
        tl.addWidget(cat_lbl)

        self._cat = QComboBox()
        for name in get_category_names():
            self._cat.addItem(name)
        self._cat.setFixedWidth(130)
        self._cat.currentIndexChanged.connect(self._load_tiles)
        tl.addWidget(self._cat)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Buscar textura...")
        self._search.setFixedWidth(170)
        self._search.textChanged.connect(self._filter)
        tl.addWidget(self._search)

        # MC version label (read-only, set at project creation)
        self._ver_lbl = QLabel(f"MC {self.mc_version}")
        self._ver_lbl.setStyleSheet(
            "color:#4a6a30;font-size:11px;padding:2px 8px;"
            "background:#1a2a10;border:1px solid #2a4a18;border-radius:3px;")
        tl.addWidget(self._ver_lbl)

        tl.addStretch()

        self._progress = QProgressBar()
        self._progress.setFixedSize(120, 6)
        self._progress.setRange(0,100)
        self._progress.setStyleSheet(
            "QProgressBar{background:#2a2a2a;border-radius:3px;border:none;}"
            "QProgressBar::chunk{background:#6ab84a;border-radius:3px;}")
        self._progress.hide()
        tl.addWidget(self._progress)

        self._status = QLabel("Selecione uma textura para editar")
        self._status.setStyleSheet("color:#505050;font-size:11px;")
        tl.addWidget(self._status)

        exp_btn = QPushButton("Exportar Pack")
        exp_btn.setObjectName("btn_primary")
        exp_btn.setFixedHeight(28)
        exp_btn.clicked.connect(self._export_pack)
        tl.addWidget(exp_btn)

        root.addWidget(top)

        # ── Splitter ──────────────────────────────────────────────────────────
        sp = QSplitter(Qt.Orientation.Horizontal)
        sp.setHandleWidth(1)
        sp.setStyleSheet("QSplitter::handle{background:#2a2a2a;}")

        # Left browser
        browser = QFrame()
        browser.setStyleSheet("background:#181818;")
        bl = QVBoxLayout(browser)
        bl.setContentsMargins(0,0,0,0)
        bl.setSpacing(0)

        hdr = QLabel("TEXTURAS VANILLA")
        hdr.setStyleSheet(
            "color:#404040;font-size:9px;font-weight:bold;letter-spacing:1px;"
            "padding:5px 10px;background:#1a1a1a;border-bottom:1px solid #222;")
        bl.addWidget(hdr)

        # Category info banner
        self._cat_info = QLabel("")
        self._cat_info.setStyleSheet(
            "background:#1a2010;border:1px solid #2a4018;border-radius:4px;"
            "color:#4a7a30;font-size:11px;padding:5px 10px;")
        self._cat_info.hide()
        bl.addWidget(self._cat_info)

        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sc.setStyleSheet("QScrollArea{border:none;background:#181818;}")
        self._gw = QWidget()
        self._gw.setStyleSheet("background:#181818;")
        self._gl = QGridLayout(self._gw)
        self._gl.setContentsMargins(8,8,8,8)
        self._gl.setSpacing(6)
        self._gl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        sc.setWidget(self._gw)
        bl.addWidget(sc)
        sp.addWidget(browser)

        # Right editor
        right = QFrame()
        right.setStyleSheet("background:#1e1e1e;")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0,0,0,0)
        rl.setSpacing(0)

        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(
            "QTabWidget::pane{border:none;}"
            "QTabBar::tab{padding:5px 14px;font-size:11px;}")

        from ui.pixel_editor import PixelArtEditor
        self.pixel_editor = PixelArtEditor()
        self.pixel_editor.texture_exported.connect(self._on_exported)
        self._tabs.addTab(self.pixel_editor, "Editor de Pixel")

        # Lang editor tab
        from ui.lang_editor import LangEditor
        self.lang_editor = LangEditor()
        self._tabs.addTab(self.lang_editor, "Idioma / Textos")

        # Pack icon tab
        self._icon_tab = self._build_icon_tab()
        self._tabs.addTab(self._icon_tab, "Ícone do Pack")

        rl.addWidget(self._tabs)

        # ── Save-to-project bar ───────────────────────────────────────────────
        save_bar = QFrame()
        save_bar.setStyleSheet(
            "background:#181818;border-top:1px solid #2a2a2a;")
        save_bar.setFixedHeight(46)
        sl = QHBoxLayout(save_bar)
        sl.setContentsMargins(12, 0, 12, 0)
        sl.setSpacing(10)

        self._save_hint = QLabel("Selecione e edite uma textura, depois salve no projeto")
        self._save_hint.setStyleSheet("color:#444;font-size:11px;")
        sl.addWidget(self._save_hint)
        sl.addStretch()

        self._save_btn = QPushButton("💾  Salvar no Projeto")
        self._save_btn.setObjectName("btn_primary")
        self._save_btn.setFixedHeight(30)
        self._save_btn.setFixedWidth(160)
        self._save_btn.setEnabled(False)
        self._save_btn.clicked.connect(self._save_to_project)
        sl.addWidget(self._save_btn)

        rl.addWidget(save_bar)
        rl.addWidget(self._build_info())
        sp.addWidget(right)
        sp.setSizes([400, 520])
        root.addWidget(sp)

        QTimer.singleShot(100, self._load_tiles)

    def _build_icon_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background:#1e1e1e;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(32,32,32,32)
        lay.setSpacing(16)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("Ícone do Resource Pack")
        title.setStyleSheet("color:#d0d0d0;font-size:14px;font-weight:bold;")
        lay.addWidget(title)

        sub = QLabel(
            "O ícone aparece na tela de seleção de resource packs do Minecraft.\n"
            "Tamanho recomendado: 128×128 pixels (PNG).")
        sub.setStyleSheet("color:#555;font-size:11px;")
        lay.addWidget(sub)

        preview_row = QHBoxLayout()
        preview_row.setSpacing(24)

        self._icon_preview = QLabel()
        self._icon_preview.setFixedSize(128,128)
        self._icon_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_preview.setStyleSheet(
            "background:#141414;border:2px dashed #333;border-radius:8px;color:#444;font-size:11px;")
        self._icon_preview.setText("Sem ícone")
        preview_row.addWidget(self._icon_preview)

        btn_col = QVBoxLayout()
        btn_col.setSpacing(8)
        btn_col.setAlignment(Qt.AlignmentFlag.AlignTop)

        upload_btn = QPushButton("📂  Escolher imagem...")
        upload_btn.setFixedHeight(34)
        upload_btn.clicked.connect(self._pick_icon)
        btn_col.addWidget(upload_btn)

        clear_btn = QPushButton("🗑  Remover ícone")
        clear_btn.setFixedHeight(34)
        clear_btn.clicked.connect(self._clear_icon)
        btn_col.addWidget(clear_btn)

        self._icon_path_lbl = QLabel("Nenhum arquivo selecionado")
        self._icon_path_lbl.setStyleSheet("color:#444;font-size:10px;")
        btn_col.addWidget(self._icon_path_lbl)

        preview_row.addLayout(btn_col)
        preview_row.addStretch()
        lay.addLayout(preview_row)
        return w

    def _pick_icon(self):
        path, _ = QFileDialog.getOpenFileName(
            self,"Escolher ícone do pack","","Imagens (*.png *.jpg *.jpeg)")
        if path:
            self.pack_icon = path
            px = QPixmap(path).scaled(
                128,128, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            self._icon_preview.setPixmap(px)
            self._icon_preview.setText("")
            self._icon_path_lbl.setText(os.path.basename(path))

    def _clear_icon(self):
        self.pack_icon = ""
        self._icon_preview.clear()
        self._icon_preview.setText("Sem ícone")
        self._icon_path_lbl.setText("Nenhum arquivo selecionado")
        w = QWidget()
        w.setStyleSheet("background:#1e1e1e;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(20,20,20,20)
        lay.setSpacing(24)

        def mk(label, color):
            col = QVBoxLayout()
            l = QLabel(label)
            l.setStyleSheet(f"color:{color};font-size:10px;font-weight:bold;")
            col.addWidget(l)
            img = QLabel()
            img.setFixedSize(128,128)
            img.setAlignment(Qt.AlignmentFlag.AlignCenter)
            img.setStyleSheet(
                "background:#111;border:1px solid #2a2a2a;border-radius:4px;color:#444;font-size:10px;")
            col.addWidget(img)
            return col, img

        vc, self._v_prev = mk("VANILLA", "#505050")
        lay.addLayout(vc)

        arr = QLabel("→")
        arr.setStyleSheet("color:#404040;font-size:28px;")
        arr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(arr)

        cc, self._c_prev = mk("CUSTOMIZADA", "#6ab84a")
        self._c_prev.setText("Sem textura\ncustomizada")
        imp = QPushButton("Importar PNG")
        imp.setFixedHeight(26)
        imp.clicked.connect(self._import)
        cc.addWidget(imp)
        lay.addLayout(cc)
        lay.addStretch()
        return w

    def _build_info(self) -> QFrame:
        f = QFrame()
        f.setStyleSheet("background:#181818;border-top:1px solid #222;")
        f.setFixedHeight(38)
        lay = QHBoxLayout(f)
        lay.setContentsMargins(12,0,12,0)
        lay.setSpacing(14)
        self._inf_name   = QLabel("Nenhuma textura selecionada")
        self._inf_name.setStyleSheet("color:#888;font-size:12px;font-weight:bold;")
        lay.addWidget(self._inf_name)
        self._inf_status = QLabel("")
        self._inf_status.setStyleSheet("color:#6ab84a;font-size:11px;")
        lay.addWidget(self._inf_status)
        lay.addStretch()
        return f

    # ── Tile management ───────────────────────────────────────────────────────
    def _load_tiles(self):
        category = self._cat.currentText()
        items    = get_category_items(category)

        # Category info messages
        info_msgs = {
            "Mobs":         "Texturas de entidades — tamanho variável (64×32, 64×64...)",
            "GUI / Interface": "Texturas de interface — tamanho variável. Edite com cuidado.",
            "Ambiente":     "Texturas de ambiente e colormaps — alguns arquivos são especiais.",
        }
        msg = info_msgs.get(category, "")
        if msg:
            self._cat_info.setText(f"ℹ  {msg}")
            self._cat_info.show()
        else:
            self._cat_info.hide()

        for t in self.tiles:
            t._alive = False
        while self._gl.count():
            item = self._gl.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.tiles.clear()
        self.selected_tile = None

        cols = 5
        for i, (dname, mc_folder, tex_name) in enumerate(items):
            tile = TextureTile(
                display_name=dname, mc_folder=mc_folder,
                tex_name=tex_name, mc_version=self.mc_version,
                parent=self._gw)
            tile.clicked.connect(self._on_click)
            key = f"{mc_folder}/{tex_name}"
            if key in self.modified:
                # Restore thumbnail from in-memory QImage
                from PyQt6.QtGui import QPixmap
                img_mem = self.modified[key]
                if hasattr(img_mem, 'width'):  # is QImage
                    thumb = QPixmap.fromImage(img_mem).scaled(
                        THUMB, THUMB,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation)
                    tile._img.setPixmap(thumb)
                    tile._img.setText("")
                    tile.custom_path = "__memory__"
                    tile._dot.show()
                    tile._update_style()
            self.tiles.append(tile)
            self._gl.addWidget(tile, i // cols, i % cols)

        self._status.setText(f"{len(items)} texturas · {category}")
        self._progress.setValue(0)
        self._progress.show()

        def on_prog(cur, total, name):
            pct = int(cur / total * 100) if total else 100
            QTimer.singleShot(0, lambda p=pct: self._set_prog(p))

        prefetch_category(self.mc_version, category, on_prog)

    def _set_prog(self, pct: int):
        self._progress.setValue(pct)
        if pct >= 100:
            QTimer.singleShot(1200, self._progress.hide)

    def _filter(self, text: str):
        text = text.lower()
        for tile in self.tiles:
            match = not text or text in tile.display_name.lower() or text in tile.tex_name.lower()
            tile.setVisible(match)

    # ── Tile click ────────────────────────────────────────────────────────────
    def _on_click(self, dname: str, mc_folder: str, tex_name: str, path: str):
        if self.selected_tile:
            self.selected_tile.set_selected(False)

        tile = next((t for t in self.tiles if t.tex_name == tex_name
                     and t.mc_folder == mc_folder), None)
        if tile:
            tile.set_selected(True)
            self.selected_tile = tile
            self._save_btn.setEnabled(True)
            self._save_hint.setText(
                f"Editando: {mc_folder}/{tex_name}.png")

        key = f"{mc_folder}/{tex_name}"
        self._inf_status.setText("✏️ Modificada" if key in self.modified else "")

        vanilla = tile.local_path if tile else path

        # Determine source: in-memory edit takes priority over vanilla
        if key in self.modified:
            from PyQt6.QtGui import QImage, QPixmap
            img = self.modified[key]
            size_txt = f"{img.width()}×{img.height()} px"
            self._inf_name.setText(f"{mc_folder}/{tex_name}.png  ·  {size_txt}  ·  editada")
            # Write to temp just for canvas loading (read-only)
            import tempfile
            tmp = os.path.join(tempfile.gettempdir(),
                               f"mms_edit_{tex_name.replace('/','_')}.png")
            img.save(tmp, "PNG")
            native = max(img.width(), img.height())
            self.open_texture.emit(tmp, native)
        elif vanilla and os.path.exists(vanilla):
            from PyQt6.QtGui import QImage
            img = QImage(vanilla)
            size_txt = f"{img.width()}×{img.height()} px" if not img.isNull() else "?"
            native   = max(img.width(), img.height()) if not img.isNull() else 16
            self._inf_name.setText(f"{mc_folder}/{tex_name}.png  ·  {size_txt}")
            self.open_texture.emit(vanilla, native)
        else:
            self._inf_name.setText(f"{mc_folder}/{tex_name}.png  ·  baixando...")

        self._tabs.setCurrentIndex(0)

    def _png_to_canvas(self, path: str):
        from PyQt6.QtGui import QImage
        from ui.pixel_editor import SUPPORTED_SIZES
        img = QImage(path)
        if img.isNull():
            return
        w, h = img.width(), img.height()
        native = max(w, h)

        # Only load into pixel editor if texture is small enough
        best = min(SUPPORTED_SIZES, key=lambda s: abs(s - native))
        # If the texture is much larger than max supported (32), skip pixel editor
        if native > max(SUPPORTED_SIZES) * 2:
            return  # large textures are handled by ImageEditor popup

        self.pixel_editor.set_canvas_size(best)
        img = img.scaled(best, best,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.FastTransformation)
        img = img.convertToFormat(QImage.Format.Format_RGBA8888)
        c = self.pixel_editor.canvas
        c.push_history()
        total = best * best
        for y in range(best):
            for x in range(best):
                idx = y * best + x
                if idx >= total:
                    break
                px = img.pixel(x, y)
                a = (px >> 24) & 0xFF
                r = (px >> 16) & 0xFF
                g = (px >> 8)  & 0xFF
                b =  px & 0xFF
                c.pixels[idx] = f"#{r:02x}{g:02x}{b:02x}" if a > 10 else None
        c.update()

    def _on_exported(self, path: str):
        """Called when pixel editor exports to file — load into memory."""
        if not self.selected_tile:
            return
        from PyQt6.QtGui import QImage, QPixmap
        img = QImage(path)
        if img.isNull():
            return
        self._store_in_memory(self.selected_tile, img)

    def _on_image_saved_from_editor(self, img):
        """Called when image editor emits texture_saved (QImage, no disk)."""
        if not self.selected_tile:
            return
        self._store_in_memory(self.selected_tile, img)

    def _store_in_memory(self, tile, img):
        """Store a QImage in memory and update the tile thumbnail."""
        from PyQt6.QtGui import QImage, QPixmap
        key = f"{tile.mc_folder}/{tile.tex_name}"
        self.modified[key] = img

        thumb = QPixmap.fromImage(img).scaled(
            THUMB, THUMB,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        tile._img.setPixmap(thumb)
        tile._img.setText("")
        tile.custom_path = "__memory__"
        tile._dot.show()
        tile._update_style()

        n = len(self.modified)
        self._inf_status.setText("✏️ Modificada")
        self._save_hint.setText(
            f"✅ {n} textura{'s' if n>1 else ''} em memória — "
            f"exporte o pack para salvar")
        self.texture_modified.emit(tile.mc_folder, tile.tex_name)

    def _save_to_project(self):
        """Store current pixel editor canvas in memory — no disk writes."""
        if not self.selected_tile:
            return
        try:
            img = self.pixel_editor.canvas.to_pixmap(1).toImage()
            self._store_in_memory(self.selected_tile, img)

            orig = self._save_btn.styleSheet()
            self._save_btn.setStyleSheet(
                "QPushButton{background:#1a4a10;border:1px solid #3a8020;"
                "border-radius:4px;color:#6ab84a;font-size:11px;}")
            QTimer.singleShot(1400, lambda: self._save_btn.setStyleSheet(orig))
        except Exception as e:
            import core.logger as log
            log.exception("Erro em _save_to_project")
            self._save_hint.setText(f"❌ Erro: {e}")

    # ── Pack I/O ──────────────────────────────────────────────────────────────
    def load_pack(self, pack_dir: str, pack_name: str, mc_version: str):
        self.pack_dir   = pack_dir
        self.pack_name  = pack_name
        self.mc_version = mc_version
        self._ver_lbl.setText(f"MC {mc_version}")
        self._save_hint.setText(
            f"Edite texturas e clique 'Salvar no Projeto', depois exporte o pack")
        self.modified.clear()
        self._load_tiles()

    def _export_pack(self):
        if not self.modified and not self.lang_editor.get_lang_json() and not self.pack_icon:
            QMessageBox.information(self, "Info",
                "Nenhuma modificação feita ainda.\n"
                "Edite texturas, textos ou adicione um ícone primeiro.")
            return
        out = QFileDialog.getExistingDirectory(self, "Pasta para exportar")
        if not out:
            return

        import json, zipfile, shutil, tempfile
        name   = self.pack_name or "meu_resource_pack"
        zip_path = os.path.join(out, f"{name}.zip")

        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                # pack.mcmeta
                mcmeta = {"pack": {"pack_format": 34,
                                   "description": f"{name} — Minecraft Mod Studio"}}
                zf.writestr(f"{name}/pack.mcmeta",
                            json.dumps(mcmeta, indent=2))

                # pack.png icon
                if self.pack_icon and os.path.exists(self.pack_icon):
                    zf.write(self.pack_icon, f"{name}/pack.png")

                # Modified textures — write from QImage directly to ZIP
                tmp_dir = tempfile.mkdtemp()
                for key, img in self.modified.items():
                    mc_folder, tex_name = key.split("/", 1)
                    parts    = tex_name.replace("\\", "/").split("/")
                    arc_path = f"{name}/assets/minecraft/textures/{mc_folder}/" + \
                               "/".join(parts) + ".png"
                    if hasattr(img, 'save'):  # QImage
                        tmp = os.path.join(tmp_dir, "tex.png")
                        img.save(tmp, "PNG")
                        zf.write(tmp, arc_path)
                    elif isinstance(img, str) and os.path.exists(img):
                        zf.write(img, arc_path)

                shutil.rmtree(tmp_dir, ignore_errors=True)

                # Language files
                lang_data = self.lang_editor.get_lang_json()
                if lang_data:
                    lang_json = json.dumps(lang_data, indent=2, ensure_ascii=False)
                    for code in ["pt_BR", "en_us"]:
                        zf.writestr(
                            f"{name}/assets/minecraft/lang/{code}.json",
                            lang_json)

            n_tex  = len(self.modified)
            n_lang = len(self.lang_editor.get_lang_json())
            QMessageBox.information(self, "Pack Exportado!",
                f"✅ Resource Pack exportado!\n\n{zip_path}\n\n"
                f"• {n_tex} textura(s) modificada(s)\n"
                f"• {n_lang} texto(s) traduzido(s)\n"
                f"{'• Ícone incluído' if self.pack_icon else ''}\n\n"
                "Para instalar: copie o ZIP para .minecraft/resourcepacks/")
        except Exception as e:
            import core.logger as log
            log.exception("Erro ao exportar pack")
            QMessageBox.critical(self, "Erro ao exportar", str(e))



