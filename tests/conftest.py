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
    # options.add_argument("--headless")  # usar en CI si quieres
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    def fin():
        driver.quit()
    request.addfinalizer(fin)
    return driver

# Hook para tomar screenshot al fallar
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver")
        if driver:
            screenshots_dir = os.path.join(os.getcwd(), "reports", "screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
            file_name = f"{item.name}.png"
            path = os.path.join(screenshots_dir, file_name)
            driver.save_screenshot(path)
