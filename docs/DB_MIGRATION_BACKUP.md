# Database Migration & Backup Plan

This document outlines the safe migration and backup strategy for production launch.

## Pre-Launch Backup (Day before deployment)

1. **Take a full database snapshot:**
   ```bash
   # Backup production DB to local file
   pg_dump -U accountingdb -h db.prod.internal -F c -b > accounting_backup_$(date +%Y%m%d_%H%M%S).dump
   
   # Or via dockerized DB:
   docker compose exec -T db pg_dump -U postgres accounting > backup_prelaunch.sql
   ```

2. **Verify backup integrity:**
   ```bash
   # Restore to a test DB and run a quick sanity check
   createdb test_restore
   pg_restore -U postgres -d test_restore accounting_backup_20260228.dump
   psql -U postgres -d test_restore -c "SELECT COUNT(*) FROM users_userprofile;"
   dropdb test_restore
   ```

3. **Store backup securely:**
   - Copy to offsite storage (S3, backup appliance, etc.)
   - Retain for 30 days minimum

## Launch Day Migration Steps

### 1. Disable write traffic (optional for brief maintenance window)
   ```bash
   # Put app into maintenance mode or redirect traffic to canary
   # (skip if using blue-green deployment)
   ```

### 2. Run Django migrations
   ```bash
   # Test migrations on staging first
   python src/manage.py migrate --plan
   
   # Execute migrations
   docker compose exec app python src/manage.py migrate --noinput
   ```

### 3. Verify migration success
   ```bash
   docker compose exec app python src/manage.py migrate --check
   ```

### 4. Update Django cache and warm up
   ```bash
   docker compose exec app python src/manage.py clear_cache
   docker compose exec app python src/manage.py shell -c "
   from django.core.cache import cache
   cache.clear()
   print('Cache cleared.')
   "
   ```

## Rollback Procedure (if critical issues arise)

### Option A: Quick Rollback (within 1 hour)
1. Stop app servers
2. Restore DB from backup snapshot taken immediately before migrations:
   ```bash
   ssh prod-db "pg_restore -U postgres -d accounting --clean accounting_backup_prelaunch.dump"
   ```
3. Restart app servers
4. Monitor for recovery; post-incident analysis

### Option B: Data-aware Rollback (conflicts with post-launch transactions)
- If data was modified after launch, a simple restore will lose it
- Consider a point-in-time restore (PITR) if available on prod DB
- Coordinate with support to notify affected users of any transaction loss

## Monitoring Checkpoints

| Checkpoint | Check | Pass/Fail |
|-----------|-------|-----------|
| DB size | `SELECT pg_size_pretty(pg_database_size('accounting'));` | No anomalous growth |
| Connection count | `SELECT count(*) FROM pg_stat_activity;` | < max_connections |
| Unread logs | Check app and DB error logs | No critical errors |
| Test user login | Browser login + journal entry creation | Success |
| Backup integrity | Verify backup file size and timestamp | Recent, >100MB expected |

## Schedule (example)
- **T-1 day, 18:00:** Backup snapshot + integrity test
- **T-day, 08:00:** Final backup, freeze code
- **T-day, 09:00:** Stop traffic, begin migration
- **T-day, 09:15:** Run migrations, verify, restart services
- **T-day, 09:30:** Green light, resume traffic (or 5-10% canary)
- **T-day, 10:00-12:00:** Heavy monitoring window
- **T-day+3 days:** Keep backup + rollback ready; preserve logs

*Adjust times for your timezone and team availability.*
