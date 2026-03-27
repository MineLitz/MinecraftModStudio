import time
import atexit
from PyQt6.QtCore import QSettings

APP_ID = "1485306661223796836"


class DiscordRPC:
    def __init__(self):
        self._rpc = None
        self._connected = False
        self._start_time = int(time.time())

    def is_enabled(self) -> bool:
        settings = QSettings("MMS", "MinecraftModStudio")
        return settings.value("discord_rpc/enabled", True, type=bool)

    def connect(self):
        if not self.is_enabled():
            return
        try:
            from pypresence import Presence
            self._rpc = Presence(APP_ID)
            self._rpc.connect()
            self._connected = True
            self._start_time = int(time.time())
            print("[Discord] Rich Presence conectado.")
        except Exception as e:
            self._connected = False
            self._rpc = None
            print(f"[Discord] Não foi possível conectar: {e}")

    def disconnect(self):
        if self._rpc and self._connected:
            try:
                self._rpc.clear()
                self._rpc.close()
                print("[Discord] Rich Presence desconectado.")
            except Exception:
                pass
        # Force close the underlying socket if it exists
        try:
            if self._rpc and hasattr(self._rpc, "sock_writer"):
                self._rpc.sock_writer.close()
        except Exception:
            pass
        try:
            if self._rpc and hasattr(self._rpc, "sock"):
                self._rpc.sock.close()
        except Exception:
            pass
        self._connected = False
        self._rpc = None

    def update(self, project_name: str = "", project_type: str = "mod"):
        if not self._connected or not self.is_enabled():
            return
        try:
            if project_name:
                ptype = "Resource Pack" if project_type == "resource_pack" else "Mod"
                details = f"Editing {project_name}"
                state   = ptype
            else:
                details = "Idle"
                state   = "No project open"

            self._rpc.update(
                details=details,
                state=state,
                large_image="simbolo",
                large_text="Minecraft Mod Studio",
                start=self._start_time,
            )
        except Exception as e:
            print(f"[Discord] Falha ao atualizar presença: {e}")
            self._connected = False

    def set_enabled(self, enabled: bool, project_name: str = "",
                    project_type: str = "mod"):
        settings = QSettings("MMS", "MinecraftModStudio")
        settings.setValue("discord_rpc/enabled", enabled)
        if enabled:
            if not self._connected:
                self.connect()
            self.update(project_name, project_type)
        else:
            self.disconnect()


# ── Global singleton ──────────────────────────────────────────────────────────
rpc = DiscordRPC()

# Garantir desconexão mesmo se o app fechar inesperadamente
atexit.register(rpc.disconnect)
