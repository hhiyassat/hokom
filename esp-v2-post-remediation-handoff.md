# ESP v2 — Platform & Services Handoff (Post-Remediation)

**Date:** 2026-07-31
**Repository HEAD:** `a4224fcceff08a73d7c348b4a3324417fe66a413` on `remediation/architecture-security-production-readiness`
**Baseline compared against:** `41e27a3a53b14da115ec63d72d9d97b6e9f535d4` (original review baseline)
**Purpose:** replace the 2026-07-30 handoff. This document reflects the repository **as inspected**, not as described in commit messages.

---

## 1. Exact branch and commit

```
Branch:         remediation/architecture-security-production-readiness
HEAD:           a4224fcceff08a73d7c348b4a3324417fe66a413
Short:          a4224fc
Commits since 41e27a3: 26
Untracked user work preserved: 8 top-level + 12 files under docs/التعليمات/
Not pushed. Not tagged. Not merged into main.
```

## 2. Worktree state

```
Tracked modifications: 0
Staged modifications:  0
Untracked (all user-owned, preserved):
  backend/dain-out-saleh.txt                                         (600KB Arabic linguistics dump; not project material)
  docs/JEA_screen_field_service_matrix_v2_audited_RTL_fixed.xlsx     (JEA reference)
  docs/data-base-all-services .jpeg                                  (JEA reference)
  docs/flowchart-فحص-التربة.jpeg                                     (JEA reference)
  docs/handoffs/2026-07-30_esp-v2-platform-and-services-handoff.md   (previous handoff — contains session-1 test-count corrections in the working copy, uncommitted)
  docs/التعليمات/                                                    (12 CSVs + 2 .md + 1 .xlsx JEA canonicalization batch)
  docs/تدقيق_الكتروني.pptx                                           (JEA reference)
  docs/كتاب_التعليمات_الفنية_2025.pdf                                (JEA reference PDF)
```

## 3. Framework and runtime versions

```
PHP           8.5.7 (composer.json requires ^8.3)
Composer      2.10.1
Laravel       ^13.8
Node.js       v22.22.0
npm           10.9.4
React         ^18.2.0
TypeScript    ^5.2.2
Vite          ^5.0.0
Vitest        ^4.1.10
@tanstack/react-query  ^5.101.2
Sanctum       * (config/sanctum.php now published with expiration=480)
PHPUnit       12 (uses PHPUnit\Framework\Attributes\DataProvider)
```

## 4. Actual tested databases (this audit)

```
SQLite in-memory  — PASS  864 tests / 860 passed / 4 skipped / 2882 assertions / 107.1s
PostgreSQL 15     — PASS  864 tests / 863 passed / 1 skipped / 2890 assertions / 103.0s (Docker container esp-pg-audit:55433)
MySQL 8           — NOT_EXECUTED
```

## 5. Actual test counts (this audit)

```
Backend PHPUnit:  864 tests, 2882 assertions (sqlite); 2890 (postgres)
Frontend Vitest:  67 files, 438 tests, 0 failures
Playwright E2E:   12 tests, 12 passed, 23.9s
PHPStan:          0 errors
```

## 6. Repository tree (top level)

```
esp-v2/
├── ARCHITECTURE.md              (STUB per BUILD_CONTRACT.md:31 — points at docs/architecture/*)
├── BUILD_CONTRACT.md            (Laravel 13 / PHP 8.3+ / Postgres — reconciled)
├── METHODOLOGY_AUDIT.md         (Laravel 13 — reconciled)
├── README.md                    (Laravel 13 / PHP 8.3+ — reconciled)
├── REQUIREMENTS.md              (still contains OTP + MP4 + autosave clauses — see DR-01..03)
├── RTM.md                       (STUB per BUILD_CONTRACT.md:31)
├── Dockerfile                   (multi-stage; missing nginx.conf + supervisord.conf; not built end-to-end this audit)
├── docker-compose.yml           (validates via `docker compose config`; not run end-to-end)
├── backend/                     Laravel 13 API
│   ├── app/                     PLATFORM (business-neutral; 0 Modules\Jea imports)
│   ├── config/                  22 config files + policy.esp-v2.yml (unused)
│   ├── database/                Platform migrations + seeders + factories
│   ├── modules/                 JeaServices, JeaProjects, JeaDues, JeaDiscipline
│   ├── plugins/                 AiSchema, Captcha
│   ├── integrations/            Gsb, Nashmi
│   ├── routes/                  api.php (109 lines) + console.php (94 lines)
│   ├── tests/                   93 test files + Architecture suite + Concurrency suite
│   └── bootstrap/, public/, resources/
├── frontend/                    React 18 / TS 5 / Vite
│   └── src/                     67 test files; 438 tests
├── e2e/                         Playwright — 8 spec files, 12 tests
├── mcp/                         (not inspected in this audit)
├── performance/                 k6/smoke_test.js + README
├── deployment/                  env.production.template + supervisor/queue-worker.conf
├── .github/workflows/ci.yml     backend (sqlite) + backend-postgres + frontend + e2e jobs
└── docs/                        architecture/ (15+ files), adr/ (2 files), handoffs/, remediation/, plus SECURITY_CONTROLS.md, BUSINESS_RULES_REGISTER.md, DECISION_REGISTER.md, EDA_DECISION_CHAIN.md
```

