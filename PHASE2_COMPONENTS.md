# Phase 2: Essential UI Components Documentation

This document describes the new essential UI components added in Phase 2 of the component system development.

## Overview

Phase 2 introduces three powerful, interactive components that enhance user experience and enable more sophisticated UI patterns:

1. **Modal/Dialog Organism** - For confirmations, forms in overlays
2. **Date Picker Molecule** - For enrollment dates, term management
3. **File Upload Molecule** - For transcripts, documents with drag-and-drop

All components are built with:
- **Alpine.js** for interactivity
- **Tailwind CSS** for styling
- **Accessibility** features (ARIA attributes, keyboard navigation)
- **Responsive design** for mobile and desktop
- **Reusability** through Django template includes

---

## Component Catalog

### 1. Modal/Dialog Organism

**Location**: `components/organisms/modal.html`

A flexible modal dialog component for displaying overlays, confirmations, forms, and content that requires user focus.

#### Features
- Multiple size options (sm, md, lg, xl, full)
- Dismissible or non-dismissible
- Keyboard navigation (ESC to close)
- Click outside to dismiss (optional)
- Smooth fade and slide animations
- Customizable header, body, and footer
- Accessible with proper ARIA attributes
- Alpine.js event system for open/close

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | string | "modal" | **Required**. Unique identifier for the modal |
| `title` | string | "" | Modal title displayed in header |
| `size` | string | "md" | Size: "sm" (400px), "md" (600px), "lg" (800px), "xl" (1000px), "full" (95vw) |
| `dismissible` | boolean | True | Allow dismissing by clicking outside or pressing ESC |
| `show_close` | boolean | True | Show close button (X) in header |
| `show_footer` | boolean | True | Show footer with action buttons |
| `primary_button_text` | string | "Confirm" | Text for primary action button |
| `secondary_button_text` | string | "Cancel" | Text for secondary action button |
| `primary_button_action` | string | "" | Alpine.js action for primary button (e.g., "handleSubmit()") |
| `secondary_button_action` | string | "" | Alpine.js action for secondary button |
| `content_html` | string | "" | HTML content for modal body |

#### Usage Examples

**Basic Confirmation Modal**

```django
<!-- In your template -->
<div x-data="{ showConfirm: false }">
  <button @click="showConfirm = true">Delete Item</button>

  <div x-show="showConfirm">
    {% include "components/organisms/modal.html" with
      id="deleteConfirm"
      title="Confirm Delete"
      size="sm"
      primary_button_text="Yes, Delete"
      secondary_button_text="Cancel"
      primary_button_action="handleDelete()"
    %}
  </div>
</div>

<script>
  function handleDelete() {
    // Your delete logic here
    alert('Item deleted');
  }
</script>
```

**Form Modal**

```django
<div x-data="{ showForm: false }">
  <button @click="showForm = true">Add New Entry</button>

  <div x-show="showForm">
    {% include "components/organisms/modal.html" with
      id="formModal"
      title="Create New Entry"
      size="md"
      primary_button_text="Save"
      secondary_button_text="Cancel"
    %}
  </div>
</div>

<!-- Set modal content via JavaScript -->
<script>
  document.addEventListener('alpine:initialized', () => {
    const modalContent = document.querySelector('#modal-formModal-content');
    if (modalContent) {
      modalContent.innerHTML = `
        <form>
          <div class="space-y-4">
            <input type="text" class="w-full px-3 py-2 border rounded" placeholder="Name">
            <textarea class="w-full px-3 py-2 border rounded" placeholder="Description"></textarea>
          </div>
        </form>
      `;
    }
  });
</script>
```

**Large Content Modal**

```django
<div x-data="{ showDetails: false }">
  <button @click="showDetails = true">View Details</button>

  <div x-show="showDetails">
    {% include "components/organisms/modal.html" with
      id="detailsModal"
      title="Detailed Information"
      size="lg"
      show_footer=False
    %}
  </div>
</div>
```

