from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

TIMEOUT = 10


class BasePage:
    """Общие действия: все ожидания явные (WebDriverWait), time.sleep нигде не используется."""

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, TIMEOUT)

    def open(self, path="/"):
        self.driver.get(self.base_url + path)
        return self

    def visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def click(self, locator):
        self.clickable(locator).click()

    def type(self, locator, text):
        el = self.visible(locator)
        el.clear()
        el.send_keys(text)

    def text_of(self, locator):
        return self.visible(locator).text

    def is_present(self, locator):
        return bool(self.driver.find_elements(*locator))

    def wait_url_contains(self, part):
        self.wait.until(EC.url_contains(part))

    def wait_url_path(self, path):
        self.wait.until(lambda d: d.execute_script("return location.pathname") == path)

    # шапка сайта
    FLASH = (By.CSS_SELECTOR, ".flash")
    CABINET_LINK = (By.CSS_SELECTOR, "a[href='/cabinet']")
    LOGOUT_BUTTON = (By.CSS_SELECTOR, ".nav form button")

    def flash_text(self):
        return self.text_of(self.FLASH)

    def header_user(self):
        return self.text_of(self.CABINET_LINK)

    def logout(self):
        self.click(self.LOGOUT_BUTTON)
        self.wait.until(EC.invisibility_of_element_located(self.CABINET_LINK))
