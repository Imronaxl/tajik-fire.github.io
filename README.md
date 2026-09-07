# tajik-fire

<p align="center">
  <strong>Платформаи барномасозии рақобатӣ бо судяи sandbox, роҳҳои омӯзишӣ ва фармони иҷтимоӣ.</strong>
</p>

<p align="center">
  <a href="https://github.com/Imronaxl/tajik-fire.github.io/actions"><img src="https://github.com/Imronaxl/tajik-fire.github.io/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/fastapi-0.115-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/svelte-4-FF3E00?logo=svelte&logoColor=white" alt="Svelte">
  <img src="https://img.shields.io/badge/judger-python%20%7C%20C%2B%2B%20%7C%20java-8A2BE2" alt="Judger">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

<p align="center">
  <a href="#дархостҳои-асосӣ">Дархостҳои асосӣ</a> ·
  <a href="#скриншотҳо">Скриншотҳо</a> ·
  <a href="#меъморӣ">Меъморӣ</a> ·
  <a href="#сохтори-лоиҳа">Сохтор</a> ·
  <a href="#забонҳо">Забонҳо</a> ·
  <a href="#тестҳо">Тестҳо</a> ·
  <a href="#api">API</a>
</p>

---

**tajik-fire** — платформаи барномасозии рақобатӣ дар услуби Codeforces бо трекери омӯзишӣ. Бэкенд дар FastAPI ҳалли Python, C++ ва Java-ро дар раванди ҷудогона месанҷад, фронтенд дар Svelte 4 ба як бандли ~126 КБ (39 КБ gzip) ҷамъ мешавад ва бе virtual DOM кор мекунад.

---

## Дархостҳои асосӣ

- **Судяи sandbox** — ҳар сабт дар раванди ҷудогона бо `RLIMIT_AS` ва wall-clock таймаут иҷро мешавад. Python 3, C++ 17 ва Java 11 дастгирӣ мешаванд.
- **Аутентификатсияи JWT** — access-токени кӯтоҳ (30 дақ), refresh-токен 7 рӯз, throttle кӯшишҳои воридшавӣ, bcrypt.
- **Email опционалӣ** — бе SMTP кодҳои тасдиқ дар ҷавоби API баргардонида мешаванд, аз ин рӯ локалӣ аз бе почта фаъолият кардан мумкин аст.
- **Многоязычность (i18n)** — интерфейс ва шарҳи масъалаҳо ба се забон тарҷума шудааст: тоҷикӣ (пешфарз), русӣ, англисӣ. Иловаи забони нав — як сатр дар конфиг.
- **Фарми сабтҳо дар вақти воқеӣ** — ҳар вердикт ба ҷадвали алоҳида навишта мешавад ва дар дашборд, саҳифаи асосӣ ва бахши «Сабтҳо» нишон дода мешавад.
- **Системаи рейтинг** — ҳали аввал хол медиҳад: осон +5, миёна +12, душвор +25. Топ-3 ба подиум меафтанд.
- **ИИ-ёрдамчи (placeholder)** — тугмаи шинокунанда дар ҳар саҳифа, модули AI дар бэкенд ҷойгир аст. Иловаи LLM дар оянда танҳо бо иваз кардани як модул.
- **Архитектураи модулӣ** — ҳар функсия (competitive, learning, social, tasks, ai) модули алоҳида. Барои илова намудани cybersecurity ё дигар намуди вазифаҳо — танҳо модули нав эҷод кунед.

---

## Скриншотҳо

Скриншотҳо аз барномаи воқеӣ гирифта шудаанд (Playwright, 1440×900, retina). Файлҳо дар [`docs/screenshots/`](./docs/screenshots).

