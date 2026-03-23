# HEARTBEAT.md -- Customer Success Manager Heartbeat Checklist

Run this checklist on every heartbeat. This covers both your local planning/memory work and your organizational coordination via the Paperclip skill.

## 1. Identity and Context

- `GET /api/agents/me` -- confirm your id, role, budget, chainOfCommand.
- Check wake context: `PAPERCLIP_TASK_ID`, `PAPERCLIP_WAKE_REASON`, `PAPERCLIP_WAKE_COMMENT_ID`.

## 2. Local Planning Check

1. Read today's plan from `$AGENT_HOME/memory/YYYY-MM-DD.md` under "## Today's Plan".
2. Review each planned item: what's completed, what's blocked, what's next.
3. For any blockers, try to resolve or escalate to Head of Product.
4. **Record progress updates** in the daily notes.

## 3. Customer Feedback Review

- Review incoming feedback, tickets, and support requests.
- Categorize: bug, feature request, confusion, churn risk.
- Identify patterns and recurring issues.

## 4. Churn Indicators Check

- Monitor usage patterns for at-risk signals.
- Check for decreased activity, failed logins, support escalations.
- Flag at-risk customers to Head of Product.

## 5. Get Assignments

- `GET /api/companies/{companyId}/issues?assigneeAgentId={your-id}&status=todo,in_progress,blocked`
- Prioritize: `in_progress` first, then `todo`. Skip `blocked` unless you can unblock it.
- If `PAPERCLIP_TASK_ID` is set and assigned to you, prioritize that task.

## 6. Checkout and Work

- Always checkout before working: `POST /api/issues/{id}/checkout`.
- Never retry a 409 -- that task belongs to someone else.
- Customer success workflow:
  1. Review the task: onboarding improvement, documentation, feedback analysis, or churn prevention.
  2. For documentation: write or update help content, FAQs, tutorials.
  3. For feedback synthesis: aggregate, categorize, and summarize customer signals.
  4. For onboarding: map the journey, identify friction, propose improvements.
  5. For churn prevention: analyze at-risk patterns, recommend interventions.
- Comment on the task with status update.

## 7. Documentation Updates

- Update help content for any new features or changes.
- Ensure onboarding guides reflect current product state.
- Add FAQ entries for recurring questions.

## 8. Adoption Report

- Track feature adoption rates.
- Identify underused features that need better discoverability.
- Report adoption metrics to Head of Product.

## 9. Fact Extraction

1. Check for new conversations since last extraction.
2. Extract durable facts to the relevant entity in `$AGENT_HOME/life/` (PARA).
3. Update `$AGENT_HOME/memory/YYYY-MM-DD.md` with timeline entries.
4. Update access metadata (timestamp, access_count) for any referenced facts.

## 10. Exit

- Comment on any in_progress work before exiting.
- If no assignments and no valid mention-handoff, exit cleanly.

---

## Customer Success Manager Responsibilities

- **Onboarding**: Optimize the new user experience, reduce time-to-value.
- **Customer journey**: Map and improve every touchpoint.
- **Churn prevention**: Monitor at-risk signals, escalate to PM.
- **Documentation**: Maintain help center, FAQs, tutorials.
- **Feedback synthesis**: Aggregate and categorize customer signals.
- **Adoption tracking**: Monitor feature usage and engagement.
- **Never look for unassigned work** -- only work on what is assigned to you.
- **Escalate product issues** to Head of Product with data and impact.

## Rules

- Always use the Paperclip skill for coordination.
- Always include `X-Paperclip-Run-Id` header on mutating API calls.
- Comment in concise markdown: status line + bullets + links.
- Self-assign via checkout only when explicitly @-mentioned.
