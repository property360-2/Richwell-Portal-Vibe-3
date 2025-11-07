# 🧭 RICHWELL SCHOOL PORTAL – DEVELOPMENT PLAN (v2.0)

---

## 🧱 **Phase 0: Foundations**

### 🎯 Goal

Establish project structure, environment, and repository standards.
always refer to the plan, this should be precise

### ✅ Tasks

* Create project repository and initialize `.env`.
* Set up Django project and core app modules (`users`, `academics`, `enrollment`, `grades`, `audit`, `settingsapp`).
* Configure SQLite (dev) and environment variables.
* Install dependencies (`django`, `django-htmx`, `alpine.js`, `tailwindcss` via CDN).
* Configure static file routing and base template system.
* Add basic `README.md`, `requirements.txt`, and `.gitignore`.

**Frontend:**

* Set up `base.html` layout with HTMX + Tailwind skeleton.
* Build simple navigation bar and placeholder dashboards.

---

## 🧮 **Phase 1: Core Models & Database Integration**

### 🎯 Goal

Implement all schema tables, constraints, and Django ORM mappings.

### ✅ Tasks

* Define all models from database schema:
 inside the Documentation\schema.md
* Apply all foreign keys, enums (as choices), and default fields.
* Run migrations and confirm integrity.
* Register all models in Django Admin for data inspection.
* Seed minimal sample data (users, terms, subjects).

**Frontend:**

* Admin interface styling with custom branding.
* Read-only table views using HTMX for quick previews.

---

## ⚙️ **Phase 2: Authentication & Role Management**

### 🎯 Goal

Implement secure login, session management, and role-based access.

### ✅ Tasks

* Extend Django `AbstractUser` for custom `Users` model.
* Implement middleware for role-based access (student, professor, registrar, admin, etc.).
* Create login, logout, and password reset pages.
* Create dashboards per role (different menus per permission).

**Frontend:**

* Use Tailwind + Alpine.js for responsive dashboards.
* Dynamic navigation depending on user role.
* HTMX fragments for dashboard content (avoid full reloads).

---

## 🧾 **Phase 3: Admissions & Student Onboarding**

### 🎯 Goal

Handle online admission forms and automatic student account creation.

### ✅ Tasks

* Admission link toggled via `Settings.admission_link_enabled`.
* Create admission form with fields for Freshman or Transferee.
* On submit:

  * Generate `Users` + `Students` records.
  * Assign `Curriculum` and default program.
  * Auto-enroll recommended freshman subjects (≤30 units).
* Build manual crediting interface for transferees (Registrar).

**Frontend:**

* Admission form (public page) with clean progress flow.
* Confirmation page summarizing enrollment details.

---

## 🧭 **Phase 4: Enrollment Module**

### 🎯 Goal

Enable validated subject enrollment tied to sections and prerequisites.

### ✅ Tasks

* Enrollment opens/closes via `Settings.enrollment_open`.
* Show student’s eligible subjects based on prerequisites.
* Validate:

  * Passed prerequisites
  * Section capacity
  * No duplicates
  * Unit cap (`Settings.freshman_unit_cap`)
* On success, record entries in `StudentSubjects`.
* Auto-generate Certificate of Registration (COR) as downloadable PDF.

**Frontend:**

* Interactive subject selection table with HTMX actions (add/drop).
* Real-time validation and unit counter.
* COR PDF preview modal.

---

## 🧑‍🏫 **Phase 5: Professors & Grading System**

### 🎯 Goal

Provide professors secure access to their sections and grade submission.

### ✅ Tasks

* Professor view limited to assigned `Sections`.
* Create grade encoding page (per student per subject).
* Update `StudentSubjects.status` based on grade.
* Handle `INC` lifecycle logic:

  * 6 months for major
  * 1 year for minor
  * Auto “repeat_required” after expiration
* Log every grade update in `AuditTrail`.

**Frontend:**

* HTMX-powered grading table with inline editing.
* Color-coded grade statuses (passed, failed, INC).
* Compact summary widget for section statistics.

---

## 🧱 **Phase 6: Archiving, AuditTrail & Settings Management**

### 🎯 Goal

Implement system control, data integrity, and accountability tools.

### ✅ Tasks

* Build `Settings` management UI (key/value editing).
* Create decorator/service for automatic audit logging on key changes.
* Implement archive service for:

  * Term closure
  * Student graduation
* Serialize data snapshots into `Archive.data_snapshot` (JSON).
* Enforce read-only access to archived data.

**Frontend:**

* Settings panel (toggle switches + inline save).
* AuditTrail viewer with filters (actor, date, entity).
* Archive list with expandable JSON preview.

---

## 📊 **Phase 7: Reporting & Analytics**

### 🎯 Goal

Generate dynamic insights for admins, deans, and registrars.

### ✅ Tasks

* Enrollment summaries (by term, program, section).
* Grade distribution charts.
* INC tracking report.
* Unit load summary per student.
* Section utilization metrics.
* Export to CSV/PDF.

**Frontend:**

* Dashboard charts (Chart.js).
* Filter controls for terms and programs.
* Printable report templates.

---

## 🚀 **Phase 8: Final QA, Optimization & Deployment**

### 🎯 Goal

Finalize and deploy a stable, production-ready system.

### ✅ Tasks

* Perform complete manual testing across all roles.
* Apply optimizations:

  * Query caching on common pages
  * Prefetch related data for ORM efficiency
  * Pagination for large tables
* Polish Tailwind theming and responsiveness.
* Prepare production `.env` and database (PostgreSQL).
* Deploy via Gunicorn + Nginx or built-in WSGI.
* Document deployment steps and admin usage.

**Frontend:**

* Final responsive layout polish.
* Landing page with login portal and system info.
* Test all HTMX components for latency and UX quality.

---

## ⚙️ **Post-MVP Extensions**

* Integrate **REST API (DRF)** for mobile access.
* Add **Notifications** (email/SMS/portal alerts).
* Connect to **Payment Tracking** system.
* Implement **SSO or OAuth2** for institutional integration.
* Build **Curriculum Visualizer** for academic flowcharts.

---