<table>
  <tr>
    <td width="50%" align="center"><b>Асосӣ</b></td>
    <td width="50%" align="center"><b>Архиви масъалаҳо</b></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/01-home.png" alt="Асосӣ"></td>
    <td><img src="docs/screenshots/03-problems.png" alt="Масъалаҳо"></td>
  </tr>
  <tr>
    <td width="50%" align="center"><b>Редактори код</b></td>
    <td width="50%" align="center"><b>Рейтинг</b></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/05-editor.png" alt="Редактор"></td>
    <td><img src="docs/screenshots/08-leaderboard.png" alt="Рейтинг"></td>
  </tr>
  <tr>
    <td width="50%" align="center"><b>Канбони вазифаҳо</b></td>
    <td width="50%" align="center"><b>Профил</b></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/12-tasks.png" alt="Вазифаҳо"></td>
    <td><img src="docs/screenshots/14-profile.png" alt="Профил"></td>
  </tr>
</table>

---

## Меъморӣ

```
┌─────────────────────────────────────────────────────────────────┐
│                            Браузер                              │
│            Svelte 4 · CSS variables · History API · i18n       │
└───────────────┬──────────────────────────────────┬──────────────┘
                │  HTTP / JSON                    │  SPA навигация
                ▼                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                          FastAPI app                            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                     core/                               │    │
│  │   config · database · security · i18n · rate_limiter   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────── modules/ ──────────────────────┐       │
│  │  accounts/   │ social/      │ competitive/           │       │
│  │  auth, users  │ messenger,   │ problems, judger,      │       │
│  │  profile,     │ friends,     │ contests, submissions  │       │
│  │  friends      │ notifications│                        │       │
│  │               │              │ learning/               │       │
│  │  analytics/   │ tasks/       │ tracks, modules          │       │
│  │  user stats  │ personal     │                         │       │
│  │               │ kanban       │ ai_assistant/ (placeholder)│   │
│  └───────────────────────────────────────────────────────┘       │
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐      │
│  │              SQLAlchemy 2.0  ·  async session         │      │
│  └───────────────────────────┬───────────────────────────┘      │
│                              │                                   │
│         ┌────────────────────┴───────────────────────┐          │
│         ▼                                            ▼          │
│  ┌─────────────┐                            ┌──────────────┐    │
│  │  SQLite /   │                            │   Судья      │    │
│  │ PostgreSQL │                            │ (subprocess) │    │
│  └─────────────┘                            └──────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

Судя ҳамчун `asyncio`-вазифаи пасзамина барои ҳар сабт кор мекунад: сессияи навро мекушояд, коди корбарро тавассути `subprocess.run` бо маҳдудияти ҳофиза ва wall-clock таймаут иҷро мекунад, вердиктро ба `submissions` менависад ва ба `submission_feed` илова мекунад. Фронтенд эндпоинти сабтро то иваз шудани вердикт аз `pending` / `judging` ҳар 800 мс мепурсад.

---

## Сохтори лоиҳа

```
.
├── .github/workflows/ci.yml        # CI: ruff + smoke + judge + Docker
├── docs/screenshots/                # Скриншотҳои UI
├── tests/                           # Ҳама тестҳо (ниже детально)
│   ├── conftest.py                  # общие фикстуры
│   ├── unit/                        # unit-тесты (пари 0.2 сек)
│   ├── integration/                 # API интеграционные (пари 17 сек)
│   ├── e2e/                         # Playwright E2E
│   ├── load/                        # Locust нагрузочные
│   └── README.md
├── frontend/                        # Svelte 4 + Vite 5
│   └── src/
│       ├── app.css                  # дизайн-система (токены)
│       ├── App.svelte               # корневой компонент
│       ├── core/
│       │   └── i18n/                # ← ИЛОВА КАРДАНИ ЗАБОН ДАР ИН ҶО
│       │       ├── config.js        #     рӯйхати забонҳо
│       │       ├── index.js        #     движок t('key')
│       │       └── locales/        #     tg.json, ru.json, en.json
│       ├── lib/
│       │   ├── api.js               # fetch-обёртка
│       │   ├── auth.js              # Svelte store: user, login, logout
│       │   ├── toast.js
│       │   ├── router.js            # History API
│       │   ├── utils.js             # formatDate, verdict helpers, markdown
│       │   └── components/          # Navbar, Footer, ToastStack,
│       │                            # LanguageSwitcher, AIAssistant
│       └── routes/pages/           # ҳар саҳифа алоҳида
├── fastapi_app/
│   ├── main.py                      # FastAPI app + модульҳо
│   ├── requirements.txt
│   ├── Dockerfile                   # многоэтапная сборка
│   └── app/
│       ├── core/
│       │   ├── config.py            # pydantic-settings
│       │   └── database.py          # async engine
│       ├── api/                     # руты по доменам
│       ├── modules/                 # ← СТРУКТУРА МОДУЛӢ
│       │   ├── registry.py          #   реестр модулей
│       │   ├── accounts/            #   auth, users, profile
│       │   ├── social/              #   messenger, friends
│       │   ├── competitive/         #   problems, judger
│       │   ├── learning/            #   tracks, modules
│       │   ├── tasks/               #   personal kanban
│       │   ├── analytics/           #   user stats
│       │   └── ai_assistant/        #   AI placeholder
│       ├── models/models.py         # 23 SQLAlchemy-модели
│       ├── schemas/                 # Pydantic v2
│       ├── services/
│       │   ├── email_service.py     # SMTP + HTML-шаблоны
│       │   ├── password_service.py
│       │   └── judger/              # судя
│       ├── middleware/rate_limiter.py
│       └── data/seed_problems.py    # демо-данные
├── docker-compose.yml
├── LICENSE
└── README.md
```

---

## Забонҳо (i18n)

Системаи многоязычности дар як нуқта марказонида шудааст — **`frontend/src/core/i18n/config.js`**.

### Иловаи забони нав

Барои илова кардани забон (масалан, узбекӣ):

1. Файли `frontend/src/core/i18n/locales/uz.json` эҷод кунед (аз `tg.json` нусха бардоред ва тарҷума кунед)
2. Дар `config.js` як сатр илова кунед:

```js
export const SUPPORTED_LANGUAGES = [
  { code: 'tg', name: 'Тоҷикӣ', nativeName: 'Тоҷикӣ', file: () => import('./locales/tg.json') },
  { code: 'uz', name: 'O‘zbek', nativeName: 'O‘zbekcha', file: () => import('./locales/uz.json') },  // ← нав
  { code: 'ru', name: 'Русский', nativeName: 'Русский', file: () => import('./locales/ru.json') },
  { code: 'en', name: 'English', nativeName: 'English', file: () => import('./locales/en.json') },
];
```

Ҳама — забон дар переключатели автоматӣ пайдо мешавад, забони пешфарз аз `localStorage` ё аз забони браузер муайян мешавад.

### Тарҷумаи серверӣ

Барои тарҷумаи шарҳи масъалаҳо дар бэкенд — `app/core/i18n.py` (планируется). Ҳоло шарҳҳо дар `seed_problems.py` дар се забон ҳамроҳ карда мешаванд.

---

## Тестҳо

Папкаи `tests/` ҳама тестҳои платформаро дар бар мегирад:

```
tests/
├── conftest.py                 # общие фикстуры (db, client, auth_token)
├── unit/                       # 23 unit-тесты (0.2 сек)
│   ├── test_password_service.py
│   ├── test_verifiers.py       #   судья
│   ├── test_email_service.py
│   └── test_config.py
├── integration/                # 49 integration-тесты (17 сек)
│   ├── test_auth_api.py        #   auth, JWT, password
│   ├── test_problems_api.py    #   problems, submissions
│   ├── test_tasks_api.py       #   personal tasks
│   ├── test_messenger_api.py   #   chats, messages
│   ├── test_friends_api.py     #   friend requests
│   ├── test_judger_api.py      #   judge pipeline
│   ├── test_ai_assistant_api.py
│   └── test_stats_api.py
├── e2e/                        # Playwright E2E
│   └── test_user_journey.py
└── load/                        # Locust нагрузочные
    └── locustfile.py