## 7. Platform backend ownership (`backend/app/`)

- **Providers** (`Providers/*`): `AppServiceProvider` (rate limiters + Gsb DI + Mock payment gateway non-prod + ProductionSafety enforce); `StorageServiceProvider` (aborts prod boot on non-object-storage); `ModulesServiceProvider`, `PluginsServiceProvider`, `IntegrationsServiceProvider` (config-driven registration).
- **Models** (`Models/*`): `User` (roles, canManageUsers, canManageRole, canEditServices=admin-only, isReviewer excludes superuser); `Organization` (tenant root; JEA relations REMOVED); `AuditLog`; `Notification` (uses `BelongsToOrganization` trait since L-10); `Concerns/{OrganizationScope, BelongsToOrganization}` (H-01 null-org fail-closed).
- **Controllers** (`Http/Controllers/Api/*`): `AuthController` (login/register/logout/me/password-change + SecurityEvents emitters); `UserManagementController`; `AdminDashboardController` (only `auditLogs` — JEA dashboard moved out); `HealthController` (L-12 `/api/ready`); `NotificationController` (per-user inbox).
- **Middleware** (`Http/Middleware/*`): `SecurityHeaders`, `CorrelationId`, `LogApiAccess` (reads correlation_id from attribute bag — L-11 fixed), `ReadTokenFromCookie`, `TokenInactivityCheck` (session_timeout via env — L-04 not fixed), `EnforcePasswordPolicy` (password_expiry via env — L-04 not fixed), `CheckRole` (emits SecurityEvents::authorizationDenied), `TrackUserActivity`.
- **Concerns** (`Http/Concerns/*`): `RequiresAdminTier` (arabic message wrong — NEW-A9). `RespondsWithLockedService` moved OUT to JEA.
- **Contracts** (`Contracts/`):
  - `Applications/{ApplicationLookup, ApplicationSnapshot}` — bound but **ZERO production consumers** (NEW-A3).
  - `Services/{ServiceLockLookup, ServiceDefinitionSnapshot}` — bound; consumed by AiSchemaController (via ServiceLockLookup) and Nashmi (via dead `pushService()` only — NEW-A5).
- **Services** (`Services/*`):
  - `Payment/{PaymentGateway, PaymentIntent, PaymentInitiation, PaymentReceipt, MockPaymentGateway}` — **0 production consumers** (NEW-A2). PaymentsController does NOT resolve any of these.
  - `Notifications/NotificationService` — slimmed to platform-neutral `sendToUser` + `dispatch`. JEA emitters moved.
- **Support** (`Support/*`): `ProductionSafety` (13 checks; **NEW-A1 config-key typo in checkNashmiSigningSecret**); `SecurityEvents` (7 emitters wired at auth + CheckRole + Nashmi; `paymentCallbackFailure` has 0 callsites; `tokenRevoked` missing at TokenInactivityCheck timeout); `PasswordPolicy` + `PasswordHistory` (P1-08).
- **Jobs** (`Jobs/`): `ProcessNotificationJob` — **0 production dispatchers** (H-10 scaffold-only).
- **Console/Commands** (`Console/Commands/*`): `AuditLogPrune`, `NotificationsPrune`, `UserCredentials`.
- **Rules** (`Rules/*`): `PdfOrDwgFile` (magic-byte + extension).

## 8. Platform frontend ownership (`frontend/src/`)

- **Routes** (`routes.tsx`, 131 lines): 32 lazy-imported pages + guards.
- **Layout** (`layout/*`): `Header`, `Sidebar`, `RouteSuspense`, `navItems.tsx` (role-based nav; hard-coded route strings).
- **Auth** (`auth/*`): `AuthProvider`, guards.
- **Components** (`components/ui/*`): **contains JEA-specific widgets** (QuotaCard, PhaseBadge, WorkflowStepper, ExpiryBadge, ServiceInfoCard, ComplianceNotesBanner, RolePathBadge, ManualReferenceIcon) — L-01 not fixed. Only `Captcha.tsx` is domain-neutral.
- **Platform** (`platform/*`): `ErrorBoundary`, `LanguageSwitcher`, `NotificationBell`, `Bilingual`, `Button`, `FormField`, `Modal`, `ConfirmDialog`, `PageHero`, `SkipToContent`. **`ReportsPanel.tsx` imports JEA types from `types/index.ts`** — L-08 not fixed.
- **Engine** (`engine/*`): `DynamicForm` (513 LOC), `DocumentUploader`, `DocumentPreviewCard`, `workflowRolePath`.
- **API** (`api/*`): `client.ts`, `http.ts`, `tokenStorage`, `queryClient`; per-domain files (`auth.ts`, `notifications.ts`, `users.ts` = platform; `applications.ts`, `projects.ts`, `engineers.ts`, `myOffice.ts`, `officeRegistrations.ts`, `review.ts`, `services.ts` = JEA). Nested `api/platform/{admin,hooks}.ts` + `api/jea/{admin,hooks}.ts`. Root `admin.ts` + `hooks.ts` are documented back-compat barrels.
- **Types** (`types/*`): `platform.ts`, `jea.ts`, `index.ts` (barrel export both). `types/index.ts` barrel intentionally retained for back-compat.
- **i18n** (`i18n/locales/*.json`): 477 AR keys / 477 EN keys, aligned.
- **Test setup** (`test/setup.ts` + Vitest config).