**Event-Based Modal Control**

```django
<!-- Trigger modal from anywhere using events -->
<button @click="$dispatch('open-modal-myModal')">Open Modal</button>
<button @click="$dispatch('close-modal-myModal')">Close Modal</button>

{% include "components/organisms/modal.html" with id="myModal" title="Event Modal" %}
```

#### Best Practices

1. **Use appropriate sizes**: Small for confirmations, medium for forms, large for detailed content
2. **Make non-critical modals dismissible**: Allow users to close by clicking outside or pressing ESC
3. **Use clear action button text**: "Delete", "Save", "Confirm" instead of generic "OK"
4. **Handle form submissions properly**: Validate before closing the modal
5. **Consider mobile experience**: Test on smaller screens, use responsive sizes

---

### 2. Date Picker Molecule

**Location**: `components/molecules/date_picker.html`

An enhanced date input component with calendar icon, validation, and user-friendly date selection.

#### Features
- Calendar icon for visual clarity
- Min/max date validation
- Required/optional field support
- Disabled state support
- Error and help text display
- Focus state with ring animation
- HTML5 date input (native browser picker)
- Accessible labels and ARIA attributes

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | string | - | **Required**. Field label |
| `name` | string | - | **Required**. Input name attribute |
| `id` | string | name | Input id attribute |
| `value` | string | "" | Current date value (YYYY-MM-DD format) |
| `placeholder` | string | "Select date" | Placeholder text |
| `required` | boolean | False | Whether field is required |
| `disabled` | boolean | False | Whether field is disabled |
| `min_date` | string | "" | Minimum selectable date (YYYY-MM-DD) |
| `max_date` | string | "" | Maximum selectable date (YYYY-MM-DD) |
| `error` | string | "" | Error message to display |
| `help_text` | string | "" | Helper text below field |
| `icon` | boolean | True | Show calendar icon |
| `autocomplete` | string | "" | Autocomplete attribute value |

#### Usage Examples

**Basic Date Picker**

```django
{% include "components/molecules/date_picker.html" with
  label="Start Date"
  name="start_date"
  required=True
  help_text="Select the term start date"
%}
```

**Date Range (Start and End)**

```django
<div class="grid grid-cols-2 gap-4">
  {% include "components/molecules/date_picker.html" with
    label="Start Date"
    name="start_date"
    required=True
  %}

  {% include "components/molecules/date_picker.html" with
    label="End Date"
    name="end_date"
    min_date="2025-01-01"
    required=True
  %}
</div>
```

**Date with Restrictions**

```django
{% include "components/molecules/date_picker.html" with
  label="Birth Date"
  name="birth_date"
  max_date="2010-12-31"
  help_text="Must be at least 15 years old"
  required=True
%}
```

**Date with Error State**

```django
{% include "components/molecules/date_picker.html" with
  label="Enrollment Date"
  name="enrollment_date"
  value=form.enrollment_date.value
  error=form.enrollment_date.errors.0
%}
```

**Disabled Date Field**

```django
{% include "components/molecules/date_picker.html" with
  label="Locked Date"
  name="locked_date"
  value="2025-06-15"
  disabled=True
  help_text="This date cannot be changed"
%}
```

#### Integration with Django Forms

```python
# forms.py
from django import forms

class TermForm(forms.Form):
    start_date = forms.DateField(
        label="Start Date",
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        label="End Date",
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
```

```django
<!-- In template -->
{% include "components/molecules/date_picker.html" with
  label="Start Date"
  name="start_date"
  value=form.start_date.value
  error=form.start_date.errors.0
  required=True
%}
```

#### Best Practices

1. **Use descriptive labels**: "Birth Date" instead of just "Date"
2. **Provide context with help text**: Explain what date is being selected
3. **Set reasonable min/max**: Prevent invalid date selections
4. **Display errors clearly**: Show validation errors from forms
5. **Consider timezone**: Handle timezone conversions on the backend

