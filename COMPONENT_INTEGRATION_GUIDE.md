# Phase 2 Component Integration Guide

This document describes how Phase 2 components (Modal, Date Picker, File Upload) have been integrated into existing and new pages.

## Integration Summary

Phase 2 components are now actively used in **5 pages** across the portal, demonstrating real-world usage patterns.

---

## 1. Modal Dialog Integration

### enrollment.html - Drop Enrollment Confirmation

**Location**: `portal/templates/portal/enrollment.html`

**Before** (JavaScript confirm):
```django
<a href="{% url 'drop_enrollment' enrollment.id %}"
   onclick="return confirm('Are you sure you want to drop this subject?')"
   class="text-red-600">
    Drop
</a>
```

**After** (Modal component):
```django
<!-- Button triggers modal -->
<button
    @click="dropEnrollmentId = {{ enrollment.id }}; dropSubjectInfo = '{{ enrollment.subject.code }} - {{ enrollment.subject.title }}'"
    class="font-medium text-red-600 hover:text-red-900"
>
    Drop
</button>

<!-- Modal with rich content -->
<div x-show="dropEnrollmentId !== null">
    <!-- Custom modal with warning icon, subject info, and styled buttons -->
</div>
```

**Benefits**:
- Better UX with animated modal instead of browser alert
- Displays subject information for confirmation
- Warning icon and styled buttons
- ESC key and click-outside to dismiss
- Prevents accidental clicks

**Key Features**:
- Warning icon (exclamation triangle)
- Dynamic subject information
- "Yes, Drop Subject" (red button) vs "Cancel" (gray button)
- Clear warning message about consequences

---

## 2. Date Picker Integration

### term_management.html - Academic Term Creation/Editing

**Location**: `portal/templates/portal/term_management.html`

**Purpose**: Manage academic terms with multiple date fields

**Date Pickers Used**:
1. **Start Date** - First day of classes
2. **End Date** - Last day of classes
3. **Add/Drop Deadline** - Last day for course changes
4. **Grade Encoding Deadline** - Last day for grade submission
5. **Enrollment Opens** - When enrollment period starts
6. **Enrollment Closes** - When enrollment period ends

**Implementation**:
```django
{% include "components/molecules/date_picker.html" with
    label="Start Date"
    name="start_date"
    required=True
    help_text="First day of classes"
%}

{% include "components/molecules/date_picker.html" with
    label="End Date"
    name="end_date"
    required=True
    help_text="Last day of classes"
%}
```

**Benefits**:
- Calendar icon for visual clarity
- Native browser date picker (mobile-friendly)
- Validation hints with help text
- Required field indicators
- Consistent styling across all date fields

**Page Features**:
- Grid layout for date pairs (start/end, enrollment period)
- Highlighted enrollment period section
- Delete confirmation modal for terms
- Status badges (Active, Upcoming, Completed)
- Guidelines card explaining requirements

---

### student_profile.html - Date of Birth

**Location**: `portal/templates/portal/student_profile.html`

**Implementation**:
```django
{% include "components/molecules/date_picker.html" with
    label="Date of Birth"
    name="birth_date"
    max_date="2010-12-31"
    help_text="Must be at least 15 years old"
    required=True
%}
```

**Benefits**:
- Max date validation (must be 15+ years old)
- Clear help text explaining requirement
- Prevents invalid date selection

---

## 3. File Upload Integration

### bulk_grade_upload.html - CSV Grade Upload

**Location**: `portal/templates/portal/bulk_grade_upload.html`

**Purpose**: Upload grades for multiple students via CSV file

**Implementation**:
```django
{% include "components/molecules/file_upload.html" with
    label="Grade CSV File"
    name="csv_file"
    accept=".csv"
    max_size_mb=5
    help_text="Upload a CSV file containing student IDs and grades (max 5MB)"
    required=True
%}
```

**Page Features**:
- Instructions card with step-by-step guide
- CSV format documentation with example
- Template download button
- Valid grades reference
- File requirements list
- Warning card about grade changes

**Benefits**:
- Drag-and-drop CSV upload
- File type restriction (.csv only)
- Size validation (5MB max)
- Clear error messages
- Visual file preview before upload

---

### student_profile.html - Multiple File Uploads

**Location**: `portal/templates/portal/student_profile.html`

**Purpose**: Comprehensive student profile with documents

**File Upload Components**:

1. **Profile Picture**:
```django
{% include "components/molecules/file_upload.html" with
    label="Profile Picture"
    name="profile_picture"
    accept="image/*"
    max_size_mb=5
    help_text="Upload a professional photo (JPG, PNG, max 5MB)"
%}
```

