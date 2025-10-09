```markdown
<!--
Sync Impact Report
- Version change: 0.1.0 -> 0.1.1 (patch: clarification / new hosting constraint)
- Modified principles: Added hosting constraint requiring Windows IIS compatibility
- Added sections: "Additional Constraints" updated with IIS requirement
- Removed sections: none
- Templates requiring updates:
	- .specify/templates/plan-template.md -> ⚠ pending (Constitution Check references generic gates; no hardcoded conflicts found)
	- .specify/templates/spec-template.md  -> ✅ aligned
	- .specify/templates/tasks-template.md -> ✅ aligned
	- .specify/templates/agent-file-template.md -> ⚠ pending (agent guidance may reference agent-specific files)
- Follow-up TODOs:
	- TODO(RATIFICATION_DATE): set original adoption date if known
	- Review `.specify/templates/commands/` if present and update agent-specific names
-->

# system-provisioning Constitution

## Core Principles

### Principle I — Simplicity FIRST (NON-NEGOTIABLE)
All design and implementation decisions MUST prioritize minimal complexity. Features MUST be implemented using the simplest correct approach that
meets requirements. Complexity additions (third-party libraries, abstractions, micro-services) are permitted ONLY with an explicit justification
recorded in the feature's plan and approved by a maintainer. Rationale: simplicity reduces maintenance, accelerates onboarding, and lowers
operational risk for small backoffice applications.

### Principle II — Minimal Dependencies
The project MUST avoid external libraries and frameworks unless there is a clear, measurable benefit (security, correctness, or an unduplicatable
capability). When a dependency is introduced, it MUST be pinned to a specific version, accompanied by a short rationale in the plan, and limited
to the smallest surface area required. Rationale: minimizes attack surface, dependency churn, and versioning complexity for backoffice systems.

### Principle III — Pragmatic Accessibility & UI
The UI MUST be functional and accessible enough for primary backoffice tasks but SHOULD prioritize simplicity over comprehensive accessibility or
highly responsive UI behavior. Developers MUST aim for straightforward, maintainable markup and styles; advanced responsive patterns or
accessibility features may be deferred unless legally required for the product. Rationale: backoffice apps often optimize operational efficiency over
public-facing UX/SEO concerns.

#### UX Consistency: Padding and Container Spacing (MUST)
UI containers (tables, modals, cards, panels, form containers and other primary UI boxes) MUST use consistent padding on all sides by default
(equal left/right/top/bottom padding) to provide a stable, predictable layout and a professional, low-friction operator experience. Any
exceptions to this rule MUST be called out explicitly in the feature spec with a short justification (for example: a data-dense table that
requires column compacting). This requirement aims to reduce ad-hoc spacing variations and improve visual consistency across features.

### Principle IV — Database-First Correctness
Data integrity and clear DB contracts are essential. Schemas, migrations, and data-access patterns MUST be explicit and reviewed. The system MUST
fail safely when data invariants are violated and include simple, deterministic migration paths. Rationale: backoffice correctness typically
depends on reliable data handling more than UI bells and whistles.

### Principle V — Test-First, Minimal Automation
Critical behaviors (business rules, persistence, and APIs) MUST have automated tests recorded in the plan and implemented with a tests-first
approach where practical. Testing scope is pragmatic: prioritize contract tests and integration tests for DB interactions; extensive UI end-to-end
tests are optional. Rationale: ensures correctness while keeping CI time and maintenance costs low.

## Additional Constraints

- Technology choices MUST favor standard language runtimes and built-in libraries. Preferred stack examples: a minimal web framework in the
	chosen language (or raw HTTP server), a relational database (Postgres, SQLite for small deployments), and no front-end frameworks if a
	simple server-rendered or minimal-JS UI suffices.
- SEO is not a consideration for this project and MUST NOT drive architectural choices.
- Performance targets are modest; optimize for clarity and reliability over micro-optimizations unless profiling demonstrates a bottleneck.
- Security: follow basic best-practices (parameterized queries, input validation, secure defaults). When higher compliance is required, document it in
	the feature spec as a NEEDS_CLARIFICATION item.

- Hosting: The application MUST be hostable on Windows IIS as a primary deployment target (for operational compatibility with existing Windows-based
	environments). Implementations SHOULD prefer technologies and packaging approaches that make IIS deployment straightforward (for example: a
	self-contained .NET deployment configured for IIS, or a reverse-proxy configuration using a lightweight Windows service wrapper). Rationale:
	many operations environments for ShoWare are Windows-centric and require IIS compatibility.

## Development Workflow & Quality Gates

- Code reviews are REQUIRED for all changes touching business logic or database schemas. Reviews MUST include a short note on how the change
	adheres to the constitution (one-line justification).
- Changes that introduce new external dependencies or significant architectural shifts (e.g., adding a service boundary) MUST include a
	short migration/rollback plan and be approved by a maintainer.
- Tests: Contract and integration tests for DB interactions MUST be in place and failing before implementation (TDD-first preferred). Unit tests
	are encouraged for non-trivial business logic.
- Basic observability: minimal structured logging and error reporting MUST be included for server-side flows. Full observability stacks are optional.

## Governance

- The Constitution is the canonical source for project constraints and supersedes informal conventions.
- Amendments: Any change to principles or governance MUST be proposed as a PR against this file and include a migration plan for affected templates
	and feature docs. Major or breaking changes to principles (removals or redefinitions) are MAJOR bumps; additions are MINOR; wording/typo fixes
	are PATCH.
- Compliance: Plans and PRs MUST reference the Constitution Check in `/specify/templates/plan-template.md` and document any justified deviations.

**Version**: 0.1.1 | **Ratified**: TODO(RATIFICATION_DATE) | **Last Amended**: 2025-10-02
``` 