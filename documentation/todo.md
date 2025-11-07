# 📋 RICHWELL SCHOOL PORTAL - TODO LIST

**Last Updated:** 2025-11-07
**Overall Completion:** 79%

---

## 🔴 **HIGH PRIORITY - Critical Gaps**

### 1. Implement Archiving System ⚠️ CRITICAL
**Status:** Model exists but completely unused (10% complete)
**Impact:** No data preservation, risk of data loss
**Reference:** plan.md Module 9

**Tasks:**
- [ ] Create archiving views in `rci/audit/views.py`
  - [ ] `archive_term_view()` - Archive all grades/enrollments when term closes
  - [ ] `archive_student_view()` - Archive student data on graduation
  - [ ] `view_archives_view()` - Browse archived data (read-only)
  - [ ] `restore_archive_view()` - Restore archived data (admin/registrar only)
- [ ] Add archiving URLs to `rci/audit/urls.py`
- [ ] Create term closing workflow
  - [ ] Update `rci/enrollment/models.py` - Add `close_term()` method to Term model
  - [ ] Create management command: `rci/enrollment/management/commands/close_term.py`
  - [ ] Auto-archive grades, enrollments, student subjects when term closes
  - [ ] Set `is_active = False` on term close
- [ ] Create graduation workflow
  - [ ] Add `graduate_student()` method to Student model
  - [ ] Archive complete academic record as JSON snapshot
  - [ ] Update student status to 'graduated'
- [ ] Create archive templates
  - [ ] `frontend/templates/audit/archives_list.html`
  - [ ] `frontend/templates/audit/archive_detail.html`
  - [ ] `frontend/templates/audit/archive_restore.html`
- [ ] Add archive access to navbar for admin/registrar
- [ ] Test archiving with seed data

**Files to Create/Modify:**
```
CREATE: rci/audit/views.py (archiving views)
CREATE: rci/audit/urls.py (if not exists)
CREATE: rci/enrollment/management/commands/close_term.py
CREATE: frontend/templates/audit/archives_list.html
CREATE: frontend/templates/audit/archive_detail.html
MODIFY: rci/enrollment/models.py (add close_term method)
MODIFY: rci/users/models.py (add graduate_student method)
MODIFY: frontend/templates/components/navbar.html (add archive link)
```

---

### 2. Complete Audit Trail Logging ⚠️ CRITICAL
**Status:** Only grade changes logged (30% complete)
**Impact:** Cannot track accountability for system changes
**Reference:** plan.md Module 8

**Tasks:**

#### A. Enrollment Audit Logging
- [ ] Add audit logging to `rci/enrollment/views.py`
  - [ ] `enroll_subject_view()` - Log when student enrolls in subject (line ~382)
  - [ ] `drop_subject_view()` - Log when student drops subject (line ~452)
  - [ ] `auto_enroll_view()` - Log auto-enrollment actions (line ~174)

**Code to add:**
```python
# After successful enrollment
AuditTrail.objects.create(
    actor=request.user,
    action='enroll_subject',
    entity='StudentSubject',
    entity_id=enrollment.id,
    new_value_json={'subject': section.subject.code, 'section': section.section_code}
)

# After successful drop
AuditTrail.objects.create(
    actor=request.user,
    action='drop_subject',
    entity='StudentSubject',
    entity_id=enrollment.id,
    old_value_json={'subject': enrollment.subject.code, 'section': enrollment.section.section_code}
)
```

#### B. Settings Audit Logging
- [ ] Update `rci/settingsapp/admin.py` - Add audit logging in `save_model()` (line ~23)

**Code to add:**
```python
def save_model(self, request, obj, form, change):
    if change:
        old_value = Setting.objects.get(pk=obj.pk).value_text
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

        # Add audit logging
        AuditTrail.objects.create(
            actor=request.user,
            action='update_setting',
            entity='Setting',
            entity_id=obj.id,
            old_value_json={'key': obj.key_name, 'value': old_value},
            new_value_json={'key': obj.key_name, 'value': obj.value_text}
        )
    else:
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
```

#### C. Section Assignment Audit Logging
- [ ] Update `rci/enrollment/admin.py` - Add audit logging for Section changes
- [ ] Override `save_model()` to log professor assignments
- [ ] Log section status changes (open/full/closed)

#### D. Term Management Audit Logging
- [ ] Log term activation/deactivation
- [ ] Log term creation
- [ ] Log deadline changes

