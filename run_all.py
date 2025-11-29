# run_all.py
import sys
import subprocess
import time
import urllib.request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def wait_for_server(url="http://127.0.0.1:5000", timeout=30, interval=0.5):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                code = resp.getcode()
                if code and 200 <= code < 400:
                    return True
        except Exception:
            pass
        time.sleep(interval)
    return False

def main():
    os.makedirs(os.path.join(BASE_DIR, "reports"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "reports", "screenshots"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "reports", "logs"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)

    python = sys.executable
    server_cmd = [python, "main.py"]

    server_log_path = os.path.join(BASE_DIR, "logs", "server_output.log")
    server_log = open(server_log_path, "a", encoding="utf-8")

    print("Iniciando servidor Flask...")
    proc = subprocess.Popen(server_cmd, stdout=server_log, stderr=server_log, cwd=BASE_DIR)

    try:
        print("Esperando a que el servidor responda en http://127.0.0.1:5000 ...")
        ready = wait_for_server("http://127.0.0.1:5000", timeout=30)
        if not ready:
            print("El servidor no respondió en 30s. Revisa logs en 'logs/server_output.log'")
            proc.terminate()
            proc.wait(timeout=5)
            server_log.close()
            sys.exit(2)

        print("Servidor listo. Ejecutando pytest...")
        pytest_cmd = [python, "-m", "pytest", "--html=reports/report.html", "--self-contained-html", "-q"]
        result = subprocess.run(pytest_cmd, cwd=BASE_DIR)
        rc = result.returncode
        print(f"pytest finalizó con código de retorno: {rc}")

    except KeyboardInterrupt:
        print("Interrupción por teclado: deteniendo servidor y saliendo.")
        rc = 130
    finally:
        print("Deteniendo servidor Flask...")
        try:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
        except Exception as e:
            print("Error al detener servidor:", e)
        server_log.close()

    sys.exit(rc)

if __name__ == "__main__":
    main()
