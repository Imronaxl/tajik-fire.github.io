# tajik-fire

<p align="center">
  <strong>Платформа соревновательного программирования с песочницей-судьёй, учебными треками и социальной лентой.</strong>
</p>

<p align="center">
  <a href="https://github.com/Imronaxl/tajik-fire.github.io/actions"><img src="https://github.com/Imronaxl/tajik-fire.github.io/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/fastapi-0.128-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/svelte-4-FF3E00?logo=svelte&logoColor=white" alt="Svelte">
  <img src="https://img.shields.io/badge/sqlalchemy-2.0-red?logo=sqlalchemy&logoColor=white" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/judger-python%20%7C%20C%2B%2B%20%7C%20java-8A2BE2" alt="Judger">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

<p align="center">
  <a href="#возможности">Возможности</a> ·
  <a href="#скриншоты">Скриншоты</a> ·
  <a href="#быстрый-старт">Старт</a> ·
  <a href="#архитектура">Архитектура</a> ·
  <a href="#api">API</a> ·
  <a href="#ci">CI</a> ·
  <a href="#roadmap">Roadmap</a>
</p>

---

**tajik-fire** — single-repo платформа для соревновательного программирования
в духе Codeforces с трекером учёбы. Бэкенд на FastAPI проверяет решения на
Python, C++ и Java в изолированном подпроцессе, фронтенд на Svelte 4
собирается в один бандл ~126 КБ (39 КБ gzip) и работает без virtual DOM.

В архиве — задачи трёх уровней сложности с переводом условий на EN/RU/TJ,
учебные треки, социальный слой (друзья, личные и групповые чаты), канбан
для личных задач, лента сабмитов в реальном времени и глобальный рейтинг.

---

## Возможности

- **Песочница-судья** — каждое решение запускается в изолированном процессе
  с `RLIMIT_AS` и wall-clock таймаутом, сравнивается с sample и hidden тестами.
  Поддерживаются Python 3, C++ 17 и Java 11.
- **JWT-аутентификация** — короткий access-токен (30 мин), refresh-токен на
  7 дней, троттлинг попыток входа, bcrypt-хеширование паролей.
- **Email опционален** — без SMTP коды подтверждения возвращаются в ответе
  API, так что можно регистрироваться локально без почтового ящика.
- **i18n условий** — у каждой задачи три перевода (EN / RU / TJ). Эндпоинт
  `/problems/{id}?lang=…` отдаёт нужную локаль.
- **Лента сабмитов** — каждый вердикт пишется в отдельную таблицу и
  отображается на дашборде, главной странице и в разделе «Сабмиты».
- **Система рейтинга** — первое решение задачи даёт очки: easy +5, medium +12,
  hard +25. Топ-3 разработчиков попадают на подиум лидерборда.
- **Без шага сборки на frontend dev** — Svelte компилируется в один бандл,
  раздаётся статикой из FastAPI. Vite dev-сервер проксирует `/api` на бэкенд.
- **CI из коробки** — GitHub Actions: ruff + smoke + проверка судьи на Python
  и C++ + сборка фронтенда + сборка Docker-образа.

---

## Скриншоты

Все скриншоты сделаны с реального запущенного приложения через Playwright
(разрешение 1440×900, retina). Файлы лежат в [`docs/screenshots/`](./docs/screenshots/).

