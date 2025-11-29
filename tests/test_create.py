from pages.login_page import LoginPage
from pages.crud_page import CrudPage
from selenium.webdriver.common.by import By

def login(driver, base_url):
    lp = LoginPage(driver)
    lp.go(base_url)
    lp.login("admin@example.com", "password123")

def test_create_camino_feliz(driver, base_url):
    login(driver, base_url)
    cp = CrudPage(driver)
    cp.go_to_list(base_url)
    cp.click_create()
    cp.fill_form("Juan Perez", 20, "Matemáticas", "juanp@example.com")
    cp.save()
    assert "Estudiante creado correctamente" in driver.page_source
    assert "Juan Perez" in driver.page_source

def test_create_negativo(driver, base_url):
    login(driver, base_url)
    cp = CrudPage(driver)
    cp.go_to_list(base_url)
    cp.click_create()
    # dejar todo vacío y guardar
    cp.save()
    assert "Todos los campos son obligatorios" in driver.page_source

def test_create_limite(driver, base_url):
    login(driver, base_url)
    cp = CrudPage(driver)
    cp.go_to_list(base_url)
    cp.click_create()
    long_name = "A" * 255
    cp.fill_form(long_name, 99, "C", "limit@example.com")
    cp.save()
    assert ("Estudiante creado correctamente" in driver.page_source) or ("Todos los campos son obligatorios" in driver.page_source)
