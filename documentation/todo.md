# 📋 RICHWELL SCHOOL PORTAL - TODO LIST

**Last Updated:** 2025-11-07
**Overall Completion:** 79%

---

## 🔴 **HIGH PRIORITY - Critical Gaps**

---

### 1. Implement Archiving System ⚠️ CRITICAL

**Status:** Model exists but completely unused (10% complete)
**Impact:** No data preservation, risk of data loss
**Reference:** plan.md Module 9

**Tasks:**

* [ ] Create archiving views in `rci/audit/views.py`

  * [ ] `archive_term_view()` - Archive all grades/enrollments when term closes — 👤 **Kirt**
  * [ ] `archive_student_view()` - Archive student data on graduation — 👤 **Kirt**
  * [ ] `view_archives_view()` - Browse archived data (read-only) — 👤 **Kirt**, **Mary Ann**
  * [ ] `restore_archive_view()` - Restore archived data (admin/registrar only) — 👤 **Kirt**, **Mary Ann**
* [ ] Add archiving URLs to `rci/audit/urls.py` — 👤 **Kirt**
* [ ] Create term closing workflow

  * [ ] Update `rci/enrollment/models.py` - Add `close_term()` method — 👤 **Kirt**
  * [ ] Create management command: `rci/enrollment/management/commands/close_term.py` — 👤 **Kirt**
  * [ ] Auto-archive grades, enrollments, student subjects when term closes — 👤 **Kirt**
  * [ ] Set `is_active = False` on term close — 👤 **Kirt**
* [ ] Create graduation workflow

  * [ ] Add `graduate_student()` method to Student model — 👤 **Kirt**
  * [ ] Archive complete academic record as JSON snapshot — 👤 **Kirt**, **Mary Ann**
  * [ ] Update student status to 'graduated' — 👤 **Kirt**
* [ ] Create archive templates

  * [ ] `frontend/templates/audit/archives_list.html` — 👤 **Joshua**, **Marjorie**
  * [ ] `frontend/templates/audit/archive_detail.html` — 👤 **Joshua**, **Mary Ann**
  * [ ] `frontend/templates/audit/archive_restore.html` — 👤 **Joshua**
* [ ] Add archive access to navbar for admin/registrar — 👤 **Joshua**, **Aira**
* [ ] Test archiving with seed data — 👤 **Yasmien**, **Jun**

---

### 2. Complete Audit Trail Logging ⚠️ CRITICAL

**Status:** Only grade changes logged (30% complete)
**Impact:** Cannot track accountability for system changes
**Reference:** plan.md Module 8

#### A. Enrollment Audit Logging

* [ ] Add audit logging to `rci/enrollment/views.py`

  * [ ] `enroll_subject_view()` (line ~382) — 👤 **Kirt**
  * [ ] `drop_subject_view()` (line ~452) — 👤 **Kirt**
  * [ ] `auto_enroll_view()` (line ~174) — 👤 **Kirt**

#### B. Settings Audit Logging

* [ ] Update `rci/settingsapp/admin.py` (line ~23) — 👤 **Kirt**

#### C. Section Assignment Audit Logging

* [ ] Update `rci/enrollment/admin.py` - Add audit logging for Section changes — 👤 **Kirt**, **Edjohn**
* [ ] Override `save_model()` to log professor assignments — 👤 **Kirt**
* [ ] Log section status changes (open/full/closed) — 👤 **Kirt**, **Edjohn**

#### D. Term Management Audit Logging

* [ ] Log term activation/deactivation — 👤 **Kirt**
* [ ] Log term creation — 👤 **Kirt**
* [ ] Log deadline changes — 👤 **Kirt**, **Jun**

---

### 3. Implement INC Auto-Expiration ⚠️ CRITICAL

**Status:** Logic exists but not automated (75% complete)
**Impact:** INCs won't expire automatically
**Reference:** plan.md Module 7

**Tasks:**

* [ ] Create management command: `rci/grades/management/commands/expire_inc_grades.py` — 👤 **Kirt**
* [ ] Set up scheduled task (cron job or Django-Q/Celery) — 👤 **Jun**, **Kirt**
* [ ] Test with seed data (student_with_inc) — 👤 **Yasmien**, **Aira**, **Edjohn**

