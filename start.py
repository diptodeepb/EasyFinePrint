#!/usr/bin/env python3
"""
EasyFinePrint Development Server Runner.
Starts FastAPI backend and Vite frontend concurrently with colored, prefixed logs.
"""
import os
import subprocess
import sys
import threading
import signal
import shutil

COLORS = {
    "backend": "\033[94m",   # Blue
    "frontend": "\033[96m",  # Cyan
    "system": "\033[92m",    # Green
    "error": "\033[91m",     # Red
    "reset": "\033[0m",
}


def log(prefix: str, msg: str, color_key: str = "system"):
    col = COLORS.get(color_key, COLORS["reset"])
    print(f"{col}[{prefix}]{COLORS['reset']} {msg}", flush=True)


def find_backend_python():
    candidates = [
        os.path.join("backend", ".venv", "bin", "python3"),
        os.path.join("backend", ".venv", "bin", "python"),
        sys.executable,
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                res = subprocess.run(
                    [path, "-c", "import uvicorn, fastapi, trafilatura"],
                    capture_output=True,
                    text=True,
                )
                if res.returncode == 0:
                    return os.path.abspath(path)
            except Exception:
                continue
    return os.path.abspath(sys.executable)


def stream_logs(pipe, prefix: str, color_key: str):
    col = COLORS.get(color_key, COLORS["reset"])
    for line in iter(pipe.readline, ""):
        if not line:
            break
        print(f"{col}[{prefix}]{COLORS['reset']} {line.rstrip()}", flush=True)
    pipe.close()


def main():
    log("EasyFinePrint", "Starting development servers...", "system")

    # 1. Check Python environment
    py_bin = find_backend_python()
    log("EasyFinePrint", f"Using Python: {py_bin}", "system")

    # 2. Check npm
    npm_bin = shutil.which("npm")
    if not npm_bin:
        log("EasyFinePrint", "Error: npm is not found in PATH", "error")
        sys.exit(1)

    procs = []

    try:
        # Start Backend
        log("Backend", "Starting FastAPI on http://localhost:8000 ...", "backend")
        backend_proc = subprocess.Popen(
            [py_bin, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            cwd=os.path.abspath("backend"),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        procs.append(backend_proc)
        t_be = threading.Thread(target=stream_logs, args=(backend_proc.stdout, "API:8000", "backend"), daemon=True)
        t_be.start()

        # Start Frontend
        log("Frontend", "Starting Vite on http://localhost:5173 ...", "frontend")
        frontend_proc = subprocess.Popen(
            [npm_bin, "run", "dev"],
            cwd=os.path.abspath("frontend"),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        procs.append(frontend_proc)
        t_fe = threading.Thread(target=stream_logs, args=(frontend_proc.stdout, "UI:5173", "frontend"), daemon=True)
        t_fe.start()

        log("EasyFinePrint", "Both servers running! Press Ctrl+C to terminate.", "system")
        backend_proc.wait()

    except KeyboardInterrupt:
        log("EasyFinePrint", "Received shutdown signal. Stopping servers...", "system")
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    p.kill()
        log("EasyFinePrint", "All services cleanly stopped.", "system")


if __name__ == "__main__":
    main()
