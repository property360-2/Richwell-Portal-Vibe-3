# rci/enrollment/management/commands/close_term.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from enrollment.models import Term
from users.models import User


class Command(BaseCommand):
    help = 'Close an academic term and archive all associated data'

    def add_arguments(self, parser):
        parser.add_argument(
            'term_id',
            type=int,
            help='ID of the term to close'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force close even if term is currently active'
        )

    def handle(self, *args, **options):
        term_id = options['term_id']
        force = options['force']

        try:
            term = Term.objects.get(id=term_id)
        except Term.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Term with ID {term_id} not found.'))
            return

        self.stdout.write(self.style.WARNING(f'\n{"="*60}'))
        self.stdout.write(self.style.WARNING(f'CLOSING TERM: {term.name}'))
        self.stdout.write(self.style.WARNING(f'{"="*60}\n'))

        # Check if term is active
        if term.is_active and not force:
            self.stdout.write(self.style.ERROR(
                f'Term "{term.name}" is currently ACTIVE.\n'
                f'Use --force flag to close an active term, or set is_active=False first.'
            ))
            return

        # Show term statistics
        from enrollment.models import StudentSubject
        enrollments = StudentSubject.objects.filter(term=term)
        
        self.stdout.write(f'Term Details:')
        self.stdout.write(f'  • Name: {term.name}')
        self.stdout.write(f'  • Start Date: {term.start_date}')
        self.stdout.write(f'  • End Date: {term.end_date}')
        self.stdout.write(f'  • Active Status: {"ACTIVE" if term.is_active else "Inactive"}')
        self.stdout.write(f'  • Total Sections: {term.sections.count()}')
        self.stdout.write(f'  • Total Enrollments: {enrollments.count()}')
        self.stdout.write('')

        # Get system admin user for archiving
        admin_user = User.objects.filter(role='admin').first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('No admin user found. Cannot proceed with archiving.'))
            return

        # Confirm
        self.stdout.write(self.style.WARNING('⚠️  This will:'))
        self.stdout.write(f'  1. Set term is_active to False')
        self.stdout.write(f'  2. Archive all {enrollments.count()} enrollment records')
        self.stdout.write(f'  3. Archive all associated grades')
        self.stdout.write(f'  4. Create term metadata archive')
        self.stdout.write('')

        confirm = input('Type "CLOSE" to confirm: ')
        if confirm != 'CLOSE':
            self.stdout.write(self.style.ERROR('Operation cancelled.'))
            return

        # Close the term
        self.stdout.write('\nClosing term and archiving data...')
        success, message, archived_count = term.close_term(admin_user)

        if success:
            self.stdout.write(self.style.SUCCESS(f'\n✓ {message}'))
            self.stdout.write(self.style.SUCCESS(f'✓ Term "{term.name}" is now closed.'))
            self.stdout.write(self.style.SUCCESS(f'✓ Archived {archived_count} records.'))
        else:
            self.stdout.write(self.style.ERROR(f'\n✗ {message}'))

        self.stdout.write(f'\n{"="*60}\n')