<table>
  <tr>
    <td width="50%" align="center"><b>Главная</b></td>
    <td width="50%" align="center"><b>Архив задач</b></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/01-home.png" alt="Главная страница с живой статистикой и превью кода" title="Главная"></td>
    <td><img src="docs/screenshots/03-problems.png" alt="Архив задач с фильтрами сложности и категорий" title="Архив задач"></td>
  </tr>
  <tr>
    <td align="center"><sub>Hero со счётчиками, табы кода и CTA</sub></td>
    <td align="center"><sub>Фильтр по сложности, категориям, поиск, сортировка</sub></td>
  </tr>
  <tr>
    <td width="50%" align="center"><b>Редактор кода + вердикт</b></td>
    <td width="50%" align="center"><b>Рейтинг</b></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/05-editor.png" alt="Разделённый редактор: условие слева, код справа" title="Редактор"></td>
    <td><img src="docs/screenshots/08-leaderboard.png" alt="Лидерборд с подиумом топ-3 и ранжированным списком" title="Рейтинг"></td>
  </tr>
  <tr>
    <td align="center"><sub>Python / C++ / Java, вердикт приходит за &lt;1 сек</sub></td>
    <td align="center"><sub>Подиум топ-3 + список с рейтингом и числом решённых</sub></td>
  </tr>
  <tr>
    <td width="50%" align="center"><b>Лента сабмитов</b></td>
    <td width="50%" align="center"><b>Учебные треки</b></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/09-submissions.png" alt="Глобальная лента сабмитов с фильтрами вердикта" title="Лента сабмитов"></td>
    <td><img src="docs/screenshots/10-learning.png" alt="Карточки учебных модулей" title="Учебные треки"></td>
  </tr>
  <tr>
    <td align="center"><sub>Лента всех вердиктов на платформе в реальном времени</sub></td>
    <td align="center"><sub>Каждый модуль связывает теорию с graded-задачами</sub></td>
  </tr>
  <tr>
    <td width="50%" align="center"><b>Канбан задач</b></td>
    <td width="50%" align="center"><b>Мессенджер</b></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/12-tasks.png" alt="Канбан с колонками to-do, in-progress, done" title="Задачи"></td>
    <td><img src="docs/screenshots/13-messenger.png" alt="Мессенджер: список чатов и переписка" title="Мессенджер"></td>
  </tr>
  <tr>
    <td align="center"><sub>Персональный трекер с цветовой маркировкой приоритетов</sub></td>
    <td align="center"><sub>Личные и групповые чаты с пузырями сообщений</sub></td>
  </tr>
  <tr>
    <td width="50%" align="center"><b>Профиль</b></td>
    <td width="50%" align="center"><b>Swagger API</b></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/14-profile.png" alt="Профиль со статистикой и недавними сабмитами" title="Профиль"></td>
    <td><img src="docs/screenshots/17-swagger-docs.png" alt="Swagger UI со всеми эндпоинтами" title="Swagger"></td>
  </tr>
  <tr>
    <td align="center"><sub>Статистика, последние сабмиты, смена пароля</sub></td>
    <td align="center"><sub>Все эндпоинты задокументированы и тестируются в браузере</sub></td>
  </tr>
</table>

> Полный список слотов скриншотов — в
> [`docs/screenshots/README.md`](./docs/screenshots/README.md).

---

## Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                            Браузер                              │
│            Svelte 4 · CSS variables · History API              │
└───────────────┬──────────────────────────────────┬──────────────┘
                │  HTTP / JSON                    │  SPA навигация
                ▼                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                          FastAPI app                            │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌─────────┐  ┌─────┐ │
│  │  auth   │  │ problems │  │ contests│  │ friends │  │ ... │ │
│  └────┬────┘  └────┬─────┘  └────┬────┘  └────┬────┘  └─────┘ │
│       │            │             │            │                │
│       ▼            ▼             ▼            ▼                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              SQLAlchemy 2.0  ·  async session            │  │
│  └────────────────────────────┬─────────────────────────────┘  │
│                               │                                │
│       ┌───────────────────────┴───────────────────────┐        │
│       ▼                                               ▼        │
│  ┌─────────────┐                              ┌──────────────┐ │
│  │  SQLite /  │                              │   Судья      │ │
│  │ PostgreSQL │                              │ (subprocess) │ │
│  └─────────────┘                              └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

Судья запускается как `asyncio`-фоновая задача на каждый сабмит, открывает
новую сессию БД, выполняет код пользователя через `subprocess.run` с лимитом
памяти и wall-clock таймаутом, пишет вердикт в `submissions` и добавляет
запись в `submission_feed`. Фронтенд опрашивает эндпоинт сабмита, пока
вердикт не сменится с `pending` / `judging`.

---

## Технологии

| Слой         | Технология                                                       |
|--------------|------------------------------------------------------------------|
| Бэкенд       | FastAPI 0.128, Starlette middleware, Pydantic 2                  |
| База данных  | SQLAlchemy 2.0 async, SQLite (по умолчанию) или PostgreSQL        |
| Аутентификация | JWT через `python-jose`, bcrypt через `passlib`                  |
| Судья        | `subprocess` с `RLIMIT_AS` + wall-clock (по умолчанию), опционально Docker |
| Фронтенд     | Svelte 4 + Vite 5, собственная дизайн-система на CSS variables  |
| Шаблонизация | Svelte SSR/CSR (одна точка входа `index.html`)                   |
| Email        | `smtplib` SSL (опционально, gracefully degrades)                |
| Markdown     | библиотека `markdown` для теории в учебных модулях              |
| CI           | GitHub Actions: ruff + smoke + judge + Docker build             |

