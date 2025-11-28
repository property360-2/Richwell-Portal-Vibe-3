# rci/audit/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.core.serializers import serialize
from django.http import JsonResponse
import json

from .models import Archive, AuditTrail
from enrollment.models import Term, Student, StudentSubject
from grades.models import Grade


def check_archive_access(user):
    """Check if user has permission to access archives"""
    return user.role in ['admin', 'registrar']


@login_required
def archive_term_view(request, term_id):
    """Archive all data for a closed term"""
    if not check_archive_access(request.user):
        messages.error(request, 'You do not have permission to archive terms.')
        return redirect('dashboard')
    
    term = get_object_or_404(Term, id=term_id)
    
    # Verify term is not active
    if term.is_active:
        messages.error(request, 'Cannot archive an active term. Please close it first.')
        return redirect('staff:terms_list')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                archived_count = 0
                
                # Archive all student subjects for this term
                student_subjects = StudentSubject.objects.filter(term=term).select_related(
                    'student__user', 'subject', 'section', 'professor'
                )
                
                for ss in student_subjects:
                    # Get grade if exists
                    grade_data = None
                    try:
                        grade = ss.grade
                        grade_data = {
                            'grade': grade.grade,
                            'posted_at': grade.posted_at.isoformat() if grade.posted_at else None,
                            'inc_posted_date': grade.inc_posted_date.isoformat() if grade.inc_posted_date else None,
                            'remarks': grade.remarks,
                        }
                    except Grade.DoesNotExist:
                        pass
                    
                    # Create snapshot
                    snapshot = {
                        'student_username': ss.student.user.username,
                        'student_name': ss.student.user.get_full_name(),
                        'subject_code': ss.subject.code,
                        'subject_title': ss.subject.title,
                        'subject_units': str(ss.subject.units),
                        'section_code': ss.section.section_code,
                        'professor_name': ss.professor.get_full_name(),
                        'status': ss.status,
                        'enrolled_date': ss.created_at.isoformat(),
                        'grade_data': grade_data,
                    }
                    
                    Archive.objects.create(
                        entity='StudentSubject',
                        entity_id=ss.id,
                        data_snapshot=snapshot,
                        reason=f'Term Closed: {term.name}',
                        archived_by=request.user
                    )
                    archived_count += 1
                
                # Archive term data itself
                term_snapshot = {
                    'name': term.name,
                    'start_date': term.start_date.isoformat(),
                    'end_date': term.end_date.isoformat(),
                    'add_drop_deadline': term.add_drop_deadline.isoformat() if term.add_drop_deadline else None,
                    'grade_encoding_deadline': term.grade_encoding_deadline.isoformat() if term.grade_encoding_deadline else None,
                    'total_sections': term.sections.count(),
                    'total_enrollments': student_subjects.count(),
                }
                
                Archive.objects.create(
                    entity='Term',
                    entity_id=term.id,
                    data_snapshot=term_snapshot,
                    reason='Term Closed',
                    archived_by=request.user
                )
                
                # Log in audit trail
                AuditTrail.objects.create(
                    actor=request.user,
                    action='archive_term',
                    entity='Term',
                    entity_id=term.id,
                    new_value_json={'archived_records': archived_count},
                )
                
                messages.success(
                    request,
                    f'Successfully archived {archived_count} enrollment records for {term.name}'
                )
                return redirect('audit:archives_list')
                
        except Exception as e:
            messages.error(request, f'Error archiving term: {str(e)}')
            return redirect('staff:terms_list')
    
    # GET request - show confirmation page
    enrollments_count = StudentSubject.objects.filter(term=term).count()
    
    context = {
        'term': term,
        'enrollments_count': enrollments_count,
    }
    return render(request, 'audit/archive_term_confirm.html', context)


