"""Проверка форм регистрации и входа по классам эквивалентности и граничным значениям.
Запуск: python check_forms.py   (портал должен работать, адрес в PORTAL_URL, по умолчанию http://127.0.0.1:8102)
Ожидаемые результаты взяты из требований (практика 1 портала), а не из текущего поведения.
"""
import os
import sys
import re

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from portal_client import Portal, Report, unique, new_user  # noqa: E402

rep = Report("Проверка форм")
OK = "+79001234567"


def reg(case_id, text, expect, **over):
    """Регистрация с одним изменённым полем; expect: 302 (принята) или 422 (отклонена)."""
    p = Portal()
    login = unique("f")
    data = dict(login=login, password="Password123", email=login + "@mail.test", phone=OK)
    data.update(over)
    r = p.register(**data)
    rep.check(case_id, text, r.status_code == expect, f"ожидали {expect}, получили {r.status_code}")
    return p, data, r


# ---------- регистрация: логин ----------
reg("R-01", "все поля верные", 302)
reg("R-02", "логин 2 символа (ниже границы)", 422, login="ab")
reg("R-03", "логин 3 символа (граница)", 302, login=unique("g")[:3] + "_")
reg("R-04", "логин 20 символов (граница)", 302, login=unique("h") + "abcdefgh")
reg("R-05", "логин 21 символ (выше границы)", 422, login="a" * 21)
reg("R-06", "логин кириллицей", 422, login="наталья")
reg("R-07", "логин с пробелом внутри", 422, login="na tali")
reg("R-08", "логин со знаком дефис", 422, login="na-tali")
reg("R-09", "логин пустой", 422, login="")
reg("R-10", "существующий логин ivan_k", 422, login="ivan_k")
reg("R-11", "существующий логин в другом регистре (Ivan_K)", 422, login="Ivan_K")

# ---------- регистрация: пароль ----------
reg("R-12", "пароль 7 символов (ниже границы)", 422, password="Pass123")
reg("R-13", "пароль 8 символов (граница)", 302, password="Pass1234")
reg("R-14", "пароль пустой", 422, password="")
reg("R-15", "пароль из 8 пробелов", 422, password=" " * 8)

# ---------- регистрация: почта ----------
reg("R-16", "почта без @", 422, email="natali.mail.test")
reg("R-17", "почта без домена (a@b)", 422, email="natali@mail")
reg("R-18", "почта с пробелом внутри", 422, email="na tali@mail.test")
reg("R-19", "почта с двумя @", 422, email="a@b@mail.test")
reg("R-20", "почта пустая", 422, email="")
reg("R-21", "почта с точкой и плюсом (допустимая)", 302, email="name.surname+tag@mail.example.ru")
reg("R-22", "почта длиной 300 символов", 422, email="a" * 290 + "@mail.test")

# ---------- регистрация: телефон ----------
reg("R-23", "телефон +7 900 123-45-67", 302, phone="+7 900 123-45-67")
reg("R-24", "телефон 8 (900) 123-45-67", 302, phone="8 (900) 123-45-67")
reg("R-25", "телефон 9 цифр после кода", 422, phone="+790012345")
reg("R-26", "телефон 12 цифр", 422, phone="+790012345678")
reg("R-27", "телефон из букв", 422, phone="abcdefghijk")
reg("R-28", "телефон с буквами после цифр", 422, phone="89001234567abc")
reg("R-29", "телефон не российский (+1)", 422, phone="+1 900 123-45-67")
reg("R-30", "телефон пустой", 422, phone="")
p, data, _ = reg("R-31", "телефон 8... сохраняется в виде +7...", 302, phone="8 900 111-22-33")
html = p.get("/cabinet").text
rep.check("R-31a", "в кабинете телефон показан как +79001112233", "+79001112233" in html)

# ---------- ошибка в форме: введённое не теряется ----------
p = Portal()
r = p.register(login="na", password="x", email="bad", phone="8900abc")
rep.check("R-32", "после ошибки в форме остался введённый телефон", 'value="8900abc"' in r.text)

# ---------- вход ----------
p = Portal()
rep.check("L-01", "верный логин и пароль", p.login("ivan_k", "Password123").status_code == 302)
p = Portal()
r1 = p.login("ivan_k", "неверный")
rep.check("L-02", "неверный пароль", r1.status_code == 401)
p = Portal()
r2 = p.login("net_takogo", "Password123")
rep.check("L-03", "неверный логин", r2.status_code == 401)
rep.check("L-04", "одинаковое сообщение для неверного логина и пароля", re.findall(r'role="alert">([^<]+)', r1.text) == re.findall(r'role="alert">([^<]+)', r2.text))
p = Portal()
rep.check("L-05", "пустые поля", p.login("", "").status_code == 401)
p = Portal()
rep.check("L-06", "пробелы вокруг логина не мешают входу", p.login("  ivan_k  ", "Password123").status_code == 302)
p = Portal()
rep.check("L-07", "SQL-инъекция в логине не пускает", p.login("' OR '1'='1' --", "x").status_code == 401)
p = Portal()
r = p.login("<script>alert(1)</script>", "x")
rep.check("L-08", "скрипт в логине показывается экранированным", "<script>alert(1)</script>" not in r.text and "&lt;script&gt;" in r.text)

# ---------- пароль длиннее 72 байт ----------
# bcrypt учитывает только первые 72 байта: либо длинный пароль отклоняется при регистрации,
# либо вход с другим окончанием не должен проходить
p = Portal()
login = unique("long")
r = p.register(login=login, password="A" * 72 + "first", email=login + "@mail.test", phone=OK)
if r.status_code == 422:
    rep.check("L-09", "пароль длиннее 72 символов отклоняется при регистрации", True, "код 422")
else:
    q = Portal()
    r = q.login(login, "A" * 72 + "other")
    rep.check("L-09", "пароль длиннее 72 символов: с другим окончанием войти нельзя", r.status_code == 401, f"код {r.status_code}")

# ---------- служебные проверки ----------
p = Portal()
r = p.s.post(p.base + "/login", data={"login": "ivan_k", "password": "Password123"}, allow_redirects=False)
rep.check("M-01", "отправка формы без токена отклоняется", r.status_code == 403, f"код {r.status_code}")
p = Portal()
r = p.s.post(p.base + "/login", data={"login": "a" * 200000, "password": "x", "_csrf": "x"}, allow_redirects=False)
rep.check("M-02", "слишком большое тело запроса даёт 413 и страницу ошибки сайта", r.status_code == 413 and "Слишком большой запрос" in r.text, f"код {r.status_code}")
r = Portal().get("/events/%E0%A4%A")
rep.check("M-03", "неверно закодированный адрес даёт 4xx, а не 500", 400 <= r.status_code < 500, f"код {r.status_code}")

sys.exit(1 if rep.finish() else 0)
