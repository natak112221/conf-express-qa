"""Задание 5. Смоук-тесты портала: открытие, регистрация, заявка, панель администратора, закрытый доступ."""
import uuid

import pytest

from pages.application_pages import AdminPage, ApplicationFormPage, EventPage, MyApplicationsPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage

pytestmark = pytest.mark.smoke
PASSWORD = "Password123"


def register(driver, base_url):
    login = "s" + uuid.uuid4().hex[:11]
    page = RegisterPage(driver, base_url).load()
    page.register(login, PASSWORD)
    page.wait_url_path("/")
    return login


def test_home_page_shows_upcoming_events(driver, base_url):
    home = HomePage(driver, base_url).load()
    assert "Встречи для разработчиков" in home.title_text()
    assert len(home.upcoming_titles()) >= 3


def test_new_participant_can_register(driver, base_url):
    login = register(driver, base_url)
    page = HomePage(driver, base_url)
    assert "Вы зарегистрированы" in page.flash_text()
    assert login in page.header_user()


def test_participant_can_apply_to_event(driver, base_url):
    register(driver, base_url)
    title = HomePage(driver, base_url).load().open_first_event()
    EventPage(driver, base_url).apply()
    ApplicationFormPage(driver, base_url).fill_and_send(room="Малый зал", payment="Картой онлайн")
    assert (title, "новая") in MyApplicationsPage(driver, base_url).cards()


def test_admin_can_assign_application(driver, base_url):
    # участник подаёт заявку
    login = register(driver, base_url)
    title = HomePage(driver, base_url).load().open_first_event()
    EventPage(driver, base_url).apply()
    ApplicationFormPage(driver, base_url).fill_and_send()
    MyApplicationsPage(driver, base_url).logout()
    # администратор находит её и меняет статус
    LoginPage(driver, base_url).load().sign_in("admin", "Admin2026")
    admin = AdminPage(driver, base_url)
    admin.wait_url_path("/admin")
    admin.filter_by_event(title)
    admin.set_status(login, "назначено")
    assert "назначено" in admin.flash_text()
    admin.logout()
    # участник видит новый статус
    LoginPage(driver, base_url).load().sign_in(login, PASSWORD)
    assert (title, "назначено") in MyApplicationsPage(driver, base_url).cards()


def test_guest_cannot_open_admin_panel(driver, base_url):
    page = LoginPage(driver, base_url).open("/admin")
    page.wait_url_path("/login")
