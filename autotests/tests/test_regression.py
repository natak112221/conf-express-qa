"""Тесты на найденные ошибки (BR-01, BR-02, BR-06). На версии портала до исправлений они падают, после исправлений проходят."""
import uuid

import pytest

from pages.application_pages import ApplicationFormPage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage

pytestmark = pytest.mark.regression


def test_br01_login_in_other_case_is_already_taken(driver, base_url):
    page = RegisterPage(driver, base_url).load()
    page.register("Ivan_K")  # в тестовых данных есть ivan_k
    assert any("уже занят" in t for t in page.error_texts())


def test_br02_password_of_spaces_is_rejected(driver, base_url):
    page = RegisterPage(driver, base_url).load()
    page.register("r" + uuid.uuid4().hex[:11], password=" " * 8)
    assert any("пробел" in t for t in page.error_texts())


def test_br06_cannot_apply_to_past_event(driver, base_url):
    login = "r" + uuid.uuid4().hex[:11]
    RegisterPage(driver, base_url).load().register(login)
    page = ApplicationFormPage(driver, base_url).open("/applications/new?event=1")  # мероприятие 1 уже прошло
    assert "Мероприятие уже прошло" in page.text_of(("css selector", ".error-page"))
