# Launch Readiness — TicTacFlow Accounting Portal

This document captures the final acceptance criteria, owners, and an initial launch runbook for production rollout.

## Feature Freeze
- Feature freeze date: TBD by Product (set as the date when all critical items are finished).
- Only critical bug fixes and security patches allowed after the freeze.
- All new features must be deferred to the next release unless explicitly approved by Product.

## Acceptance Criteria (must be satisfied before production rollout)
- Tests: All unit/integration tests pass in CI; critical end-to-end smoke tests pass on staging.
- Security: No outstanding critical or high severity vulnerabilities; SCA and static analysis reports reviewed.
- Performance: Staging load test shows acceptable p95 latency at expected concurrency.
- Database: Migrations reviewed; backup & restore procedure validated on staging.
- Observability: Error, latency and job backlog alerts configured and tested.
- Documentation: `docs/USER_GUIDE.md` published and in-app help available.
- Rollout Plan: Canary strategy and rollback playbook are documented.

## Owners & Contacts
- Product: [assign product owner]
- Engineering: [assign engineering lead]
- DevOps / SRE: [assign SRE lead]
- QA: [assign QA lead]
- Security: [assign security lead]
- Support: [assign support lead]

## Basic Rollout Timeline (example)
1. Feature freeze.
2. CI run: full test suite.
3. Security scan & fix.
4. Performance testing and tuning.
5. Deploy to staging and run smoke tests.
6. Canary rollout (internal users) for 24–72 hours.
7. Full production rollout.

## Critical Smoke Tests (to automate in CI/CD)
- User authentication (login/logout/register)
- Create journal entry and verify it's posted
- Generate Trial Balance report
- Create and delete a user (super-user)
- Create and delete an organization (super-user)

## Quick Checklist for Release
- [ ] Feature freeze declared
- [ ] CI: all tests green
- [ ] Security scan completed
- [ ] Performance tests completed
- [ ] Backups and restore validated
- [ ] Runbook & rollback documented
- [ ] Monitoring and alerts configured
- [ ] Support rota assigned

---

*This file is a living checklist; update owners, dates, and specific thresholds as the team finalizes the plan.*
