import os
import re
import uuid

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_URL = os.environ.get("PORTAL_URL", "http://127.0.0.1:8102")
FAILURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "failures")


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture
def driver():
    """Chrome. По умолчанию без окна; HEADLESS=0 открывает обычное окно."""
    o = Options()
    if os.environ.get("HEADLESS", "1") != "0":
        o.add_argument("--headless=new")
    o.add_argument("--window-size=1280,900")
    o.add_argument("--lang=ru")
    if os.environ.get("CI"):
        o.add_argument("--no-sandbox")
        o.add_argument("--disable-dev-shm-usage")
    d = webdriver.Chrome(options=o)
    yield d
    d.quit()


@pytest.fixture
def new_login():
    """Уникальный логин для регистрации (до 20 символов)."""
    return "t" + uuid.uuid4().hex[:11]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Если тест упал, сохраняем скриншот окна браузера в папку failures."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        drv = item.funcargs.get("driver")
        if drv is not None:
            os.makedirs(FAILURES, exist_ok=True)
            name = re.sub(r"[^\w-]+", "_", item.name)
            path = os.path.join(FAILURES, name + ".png")
            drv.save_screenshot(path)
            rep.sections.append(("Скриншот при падении", path))
