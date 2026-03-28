"""
ui/animation_editor.py
----------------------
Editor visual de texturas animadas para Minecraft Resource Packs.

Layout (3 colunas):
  ┌─────────────────────────────────────────────────────────┐
  │  [Lista de Frames]  │  [Canvas do Frame]  │ [Preview +  │
  │  miniaturas +       │  edição de pixels   │  Config     │
  │  controles          │  (zoom 16x)         │  .mcmeta]   │
  └─────────────────────────────────────────────────────────┘

Uso:
    from ui.animation_editor import AnimationEditorDialog
    dlg = AnimationEditorDialog(parent=self)
    if dlg.exec():
        anim = dlg.animation   # AnimationData pronto para exportar
"""

from __future__ import annotations

import os
from typing import Optional

from PyQt6.QtCore import (
    QByteArray, QIODevice, QBuffer, QRect, QSize, Qt, QTimer,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QBrush, QColor, QFont, QIcon, QImage, QPainter, QPen,
    QPixmap, QWheelEvent,
)
from PyQt6.QtWidgets import (
    QCheckBox, QDialog, QDialogButtonBox, QFileDialog, QFrame,
    QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMenu,
    QMessageBox, QPushButton, QScrollArea, QSizePolicy,
    QSlider, QSpinBox, QSplitter, QToolBar, QVBoxLayout, QWidget,
    QGroupBox, QFormLayout, QToolButton,
)

from core.animation import AnimationData, AnimationFrame


# ═══════════════════════════════════════════════════════════════════════════
# Paleta de cores (segue o tema escuro do projeto)
# ═══════════════════════════════════════════════════════════════════════════

COLOR_BG        = "#1e1e2e"
COLOR_PANEL     = "#252535"
COLOR_SURFACE   = "#2a2a3d"
COLOR_BORDER    = "#3a3a55"
COLOR_ACCENT    = "#4CAF50"
COLOR_ACCENT2   = "#2196F3"
COLOR_TEXT      = "#e0e0e0"
COLOR_TEXT_DIM  = "#888899"
COLOR_DANGER    = "#f44336"
COLOR_SELECTED  = "#3d3d60"

PANEL_STYLE = f"""
    QWidget {{ background: {COLOR_PANEL}; color: {COLOR_TEXT}; }}
    QGroupBox {{
        border: 1px solid {COLOR_BORDER};
        border-radius: 6px;
        margin-top: 8px;
        padding-top: 12px;
        font-weight: bold;
        color: {COLOR_TEXT};
    }}
    QGroupBox::title {{ subcontrol-origin: margin; left: 10px; }}
    QSpinBox, QCheckBox {{ color: {COLOR_TEXT}; background: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER}; border-radius: 4px; padding: 2px 6px; }}
    QSpinBox:focus {{ border-color: {COLOR_ACCENT}; }}
    QPushButton {{
        background: {COLOR_SURFACE}; color: {COLOR_TEXT};
        border: 1px solid {COLOR_BORDER}; border-radius: 5px;
        padding: 5px 12px; font-size: 12px;
    }}
    QPushButton:hover  {{ background: {COLOR_SELECTED}; border-color: {COLOR_ACCENT}; }}
    QPushButton:pressed {{ background: {COLOR_ACCENT}; color: #fff; }}
    QListWidget {{
        background: {COLOR_BG}; border: 1px solid {COLOR_BORDER};
        border-radius: 5px; outline: none;
    }}
    QListWidget::item {{ padding: 2px; border-radius: 4px; }}
    QListWidget::item:selected {{ background: {COLOR_SELECTED}; border: 1px solid {COLOR_ACCENT}; }}
    QScrollBar:vertical {{ background: {COLOR_BG}; width: 8px; border-radius: 4px; }}
    QScrollBar::handle:vertical {{ background: {COLOR_BORDER}; border-radius: 4px; }}
    QLabel {{ color: {COLOR_TEXT}; }}
    QToolButton {{
        background: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER};
        border-radius: 4px; padding: 4px; color: {COLOR_TEXT};
    }}
    QToolButton:hover {{ background: {COLOR_SELECTED}; }}
"""


# ═══════════════════════════════════════════════════════════════════════════
# Utilitários
# ═══════════════════════════════════════════════════════════════════════════

def _qimage_to_pixmap(img: QImage, size: int = 48) -> QPixmap:
    """Converte QImage → QPixmap quadrado com fundo xadrez."""
    canvas = QImage(size, size, QImage.Format.Format_ARGB32)
    canvas.fill(0)

    # Fundo xadrez (transparência)
    painter = QPainter(canvas)
    tile = 8
    for row in range(0, size, tile):
        for col in range(0, size, tile):
            color = QColor("#3a3a3a") if (row // tile + col // tile) % 2 == 0 else QColor("#555555")
            painter.fillRect(col, row, tile, tile, color)

    scaled = img.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.FastTransformation)
    x = (size - scaled.width()) // 2
    y = (size - scaled.height()) // 2
    painter.drawImage(x, y, scaled)
    painter.end()

    return QPixmap.fromImage(canvas)


