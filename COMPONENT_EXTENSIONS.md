# Component System Extensions

This document details the new components added to extend the Richwell Portal atomic design system.

## Table of Contents
1. [New Atoms](#new-atoms)
2. [New Organisms](#new-organisms)
3. [Migrated Dashboards](#migrated-dashboards)
4. [Testing](#testing)

---

## New Atoms

### Checkbox

Interactive checkbox input with label and description.

**File**: `components/atoms/checkbox.html`

**Props**:
- `name` (required): Field name
- `id`: Checkbox ID (defaults to name)
- `value`: Checkbox value (defaults to "on")
- `checked`: Whether checkbox is checked (boolean)
- `label`: Label text for the checkbox
- `disabled`: Whether checkbox is disabled (boolean)
- `required`: Whether field is required (boolean)
- `help_text`: Help text to display below checkbox
- `description`: Description text next to label

**Example**:
```django
{% include 'components/atoms/checkbox.html'
    with name='agree_terms'
    label='I agree to the terms and conditions'
    required=True %}

{% include 'components/atoms/checkbox.html'
    with name='newsletter'
    label='Subscribe to newsletter'
    description='Receive updates about new features'
    checked=True %}
```

---

### Radio Button

Radio button input for mutually exclusive selections.

**File**: `components/atoms/radio.html`

**Props**:
- `name` (required): Field name - must be same for all radios in group
- `id` (required): Radio button ID - must be unique
- `value` (required): Radio button value
- `checked`: Whether radio is checked (boolean)
- `label`: Label text for the radio button
- `disabled`: Whether radio is disabled (boolean)
- `required`: Whether field is required (boolean)
- `description`: Description text below label

**Example**:
```django
{% include 'components/atoms/radio.html'
    with name='payment_method'
    id='payment_card'
    value='card'
    label='Credit Card'
    checked=True %}

{% include 'components/atoms/radio.html'
    with name='payment_method'
    id='payment_cash'
    value='cash'
    label='Cash' %}

{% include 'components/atoms/radio.html'
    with name='payment_method'
    id='payment_paypal'
    value='paypal'
    label='PayPal'
    description='Pay securely with PayPal' %}
```

---

### Toggle Switch

Modern toggle switch with Alpine.js interactivity.

**File**: `components/atoms/toggle.html`

**Props**:
- `name` (required): Field name
- `id`: Toggle ID (defaults to name)
- `checked`: Whether toggle is on (boolean)
- `label`: Label text for the toggle
- `disabled`: Whether toggle is disabled (boolean)
- `size`: Size variant (sm, md, lg) - defaults to md
- `description`: Description text below label
- `on_label`: Text to show when toggle is ON (optional)
- `off_label`: Text to show when toggle is OFF (optional)

**Example**:
```django
{% include 'components/atoms/toggle.html'
    with name='notifications'
    label='Enable Notifications'
    checked=True %}

{% include 'components/atoms/toggle.html'
    with name='dark_mode'
    label='Dark Mode'
    size='lg'
    on_label='On'
    off_label='Off' %}

{% include 'components/atoms/toggle.html'
    with name='auto_save'
    label='Auto Save'
    description='Automatically save your work every 5 minutes' %}
```

---

## New Organisms

### Sortable Table

Advanced data table with sorting, searching, and pagination powered by Alpine.js.

**File**: `components/organisms/sortable_table.html`

**Props**:
- `headers` (required): List of header dicts with 'text' and 'sortable' keys
  - Example: `[{'text': 'Name', 'sortable': True, 'key': 'name'}, {'text': 'Status', 'sortable': False}]`
- `rows` (required): List of row data (list of lists or list of dicts)
- `title`: Optional table title
- `description`: Optional table description
- `empty_message`: Message when no data (defaults to "No data available")
- `striped`: Enable striped rows (boolean, defaults to False)
- `hoverable`: Enable hover effect (boolean, defaults to True)
- `actions`: Optional list of action buttons for each row
- `pagination`: Enable pagination (boolean, defaults to False)
- `per_page`: Number of rows per page (defaults to 10)
- `search`: Enable search functionality (boolean, defaults to False)

**Features**:
- Click column headers to sort
- Client-side search across all columns
- Pagination with page numbers
- Responsive design
- Interactive hover states

**Example**:
```django
{% with table_headers=list %}
    {% for header in table_headers %}
        {{ header }}  {# {'text': 'Student Name', 'sortable': True, 'key': 'name'} #}
    {% endfor %}
{% endwith %}

{% include 'components/organisms/sortable_table.html'
    with headers=table_headers
    rows=table_data
    title='Student Roster'
    striped=True
    hoverable=True
    search=True
    pagination=True
    per_page=20 %}
```

**JavaScript Data Format**:
```javascript
// Example row data structure
const rows = [
    ['John Doe', '2024001', 'BSCS', 3.5],
    ['Jane Smith', '2024002', 'BSIT', 3.8],
    // ... more rows
];

// Or as objects
const rows = [
    {name: 'John Doe', id: '2024001', program: 'BSCS', gpa: 3.5},
    {name: 'Jane Smith', id: '2024002', program: 'BSIT', gpa: 3.8},
];
```

---

### Advanced Form

Multi-step form with validation, progress tracking, and Alpine.js interactivity.

**File**: `components/organisms/advanced_form.html`

**Props**:
- `action` (required): Form action URL
- `method`: HTTP method (defaults to POST)
- `title`: Form title
- `description`: Form description
- `sections` (required): List of form sections with fields
  ```python
  sections = [
      {
          'title': 'Personal Info',
          'description': 'Enter your details',
          'fields': [
              {'type': 'text', 'name': 'first_name', 'label': 'First Name', 'required': True},
              {'type': 'email', 'name': 'email', 'label': 'Email'}
          ]
      }
  ]
  ```
- `multi_step`: Enable multi-step form (boolean, defaults to False)
- `submit_text`: Submit button text (defaults to "Submit")
- `cancel_url`: Cancel button URL (optional)
- `show_progress`: Show progress bar for multi-step (boolean, defaults to True)
- `client_validation`: Enable client-side validation (boolean, defaults to True)
- `confirm_before_submit`: Show confirmation dialog (boolean, defaults to False)

**Supported Field Types**:
- `text`, `email`, `password`, `number`, `date`, `tel`
- `textarea`
- `select`
- `checkbox`
- `radio`
- `toggle`

**Example**:
```django
{% with form_sections=list %}
    {# Section 1: Personal Information #}
    {% with section=dict %}
        {{ section.title }}  {# 'Personal Information' #}
        {{ section.fields }}  {# List of field dicts #}
    {% endwith %}

    {# Section 2: Account Details #}
    {% with section=dict %}
        {{ section.title }}  {# 'Account Details' #}
        {{ section.fields }}  {# List of field dicts #}
    {% endwith %}
{% endwith %}

{% include 'components/organisms/advanced_form.html'
    with action='/register/'
    title='Registration Form'
    sections=form_sections
    multi_step=True
    show_progress=True
    submit_text='Complete Registration' %}
```

**Field Configuration Examples**:
```python
# Text field
{'type': 'text', 'name': 'first_name', 'label': 'First Name', 'required': True}

# Email with help text
{'type': 'email', 'name': 'email', 'label': 'Email', 'help_text': 'We will never share your email'}

# Checkbox
{'type': 'checkbox', 'name': 'agree', 'label': 'I agree to terms', 'required': True}

# Radio buttons
{
    'type': 'radio',
    'name': 'gender',
    'label': 'Gender',
    'options': [
        {'id': 'gender_m', 'value': 'male', 'label': 'Male'},
        {'id': 'gender_f', 'value': 'female', 'label': 'Female'}
    ]
}

# Toggle switch
{'type': 'toggle', 'name': 'notifications', 'label': 'Enable Notifications', 'checked': True}

# Select dropdown
{
    'type': 'select',
    'name': 'country',
    'label': 'Country',
    'options': [
        {'value': 'us', 'label': 'United States'},
        {'value': 'uk', 'label': 'United Kingdom'}
    ]
}
```

---

## Migrated Dashboards

The following dashboard templates have been migrated to use the atomic design component system:

### 1. Professor Dashboard
**File**: `portal/templates/portal/professor_dashboard.html`

**Components Used**:
- `page_header`: Dashboard title and subtitle
- `stat_card`: Active sections, total students, all-time sections
- `badge`: Section status indicators (OPEN, FULL, CLOSED)
- `button`: View students and manage grades actions
- Data tables for current and recent sections

### 2. Registrar Dashboard
**File**: `portal/templates/portal/registrar_dashboard.html`

**Components Used**:
- `page_header`: Dashboard title
- `stat_card`: Total students, enrollments, sections
- `badge`: Enrollment status (Open/Closed), section status
- `alert`: Warning for missing active term
- `button`: Quick action buttons
- Data tables for sections and enrollments

### 3. Dean Dashboard
**File**: `portal/templates/portal/dean_dashboard.html`

**Components Used**:
- `page_header`: Dashboard title
- `stat_card`: Students, programs, INC grades
- `card`: Term information display
- Data tables for programs and INC grades
- `button`: Admin action buttons

### 4. Admission Dashboard
**File**: `portal/templates/portal/admission_dashboard.html`

**Components Used**:
- `page_header`: Dashboard title
- `card`: Program statistics display
- `badge`: Student status indicators
- `button`: User and student management actions
- Data table for recent students

---

## Testing

Comprehensive test suite has been added in `portal/tests.py`:

### Component Rendering Tests
Tests that verify each atomic component renders correctly:
- Button atom
- Badge atom
- Checkbox atom
- Radio atom
- Toggle atom
- Input atom
- Card molecule
- Alert molecule
- Form field molecule

### Model Tests
Tests for database models and their methods:
- User creation and roles
- Program creation
- Student methods (is_freshman)
- Term enrollment status
- Section enrollment counts
- Grade passing validation

### View Tests
Tests for URL routing and view access:
- Login page loads
- Dashboard authentication requirements
- Role-based dashboard access
- Logout functionality

### Form Tests
Tests for form validation:
- Enrollment form validation

### Integration Tests
End-to-end workflow tests:
- Complete enrollment workflow
- Grade submission workflow

**Running Tests**:
```bash
# Run all tests
python manage.py test portal

# Run specific test class
python manage.py test portal.ComponentRenderingTests

# Run specific test method
python manage.py test portal.ComponentRenderingTests.test_button_atom_renders

# Run with verbose output
python manage.py test portal --verbosity=2
```

---

## Summary of Changes

### New Components Added
1. **Checkbox atom** - Interactive checkbox inputs
2. **Radio atom** - Radio button selections
3. **Toggle atom** - Modern toggle switches
4. **Sortable Table organism** - Advanced data tables
5. **Advanced Form organism** - Multi-step forms

### Dashboards Migrated
1. Professor Dashboard
2. Registrar Dashboard
3. Dean Dashboard
4. Admission Dashboard

### Testing Infrastructure
- Complete test suite with 25+ tests
- Component rendering tests
- Model and view tests
- Integration tests

### Total Component Count
- **Atoms**: 13 (up from 10)
- **Molecules**: 8 (unchanged)
- **Organisms**: 9 (up from 7)
- **Total**: 30 components

---

## Next Steps

To continue extending the system:

1. **Add More Form Components**:
   - Date picker
   - Time picker
   - File upload
   - Rich text editor

2. **Create More Organisms**:
   - Modal dialogs
   - Sidebars
   - Wizards
   - Breadcrumb navigation

3. **Enhance Existing Components**:
   - Add loading states
   - Add skeleton loaders
   - Add tooltips
   - Add animations

4. **Migrate Remaining Templates**:
   - Login page
   - Enrollment page
   - Grade entry page
   - Section students page

5. **Add Component Showcase Page**:
   - Create a dedicated page to showcase all components
   - Add interactive examples
   - Provide copy-paste code snippets

6. **Expand Test Coverage**:
   - Add visual regression tests
   - Add accessibility tests
   - Add performance tests
   - Increase coverage to 90%+

---

## Best Practices

When using the extended component system:

1. **Always use semantic HTML** - Ensure proper accessibility
2. **Test interactivity** - Verify Alpine.js components work correctly
3. **Follow naming conventions** - Use consistent prop names
4. **Document new components** - Add examples and props
5. **Write tests** - Add component rendering tests for new components
6. **Keep components simple** - Each component should do one thing well
7. **Use progressive enhancement** - Ensure basic functionality without JavaScript
8. **Maintain consistency** - Follow existing patterns and styles

---

## Resources

- [Atomic Design Methodology](https://atomicdesign.bradfrost.com/)
- [Django Templates Documentation](https://docs.djangoproject.com/en/5.0/topics/templates/)
- [Alpine.js Documentation](https://alpinejs.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [HTMX Documentation](https://htmx.org/)

---

*Last Updated: January 2025*
