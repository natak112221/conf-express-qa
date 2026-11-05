"""Задание 4. Автотесты формы входа: Page Object, явные ожидания, скриншот при падении (conftest.py)."""
import uuid

import pytest
import requests

from pages.base_page import BasePage
from pages.login_page import LoginPage

PASSWORD = "Password123"


@pytest.fixture
def user(base_url):
    """Новый участник: регистрируем запросом, чтобы тесты входа не зависели друг от друга."""
    login = "u" + uuid.uuid4().hex[:11]
    s = requests.Session()
    page = s.get(base_url + "/register").text
    token = page.split('name="_csrf" value="')[1].split('"')[0]
    r = s.post(base_url + "/register", allow_redirects=False,
               data={"login": login, "password": PASSWORD, "email": login + "@mail.test", "phone": "+79001234567", "_csrf": token})
    assert r.status_code == 302
    return login


def test_successful_login_opens_my_applications(driver, base_url, user):
    page = LoginPage(driver, base_url).load()
    page.sign_in(user, PASSWORD)
    page.wait_url_path("/applications")
    assert user in page.header_user()


def test_wrong_password_shows_error(driver, base_url, user):
    page = LoginPage(driver, base_url).load()
    page.sign_in(user, "Неверный1")
    assert page.error_text() == "Неверный логин или пароль"
    assert driver.execute_script("return location.pathname") == "/login"


def test_unknown_login_shows_same_error(driver, base_url):
    """Сообщение не должно выдавать, что такого логина нет."""
    page = LoginPage(driver, base_url).load()
    page.sign_in("net_takogo_" + uuid.uuid4().hex[:4], PASSWORD)
    assert page.error_text() == "Неверный логин или пароль"


def test_empty_fields_are_stopped_by_browser(driver, base_url):
    page = LoginPage(driver, base_url).load()
    page.click(page.SUBMIT)
    assert page.validation_message(page.LOGIN) != ""
    assert driver.execute_script("return location.pathname") == "/login"


def test_logout_shows_guest_header(driver, base_url, user):
    page = LoginPage(driver, base_url).load()
    page.sign_in(user, PASSWORD)
    page.wait_url_path("/applications")
    page.logout()
    assert not page.is_present(BasePage.CABINET_LINK)
    assert page.is_present(("link text", "Вход"))


def test_guest_is_redirected_from_private_page(driver, base_url):
    page = LoginPage(driver, base_url).open("/applications")
    page.wait_url_path("/login")
    assert "Сначала войдите" in page.flash_text()


def test_password_can_be_shown_and_hidden(driver, base_url):
    page = LoginPage(driver, base_url).load()
    assert page.password_type() == "password"
    page.toggle_password()
    assert page.password_type() == "text"
    page.toggle_password()
    assert page.password_type() == "password"


@pytest.mark.demo_fail
def test_demo_failure_makes_screenshot(driver, base_url):
    """Падает специально (ждёт неверный текст): так получаем скриншот при падении. В обычный запуск не входит."""
    page = LoginPage(driver, base_url).load()
    page.sign_in("ivan_k", "неверный")
    assert page.error_text() == "Пароль не подошёл"
