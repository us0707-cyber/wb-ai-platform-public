# Changelog

## 3.0.0-alpha.6

- Added persistent schedules and scheduler worker.
- Added interval and one-time job execution.
- Added autopilot rules and product evaluation.
- Added migration 0010_scheduler_autopilot.
- Added scheduler/autopilot API and tests.


## 3.0.0-alpha.5

- Added persistent background job engine.
- Added job API, retries, cancellation, priorities and internal worker.
- Added analytics demo generation as a background job.
- Added migration `0009_job_engine`.

## 3.0.0-alpha.4

- Added Analytics Engine with daily fact storage.
- Added KPI overview, revenue/profit trends, ABC/XYZ classification and stock forecast.
- Added deterministic demo history generation for end-to-end testing.
- Added analytics UI with period filters, SVG trend chart, forecast cards and ABC/XYZ matrix.
- Added Alembic migration `0008_analytics_engine`.
- Added analytics service and API tests.

## 3.0.0-alpha.3

- Added provider-based AI Engine.
- Added deterministic local provider and OpenAI provider.
- Added structured AI endpoints for title, description, keywords, card improvement and analysis.
- Added database-backed AI response cache.
- Added role-protected application of AI results and audit logging.
- Added migration `0007_ai_engine`.
- Added strict OpenAI Structured Outputs schemas and refusal handling.
- Added `.gitattributes` and security guidance; `.env` is excluded from release archives.

## 3.0.0-alpha.2

- Added admin, manager and analyst roles.
- Added role-based write permissions.
- Added audit log model, API and migration.
- Added audit events for login, stores and products.
- Added request IDs and IP addresses to audit entries.

## 2.1.0

- Исправлен AI Pricing для товаров, у которых WB не вернул цену.
- Добавлена ручная форма финансовых параметров: текущая цена, себестоимость, логистика, реклама, комиссия, налог и рыночная цена.
- Финансовые параметры сохраняются в товаре при расчёте.
- Добавлены точка безубыточности, расчётная маржа, прибыль с единицы и объяснение рекомендации.
- Убраны фиктивные рекомендации 0,99 ₽ и средняя цена конкурентов 1 ₽.
- Анализ конкурентов теперь требует ценовой опоры и показывает диапазон цен.
- Автопилот создаёт рекомендацию заполнить финансовые данные вместо бессмысленного изменения нулевой цены.
- Добавлены проверки диапазона минимальной и максимальной цены.
- Добавлены тесты ручных финансовых входов и неполных данных.

## 2.0.0

- Синхронизация каталога Wildberries.
- Аналитика, конкурентный анализ, AI Pricing и автопилот.

## 3.0.0-alpha.1 - Enterprise Foundation

- Added repository layer for stores and products.
- Added ProductService to isolate business logic from API routes.
- Added request correlation IDs through `X-Request-ID`.
- Added structured access logging with method, path, status and duration.
- Added `/api/v1/system/info` architecture metadata endpoint.
- Moved application version to environment-aware settings.
- Preserved the existing database schema and user-facing functionality.
