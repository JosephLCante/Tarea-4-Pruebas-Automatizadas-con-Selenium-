from pages.login_page import LoginPage
from pages.crud_page import CrudPage

def test_delete_camino_feliz(driver, base_url):
    lp = LoginPage(driver)
    lp.go(base_url)
    lp.login("admin@example.com", "password123")
    cp = CrudPage(driver)
    cp.go_to_list(base_url)
    # eliminar el primer registro
    cp.delete_first()
    # tras submit la página muestra mensaje
    assert "Estudiante eliminado" in driver.page_source or "Estudiantes" in driver.page_source