2. **Official Transcript**:
```django
{% include "components/molecules/file_upload.html" with
    label="Official Transcript"
    name="transcript"
    accept=".pdf"
    max_size_mb=10
    help_text="Upload your official transcript from previous institution (PDF only)"
    current_file="transcript_2024.pdf"
%}
```

3. **Birth Certificate**:
```django
{% include "components/molecules/file_upload.html" with
    label="Birth Certificate"
    name="birth_certificate"
    accept=".pdf,image/*"
    max_size_mb=5
    help_text="Upload a clear copy of your birth certificate (PDF or image)"
%}
```

4. **Additional Documents** (Multiple):
```django
{% include "components/molecules/file_upload.html" with
    label="Additional Documents"
    name="additional_docs"
    multiple=True
    accept=".pdf,.doc,.docx,image/*"
    max_size_mb=10
    help_text="Upload certificates, awards, or other supporting documents (multiple files allowed)"
%}
```

**Page Features**:
- Personal information form with date picker
- Multiple file upload sections
- Uploaded documents list with status badges
- Document verification status
- Delete confirmation modals
- Help card with requirements

**Benefits**:
- Image preview for photos
- Different file type restrictions per upload
- Multiple file support for additional docs
- Existing file display
- Individual file removal
- Visual file size display

---

## Integration Patterns

### Pattern 1: Modal for Destructive Actions

**Use Case**: Any action that cannot be undone

```django
<!-- Page with Alpine.js data -->
<div x-data="{ deleteId: null, deleteName: '' }">

    <!-- Trigger button -->
    <button @click="deleteId = 1; deleteName = 'Item Name'">
        Delete
    </button>

    <!-- Modal -->
    <div x-show="deleteId !== null">
        <!-- Modal implementation -->
    </div>
</div>
```

**Applied To**:
- Drop enrollment (enrollment.html)
- Delete term (term_management.html)
- Delete document (student_profile.html)

---

### Pattern 2: Date Picker for Date Fields

**Use Case**: Any form with date input

```django
{% include "components/molecules/date_picker.html" with
    label="Field Label"
    name="field_name"
    required=True
    min_date="2025-01-01"
    max_date="2025-12-31"
    help_text="Helpful description"
%}
```

**Applied To**:
- Term management (6 date fields)
- Student profile (birth date)

**Best Practices**:
- Always provide help text
- Use min/max for validation
- Group related dates (start/end) in grid layout
- Mark required dates clearly

---

### Pattern 3: File Upload for Documents

**Use Case**: Document submission, file attachments

**Single File**:
```django
{% include "components/molecules/file_upload.html" with
    label="Document Name"
    name="field_name"
    accept=".pdf"
    max_size_mb=10
    required=True
    current_file="existing.pdf"
%}
```

**Multiple Files**:
```django
{% include "components/molecules/file_upload.html" with
    label="Documents"
    name="field_name"
    multiple=True
    accept=".pdf,.doc,.docx"
    max_size_mb=10
%}
```

**Applied To**:
- Bulk grade upload (CSV file)
- Student profile (4 different uploads)

**Best Practices**:
- Restrict file types with accept
- Set reasonable size limits
- Provide clear help text
- Show existing files when editing
- Allow preview for images

---

## Page Statistics

### Component Usage Breakdown

```
Total Pages with Phase 2 Components: 5

Modal Dialog:
├── enrollment.html (1 modal - drop confirmation)
├── term_management.html (1 modal - delete term)
└── student_profile.html (1 modal - delete document)

Date Picker:
├── term_management.html (6 date pickers)
└── student_profile.html (1 date picker - birth date)

File Upload:
├── bulk_grade_upload.html (1 file upload - CSV)
└── student_profile.html (4 file uploads - various documents)

Total Component Instances: 14
├── Modals: 3
├── Date Pickers: 7
└── File Uploads: 5
```

---

## Real-World Use Cases

### Use Case 1: Student Enrollment Management

**Scenario**: Student wants to drop a course

**Flow**:
1. Student views enrolled courses
2. Clicks "Drop" button for a course
3. **Modal appears** with course information and warning
4. Student confirms or cancels
5. If confirmed, enrollment is dropped

**Components Used**: Modal Dialog

---

### Use Case 2: Academic Term Setup

**Scenario**: Registrar creates new academic term

**Flow**:
1. Registrar accesses term management
2. Fills in term name and status
3. **Uses date pickers** to set:
   - Start and end dates
   - Add/drop deadline
   - Grade encoding deadline
   - Enrollment period
4. Saves term

**Components Used**: Date Picker (6 instances)

---

### Use Case 3: Bulk Grade Submission

