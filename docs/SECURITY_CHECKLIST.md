# Security Checklist & Audit Steps

This checklist covers initial security scans and remediation steps to run before launch.

## Scanning (local / CI)
- Dependency SCA (Software Composition Analysis):
  - Recommended: `pip-audit` or `safety` to scan for vulnerable packages.
  - Example:
    ```bash
    # install pip-audit in CI environment
    python -m pip install pip-audit
    pip-audit --format json > security/pip_audit.json
    ```
- Static analysis for Python:
  - `bandit` for common security issues
    ```bash
    pip install bandit
    bandit -r src/ -f json -o security/bandit.json
    ```
- Secrets scanning:
  - Use `git-secrets` or `truffleHog` in CI to prevent secrets in commits.

## Configuration checks
- Run Django security checks:
  ```bash
  python src/manage.py check --deploy
  ```
- Verify `DEBUG=False` in production and that `ALLOWED_HOSTS` is set.
- Ensure `SECRET_KEY` is stored securely (env or secret manager).

## Hardening
- HTTPS enforced, HSTS set, secure cookies (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`).
- CSP header and other security headers via Nginx or middleware.

## Access control
- Review admin access: restrict `is_superuser` accounts; use `django-admin` for privileged tasks.
- Rotate credentials for service accounts and DB users.

## Incident response
- Ensure Sentry (or equivalent) is configured for error reporting.
- Document escalation path and contact list in `docs/LAUNCH_READINESS.md`.

## Post-scan remediation
- Triage vulnerabilities by severity; for critical/high, stop the release until mitigated or compensating controls applied.
- For medium/low, schedule fixes and document acceptance criteria for deferred issues.

## Deliverables
- `security/pip_audit.json`, `security/bandit.json` stored as CI artifacts.
- A documented remediation plan for any discovered vulnerabilities.

*This is a practical checklist — adjust commands for your CI and deployment environment.*
