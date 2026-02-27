# Rollout Plan — Canary to Full Production

This document describes the phased rollout strategy to minimize risk and enable fast rollback.

## Strategy Overview

**Phased approach:**
1. **Internal canary (hour 0–2):** Super-users and internal staff test the system.
2. **Pilot orgs (day 0–1):** 1–2 large, tech-savvy customer organizations.
3. **General availability (day 2+):** Roll out to all organizations.

Each phase has **go/no-go decision points** backed by monitoring and quick-rollback capability.

## Phase 1: Internal Canary (hours 0–2)

**Who:** Product, engineering, and super-users (< 20 users)

**Traffic:**
- 100% of internal sessions route to the new version.
- Monitor error rate, latency, and database queries closely.

**Smoke test checklist:**
- [ ] Login/logout works
- [ ] Create a journal entry
- [ ] Generate a trial balance report
- [ ] Create and delete a user
- [ ] View user profile
- [ ] Help panel renders on multiple pages
- [ ] In-app error handling graceful

**Success criteria:**
- Zero critical errors
- All smoke tests pass
- Latency p95 < 2s (or baseline + 10%)
- No unhandled exceptions in Sentry

**Go/No-go decision:** Engineering lead + Product lead at T+2h

---

## Phase 2: Pilot Orgs (day 0–1)

**Who:** 1–2 volunteer customer organizations (< 500 users per org)

**Traffic routing:** Gradually shift traffic:
- Hour 4: 10% of pilot org traffic
- Hour 6: 25% pilot org traffic
- Hour 12: 50% pilot org traffic
- Hour 24: 100% pilot org traffic (if no critical issues)

**Monitoring during pilot:**
- Real user monitoring (RUM): track session duration, errors, page load times
- Error rate and latency percentiles (p50, p95, p99)
- Database queue/connection pool utilization
- Scheduled job backlog (Celery)
- Customer support tickets related to system behavior

**Success criteria:**
- Error rate < 0.5% (or baseline)
- Latency p95 < 3s
- Customer-reported issues resolving quickly (< 1h)
- No data integrity issues
- All critical features functional

**Go/no-go decision:** SRE lead + Product lead at T+24h

---

## Phase 3: General Availability (day 2+)

**Traffic:** Roll out to all remaining organizations at:
- Day 2: 25%
- Day 3: 50%
- Day 4: 100%

**Monitoring:**
- Higher thresholds; look for patterns across orgs
- Customer support volume
- Financial data consistency checks (entry balances, report totals)

**Success criteria:**
- Error rate < 1% (or SLA)
- Latency and throughput stable
- Support tickets at normal baseline
- Revenue/usage KPIs tracking as expected

**Go/no-go decision:** Product + SRE at end of each day

---

## Quick Rollback (any phase)

**Trigger:** Critical bug, data corruption, or uncontrollable error rate

**Procedure (< 30 minutes):**
1. Page on-call SRE + Product
2. Halt traffic to new version (kill canary, revert traffic split)
3. Restart previous approved version from container registry
4. Run smoke tests on previous version
5. Resume service
6. Document what went wrong; open incident ticket
7. Post-mortem within 24 hours

```bash
# Example rollback commands
docker compose stop app
docker compose pull  # (gets previous tag)
docker compose up -d
docker compose exec app python src/manage.py migrate  # if DB needs downgrade (risky)
```

**Note:** DB rollback is only safe if performed immediately; after that, restore from backup.

---

## Communication Plan

| Phase | Communication | Owner | When |
|-------|---------------|-------|------|
| Canary start | Slack notification to team | Engineering | T+0 |
| Pilot start | Email to pilot orgs + in-app banner | Product | T+4h |
| Pilot go-live 100% | Email to pilot orgs | Product | T+24h |
| GA start | Email to all customers + marketing announcement | Product | T+48h |
| Issue escalation | Support ticket + Slack to on-call | Support | Immediate |
| Rollback | Emergency notification to all affected users | Product + Comms | Immediate |

---

## Rollout Calendar (example)

| Time | Phase | Action | Owner |
|------|-------|--------|-------|
| Feb 28 09:00 | Canary | Deploy to internal | SRE |
| Feb 28 11:00 | Canary | Go/no-go decision | Eng + Product |
| Feb 28 13:00 | Pilot | Deploy to pilot orgs (10% traffic) | SRE |
| Feb 28 18:00 | Pilot | Increase to 50% | SRE |
| Mar 01 09:00 | Pilot | 100% pilot traffic | SRE |
| Mar 01 18:00 | Pilot | Go/no-go final | SRE + Product |
| Mar 02 09:00 | GA | Deploy to 25% of remaining | SRE |
| Mar 03 09:00 | GA | 50% remaining | SRE |
| Mar 04 09:00 | GA | 100% all orgs | SRE |

---

## Success Metrics (Post-Rollout)

Track these for 7 days:
- **Availability:** 99.9% target
- **Error rate:** < 1% of requests
- **Latency p95:** < 3 seconds
- **Support ticket surge:** no sustained spike
- **Data integrity:** no inconsistencies reported
- **Performance degradation:** none vs. baseline

*Document actual results and compare against targets for launch retrospective.*
