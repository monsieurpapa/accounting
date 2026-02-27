# Monitoring Setup Guide

This document covers monitoring, alerting, and observability for production launch.

## Quick Start

**Recommended stack:**
- **Metrics:** Prometheus (or managed service like Datadog)
- **Logging:** ELK, Splunk, or cloud logs (CloudWatch, Stackdriver)
- **Tracing:** Sentry for error tracking (errors + transactions)
- **Dashboards:** Grafana

## 1. Django Health Endpoints

Add a simple health check view in the app.

**File: `src/config/views.py` (or new `src/core/views.py`)**

```python
from django.http import JsonResponse
from django.db import connections
from django.core.cache import cache
import json

def health_check(request):
    """Health endpoint for load balancers and monitoring."""
    checks = {}
    
    # Database connectivity
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT 1")
        checks['database'] = 'ok'
    except Exception as e:
        checks['database'] = f'error: {str(e)}'
    
    # Cache connectivity (Redis)
    try:
        cache.set('health_check', 'ok', timeout=1)
        cache.get('health_check')
        checks['cache'] = 'ok'
    except Exception as e:
        checks['cache'] = f'error: {str(e)}'
    
    # Overall status
    status = 'ok' if all(v == 'ok' for v in checks.values()) else 'degraded'
    http_code = 200 if status == 'ok' else 503
    
    return JsonResponse({'status': status, 'checks': checks}, status=http_code)
```

**Register in `src/config/urls.py`:**

```python
from config.views import health_check

urlpatterns = [
    # ... existing patterns ...
    path('health/', health_check, name='health_check'),
]
```

**Test locally:**

```bash
curl http://localhost:8000/health/ | jq
```

## 2. Metrics to Collect

| Metric | Type | Threshold/Alert | Tool |
|--------|------|-----------------|------|
| HTTP error rate (5xx) | gauge | > 1% of traffic | Prometheus + Grafana |
| HTTP latency (p95, p99) | histogram | p95 > 2s | Prometheus |
| DB query duration | histogram | p95 > 1s | Django DB logging |
| DB connection pool | gauge | > 80% usage | psycopg2 logging |
| Cache hit rate | gauge | < 70% indicates issues | Redis CLI |
| Celery task failures | counter | any failure | Flower + Sentry |
| Memory usage (app) | gauge | > 80% container limit | Docker stats |
| Disk space | gauge | < 10% free | OS-level monitoring |
| SSL certificate expiry | days remaining | < 30 days | cert-exporter |

## 3. Sample Prometheus Configuration

**File: `prometheus.yml` (in your infrastructure repo)**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'app'
    static_configs:
      - targets: ['localhost:9000']  # Your Django metrics exporter
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']  # postgres_exporter

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']  # redis_exporter
```

## 4. Alerting Rules

**File: `prometheus_alerts.yml`**

```yaml
groups:
  - name: app
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
          
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 10m
        annotations:
          summary: "High latency (p95 > 2s)"
          
      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        annotations:
          summary: "PostgreSQL database is down"
          
      - alert: CeleryBacklogHigh
        expr: celery_queue_length > 1000
        for: 5m
        annotations:
          summary: "Celery queue backlog > 1000 tasks"
```

## 5. Sentry Integration

Add error tracking to catch and alert on exceptions.

**In `src/config/settings.py`:**

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,  # 10% of transactions
    environment="production",
    release="1.0.0",  # Match your git tag/version
)
```

## 6. Sample Grafana Dashboard

Create a dashboard with panels for:
- Request rate and 5xx errors
- Latency percentiles (p50, p95, p99)
- Database connections and query duration
- Memory and CPU usage
- Celery queue length

**Dashboard JSON** can be imported from Grafana's community contributions.

## 7. Logging Configuration

**`src/config/settings.py` logging config:**

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'accounting': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

Logs stream to stdout, where Docker or Kubernetes captures them and forwards to your logging backend.

## 8. Incident Response

**On-call runbook:**

1. Alert fires → on-call opens Grafana and Sentry
2. Triage severity (P1 = customer-facing, P2 = degraded, P3 = minor)
3. For P1: page incident commander; establish war room
4. Investigate: check recent deployments, error patterns, resource usage
5. Mitigate: scale up, restart services, roll back if needed
6. communicate with support and customers
7. Post-incident: review logs, update runbooks

## Monitoring Checklist (Pre-Launch)

- [ ] Health endpoint deployed and tested
- [ ] Prometheus instance running and scraping targets
- [ ] Alerting rules validated
- [ ] Sentry project created and SDK integrated
- [ ] Grafana dashboards created
- [ ] On-call escalation list documented
- [ ] Slack/PagerDuty integrations set up
- [ ] Log aggregation tested (logs flowing to backend)
- [ ] Team trained on reading dashboards and responding to alerts

*Save alert credentials securely in env or secret manager.*
