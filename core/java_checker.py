import subprocess
import os
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class JavaInfo:
    found: bool
    version: Optional[int] = None
    path: Optional[str] = None
    message: str = ""


def check_java() -> JavaInfo:
    """Detects Java installation and version."""
    candidates = ["java"]

    # Common Windows paths
    if os.name == "nt":
        for base in [
            r"C:\Program Files\Java",
            r"C:\Program Files\Eclipse Adoptium",
            r"C:\Program Files\Microsoft",
            r"C:\Program Files\BellSoft",
        ]:
            if os.path.exists(base):
                for entry in os.listdir(base):
                    java_bin = os.path.join(base, entry, "bin", "java.exe")
                    if os.path.exists(java_bin):
                        candidates.insert(0, java_bin)

        # Check JAVA_HOME
        java_home = os.environ.get("JAVA_HOME", "")
        if java_home:
            java_bin = os.path.join(java_home, "bin", "java.exe")
            if os.path.exists(java_bin):
                candidates.insert(0, java_bin)

    for candidate in candidates:
        try:
            result = subprocess.run(
                [candidate, "-version"],
                capture_output=True, text=True, timeout=5
            )
            output = result.stderr + result.stdout
            match = re.search(r'version "(\d+)[\._]', output)
            if match:
                major = int(match.group(1))
                if major == 1:
                    # Old format: 1.8 → 8
                    match2 = re.search(r'version "1\.(\d+)', output)
                    if match2:
                        major = int(match2.group(1))
                return JavaInfo(
                    found=True,
                    version=major,
                    path=candidate,
                    message=f"Java {major} encontrado em: {candidate}"
                )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    return JavaInfo(
        found=False,
        message="Java não encontrado no sistema."
    )


def check_java_for_minecraft() -> tuple[bool, str]:
    """
    Returns (ok, message).
    Minecraft modding requires Java 21+.
    """
    info = check_java()
    if not info.found:
        return False, (
            "Java 21 não encontrado.\n\n"
            "Para compilar mods Minecraft, instale o Java 21:\n"
            "https://adoptium.net/temurin/releases/?version=21\n\n"
            "Após instalar, reinicie o Minecraft Mod Studio."
        )
    if info.version < 21:
        return False, (
            f"Java {info.version} encontrado, mas é necessário Java 21+.\n\n"
            "Baixe o Java 21 em:\n"
            "https://adoptium.net/temurin/releases/?version=21"
        )
    return True, f"Java {info.version} pronto para compilar."
