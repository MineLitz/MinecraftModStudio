"""
ImageEditor — janela popup para texturas grandes (64-256px).
paintEvent usa apenas drawPixmap (1 blit) + linhas opcionais. Zero loops no render.
Zoom suave via scroll do mouse.
"""
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QFileDialog, QSlider, QComboBox, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap, QImage

LARGE_SIZES = [64, 128, 256]


# ── Canvas ────────────────────────────────────────────────────────────────────
class ImageCanvas(QWidget):
    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.img_size   = 64
        self.brush_size = 1
        self.color      = "#7dc553"
        self.tool       = "pencil"
        self._image     = QImage(64, 64, QImage.Format.Format_ARGB32)
        self._image.fill(Qt.GlobalColor.transparent)
        self._history:  list[QImage] = []
        self._drawing   = False
        self._scale     = 6.0
        self._bg_px:    QPixmap | None = None   # cached checkerboard
        self._bg_scale  = -1.0
        self._bg_size   = -1
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self._resize()

    def _resize(self):
        s = max(1, int(self.img_size * self._scale))
        self.setFixedSize(s, s)

    # ── Zoom ──────────────────────────────────────────────────────────────────
    def zoom_by(self, delta: int):
        factor = 1.18 if delta > 0 else 1 / 1.18
        self._scale = max(0.25, min(32.0, self._scale * factor))
        self._resize()
        self.update()

    def wheelEvent(self, e):
        self.zoom_by(e.angleDelta().y())

    # ── Load/resize ───────────────────────────────────────────────────────────
    def set_size(self, size: int):
        self._history.clear()
        self.img_size = size
        self._image   = QImage(size, size, QImage.Format.Format_ARGB32)
        self._image.fill(Qt.GlobalColor.transparent)
        self._scale   = max(1.0, min(8.0, 512.0 / size))
        self._bg_px   = None
        self._resize()
        self.update()

    def load_image(self, path: str):
        img = QImage(path)
        if img.isNull():
            return
        self._history.clear()
        best  = min(LARGE_SIZES, key=lambda s: abs(s - max(img.width(), img.height())))
        self.img_size = best
        self._image   = img.scaled(
            best, best,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ).convertToFormat(QImage.Format.Format_ARGB32)
        self._scale   = max(1.0, min(8.0, 512.0 / best))
        self._bg_px   = None
        self._resize()
        self.update()
        self.changed.emit()

    # ── BG cache ──────────────────────────────────────────────────────────────
    def _checkerboard(self) -> QPixmap:
        sc = int(self._scale)
        n  = self.img_size
        if (self._bg_px is None or self._bg_scale != sc or self._bg_size != n):
            disp = int(n * self._scale)
            px   = QPixmap(disp, disp)
            p    = QPainter(px)
            cell = max(8, sc * 2)
            c1, c2 = QColor("#2d2d2d"), QColor("#232323")
            cols = (disp + cell - 1) // cell
            rows = (disp + cell - 1) // cell
            for row in range(rows):
                for col in range(cols):
                    p.fillRect(col*cell, row*cell, cell, cell,
                               c1 if (row+col)%2==0 else c2)
            p.end()
            self._bg_px    = px
            self._bg_scale = sc
            self._bg_size  = n
        return self._bg_px

    # ── Tools ─────────────────────────────────────────────────────────────────
    def set_tool(self, t): self.tool = t
    def set_color(self, c): self.color = c
    def set_brush(self, s): self.brush_size = max(1, s)

    # ── History ───────────────────────────────────────────────────────────────
    def push_history(self):
        self._history.append(self._image.copy())
        if len(self._history) > 30:
            self._history.pop(0)

    def undo(self):
        if self._history:
            self._image = self._history.pop()
            self.update(); self.changed.emit()

    def clear(self):
        self.push_history()
        self._image.fill(Qt.GlobalColor.transparent)
        self.update(); self.changed.emit()

    # ── Draw ──────────────────────────────────────────────────────────────────
    def _img_xy(self, pos: QPoint):
        sc = self._scale
        return (min(self.img_size-1, max(0, int(pos.x()/sc))),
                min(self.img_size-1, max(0, int(pos.y()/sc))))

    def _paint_at(self, x, y):
        p = QPainter(self._image)
        b = self.brush_size
        if self.tool == "eraser":
            p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            p.fillRect(x, y, b, b, Qt.GlobalColor.transparent)
        elif self.tool == "pencil":
            p.fillRect(x, y, b, b, QColor(self.color))
        elif self.tool == "eyedrop":
            self.color = QColor(self._image.pixel(x, y)).name()
            self.changed.emit(); p.end(); return
        elif self.tool == "fill":
            p.end(); self._flood(x, y); self.update(); self.changed.emit(); return
        p.end(); self.update(); self.changed.emit()

    def _flood(self, sx, sy):
        target = QColor(self._image.pixel(sx, sy)).name()
        repl   = self.color
        if target == repl:
            return
        stack, vis = [(sx, sy)], set()
        p = QPainter(self._image)
        p.setPen(Qt.PenStyle.NoPen)
        while stack:
            x, y = stack.pop()
            if (x,y) in vis or x<0 or x>=self.img_size or y<0 or y>=self.img_size:
                continue
            if QColor(self._image.pixel(x,y)).name() != target:
                continue
            vis.add((x,y))
            p.fillRect(x, y, 1, 1, QColor(repl))
            stack += [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
        p.end()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.push_history(); self._drawing = True
            self._paint_at(*self._img_xy(e.pos()))

    def mouseMoveEvent(self, e):
        if self._drawing and e.buttons() & Qt.MouseButton.LeftButton:
            self._paint_at(*self._img_xy(e.pos()))

    def mouseReleaseEvent(self, e):
        self._drawing = False

    # ── Render — single blit, NO per-pixel loops ──────────────────────────────
    def paintEvent(self, e):
        p    = QPainter(self)
        n    = self.img_size
        disp = int(n * self._scale)

        # 1. Cached checkerboard (rebuilt only on zoom/resize change)
        p.drawPixmap(0, 0, self._checkerboard())

        # 2. Image — one scaled blit
        p.drawPixmap(QRect(0, 0, disp, disp),
                     QPixmap.fromImage(self._image),
                     QRect(0, 0, n, n))

        # 3. Pixel grid — only when zoomed in enough
        sc = int(self._scale)
        if sc >= 8:
            pen = QPen(QColor(55, 55, 55, 120))
            pen.setWidth(1)
            p.setPen(pen)
            for i in range(n + 1):
                p.drawLine(i*sc, 0, i*sc, disp)
                p.drawLine(0, i*sc, disp, i*sc)

    def export_png(self, path): self._image.save(path, "PNG")
    def to_pixmap(self): return QPixmap.fromImage(self._image)


# ── Dialog ────────────────────────────────────────────────────────────────────
class ImageEditor(QDialog):
    texture_exported = pyqtSignal(str)     # from "Exportar PNG" — writes to user-chosen file
    texture_saved    = pyqtSignal(object)  # from "Salvar no Projeto" — emits QImage, no disk

    def __init__(self, parent=None, path: str = "", tex_name: str = ""):
        super().__init__(parent)
        self.setWindowTitle(f"Image Editor — {tex_name}" if tex_name else "Image Editor")
        self.setMinimumSize(800, 580)
        self.resize(960, 660)
        self.setModal(False)
        self._tex_name = tex_name
        self._build_ui()
        if path:
            self.load_image(path)

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(14)

        # ── Left: toolbar + canvas ────────────────────────────────────────────
        left = QVBoxLayout()
        left.setSpacing(8)

        # Toolbar
        tb = QFrame()
        tb.setStyleSheet(
            "background:#1e1e1e;border:1px solid #2a2a2a;border-radius:5px;")
        tl = QHBoxLayout(tb)
        tl.setContentsMargins(8, 5, 8, 5)
        tl.setSpacing(4)

        self._tool_btns = {}
        for icon_n, tool, tip in [
            ("fa5s.pencil-alt","pencil","Lápis"),
            ("fa5s.fill-drip", "fill",  "Balde"),
            ("fa5s.eraser",    "eraser","Borracha"),
            ("fa5s.eye-dropper","eyedrop","Conta-gotas"),
        ]:
            btn = QPushButton()
            btn.setFixedSize(32, 28)
            btn.setCheckable(True)
            btn.setToolTip(tip)
            try:
                import qtawesome as qta
                btn.setIcon(qta.icon(icon_n, color="#909090"))
            except Exception:
                btn.setText(tool[0].upper())
            btn.setStyleSheet(
                "QPushButton{background:transparent;border:1px solid transparent;border-radius:4px;}"
                "QPushButton:hover{background:#2a2a2a;border-color:#3a3a3a;}"
                "QPushButton:checked{background:#1e3010;border-color:#4a7a20;}")
            btn.clicked.connect(lambda _, t=tool: self._set_tool(t))
            self._tool_btns[tool] = btn
            tl.addWidget(btn)

        tl.addSpacing(6)
        tl.addWidget(QLabel("Pincel:"))
        self._brush = QSlider(Qt.Orientation.Horizontal)
        self._brush.setRange(1, 32)
        self._brush.setValue(1)
        self._brush.setFixedWidth(80)
        self._brush.valueChanged.connect(lambda v: self.canvas.set_brush(v))
        tl.addWidget(self._brush)
        self._brush_lbl = QLabel("1px")
        self._brush_lbl.setFixedWidth(30)
        self._brush.valueChanged.connect(lambda v: self._brush_lbl.setText(f"{v}px"))
        tl.addWidget(self._brush_lbl)

        tl.addSpacing(6)
        tl.addWidget(QLabel("Tamanho:"))
        self._size = QComboBox()
        for s in LARGE_SIZES:
            self._size.addItem(f"{s}×{s}", s)
        self._size.setFixedWidth(82)
        self._size.currentIndexChanged.connect(
            lambda i: self.canvas.set_size(self._size.itemData(i)))
        tl.addWidget(self._size)

        tl.addSpacing(6)
        # Zoom buttons
        for icon_n, delta, tip in [
            ("fa5s.search-minus", -1, "Zoom −  (roda do mouse)"),
            ("fa5s.search-plus",  +1, "Zoom +  (roda do mouse)"),
        ]:
            z = QPushButton()
            z.setFixedSize(30, 28)
            z.setToolTip(tip)
            try:
                import qtawesome as qta
                z.setIcon(qta.icon(icon_n, color="#909090"))
            except Exception:
                z.setText("-" if delta < 0 else "+")
            z.setStyleSheet(
                "QPushButton{background:#2a2a2a;border:1px solid #333;border-radius:3px;}"
                "QPushButton:hover{background:#383838;}")
            z.clicked.connect(lambda _, d=delta: self.canvas.zoom_by(d))
            tl.addWidget(z)

        tl.addStretch()

        for icon_n, tip, cb in [
            ("fa5s.undo",   "Desfazer (Ctrl+Z)", lambda: self.canvas.undo()),
            ("fa5s.eraser", "Limpar canvas",      lambda: self.canvas.clear()),
        ]:
            btn = QPushButton()
            btn.setFixedSize(30, 28)
            btn.setToolTip(tip)
            try:
                import qtawesome as qta
                btn.setIcon(qta.icon(icon_n, color="#909090"))
            except Exception:
                btn.setText("↩" if "undo" in icon_n else "X")
            btn.setStyleSheet(
                "QPushButton{background:#2a2a2a;border:1px solid #333;border-radius:3px;}"
                "QPushButton:hover{background:#383838;}")
            btn.clicked.connect(cb)
            tl.addWidget(btn)

        left.addWidget(tb)

        # Canvas scroll area
        sc = QScrollArea()
        sc.setWidgetResizable(False)
        sc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sc.setStyleSheet(
            "QScrollArea{border:1px solid #2a2a2a;border-radius:4px;background:#1a1a1a;}")
        self.canvas = ImageCanvas()
        self.canvas.changed.connect(self._on_changed)
        sc.setWidget(self.canvas)
        left.addWidget(sc)

        root.addLayout(left, stretch=3)

        # ── Right: color + palette + preview ─────────────────────────────────
        right = QVBoxLayout()
        right.setSpacing(10)
        right.setContentsMargins(0, 0, 0, 0)

        right.addWidget(self._lbl("COR ATUAL"))
        row = QHBoxLayout()
        self._swatch = QFrame()
        self._swatch.setFixedSize(36, 36)
        self._swatch.setStyleSheet(
            "background:#7dc553;border:1px solid #3a3a3a;border-radius:4px;")
        self._hex_lbl = QLabel("#7dc553")
        self._hex_lbl.setStyleSheet("color:#888;font-size:11px;font-family:monospace;")
        row.addWidget(self._swatch)
        row.addWidget(self._hex_lbl)
        row.addStretch()
        right.addLayout(row)

        cust = QPushButton("  Cor personalizada...")
        cust.setFixedHeight(28)
        try:
            import qtawesome as qta
            cust.setIcon(qta.icon("fa5s.palette", color="#909090"))
        except Exception:
            pass
        cust.setStyleSheet(
            "QPushButton{background:#1e1e1e;border:1px solid #333;border-radius:4px;"
            "color:#888;font-size:11px;}"
            "QPushButton:hover{background:#2a2a2a;color:#bbb;}")
        cust.clicked.connect(self._pick_color)
        right.addWidget(cust)

        right.addWidget(self._lbl("PALETA MC"))
        from ui.pixel_editor import MC_PALETTE
        pal = QFrame()
        pal.setStyleSheet(
            "background:#1e1e1e;border:1px solid #2a2a2a;border-radius:5px;")
        pg = QGridLayout(pal)
        pg.setContentsMargins(6,6,6,6)
        pg.setSpacing(3)
        for i, c in enumerate(MC_PALETTE):
            sw = QFrame()
            sw.setFixedSize(14, 14)
            sw.setStyleSheet(f"background:{c};border-radius:2px;")
            sw.setCursor(Qt.CursorShape.PointingHandCursor)
            sw.mousePressEvent = lambda e, col=c: self._apply_color(col)
            pg.addWidget(sw, i//8, i%8)
        right.addWidget(pal)

        right.addWidget(self._lbl("PREVIEW"))
        self._prev = QLabel()
        self._prev.setFixedSize(128, 128)
        self._prev.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._prev.setStyleSheet(
            "background:#1a1a1a;border:1px solid #2a2a2a;border-radius:4px;")
        right.addWidget(self._prev)

        save_proj = QPushButton("  Salvar no Projeto")
        save_proj.setFixedHeight(34)
        try:
            import qtawesome as qta
            save_proj.setIcon(qta.icon("fa5s.save", color="#909090"))
        except Exception:
            pass
        save_proj.setStyleSheet(
            "QPushButton{background:#1a2a10;border:1px solid #2a4a18;"
            "border-radius:4px;color:#6ab84a;font-size:11px;}"
            "QPushButton:hover{background:#1e3a14;}")
        save_proj.clicked.connect(self._save_to_project)
        right.addWidget(save_proj)

        exp = QPushButton("  Exportar PNG")
        exp.setObjectName("btn_primary")
        exp.setFixedHeight(34)
        try:
            import qtawesome as qta
            exp.setIcon(qta.icon("fa5s.file-image", color="#1e3010"))
        except Exception:
            pass
        exp.clicked.connect(self._export)
        right.addWidget(exp)
        right.addStretch()
        root.addLayout(right, stretch=0)

        self._set_tool("pencil")

    def _lbl(self, text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet(
            "color:#505050;font-size:10px;font-weight:bold;letter-spacing:1px;")
        return l

    def _set_tool(self, t):
        self.canvas.set_tool(t)
        for n, b in self._tool_btns.items():
            b.setChecked(n == t)

    def _on_changed(self):
        px = self.canvas.to_pixmap().scaled(
            128, 128, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation)
        self._prev.setPixmap(px)

    def _pick_color(self):
        from PyQt6.QtWidgets import QColorDialog
        c = QColorDialog.getColor(
            QColor(self.canvas.color), self, "Escolher cor",
            QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if c.isValid():
            self._apply_color(c.name())

    def _apply_color(self, color: str):
        self.canvas.set_color(color)
        self._swatch.setStyleSheet(
            f"background:{color};border:1px solid #3a3a3a;border-radius:4px;")
        self._hex_lbl.setText(color)

    def set_project_info(self, pack_dir: str, mc_folder: str, tex_name: str):
        """Called by mainwindow so the editor knows where to save."""
        self._pack_dir  = pack_dir
        self._mc_folder = mc_folder
        self._tex_name  = tex_name
        self.setWindowTitle(f"Image Editor — {tex_name}")

    def _save_to_project(self):
        """Emit the canvas QImage directly — no disk writes."""
        img = self.canvas._image.copy()
        self.texture_saved.emit(img)
        self.setWindowTitle(
            f"Image Editor — {self._tex_name} ✅" if self._tex_name
            else "Image Editor ✅")


    def load_image(self, path: str):
        self.canvas.load_image(path)
        size = self.canvas.img_size
        self._size.blockSignals(True)
        self._size.setCurrentText(f"{size}×{size}")
        self._size.blockSignals(False)
        self._on_changed()

    def _export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar PNG",
            f"{self._tex_name or 'texture'}.png", "PNG (*.png)")
        if path:
            self.canvas.export_png(path)
            self.texture_exported.emit(path)
