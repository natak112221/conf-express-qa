"""Маленький HTTP-клиент для проверок портала: сессия, токен формы, вход, регистрация."""
import os
import re
import time
import uuid

import requests

BASE = os.environ.get("PORTAL_URL", "http://127.0.0.1:8102")


class Portal:
    def __init__(self, base=BASE):
        self.base = base.rstrip("/")
        self.s = requests.Session()

    def get(self, path, **kw):
        return self.s.get(self.base + path, allow_redirects=False, timeout=15, **kw)

    def token(self, page):
        html = self.get(page).text
        m = re.search(r'name="_csrf" value="([^"]+)"', html)
        return m.group(1) if m else ""

    def post(self, path, data, page=None):
        """Отправляет форму с токеном, который берёт со страницы page (по умолчанию со страницы path)."""
        data = dict(data)
        data["_csrf"] = self.token(page or path)
        return self.s.post(self.base + path, data=data, allow_redirects=False, timeout=15)

    def login(self, login, password):
        return self.post("/login", {"login": login, "password": password})

    def register(self, **fields):
        return self.post("/register", fields)

    def logout(self):
        self.post("/logout", {}, page="/")


def unique(prefix="qa"):
    """Короткое уникальное имя для логина (до 20 символов)."""
    return (prefix + uuid.uuid4().hex)[:12]


def new_user(prefix="qa", password="Password123"):
    """Регистрирует нового участника, возвращает вошедший клиент и логин."""
    p = Portal()
    login = unique(prefix)
    r = p.register(login=login, password=password, email=login + "@mail.test", phone="+79001234567")
    assert r.status_code == 302, f"не удалось зарегистрировать {login}: {r.status_code}"
    return p, login


def admin():
    p = Portal()
    r = p.login("admin", "Admin2026")
    assert r.status_code == 302, "вход администратора не удался"
    return p


class Report:
    """Печатает результаты проверок в виде таблицы и считает итог."""

    def __init__(self, title):
        self.title = title
        self.rows = []

    def check(self, case_id, text, ok, detail=""):
        self.rows.append((case_id, ok))
        print(("OK   " if ok else "НЕТ  ") + f"{case_id:6} {text}" + (f"  [{detail}]" if detail else ""))

    def finish(self):
        bad = [c for c, ok in self.rows if not ok]
        print(f"\n{self.title}: проверок {len(self.rows)}, не прошло {len(bad)}" + (": " + ", ".join(bad) if bad else ""))
        return len(bad)