---

## Быстрый старт

### Вариант A — локальная разработка (рекомендуется)

```bash
git clone https://github.com/Imronaxl/tajik-fire.github.io.git
cd tajik-fire.github.io

# 1. Бэкенд
cd fastapi_app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# 2. Фронтенд (собрать один раз)
cd ../frontend
npm install
npm run build

# 3. Запустить бэкенд (он раздаёт собранный фронтенд)
cd ../fastapi_app
uvicorn main:app --reload
```

Открыть <http://localhost:8000>. На первом старте seeded демо-датасет:

| Логин  | Пароль     | Описание                                |
|--------|------------|-----------------------------------------|
| `demo` | `Demo1234` | Демо-аккаунт с рейтингом и прогрессом   |

> SMTP выключен по умолчанию. Коды подтверждения и сброса пароля возвращаются
> в API-ответе, так что можно проходить флоу без почтового ящика. Включите
> `SMTP_USER` / `SMTP_PASSWORD` в `.env`, чтобы отправлять реальные письма.

### Dev-режим фронтенда (с HMR)

```bash
# Терминал 1: бэкенд
cd fastapi_app && uvicorn main:app --reload

# Терминал 2: Vite dev server
cd frontend && npm run dev
```

Vite проксирует `/api` на `http://127.0.0.1:8000`. Откройте <http://localhost:5173>.

### Вариант B — Docker

```bash
docker compose up --build
```

В контейнере установлены Python 3.12, GCC 12 и OpenJDK 11, чтобы судья
мог компилировать C++ и Java из коробки.

---

## Структура проекта

```
.
├── .github/workflows/ci.yml       # CI: ruff + smoke + judge + Docker
├── docs/screenshots/              # Скриншоты UI + гайд по съёмке
├── frontend/                      # Svelte 4 + Vite 5
│   ├── src/
│   │   ├── app.css                # Глобальные токены дизайн-системы
│   │   ├── main.js                # Точка входа Svelte
│   │   ├── App.svelte             # Корневой компонент + History-роутер
│   │   ├── lib/
│   │   │   ├── api.js             # fetch-обёртка с авто-рефрешем токена
│   │   │   ├── auth.js            # Svelte store: user, login, logout
│   │   │   ├── toast.js           # Toast-стор
│   │   │   ├── utils.js           # formatDate, verdict helpers, markdown
│   │   │   ├── router.js          # Обёртка над window.navigate
│   │   │   ├── stores.js
│   │   │   └── components/         # Navbar, Footer, ToastStack
│   │   └── routes/pages/         # Одна страница = один .svelte
│   │       ├── Home.svelte         # Главная / лендинг
│   │       ├── Auth.svelte         # Вход / регистрация / сброс
│   │       ├── Problems.svelte     # Архив с фильтрами
│   │       ├── ProblemDetail.svelte
│   │       ├── ProblemEditor.svelte # Редактор кода + вердикты
│   │       ├── Leaderboard.svelte
│   │       ├── Submissions.svelte
│   │       ├── Learning.svelte
│   │       ├── LearningDetail.svelte
│   │       ├── Tasks.svelte        # Канбан с drag-and-drop
│   │       ├── Messenger.svelte
│   │       ├── News.svelte
│   │       ├── Profile.svelte
│   │       └── NotFound.svelte
│   ├── package.json
│   └── vite.config.js
├── fastapi_app/
│   ├── main.py                    # FastAPI app, lifespan, раздача фронта
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .env.example
│   └── app/
│       ├── api/                   # 11 роут-модулей по доменам
│       ├── core/config.py         # pydantic-settings + email_enabled
│       ├── db/database.py         # async engine, sessionmaker, init_db
│       ├── models/models.py       # 23 SQLAlchemy-модели
│       ├── schemas/               # Pydantic v2
│       ├── services/
│       │   ├── email_service.py   # SMTP + HTML-шаблоны
│       │   ├── password_service.py
│       │   └── judger/             # Судья: judger + runner + verifiers
│       ├── middleware/rate_limiter.py
│       └── data/seed_problems.py  # Демо: юзеры, задачи, модули, новости
├── LICENSE
└── README.md
```

---

## API

49 эндпоинтов, полностью задокументированы в OpenAPI.

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
- **Health**: <http://localhost:8000/health>