## 9. Every backend module

### 9.1 JeaServices (central JEA module)

- **Models**: `Application`, `ApplicationDocument`, `ApplicationReview`, `ApplicationCounter` (new H-02), `Certificate`, `CertificateCounter`, `ServiceDefinition`, `ManualReference`, `OfficeRegistrationRequest`.
- **Controllers**: `ApplicationController` (index/store/update/submit/uploadDocument/downloadDocument), `ReviewQueueController` (queue/claim/release/decide), `ReviewDashboardController`, `PaymentsController` (confirm — takes payment_reference string, does NOT use PaymentGateway abstraction), `CertificatesController` (issue/verify/downloadPdf/downloadPdfAuthenticated — P1-10), `ServiceCatalogController`, `ServiceFeesController`, `ManualReferenceController`, `OfficeRegistrationController` (submit/index/show/approve/reject; writes `Modules\JeaProjects\Engineer` — NEW-A18), `JeaAdminDashboardController` (dashboard + allApplications — session-3 extraction).
- **Engines** (`Engine/*`, 22 files): `WorkflowEngine` (738 LOC — M-17 not fixed); `CrossCuttingSubmissionPipeline` (advisory-lock cadastral guard C-04); `CadastralConflictGuard`; `OwnerMatchClearanceGuard`; `CadastralPriorApplicationLookup` (portable Eloquent — C-05); `Srv001Guard`; `SchemaValidator`; `SchemaStructureValidator`; `StageActions`; `FeeCalculator`; `NetDepthTable`; `WellsCountCalculator`; `ExplorationRequirementMatrix`; `GridSystemResolver` (**DEAD** — NEW-A4); `MultiBuildingResolver` (**DEAD** — NEW-A4); `OfficeRegistrationValidator`; `HttpJeaMembershipVerifier` (C-03 skeleton); `FakeJeaMembershipVerifier`; `JeaMembershipVerifier` (interface); `JeaMembershipResult`; `ServiceSubmissionGuard{Registry}`; `CrossCuttingSubmissionGuard` (interface).
- **Services** (`Services/*`, 3 files): `JeaNotificationService` (JEA-shaped emit* methods — session-3 extraction); `EloquentServiceLockLookup`; `EloquentApplicationLookup` (**0 consumers** — NEW-A3).
- **Concerns**: `RespondsWithLockedService` (session-3 move from Platform).
- **Requests**: `SubmitOfficeRegistrationRequest` (unused JeaMembershipVerifier import — DC-12).
- **Providers**: `JeaServicesServiceProvider` (binds pipeline + registry + verifier + ServiceLockLookup + ApplicationLookup).
- **Migrations** (16): applications, application_documents, application_reviews, application_counters, service_definitions, certificates, certificate_counters, manual_references, office_registration_requests, add_cadastral_columns, add_office_registration_fks, various column adds.
- **Seeders** (7 including `ServicePlan2026Seeder`; `JeaDrawingsSeeder` deleted per session 1).

### 9.2 JeaProjects

- **Models**: `Project`, `Engineer`, `OfficeCoalition`, `OfficeCoalitionMember`, `OfficeCeiling`, `QuotaConsumption`, `EngineerDisciplineQuota`.
- **Controllers**: `ProjectController` (index/show/store/quota), `EngineerController` (index/show/store/quota), `OfficeSettingsController` (admin surface).
- **Engines**: `QuotaLedger` (reads `Modules\JeaServices\Models\Application` — SM allowlisted); `CapacityGuard` (same); `Disciplines` (enum).
- **Support**: `OfficeCoalitionResolver` (H-08 lift from Platform User).
- **Migrations**: 8 including engineers, projects, office_coalitions/members, quotas/ceilings.
- **Seeders**: DemoEngineers, GovernmentSurveyQuota, MaterialsTestingQuota, QuotasAndCeilings, SampleProjects.

### 9.3 JeaDues

- **Models**: `RecurringObligation`.
- **Controllers**: `MyDuesController`, `RecurringDuesController` (admin surface).
- **Services**: `RecurringDuesService`.
- **Commands**: `OpenAnnualDues` (scheduled Feb 1 04:00).
- **Migrations**: 1 (`create_recurring_obligations_table`).
- **Cross-module coupling**: ZERO. Cleanest module.

