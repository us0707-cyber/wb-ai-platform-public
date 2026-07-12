# WB AI Platform 3.0 Architecture

## Request flow

```text
HTTP API -> Service -> Repository -> SQLAlchemy -> PostgreSQL
```

Routers validate transport data and authentication. Services own business rules.
Repositories own database queries and persistence. Marketplace integrations are
kept behind integration clients.

## Foundation modules

- `src/api`: HTTP transport layer.
- `src/services`: business use cases.
- `src/repositories`: persistence layer.
- `src/integrations`: Wildberries and future marketplace adapters.
- `src/middleware`: request context and observability.
- `src/core`: configuration, security, errors and logging.

## Request correlation

Every response contains `X-Request-ID`. A client-supplied request ID is reused;
otherwise the API creates one. The same ID is included in access logs so a user
report can be matched with the exact backend request.

## Migration strategy

The alpha foundation does not change the database schema. Existing PostgreSQL
volumes from v2.1 remain compatible.


## Analytics subsystem

`AnalyticsDaily` stores product-level daily facts. `AnalyticsRepository` handles persistence and scoped queries, while `AnalyticsService` calculates KPI summaries, time series, ABC/XYZ classes and demand forecasts. HTTP handlers are isolated in `api/v1/analytics.py`.


## Scheduler and Autopilot

`SchedulerWorker` polls due schedules and converts them into persistent `Job` records. `AutopilotService` evaluates owner-scoped products against enabled rules and creates deduplicated recommendations.
