# Control-M Self-Service Portal — Phase 1

Starter scaffold: FastAPI + SQLAlchemy + PostgreSQL, with Control-M 9.0.21 individual-job Hold/Release API client.

## Confirmed API contract
- Base URL: `https://<Control-M-EM-host>:8443/automation-api` (confirm host/port locally)
- Hold: `POST /run/job/{jobId}/hold`
- Release: `POST /run/job/{jobId}/free`
- Auth header: `x-api-key: <token>`
- `jobId` must be the active instance identifier `<Control-M server>:<order ID>`; URL-encode it.

Verify your installed patch level and local Swagger at `<base-url>` before enabling writes. If action annotation is enabled, supply required annotation headers.

## Setup
1. Use an approved Python 3.11+ runtime and PostgreSQL instance.
2. `python3 -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `cp .env.example .env`, then fill values locally. Never commit `.env` or tokens.
5. Create DB/role through your DBA process.
6. `psql "$DATABASE_URL" -f sql/schema.sql`
7. `uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`
8. Visit `/health` and `/docs`.

## Important implementation gates
- The `X-Dev-User` header is a localhost-only development stub, not authentication. Replace with LDAP/SSO middleware before shared use.
- Application ACL enforcement is deliberately fail-closed until AD group membership is implemented.
- Job browsing reads PostgreSQL; this scaffold does not invent a daily catalogue API response. Implement refresh only after verifying the exact API response on your 9.0.21 instance.
- Individual job Hold/Release calls are implemented. Folder actions must preview selected active instances and execute each job with per-job results; do not assume a folder-level endpoint.
- API acceptance is not final-state confirmation. Add a verified status query/reconciliation loop before treating requests as completed. Timeouts are marked UNKNOWN and must not be blindly retried.
- TLS verification is enabled. Configure a trusted CA bundle rather than disabling verification.
