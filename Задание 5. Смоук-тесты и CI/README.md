# Задание 5. Смоук-автотесты своего приложения и запуск в CI

Тестирую свой портал «Конференции.РФ» (репозиторий `conf-express`). Смоук-тесты проверяют главное: сайт открывается, можно зарегистрироваться, подать заявку, администратор видит заявку и меняет статус, закрытые страницы закрыты. Код: `autotests/tests/test_smoke.py`, страницы `autotests/pages` (те же, что в задании 4).

## Пять смоук-тестов

| Тест | Что проверяет |
|---|---|
| `test_home_page_shows_upcoming_events` | главная открывается, заголовок на месте, мероприятий не меньше трёх |
| `test_new_participant_can_register` | регистрация нового участника: сообщение «Вы зарегистрированы», логин в шапке |
| `test_participant_can_apply_to_event` | участник открывает первое мероприятие, подаёт заявку, видит её в «Моих заявках» со статусом «новая» |
| `test_admin_can_assign_application` | администратор находит заявку по логину через фильтр, ставит «назначено», участник видит новый статус |
| `test_guest_cannot_open_admin_panel` | гость на `/admin` попадает на `/login` |

Тесты изолированы: каждому нужен свой участник с уникальным логином, тесты можно запускать повторно без сброса базы. Тестовые данные (администратор и мероприятия) создаёт `npm run setup` в портале.

## Как запустить

```
cd conf-express/portal
npm install
npm run setup
npm start
```

В другом окне:

```
cd conf-express-qa/autotests
pip install -r requirements.txt
python -m pytest -m smoke -v
```

Результат на своём компьютере: `screens/01-смоук-тесты.png`, 5 из 5 прошли.

Время фиксируется переменной `PORTAL_NOW`: мероприятия в тестовых данных назначены на ноябрь 2026, январь 2027, и после этих дат «ближайших» уже не будет. Для запуска с зафиксированной датой: `PORTAL_NOW="2026-11-05 12:00"` перед `npm start`.

## CI: GitHub Actions

Файл `.github/workflows/smoke.yml` запускается на каждый push и pull request. Задача на `ubuntu-latest` делает по шагам: берёт этот репозиторий и репозиторий портала `conf-express`, ставит Node 22 и зависимости (`npm ci`), готовит базу (`npm run setup`), запускает портал на порту 8102, ставит Python и Selenium, запускает `pytest -m smoke` и сохраняет `report.html`, снимки падений и журнал портала как артефакт `smoke-report`. Chrome в образе `ubuntu-latest` уже есть, при `CI=1` тесты добавляют ключи `--no-sandbox` и `--disable-dev-shm-usage`. Дата для портала задана переменной `PORTAL_NOW`, чтобы мероприятия оставались «ближайшими».

Прогоны:

| Прогон | Коммит | Результат |
|---|---|---|
| [#1](https://github.com/natak112221/conf-express-qa/actions/runs/42128422172) | `78eac10` | Success, 36 с, 5 тестов из 5 (`5 passed, 11 deselected in 11.30s`) |
| [#2](https://github.com/natak112221/conf-express-qa/actions/runs/42128927484) | `a2b1adc` | Failure: упал `test_admin_can_assign_application` |
| [#3](https://github.com/natak112221/conf-express-qa/actions/runs/42129108948) | `0d55127` | Success, 5 из 5; повторный запуск этого же прогона ещё дважды, оба Success |

В прогоне #2 тест упал в `logout()`: `invisibility_of_element_located` обратился к ссылке в шапке в момент перехода страницы, и Chrome ответил ошибкой `Node with given id does not belong to the document`. Локально тест проходил, потому что там быстрее. Заменила ожидание на `not driver.find_elements(...)`, которое при переходе не падает (`autotests/pages/base_page.py`). Снимки первого прогона: `screens/02-github-actions-прогон.png`, `screens/03-github-actions-шаги.png`.

Для проверки отдельных шагов на своём компьютере запускала те же команды (портал с `PORTAL_NOW`, `pytest -m smoke --html=report.html`): 5 из 5.