---

### 3. File Upload Molecule

**Location**: `components/molecules/file_upload.html`

A powerful drag-and-drop file upload component with preview, validation, and multi-file support.

#### Features
- Drag-and-drop file upload
- Click to browse files
- Image preview for uploaded images
- File type restrictions (accept attribute)
- File size validation
- Multiple file support
- File removal before submission
- Visual file size display
- Error and help text display
- Disabled state support
- Display current/existing files
- Accessible and keyboard friendly

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | string | - | **Required**. Field label |
| `name` | string | - | **Required**. Input name attribute |
| `id` | string | name | Input id attribute |
| `required` | boolean | False | Whether field is required |
| `disabled` | boolean | False | Whether field is disabled |
| `multiple` | boolean | False | Allow multiple file selection |
| `accept` | string | "" | File type restrictions (e.g., "image/*", ".pdf,.doc") |
| `max_size_mb` | number | 10 | Maximum file size in MB |
| `error` | string | "" | Error message to display |
| `help_text` | string | "" | Helper text below field |
| `show_preview` | boolean | True | Show image preview for uploaded images |
| `current_file` | string | "" | Current file name/url if editing |

#### Usage Examples

**Single Image Upload**

```django
{% include "components/molecules/file_upload.html" with
  label="Profile Picture"
  name="avatar"
  accept="image/*"
  max_size_mb=5
  help_text="Upload a profile picture (JPG, PNG, max 5MB)"
  required=True
%}
```

**Multiple Document Upload**

```django
{% include "components/molecules/file_upload.html" with
  label="Supporting Documents"
  name="documents"
  multiple=True
  accept=".pdf,.doc,.docx"
  max_size_mb=10
  help_text="Upload transcripts, certificates, etc. (PDF or Word, max 10MB each)"
%}
```

**PDF Upload with Current File**

```django
{% include "components/molecules/file_upload.html" with
  label="Official Transcript"
  name="transcript"
  accept=".pdf"
  current_file="transcript_2024.pdf"
  help_text="Replace existing transcript if needed"
%}
```

**File Upload with Error**

```django
{% include "components/molecules/file_upload.html" with
  label="Required Document"
  name="document"
  required=True
  error="Please upload a valid document"
  accept=".pdf"
%}
```

**Disabled File Upload**

```django
{% include "components/molecules/file_upload.html" with
  label="System File"
  name="system_file"
  disabled=True
  current_file="system_generated.pdf"
  help_text="This file is managed by the system"
%}
```

#### Integration with Django Forms

```python
# forms.py
from django import forms

class DocumentUploadForm(forms.Form):
    profile_picture = forms.ImageField(
        label="Profile Picture",
        required=False,
        help_text="Upload your profile picture"
    )

    transcript = forms.FileField(
        label="Official Transcript",
        required=True,
        help_text="Upload your official transcript (PDF only)"
    )

    supporting_docs = forms.FileField(
        label="Supporting Documents",
        required=False,
        widget=forms.FileInput(attrs={'multiple': True})
    )
```

```django
<!-- In template -->
<form method="post" enctype="multipart/form-data">
  {% csrf_token %}

  {% include "components/molecules/file_upload.html" with
    label="Profile Picture"
    name="profile_picture"
    accept="image/*"
    error=form.profile_picture.errors.0
  %}

  {% include "components/molecules/file_upload.html" with
    label="Official Transcript"
    name="transcript"
    accept=".pdf"
    required=True
    error=form.transcript.errors.0
  %}

  <button type="submit">Upload Files</button>
</form>
```

#### File Type Accept Values

| Value | Description |
|-------|-------------|
| `image/*` | All image types (JPEG, PNG, GIF, etc.) |
| `image/jpeg,image/png` | Only JPEG and PNG images |
| `.pdf` | Only PDF files |
| `.doc,.docx` | Only Word documents |
| `.pdf,.doc,.docx` | PDF and Word documents |
| `video/*` | All video types |
| `audio/*` | All audio types |

