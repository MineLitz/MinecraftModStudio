from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy, QScrollArea, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QSize
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QPixmap, QImage, QCursor
)

GRID = 16
ZOOM = 16

SUPPORTED_SIZES    = [16, 32]          # pixel-by-pixel editing
LARGE_SIZES        = [64, 128, 256]    # handled by ImageEditor

MC_PALETTE = [
    "#000000","#1d1d21","#474f52","#8d8d8d","#b4b4b4","#ffffff",
    "#835432","#c97836","#e9b416","#f9f9a0","#7dc553","#3aa12e",
    "#1d7a25","#0d4f21","#178bc2","#3c5fca","#7c3bca","#c93c8e",
    "#d63e3e","#e8623e","#f0a020","#ffd83d","#80c050","#5aad3c",
    "#1a9040","#35b88e","#2060c8","#6030a8","#a030a0","#e03060",
    "#c03030","#882020","#7b4a1d","#b87333","#cda05a","#d4b896",
    "#f4e0c0","#c0e8ff","#80b8e8","#4888c8","#2050a0","#103878",
    "#301878","#602090","#a050d0","#d890f0","#f0c0e0","#f8e8f0",
]

SUPPORTED_SIZES = [16, 32, 64, 128, 256]


class PixelCanvas(QWidget):
    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid   = GRID   # current canvas size (NxN)
        self.zoom   = ZOOM
        self.pixels = [None] * (self.grid * self.grid)
        self.tool   = "pencil"
        self.color  = "#7dc553"
        self._drawing = False
        self._history = []
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self._update_size()

    def set_grid(self, size: int):
        """Resize the canvas to NxN. Clears current pixels."""
        if size == self.grid:
            return
        self._history.clear()
        self.grid   = size
        self.pixels = [None] * (size * size)
        # Auto-adjust zoom so canvas stays ~400px
        self.zoom = max(2, min(32, 400 // size))
        self._update_size()
        self.update()
        self.changed.emit()

    def _update_size(self):
        size = self.grid * self.zoom
        self.setFixedSize(size, size)

    def set_zoom(self, z: int):
        self.zoom = max(2, min(40, z))
        self._update_size()
        self.update()

    def set_tool(self, t: str):
        self.tool = t
        self.setCursor(Qt.CursorShape.CrossCursor if t != "eraser"
                       else Qt.CursorShape.PointingHandCursor)

    def set_color(self, c: str):
        self.color = c

    def push_history(self):
        self._history.append(self.pixels[:])
        if len(self._history) > 50:
            self._history.pop(0)

    def undo(self):
        if self._history:
            self.pixels = self._history.pop()
            self.update()
            self.changed.emit()

    def clear(self):
        self.push_history()
        self.pixels = [None] * (self.grid * self.grid)
        self.update()
        self.changed.emit()

    def _xy(self, pos: QPoint):
        x = min(self.grid - 1, max(0, pos.x() // self.zoom))
        y = min(self.grid - 1, max(0, pos.y() // self.zoom))
        return x, y

    def _apply(self, x: int, y: int):
        idx = y * self.grid + x
        if self.tool == "pencil":
            self.pixels[idx] = self.color
        elif self.tool == "eraser":
            self.pixels[idx] = None
        elif self.tool == "eyedrop":
            if self.pixels[idx]:
                self.color = self.pixels[idx]
                self.changed.emit()
            return
        elif self.tool == "fill":
            target = self.pixels[idx]
            if target != self.color:
                self._flood(x, y, target, self.color)
        self.update()
        self.changed.emit()

    def _flood(self, x, y, target, replacement):
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if cx < 0 or cx >= self.grid or cy < 0 or cy >= self.grid:
                continue
            idx = cy * self.grid + cx
            if self.pixels[idx] != target:
                continue
            self.pixels[idx] = replacement
            stack += [(cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1)]

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.push_history()
            self._drawing = True
            self._apply(*self._xy(e.pos()))

    def mouseMoveEvent(self, e):
        if self._drawing and e.buttons() & Qt.MouseButton.LeftButton:
            self._apply(*self._xy(e.pos()))

    def mouseReleaseEvent(self, e):
        self._drawing = False

    def paintEvent(self, e):
        p = QPainter(self)
        g = self.grid
        z = self.zoom
        # Checkerboard for transparency
        for y in range(g):
            for x in range(g):
                c = QColor("#2a2a2a") if (x+y) % 2 == 0 else QColor("#222222")
                p.fillRect(x*z, y*z, z, z, c)
        # Pixels
        for i, col in enumerate(self.pixels):
            if col:
                x, y = i % g, i // g
                p.fillRect(x*z, y*z, z, z, QColor(col))
        # Grid lines (only draw if zoom >= 4 to avoid clutter on large canvases)
        if z >= 4:
            pen = QPen(QColor(50, 50, 50, 100))
            pen.setWidth(1)
            p.setPen(pen)
            for i in range(g + 1):
                p.drawLine(i*z, 0, i*z, g*z)
                p.drawLine(0, i*z, g*z, i*z)

    def to_pixmap(self, scale: int = 1) -> QPixmap:
        g = self.grid
        img = QImage(g * scale, g * scale, QImage.Format.Format_ARGB32)
        img.fill(Qt.GlobalColor.transparent)
        p = QPainter(img)
        for i, col in enumerate(self.pixels):
            if col:
                x, y = i % g, i // g
                p.fillRect(x*scale, y*scale, scale, scale, QColor(col))
        p.end()
        return QPixmap.fromImage(img)

    def export_png(self, path: str):
        self.to_pixmap(1).save(path, "PNG")


class ColorSwatch(QWidget):
    clicked = pyqtSignal(str)

    def __init__(self, color: str, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(18, 18)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.selected = False

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(0, 0, 18, 18, QColor(self.color))
        if self.selected:
            pen = QPen(QColor("#ffffff"))
            pen.setWidth(2)
            p.setPen(pen)
            p.drawRect(1, 1, 15, 15)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.color)


class PixelArtEditor(QWidget):
    texture_exported = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._element_name = ""
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        # ── Left: canvas ──────────────────────────────────────────────────────
        canvas_col = QVBoxLayout()
        canvas_col.setSpacing(10)

        # Toolbar
        tb = QFrame()
        tb.setStyleSheet("background:#1e1e1e; border:1px solid #2a2a2a; border-radius:5px;")
        tb_lay = QHBoxLayout(tb)
        tb_lay.setContentsMargins(8, 6, 8, 6)
        tb_lay.setSpacing(4)

        self._tool_btns = {}
        tools = [
            ("fa5s.pencil-alt", "pencil",   "Lápis"),
            ("fa5s.fill-drip",  "fill",     "Balde de tinta"),
            ("fa5s.eraser",     "eraser",   "Borracha"),
            ("fa5s.eye-dropper","eyedrop",  "Conta-gotas"),
        ]
        for icon_name, tool, tip in tools:
            btn = QPushButton()
            btn.setFixedSize(32, 28)
            btn.setCheckable(True)
            btn.setToolTip(tip)
            try:
                import qtawesome as qta
                btn.setIcon(qta.icon(icon_name, color="#909090"))
            except Exception:
                btn.setText({"pencil": "P", "fill": "F",
                             "eraser": "E", "eyedrop": "D"}.get(tool, "?"))
            btn.setStyleSheet("""
                QPushButton { background:transparent; border:1px solid transparent;
                    border-radius:4px; }
                QPushButton:hover { background:#2a2a2a; border-color:#3a3a3a; }
                QPushButton:checked { background:#1e3010; border-color:#4a7a20; }
            """)
            btn.clicked.connect(lambda _, t=tool: self._set_tool(t))
            self._tool_btns[tool] = btn
            tb_lay.addWidget(btn)

        tb_lay.addSpacing(8)

        # Canvas size selector
        from PyQt6.QtWidgets import QComboBox
        size_lbl = QLabel("Tamanho:")
        size_lbl.setStyleSheet("background:transparent;color:#666;font-size:11px;")
        tb_lay.addWidget(size_lbl)
        self._size_combo = QComboBox()
        for s in SUPPORTED_SIZES:
            self._size_combo.addItem(f"{s}×{s}", s)
        self._size_combo.setFixedWidth(68)
        self._size_combo.setStyleSheet("""
            QComboBox { background:#1e1e1e; border:1px solid #333;
                border-radius:3px; color:#aaa; font-size:11px; padding:2px 4px; }
            QComboBox::drop-down { border:none; width:16px; }
            QComboBox QAbstractItemView { background:#2a2a2a; color:#ccc; }
        """)
        self._size_combo.currentIndexChanged.connect(self._on_size_change)
        tb_lay.addWidget(self._size_combo)
        for icon_name, delta, tip in [("fa5s.search-minus", -4, "Zoom −"), ("fa5s.search-plus", 4, "Zoom +")]:
            z = QPushButton()
            z.setFixedSize(30, 28)
            z.setToolTip(tip)
            try:
                import qtawesome as qta
                z.setIcon(qta.icon(icon_name, color="#909090"))
            except Exception:
                z.setText("−" if delta < 0 else "+")
            z.setStyleSheet("QPushButton { background:#2a2a2a; border:1px solid #333; border-radius:3px; } QPushButton:hover { background:#383838; }")
            z.clicked.connect(lambda _, d=delta: self._zoom(d))
            tb_lay.addWidget(z)

        tb_lay.addStretch()

        for icon_name, tip, callback in [
            ("fa5s.undo",   "Desfazer (Ctrl+Z)", lambda: self.canvas.undo()),
            ("fa5s.eraser", "Limpar canvas",      lambda: self.canvas.clear()),
        ]:
            btn = QPushButton()
            btn.setFixedSize(30, 28)
            btn.setToolTip(tip)
            try:
                import qtawesome as qta
                btn.setIcon(qta.icon(icon_name, color="#909090"))
            except Exception:
                btn.setText("↩" if "undo" in icon_name else "🗑")
            btn.setStyleSheet("QPushButton { background:#2a2a2a; border:1px solid #333; border-radius:3px; } QPushButton:hover { background:#383838; }")
            btn.clicked.connect(callback)
            tb_lay.addWidget(btn)

        canvas_col.addWidget(tb)

        # Canvas scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(False)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setStyleSheet("QScrollArea { border:1px solid #2a2a2a; border-radius:4px; background:#1a1a1a; }")
        self.canvas = PixelCanvas()
        self.canvas.changed.connect(self._on_canvas_changed)
        scroll.setWidget(self.canvas)
        scroll.setMinimumSize(420, 420)
        canvas_col.addWidget(scroll)

        root.addLayout(canvas_col)

        # ── Right: palette + preview + export ────────────────────────────────
        right_col = QVBoxLayout()
        right_col.setSpacing(12)
        right_col.setContentsMargins(0, 0, 0, 0)

        # Current color
        cur_lbl = QLabel("COR ATUAL")
        cur_lbl.setStyleSheet("color:#505050; font-size:10px; font-weight:bold; letter-spacing:1px;")
        right_col.addWidget(cur_lbl)

        cur_row = QHBoxLayout()
        cur_row.setSpacing(8)
        self._cur_swatch = QFrame()
        self._cur_swatch.setFixedSize(36, 36)
        self._cur_swatch.setStyleSheet("background:#7dc553; border:1px solid #3a3a3a; border-radius:4px;")
        cur_row.addWidget(self._cur_swatch)
        self._cur_hex = QLabel("#7dc553")
        self._cur_hex.setStyleSheet("color:#888; font-size:11px; font-family:monospace;")
        cur_row.addWidget(self._cur_hex)
        cur_row.addStretch()
        right_col.addLayout(cur_row)

        # Palette
        pal_lbl = QLabel("PALETA MINECRAFT")
        pal_lbl.setStyleSheet("color:#505050; font-size:10px; font-weight:bold; letter-spacing:1px;")
        right_col.addWidget(pal_lbl)

        pal_grid = QFrame()
        pal_grid.setStyleSheet("background:#1e1e1e; border:1px solid #2a2a2a; border-radius:5px;")
        pg_lay = QHBoxLayout(pal_grid)
        pg_lay.setContentsMargins(8, 8, 8, 8)
        pg_lay.setSpacing(0)

        # Wrap swatches in a grid-like layout
        pal_inner = QWidget()
        pal_inner.setStyleSheet("background:transparent;")
        from PyQt6.QtWidgets import QGridLayout
        pal_g = QGridLayout(pal_inner)
        pal_g.setSpacing(3)
        pal_g.setContentsMargins(0, 0, 0, 0)

        self._swatches = []
        for i, col in enumerate(MC_PALETTE):
            sw = ColorSwatch(col)
            sw.clicked.connect(self._pick_color)
            pal_g.addWidget(sw, i // 8, i % 8)
            self._swatches.append(sw)

        pg_lay.addWidget(pal_inner)
        right_col.addWidget(pal_grid)

        # Custom color picker button
        custom_btn = QPushButton("  Cor personalizada...")
        custom_btn.setFixedHeight(30)
        try:
            import qtawesome as qta
            custom_btn.setIcon(qta.icon("fa5s.palette", color="#909090"))
        except Exception:
            pass
        custom_btn.setStyleSheet("""
            QPushButton {
                background:#1e1e1e; border:1px solid #333;
                border-radius:4px; color:#888; font-size:11px;
            }
            QPushButton:hover { background:#2a2a2a; border-color:#4a4a4a; color:#bbb; }
        """)
        custom_btn.clicked.connect(self._open_color_dialog)
        right_col.addWidget(custom_btn)

        # Preview
        prev_lbl = QLabel("PREVIEW (×8)")
        prev_lbl.setStyleSheet("color:#505050; font-size:10px; font-weight:bold; letter-spacing:1px;")
        right_col.addWidget(prev_lbl)

        self._preview = QLabel()
        self._preview.setFixedSize(128, 128)
        self._preview.setStyleSheet("background:#1a1a1a; border:1px solid #2a2a2a; border-radius:4px;")
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_col.addWidget(self._preview)

        # Export button
        export_btn = QPushButton("  Exportar PNG")
        try:
            import qtawesome as qta
            export_btn.setIcon(qta.icon("fa5s.file-image", color="#1e3010"))
        except Exception:
            pass
        export_btn.setObjectName("btn_primary")
        export_btn.setFixedHeight(34)
        export_btn.clicked.connect(self._export)
        right_col.addWidget(export_btn)

        right_col.addStretch()
        root.addLayout(right_col)

        # Init tool
        self._set_tool("pencil")

    def _on_size_change(self, idx: int):
        new_size = self._size_combo.itemData(idx)
        if new_size and new_size != self.canvas.grid:
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, "Redimensionar canvas",
                f"Redimensionar para {new_size}×{new_size}?\nIsso limpará o canvas atual.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.canvas.set_grid(new_size)
                self._on_canvas_changed()
            else:
                # Revert combo
                self._size_combo.blockSignals(True)
                self._size_combo.setCurrentText(f"{self.canvas.grid}×{self.canvas.grid}")
                self._size_combo.blockSignals(False)

    def set_canvas_size(self, size: int):
        """Programmatically set canvas size without asking."""
        if size not in SUPPORTED_SIZES:
            # Round to nearest supported
            size = min(SUPPORTED_SIZES, key=lambda s: abs(s - size))
        self.canvas.set_grid(size)
        self._size_combo.blockSignals(True)
        self._size_combo.setCurrentText(f"{size}×{size}")
        self._size_combo.blockSignals(False)
        self._on_canvas_changed()

    def _set_tool(self, tool: str):
        self.canvas.set_tool(tool)
        for t, btn in self._tool_btns.items():
            btn.setChecked(t == tool)

    def _zoom(self, delta: int):
        self.canvas.set_zoom(self.canvas.zoom + delta)

    def _open_color_dialog(self):
        from PyQt6.QtWidgets import QColorDialog
        from PyQt6.QtGui import QColor
        initial = QColor(self.canvas.color)
        color = QColorDialog.getColor(initial, self, "Escolher cor",
                                      QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if color.isValid():
            hex_color = color.name()
            self._pick_color(hex_color)

    def _pick_color(self, color: str):
        self.canvas.set_color(color)
        self._cur_swatch.setStyleSheet(f"background:{color}; border:1px solid #3a3a3a; border-radius:4px;")
        self._cur_hex.setText(color)
        for sw in self._swatches:
            sw.selected = sw.color == color
            sw.update()

    def _on_canvas_changed(self):
        g = self.canvas.grid
        scale = max(1, 128 // g)
        px = self.canvas.to_pixmap(scale)
        self._preview.setPixmap(px.scaled(
            128, 128,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation
        ))

    def _export(self):
        default = f"{self._element_name or 'texture'}.png"
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Textura", default, "PNG (*.png)"
        )
        if path:
            self.canvas.export_png(path)
            self.texture_exported.emit(path)

    def load_element(self, element):
        self._element_name = element.registry_name
        # Could load existing texture data here in the future

    def get_pixels(self):
        return self.canvas.pixels[:]
