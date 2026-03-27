import os
import sys
import zipfile
import io
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(BASE_DIR, "resources", "fonts")

# TTF names to look for inside the release zip
NEEDED = [
    "Inter-Regular.ttf",
    "Inter-Medium.ttf",
    "Inter-SemiBold.ttf",
    "Inter-Bold.ttf",
]

# Official Inter v4.0 release zip (works em qualquer máquina com internet normal)
INTER_ZIP_URL = (
    "https://github.com/rsms/inter/releases/download/v4.0/Inter-4.0.zip"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
    )
}


def _fonts_already_downloaded() -> bool:
    """Retorna True se todos os TTFs já estão na pasta local."""
    return all(
        os.path.exists(os.path.join(FONTS_DIR, f)) for f in NEEDED
    )


def _check_system_inter() -> str | None:
    """Verifica se Inter está instalada nas Fonts do Windows."""
    if sys.platform != "win32":
        return None
    win_fonts = r"C:\Windows\Fonts"
    for candidate in ["Inter-Regular.ttf", "Inter.ttf", "inter-Regular.ttf"]:
        path = os.path.join(win_fonts, candidate)
        if os.path.exists(path):
            return "Inter"
    return None


def _download_and_extract() -> bool:
    """Baixa o zip do Inter e extrai os TTFs necessários."""
    os.makedirs(FONTS_DIR, exist_ok=True)
    print("[Fonts] Baixando Inter 4.0 (primeira execução)...")
    try:
        req = urllib.request.Request(INTER_ZIP_URL, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()

        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            extracted = 0
            for member in zf.namelist():
                fname = os.path.basename(member)
                if fname in NEEDED:
                    dest = os.path.join(FONTS_DIR, fname)
                    with zf.open(member) as src, open(dest, "wb") as dst:
                        dst.write(src.read())
                    extracted += 1

        if extracted > 0:
            print(f"[Fonts] Inter extraída ({extracted} arquivos).")
            return True
        else:
            print("[Fonts] Arquivos TTF não encontrados no zip.")
            return False

    except Exception as e:
        print(f"[Fonts] Falha ao baixar Inter: {e}")
        return False


def load_fonts() -> str:
    """
    Tenta carregar a fonte Inter via:
      1. Pasta local (resources/fonts/)
      2. Fontes do sistema Windows
      3. Download do zip oficial
    Retorna o nome da fonte para usar no QSS.
    """
    from PyQt6.QtGui import QFontDatabase

    # 1. Já baixada anteriormente?
    if not _fonts_already_downloaded():
        # 2. Instalada no sistema Windows?
        sys_font = _check_system_inter()
        if sys_font:
            print("[Fonts] Inter encontrada nas fontes do sistema.")
            return "Inter"
        # 3. Tenta baixar
        _download_and_extract()

    # Carrega arquivos locais no Qt
    loaded = 0
    for name in NEEDED:
        path = os.path.join(FONTS_DIR, name)
        if os.path.exists(path):
            fid = QFontDatabase.addApplicationFont(path)
            if fid != -1:
                loaded += 1

    if loaded > 0:
        print(f"[Fonts] Inter carregada ({loaded} variantes).")
        return "Inter"

    print("[Fonts] Usando Segoe UI como fallback.")
    return "Segoe UI"
