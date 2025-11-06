# 🚀 Richwell School Portal - Quick Start Guide

This guide will help you get the Richwell School Portal up and running in minutes.

---

## 📋 Prerequisites

- Python 3.11+
- Git
- Basic knowledge of Django

---

## ⚡ Quick Setup (5 Steps)

### 1. Clone & Navigate
```bash
cd /home/user/Richwell-Portal-Vibe-3
```

### 2. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 3. Navigate to Django Project
```bash
cd richwell
```

### 4. Run Development Server
```bash
python manage.py runserver
```

### 5. Open Browser
Navigate to: **http://127.0.0.1:8000/**

---

## 🔑 Default Login Credentials

### Admin Access
- **Username**: `admin`
- **Password**: `admin123`
- **Dashboard**: http://127.0.0.1:8000/admin/

### Registrar
- **Username**: `registrar`
- **Password**: `registrar123`

### Dean
- **Username**: `dean`
- **Password**: `dean123`

### Admission Staff
- **Username**: `admission`
- **Password**: `admission123`

### Professor
- **Username**: `prof1` or `prof2`
- **Password**: `prof123`

### Student
- **Username**: `student1` or `student2`
- **Password**: `student123`

---

## 🎯 What to Try First

### As a Student (student1):
1. ✅ View your dashboard
2. ✅ Check enrolled subjects
3. ✅ Try enrolling in a new subject
4. ✅ View your grades

### As a Professor (prof1):
1. ✅ View your assigned sections
2. ✅ Check student roster
3. ✅ Enter grades for students
4. ✅ Try bulk grade upload

### As a Registrar:
1. ✅ Manage terms
2. ✅ Create/edit sections
3. ✅ Manage programs and curricula
4. ✅ View enrollment reports

### As an Admin:
1. ✅ Access Django admin panel
2. ✅ Manage users
3. ✅ Configure system settings
4. ✅ View audit trails

---

## 🛠️ Common Commands

### Database Operations
```bash
# Apply migrations
python manage.py migrate

# Create new migrations
python manage.py makemigrations

# Reset database (WARNING: Deletes all data!)
rm db.sqlite3
python manage.py migrate
python manage.py seed_data
```

### Data Management
```bash
# Seed initial data
python manage.py seed_data

# Create superuser
python manage.py createsuperuser
```

### Development
```bash
# Run tests
python manage.py test

# Check for issues
python manage.py check

# Collect static files (for production)
python manage.py collectstatic
```

### Django Shell
```bash
# Access Django shell
python manage.py shell

# Example: Get all students
from portal.models import Student
students = Student.objects.all()
for s in students:
    print(s.user.username, s.program.name)
```

---

## 📁 Important Files

### Configuration
- `richwell/settings.py` - Django settings
- `portal/urls.py` - URL routing
- `requirements.txt` - Python dependencies

### Backend
- `portal/models.py` - Database models
- `portal/views.py` - View functions
- `portal/services.py` - Business logic
- `portal/forms.py` - Form definitions

### Frontend
- `portal/templates/` - HTML templates

---

## 🔄 Workflow Examples

### Adding a New Student
1. Login as **admission** or **registrar**
2. Go to "Admission" → "Admit New Student"
3. Fill in student details
4. Assign program and curriculum
5. Student can now login

### Creating a New Section
1. Login as **registrar**
2. Go to "Sections" → "Create Section"
3. Select subject, term, professor
4. Set capacity and status
5. Section is now available for enrollment

### Enrolling a Student
1. Login as **student**
2. Go to "Enrollment"
3. Select available sections
4. System validates prerequisites and unit caps
5. Enrollment confirmed

### Entering Grades
1. Login as **professor**
2. View assigned sections
3. Click on a section to see student roster
4. Enter grades individually or bulk upload CSV
5. Grades are posted and visible to students

---

## 🐛 Troubleshooting

### Server Won't Start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Use different port
python manage.py runserver 8080
```

### Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Issues
```bash
# Check migrations
python manage.py showmigrations

# Apply pending migrations
python manage.py migrate
```

### No Sample Data
```bash
# Run seed command
python manage.py seed_data
```

---

## 📚 Learn More

### Django Documentation
- https://docs.djangoproject.com/

### Project Documentation
- `TODO.md` - Development roadmap
- `DEVELOPMENT_STATUS.md` - Current status and features

### Code Organization
```
portal/
├── models.py              # Database schema
├── views.py               # Request handlers
├── services.py            # Business logic
├── forms.py               # Form validation
├── decorators.py          # Access control
├── context_processors.py  # Template context
└── templates/             # HTML templates
```

---

## 🎓 Sample Data Overview

The `seed_data` command creates:

- **2 Programs**: Computer Science, Information Technology
- **2 Curricula**: CHED 2023 Rev for each program
- **6 Subjects**: CS101, CS102, CS201, IT101, IT102, GE101
- **6 Sections**: One section per subject
- **8 Users**: Admin, Registrar, Dean, Admission, 2 Professors, 2 Students
- **1 Term**: First Semester AY 2024-2025 (active)
- **System Settings**: Enrollment open, admission enabled, etc.

---

## 🚀 Next Steps

1. **Explore the Application**: Login with different roles
2. **Test Features**: Try enrolling, grading, reporting
3. **Read Documentation**: Check TODO.md for roadmap
4. **Customize**: Modify templates, add features
5. **Deploy**: Prepare for production (see Phase 8 in TODO.md)

---

## 💡 Tips

- **Development**: Always activate virtual environment first
- **Testing**: Use different user roles to test access control
- **Data**: Re-run `seed_data` to reset to initial state
- **Logs**: Check console for debug information
- **Admin Panel**: Use Django admin for quick data inspection

---

## 📞 Need Help?

Check these resources:
1. `DEVELOPMENT_STATUS.md` - Current status and features
2. `TODO.md` - Development roadmap and tasks
3. Code comments and docstrings
4. Django documentation

---

**Happy Coding! 🎉**

*The Richwell School Portal is ready for development and testing.*
