from selenium.webdriver.common.by import By

from .base_page import BasePage


class LoginPage(BasePage):
    LOGIN = (By.ID, "login")
    PASSWORD = (By.ID, "password")
    SUBMIT = (By.CSS_SELECTOR, "main form button.btn")
    TOGGLE = (By.CSS_SELECTOR, "[data-toggle-password]")
    ALERT = (By.CSS_SELECTOR, ".alert")

    def load(self):
        return self.open("/login")

    def sign_in(self, login, password):
        self.type(self.LOGIN, login)
        self.type(self.PASSWORD, password)
        self.click(self.SUBMIT)

    def error_text(self):
        return self.text_of(self.ALERT)

    def password_type(self):
        return self.visible(self.PASSWORD).get_attribute("type")

    def toggle_password(self):
        self.click(self.TOGGLE)

    def validation_message(self, locator):
        """Текст подсказки браузера у обязательного поля (атрибут required)."""
        return self.driver.execute_script("return arguments[0].validationMessage", self.visible(locator))