# ═══════════════════════════════════════════════════════════════════════════
# Canvas do frame (zoom + pixel drawing)
# ═══════════════════════════════════════════════════════════════════════════

class FrameCanvas(QWidget):
    """
    Canvas central que mostra o frame atual em alta escala.
    Suporta:
      - Zoom via scroll / slider
      - Desenho de pixel com LMB (cor primária)
      - Apagar com RMB (transparente)
      - Grade de pixels opcional
    """

    pixel_painted = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._image: Optional[QImage] = None
        self._zoom = 16
        self._grid = True
        self._primary_color = QColor(Qt.GlobalColor.white)
        self._painting = False
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setMinimumSize(256, 256)

    # ── pública ──────────────────────────────────────────────────────────

    def set_image(self, img: QImage):
        self._image = img.copy()
        self._update_size()
        self.update()

    def get_image(self) -> Optional[QImage]:
        return self._image

    def set_zoom(self, z: int):
        self._zoom = max(1, min(z, 32))
        self._update_size()
        self.update()

    def set_grid(self, on: bool):
        self._grid = on
        self.update()

    def set_primary_color(self, c: QColor):
        self._primary_color = c

    # ── privado ──────────────────────────────────────────────────────────

    def _update_size(self):
        if self._image:
            w = self._image.width() * self._zoom
            h = self._image.height() * self._zoom
            self.setFixedSize(w, h)

    def _pixel_at(self, pos) -> tuple[int, int]:
        return pos.x() // self._zoom, pos.y() // self._zoom

    def _paint_pixel(self, pos, erase=False):
        if self._image is None:
            return
        x, y = self._pixel_at(pos)
        if 0 <= x < self._image.width() and 0 <= y < self._image.height():
            color = QColor(Qt.GlobalColor.transparent) if erase else self._primary_color
            self._image.setPixelColor(x, y, color)
            self.update()
            self.pixel_painted.emit()

    # ── eventos ──────────────────────────────────────────────────────────

    def mousePressEvent(self, e):
        self._painting = True
        self._paint_pixel(e.pos(), erase=e.button() == Qt.MouseButton.RightButton)

    def mouseMoveEvent(self, e):
        if self._painting:
            self._paint_pixel(e.pos(),
                              erase=e.buttons() & Qt.MouseButton.RightButton)

    def mouseReleaseEvent(self, e):
        self._painting = False

    def wheelEvent(self, e: QWheelEvent):
        delta = 1 if e.angleDelta().y() > 0 else -1
        self.set_zoom(self._zoom + delta * 2)

    def paintEvent(self, e):
        if self._image is None:
            return
        painter = QPainter(self)
        z = self._zoom
        w = self._image.width()
        h = self._image.height()

        # Xadrez de fundo
        tile = z if z >= 4 else 4
        for row in range(h):
            for col in range(w):
                light = (row + col) % 2 == 0
                c = QColor("#3a3a3a") if light else QColor("#555555")
                painter.fillRect(col * z, row * z, z, z, c)

        # Pixels da imagem
        painter.drawImage(QRect(0, 0, w * z, h * z),
                          self._image,
                          QRect(0, 0, w, h))

        # Grade
        if self._grid and z >= 4:
            painter.setPen(QPen(QColor("#ffffff22"), 0.5))
            for col in range(w + 1):
                painter.drawLine(col * z, 0, col * z, h * z)
            for row in range(h + 1):
                painter.drawLine(0, row * z, w * z, row * z)

        painter.end()


# ═══════════════════════════════════════════════════════════════════════════
# Preview de animação
# ═══════════════════════════════════════════════════════════════════════════

class AnimationPreview(QLabel):
    """Reproduz os frames em loop usando QTimer."""

    def __init__(self, size=96, parent=None):
        super().__init__(parent)
        self._frames: list[QImage] = []
        self._frametime = 2          # ticks
        self._current = 0
        self._size = size
        self._playing = True

        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"background: #111; border: 1px solid {COLOR_BORDER}; border-radius: 6px;")

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._next_frame)
        self._restart_timer()

    def set_frames(self, frames: list[QImage], frametime: int = 2):
        self._frames = [f.copy() for f in frames]
        self._frametime = max(1, frametime)
        self._current = 0
        self._restart_timer()
        self._show_current()

    def set_playing(self, on: bool):
        self._playing = on
        if on:
            self._restart_timer()
        else:
            self._timer.stop()

    def _restart_timer(self):
        # 1 tick = 50 ms (20 TPS do Minecraft)
        self._timer.start(self._frametime * 50)

    def _next_frame(self):
        if not self._frames:
            return
        self._current = (self._current + 1) % len(self._frames)
        self._show_current()

    def _show_current(self):
        if not self._frames:
            self.clear()
            return
        img = self._frames[self._current]
        px = _qimage_to_pixmap(img, self._size)
        self.setPixmap(px)


