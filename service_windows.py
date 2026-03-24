import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PATH = os.path.join(BASE_DIR, '.venv')
sys.path.insert(0, os.path.join(VENV_PATH, 'Lib', 'site-packages'))

import subprocess
import win32event
import win32service
import win32serviceutil
import servicemanager

APP_DIR = BASE_DIR
PORT = int(os.environ.get("PORT", "8000"))
PYTHON_EXE = os.path.join(VENV_PATH, 'Scripts', 'python.exe')


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
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ""),
        )
        self.main()

    def main(self):
        cmd = [
            PYTHON_EXE, "-m", "uvicorn",
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