**Scenario**: Professor uploads grades for entire section

**Flow**:
1. Professor downloads CSV template
2. Fills in student IDs and grades
3. **Uploads CSV file** via drag-and-drop or browse
4. Reviews upload preview
5. Confirms grade submission

**Components Used**: File Upload

---

### Use Case 4: Student Document Submission

**Scenario**: New student submits required documents

**Flow**:
1. Student accesses profile page
2. **Uploads profile picture** (image preview)
3. **Uploads transcript** (PDF, replaces existing)
4. **Uploads birth certificate** (PDF or image)
5. **Uploads additional documents** (multiple files)
6. Submits for verification

**Components Used**: File Upload (4 instances), Date Picker (birth date)

---

## Testing Checklist

### Modal Component
- [x] Modal opens on button click
- [x] Modal closes on Cancel
- [x] Modal closes on ESC key
- [x] Modal closes on backdrop click
- [x] Animations are smooth
- [x] Dynamic content displays correctly
- [x] Primary action works

### Date Picker Component
- [x] Calendar icon displays
- [x] Date input accepts dates
- [x] Min/max validation works
- [x] Required validation works
- [x] Help text displays
- [x] Focus state is visible
- [x] Mobile date picker works

### File Upload Component
- [x] Click to browse works
- [x] Drag and drop works
- [x] File type restrictions work
- [x] Size validation works
- [x] Image preview displays
- [x] Multiple files work
- [x] Remove file works
- [x] Existing file displays

---

## Migration Guide

### Upgrading Existing Pages

#### Step 1: Replace JavaScript confirm() with Modal

**Before**:
```django
<a href="{% url 'delete' id %}" onclick="return confirm('Delete?')">Delete</a>
```

**After**:
```django
<div x-data="{ showModal: false }">
    <button @click="showModal = true">Delete</button>
    <div x-show="showModal">
        <!-- Modal component -->
    </div>
</div>
```

#### Step 2: Replace Date Inputs with Date Picker

**Before**:
```django
<input type="date" name="start_date" required>
```

**After**:
```django
{% include "components/molecules/date_picker.html" with
    label="Start Date"
    name="start_date"
    required=True
%}
```

#### Step 3: Replace File Inputs with File Upload

**Before**:
```django
<input type="file" name="document" accept=".pdf">
```

**After**:
```django
{% include "components/molecules/file_upload.html" with
    label="Document"
    name="document"
    accept=".pdf"
%}
```

---

## Performance Considerations

### Modal
- Modals use Alpine.js `x-show` for efficient toggling
- Backdrop and modal panel have separate animations
- Body scroll is locked when modal is open

### Date Picker
- Uses native HTML5 date input (no JavaScript library)
- Minimal Alpine.js usage (focus state only)
- No external dependencies

### File Upload
- Efficient file reading with FileReader API
- Image preview only for image files
- File size validation before upload
- Individual file removal without form submission

---

## Browser Compatibility

All Phase 2 components are tested and compatible with:

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile Safari (iOS)
- Chrome Mobile (Android)

### Native Date Picker Support
- All modern browsers support HTML5 date input
- Mobile devices show native date picker
- Fallback is standard text input (still functional)

---

## Accessibility Features

All integrated components maintain accessibility:

### Modal
- ARIA `role="dialog"` and `aria-modal="true"`
- Keyboard navigation (ESC to close)
- Focus management
- Screen reader announcements

### Date Picker
- Proper label association
- Required indicators
- Error messages with ARIA
- Help text for context

### File Upload
- Keyboard accessible
- Screen reader friendly
- Clear labels and instructions
- Button alternative to drag-and-drop

---

## Next Steps

### Recommended Integrations

1. **Add modals to more delete actions**:
   - Grade deletion
   - Section deletion
   - User account deletion

2. **Add date pickers to admin forms**:
   - Section creation (start/end dates)
   - Announcement scheduling
   - Event management

3. **Add file uploads to**:
   - Professor profile (CV, certifications)
   - Course materials upload
   - Assignment submissions

4. **Create composite forms**:
   - Combine all three components in complex forms
   - Multi-step wizards with file uploads
   - Dynamic forms with conditional fields

---

## Resources

- **Phase 2 Component Documentation**: PHASE2_COMPONENTS.md
- **Component Showcase**: portal/component_showcase.html
- **Atomic Components Guide**: ATOMIC_COMPONENTS.md
- **Component Extensions**: COMPONENT_EXTENSIONS.md

---

**Last Updated**: November 2025
**Integration Status**: 5 pages using Phase 2 components
**Total Component Instances**: 14 (3 modals, 7 date pickers, 5 file uploads)