#### Best Practices

1. **Set appropriate file size limits**: Consider server and user constraints
2. **Restrict file types**: Use `accept` to limit file types for security
3. **Provide clear help text**: Explain what files are accepted
4. **Handle large files**: Consider chunked uploads for very large files
5. **Validate on server**: Always validate file type and size on the backend
6. **Show current files**: Display existing files when editing
7. **Allow file removal**: Let users remove files before submission
8. **Consider mobile**: Test file upload on mobile devices

---

## Component Showcase Page

A dedicated showcase page has been created to demonstrate all Phase 2 components in action.

**Location**: `portal/templates/portal/component_showcase.html`

**URL**: `/component-showcase/` (requires view and URL configuration)

The showcase page includes:
- Live examples of each component
- Interactive demonstrations
- Usage code snippets
- Implementation guides
- Best practices

---

## Integration Guide

### Adding to Existing Pages

#### Example: Add Date Picker to Enrollment Form

```django
<!-- Before -->
<div class="mb-6">
  <label for="enrollment_date" class="block text-gray-700 font-medium mb-2">
    Enrollment Date
  </label>
  <input type="date" id="enrollment_date" name="enrollment_date" class="w-full px-4 py-3 border border-gray-300 rounded-lg">
</div>

<!-- After -->
{% include "components/molecules/date_picker.html" with
  label="Enrollment Date"
  name="enrollment_date"
  required=True
  help_text="Select your preferred enrollment date"
%}
```

#### Example: Add File Upload to Student Profile

```django
<!-- Before -->
<div class="mb-6">
  <label for="transcript" class="block text-gray-700 font-medium mb-2">
    Upload Transcript
  </label>
  <input type="file" id="transcript" name="transcript" accept=".pdf">
</div>

<!-- After -->
{% include "components/molecules/file_upload.html" with
  label="Official Transcript"
  name="transcript"
  accept=".pdf"
  max_size_mb=10
  help_text="Upload your official transcript (PDF only)"
  required=True
%}
```

#### Example: Add Confirmation Modal to Delete Action

```django
<!-- Before -->
<a href="{% url 'delete_enrollment' enrollment.id %}"
   onclick="return confirm('Are you sure?')"
   class="text-red-600">
  Delete
</a>

<!-- After -->
<div x-data="{ showDelete: false }">
  <button @click="showDelete = true" class="text-red-600 hover:text-red-800">
    Delete
  </button>

  <div x-show="showDelete">
    {% include "components/organisms/modal.html" with
      id="deleteEnrollment"
      title="Confirm Delete"
      size="sm"
      primary_button_text="Yes, Delete"
      secondary_button_text="Cancel"
      primary_button_action="window.location.href='{% url 'delete_enrollment' enrollment.id %}'"
    %}
  </div>
</div>
```

---

## Testing Guidelines

### Manual Testing Checklist

#### Modal Component
- [ ] Modal opens and closes correctly
- [ ] ESC key closes dismissible modals
- [ ] Click outside closes dismissible modals
- [ ] Non-dismissible modals stay open
- [ ] All size variants render correctly
- [ ] Modal scrolls on small screens
- [ ] Animations are smooth
- [ ] Buttons trigger correct actions
- [ ] Content displays properly
- [ ] Accessible with keyboard navigation

#### Date Picker Component
- [ ] Calendar icon displays
- [ ] Date input accepts dates
- [ ] Min/max date validation works
- [ ] Required field validation works
- [ ] Error messages display correctly
- [ ] Help text displays
- [ ] Disabled state works
- [ ] Focus state is visible
- [ ] Mobile date picker works
- [ ] Date format is correct (YYYY-MM-DD)