**Files to Modify:**
```
MODIFY: rci/enrollment/views.py (lines ~382, ~452, ~174)
MODIFY: rci/settingsapp/admin.py (line ~23)
MODIFY: rci/enrollment/admin.py (add save_model override)
```

---

### 3. Implement INC Auto-Expiration ⚠️ CRITICAL
**Status:** Logic exists but not automated (75% complete)
**Impact:** INCs won't expire automatically, requires manual intervention
**Reference:** plan.md Module 7

**Tasks:**
- [ ] Create management command: `rci/grades/management/commands/expire_inc_grades.py`
  - [ ] Query all Grade records with grade='INC'
  - [ ] Check `is_inc_expired` property for each
  - [ ] Update status to 'repeat_required' for expired INCs
  - [ ] Log expiration in AuditTrail
  - [ ] Send notification/email to affected students (optional)
- [ ] Set up scheduled task (cron job or Django-Q/Celery)
  - [ ] Run daily at midnight: `python manage.py expire_inc_grades`
  - [ ] Document in deployment docs
- [ ] Test with seed data (student_with_inc has expired INC)

**Management Command Code:**
```python
# rci/grades/management/commands/expire_inc_grades.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from rci.grades.models import Grade
from rci.audit.models import AuditTrail

class Command(BaseCommand):
    help = 'Check and expire INC grades based on subject type and posting date'

    def handle(self, *args, **options):
        inc_grades = Grade.objects.filter(grade='INC')
        expired_count = 0

        for grade in inc_grades:
            if grade.is_inc_expired:
                student_subject = grade.student_subject
                old_status = student_subject.status

                student_subject.status = 'repeat_required'
                student_subject.save()

                # Log in audit trail
                AuditTrail.objects.create(
                    actor=None,  # System action
                    action='expire_inc',
                    entity='StudentSubject',
                    entity_id=student_subject.id,
                    old_value_json={'status': old_status},
                    new_value_json={'status': 'repeat_required', 'reason': 'INC expired'}
                )

                expired_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'Expired INC: {student_subject.student.user.get_full_name()} - {student_subject.subject.code}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully expired {expired_count} INC grades')
        )
```

**Files to Create:**
```
CREATE: rci/grades/management/commands/expire_inc_grades.py
CREATE: rci/grades/management/commands/__init__.py (if not exists)
UPDATE: documentation/deployment.md (add cron job setup)
```

**Cron Job Setup:**
```bash
# Add to crontab: Run daily at midnight
0 0 * * * cd /path/to/Richwell-Portal-Vibe-3/rci && python manage.py expire_inc_grades
```

---

### 4. Fix Admission Status Field ⚠️ HIGH
**Status:** Field missing, code references it (85% complete)
**Impact:** Application tracking broken, no approval workflow
**Reference:** plan.md Module 2

**Tasks:**
- [ ] Update `rci/admission/models.py` - Add status field to AdmissionApplication
  - [ ] Add STATUS_CHOICES: pending, approved, rejected
  - [ ] Add `status` field with default='pending'
  - [ ] Add `processed_by` ForeignKey (registrar/admin who processed)
  - [ ] Add `processed_at` DateTimeField
- [ ] Create migration: `python manage.py makemigrations`
- [ ] Update `rci/admission/views.py`
  - [ ] Modify `admission_form_view()` - Set status='pending' instead of auto-creating account
  - [ ] Fix `process_application_view()` - Only create account when status='approved'
  - [ ] Add rejection workflow
- [ ] Update templates
  - [ ] Show status on application list
  - [ ] Add approve/reject buttons for admission staff
- [ ] Add audit logging for status changes
- [ ] Test approval/rejection workflow

**Model Changes:**
```python
# rci/admission/models.py - Add to AdmissionApplication
class AdmissionApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # Add these fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='processed_applications')
    processed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
```

**Files to Modify:**
```
MODIFY: rci/admission/models.py (add status field)
MODIFY: rci/admission/views.py (fix approval workflow)
MODIFY: frontend/templates/admission/application_list.html (show status)
MODIFY: frontend/templates/admission/application_detail.html (add approve/reject buttons)
```

---

## 🟡 **MEDIUM PRIORITY - Enhancements**

