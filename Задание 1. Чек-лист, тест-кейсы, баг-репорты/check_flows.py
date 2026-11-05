"""Проверка сценариев с заявками, статусами и отзывами (запросами к работающему порталу).
Запуск: python check_flows.py   (адрес в PORTAL_URL, по умолчанию http://127.0.0.1:8102)
Ожидаемые результаты взяты из требований (практики 1 и 6 портала).
Используются мероприятия из тестовых данных: 1-3 прошли, 4-8 впереди.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from portal_client import Portal, Report, new_user, admin  # noqa: E402

rep = Report("Проверка сценариев")
PAST, FUTURE = 1, 6


def apply(p, event, room="Малый зал", payment="Картой онлайн"):
    return p.post("/applications", {"event_id": event, "room": room, "payment": payment}, page=f"/applications/new?event={event}")


def app_id(adm, login, event):
    """Номер заявки участника на мероприятие: ищем карточку в панели администратора."""
    html = adm.get(f"/admin?event={event}").text
    for card in html.split("<article")[1:]:
        if f"<dd>{login}</dd>" in card:
            return int(re.search(r"/admin/applications/(\d+)/status", card).group(1))
    return None


def set_status(adm, aid, status):
    return adm.post(f"/admin/applications/{aid}/status", {"status": status, "back": "/admin"}, page="/admin")


def review(p, aid, rating="5", text="Хорошая встреча, всё понятно"):
    return p.post(f"/applications/{aid}/review", {"rating": rating, "text": text}, page="/applications")


adm = admin()

# ---------- заявки ----------
u, login = new_user("flow")
r = apply(u, FUTURE)
rep.check("F-01", "заявка на будущее мероприятие принимается", r.status_code == 302, f"код {r.status_code}")
rep.check("F-02", "вторая заявка на то же мероприятие отклоняется", apply(u, FUTURE).status_code == 422)
rep.check("F-03", "помещение не из списка отклоняется", apply(u, 7, room="Подвал").status_code == 422)
rep.check("F-04", "способ оплаты не из списка отклоняется", apply(u, 7, payment="Биткоины").status_code == 422)
r = apply(u, PAST)
rep.check("F-05", "заявка на прошедшее мероприятие отклоняется", r.status_code == 422, f"код {r.status_code}")

# ---------- статусы ----------
aid = app_id(adm, login, FUTURE)
rep.check("F-06", "новая заявка видна администратору", aid is not None)
rep.check("F-07", "статус новая -> назначено меняется", set_status(adm, aid, "назначено").status_code == 302)
r = set_status(adm, aid, "завершено")
rep.check("F-08", "заявку на будущее мероприятие завершить нельзя", r.status_code in (400, 403, 422), f"код {r.status_code}")
html = u.get("/applications").text
rep.check("F-09", "участник видит статус заявки", "назначено" in html or "завершено" in html)

# заявка на прошедшее мероприятие через базу тестовых данных: берём мероприятие 2 как завершённое
u2, login2 = new_user("flow")
apply(u2, 7)
aid2 = app_id(adm, login2, 7)
set_status(adm, aid2, "назначено")
r = set_status(adm, aid2, "новая")
rep.check("F-10", "вернуть назначенную заявку в статус новая нельзя", r.status_code in (400, 403, 422), f"код {r.status_code}")
r = set_status(adm, aid2, "выдуманный")
rep.check("F-11", "неизвестный статус отклоняется", r.status_code == 400, f"код {r.status_code}")

# ---------- отзывы ----------
rep.check("F-12", "отзыв до завершения заявки запрещён", review(u, aid).status_code == 403)
ivan = Portal()
ivan.login("ivan_k", "Password123")
ivan_app = app_id(adm, "ivan_k", 1)
r = review(ivan, ivan_app, rating="6")
rep.check("F-13", "оценка 6 отклоняется", r.status_code == 422, f"код {r.status_code}")
rep.check("F-14", "чужую заявку оценить нельзя", review(u, ivan_app).status_code == 404)
maria = Portal()
maria.login("maria_s", "Password123")
rep.check("F-15", "второй отзыв на ту же заявку запрещён", review(maria, app_id(adm, "maria_s", 2)).status_code == 403)

# ---------- права и кеш ----------
rep.check("F-16", "участник не открывает панель администратора", u.get("/admin").status_code == 403)
g = Portal()
r = g.get("/applications")
rep.check("F-17", "гость с «Моих заявок» уходит на вход", r.status_code == 302 and r.headers.get("Location") == "/login")
for n, (path, who) in enumerate((("/applications", u), ("/cabinet", u), ("/admin", adm))):
    cc = who.get(path).headers.get("Cache-Control", "")
    rep.check("F-18" + "abc"[n], f"личная страница {path} не кешируется (Cache-Control: no-store)", "no-store" in cc, f"заголовок: {cc or 'нет'}")

sys.exit(1 if rep.finish() else 0)