@login_required
def archive_student_view(request, student_id):
    """Archive student's complete academic record on graduation"""
    if not check_archive_access(request.user):
        messages.error(request, 'You do not have permission to archive student records.')
        return redirect('dashboard')
    
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get all student data
                all_subjects = StudentSubject.objects.filter(
                    student=student
                ).select_related('subject', 'term', 'section', 'professor')
                
                # Build complete academic record
                subjects_data = []
                for ss in all_subjects:
                    grade_data = None
                    try:
                        grade = ss.grade
                        grade_data = {
                            'grade': grade.grade,
                            'posted_at': grade.posted_at.isoformat() if grade.posted_at else None,
                            'remarks': grade.remarks,
                        }
                    except Grade.DoesNotExist:
                        pass
                    
                    subjects_data.append({
                        'term': ss.term.name,
                        'subject_code': ss.subject.code,
                        'subject_title': ss.subject.title,
                        'units': str(ss.subject.units),
                        'section': ss.section.section_code,
                        'professor': ss.professor.get_full_name(),
                        'status': ss.status,
                        'grade': grade_data,
                    })
                
                # Calculate totals
                total_units = sum(float(ss.subject.units) for ss in all_subjects if ss.status == 'completed')
                
                # Create comprehensive snapshot
                snapshot = {
                    'student_info': {
                        'username': student.user.username,
                        'full_name': student.user.get_full_name(),
                        'email': student.user.email,
                        'program': student.program.name,
                        'curriculum': student.curriculum.version,
                        'status': student.status,
                    },
                    'academic_record': subjects_data,
                    'statistics': {
                        'total_subjects': len(subjects_data),
                        'completed_subjects': sum(1 for s in subjects_data if s['status'] == 'completed'),
                        'total_units': str(total_units),
                    },
                    'archived_date': timezone.now().isoformat(),
                }
                
                Archive.objects.create(
                    entity='Student',
                    entity_id=student.id,
                    data_snapshot=snapshot,
                    reason='Student Graduated',
                    archived_by=request.user
                )
                
                # Update student status
                student.status = 'graduated'
                student.save()
                
                # Log audit
                AuditTrail.objects.create(
                    actor=request.user,
                    action='graduate_student',
                    entity='Student',
                    entity_id=student.id,
                    old_value_json={'status': 'active'},
                    new_value_json={'status': 'graduated'},
                )
                
                messages.success(
                    request,
                    f'Successfully archived academic record for {student.user.get_full_name()} and marked as graduated.'
                )
                return redirect('audit:archives_list')
                
        except Exception as e:
            messages.error(request, f'Error archiving student: {str(e)}')
            return redirect('staff:students_list')
    
    # GET request - show confirmation
    total_subjects = StudentSubject.objects.filter(student=student).count()
    completed_subjects = StudentSubject.objects.filter(student=student, status='completed').count()
    
    context = {
        'student': student,
        'total_subjects': total_subjects,
        'completed_subjects': completed_subjects,
    }
    return render(request, 'audit/archive_student_confirm.html', context)


@login_required
def view_archives_view(request):
    """Browse all archived data"""
    if not check_archive_access(request.user):
        messages.error(request, 'You do not have permission to view archives.')
        return redirect('dashboard')
    
    entity_filter = request.GET.get('entity', '')
    search = request.GET.get('search', '')
    
    archives = Archive.objects.select_related('archived_by').order_by('-archived_at')
    
    if entity_filter:
        archives = archives.filter(entity=entity_filter)
    
    if search:
        archives = archives.filter(reason__icontains=search)
    
    entity_types = Archive.objects.values_list('entity', flat=True).distinct()
    
    archives = archives[:50]  # limit
    
    context = {
        'archives': archives,
        'entity_types': entity_types,
        'selected_entity': entity_filter,
        'search': search,
    }
    return render(request, 'audit/archives_list.html', context)


@login_required
def archive_detail_view(request, archive_id):
    """View detailed archive snapshot"""
    if not check_archive_access(request.user):
        messages.error(request, 'You do not have permission to view archives.')
        return redirect('dashboard')
    
    archive = get_object_or_404(Archive, id=archive_id)
    
    snapshot_json = json.dumps(archive.data_snapshot, indent=2)
    
    context = {
        'archive': archive,
        'snapshot_json': snapshot_json,
    }
    return render(request, 'audit/archive_detail.html', context)


@login_required
def restore_archive_view(request, archive_id):
    """Restore archived data (admin only)"""
    if request.user.role != 'admin':
        messages.error(request, 'Only administrators can restore archived data.')
        return redirect('audit:archives_list')
    
    archive = get_object_or_404(Archive, id=archive_id)
    
    if request.method == 'POST':
        messages.warning(
            request,
            'Archive restoration is not yet implemented. This feature requires careful validation and is reserved for critical data recovery.'
        )
        return redirect('audit:archive_detail', archive_id=archive_id)
    
    context = {
        'archive': archive,
    }
    return render(request, 'audit/archive_restore.html', context)


# ✅ NEW VIEW — Simple placeholder for Archives List
@login_required
def archives_list_view(request):
    """Simple list view for Archives page"""
    if not check_archive_access(request.user):
        messages.error(request, 'You do not have permission to view archives.')
        return redirect('dashboard')

    archives = Archive.objects.all().order_by('-archived_at')

    context = {
        'archives': archives
    }
    return render(request, 'audit/archives_list.html', context)