### Аутентификация

| Метод | Путь                              | Описание                                |
|-------|-----------------------------------|-----------------------------------------|
| POST  | `/api/auth/register`              | Регистрация, высылается код             |
| POST  | `/api/auth/login`                 | Вход, access + refresh токены           |
| POST  | `/api/auth/refresh`               | Обновить пару токенов                   |
| POST  | `/api/auth/logout`                | Выход                                   |
| GET   | `/api/auth/me`                    | Текущий пользователь                    |
| POST  | `/api/auth/confirm-email`         | Подтвердить email 6-значным кодом       |
| POST  | `/api/auth/reset-password-request`| Запросить код сброса пароля              |
| POST  | `/api/auth/reset-password-confirm`| Сбросить пароль                          |
| POST  | `/api/auth/change-password`       | Сменить пароль (требует аутентификации)  |
| PUT   | `/api/auth/profile`               | Обновить имя / фамилию                  |

### Задачи и сабмиты

| Метод | Путь                                | Описание                              |
|-------|-------------------------------------|---------------------------------------|
| GET   | `/api/problems/`                    | Список с фильтрами (difficulty, category, search) |
| GET   | `/api/problems/categories`          | Счётчики по категориям                |
| GET   | `/api/problems/{id}?lang=en\|ru\|tj` | Детали задачи с переводом             |
| POST  | `/api/problems/submissions`         | Отправить решение, судья async        |
| GET   | `/api/problems/submissions/{id}`    | Статус сабмита (фронт опрашивает)     |
| GET   | `/api/problems/submissions`        | Лента сабмитов с фильтрами             |

### Прочее

- **Задачи личные**: `GET/POST/PATCH/DELETE /api/tasks/`
- **Мессенджер**: `/api/messenger/chats`, `/messages`, `/messages/direct/{user_id}`
- **Друзья**: `/api/friends/request/{id}`, `/accept/{id}`, `/reject/{id}`, `/list`, `/requests`
- **Обучение**: `/api/learning/modules`, `/modules/{slug}`, `/modules/{id}/enroll`
- **Новости**: `/api/news`, `/news/{id}`, полный CRUD для авторов
- **Олимпиады**: `/api/olympiads/contests`, `/contests/{id}/standings`
- **Статистика**: `/api/stats/dashboard`, `/stats/leaderboard`, `/stats/feed`, `/stats/me`
- **Админ**: `/api/admin/users` (только id == 1)

---

## Судья

Подключается через переменную окружения `JUDGER_BACKEND`:

| Backend       | Когда использовать                                       |
|---------------|----------------------------------------------------------|
| `subprocess`  | По умолчанию. Не требует внешних зависимостей. `RLIMIT_AS` + wall-clock. |
| `docker`      | Опционально. Каждый сабмит в эфемерном контейнере с `--network-disabled`. |

Оркестратор `JudgerService.judge_submission`:

1. Грузит сабмит и его тест-кейсы.
2. Ставит вердикт `JUDGING` и коммитит.
3. Идёт по тестам по порядку. На первом упавшем — короткое замыкание с
   `COMPILATION_ERROR` / `TIME_LIMIT_EXCEEDED` / `MEMORY_LIMIT_EXCEEDED` /
   `RUNTIME_ERROR` / `WRONG_ANSWER`.
4. Если все тесты прошли — `ACCEPTED`, создаётся `ProblemSolve` (при первом
   решении), обновляются `solved_count` и `rating` пользователя, пишется
   `SubmissionFeed`.
5. Коммитит и возвращает вердикт.

Фронтенд опрашивает `GET /api/problems/submissions/{id}` каждые 800 мс.

---

## Конфигурация

Все настройки — в `app/core/config.py`, читаются из переменных окружения или
`.env`. Скопируйте `.env.example` в `.env`:

