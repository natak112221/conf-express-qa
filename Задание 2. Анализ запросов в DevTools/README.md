# Задание 2. Анализ запросов и ответов в DevTools

Разобрал вход в систему на двух сайтах: на сайте для тренировки тестировщиков the-internet.herokuapp.com (чужой, работающий в интернете) и на своём портале (localhost:8102). Chrome 156.0.8078.80, вкладка «Сеть», фильтр «Документ», включено «Сохранять журнал» (иначе при переходе после отправки формы запрос исчезает из списка). Данные для входа на чужом сайте написаны на его странице входа (`tomsmith`), на своём портале тестовый участник `ivan_k`. Снимки в папке `screens`, дата 05.11.2026.

## Запрос 1. GET страницы входа на чужом сайте

URL: https://the-internet.herokuapp.com/login. Снимки `01`, `02`.

| Что | Значение |
|---|---|
| Метод и код | GET, 200 OK |
| Адрес сервера | 13.248.162.64:443 (https) |
| Content-Type | text/html; charset=utf-8 |
| Content-Length | 2486 |
| Server, Via | Heroku, 2.0 heroku-router |
| Защитные заголовки | X-Frame-Options: SAMEORIGIN, X-Content-Type-Options: nosniff, X-Xss-Protection: 1; mode=block |
| Set-Cookie | rack.session=...; path=/; httponly |
| Тело запроса | нет (GET) |
| Тело ответа | HTML страницы, заголовок «The Internet», форма с полями username и password (вкладка «Ответ») |

В запросе браузер отправил `Accept: text/html,...`, `User-Agent: Chrome/156...` и заголовки `Sec-Ch-Ua...`.

## Запрос 2. POST входа на чужом сайте

URL: https://the-internet.herokuapp.com/authenticate. Снимки `03`, `04`.

| Что | Значение |
|---|---|
| Метод и код | POST, 303 See Other |
| Location | https://the-internet.herokuapp.com/secure (дальше браузер сам делает GET) |
| Content-Length ответа | 0 (тела нет, ответ только перенаправляет) |
| Set-Cookie | новая rack.session, httponly |
| Тело запроса (вкладка «Полезная нагрузка») | username = tomsmith, password = SuperSecretPassword! |

Следом в списке идёт GET /secure, это страница после входа.

## Запрос 3. GET страницы входа на своём портале

URL: http://localhost:8102/login. Снимок `05`.

Код 304 Not Modified: страницу браузер уже загружал, и сервер ответил, что она не изменилась (проверка по заголовку ETag). Метод GET, Keep-Alive timeout=5. В ответе есть Content-Security-Policy, X-Content-Type-Options: nosniff, X-Frame-Options: SAMEORIGIN, Referrer-Policy: no-referrer, Strict-Transport-Security. Заголовка X-Powered-By нет, версия Express не видна.

## Запрос 4. POST входа на своём портале

URL: http://localhost:8102/login. Снимки `06`, `07`.

| Что | Значение |
|---|---|
| Метод и код | POST, 302 Found |
| Location | /applications |
| Content-Length ответа | 103 (короткая страница с сообщением о переходе) |
| Set-Cookie | sid=s%3A...; Path=/; Expires=(через 2 часа); HttpOnly; SameSite=Lax |
| Тело запроса | поля формы `_csrf` (токен формы), `login` = ivan_k, `password` = Password123 |

## Что полезно для тестирования

1. Вход на обоих сайтах работает по схеме «POST, потом перенаправление, потом GET». В автотесте надо проверять не только код POST, но и адрес в `Location`, и что следующая страница открылась.
2. У моего портала в cookie сессии есть HttpOnly и SameSite=Lax, у чужого сайта только HttpOnly. Флага Secure у портала нет, потому что тестирую по http; на https его включает переменная `COOKIE_SECURE=1`.
3. Пароль в «Полезной нагрузке» виден открытым текстом. Это нормально для формы входа, но значит, что на настоящем сервере нужен только https, а для проверок годятся только тестовые учётные записи.
4. Токен `_csrf` в теле запроса есть только у моего портала. Если отправить такую форму без токена, сервер ответит 403 (это проверяет `check_forms.py`, задание 3).
5. Мой портал не выдаёт название сервера и технологию, чужой сайт выдаёт `Server: Heroku`. Заголовок `X-Powered-By` я убрал при защите портала (практика 4).