### 9.4 JeaDiscipline

- **Models**: `Complaint`, `Sanction`, `LegalFine`, `SupervisionTransfer` (LegalFine + SupervisionTransfer FK-belongsTo `Modules\JeaServices\Models\Application` — SM allowlisted).
- **Controllers**: `ComplaintController` (intake + admin decide), `MyDisciplineController`, `LegalFineController`, `SupervisionTransferController`.
- **Engines**: `SanctionGuard` (cross-cutting submission guard — invoked via `app(\FQCN)` from `ApplicationController:318` — hidden coupling NEW-A6).
- **Services**: `SupervisionTransferService`.
- **Commands**: `RemindExpiries` (scheduled daily 05:00; resolves `JeaNotificationService` from container).
- **Migrations**: 3 (complaints/sanctions, legal_fines, supervision_transfers).

## 10. Every frontend module (`frontend/src/modules/*`)

- **JeaServices**: Apply.tsx (**663 LOC — M-16 not fixed**), ApplicationDetail.tsx (398 LOC), MyApplications, Dashboard, ReviewPanel, EditService, NewService, others.
- **JeaProjects**: ProjectsList, ProjectDetail, ProjectContextHeader (imported cross-module by JeaServices/Apply.tsx:13 — NEW-A8).
- **JeaDues**: OfficeDues.
- **JeaDiscipline**: ComplaintsAdmin, LegalFinesAdmin, SupervisionTransfersAdmin.

`frontend/src/pages/*` also contains `admin/`, `public/` route-level pages. `frontend/src/pages/applicant/ApplicationDetail.tsx` was **deleted** per session-1 remediation — verified gone.

## 11. Plugins

- **AiSchema** (`backend/plugins/AiSchema/`): `AiSchemaController` (generate/edit service schemas via Claude API). Consumes `App\Contracts\Services\ServiceLockLookup` (session-3 change). Rate limit `throttle:ai-schema` (10/hr per user).
- **Captcha** (`backend/plugins/Captcha/`): `VerifyCaptcha` middleware alias, `CaptchaController@issue`, `CaptchaService` (SVG generation, cache-backed).

Removing a plugin from `config/plugins.php` drops the routes + middleware alias cleanly.

## 12. Integrations

- **Gsb** (`backend/integrations/Gsb/`): `GsbController` (citizen OTP, citizen lookup, audit-logs), `GsbClient` (outbound HTTP with retry), `GsbAuthManager` (OAuth token cache), `GsbIpWhitelist` middleware (fail-closed prod — H-05), `GsbPruneLogs` command. **Outbound `GsbClient::isIpAllowed()` still permissive on empty allowlist — NEW-A20.**
- **Nashmi** (`backend/integrations/Nashmi/`): 6 `/api/integration/*` routes; `IntegrationController` (receive/notify/download); `ValidateIntegrationKey` middleware (HMAC + timestamp + optional nonce + IP allowlist — H-04); `NashmiIntegrationService` (`pushService` DEAD — NEW-A5; `notifyCodeDone` synchronous); `ProcessNashmiOutboundJob` (**0 production dispatchers** — H-10). `IntegrationCycle::count()+1` for cycle_ref (NEW-A16).

## 13. Shared contracts (`backend/app/Contracts/`)

| Contract | Impl | Consumers | Verdict |
|---|---|---|---|
| `Applications\ApplicationLookup` | `EloquentApplicationLookup` | **0 production consumers** | UNUSED (NEW-A3) |
| `Applications\ApplicationSnapshot` (DTO) | Only produced by `EloquentApplicationLookup::toSnapshot()` | 0 | UNUSED |
| `Services\ServiceLockLookup` | `EloquentServiceLockLookup` | AiSchemaController:829 | HEALTHY_REUSE (1 consumer) |
| `Services\ServiceDefinitionSnapshot` | Nashmi `pushService()` type-hint | 0 (pushService is dead) | UNUSED |

## 14. Queues / jobs

**Reality: scaffold only.**

| Job class | Prod dispatchers | Idempotency | Retries | Failed-job persistence |
|---|---|---|---|---|
| `App\Jobs\ProcessNotificationJob` | 0 (only `QueueJobsTest`) | none | 3 tries / 10s backoff | `failed_jobs` table NOT MIGRATED |
| `Integrations\Nashmi\Jobs\ProcessNashmiOutboundJob` | 0 (only `QueueJobsTest`) | none | 3 tries / 30s backoff | same |

`config/queue.php` code default is `database`; `.env.example`/`.env` set `sync`. **NO `create_jobs_table` migration exists** (NEW-A14) — any deploy using the code default 500s on first dispatch. `create_failed_jobs_table` also missing (NEW-A15) — `queue:failed` non-functional.

All work that session-3 claimed as async (notifications, Nashmi outbound, GSB, PDF rendering, bulk supervision transfers, annual dues, reminders) remains **synchronous in the HTTP request path**.

