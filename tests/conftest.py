# Insertar la raíz del proyecto en sys.path para permitir imports desde pages/
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture(scope="session")
def base_url():
    return os.getenv("BASE_URL", "http://localhost:5000")

@pytest.fixture
def driver(request):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")  # activar en CI si lo deseas

    # habilitar captura de logs del navegador (Chrome)
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

    # Iniciar driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def fin():
        try:
            driver.quit()
        except Exception:
            pass
    request.addfinalizer(fin)
    return driver

# Hook para guardar screenshots y browser logs al terminar cada test
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    rep = outcome.get_result()

    # directorios para artefactos
    reports_dir = os.path.join(os.getcwd(), "reports")
    screenshots_dir = os.path.join(reports_dir, "screenshots")
    logs_dir = os.path.join(reports_dir, "logs")
    os.makedirs(screenshots_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    test_name = item.name

    # intentar recuperar driver (manejar distintas versiones de pytest)
    driver = None
    try:
        # preferible: si el test usó el fixture 'driver'
        driver = item.funcargs.get("driver")
    except Exception:
        try:
            driver = item._request.getfixturevalue("driver")
        except Exception:
            driver = None

    # guardar logs de consola del navegador si hay driver
    if driver is not None:
        try:
            # obtener logs de navegador (Chrome)
            browser_logs = []
            try:
                browser_logs = driver.get_log('browser')
            except Exception:
                browser_logs = []
            if browser_logs:
                log_path = os.path.join(logs_dir, f"{test_name}_browser.log")
                with open(log_path, "w", encoding="utf-8") as f:
                    for entry in browser_logs:
                        # entry tiene keys: level, timestamp, message
                        f.write(f"{entry.get('level')} {entry.get('timestamp')} {entry.get('message')}\n")
        except Exception:
            # no bloquear el reporte si falla la recolección de logs
            pass

    # si el test falló, guardar screenshot
    if rep.when == "call" and rep.failed:
        if driver is not None:
            try:
                screenshot_path = os.path.join(screenshots_dir, f"{test_name}.png")
                driver.save_screenshot(screenshot_path)
            except Exception:
                pass
