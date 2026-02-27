# Incident Response Playbook

This document guides the team through incident response during and after launch.

## Incident Severity Classification

| Severity | Criteria | Response Time | Owner |
|----------|----------|----------------|-------|
| **P1 - Critical** | System-wide outage, data loss, security breach, no workaround | 5 min | On-call SRE + Incident Commander |
| **P2 - High** | Major feature broken, multiple users affected, workaround exists | 30 min | Engineering lead + Support |
| **P3 - Medium** | Single user affected or minor feature, workaround exists | 2 hours | Support → Engineering |
| **P4 - Low** | Cosmetic, documentation, future enhancement | 1 week | Backlog |

## Incident Lifecycle

### 1. Detection (0-5 min)

**Alert routing:**
- Automated: Alert fires → page on-call via PagerDuty/Slack
- Manual: User / support reports issue → escalates to engineering

**Initial check:**
```
Is the status page updated? 
Status page → "Investigating" or "Partial Outage"

Quick triage:
- Check Grafana dashboard: error rate, latency, resource usage
- Check recent deployments: was something deployed in last 30 min?
- Check Sentry: error spikes?
```

### 2. Response (5-30 min)

**Declare incident:**
- Incident commander = highest ranking person on-call
- Open war room (Slack channel #incident-*hash*, Zoom call, or both)
- Invite: SRE, engineering, product, support lead
- Document timeline in incident ticket

**Initial response:**
```
Incident Commander role:
- Who: [name]
- What: [brief description]
- When: [start time]
- Where: [which component/org affected]
- Impact: [estimated users, revenue impact if any]
- Status: [investigating / mitigating / resolved]

SRE role:
- Monitor dashboards continuously
- Collect logs and metrics in ticket
- Report every 5 min
- Suggest remediation

Engineering role:
- Review recent code changes
- Check database replication lag
- Suggest rollback or hotfix

Support role:
- Monitor customer support queue
- Respond to tickets with status updates
- Collect user impact data
```

### 3. Mitigation (within SLA)

**Possible actions (in priority order):**

1. **Disable feature** (if isolated)
   ```bash
   # If accounting reports are broken but journal entries work:
   # Temporarily hide reporting menu or return 503
   ```

2. **Scale resources** (if overload)
   ```bash
   docker compose up -d --scale app=5  # Increase replicas
   ```

3. **Restart service** (if hang/memory leak)
   ```bash
   docker compose restart app
   ```

4. **Partial rollback** (if new code is culprit)
   ```bash
   git revert <commit-hash>
   git push
   docker compose up -d --build
   ```

5. **Full rollback** (if critical)
   ```bash
   docker compose stop
   docker pull accountingapp:v1.0.0  # Previous version
   docker compose up -d
   ```

6. **Database recovery** (if data corrupted)
   ```bash
   # Restore from backup (see docs/DB_MIGRATION_BACKUP.md)
   ```

### 4. Communication

**Update status page every 5-10 min:**
- Status page URL: `status.yourdomain.com`
- Message: "We are investigating slow journal entry creation. ETA: 30 min"

**Notify customers:**
- Email: Send to affected organizations
- In-app banner: "System experiencing issues; we are in the process of restoring service"
- Support: Post to support tickets

**Example email:**
```
Subject: System Status Update - [Time]

We are currently experiencing [brief issue description].
Impact: [what users can/can't do]
ETA: [estimated time to resolution]
Action: [what users should do; retry or wait]
Updates: [check status page for realtime updates]

Thank you for your patience.
- TicTacFlow Team
```

### 5. Resolution

**Verification:**
- Error rate drops to baseline
- Latency returns to normal
- Health endpoint returns 200
- Spot check: user can log in and perform key action

**Close incident:**
- Update ticket: "RESOLVED at [time]"
- Update status page to "All clear"
- Post final message to war room

### 6. Post-Incident Analysis (within 24 hours)

**Hold brief retro meeting**

**Blameless post-mortem:**
1. **What happened?** – timeline of events
2. **Why did it happen?** – root cause (not "someone made a mistake")
3. **How do we prevent it?** – action items
4. **Follow-up:** Assign owners; set due dates

**Example format:**
```
INCIDENT: Database connection pool exhaustion
DATE/TIME: 2026-03-01 09:15 UTC
DURATION: 23 minutes (detected after 5 min, resolved after 18 min)

TIMELINE:
09:10 – Deployment of caching layer for reports
09:15 – Alert: DB connections 95% + error rate spiking
09:20 – War room opened; identified connection leak in new code
09:25 – Reverted deployment
09:30 – DB recovered; confirmed green

ROOT CAUSE:
New caching code didn't close database cursors properly, leading to connection accumulation.
Should have been caught in code review + connection-pooling unit test.

PREVENTION:
1. Add connection pool monitoring to integration tests
2. Add pre-deployment perf test (load test connection behavior)
3. Code review process must verify resource cleanup
4. Owner: [engineer]; Due: [date]
```

## War Room Protocol

**Video call:** Start immediately for P1, within 30 min for P2

**Chat channel:** 
```
#incident-[severity]-[TIMESTAMP]
Message format:
@on-call-sre: [status / metrics]
@incident-commander: [updated status message]
@support: [customer impact]
```

**No blame; focus on fixing and learning**

## Escalation Matrix

| Situation | Action |
|-----------|--------|
| Single component broken (e.g., reports) | Disable component; continue with workaround |
| Multiple components broken | Full rollback |
| Database corruption | Restore from backup snapshot |
| Security breach | Page security team; notify legal |
| Prolonged outage (> 1 hour) | Executive stakeholder notification |

## On-Call Rotation

**First week post-launch:**
- 24/7 on-call including weekends
- 24-hour shifts if possible

**Ongoing:**
- Business hours: support lead on-call
- After hours: rotating engineer on-call
- Escalation: incident commander on 30-min response SLA

**Contacts:**
- PagerDuty: [link]
- Incident commander contact: [phone/email]
- Vendor support (AWS/hosting): [account contact]

## Tools & Access

Ensure all incident responders have:
- [ ] PagerDuty access
- [ ] Slack #incident channel
- [ ] Grafana dashboards
- [ ] Sentry project access
- [ ] SSH/kubectl access to production
- [ ] Database admin credentials (vaulted, not in email)
- [ ] Container registry credentials
- [ ] Status page admin access

## Incident Log

Maintain a shared spreadsheet (Google Sheets or Jira):

| Date | Time | Severity | Issue | Duration | RCA Owner | Status |
|------|------|----------|-------|----------|-----------|--------|
| 2026-03-01 | 09:15 | P2 | DB connection leak | 23 min | [engineer] | Closed |

---

## Quick Runbook: "App is down"

1. **Confirm:** Check status page, Grafana, try accessing app
2. **Declare:** Open war room, post "#incident-p1-[timestamp]"
3. **Check:** Recent deployment? DB up? Disk full?
4. **Act:** Restart app → if no joy, rollback → if no joy, restore DB
5. **Verify:** Health endpoint, login, create entry
6. **Communicate:** Update status page + send email
7. **Analyze:** Post-mortem within 24 hours

**Timeboxes:**
- Triage: 2 min
- First action: 5 min
- Resolution target: 30 min (P1)
- Communication: continuous

---

*Keep this playbook accessible to on-call team; rehearse monthly.*
