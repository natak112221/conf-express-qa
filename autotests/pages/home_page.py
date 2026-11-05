from selenium.webdriver.common.by import By

from .base_page import BasePage


class HomePage(BasePage):
    UPCOMING_CARDS = (By.CSS_SELECTOR, "#afisha .event-card")
    HERO_TITLE = (By.CSS_SELECTOR, ".hero h1")

    def load(self):
        return self.open("/")

    def title_text(self):
        return self.text_of(self.HERO_TITLE)

    def upcoming_titles(self):
        self.visible(self.UPCOMING_CARDS)
        return [c.find_element(By.TAG_NAME, "h3").text for c in self.driver.find_elements(*self.UPCOMING_CARDS)]

    def open_first_event(self):
        self.visible(self.UPCOMING_CARDS)
        card = self.driver.find_elements(*self.UPCOMING_CARDS)[0]
        title = card.find_element(By.TAG_NAME, "h3").text
        card.click()
        self.wait_url_contains("/events/")
        return title