# ═══════════════════════════════════════════════════════════════════════════
# Painel esquerdo — lista de frames
# ═══════════════════════════════════════════════════════════════════════════

class FrameListPanel(QWidget):
    frame_selected = pyqtSignal(int)
    frames_changed = pyqtSignal()

    def __init__(self, anim: AnimationData, parent=None):
        super().__init__(parent)
        self._anim = anim
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(6)

        # Título
        title = QLabel("🎞  Frames")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        lay.addWidget(title)

        # Lista
        self._list = QListWidget()
        self._list.setIconSize(QSize(52, 52))
        self._list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self._list.currentRowChanged.connect(self.frame_selected)
        self._list.model().rowsMoved.connect(self._on_rows_moved)
        lay.addWidget(self._list)

        # Botões
        btn_row = QHBoxLayout()
        for icon, tip, slot in [
            ("➕", "Novo frame em branco",   self._add_blank),
            ("📋", "Duplicar frame",         self._duplicate),
            ("🗑", "Remover frame",          self._remove),
            ("⬆", "Mover para cima",        self._move_up),
            ("⬇", "Mover para baixo",       self._move_down),
        ]:
            btn = QToolButton()
            btn.setText(icon)
            btn.setToolTip(tip)
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)

        lay.addLayout(btn_row)

        # Botão importar PNG
        btn_import = QPushButton("📂  Importar PNG / Sprite-sheet")
        btn_import.clicked.connect(self._import_png)
        lay.addWidget(btn_import)

        self.refresh()

    # ── refresh ──────────────────────────────────────────────────────────

    def refresh(self, keep_selection: int = -1):
        self._list.blockSignals(True)
        self._list.clear()
        for i, frame in enumerate(self._anim.frames):
            px = _qimage_to_pixmap(frame.image, 52)
            item = QListWidgetItem(QIcon(px), f"Frame {i + 1}")
            item.setSizeHint(QSize(80, 64))
            self._list.addItem(item)
        self._list.blockSignals(False)

        if keep_selection >= 0:
            self._list.setCurrentRow(min(keep_selection, self._anim.frame_count - 1))
        elif self._list.count() > 0:
            self._list.setCurrentRow(0)

    def current_index(self) -> int:
        return self._list.currentRow()

    # ── slots ──────────────────────────────────────────────────────────

    def _add_blank(self):
        idx = self._anim.add_blank_frame()
        self.refresh(idx)
        self.frames_changed.emit()

    def _duplicate(self):
        idx = self.current_index()
        new_idx = self._anim.duplicate_frame(idx)
        if new_idx >= 0:
            self.refresh(new_idx)
            self.frames_changed.emit()

    def _remove(self):
        idx = self.current_index()
        if self._anim.remove_frame(idx):
            self.refresh(max(0, idx - 1))
            self.frames_changed.emit()

    def _move_up(self):
        idx = self.current_index()
        if self._anim.move_frame(idx, idx - 1):
            self.refresh(idx - 1)
            self.frames_changed.emit()

    def _move_down(self):
        idx = self.current_index()
        if self._anim.move_frame(idx, idx + 1):
            self.refresh(idx + 1)
            self.frames_changed.emit()

    def _on_rows_moved(self, parent, src_start, src_end, dst_parent, dst_row):
        """Sincroniza o drag-and-drop da QListWidget com AnimationData."""
        # Rebuild frames list from current list order
        new_frames = []
        for i in range(self._list.count()):
            item = self._list.item(i)
            # Recupera o índice original pelo texto "Frame N"
            orig_text = item.text()  # "Frame N"
            try:
                orig_idx = int(orig_text.split()[-1]) - 1
                new_frames.append(self._anim.frames[orig_idx])
            except (ValueError, IndexError):
                pass
        self._anim.frames = new_frames
        self.refresh(self._list.currentRow())
        self.frames_changed.emit()

    def _import_png(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Importar PNG ou Sprite-sheet",
            filter="Imagens PNG (*.png)"
        )
        if not path:
            return
        img = QImage(path)
        if img.isNull():
            QMessageBox.warning(self, "Erro", "Não foi possível carregar a imagem.")
            return

        w = img.width()
        h = img.height()

        if h > w and h % w == 0:
            # Parece ser sprite-sheet vertical
            reply = QMessageBox.question(
                self, "Sprite-sheet detectada",
                f"A imagem ({w}×{h}) parece ser uma sprite-sheet com {h // w} frames.\n"
                "Deseja fatiá-la automaticamente?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                imported = AnimationData.from_spritesheet(img)
                self._anim.frames = imported.frames
                self.refresh(0)
                self.frames_changed.emit()
                return

        # Importar como frame único
        frame_img = img.convertToFormat(QImage.Format.Format_ARGB32)
        self._anim.frames.append(AnimationFrame(image=frame_img))
        self.refresh(self._anim.frame_count - 1)
        self.frames_changed.emit()


# ═══════════════════════════════════════════════════════════════════════════
# Painel direito — preview + configuração .mcmeta
# ═══════════════════════════════════════════════════════════════════════════

class McmetaPanel(QWidget):
    settings_changed = pyqtSignal()

    def __init__(self, anim: AnimationData, parent=None):
        super().__init__(parent)
        self._anim = anim
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(10)

        # ── Preview ─────────────────────────────────────────────────────
        grp_prev = QGroupBox("Preview")
        prev_lay = QVBoxLayout(grp_prev)

        self._preview = AnimationPreview(size=120)
        prev_lay.addWidget(self._preview, alignment=Qt.AlignmentFlag.AlignCenter)

        # Play/Pause
        self._btn_play = QPushButton("⏸  Pausar")
        self._btn_play.setCheckable(True)
        self._btn_play.clicked.connect(self._toggle_play)
        prev_lay.addWidget(self._btn_play)

        # Frame atual
        self._lbl_frame = QLabel("Frame 1 / 1")
        self._lbl_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_frame.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 11px;")
        prev_lay.addWidget(self._lbl_frame)

        lay.addWidget(grp_prev)

        # ── Configuração .mcmeta ─────────────────────────────────────────
        grp_cfg = QGroupBox(".mcmeta — Configurações")
        form = QFormLayout(grp_cfg)
        form.setSpacing(8)

        # frametime
        self._spin_ft = QSpinBox()
        self._spin_ft.setRange(1, 200)
        self._spin_ft.setValue(self._anim.frametime)
        self._spin_ft.setSuffix("  tick(s)")
        self._spin_ft.setToolTip(
            "1 tick = 50 ms (20 TPS)\n"
            "frametime 2 = 100 ms por frame"
        )
        self._spin_ft.valueChanged.connect(self._on_frametime_changed)
        form.addRow("Frametime:", self._spin_ft)

        # interpolate
        self._chk_interp = QCheckBox("Interpolação suave")
        self._chk_interp.setChecked(self._anim.interpolate)
        self._chk_interp.setToolTip("Suaviza a transição entre frames (blur)")
        self._chk_interp.toggled.connect(self._on_interpolate_changed)
        form.addRow("", self._chk_interp)

        lay.addWidget(grp_cfg)

        # ── JSON preview ─────────────────────────────────────────────────
        grp_json = QGroupBox("JSON gerado (.mcmeta)")
        json_lay = QVBoxLayout(grp_json)

        self._lbl_json = QLabel()
        self._lbl_json.setStyleSheet(
            f"font-family: monospace; font-size: 11px; "
            f"background: {COLOR_BG}; color: #a8d8a8; "
            f"padding: 8px; border-radius: 4px;"
        )
        self._lbl_json.setWordWrap(True)
        json_lay.addWidget(self._lbl_json)

        lay.addWidget(grp_json)
        lay.addStretch()

        self.refresh_json()

    # ── público ──────────────────────────────────────────────────────────

    def refresh_preview(self, frames: list[QImage]):
        self._preview.set_frames(frames, self._anim.frametime)
        n = len(frames)
        self._lbl_frame.setText(f"{n} frame{'s' if n != 1 else ''}")

    def refresh_json(self):
        self._lbl_json.setText(self._anim.to_mcmeta())

    # ── slots ─────────────────────────────────────────────────────────────

    def _toggle_play(self, checked: bool):
        self._preview.set_playing(not checked)
        self._btn_play.setText("▶  Retomar" if checked else "⏸  Pausar")

    def _on_frametime_changed(self, val: int):
        self._anim.frametime = val
        self._preview._frametime = val
        self._preview._restart_timer()
        self.refresh_json()
        self.settings_changed.emit()

    def _on_interpolate_changed(self, val: bool):
        self._anim.interpolate = val
        self.refresh_json()
        self.settings_changed.emit()


# ═══════════════════════════════════════════════════════════════════════════
# Diálogo principal
# ═══════════════════════════════════════════════════════════════════════════

class AnimationEditorDialog(QDialog):
    """
    Diálogo completo do editor de animações.

    Após aceitar:
        dlg.animation  →  AnimationData pronto para exportar
        dlg.texture_name  →  nome sugerido (ex: 'lava')
    """

    def __init__(self, anim: Optional[AnimationData] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎬  Editor de Texturas Animadas — Minecraft Mod Studio")
        self.setMinimumSize(1000, 620)
        self.resize(1200, 700)

        # Cria animação inicial com 4 frames de exemplo se não fornecida
        if anim is None:
            self.animation = AnimationData(name="nova_animacao", frametime=2)
            for color in [0xFF1a6b1a, 0xFF228822, 0xFF1e7a1e, 0xFF166616]:
                self.animation.add_blank_frame(color)
        else:
            self.animation = anim

        self._current_frame_idx: int = 0

        self.setStyleSheet(PANEL_STYLE)
        self._build_ui()
        self._sync_all()

    # ── construção da UI ─────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        # Toolbar superior
        root.addWidget(self._build_toolbar())

        # Splitter principal 3 colunas
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Coluna 1 — frame list
        self._frame_panel = FrameListPanel(self.animation)
        self._frame_panel.setMinimumWidth(150)
        self._frame_panel.setMaximumWidth(220)
        self._frame_panel.frame_selected.connect(self._on_frame_selected)
        self._frame_panel.frames_changed.connect(self._on_frames_changed)
        splitter.addWidget(self._frame_panel)

        # Coluna 2 — canvas (scrollable)
        canvas_wrapper = QWidget()
        cw_lay = QVBoxLayout(canvas_wrapper)
        cw_lay.setContentsMargins(4, 4, 4, 4)

        lbl_canvas = QLabel("✏  Canvas do Frame")
        lbl_canvas.setStyleSheet("font-weight: bold; font-size: 13px;")
        cw_lay.addWidget(lbl_canvas)

        # Zoom
        zoom_row = QHBoxLayout()
        zoom_row.addWidget(QLabel("Zoom:"))
        self._zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self._zoom_slider.setRange(2, 32)
        self._zoom_slider.setValue(16)
        self._zoom_slider.setTickInterval(2)
        self._zoom_slider.valueChanged.connect(lambda v: self._canvas.set_zoom(v))
        zoom_row.addWidget(self._zoom_slider)
        self._lbl_zoom = QLabel("16×")
        self._zoom_slider.valueChanged.connect(lambda v: self._lbl_zoom.setText(f"{v}×"))
        zoom_row.addWidget(self._lbl_zoom)

        # Grid toggle
        self._chk_grid = QCheckBox("Grade")
        self._chk_grid.setChecked(True)
        self._chk_grid.toggled.connect(lambda v: self._canvas.set_grid(v))
        zoom_row.addWidget(self._chk_grid)
        cw_lay.addLayout(zoom_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(False)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setStyleSheet(f"background: {COLOR_BG};")
        self._canvas = FrameCanvas()
        self._canvas.pixel_painted.connect(self._on_pixel_painted)
        scroll.setWidget(self._canvas)
        cw_lay.addWidget(scroll)

        splitter.addWidget(canvas_wrapper)

        # Coluna 3 — preview + .mcmeta
        self._mcmeta_panel = McmetaPanel(self.animation)
        self._mcmeta_panel.setMinimumWidth(220)
        self._mcmeta_panel.setMaximumWidth(320)
        self._mcmeta_panel.settings_changed.connect(self._on_settings_changed)
        splitter.addWidget(self._mcmeta_panel)

        splitter.setSizes([180, 600, 260])
        root.addWidget(splitter)

        # Botões OK / Cancelar
        bbox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btn_ok = bbox.button(QDialogButtonBox.StandardButton.Ok)
        btn_ok.setText("✅  Salvar animação")
        btn_ok.setStyleSheet(f"background: {COLOR_ACCENT}; color: #fff; font-weight: bold; padding: 6px 18px;")
        btn_cancel = bbox.button(QDialogButtonBox.StandardButton.Cancel)
        btn_cancel.setText("Cancelar")
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)

        # Botão exportar direto
        btn_export = QPushButton("📦  Exportar PNG + .mcmeta")
        btn_export.setStyleSheet(f"background: {COLOR_ACCENT2}; color: #fff; font-weight: bold; padding: 6px 16px;")
        btn_export.clicked.connect(self._export_files)

        bottom_row = QHBoxLayout()
        bottom_row.addWidget(btn_export)
        bottom_row.addStretch()
        bottom_row.addWidget(bbox)
        root.addLayout(bottom_row)

    def _build_toolbar(self) -> QWidget:
        bar = QWidget()
        bar.setStyleSheet(f"background: {COLOR_SURFACE}; border-radius: 6px;")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(8, 4, 8, 4)
        lay.setSpacing(8)

        lbl = QLabel("🎬  Editor de Animações")
        lbl.setStyleSheet("font-weight: bold; font-size: 14px;")
        lay.addWidget(lbl)

        lay.addStretch()

        # Cor primária
        lbl_color = QLabel("Cor:")
        lay.addWidget(lbl_color)

        self._color_btn = QPushButton()
        self._color_btn.setFixedSize(28, 28)
        self._color_btn.setStyleSheet("background: white; border: 2px solid #888; border-radius: 4px;")
        self._color_btn.setToolTip("Clique para escolher cor de pintura")
        self._color_btn.clicked.connect(self._pick_color)
        lay.addWidget(self._color_btn)

        # Preset de cores do Minecraft
        lay.addWidget(QLabel("Presets:"))
        presets = [
            ("#ff4444", "Vermelho"),
            ("#44ff44", "Verde"),
            ("#4444ff", "Azul"),
            ("#ffff44", "Amarelo"),
            ("#ff8800", "Laranja"),
            ("#ffffff", "Branco"),
            ("#000000", "Preto"),
        ]
        for hex_c, name in presets:
            btn = QPushButton()
            btn.setFixedSize(20, 20)
            btn.setToolTip(name)
            btn.setStyleSheet(f"background: {hex_c}; border: 1px solid #555; border-radius: 3px;")
            btn.clicked.connect(lambda _, c=hex_c: self._set_color(c))
            lay.addWidget(btn)

        return bar

    # ── sincronização ────────────────────────────────────────────────────

    def _sync_all(self):
        """Atualiza canvas, preview e JSON a partir do estado atual."""
        if self.animation.frame_count == 0:
            return

        idx = self._current_frame_idx
        idx = max(0, min(idx, self.animation.frame_count - 1))
        self._current_frame_idx = idx

        # Canvas
        self._canvas.set_image(self.animation.frames[idx].image)

        # Preview
        imgs = [f.image for f in self.animation.frames]
        self._mcmeta_panel.refresh_preview(imgs)
        self._mcmeta_panel.refresh_json()

    # ── slots ────────────────────────────────────────────────────────────

    def _on_frame_selected(self, idx: int):
        if idx < 0 or idx >= self.animation.frame_count:
            return
        # Salva edições no frame anterior antes de trocar
        self._save_canvas_to_frame(self._current_frame_idx)
        self._current_frame_idx = idx
        self._canvas.set_image(self.animation.frames[idx].image)

    def _on_frames_changed(self):
        self._current_frame_idx = self._frame_panel.current_index()
        self._sync_all()

    def _on_pixel_painted(self):
        """Sincroniza o pixel editado de volta para o frame em memória."""
        self._save_canvas_to_frame(self._current_frame_idx)
        # Atualiza miniatura na lista
        frame = self.animation.frames[self._current_frame_idx]
        px = _qimage_to_pixmap(frame.image, 52)
        item = self._frame_panel._list.item(self._current_frame_idx)
        if item:
            item.setIcon(QIcon(px))
        # Atualiza preview
        imgs = [f.image for f in self.animation.frames]
        self._mcmeta_panel.refresh_preview(imgs)

    def _on_settings_changed(self):
        pass  # JSON já atualizado pelo McmetaPanel

    def _save_canvas_to_frame(self, idx: int):
        """Copia a imagem atual do canvas de volta ao frame."""
        if 0 <= idx < self.animation.frame_count:
            img = self._canvas.get_image()
            if img:
                self.animation.frames[idx].image = img.copy()

    def _pick_color(self):
        from PyQt6.QtWidgets import QColorDialog
        c = QColorDialog.getColor(self._canvas._primary_color, self, "Escolher cor")
        if c.isValid():
            self._set_color(c.name())

    def _set_color(self, hex_color: str):
        c = QColor(hex_color)
        self._canvas.set_primary_color(c)
        self._color_btn.setStyleSheet(
            f"background: {hex_color}; border: 2px solid #888; border-radius: 4px;"
        )

    # ── exportação ───────────────────────────────────────────────────────

    def _export_files(self):
        """Exporta PNG vertical + .mcmeta para pasta escolhida pelo usuário."""
        self._save_canvas_to_frame(self._current_frame_idx)

        if self.animation.frame_count == 0:
            QMessageBox.warning(self, "Sem frames", "Adicione pelo menos um frame antes de exportar.")
            return

        folder = QFileDialog.getExistingDirectory(self, "Escolher pasta de destino")
        if not folder:
            return

        name = self.animation.name.strip() or "animacao"
        png_path  = os.path.join(folder, f"{name}.png")
        meta_path = os.path.join(folder, f"{name}.png.mcmeta")

        # PNG vertical
        sheet = self.animation.to_spritesheet()
        if sheet:
            ok = sheet.save(png_path, "PNG")
            if not ok:
                QMessageBox.critical(self, "Erro", f"Não foi possível salvar {png_path}")
                return

        # .mcmeta
        with open(meta_path, "w", encoding="utf-8") as f:
            f.write(self.animation.to_mcmeta())

        QMessageBox.information(
            self, "Exportado!",
            f"Arquivos gerados em:\n"
            f"  • {os.path.basename(png_path)}\n"
            f"  • {os.path.basename(meta_path)}\n\n"
            f"Coloque na pasta:\n"
            f"  assets/<namespace>/textures/block/"
        )

    # ── accept ───────────────────────────────────────────────────────────

    def accept(self):
        self._save_canvas_to_frame(self._current_frame_idx)
        super().accept()


# ═══════════════════════════════════════════════════════════════════════════
# Widget embutido na aba do MainWindow
# ═══════════════════════════════════════════════════════════════════════════

class AnimationEditorWidget(QWidget):
    """
    Versão do editor de animações para viver dentro de uma aba do MainWindow.

    Diferentemente do AnimationEditorDialog (que é um QDialog modal),
    este widget é permanente e gerencia uma lista de animações do workspace.

    Sinal emitido quando o usuário salva uma animação no projeto:
        animation_saved(name: str, texture_type: str)
    """

    animation_saved = pyqtSignal(str, str)

    def __init__(self, workspace, parent=None):
        super().__init__(parent)
        self._workspace = workspace
        self._current_anim_idx: int = -1
        self.setStyleSheet(PANEL_STYLE)
        self._build_ui()

    # ── construção ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        # Painel esquerdo — lista de animações do projeto
        left = QWidget()
        left.setMaximumWidth(220)
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(6)

        lbl = QLabel("🎬  Animações do Projeto")
        lbl.setStyleSheet("font-weight: bold; font-size: 13px;")
        left_lay.addWidget(lbl)

        self._anim_list = QListWidget()
        self._anim_list.currentRowChanged.connect(self._on_anim_selected)
        left_lay.addWidget(self._anim_list)

        # Tipo de textura
        from PyQt6.QtWidgets import QComboBox, QLabel as QL
        left_lay.addWidget(QL("Tipo de textura:"))
        self._combo_type = QComboBox()
        self._combo_type.addItems(["block", "item", "particle", "environment", "entity", "gui"])
        self._combo_type.setStyleSheet(
            f"background: {COLOR_SURFACE}; color: {COLOR_TEXT}; "
            f"border: 1px solid {COLOR_BORDER}; border-radius: 4px; padding: 3px 6px;"
        )
        left_lay.addWidget(self._combo_type)

        # Botões de gestão
        btn_new = QPushButton("➕  Nova Animação")
        btn_new.clicked.connect(self._new_animation)
        left_lay.addWidget(btn_new)

        btn_save = QPushButton("💾  Salvar no Projeto")
        btn_save.setStyleSheet(f"background: {COLOR_ACCENT}; color: #fff; font-weight: bold;")
        btn_save.clicked.connect(self._save_to_project)
        left_lay.addWidget(btn_save)

        btn_remove = QPushButton("🗑  Remover")
        btn_remove.setStyleSheet(f"color: {COLOR_DANGER};")
        btn_remove.clicked.connect(self._remove_animation)
        left_lay.addWidget(btn_remove)

        root.addWidget(left)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(f"color: {COLOR_BORDER};")
        root.addWidget(sep)

        # Área central — editor completo (reutiliza o mesmo layout do Dialog)
        self._editor_area = QWidget()
        self._editor_lay = QVBoxLayout(self._editor_area)
        self._editor_lay.setContentsMargins(0, 0, 0, 0)

        self._placeholder = QLabel("← Selecione ou crie uma animação")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-size: 14px;")
        self._editor_lay.addWidget(self._placeholder)

        root.addWidget(self._editor_area, 1)

        self._active_dialog: Optional[AnimationEditorDialog] = None
        self._refresh_list()

    # ── lista de animações ────────────────────────────────────────────────

    def _refresh_list(self):
        self._anim_list.clear()
        animations = getattr(self._workspace, "animations", [])
        for anim, tex_type in animations:
            item = QListWidgetItem(f"🎞  {anim.name}  [{tex_type}]")
            self._anim_list.addItem(item)
        if not animations:
            empty = QListWidgetItem("(nenhuma animação)")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            self._anim_list.addItem(empty)

    def _on_anim_selected(self, idx: int):
        animations = getattr(self._workspace, "animations", [])
        if 0 <= idx < len(animations):
            self._current_anim_idx = idx
            anim, tex_type = animations[idx]
            self._combo_type.setCurrentText(tex_type)
            self._open_editor_for(anim)
        else:
            self._current_anim_idx = -1

    def _open_editor_for(self, anim: AnimationData):
        """Substitui o conteúdo da área central pelo editor da animação escolhida."""
        # Remove widget anterior
        while self._editor_lay.count():
            item = self._editor_lay.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # Cria um AnimationEditorDialog sem barra de botões e o embute como widget
        editor = _InlineAnimationEditor(anim)
        self._editor_lay.addWidget(editor)
        self._active_editor = editor

    # ── ações ─────────────────────────────────────────────────────────────

    def _new_animation(self):
        if not hasattr(self._workspace, "animations"):
            self._workspace.animations = []

        anim = AnimationData(name=f"animacao_{len(self._workspace.animations) + 1}", frametime=2)
        anim.add_blank_frame(0xFF1a6b1a)
        anim.add_blank_frame(0xFF228822)
        anim.add_blank_frame(0xFF1e7a1e)
        anim.add_blank_frame(0xFF166616)

        tex_type = self._combo_type.currentText()
        self._workspace.animations.append((anim, tex_type))
        self._refresh_list()
        self._anim_list.setCurrentRow(len(self._workspace.animations) - 1)

    def _save_to_project(self):
        idx = self._current_anim_idx
        animations = getattr(self._workspace, "animations", [])
        if idx < 0 or idx >= len(animations):
            QMessageBox.information(self, "Info", "Selecione uma animação primeiro.")
            return

        anim, _ = animations[idx]
        tex_type = self._combo_type.currentText()
        animations[idx] = (anim, tex_type)

        self._refresh_list()
        self._anim_list.setCurrentRow(idx)
        self.animation_saved.emit(anim.name, tex_type)

    def _remove_animation(self):
        idx = self._current_anim_idx
        animations = getattr(self._workspace, "animations", [])
        if idx < 0 or idx >= len(animations):
            return
        anim, _ = animations[idx]
        reply = QMessageBox.question(
            self, "Remover",
            f"Remover a animação '{anim.name}' do projeto?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            del animations[idx]
            self._current_anim_idx = -1
            self._refresh_list()
            # Limpa área central
            while self._editor_lay.count():
                item = self._editor_lay.takeAt(0)
                if item.widget():
                    item.widget().setParent(None)
            self._editor_lay.addWidget(self._placeholder)


class _InlineAnimationEditor(QWidget):
    """
    Editor embutido (sem botões OK/Cancelar) para uso dentro do AnimationEditorWidget.
    Reutiliza FrameListPanel, FrameCanvas e McmetaPanel.
    """

    def __init__(self, anim: AnimationData, parent=None):
        super().__init__(parent)
        self.animation = anim
        self._current_frame_idx = 0
        self.setStyleSheet(PANEL_STYLE)
        self._build_ui()
        self._sync_all()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(4)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Frame list
        self._frame_panel = FrameListPanel(self.animation)
        self._frame_panel.setMaximumWidth(200)
        self._frame_panel.frame_selected.connect(self._on_frame_selected)
        self._frame_panel.frames_changed.connect(self._on_frames_changed)
        splitter.addWidget(self._frame_panel)

        # Canvas
        canvas_wrap = QWidget()
        cw = QVBoxLayout(canvas_wrap)
        cw.setContentsMargins(4, 4, 4, 4)

        zoom_row = QHBoxLayout()
        zoom_row.addWidget(QLabel("Zoom:"))
        self._zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self._zoom_slider.setRange(2, 32)
        self._zoom_slider.setValue(16)
        self._zoom_slider.valueChanged.connect(lambda v: self._canvas.set_zoom(v))
        zoom_row.addWidget(self._zoom_slider)
        lbl_z = QLabel("16×")
        self._zoom_slider.valueChanged.connect(lambda v: lbl_z.setText(f"{v}×"))
        zoom_row.addWidget(lbl_z)
        chk_grid = QCheckBox("Grade")
        chk_grid.setChecked(True)
        chk_grid.toggled.connect(lambda v: self._canvas.set_grid(v))
        zoom_row.addWidget(chk_grid)
        cw.addLayout(zoom_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(False)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setStyleSheet(f"background: {COLOR_BG};")
        self._canvas = FrameCanvas()
        self._canvas.pixel_painted.connect(self._on_pixel_painted)
        scroll.setWidget(self._canvas)
        cw.addWidget(scroll)
        splitter.addWidget(canvas_wrap)

        # Mcmeta + preview
        self._mcmeta_panel = McmetaPanel(self.animation)
        self._mcmeta_panel.setMaximumWidth(300)
        splitter.addWidget(self._mcmeta_panel)

        splitter.setSizes([170, 500, 260])
        root.addWidget(splitter)

    def _sync_all(self):
        if not self.animation.frame_count:
            return
        idx = max(0, min(self._current_frame_idx, self.animation.frame_count - 1))
        self._current_frame_idx = idx
        self._canvas.set_image(self.animation.frames[idx].image)
        self._mcmeta_panel.refresh_preview([f.image for f in self.animation.frames])
        self._mcmeta_panel.refresh_json()

    def _on_frame_selected(self, idx: int):
        if idx < 0 or idx >= self.animation.frame_count:
            return
        self._save_canvas(self._current_frame_idx)
        self._current_frame_idx = idx
        self._canvas.set_image(self.animation.frames[idx].image)

    def _on_frames_changed(self):
        self._current_frame_idx = self._frame_panel.current_index()
        self._sync_all()

    def _on_pixel_painted(self):
        self._save_canvas(self._current_frame_idx)
        frame = self.animation.frames[self._current_frame_idx]
        px = _qimage_to_pixmap(frame.image, 52)
        item = self._frame_panel._list.item(self._current_frame_idx)
        if item:
            item.setIcon(QIcon(px))
        self._mcmeta_panel.refresh_preview([f.image for f in self.animation.frames])

    def _save_canvas(self, idx: int):
        if 0 <= idx < self.animation.frame_count:
            img = self._canvas.get_image()
            if img:
                self.animation.frames[idx].image = img.copy()


# ═══════════════════════════════════════════════════════════════════════════
# Teste standalone
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dlg = AnimationEditorDialog()
    if dlg.exec():
        print("=== .mcmeta gerado ===")
        print(dlg.animation.to_mcmeta())
        print(f"\n{dlg.animation.frame_count} frames, "
              f"frametime={dlg.animation.frametime}, "
              f"interpolate={dlg.animation.interpolate}")
    sys.exit(0)
