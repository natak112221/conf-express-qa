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

Результат: `screens/01-смоук-тесты.png`, 5 из 5 прошли (26 секунд).

Время фиксируется переменной `PORTAL_NOW`: мероприятия в тестовых данных назначены на ноябрь 2026, январь 2027, и после этих дат «ближайших» уже не будет. Для запуска с зафиксированной датой: `PORTAL_NOW="2026-11-05 12:00"` перед `npm start`.

## CI: GitHub Actions

Файл `smoke.yml` (должен лежать в `.github/workflows/`) делает на каждый push и pull request: скачивает портал из репозитория `conf-express`, ставит Node 22 и зависимости, готовит базу, запускает портал, ставит Python и Selenium (Chrome в образе `ubuntu-latest` уже есть), запускает смоук-тесты и сохраняет отчёт `report.html`, скриншоты падений и журнал портала как артефакт.

```yaml
name: smoke
on: [push, pull_request]

jobs:
  smoke:
    runs-on: ubuntu-latest
    env:
      CI: "1"
      PORTAL_NOW: "2026-11-05 12:00"
      PORTAL_URL: http://127.0.0.1:8102
    steps:
      - uses: actions/checkout@v4
      - uses: actions/checkout@v4
        with:
          repository: natak112221/conf-express
          path: conf-express
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
          cache-dependency-path: conf-express/portal/package-lock.json
      - name: Установка портала и данных
        working-directory: conf-express/portal
        run: |
          npm ci
          npm run setup
      - name: Запуск портала
        working-directory: conf-express/portal
        run: |
          nohup node src/server.js > ../../portal.log 2>&1 &
          for i in $(seq 1 30); do curl -sf http://127.0.0.1:8102/ > /dev/null && break; sleep 1; done
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r autotests/requirements.txt
      - name: Смоук-тесты
        working-directory: autotests
        run: python -m pytest -m smoke -v --html=report.html --self-contained-html
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: smoke-report
          path: |
            autotests/report.html
            autotests/failures
            portal.log
```

### Что проверено и что нет

- Те же команды (запуск портала с `PORTAL_NOW`, `pytest -m smoke` с `--html`, переменная `CI=1`) выполнила на своём компьютере: смоук и тесты на ошибки, 8 из 8 прошли, отчёт создался.
- **Сам запуск в GitHub Actions не проверялся.** Токен, которым я выкладывала репозитории, не имеет права `workflow`, а GitHub не принимает файлы из `.github/workflows` без него. Попытку отправить файл сделала один раз, её отклонили (см. корневой README). Поэтому файл `smoke.yml` лежит в отдельной ветке `ci` только у меня, а в этом репозитории он приведён выше. Чтобы включить CI: добавить файл `.github/workflows/smoke.yml` через веб-интерфейс GitHub (Add file, Create new file) или отправить его токеном с правом `workflow`.
- Не знаю заранее, как поведёт себя установка `better-sqlite3` на `ubuntu-latest` (для Node 22 на Linux есть готовая сборка, но я это не проверяла), и нужен ли Chrome-аргумент `--no-sandbox` (он добавлен при `CI=1`).