## 15. Security controls

Full inventory in `docs/SECURITY_CONTROLS.md` (authored 2026-07-31). Verified this audit:

- Identity & Access: session absolute lifetime 480 min (M-22); idle timeout 30 min; role tiers (superuser=user-mgmt only — C-01); RequiresAdminTier (arabic message wrong — NEW-A9).
- Session mgmt: httpOnly + SameSite=Strict cookie; secure-auto in prod; single-session on login.
- Password: min 12 + symbols + optional HIBP (P1-08); rolling history N=5.
- Authz / tenancy: `BelongsToOrganization` global scope; null-org fail-closed (H-01); cross-tenant negative tests for 11 endpoints. `EloquentApplicationLookup::find()` returns cross-org snapshots — callers must self-enforce (NEW-A13).
- Input validation: SchemaValidator; PdfOrDwgFile magic-byte + extension.
- Transport: HSTS, restrictive CSP, X-Frame-Options DENY, Permissions-Policy, Cache-Control no-store for /api/*.
- Integration security: Nashmi HMAC + timestamp + IP (nonce optional — NEW-A12); GSB IP fail-closed in prod (H-05) + PII log redaction (H-06); Payment/JEA verifier boot guards (C-02/C-03; **NEW-A1 blocks every prod boot**).
- Audit + observability: append-only AuditLog; retention pruner; dedicated `security` log channel (365-day retention); `SecurityEvents` emitters (paymentCallbackFailure has 0 callsites — NEW-A10; tokenRevoked not emitted from TokenInactivityCheck).
- Production safety: `ProductionSafety` 13-check validator wired into `AppServiceProvider::boot`. Note: `checkNashmiSigningSecret` reads WRONG config key (NEW-A1).

**6 categories of authenticated admin/decision endpoints are UNRATED** (NEW-A11) — including `auth/password/change` (brute-force pivot on stolen session).

## 16. Tenancy model

- Trait: `App\Models\Concerns\BelongsToOrganization` — global scope filters queries by `Auth::user()->organization_id`. Null-org authenticated users get `whereRaw('1 = 0')` (H-01).
- Trait applied to: Application, ApplicationDocument, ApplicationReview, Certificate, ServiceDefinition, Project, Engineer, OfficeCeiling, QuotaConsumption, EngineerDisciplineQuota, OfficeCoalitionMember, Complaint, Sanction, LegalFine, SupervisionTransfer, RecurringObligation, Notification (L-10 added).
- Explicit `withoutOrgScope()` sites: 8 production sites, all justified (Section 3 of audit).
- Cross-tenant negative tests: `CrossTenantIsolationTest` (11 assertions) + `CadastralConflictGuardTest` + `OwnerMatchClearanceGuardTest`.

## 17. Workflow model

- `WorkflowEngine::ALLOWED_TRANSITIONS` — single authority. 7 statuses: draft, submitted, under_review, modifications_requested, approved, rejected, certificate_issued.
- Every mutating public method wrapped in `DB::transaction` + writes `audit_logs` with `rule_id`.
- Submit path: FormRequest validation → `SchemaValidator` → `CrossCuttingSubmissionPipeline` (advisory lock + Cadastral + OwnerMatch guards) → `ServiceSubmissionGuardRegistry` → transition to first reviewer stage. Cross-cutting pipeline re-runs inside submit's own transaction (C-04 fix).
- Guards resolved via container: JeaProjects `QuotaLedger` + `CapacityGuard` + JeaDiscipline `SanctionGuard` (via `app(\FQCN::class)` — invisible to SiblingModuleBoundariesTest).

## 18. Payment model

- Interface `PaymentGateway::initiate(PaymentIntent): PaymentInitiation`; `verifyCallback(array): PaymentReceipt`; `refund(string, ?string): bool`.
- `MockPaymentGateway` bound in non-production only. In production ProductionSafety aborts boot when Mock resolves.
- **`PaymentsController::confirm` does NOT resolve `PaymentGateway` from the container** (NEW-A2). It accepts a plain `payment_reference` string via request validation and calls `WorkflowEngine::confirmPayment` directly. The entire PaymentGateway abstraction is currently unused scaffolding.

## 19. Document model

- Upload: `POST /applications/{id}/documents` — `PdfOrDwgFile` magic-byte + extension + 50MB cap → stored on `config('filesystems.default')` (S3 required in prod per ProductionSafety) → `ApplicationDocument::create`.
- Download: `GET /applications/{id}/documents/{docId}` (P1-09) — `findAccessible` + `no-store` + `nosniff` headers.

## 20. Database ownership

Full ownership table in Part 7 of `/tmp/esp-v2-post-remediation-audit.md`. Notable:
- `users` table CO-OWNED — Platform (2025_01_01_000002) + JeaProjects migration adds `annual_quota_m2` + boost flags (NEW-A19).
- `Engineer` model (JeaProjects) is written cross-module by `Modules\JeaServices\Http\Controllers\OfficeRegistrationController:135` (NEW-A18).
- `application_reviews` missing explicit `(reviewer_id, created_at)` index (NEW-A17) — Postgres does not auto-index FK columns.

## 21. Deployment assets

- `Dockerfile` — multi-stage (Node → PHP-FPM). **Missing nginx.conf + supervisord.conf**; `--no-gc` typo (should be `--no-cache`). ASSET_EXISTS, not runnable end-to-end. Full-stack docker build not proven in this audit.
- `docker-compose.yml` — `docker compose config` validates (obsolete `version:` warning only). Not exercised end-to-end.
- `deployment/env.production.template` — exists. Not validated.
- `deployment/supervisor/queue-worker.conf` — exists. No worker exercised (no jobs dispatched — see §14).
- `.github/workflows/ci.yml` — `backend` (sqlite) + `backend-postgres` (Postgres 15 service) + `frontend` + `e2e` jobs. This audit ran the Postgres pipeline locally via Docker; the CI job has not been observed running on a PR.

## 22. Observability

- Structured JSON access log: `LogApiAccess` middleware writes to `api_access` channel.
- Correlation IDs: `CorrelationId` middleware mints/echoes `X-Request-Id`; `LogApiAccess` reads from attribute bag (L-11 unified).
- `security` log channel (P0-E-2) — 365-day retention; emitters via `SecurityEvents`.
- Health probes: `/up` (liveness) + `/api/ready` (DB + cache round-trip — L-12).
- **NO metrics exporter** (Prometheus/OTel/StatsD).
- **NO error-reporting integration** (Sentry/Bugsnag/Rollbar).
- **NO tracing** (OpenTelemetry).

## 23. Performance assets

- `performance/k6/smoke_test.js` — session-3 executed (314 req / 0 fail / p95=51.9ms). Not re-run this audit.
- `performance/README.md` — exists.
- 16-scenario capacity plan from Phase 12 of the review: scaffolded only. Not executed.
- No `LoadTestSeeder` (needed for the 100k-application dataset).

## 24. Known external blockers (BLK-*)

Documented in `docs/DECISION_REGISTER.md`:

| ID | External input | Currently |
|---|---|---|
| BLK-01 | Real payment gateway provider + callback spec + credentials | ProductionSafety aborts boot |
| BLK-02 | JEA membership endpoint URL + auth + response schema | HttpJeaMembershipVerifier throws if base_url unconfigured |
| BLK-03 | Nashmi HMAC signing secret + rotation policy | ProductionSafety aborts on empty secret (but see NEW-A1) |
| BLK-04 | GSB IP allowlist values | Middleware fail-closed |
| BLK-05 | GitHub Actions CI run of the Postgres matrix job | Locally verified this audit against Docker Postgres |
| BLK-06 | Business decisions on OTP-only auth / MP4 uploads / autosave-to-cache | DECISION_REGISTER classifies each row |

## 25. Known internal residuals

The complete list is in `/tmp/esp-v2-post-remediation-findings.csv`. Most impactful:

**Critical:** NEW-A1 (Nashmi config-key typo blocks prod boot).

**High:** H-10 (queue scaffold-only); NEW-A2 (unused PaymentGateway abstraction); NEW-A3 (unused ApplicationLookup contract); NEW-A6/NEW-A7 (4 hidden `app(FQCN)` cross-module resolves invisible to boundary test).

**Medium/Low unremediated:** M-10 (office-reg captcha), M-14 (leading-% LIKE), M-16 (Apply.tsx God_Component), M-17 (WorkflowEngine split), L-01 (JEA widgets in components/ui), L-04 (env() bypass), L-06 (CORS credentials), L-08 (ReportsPanel JEA types), NEW-A4 (Grid+MultiBuilding resolvers dead), NEW-A5 (pushService dead), NEW-A17 (application_reviews index), NEW-A11 (unrated admin decision endpoints), NEW-A12 (Nashmi nonce optional).

## 26. Local development instructions

```bash
git clone <repo>
cd esp-v2

# Backend
cd backend
cp .env.example .env
composer install
php artisan key:generate
touch database/database.sqlite
php artisan migrate --seed          # sqlite; loads DemoSeeder — 4 demo users (admin/staff/auditor/applicant@demo.esp Demo1234!)
php artisan serve --port=8002

# Frontend (separate terminal)
cd ../frontend
npm ci
npm run dev                         # Vite on :5173

# Playwright E2E (from repo root, separate terminal)
npm ci                              # root npm for playwright deps
npx playwright install --with-deps chromium
npx playwright test

# Postgres full backend suite (requires Docker)
docker run -d --rm --name esp-pg-local -e POSTGRES_DB=esp_test -e POSTGRES_USER=esp -e POSTGRES_PASSWORD=esp -p 55432:5432 postgres:15-alpine
cd backend
DB_CONNECTION=pgsql DB_HOST=127.0.0.1 DB_PORT=55432 DB_DATABASE=esp_test DB_USERNAME=esp DB_PASSWORD=esp APP_ENV=testing php artisan test
docker stop esp-pg-local
```

## 27. Test commands

```bash
# Backend
cd backend
php artisan test                                    # sqlite in-memory
vendor/bin/phpstan analyse --memory-limit=1G
php artisan migrate:fresh && php artisan migrate:rollback

# Frontend
cd frontend
npm test
npm run typecheck
npm run build

# E2E
cd ..
npx playwright test

# Postgres (see §26)

# Real concurrency (Postgres required)
DB_CONNECTION=pgsql ... php artisan test --filter=RealConcurrencyOnPostgresTest
```

## 28. Production activation requirements

Before any deploy to `APP_ENV=production`:

1. **NEW-A1 must be fixed** — one-word edit in `backend/app/Support/ProductionSafety.php:191` (`integrations.nashmi.signing_secret` → `nashmi.signing_secret`). Otherwise every boot aborts.
2. Bind a real `PaymentGateway` implementation in a production ServiceProvider (BLK-01).
3. Bind `HttpJeaMembershipVerifier` (or another driver) once the JEA endpoint contract is available (BLK-02).
4. Set `NASHMI_SIGNING_SECRET` env; agree rotation policy with Nashmi ops (BLK-03).
5. Set `GSB_ALLOWED_IPS` env from MODEE (BLK-04).
6. Set `FILESYSTEM_DISK=s3` (or another object-storage driver) — StorageServiceProvider aborts otherwise.
7. Set `QUEUE_CONNECTION` to something other than `sync` (redis recommended). **Also add `create_jobs_table` + `create_failed_jobs_table` migrations if using the `database` driver — NEW-A14 / NEW-A15.**
8. Set `CACHE_STORE`, `SESSION_DRIVER` to non-file drivers.
9. Set `APP_DEBUG=false`, `SESSION_SECURE_COOKIE=true`, `SESSION_HTTP_ONLY=true`.
10. Set `SANCTUM_EXPIRATION_MINUTES` (default 480).
11. Set `CAPTCHA_ENABLED=true` (ProductionSafety enforces).
12. Set `PASSWORD_CHECK_COMPROMISED=true` (ProductionSafety enforces).
13. **Even after all the above, H-10 remains**: the two Job classes have no production dispatchers. Notifications and Nashmi outbound remain synchronous in the request thread.

## 29. Explicit non-production-safe adapters

- `App\Services\Payment\MockPaymentGateway` — non-prod only; PS aborts prod. Bound in `AppServiceProvider:56`.
- `Modules\JeaServices\Engine\FakeJeaMembershipVerifier` — non-prod only; PS aborts prod. Bound in `JeaServicesServiceProvider:113`.

## 30. Exact next engineering priorities

In order of risk:

1. **Fix NEW-A1** (`ProductionSafety::checkNashmiSigningSecret` reads wrong config key) — one line, blocks every prod boot.
2. **Wire H-10 async or delete Job classes** — the `ProcessNotificationJob` + `ProcessNashmiOutboundJob` exist but nothing dispatches them. Either dispatch from `JeaNotificationService::send()` and `NashmiIntegrationService`, add `create_jobs_table` + `create_failed_jobs_table` migrations, and switch `QUEUE_CONNECTION` to `redis` in production — or delete the Job classes as scaffolding.
3. **Decide PaymentGateway (NEW-A2)** — either delete the 5 files + `AppServiceProvider:56` binding + `ProductionSafety::checkPaymentGatewayBinding`, OR refactor `PaymentsController::confirm` to resolve `PaymentGateway::class`.
4. **Decide ApplicationLookup (NEW-A3)** — either migrate the 15 allowlisted files to consume the contract, OR delete the 3 files.
5. **Add captcha to office-registration submit (M-10)** — one-line middleware add.
6. **Delete GridSystemResolver + MultiBuildingResolver (NEW-A4)** or wire into Srv001Guard.
7. **Delete NashmiIntegrationService::pushService (NEW-A5)** or add an admin route.
8. **Convert env() bypass (L-04)** to `config()` in SecurityHeaders, TokenInactivityCheck, EnforcePasswordPolicy.
9. **Add rate limits to admin decision endpoints (NEW-A11)** including `auth/password/change`.
10. **Make Nashmi nonce required (NEW-A12)** in production.
11. **Add `(reviewer_id, created_at)` index on application_reviews (NEW-A17)**.
12. **Actually finish Dockerfile** (nginx.conf + supervisord.conf + entrypoint).
13. **Add metrics + error reporting** — `spatie/laravel-prometheus` + Sentry or equivalent.

---

## 32. Handoff truth table

| Claim | Status | Evidence |
|---|---|---|
| Modular monolith boundaries fully enforced | PARTIAL | Platform→JEA clean; sibling has 15 documented + 4 hidden violations (NEW-A6/A7); frontend has no enforcement |
| Platform is business-neutral | VERIFIED | `grep -RIn 'Modules\\Jea' backend/app` returns only removal-explaining doc comments |
| Optional modules are independently bootable | PARTIAL | Only jea-dues; disabling jea-projects/jea-services/jea-discipline breaks siblings |
| No confirmed dead production code remains | NOT_VERIFIED | 12 new unused/dead items detected (NEW-A2..NEW-A5, DC-6..DC-14) |
| No duplicate production implementation remains | VERIFIED | DUP-01, DUP-04 gone; no session-3 duplicates introduced |
| Tenant isolation is fail-closed | VERIFIED | H-01 + `whereRaw('1 = 0')` + `BelongsToOrganizationTest` |
| Superuser scope matches policy | VERIFIED | SuperuserScopeTest 36 data cases + model helpers |
| Payment production adapter active | BLOCKED_EXTERNAL_INPUT | Real gateway not bound (BLK-01). Additionally NEW-A2: `PaymentsController::confirm` doesn't use the abstraction anyway. |
| JEA verification production adapter active | BLOCKED_EXTERNAL_INPUT | HttpJeaMembershipVerifier skeleton present; endpoint URL/auth not available (BLK-02) |
| PostgreSQL full suite passed | VERIFIED | 864 tests / 863 passed / 1 skipped this audit against Docker Postgres 15 |
| Real concurrency tests passed | VERIFIED | 3/3 pcntl_fork tests on Postgres |
| Queue worker integration passed | NOT_VERIFIED | Jobs have 0 production dispatchers; no jobs/failed_jobs migrations |
| Frontend production build passed | VERIFIED | `vite build` exit 0 this audit |
| E2E passed | VERIFIED | 12/12 Playwright this audit |
| Docker stack executed | PARTIAL | `docker compose config` validates; full stack build not run (Dockerfile lacks nginx/supervisord configs) |
| Performance smoke executed | NOT_VERIFIED (this audit) | Session-3 ran it once (314 req / 0 fail / p95=51.9ms) — not re-run here |
| Capacity test executed | NOT_VERIFIED | 16-scenario plan scaffolded only |
| Production deployment approved | NOT_VERIFIED | NEW-A1 blocks every boot; BLK-01..BLK-04 outstanding |

---

## Factual ending

```
AUDIT_HEAD=a4224fcceff08a73d7c348b4a3324417fe66a413
AUDIT_BRANCH=remediation/architecture-security-production-readiness
WORKTREE_CLEAN=NO (0 tracked modifications; 8 user-owned untracked preserved)
REMEDIATION_COMMITS_COUNT=26
FILES_INSPECTED=~400 individual + bulk groups (see file inventory CSV)
FILES_NOT_FULLY_INSPECTED=~10 (Dockerfile config sub-files; some seeder bodies; JEA reference PDFs; vendor/)

ORIGINAL_CRITICAL_FINDINGS=5
VERIFIED_CRITICAL_FIXED=3 + 2 PARTIALLY (BLOCKED_EXTERNAL_INPUT)
ORIGINAL_HIGH_FINDINGS=12
VERIFIED_HIGH_FIXED=8 + 2 PARTIALLY + 1 NOT_FIXED (H-10) + 1 BLOCKED (H-11)
ORIGINAL_MEDIUM_FINDINGS=22
VERIFIED_MEDIUM_FIXED=13 + 5 PARTIALLY + 4 NOT_FIXED (M-10, M-14, M-16, M-17)
ORIGINAL_LOW_FINDINGS=13
VERIFIED_LOW_FIXED=8 + 1 PARTIALLY + 4 NOT_FIXED (L-01, L-04, L-06, L-08)

ARCHITECTURE_BOUNDARY_STATUS=PARTIAL
DEAD_CODE_STATUS=PARTIAL
DUPLICATION_STATUS=PASS
TENANCY_STATUS=PASS
SECURITY_INTERNAL_STATUS=PARTIAL
EXTERNAL_INTEGRATION_STATUS=BLOCKED_EXTERNAL_INPUT
DATABASE_STATUS=PASS
CONCURRENCY_STATUS=PASS
QUEUE_STATUS=FAIL
BACKEND_TEST_STATUS=PASS
FRONTEND_TEST_STATUS=PASS
FRONTEND_BUILD_STATUS=PASS
E2E_STATUS=PASS
OPERATIONS_STATUS=PARTIAL
PERFORMANCE_SMOKE_STATUS=NOT_EXECUTED
PERFORMANCE_CAPACITY_STATUS=NOT_EXECUTED
DOCUMENTATION_STATUS=PARTIAL
PRODUCTION_DEPLOYMENT_APPROVED=NO

FINAL_REMEDIATION_VERDICT=REMEDIATION_SUBSTANTIALLY_SUCCESSFUL_WITH_RESIDUALS
CODE_MODIFIED=NO
COMMIT_CREATED=NO
TAG_CREATED=NO
PUSH_PERFORMED=NO
```
