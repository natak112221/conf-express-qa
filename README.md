# conf-express-qa

Тестирование учебного портала «Конференции.РФ» (МДК.05.03). Сам портал в репозитории [conf-express](https://github.com/natak112221/conf-express). Работа выполнена в ноябре 2026: задания 1-3, дополнительные 4 и 5. Отчёт: `Отчет МДК.05.03.docx`.

[![smoke](https://github.com/natak112221/conf-express-qa/actions/workflows/smoke.yml/badge.svg)](https://github.com/natak112221/conf-express-qa/actions/workflows/smoke.yml)

## Папки

| Папка | Что внутри |
|---|---|
| `Задание 1. Чек-лист, тест-кейсы, баг-репорты` | чек-лист из 20 пунктов, 5 тест-кейсов, 9 баг-репортов, скрипт `check_flows.py` (20 проверок), снимки |
| `Задание 2. Анализ запросов в DevTools` | разбор GET и POST входа на чужом сайте и на своём портале, снимки DevTools |
| `Задание 3. Тестирование форм` | `check_forms.py` (45 проверок по классам эквивалентности и границам), таблицы результатов |
| `Задание 4. Автотест входа (Selenium)` | описание, снимки; код в `autotests` |
| `Задание 5. Смоук-тесты и CI` | 5 смоук-тестов, описание CI и первого прогона, снимки |
| `.github/workflows` | `smoke.yml`: запуск смоук-тестов в GitHub Actions |
| `autotests` | Selenium и pytest: `pages` (Page Object), `tests` (вход, смоук, тесты на найденные ошибки), `conftest.py` |
| `tools` | клиент для проверок запросами |

## Результат

Найдено 9 реальных дефектов портала, все исправлены в портале. До исправлений `check_forms.py` не прошло 5 проверок из 45, `check_flows.py` 6 из 20, три автотеста на ошибки падали. После исправлений: 45 из 45, 20 из 20, 15 автотестов Selenium из 15 (7 входа, 5 смоук, 3 на ошибки).

## Как запустить

1. Запустить портал (`conf-express/portal`: `npm install`, `npm run setup`, `npm start`), он слушает порт 8102.
2. Проверки запросами: `python "Задание 3. Тестирование форм/check_forms.py"` и `python "Задание 1. Чек-лист, тест-кейсы, баг-репорты/check_flows.py"` (нужен `pip install requests`).
3. Автотесты: `cd autotests`, `pip install -r requirements.txt`, `python -m pytest -v` (нужен Chrome).

Адрес портала меняется переменной `PORTAL_URL`, окно браузера включается `HEADLESS=0`.

## CI

На каждый push смоук-тесты запускаются в GitHub Actions (`.github/workflows/smoke.yml`): [прогон #1](https://github.com/natak112221/conf-express-qa/actions/runs/42128422172), 5 тестов из 5. Подробности в задании 5.

## Где проверено

Chrome 156 (Selenium 4.51) на Windows 11 и Chrome на `ubuntu-latest` в GitHub Actions; Edge 156 использовала только в практике 10 портала, телефон в эмуляции Chrome. Firefox и Safari не запускала.
