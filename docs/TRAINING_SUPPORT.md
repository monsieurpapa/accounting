# Training & Support Runbook

This document prepares the team and first-line support for launch.

## Quick Onboarding (30 min training)

**Audience:** End users, super-users, support staff

**Outline:**

### Part 1: System Overview (5 min)
- What is TicTacFlow? Modern, web-based accounting system.
- Key features: journals, entries, reports, budgets, cash flow.
- Access: browser login at `https://yourdomain.com/accounts/login/`

### Part 2: Primary Use Cases (15 min)
1. **Create a journal entry**
   - Navigate to Accounting → Journal Entries
   - Select journal, enter date/description and lines
   - Ensure debits = credits
   - Save (posted immediately or draft if needed)

2. **Generate a report**
   - Reporting → select Trial Balance / Income Statement / Balance Sheet
   - Choose fiscal year and period
   - Click Generate
   - Export to PDF or CSV

3. **Manage users** (super-users only)
   - Admin → Users
   - Add, edit, view details, delete users
   - Assign organization and role

### Part 3: Getting Help (5 min)
- **In-app help:** Click the floating Help button for context-sensitive tips
- **User guide:** Available in `Docs` or at `/docs/USER_GUIDE.md`
- **Support ticket:** Contact support@yourdomain.com with issue details
- **Status page:** Check `status.yourdomain.com` for system updates

## First-Line Support Runbook

### Common Issues & Resolutions

#### Login Problems
**User can't log in**
- Ask: Do they have an account? (Verify in admin dashboard)
- Check: Is their account active/not locked?
- Reset password via `/accounts/password/reset/` or admin dashboard
- **Escalate if:** Multiple users can't log in → check auth service / DB

#### Permission Denied on Admin Pages
**User sees "403 Forbidden" on Users or Organizations pages**
- Only super-users can access Admin
- Check: Is the user super-user? (View in Users list, look for admin badge)
- Workaround: Ask admin to grant `is_superuser` flag
- **Escalate if:** Super-user flag is set but still can't access → session/cache issue

#### Journal Entry Won't Save
**Entry shows "unbalanced" error**
- Sum of debits must equal sum of credits
- Walk through: add up debit lines and credit lines; ensure they match
- Add a correcting line if needed

**Entry saves but marked as "Draft"**
- Some organizations require approval before posting
- Contact super-user to post the entry

#### Report Shows No Data
**Trial Balance or Income Statement returns empty**
- Check: Are there posted journal entries? (Go to Journal Entries list)
- Check: Date range — did the entries fall within the selected period?
- Try expanding the date range to verify data exists
- **Escalate if:** Data exists but still missing on report → query issue

#### General Slowness / Timeouts
**Page takes > 5 seconds to load**
1. Check: Is the system status page showing issues? (Check `status.yourdomain.com`)
2. Suggest: Clear browser cache (Ctrl+Shift+Del)
3. Try: Retry in a different browser or incognito window
4. Ask: What is your internet speed? (Heavy reports with years of data may be slow)
5. **Escalate if:** Slow for multiple users at same time → infrastructure issue

#### Help Button Not Working
**Help panel doesn't open or shows generic text**
- Try: Refresh the page
- Check: Are we on a page with context-specific help? (Profile, Users list, Journals)
- **Escalate if:** Help button missing entirely → frontend issue

### Escalation Path

**L1 (Support):** Resolve common issues, reset passwords, check status
**L2 (Engineering):** Performance issues, permission bugs, data inconsistencies
**L3 (On-call SRE):** Infrastructure, database, deployment issues; incidents

**Escalation template (send to engineering):**
```
TICKET: [support-12345]
SEVERITY: [P1/P2/P3]
USER: [user@example.com]
ORG: [Organization Name]
ISSUE: [Clear description]
STEPS TO REPRODUCE:
1. ...
2. ...
EXPECTED: ...
ACTUAL: ...
ERROR MESSAGE: [if any, paste full traceback]
BROWSER/OS: [e.g., Chrome 120 on Windows 10]
TIME OF OCCURRENCE: [timestamp]
AFFECTED USERS: [count]
```

## Training Materials Template

### Slide Deck (PowerPoint / Google Slides)

**Slide 1:** Title
- TicTacFlow Accounting Portal
- [Today's Date]
- Your Organization

**Slides 2-5:** Screenshots showing:
1. Login page
2. Dashboard
3. Journal entry creation
4. Report generation

**Slide 6:** Getting Help
- In-app Help button
- User Guide link
- Support email
- Status page

**Slide 7:** Q&A

### Hands-on Lab (30 min, optional)

Provide a demo environment with pre-populated data.

1. Have trainees log in
2. Walk through creating a simple journal entry (with pre-filled accounts)
3. Generate a report together
4. Answer questions

**Key files to prep:**
- Demo data (accounts, journals, sample entries)
- Screenshot guide (step-by-step PDFs) 
- FAQs document

## Support Shift Coverage

Assign roles:
- **Launch day (Day 0):** All team members on-call, 24/7 support rotation
- **Day 1-3:** Dedicated support person + engineering on standby
- **Week 2+:** Normal support hours with escalation on-call

## Post-Launch Metrics (track daily for first 7 days)

| Metric | Target | Notes |
|--------|--------|-------|
| Avg support ticket response time | < 1 hour | First response |
| % tickets resolved L1 | > 70% | Reduces escalation |
| User satisfaction (NPS) | > 50 | If surveyed |
| System uptime | 99.9% | No unplanned downtime |
| Critical incidents | 0 | Data corruption, auth failures |

## Feedback Loop

Collect during first week:
- User survey: "What's confusing?" (via Typeform or email)
- Support ticket themes: common issues for docs updates
- Performance feedback: latency complaints, feature requests

Prioritize high-impact improvements for release 1.1.

## Knowledge Base (ongoing)

Maintain internally:
- FAQ document (copy support resolutions)
- Troubleshooting guide (screenshot-based)
- Known issues (time-bound, link to tracking)

Share portions with users in the Help panel and User Guide.

---

*Customize this runbook for your organization; add your support email, status page URL, and escalation list.*
