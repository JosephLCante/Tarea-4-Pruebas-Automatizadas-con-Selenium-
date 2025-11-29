from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class CrudPage(BasePage):
    # Selectores principales
    create_btn = (By.ID, "create-btn")
    table = (By.ID, "students-table")
    save_btn = (By.ID, "save-btn")
    # inputs del formulario
    nombre = (By.ID, "nombre")
    edad = (By.ID, "edad")
    curso = (By.ID, "curso")
    student_email = (By.ID, "student-email")

    def go_to_list(self, base_url):
        self.visit(f"{base_url}/students")

    def click_create(self):
        self.click(*self.create_btn)

    def fill_form(self, nombre, edad, curso, email):
        self.type(*self.nombre, nombre)
        self.type(*self.edad, str(edad))
        self.type(*self.curso, curso)
        self.type(*self.student_email, email)

    def save(self):
        self.click(*self.save_btn)

    def edit_first(self):
        btns = self.driver.find_elements(By.CSS_SELECTOR, "a[id^='edit-']")
        if not btns:
            raise Exception("No hay botones de editar")
        btns[0].click()

    def delete_first(self):
        btns = self.driver.find_elements(By.CSS_SELECTOR, "button[id^='delete-']")
        if not btns:
            raise Exception("No hay botones de eliminar")
        btns[0].click()

    def get_table_text(self):
        return self.find(*self.table).text
