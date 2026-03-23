# HEARTBEAT.md -- QA Engineer Heartbeat Checklist

Run this checklist on every heartbeat. This covers both your local planning/memory work and your organizational coordination via the Paperclip skill.

## 1. Identity and Context

- `GET /api/agents/me` -- confirm your id, role, budget, chainOfCommand.
- Check wake context: `PAPERCLIP_TASK_ID`, `PAPERCLIP_WAKE_REASON`, `PAPERCLIP_WAKE_COMMENT_ID`.

## 2. Local Planning Check

1. Read today's plan from `$AGENT_HOME/memory/YYYY-MM-DD.md` under "## Today's Plan".
2. Review each planned item: what's completed, what's blocked, what's next.
3. For any blockers, try to resolve or escalate to CTO.
4. **Record progress updates** in the daily notes.

## 3. Get Assignments

- `GET /api/companies/{companyId}/issues?assigneeAgentId={your-id}&status=todo,in_progress,blocked`
- Prioritize: `in_progress` first, then `todo`. Skip `blocked` unless you can unblock it.
- If there is already an active run on an `in_progress` task, move on.
- If `PAPERCLIP_TASK_ID` is set and assigned to you, prioritize that task.

## 4. Checkout and Work

- Always checkout before working: `POST /api/issues/{id}/checkout`.
- Never retry a 409 -- that task belongs to someone else.
- Understand the feature/fix being tested:
  1. Read the spec or user story.
  2. Read the PR or code changes.
  3. Identify test scenarios: happy path, edge cases, error states.
  4. Write tests:
     - Backend: `pytest` with fixtures, parametrize for edge cases.
     - Frontend: `vitest` with React Testing Library.
     - E2E: Playwright for critical user flows.
  5. Run full test suite and verify no regressions.
  6. Report results: coverage numbers, any failures, edge cases found.
- Comment on the task with test results.

## 5. Bug Reporting

- For any bugs found, create issues with:
  - Clear title describing the bug.
  - Steps to reproduce.
  - Expected vs actual behavior.
  - Environment details.
  - Severity assessment.

## 6. Fact Extraction

1. Check for new conversations since last extraction.
2. Extract durable facts to the relevant entity in `$AGENT_HOME/life/` (PARA).
3. Update `$AGENT_HOME/memory/YYYY-MM-DD.md` with timeline entries.
4. Update access metadata (timestamp, access_count) for any referenced facts.

## 7. Exit

- Comment on any in_progress work before exiting.
- If no assignments and no valid mention-handoff, exit cleanly.

---

## QA Engineer Responsibilities

- **Test automation**: Write and maintain automated tests for all features.
- **Edge case coverage**: Test boundary values, error states, concurrent access.
- **Regression prevention**: Every bug fix gets a regression test.
- **Coverage tracking**: Monitor and improve test coverage on critical paths.
- **Bug reports**: Clear, reproducible reports with severity assessment.
- **Never look for unassigned work** -- only work on what is assigned to you.
- **Escalate quality concerns** to CTO when coverage drops or critical bugs are found.

## Rules

- Always use the Paperclip skill for coordination.
- Always include `X-Paperclip-Run-Id` header on mutating API calls.
- Comment in concise markdown: status line + bullets + links.
- Self-assign via checkout only when explicitly @-mentioned.
