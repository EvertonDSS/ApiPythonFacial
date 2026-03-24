"""
Serviço Windows nativo para a API de Verificação Facial.
Usa pywin32 (win32serviceutil) - sem programas externos.

Uso (como Administrador):
    python service_windows.py install   - instalar
    python service_windows.py start     - iniciar
    python service_windows.py stop      - parar
    python service_windows.py remove    - desinstalar
    python service_windows.py debug     - rodar em modo debug (console)
"""

import os
import sys
import subprocess
import win32event
import win32service
import win32serviceutil
import servicemanager


# Diretório da aplicação (onde está main.py)
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("PORT", "8000"))


class ApiPythonFacialService(win32serviceutil.ServiceFramework):
    _svc_name_ = "ApiPythonFacial"
    _svc_display_name_ = "API de Verificação Facial"
    _svc_description_ = "API REST de verificação facial com InsightFace (FastAPI + Uvicorn)"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.process = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.process and self.process.poll() is None:
            self.process.terminate()
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ""),
        )
        self.main()

    def main(self):
        python_exe = sys.executable
        cmd = [
            python_exe, "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", str(PORT),
        ]

        self.process = subprocess.Popen(
            cmd,
            cwd=APP_DIR,
            env={**os.environ, "PYTHONPATH": APP_DIR},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Aguarda sinal de parada ou fim do processo
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ApiPythonFacialService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(ApiPythonFacialService)
