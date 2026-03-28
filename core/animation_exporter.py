"""
core/animation_exporter.py
--------------------------
Módulo responsável por incluir texturas animadas no ZIP do resource pack.

Integração com exporter.py existente:
    from core.animation_exporter import AnimationExporter
    anim_exp = AnimationExporter(workspace)
    anim_exp.write_to_zip(zipf)   # zipf = zipfile.ZipFile aberto

Estrutura gerada no ZIP:
    assets/<namespace>/textures/block/<name>.png
    assets/<namespace>/textures/block/<name>.png.mcmeta
    assets/<namespace>/textures/item/<name>.png       (se tipo == 'item')
    assets/<namespace>/textures/item/<name>.png.mcmeta
"""

from __future__ import annotations

import io
import zipfile
from typing import List, Tuple

from PyQt6.QtCore import QBuffer, QIODevice
from PyQt6.QtGui import QImage

from core.animation import AnimationData


# ────────────────────────────────────────────────────────────────────────────
# Tipos de textura suportados → caminho dentro do resource pack
# ────────────────────────────────────────────────────────────────────────────

TEXTURE_PATHS = {
    "block":       "textures/block",
    "item":        "textures/item",
    "entity":      "textures/entity",
    "particle":    "textures/particle",
    "environment": "textures/environment",
    "gui":         "textures/gui",
}


# ────────────────────────────────────────────────────────────────────────────
# AnimationExporter
# ────────────────────────────────────────────────────────────────────────────

class AnimationExporter:
    """
    Responsável por serializar todas as AnimationData de um workspace
    e adicioná-las ao ZIP do resource pack.

    Parâmetros
    ----------
    namespace : str
        Namespace do resource pack (ex: "meu_pack", "meumod").
    animations : list[tuple[AnimationData, str]]
        Lista de (animação, tipo_de_textura).
        tipo_de_textura deve ser uma chave de TEXTURE_PATHS.
    """

    def __init__(self, namespace: str, animations: List[Tuple[AnimationData, str]] | None = None):
        self.namespace = namespace.lower().replace(" ", "_")
        self.animations: List[Tuple[AnimationData, str]] = animations or []

    # ── API pública ──────────────────────────────────────────────────────

    def add(self, anim: AnimationData, texture_type: str = "block"):
        """Adiciona uma animação para exportação."""
        if texture_type not in TEXTURE_PATHS:
            texture_type = "block"
        self.animations.append((anim, texture_type))

    def write_to_zip(self, zipf: zipfile.ZipFile) -> List[str]:
        """
        Escreve todas as animações no ZipFile aberto.

        Retorna lista de caminhos adicionados (útil para log/console).
        """
        added: List[str] = []

        for anim, tex_type in self.animations:
            paths = self._write_animation(zipf, anim, tex_type)
            added.extend(paths)

        return added

    def write_pack_mcmeta(self, zipf: zipfile.ZipFile, description: str = "Resource Pack", pack_format: int = 34):
        """
        Garante que o pack.mcmeta está no ZIP.
        pack_format 34 = Minecraft 1.20.x
        """
        import json
        path = "pack.mcmeta"
        if path not in zipf.namelist():
            content = json.dumps({
                "pack": {
                    "pack_format": pack_format,
                    "description": description
                }
            }, indent=2)
            zipf.writestr(path, content)

    # ── interno ──────────────────────────────────────────────────────────

    def _write_animation(
        self,
        zipf: zipfile.ZipFile,
        anim: AnimationData,
        tex_type: str,
    ) -> List[str]:
        """Escreve PNG vertical + .mcmeta no ZIP. Retorna os caminhos escritos."""

        if anim.frame_count == 0:
            return []

        name = anim.name.strip().lower().replace(" ", "_") or "animacao"
        tex_folder = TEXTURE_PATHS.get(tex_type, "textures/block")
        base_path = f"assets/{self.namespace}/{tex_folder}/{name}"

        png_path  = f"{base_path}.png"
        meta_path = f"{base_path}.png.mcmeta"

        # ── PNG vertical (sprite-sheet) ──────────────────────────────────
        sheet = anim.to_spritesheet()
        if sheet is None:
            return []

        buf = QBuffer()
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        sheet.save(buf, "PNG")
        png_bytes = bytes(buf.data())
        buf.close()

        zipf.writestr(png_path, png_bytes)

        # ── .mcmeta ─────────────────────────────────────────────────────
        mcmeta_content = anim.to_mcmeta()
        zipf.writestr(meta_path, mcmeta_content)

        return [png_path, meta_path]


# ────────────────────────────────────────────────────────────────────────────
# Função auxiliar — exportação rápida para arquivo .zip standalone
# ────────────────────────────────────────────────────────────────────────────

def export_animations_to_zip(
    animations: List[Tuple[AnimationData, str]],
    namespace: str,
    output_path: str,
    description: str = "Resource Pack criado com Minecraft Mod Studio",
    pack_format: int = 34,
) -> Tuple[bool, str]:
    """
    Exporta uma lista de animações para um arquivo ZIP standalone.

    Retorna (sucesso: bool, mensagem: str)

    Uso:
        ok, msg = export_animations_to_zip(
            [(anim_lava, "block"), (anim_agua, "block")],
            namespace="meu_pack",
            output_path="/caminho/para/saida.zip"
        )
    """
    try:
        exporter = AnimationExporter(namespace=namespace, animations=animations)

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            exporter.write_pack_mcmeta(zipf, description=description, pack_format=pack_format)
            added = exporter.write_to_zip(zipf)

        msg = f"Exportado com sucesso!\n{len(added)} arquivo(s) gerado(s):\n"
        msg += "\n".join(f"  • {p}" for p in added)
        return True, msg

    except Exception as exc:
        return False, f"Erro na exportação: {exc}"