#### File Upload Component
- [ ] Click to browse works
- [ ] Drag and drop works
- [ ] Multiple files work (when enabled)
- [ ] Image preview displays
- [ ] File size validation works
- [ ] File type restrictions work
- [ ] Remove file works
- [ ] Error messages display
- [ ] Help text displays
- [ ] Disabled state works
- [ ] Current file displays (when set)

### Browser Testing

Test all components in:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile Safari (iOS)
- Chrome Mobile (Android)

---

## Accessibility Features

All Phase 2 components are built with accessibility in mind:

### Modal
- ARIA `role="dialog"` and `aria-modal="true"`
- ARIA `aria-labelledby` for title
- Keyboard navigation (ESC to close)
- Focus trap (optional, to be added)
- Screen reader announcements

### Date Picker
- Proper `<label>` association
- Required indicator
- Error messages linked with ARIA
- Help text for context
- Native date input (browser accessibility)

### File Upload
- Proper `<label>` association
- Button alternative to drag-and-drop
- Keyboard accessible
- Screen reader friendly file list
- Clear error messages

---

## Performance Considerations

### Modal
- Lazy load modal content
- Use Alpine.js `x-show` instead of `v-if` for better performance
- Avoid nesting multiple modals
- Clean up event listeners on modal close

### Date Picker
- Uses native HTML5 date input (no JavaScript date library needed)
- Minimal Alpine.js usage for focus state only
- No external dependencies

### File Upload
- Efficient file reading with FileReader API
- Image preview only for image files
- File size validation before upload
- Consider chunked uploads for large files (backend implementation)

---

## Future Enhancements

### Planned for Phase 3+
1. **Modal Improvements**
   - Focus trap
   - Nested modals support
   - Animation customization
   - Modal position options (center, top, bottom)

2. **Date Picker Enhancements**
   - Custom date picker (replacing native)
   - Date range selection
   - Recurring date selection
   - Time picker integration

3. **File Upload Improvements**
   - Progress bar for uploads
   - Chunked file uploads
   - Direct upload to cloud storage
   - Image cropping/editing
   - Video preview

---

## Component Statistics

### Phase 2 Summary

```
Total New Components: 3
├── Organisms: 1 (modal)
├── Molecules: 2 (date_picker, file_upload)
└── Atoms: 0

Lines of Code: ~650
├── modal.html: ~200 lines
├── date_picker.html: ~100 lines
└── file_upload.html: ~350 lines

Features Added:
- Modal dialogs with 5 size variants
- Date picker with min/max validation
- Drag-and-drop file upload
- Image preview
- File size validation
- Multi-file support

Testing: Showcase page with live examples
```

### Overall Component System

```
Total Components: 34 (31 from Phase 1 + 3 from Phase 2)
├── Atoms: 14
├── Molecules: 10 (8 + 2 new)
└── Organisms: 10 (9 + 1 new)

Pages Using Components: 10/10 (100%)
Documentation: 4 comprehensive markdown files
Test Coverage: Component showcase + manual testing
```

---

## Support & Contribution

### Reporting Issues
- Check existing documentation first
- Test in latest browsers
- Provide code examples
- Include browser/OS information

### Contributing
- Follow existing component patterns
- Add comprehensive documentation
- Test on multiple browsers
- Update this documentation

---

## Changelog

### Phase 2 (Current)
- Added Modal/Dialog organism
- Added Date Picker molecule
- Added File Upload molecule
- Created component showcase page
- Added comprehensive documentation

### Phase 1
- Created atomic design system foundation
- Built 31 base components
- Migrated 10 portal pages
- Established component patterns

---

## Resources

- **Alpine.js Documentation**: https://alpinejs.dev/
- **Tailwind CSS Documentation**: https://tailwindcss.com/docs
- **Atomic Design Methodology**: https://atomicdesign.bradfrost.com/
- **WCAG 2.1 Guidelines**: https://www.w3.org/WAI/WCAG21/quickref/

---

**Last Updated**: November 2025
**Version**: 2.0
**Maintained by**: Component System Team
