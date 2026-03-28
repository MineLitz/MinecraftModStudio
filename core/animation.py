"""
core/animation.py
-----------------
Modelo de dados para texturas animadas do Minecraft.

Responsabilidades:
  - Armazenar frames (QImage)
  - Gerar o JSON do .mcmeta
  - Montar o PNG vertical (sprite-sheet) para exportação
  - Carregar um PNG vertical existente e fatiá-lo em frames
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, Optional

from PyQt6.QtCore import QBuffer, QByteArray, QIODevice
from PyQt6.QtGui import QImage, QPainter


# ---------------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------------

@dataclass
class AnimationFrame:
    """Representa um único frame da animação."""
    image: QImage
    duration: int = 1          # duração individual (em ticks) — 0 → usa frametime global


# ---------------------------------------------------------------------------
# AnimationData
# ---------------------------------------------------------------------------

@dataclass
class AnimationData:
    """
    Modelo completo de uma textura animada do Minecraft.

    Parâmetros do .mcmeta:
        frametime   – ticks por frame (padrão = 1 tick ≈ 50 ms)
        interpolate – suaviza a transição entre frames
        frames      – lista de AnimationFrame
    """

    name: str = "untitled"
    frametime: int = 2
    interpolate: bool = False
    frames: List[AnimationFrame] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Propriedades de conveniência
    # ------------------------------------------------------------------

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    @property
    def frame_size(self) -> tuple[int, int]:
        """Retorna (width, height) do primeiro frame, ou (16,16) se vazio."""
        if self.frames:
            img = self.frames[0].image
            return img.width(), img.height()
        return 16, 16

    # ------------------------------------------------------------------
    # Geração do .mcmeta
    # ------------------------------------------------------------------

    def to_mcmeta(self) -> str:
        """
        Gera o conteúdo JSON do arquivo .mcmeta.

        Formato esperado pelo Minecraft:
        {
          "animation": {
            "frametime": 2,
            "interpolate": false,
            "frames": [
              {"index": 0, "time": 3},
              1,
              2
            ]
          }
        }
        Se todos os frames usam duração padrão (duration == 1 ou == 0),
        a lista de frames é omitida (Minecraft usa frametime global).
        """
        anim: dict = {"frametime": self.frametime}

        if self.interpolate:
            anim["interpolate"] = True

        # Verifica se algum frame tem duração customizada
        has_custom = any(f.duration > 1 for f in self.frames)

        if has_custom:
            frame_list = []
            for i, f in enumerate(self.frames):
                if f.duration > 1:
                    frame_list.append({"index": i, "time": f.duration})
                else:
                    frame_list.append(i)
            anim["frames"] = frame_list

        return json.dumps({"animation": anim}, indent=2)

    # ------------------------------------------------------------------
    # Geração do PNG vertical (sprite-sheet)
    # ------------------------------------------------------------------

    def to_spritesheet(self) -> Optional[QImage]:
        """
        Empilha todos os frames verticalmente num único QImage.
        Retorna None se não houver frames.
        """
        if not self.frames:
            return None

        w, h = self.frame_size
        total_h = h * self.frame_count

        sheet = QImage(w, total_h, QImage.Format.Format_ARGB32)
        sheet.fill(0)  # transparente

        painter = QPainter(sheet)
        for i, frame in enumerate(self.frames):
            img = frame.image.scaled(w, h)   # garante tamanho uniforme
            painter.drawImage(0, i * h, img)
        painter.end()

        return sheet

    def to_spritesheet_bytes(self, fmt: str = "PNG") -> bytes:
        """Retorna o PNG vertical como bytes prontos para gravar em disco."""
        sheet = self.to_spritesheet()
        if sheet is None:
            return b""

        buf = QBuffer()
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        sheet.save(buf, fmt)
        return bytes(buf.data())

    # ------------------------------------------------------------------
    # Carregamento de PNG vertical existente
    # ------------------------------------------------------------------

    @classmethod
    def from_spritesheet(
        cls,
        image: QImage,
        name: str = "imported",
        frametime: int = 2,
        interpolate: bool = False,
    ) -> "AnimationData":
        """
        Carrega um PNG vertical e o faria em N frames quadrados.

        Assume que cada frame é um quadrado de `width × width` pixels.
        Exemplo: PNG 16×160 → 10 frames de 16×16.
        """
        w = image.width()
        h = image.height()

        if w == 0 or h == 0:
            return cls(name=name, frametime=frametime, interpolate=interpolate)

        # Frame height = width (textura quadrada)
        frame_h = w
        n_frames = h // frame_h

        frames: List[AnimationFrame] = []
        for i in range(n_frames):
            crop = image.copy(0, i * frame_h, w, frame_h)
            frames.append(AnimationFrame(image=crop))

        return cls(
            name=name,
            frametime=frametime,
            interpolate=interpolate,
            frames=frames,
        )

    # ------------------------------------------------------------------
    # Adicionar / remover frames
    # ------------------------------------------------------------------

    def add_blank_frame(self, color: int = 0xFF555555) -> int:
        """Adiciona um frame em branco e retorna seu índice."""
        w, h = self.frame_size
        img = QImage(w, h, QImage.Format.Format_ARGB32)
        img.fill(color)
        self.frames.append(AnimationFrame(image=img))
        return self.frame_count - 1

    def duplicate_frame(self, index: int) -> int:
        """Duplica o frame em `index` e insere logo após. Retorna novo índice."""
        if 0 <= index < self.frame_count:
            original = self.frames[index]
            copy_img = original.image.copy()
            new_frame = AnimationFrame(image=copy_img, duration=original.duration)
            self.frames.insert(index + 1, new_frame)
            return index + 1
        return -1

    def remove_frame(self, index: int) -> bool:
        if 0 <= index < self.frame_count and self.frame_count > 1:
            del self.frames[index]
            return True
        return False

    def move_frame(self, from_idx: int, to_idx: int) -> bool:
        n = self.frame_count
        if 0 <= from_idx < n and 0 <= to_idx < n and from_idx != to_idx:
            frame = self.frames.pop(from_idx)
            self.frames.insert(to_idx, frame)
            return True
        return False
