# Shahm Technical Documentation

```text
docs/
├── API_PUBLIC_DOC.md
├── API_DASHBOARD_DOC.md
├── API_CONTRACT_MATRIX.md
├── API_CONTRACT_MATRIX.json
├── ARCHITECTURE.md
├── CODEBASE_MAP.md
├── FINAL_SMOKE_TESTS.md
└── HANDOFF.md
```

- [Public API](API_PUBLIC_DOC.md): anonymous and temporary-access REST API.
- [Dashboard API](API_DASHBOARD_DOC.md): JWT-authenticated management REST API.
- [Architecture](ARCHITECTURE.md): runtime topology and major flows.
- [Codebase map](CODEBASE_MAP.md): where common changes belong.
- [API contract matrix](API_CONTRACT_MATRIX.md): generated frontend-to-resolver verification; JSON is provided for tooling.
- [Operational handoff](HANDOFF.md): setup, validation, migration, deployment, and external-service checklist.
- [Final smoke tests](FINAL_SMOKE_TESTS.md): manual staging acceptance matrix for public, dashboard, dynamic, and email flows.

Django URL configuration is the source of truth. Start at `config/urls.py`, follow every `include()`, and inspect router registrations and view permissions under `apps/`.

## Project Attribution

Project source developed by **ENG. FAHAD ALSHWIHANI**. Portfolio: [fyaa.io](https://fyaa.io) · [GitHub](https://github.com/FahadAlshwihani) · [LinkedIn](https://www.linkedin.com/in/fahad-alshwihani/).

Copyright © 2026 ENG. FAHAD ALSHWIHANI.
