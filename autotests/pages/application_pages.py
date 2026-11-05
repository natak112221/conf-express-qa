from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from .base_page import BasePage


class EventPage(BasePage):
    APPLY = (By.LINK_TEXT, "Подать заявку")

    def apply(self):
        self.click(self.APPLY)
        self.wait_url_contains("/applications/new")


class ApplicationFormPage(BasePage):
    ROOM = (By.ID, "room")
    PAYMENT = (By.ID, "payment")
    SUBMIT = (By.CSS_SELECTOR, "main form button.btn")

    def fill_and_send(self, room="Малый зал", payment="Картой онлайн"):
        Select(self.visible(self.ROOM)).select_by_visible_text(room)
        Select(self.visible(self.PAYMENT)).select_by_visible_text(payment)
        self.click(self.SUBMIT)
        self.wait_url_path("/applications")


class MyApplicationsPage(BasePage):
    CARDS = (By.CSS_SELECTOR, ".app-card")

    def load(self):
        return self.open("/applications")

    def cards(self):
        """Список (название мероприятия, статус) по карточкам заявок."""
        self.visible(self.CARDS)
        return [
            (c.find_element(By.TAG_NAME, "h3").text, c.find_element(By.CSS_SELECTOR, ".status").text)
            for c in self.driver.find_elements(*self.CARDS)
        ]


class AdminPage(BasePage):
    CARDS = (By.CSS_SELECTOR, ".app-card")
    FILTER_EVENT = (By.ID, "f-event")
    FILTER_SUBMIT = (By.CSS_SELECTOR, "form.filter button.btn")

    def load(self):
        return self.open("/admin")

    def filter_by_event(self, title):
        Select(self.visible(self.FILTER_EVENT)).select_by_visible_text(title)
        self.click(self.FILTER_SUBMIT)
        self.wait_url_contains("event=")

    def card_of(self, login):
        """Карточка заявки участника с таким логином (в карточке строка «Участник»)."""
        self.visible(self.CARDS)
        for card in self.driver.find_elements(*self.CARDS):
            if card.find_element(By.XPATH, ".//dt[text()='Участник']/following-sibling::dd[1]").text == login:
                return card
        return None

    def set_status(self, login, status):
        card = self.card_of(login)
        Select(card.find_element(By.CSS_SELECTOR, "select")).select_by_visible_text(status)
        card.find_element(By.CSS_SELECTOR, "button").click()
        self.visible(self.FLASH)
