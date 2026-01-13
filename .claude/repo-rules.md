# Repository Rules - AI Company

## Commit Convention
- Type: feat|fix|docs|style|refactor|test|chore
- Format: type(scope): message
- Example: feat(agent): add HR agent service

## Branch Strategy
- Main: main
- Feature: feature/{backlog-keyword}
- Bugfix: bugfix/{issue-id}

## Project Structure
```
ai_company_test/
├── frontend/          # Next.js 15+ (App Router)
│   ├── src/
│   │   ├── app/       # App Router pages
│   │   ├── components/
│   │   ├── lib/
│   │   └── types/
│   └── package.json
├── backend/           # FastAPI (Python 3.11+)
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── models/    # SQLAlchemy models
│   │   ├── services/  # Business logic
│   │   └── schemas/   # Pydantic schemas
│   ├── tests/
│   └── pyproject.toml
├── docs/              # Project documentation
├── docker-compose.yml
└── .claude/           # Claude skills & rules
```

## Lint Rules
- Frontend: ESLint + Prettier
- Backend: Ruff + Black + mypy

## Test Commands
- Frontend Unit: pnpm test
- Backend Unit: pytest
- E2E: pnpm test:e2e (Playwright)

## CI Checks Required
- Lint pass (frontend + backend)
- Tests pass (unit + integration)
- Build success
- Type check pass

## Technology Stack
- Frontend: Next.js 15+, TypeScript, Tailwind CSS, Zustand
- Backend: FastAPI, SQLAlchemy, Pydantic
- Database: PostgreSQL 16+
- AI: Claude API (Anthropic)
- Real-time: SSE or WebSocket