```

### Запуск

```bash
# Ҳама тестҳо
pytest tests/unit tests/integration -v

# Танҳо unit (0.2 сония)
pytest tests/unit -v

# Танҳо integration (17 сония)
pytest tests/integration -v

# E2E (need running backend)
uvicorn main:app --reload &  # in fastapi_app/
pytest tests/e2e -v

# Нагрузочные (Locust)
cd tests/load && locust -f locustfile.py --host=http://localhost:8000
```

### Покрытие

| Уровень      | Тестҳо                                                  |
|--------------|----------------------------------------------------------|
| unit         | изолированные функции: пароль, вердикт, email, конфиг   |
| integration  | ҳар эндпоинти API: статус-коды, хатоҳо, бизнес-логика   |
| e2e          | UI пользовательский путь в реальном браузере            |
| load         | поведение под нагрузкой: RPS, латентность, ошибки       |

---

## API

49 эндпоинтов, в OpenAPI документированы.

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
- **Health**: <http://localhost:8000/health>

### Аутентификация

| Метод | Путь                              | Описание                                |
|-------|-----------------------------------|-----------------------------------------|
| POST  | `/api/auth/register`              | Бақайдгирӣ                              |
| POST  | `/api/auth/login`                 | Воридшавӣ                               |
| POST  | `/api/auth/refresh`               | Навсозии токенҳо                        |
| POST  | `/api/auth/logout`                | Баромадан                               |
| GET   | `/api/auth/me`                    | Корбари ҷорӣ                            |
| POST  | `/api/auth/change-password`       | Тағйири парол                           |
| PUT   | `/api/auth/profile`               | Таҳрири профил                          |

### Масъалаҳо ва сабтҳо

| Метод | Путь                                | Описание                              |
|-------|-------------------------------------|---------------------------------------|
| GET   | `/api/problems/`                    | Рӯйхат бо филтрҳо                     |
| GET   | `/api/problems/{id}?lang=tg\|ru\|en` | Тафсилот бо тарҷума                   |
| POST  | `/api/problems/submissions`         | Сабти ҳал                              |
| GET   | `/api/problems/submissions/{id}`    | Вердикт                                |

### AI Assistant

| Метод | Путь              | Описание                              |
|-------|-------------------|---------------------------------------|
| GET   | `/api/ai/status`  | Статуси ИИ (placeholder)              |
| POST  | `/api/ai/chat`    | Чат бо ИИ (ҷавоби placeholder)        |

---

## Быстрый старт

### Локальная разработка

```bash
git clone https://github.com/Imronaxl/tajik-fire.github.io.git
cd tajik-fire.github.io

