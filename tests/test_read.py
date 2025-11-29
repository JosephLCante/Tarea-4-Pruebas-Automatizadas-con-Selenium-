from pages.login_page import LoginPage
from pages.crud_page import CrudPage

def test_read_list_shows_students(driver, base_url):
    lp = LoginPage(driver)
    lp.go(base_url)
    lp.login("admin@example.com", "password123")
    cp = CrudPage(driver)
    cp.go_to_list(base_url)
    table_text = cp.get_table_text()
    # al menos la cabecera o texto que indica que la tabla existe
    assert "Nombre" in table_text or "Estudiantes" in driver.page_source
