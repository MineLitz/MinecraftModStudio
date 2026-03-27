import os
import subprocess
import threading
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTextEdit, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor


class BuildWorker(QObject):
    output    = pyqtSignal(str, str)   # text, color
    finished  = pyqtSignal(bool, str)  # success, message

    def __init__(self, project_dir: str, java_path: str = "java"):
        super().__init__()
        self.project_dir = project_dir
        self.java_path   = java_path
        self._cancelled  = False

    def run(self):
        gradlew = os.path.join(self.project_dir, "gradlew.bat")
        if not os.path.exists(gradlew):
            gradlew = os.path.join(self.project_dir, "gradlew")
        if not os.path.exists(gradlew):
            self.finished.emit(False, "gradlew não encontrado no projeto.")
            return

        env = os.environ.copy()
        if self.java_path != "java":
            java_home = os.path.dirname(os.path.dirname(self.java_path))
            env["JAVA_HOME"] = java_home

        cmd = [gradlew, "build", "--info", "--no-daemon"] if os.name == "nt" else \
              ["bash", gradlew, "build", "--info", "--no-daemon"]

        self.output.emit("▶ Iniciando build...\n", "#6ab84a")
        self.output.emit(f"  Diretório: {self.project_dir}\n", "#505050")
        self.output.emit(f"  Comando: {' '.join(cmd)}\n\n", "#505050")

        try:
            proc = subprocess.Popen(
                cmd,
                cwd=self.project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                shell=(os.name == "nt"),
            )
            self._proc = proc

            for line in proc.stdout:
                if self._cancelled:
                    proc.kill()
                    self.finished.emit(False, "Build cancelado.")
                    return
                color = "#c04040" if "ERROR" in line.upper() or "FAILED" in line.upper() \
                    else "#c89040" if "WARN" in line.upper() \
                    else "#6ab84a" if "BUILD SUCCESSFUL" in line \
                    else "#707070"
                self.output.emit(line.rstrip(), color)

            proc.wait()
            success = proc.returncode == 0

            if success:
                # Find output jar
                libs_dir = os.path.join(self.project_dir, "build", "libs")
                jars = [f for f in os.listdir(libs_dir)
                        if f.endswith(".jar") and "sources" not in f] \
                    if os.path.exists(libs_dir) else []
                jar_msg = f"\n✅ Mod compilado: build/libs/{jars[0]}" if jars else \
                          "\n✅ BUILD SUCCESSFUL"
                self.finished.emit(True, jar_msg)
            else:
                self.finished.emit(False, "\n❌ BUILD FAILED — veja os erros acima")

        except Exception as e:
            self.finished.emit(False, f"Erro ao executar build: {e}")

    def cancel(self):
        self._cancelled = True
        if hasattr(self, "_proc"):
            try: self._proc.kill()
            except Exception: pass


class BuildDialog(QDialog):
    def __init__(self, project_dir: str, project_name: str,
                 loader: str, java_path: str = "java", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Build — {project_name}")
        self.setMinimumSize(680, 480)
        self.setModal(True)
        self.project_dir  = project_dir
        self.loader       = loader
        self.java_path    = java_path
        self._worker      = None
        self._thread      = None
        self._build_done  = False
        self._build_ok    = False
        self._jar_path    = ""
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Header
        hdr = QFrame()
        hdr.setStyleSheet("background:#1e1e1e; border-bottom:1px solid #2a2a2a;")
        hdr.setFixedHeight(56)
        h = QHBoxLayout(hdr)
        h.setContentsMargins(20, 0, 20, 0)
        h.setSpacing(12)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        t = QLabel("Build do Mod")
        t.setStyleSheet("background:transparent; color:#d0d0d0; font-size:14px; font-weight:bold;")
        self._sub = QLabel(f"Compilando com {self.loader}...")
        self._sub.setStyleSheet("background:transparent; color:#505050; font-size:11px;")
        title_col.addWidget(t)
        title_col.addWidget(self._sub)
        h.addLayout(title_col)
        h.addStretch()

        self._progress = QProgressBar()
        self._progress.setFixedWidth(160)
        self._progress.setFixedHeight(8)
        self._progress.setRange(0, 0)  # indeterminate
        self._progress.setStyleSheet("""
            QProgressBar { background:#2a2a2a; border-radius:4px; border:none; }
            QProgressBar::chunk { background:#6ab84a; border-radius:4px; }
        """)
        h.addWidget(self._progress)
        lay.addWidget(hdr)

        # Console output
        self._console = QTextEdit()
        self._console.setReadOnly(True)
        self._console.setFont(QFont("Consolas", 10))
        self._console.setStyleSheet("""
            QTextEdit { background:#111; border:none; padding:8px; }
        """)
        lay.addWidget(self._console)

        # Footer
        ftr = QFrame()
        ftr.setStyleSheet("background:#1e1e1e; border-top:1px solid #2a2a2a;")
        ftr.setFixedHeight(52)
        f = QHBoxLayout(ftr)
        f.setContentsMargins(16, 0, 16, 0)
        f.setSpacing(10)

        self._open_btn = QPushButton("📁 Abrir pasta build/libs")
        self._open_btn.setFixedHeight(32)
        self._open_btn.hide()
        self._open_btn.clicked.connect(self._open_output)
        f.addWidget(self._open_btn)

        f.addStretch()

        self._cancel_btn = QPushButton("Cancelar")
        self._cancel_btn.setObjectName("btn_secondary")
        self._cancel_btn.setFixedWidth(100)
        self._cancel_btn.clicked.connect(self._cancel)
        f.addWidget(self._cancel_btn)

        self._close_btn = QPushButton("Fechar")
        self._close_btn.setObjectName("btn_primary")
        self._close_btn.setFixedWidth(100)
        self._close_btn.hide()
        self._close_btn.clicked.connect(self.accept)
        f.addWidget(self._close_btn)

        lay.addWidget(ftr)

    def start_build(self):
        self._worker = BuildWorker(self.project_dir, self.java_path)
        self._worker.output.connect(self._append)
        self._worker.finished.connect(self._on_finished)

        self._thread = threading.Thread(target=self._worker.run, daemon=True)
        self._thread.start()

    def _append(self, text: str, color: str):
        self._console.setTextColor(QColor(color))
        self._console.append(text)
        self._console.ensureCursorVisible()

    def _on_finished(self, success: bool, message: str):
        self._build_done = True
        self._build_ok   = success
        self._progress.setRange(0, 1)
        self._progress.setValue(1)

        color = "#6ab84a" if success else "#c04040"
        self._append(message, color)

        self._sub.setText("Build concluído ✅" if success else "Build falhou ❌")
        self._sub.setStyleSheet(f"background:transparent; color:{color}; font-size:11px;")

        self._cancel_btn.hide()
        self._close_btn.show()

        if success:
            libs = os.path.join(self.project_dir, "build", "libs")
            if os.path.exists(libs):
                self._jar_path = libs
                self._open_btn.show()

    def _cancel(self):
        if self._worker:
            self._worker.cancel()
        self.reject()

    def _open_output(self):
        if self._jar_path and os.path.exists(self._jar_path):
            os.startfile(self._jar_path)

    def closeEvent(self, e):
        if self._worker and not self._build_done:
            self._worker.cancel()
        e.accept()