# Backend
cd fastapi_app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Frontend
cd ../frontend
npm install
npm run build

# Запуск (раздаёт фронтенд)
cd ../fastapi_app
uvicorn main:app --reload
```

Боз: <http://localhost:8000>. Демо-аккаунт: `demo / Demo1234`.

### Dev-режим фронтенда (с HMR)

```bash
# Терминал 1: бэкенд
cd fastapi_app && uvicorn main:app --reload

# Терминал 2: Vite dev server
cd frontend && npm run dev
```

### Docker

```bash
docker compose up --build
```

---

## Конфигурация

| Переменная              | По умолчанию                          | Описание                          |
|-------------------------|---------------------------------------|-----------------------------------|
| `SECRET_KEY`            | случайный                             | JWT секрет                        |
| `DATABASE_URL`          | `sqlite+aiosqlite:///./devstudio.db` | SQLAlchemy URL                    |
| `DEBUG`                 | `true`                                | Подробные логи                    |
| `ALLOWED_ORIGINS`       | `["http://localhost:8000", …]`        | CORS allowlist                    |
| `PASSWORD_MIN_LENGTH`   | `8`                                   | Мин. длина пароля                 |
| `JUDGER_BACKEND`        | `subprocess`                          | `subprocess` или `docker`         |
| `SMTP_USER`             | (пусто)                               | SMTP логин; пусто = без почты     |
| `FRONTEND_DIST`         | `../frontend/dist`                    | Путь к собранному Svelte          |

---

## CI

GitHub Actions (`.github/workflows/ci.yml`):

1. **Backend** (Python 3.11 + 3.12): ruff lint + smoke + судья на Python + C++ + AI assistant
2. **Frontend** (Node 20): npm install + build + проверка размера бандла
3. **Docker**: сборка образа + проверка `/health`

---

## Лицензия

[MIT](./LICENSE) — форк кунед, кораб кунед, омӯзед.
