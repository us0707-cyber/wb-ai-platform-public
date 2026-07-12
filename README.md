# WB AI Platform 2.1

Платформа управления товарами Wildberries: каталог, SEO, аналитика, расчёт цен и AI-автопилот.

## Главное изменение 2.1

Wildberries Content API не всегда возвращает цену карточки. Поэтому раздел **Цены** теперь позволяет ввести и сохранить финансовые параметры вручную:

- текущая цена;
- себестоимость;
- логистика на единицу;
- реклама на единицу;
- комиссия Wildberries;
- налог;
- средняя рыночная цена;
- целевая маржа.

Расчёт показывает рекомендуемую цену, точку безубыточности, прибыль с единицы и ожидаемую маржу. При недостатке данных система сообщает, что нужно заполнить, и не предлагает фиктивные цены.

## Запуск

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
docker compose logs api --tail=80
```

Открыть: `http://localhost:8000`

## Обновление с 2.0

Новых миграций базы данных нет. Остановите старую версию командой `docker compose down`, распакуйте 2.1, скопируйте `.env.example` в `.env` и запустите сборку. Docker Compose использует существующий именованный том проекта.

## Enterprise v3.0 Alpha

The `3.0.0-alpha.2` foundation introduces a service/repository architecture,
request correlation IDs and structured access logging without changing the
existing database schema. See `docs/ARCHITECTURE.md`.



## Roles and audit

Roles: `admin`, `manager`, `analyst`. Audit history is available at `GET /api/v1/audit`.

## AI Engine (v3.0 Alpha 3)

The platform supports a deterministic local provider out of the box and an optional OpenAI provider.

Environment settings:

```env
AI_PROVIDER=local
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
```

Available endpoints:

- `GET /api/v1/ai/provider`
- `POST /api/v1/ai/title`
- `POST /api/v1/ai/description`
- `POST /api/v1/ai/keywords`
- `POST /api/v1/ai/improve-card`
- `POST /api/v1/ai/analyze-product`
- `POST /api/v1/ai/apply`

Without an API key the application remains fully functional using the local provider.


## Analytics Engine (v3.0 Alpha 4)

The platform now provides KPI overview, daily revenue/profit trends, ABC/XYZ product classification, demand forecast and stock replenishment suggestions. Use `POST /api/v1/analytics/demo/generate` to create deterministic demo history for testing.
