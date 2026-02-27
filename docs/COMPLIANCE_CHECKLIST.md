# Accessibility, Privacy & Compliance Checklist

This document ensures the system meets legal, privacy, and accessibility standards.

## Accessibility (WCAG 2.1 Level A/AA)

### Automated Testing
Run tools (local or CI):
```bash
# Axe DevTools (browser extension or headless)
npm install -g @axe-core/cli
axe https://localhost:8000/admin/users/ --tags wcag2aa

# Lighthouse (Chrome DevTools or CLI)
lighthouse https://localhost:8000/admin/users/ --view
```

### Manual Testing Checklist

| Item | Status | Notes |
|------|--------|-------|
| **Keyboard navigation** | ?  | Can navigate all forms with Tab/Shift+Tab; no keyboard traps |
| **Color contrast** | ? | Text/background meets 4.5:1 for normal text, 3:1 for large text |
| **Images & icons** | ? | All have alt-text or aria-label; decorative images marked |
| **Forms** | ? | All inputs have associated labels; error messages clear |
| **Headings** | ? | Proper hierarchy (h1 → h2 → h3); no skips |
| **Focus indicators** | ? | Focus ring visible; not removed or hidden |
| **Page titles** | ? | Unique, descriptive titles for each page |
| **Skip links** | ? | "Skip to main content" available (useful for keyboard users) |

### Common Fixes
- Add `aria-label` to icon buttons
- Ensure form inputs have `<label>` elements
- Use semantic HTML: `<button>` not `<div role="button">`
- Test with screen reader (NVDA on Windows, VoiceOver on Mac)

### Tools
- Free: WAVE, Axe DevTools, Lighthouse, aXe-core
- Paid/Managed: Deque, accessibility.ai

## Privacy & Data Protection

### GDPR (if customers are in EU)
- [ ] Privacy policy published and linked from login page
- [ ] Data processing agreement (DPA) in place with customers
- [ ] User consent for cookies / tracking (if any)
- [ ] Right to access, delete, export data implemented
- [ ] Data retention policy defined (e.g., delete old data after 7 years)

**Note:** Django doesn't store cookies for analytics by default; confirm in settings.

### CCPA (if customers in California)
- [ ] Do-not-sell disclosure 
- [ ] Consumer rights (access, delete, opt-out) documented
- [ ] Third-party vendor list (if using external services)

### General Data Safety
- [ ] Encryption in transit (HTTPS enforced)
- [ ] Encryption at rest (DB and backups encrypted) — check with SRE
- [ ] Access logs: who/when accessed sensitive data
- [ ] Audit trails: track changes to critical data (e.g., journal entries, user roles)
- [ ] Backup/restore procedure documented (recovery time objective agreed with customers)

## Security Compliance

### SOC 2 / ISO 27001 (if applicable)
- [ ] Security policy documented
- [ ] Change management process (code reviews, deployments, approvals)
- [ ] Incident response plan (→ `docs/INCIDENT_RESPONSE.md`)
- [ ] Access control and RBAC reviewed
- [ ] Monitoring and logging in place (→ `docs/MONITORING_SETUP.md`)
- [ ] Vulnerability scanning (SCA, SAST) in CI/CD

### PCI DSS (if handling payment cards)
- [ ] **DO NOT store card data** — use Stripe/PayPal/Square
- [ ] Validate PCI compliance via third-party assessor if you touch card data

## Pre-Launch Compliance Checklist

### Product
- [ ] Privacy policy finalized and reviewed by legal
- [ ] Terms of service agreed
- [ ] Feature parity verified (all promised features working)

### Engineering
- [ ] No critical security vulnerabilities
- [ ] Automated tests passing
- [ ] Accessibility scan passing (no critical WCAG issues)
- [ ] HTTPS configured; SSL certificates valid

### Legal
- [ ] DPA signed with initial customers (if GDPR applies)
- [ ] Insurance reviewed (E&O, liability)
- [ ] Incident response insurance (cyber liability) in place

### Operations
- [ ] Backup and recovery tested
- [ ] Monitoring and alerting live
- [ ] Incident response team trained and on-call roster assigned
- [ ] Support processes in place (ticket system, escalation path)

## Post-Launch Audits (ongoing)

**Monthly:**
- Run accessibility scan; fix any regressions
- Review new compliance regulations (GDPR updates, new state laws)
- Spot-check user data access logs (ensure no unauthorized access)

**Annually:**
- Full accessibility audit (manual + tool-based)
- Security penetration test (if using contractor)
- Privacy impact assessment (PIA) for any new data collection
- Review data retention policy; purge old data if applicable

## Accessibility Fixes (quick wins)

1. **Profile page help text:**
   ```html
   <label for="email">Email <span aria-label="required">*</span></label>
   <input id="email" type="email" required>
   ```

2. **Icon buttons:**
   ```html
   <button aria-label="Help"><i class="fas fa-question"></i></button>
   ```

3. **Form validation:**
   ```html
   <div role="alert" class="error">{{ form.errors }}</div>
   ```

4. **Skip link (in base template):**
   ```html
   <a href="#main-content" class="skip-link">Skip to main content</a>
   <main id="main-content">
   ```

## Resources

- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/
- GDPR Checklist: https://gdpr.eu/
- CCPA Guide: https://oag.ca.gov/privacy/ccpa
- Accessibility testing tools: https://www.w3.org/WAI/test-evaluate/

---

*Assign compliance owner (likely product or legal) to maintain this checklist post-launch.*
