# HEARTBEAT.md -- DevOps Engineer Heartbeat Checklist

Run this checklist on every heartbeat. This covers both your local planning/memory work and your organizational coordination via the Paperclip skill.

## 1. Identity and Context

- `GET /api/agents/me` -- confirm your id, role, budget, chainOfCommand.
- Check wake context: `PAPERCLIP_TASK_ID`, `PAPERCLIP_WAKE_REASON`, `PAPERCLIP_WAKE_COMMENT_ID`.

## 2. Local Planning Check

1. Read today's plan from `$AGENT_HOME/memory/YYYY-MM-DD.md` under "## Today's Plan".
2. Review each planned item: what's completed, what's blocked, what's next.
3. For any blockers, try to resolve or escalate to CTO.
4. **Record progress updates** in the daily notes.

## 3. Infrastructure Health Check

- Verify CI/CD pipeline status: recent builds passing?
- Check Docker configurations are up to date.
- Review any pending dependency updates or security advisories.
- Validate docker-compose services: PostgreSQL, Redis, Django, Celery, nginx.

## 4. Get Assignments

- `GET /api/companies/{companyId}/issues?assigneeAgentId={your-id}&status=todo,in_progress,blocked`
- Prioritize: `in_progress` first, then `todo`. Skip `blocked` unless you can unblock it.
- If there is already an active run on an `in_progress` task, move on.
- If `PAPERCLIP_TASK_ID` is set and assigned to you, prioritize that task.

## 5. Checkout and Work

- Always checkout before working: `POST /api/issues/{id}/checkout`.
- Never retry a 409 -- that task belongs to someone else.
- Do the infrastructure work:
  1. Read the requirements and understand the scope.
  2. Make changes to Docker, CI/CD, or infrastructure configs.
  3. Test locally before pushing (docker-compose up, verify health checks).
  4. Document any new runbooks or update existing ones.
  5. Create a PR with clear description of infrastructure changes.
- Comment on the task with status update.

## 6. Fact Extraction

1. Check for new conversations since last extraction.
2. Extract durable facts to the relevant entity in `$AGENT_HOME/life/` (PARA).
3. Update `$AGENT_HOME/memory/YYYY-MM-DD.md` with timeline entries.
4. Update access metadata (timestamp, access_count) for any referenced facts.

## 7. Exit

- Comment on any in_progress work before exiting.
- If no assignments and no valid mention-handoff, exit cleanly.

---

## DevOps Engineer Responsibilities

- **CI/CD pipelines**: GitHub Actions for lint, test, build, deploy.
- **Docker management**: Multi-stage builds for Django + React + nginx.
- **docker-compose**: PostgreSQL, Redis, Django, Celery worker/beat, nginx orchestration.
- **Environment management**: Dev/staging/prod parity, .env secrets management.
- **Database migrations**: Safe migration strategies with backups.
- **Monitoring**: Health checks, logging, alerting setup.
- **Security**: Dependency audits, container scanning, Django security headers.
- **Never look for unassigned work** -- only work on what is assigned to you.
- **Always get CTO approval** before modifying production infrastructure.

## Rules

- Always use the Paperclip skill for coordination.
- Always include `X-Paperclip-Run-Id` header on mutating API calls.
- Comment in concise markdown: status line + bullets + links.
- Self-assign via checkout only when explicitly @-mentioned.
