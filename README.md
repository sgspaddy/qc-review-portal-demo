QC Review Portal (Demo)

This repository contains a Django-based QC Review Portal built as a personal demo project for interview and code-review purposes.
The application demonstrates my backend architecture, API design, business-logic separation, and UI implementation using a realistic clinical QC workflow.

The domain and functionality are inspired by a production QC Checker application, but the implementation, structure, and naming are intentionally redesigned for demonstration.

Purpose of this demo

This project is designed to showcase:

Clean Django project structure

Separation of concerns (rules, services, views, APIs)

Practical database modeling

REST API + HTML UI living side-by-side

Realistic QC decision logic and audit trails

Readable, maintainable, “human-written” code style

It is not connected to real patient data and uses synthetic demo records only.

Core functionality
1. QC Metric Ingestion (Mocked)

Stores specimen-level QC metrics (reads, contamination, coverage)

Supports multiple specimen types:

NORMAL

TUMOR

CONTROL

Data is stored in an external database (via DATABASE_URL, mocked for demo)

This mirrors how QC metrics are persisted in the real QC Checker system.

2. Automated QC Evaluation

Each specimen is automatically evaluated using rule-based thresholds:

PASS

FAIL

NEEDS_REPEAT

PENDING (missing data)

Rules are:

Centralized in a rules module

Independent from views and APIs

Easy to adjust or extend

This matches the automated QC scoring logic in the production QC Checker app.

3. Run-Level QC Status (CONTROL-based)

Run status is derived only from CONTROL specimens

Logic:

All controls PASS → Run PASS

Any control FAIL → Run FAIL

No control present → Run PENDING

This is the same run-level logic used in the real application.

4. Reviewer Decision Workflow

Reviewers can override automated decisions

Each decision records:

Decision value

Reviewer

Timestamp

Optional comment

Full decision history is retained (audit-friendly)

This mirrors the manual review and audit trail functionality of the QC Checker.

5. Web UI (HTML + Bootstrap)

The UI provides:

Dashboard with filtering and pagination

Run detail view (all specimens in a run)

Specimen review page with:

Computed QC result

Metric breakdown

Reviewer decision form

Decision history

UI behavior and information density closely match the production QC Checker, but with simplified styling for demo clarity.

6. REST API (Django REST Framework)

The same data and logic are exposed via APIs:

List runs

Retrieve run specimens + run QC status

Retrieve specimen details

Submit reviewer decisions programmatically

This demonstrates:

Shared business logic between UI and API

Clean, versioned endpoints

Backend-first design

What is intentionally the same as the real QC Checker

QC decision logic concepts

CONTROL-based run status

Automated + manual review flow

Decision audit trail

Separation of ingestion, evaluation, and review

Combination of UI and API access patterns

What is intentionally different

Simplified schema and thresholds

Synthetic demo data only

Renamed models and modules

No production integrations (LIMS, file watchers, pipelines)

No PHI / clinical identifiers

These changes ensure this repository is safe, portable, and interview-appropriate.

Tech stack

Python

Django

Django REST Framework

External DB via DATABASE_URL (Postgres/MySQL compatible)

HTML templates + Bootstrap

Session-based authentication

Intended audience

Engineering interviewers

Code reviewers

Hiring managers evaluating:

Backend design

Django best practices

Business-logic modeling

Real-world system thinking
