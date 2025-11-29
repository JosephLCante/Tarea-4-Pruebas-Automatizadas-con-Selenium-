from pages.login_page import LoginPage
from selenium.webdriver.common.by import By

def test_login_camino_feliz(driver, base_url):
    lp = LoginPage(driver)
    lp.go(base_url)
    lp.login("admin@example.com", "password123")
    assert "Estudiantes" in driver.page_source

def test_login_negativo(driver, base_url):
    lp = LoginPage(driver)
    lp.go(base_url)
    lp.login("wrong@example.com", "badpass")
    assert "Email o contraseña incorrectos" in driver.page_source

def test_login_limite(driver, base_url):
    lp = LoginPage(driver)
    lp.go(base_url)
    long_email = "a"*300 + "@test.com"
    lp.login(long_email, "password123")
    assert "Email o contraseña incorrectos" in driver.page_source or "Todos los campos" in driver.page_source
