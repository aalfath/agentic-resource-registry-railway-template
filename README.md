# Deploy and Host Agentic Resource Registry on Railway

[Agentic Resource Registry](https://github.com/AgenticResourceRegistry/AgenticResourceRegistry) (formerly Observal) is a self-hosted, Apache-2.0 registry where a team shares and discovers coding agent resources: skills, agent files, MCP servers, hooks, prompts and sandboxes. It renders the right config for Claude Code, Cursor, Kiro, Codex, Pi, Copilot and OpenCode, and shows how each resource is used. This template runs version 1.17.1.

## About Hosting Agentic Resource Registry

The template runs the official images in five services. **Registry** is the web UI (nginx) on the public domain; it forwards `/api` to the **API** service over Railway's private network. **API** runs the FastAPI server and its background worker, and keeps its JWT signing keys on a volume at `/data`. Railway's **Postgres** holds users and the registry, **Redis** holds the job queue and caches, and **ClickHouse** (with a volume) stores session traces and the audit log. Migrations run on every start.

On first boot the API creates a super admin from `ADMIN_EMAIL` and a generated `ADMIN_PASSWORD`, so there's no open setup page and no demo account.

**After deploying:**

1. Open the Registry service's public URL.
2. Sign in with your `ADMIN_EMAIL` and the `ADMIN_PASSWORD` value from the **API** service's **Variables** tab. You can change the password on your account page.
3. Add your team in **Admin > Users**, then connect each harness with the CLI: `uv tool install observal-cli`, `observal auth login` (server `https://YOUR-DOMAIN`), `observal doctor patch`.

**Updates:** the template builds from [aalfath/agentic-resource-registry-railway-template](https://github.com/aalfath/agentic-resource-registry-railway-template), with every image pinned by version and digest. When a new version is tested and merged, Railway shows an update notice in your project and you choose when to apply it. Read [CHANGELOG.md](https://github.com/aalfath/agentic-resource-registry-railway-template/blob/main/CHANGELOG.md) first.

## Common Use Cases

* One internal catalogue of approved skills, agent files and MCP servers that every developer installs from, whatever coding agent they use
* Reviewing and approving submitted agent resources, with version diffs, before the team uses them
* Seeing which agents, tools and prompts are actually used, and replaying sessions to debug a failing one

## Dependencies for Agentic Resource Registry Hosting

* PostgreSQL and Redis (Railway's own, included)
* ClickHouse 26.6 (included, with a volume)

### Deployment Dependencies

* Source and releases: https://github.com/AgenticResourceRegistry/AgenticResourceRegistry/releases
* Self-hosting docs: https://github.com/AgenticResourceRegistry/AgenticResourceRegistry/tree/main/docs/self-hosting
* CLI (`observal-cli`): https://pypi.org/project/observal-cli/
* This template's source: https://github.com/aalfath/agentic-resource-registry-railway-template

### Implementation Details

| Service | Variable | What it does |
| --- | --- | --- |
| API | `ADMIN_EMAIL` | Asked at deploy. Email of the first super admin, created on first boot only. |
| API | `ADMIN_PASSWORD` | Generated. That admin's password. Changing it later has no effect: change it in the web UI. |
| API | `SECRET_KEY` | Generated. Signs sessions and encrypts stored secrets. Keep it with your backups. |
| API | `PUBLIC_URL` | `https://${{Registry.RAILWAY_PUBLIC_DOMAIN}}`. Set it to your custom domain if you add one. |
| API | `DATABASE_URL`, `REDIS_URL`, `CLICKHOUSE_URL` | References to the database services. |
| ClickHouse | `CLICKHOUSE_PASSWORD` | Generated. Password of ClickHouse's `default` user. |
| Registry | `API_HOST`, `API_PORT` | The API service on the private network. |

* Upstream's usage reporting is on by default: every six hours the API sends aggregate counts (no names, emails, prompts or code) to `usage.observal.io`. A super admin can turn it off in **Admin > Settings > Usage Reporting**.
* Health checks: `/healthz` on Registry and API. A crash exits non-zero, so Railway restarts the service.
* Single sign-on (OIDC, SAML, SCIM) is off until you set it up in **Admin > Settings** and **Admin > SSO**.
* Back up the Postgres database, the API's `/data` volume (JWT keys) and the ClickHouse volume.

## Why Deploy Agentic Resource Registry on Railway?

<!-- Recommended: Keep this section as shown below -->
Railway is a singular platform to deploy your infrastructure stack. Railway will host your infrastructure so you don't have to deal with configuration, while allowing you to vertically and horizontally scale it.

By deploying Agentic Resource Registry on Railway, you are one step closer to supporting a complete full-stack application with minimal burden. Host your servers, databases, AI agents, and more on Railway.
<!-- End recommended section -->