### 5. Add Term Closing Workflow UI
- [ ] Create term management dashboard for registrar
- [ ] Add "Close Term" button with confirmation dialog
- [ ] Show term statistics before closing (enrollments, pending grades)
- [ ] Trigger archiving workflow on close
- [ ] Add validation (all grades must be posted before closing)

**Files to Create:**
```
CREATE: rci/enrollment/views.py - close_term_view()
CREATE: frontend/templates/enrollment/term_management.html
UPDATE: rci/enrollment/urls.py (add term management routes)
```

---

### 6. Improve Audit Trail Reporting
- [ ] Add audit trail detail view (show old_value vs new_value side-by-side)
- [ ] Add filtering by actor, action type, date range
- [ ] Add export to CSV functionality
- [ ] Add real-time audit log viewer (WebSocket/SSE)

**Files to Update:**
```
UPDATE: rci/reports/views.py (enhance audit_trail_report_view)
UPDATE: frontend/templates/reports/audit_trail.html
```

---

### 7. Student Notifications System
- [ ] Create Notification model
- [ ] Send notifications for:
  - [ ] INC expiration warnings (1 month before)
  - [ ] Grade posting
  - [ ] Enrollment deadlines
  - [ ] Application status changes
- [ ] Add notification bell icon to navbar
- [ ] Create notification center page

**Files to Create:**
```
CREATE: rci/notifications/ (new app)
CREATE: rci/notifications/models.py
CREATE: rci/notifications/views.py
CREATE: frontend/templates/notifications/list.html
```

---

## 🟢 **LOW PRIORITY - Nice to Have**

### 8. Enhanced Error Handling
- [ ] Create custom 404 page
- [ ] Create custom 500 page
- [ ] Add error logging to file
- [ ] Add user-friendly error messages

---

### 9. Performance Optimizations
- [ ] Add database indexes to frequently queried fields
- [ ] Implement query optimization (select_related, prefetch_related)
- [ ] Add caching for Settings queries
- [ ] Add pagination to large lists (students, sections)

---

### 10. Testing & Documentation
- [ ] Write unit tests for models
- [ ] Write integration tests for enrollment workflow
- [ ] Write tests for prerequisite validation
- [ ] Write tests for INC expiration
- [ ] Create user manual (PDF)
- [ ] Create deployment guide
- [ ] Create API documentation (if API exists)

---

## 📊 **Progress Tracking**

### Completion by Module:
```
✅ User & Role Management        100%
⚠️  Admissions                    85% → Need status field
✅ Curriculum Management         100%
⚠️  Term Management               80% → Need closing workflow
✅ Section Management            100%
✅ Enrollment                    100%
⚠️  Grades & INC                  75% → Need auto-expiration
❌ Audit Trail                    30% → Need comprehensive logging
❌ Archiving                      10% → Need full implementation
⚠️  Settings                      90% → Need audit logging
✅ Reporting                     100%
```

### Target Completion: 95%+

**After completing HIGH PRIORITY tasks:**
- Archiving: 10% → 90%
- Audit Trail: 30% → 95%
- Grades & INC: 75% → 95%
- Admissions: 85% → 100%

**Estimated New Overall Completion: 94%**

---

## 🚀 **Recommended Implementation Order**

1. **Week 1:** Audit Trail Logging (Quick wins, high impact)
   - Add logging to enrollment, settings, sections
   - Low complexity, immediate accountability improvement

2. **Week 2:** INC Auto-Expiration (Automate critical process)
   - Create management command
   - Set up cron job
   - Test with seed data

3. **Week 3:** Admission Status Field (Fix broken workflow)
   - Add model field + migration
   - Update views and templates
   - Test approval/rejection flow

4. **Week 4:** Archiving System (Most complex, highest impact)
   - Implement term closing workflow
   - Create archiving views
   - Test data preservation
   - Document restoration process

---

## 📝 **Notes**

- All HIGH PRIORITY tasks are required per plan.md specifications
- Current system is functional but missing critical compliance features
- Archiving and audit trail are required for data integrity and accountability
- INC auto-expiration is required for academic rule enforcement
- Admission status field fixes existing bug in code

---

## 🔗 **Related Files**

- **Requirements:** `/home/user/Richwell-Portal-Vibe-3/documentation/plan.md`
- **Verification Report:** See conversation history for detailed gap analysis
- **Models:** `rci/*/models.py`
- **Seed Data:** `rci/users/management/commands/seed_data.py`
