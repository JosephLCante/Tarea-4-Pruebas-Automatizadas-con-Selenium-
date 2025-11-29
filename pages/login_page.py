from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class LoginPage(BasePage):
    email = (By.ID, "email")
    password = (By.ID, "password")
    submit = (By.ID, "login-btn")

    def go(self, base_url):
        self.visit(f"{base_url}/login")

    def login(self, email, password):
        self.type(*self.email, email)
        self.type(*self.password, password)
        self.click(*self.submit)
