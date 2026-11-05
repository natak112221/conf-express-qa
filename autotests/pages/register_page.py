from selenium.webdriver.common.by import By

from .base_page import BasePage


class RegisterPage(BasePage):
    FIELDS = {"login": (By.ID, "login"), "password": (By.ID, "password"), "email": (By.ID, "email"), "phone": (By.ID, "phone")}
    SUBMIT = (By.CSS_SELECTOR, "main form button.btn")
    ERRORS = (By.CSS_SELECTOR, ".error")

    def load(self):
        return self.open("/register")

    def register(self, login, password="Password123", email=None, phone="+7 900 123-45-67"):
        values = {"login": login, "password": password, "email": email or login + "@mail.test", "phone": phone}
        for name, locator in self.FIELDS.items():
            self.type(locator, values[name])
        self.click(self.SUBMIT)

    def error_texts(self):
        self.visible(self.ERRORS)
        return [e.text for e in self.driver.find_elements(*self.ERRORS)]
