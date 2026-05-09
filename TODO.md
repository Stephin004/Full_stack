# TODO - Project & Task Management Web App (Django + DRF + React)

- [ ] Create project scaffolding: backend/ and frontend/ directories
- [ ] Initialize Django project (config/) and apps: accounts/, projects/, tasks/
- [ ] Configure settings: custom User model, DRF, JWT, CORS, drf-spectacular
- [ ] Implement models: Project, Membership (RBAC per-project), Task
- [ ] Implement serializers with business validation (due_date, membership checks)
- [ ] Implement permissions: Member vs Admin per project, secure object-level checks
- [ ] Implement viewsets + routers for projects, project members, tasks
- [ ] Implement dashboard endpoint (aggregates + overdue counts)
- [ ] Add API docs endpoints (Swagger UI via drf-spectacular)
- [ ] Add backend tests for RBAC + validation
- [ ] Create React frontend (Vite + Tailwind + Router), auth flows, pages
- [ ] Wire Axios with JWT + refresh interceptor
- [ ] Add frontend role-aware UI (backend remains secure boundary)
- [ ] Update README.md with full setup, endpoints, ER diagram, screenshots placeholders
- [ ] Add Railway deployment files (Procfile, runtime.txt optional)
- [ ] Run backend migrations and tests locally
- [ ] Run frontend build locally

