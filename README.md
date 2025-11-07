# 🎓 Richwell School Portal

A comprehensive school management system built with Django, HTMX, Alpine.js, and Tailwind CSS.

## 📋 Overview

The Richwell School Portal is a full-featured academic management system designed to handle:
- Student admissions and enrollment
- Academic records and grading
- Course and curriculum management
- Role-based access control (Students, Professors, Registrars, Deans, Admins)
- Audit trail and data archiving

## 🚀 Tech Stack

- **Backend**: Django 5.0+
- **Frontend**: HTMX, Alpine.js, Tailwind CSS (via CDN)
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **Authentication**: Django built-in with custom User model

## 📁 Project Structure

```
Richwell-Portal-Vibe-3/
├── rci/                    # Main Django project
│   ├── rci/               # Core settings and configuration
│   ├── users/             # User authentication and management
│   ├── academics/         # Academic programs and curriculum
│   ├── enrollment/        # Student enrollment system
│   ├── grades/            # Grading and evaluation
│   ├── audit/             # Audit trail tracking
│   └── settingsapp/       # System settings management
├── documentation/         # Project documentation
├── .env                   # Environment variables (not in git)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.10+
- pip
- virtualenv (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Richwell-Portal-Vibe-3
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env` (if available)
   - Or use the existing `.env` file
   - Update SECRET_KEY and other settings as needed

5. **Run migrations**
   ```bash
   cd rci
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## 👥 User Roles

The system supports the following user roles:
- **Student**: Access to personal records, enrollment, and grades
- **Professor**: Manage assigned classes and submit grades
- **Registrar**: Handle enrollment, academic records, and reporting
- **Dean**: Oversight of academic programs and approvals
- **Admission**: Process new student applications
- **Admin**: Full system access and configuration

## 📖 Development Phases

The project follows a structured development plan:
- **Phase 0**: Foundations ✅ (Current)
- **Phase 1**: Core Models & Database Integration
- **Phase 2**: Authentication & Role Management
- **Phase 3**: Admissions & Student Onboarding
- **Phase 4**: Enrollment Module
- **Phase 5**: Professors & Grading System
- **Phase 6**: Archiving, AuditTrail & Settings
- **Phase 7**: Reporting & Analytics
- **Phase 8**: Final QA & Deployment

See `documentation/phase.md` for detailed phase descriptions.

## 🔒 Security Notes

- Never commit `.env` file to version control
- Change SECRET_KEY in production
- Use PostgreSQL in production, not SQLite
- Enable HTTPS and proper security headers in production
- Regularly update dependencies

## 📝 License

[Specify your license here]

## 🤝 Contributing

[Add contribution guidelines if applicable]

## 📧 Contact

[Add contact information]