| Переменная                       | По умолчанию                          | Описание                              |
|----------------------------------|---------------------------------------|---------------------------------------|
| `SECRET_KEY`                     | случайный 32-байтный URL-safe         | Секрет для подписи JWT                |
| `DATABASE_URL`                   | `sqlite+aiosqlite:///./devstudio.db` | URL SQLAlchemy                        |
| `DEBUG`                          | `true`                                | Подробные логи                        |
| `ALLOWED_ORIGINS`                | `["http://localhost:8000", …]`        | CORS allowlist                        |
| `PASSWORD_MIN_LENGTH`            | `8`                                   | Минимальная длина пароля              |
| `ACCESS_TOKEN_EXPIRE_MINUTES`    | `30`                                  | TTL access-токена                     |
| `REFRESH_TOKEN_EXPIRE_DAYS`      | `7`                                   | TTL refresh-токена                    |
| `MAX_LOGIN_ATTEMPTS`             | `5`                                   | Попыток до троттлинга                  |
| `LOGIN_ATTEMPT_WINDOW_MINUTES`   | `60`                                  | Окно троттлинга                       |
| `EMAIL_TOKEN_EXPIRE_MINUTES`     | `30`                                  | TTL кода подтверждения / сброса        |
| `JUDGER_BACKEND`                 | `subprocess`                          | `subprocess` или `docker`             |
| `JUDGER_WORKDIR`                 | `/tmp/devstudio-judge`                | Куда класть temp-файлы кода           |
| `SMTP_USER`                      | (пусто)                               | Логин SMTP; пусто = без почты         |
| `SMTP_PASSWORD`                  | (пусто)                               | Пароль SMTP                           |
| `SMTP_HOST`                      | `smtp.yandex.ru`                      | SMTP-сервер                           |
| `SMTP_PORT`                      | `465`                                 | SMTP SSL-порт                         |
| `EMAIL_FROM`                     | `noreply@tajik-fire.io`               | Адрес отправителя                     |
| `FRONTEND_DIST`                  | `../frontend/dist`                   | Путь к собранному Svelte              |

Если `SMTP_USER` пуст — API возвращает код подтверждения в теле ответа,
чтобы можно было проходить флоу локально.

---

## CI

GitHub Actions (`.github/workflows/ci.yml`) запускается на каждый push и PR:

1. **Бэкенд** (Python 3.11 и 3.12 параллельно):
   - Устанавливает `g++` и `default-jdk` для судьи.
   - `ruff` lint (E9, F63, F7, F82, F401, F811).
   - Smoke-test: импортирует приложение, запускает `init_db()`, проверяет
     что ключевые роуты зарегистрированы.
   - **Тест судьи на Python**: логинится как demo, сабмитит корректное
     решение, опрашивает эндпоинт до получения `accepted`.
   - **Тест судьи на C++**: то же, но на C++17 — проверяет компиляцию и
     запуск через g++.

2. **Фронтенд** (Node 20):
   - `npm ci` или `npm install`.
   - `npm run build`.
   - Проверка размера бандла (warning, если > 250 КБ).
   - Загрузка `frontend/dist` как артефакта.

3. **Docker** (только на push):
   - Сборка образа с кэшем buildx.
   - Запуск контейнера и проверка `/health`.

---

## Деплой

### Docker

```bash
docker compose up --build -d
docker compose logs -f app
```

Контейнер открывает порт `8000`. Примонтируйте volume в `/app/data` для
SQLite-персистентности между рестартами.

### Ручной деплой

```bash
pip install -r requirements.txt
export SECRET_KEY=$(openssl rand -hex 32)
export DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/tajikfire
cd ../frontend && npm install && npm run build && cd ../fastapi_app
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Для PostgreSQL замените драйвер на `postgresql+asyncpg` и добавьте
`asyncpg` в `requirements.txt`.

### Продакшен-чеклист

- [ ] `SECRET_KEY` — длинная случайная строка (≥ 32 байта).
- [ ] `DEBUG=false`.
- [ ] `ALLOWED_ORIGINS` настроен под ваш домен.
- [ ] `SMTP_USER` / `SMTP_PASSWORD` для реальной почты.
- [ ] Приложение за HTTPS (Caddy, Nginx, Cloudflare, …).
- [ ] `JUDGER_BACKEND=docker` для более сильной изоляции в мультитенантном деплое.
- [ ] Smoke-тесты доступности `g++` и `java` перед запуском.

---

## Roadmap

- [ ] WebSocket-push вердиктов вместо поллинга.
- [ ] Живое участие в контестах с персональным скорингом и пенальти.
- [ ] Админ-панель для управления задачами с инлайн-редактором тест-кейсов.
- [ ] Светлая тема + переключатель `data-theme`.
- [ ] Индикатор «печатает…» в групповых чатах.
- [ ] Виртуальное участие в контестах.
- [ ] График истории рейтинга пользователя в стиле Codeforces.

---

## Лицензия

[MIT](./LICENSE) — форкайте, шипьте, учитесь.