---

### 4. Fix Admission Status Field ⚠️ HIGH

**Status:** Field missing, code references it (85% complete)
**Impact:** Application tracking broken
**Reference:** plan.md Module 2

**Tasks:**

* [ ] Update `rci/admission/models.py` - Add status field — 👤 **Kirt**
* [ ] Create migration — 👤 **Kirt**
* [ ] Update `rci/admission/views.py` (fix approval/rejection workflow) — 👤 **Kirt**, **Mary Ann**
* [ ] Update templates

  * [ ] Show status on list — 👤 **Mary Ann**, **Joshua**
  * [ ] Add approve/reject buttons — 👤 **Mary Ann**, **Marjorie**
* [ ] Add audit logging for status changes — 👤 **Kirt**
* [ ] Test workflow — 👤 **Yasmien**

---

## 🟡 **MEDIUM PRIORITY - Enhancements**

---

### 5. Add Term Closing Workflow UI

* [ ] Create term management dashboard — 👤 **Joshua**, **Mary Ann**
* [ ] Add "Close Term" button — 👤 **Joshua**, **Marjorie**
* [ ] Show term statistics — 👤 **Joshua**, **Aira**
* [ ] Trigger archiving workflow — 👤 **Kirt**
* [ ] Add validation (all grades posted) — 👤 **Kirt**

---

### 6. Improve Audit Trail Reporting

* [ ] Add audit trail detail view — 👤 **Kirt**, **Joshua**
* [ ] Add filtering + export CSV — 👤 **Kirt**, **Aira**
* [ ] Add real-time audit log viewer (SSE/WebSocket) — 👤 **Kirt**, **Joshua**

---

### 7. Student Notifications System

* [ ] Create Notification model — 👤 **Kirt**
* [ ] Send notifications for events — 👤 **Kirt**, **Aira**
* [ ] Add notification bell icon — 👤 **Joshua**, **Marjorie**
* [ ] Create notification center page — 👤 **Joshua**

---

## 🟢 **LOW PRIORITY - Nice to Have**

---

### 8. Enhanced Error Handling

* [ ] Create custom 404/500 pages — 👤 **Joshua**, **Marjorie**
* [ ] Add error logging — 👤 **Kirt**
* [ ] Add user-friendly messages — 👤 **Joshua**, **Aira**

---

### 9. Performance Optimizations

* [ ] Add DB indexes — 👤 **Kirt**
* [ ] Optimize queries (select_related/prefetch_related) — 👤 **Kirt**
* [ ] Add caching for settings — 👤 **Kirt**
* [ ] Add pagination to lists — 👤 **Joshua**, **Aira**

---

### 10. Testing & Documentation

* [ ] Write unit tests for models — 👤 **Kirt**, **Yasmien**
* [ ] Write integration tests — 👤 **Yasmien**, **Edjohn**
* [ ] Write tests for INC expiration — 👤 **Yasmien**
* [ ] Create user manual (PDF) — 👤 **Jun**, **Mary Ann**
* [ ] Create deployment guide — 👤 **Jun**
* [ ] Create API documentation — 👤 **Kirt**, **Jun**

---

## 📊 **Progress Tracking**

(unchanged; same completion and targets)

---

## 🚀 **Recommended Implementation Order**

(unchanged — follows week-based rollout)

---

## 🧩 **Team Overview**

| Name         | Role          | Focus                                      |
| ------------ | ------------- | ------------------------------------------ |
| **Jun**      | PM / Docs     | Repo management, deployment docs, reviews  |
| **Kirt**     | Backend Lead  | Django, archiving, audit logging, commands |
| **Joshua**   | Frontend Lead | Templates, layout, term UI                 |
| **Aira**     | Frontend      | Student UI, status views                   |
| **Mary Ann** | Registrar UI  | Admissions, archive views                  |
| **Edjohn**   | Professor UI  | Grade UI, testing                          |
| **Marjorie** | UI/UX Lead    | Components, design, responsiveness         |
| **Yasmien**  | QA / Testing  | Test plans, QA reports, bug tracking       |

---
