# Atomic Design Component System

This project uses **Atomic Design** principles to create reusable, maintainable UI components. The component system is organized into three levels: **Atoms**, **Molecules**, and **Organisms**.

## Table of Contents
1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Atoms](#atoms)
4. [Molecules](#molecules)
5. [Organisms](#organisms)
6. [Usage Examples](#usage-examples)
7. [Best Practices](#best-practices)

---

## Overview

**Atomic Design** is a methodology for creating design systems with the following hierarchy:

- **Atoms**: Basic building blocks (buttons, inputs, labels)
- **Molecules**: Simple groups of atoms functioning together (form fields, cards)
- **Organisms**: Complex components combining molecules and atoms (navigation bars, forms, tables)

---

## Directory Structure

```
richwell/portal/templates/components/
├── atoms/
│   ├── button.html
│   ├── button_inner.html
│   ├── button_render.html
│   ├── input.html
│   ├── textarea.html
│   ├── select.html
│   ├── label.html
│   ├── badge.html
│   ├── badge_inner.html
│   └── badge_render.html
├── molecules/
│   ├── form_field.html
│   ├── card.html
│   ├── card_inner.html
│   ├── alert.html
│   ├── alert_inner.html
│   ├── info_item.html
│   ├── search_bar.html
│   └── stat_card.html
└── organisms/
    ├── navbar.html
    ├── footer.html
    ├── page_header.html
    ├── data_table.html
    ├── form.html
    ├── info_grid.html
    └── stat_grid.html
```

---

## Atoms

### Button
The most basic interactive element.

**File**: `components/atoms/button.html`

**Props**:
- `text` (required): Button text
- `type`: `primary|secondary|danger|success|warning|outline` (default: `primary`)
- `size`: `sm|md|lg` (default: `md`)
- `href`: URL for link buttons (optional)
- `onclick`: JavaScript onclick handler (optional)
- `disabled`: boolean (optional)

**Example**:
```django
{% include 'components/atoms/button.html' with text='Save' type='primary' size='md' %}
{% include 'components/atoms/button.html' with text='Cancel' type='secondary' href='/cancel/' %}
{% include 'components/atoms/button.html' with text='Delete' type='danger' disabled=True %}
```

---

### Input
Basic text input field.

**File**: `components/atoms/input.html`

**Props**:
- `name` (required): Input name attribute
- `type`: `text|email|password|number|date|tel` (default: `text`)
- `placeholder`: Placeholder text (optional)
- `value`: Input value (optional)
- `required`: boolean (optional)
- `disabled`: boolean (optional)
- `id`: Input ID (optional, defaults to name)

**Example**:
```django
{% include 'components/atoms/input.html' with name='email' type='email' placeholder='Enter email' required=True %}
```

---

### Textarea
Multi-line text input.

**File**: `components/atoms/textarea.html`

**Props**:
- `name` (required): Textarea name attribute
- `placeholder`: Placeholder text (optional)
- `value`: Textarea value (optional)
- `rows`: Number of rows (default: `4`)
- `required`: boolean (optional)
- `disabled`: boolean (optional)

**Example**:
```django
{% include 'components/atoms/textarea.html' with name='description' rows='6' placeholder='Enter description' %}
```

---

### Select
Dropdown selection field.

**File**: `components/atoms/select.html`

**Props**:
- `name` (required): Select name attribute
- `options` (required): List of options - each with `value` and `label`
- `selected`: Currently selected value (optional)
- `required`: boolean (optional)
- `disabled`: boolean (optional)

**Example**:
```django
{% with role_options=list %}
    {% include 'components/atoms/select.html' with name='role' options=role_options %}
{% endwith %}
```

---

### Label
Form field label.

**File**: `components/atoms/label.html`

**Props**:
- `text` (required): Label text
- `for`: Input ID this label is for (optional)
- `required`: boolean - shows asterisk (optional)

**Example**:
```django
{% include 'components/atoms/label.html' with text='Email Address' for='email' required=True %}
```

---

### Badge
Status or category indicator.

**File**: `components/atoms/badge.html`

**Props**:
- `text` (required): Badge text
- `type`: `success|danger|warning|info|primary|default` (default: `default`)
- `size`: `sm|md|lg` (default: `md`)
- `rounded`: boolean - fully rounded (default: `True`)

**Example**:
```django
{% include 'components/atoms/badge.html' with text='Active' type='success' size='sm' %}
{% include 'components/atoms/badge.html' with text='ADMIN' type='primary' %}
```

---

## Molecules

### Form Field
Complete form field with label, input, and error message.

**File**: `components/molecules/form_field.html`

**Props**:
- `label` (required): Field label
- `name` (required): Field name
- `type`: `text|email|password|number|date|tel|select|textarea` (default: `text`)
- `placeholder`: Placeholder text (optional)
- `value`: Field value (optional)
- `required`: boolean (optional)
- `error`: Error message (optional)
- `help_text`: Help text below field (optional)
- `options`: For select type - list of {value, label} (optional)
- `rows`: For textarea type - number of rows (optional)

**Example**:
```django
{% include 'components/molecules/form_field.html' with label='Email' name='email' type='email' required=True help_text='We will never share your email' %}
```

---

### Card
Container with optional title and subtitle.

**File**: `components/molecules/card.html`

**Props**:
- `title`: Card title (optional)
- `subtitle`: Card subtitle (optional)
- `padding`: `sm|md|lg` (default: `md`)
- `shadow`: boolean (default: `True`)

**Example**:
```django
{% include 'components/molecules/card.html' with title='Welcome' subtitle='Get started with your dashboard' %}
```

---

### Alert
Message notification box.

**File**: `components/molecules/alert.html`

**Props**:
- `message` (required): Alert message
- `type`: `success|error|warning|info` (default: `info`)
- `dismissible`: boolean (default: `False`)
- `title`: Alert title (optional)

**Example**:
```django
{% include 'components/molecules/alert.html' with message='Your changes have been saved!' type='success' dismissible=True %}
```

---

### Info Item
Label-value pair display.

**File**: `components/molecules/info_item.html`

**Props**:
- `label` (required): Item label
- `value` (required): Item value
- `icon`: Icon HTML (optional)
- `badge_type`: Type for value badge display (optional)

**Example**:
```django
{% include 'components/molecules/info_item.html' with label='Student ID' value='12345' %}
{% include 'components/molecules/info_item.html' with label='Status' value='Active' badge_type='success' %}
```

---

### Search Bar
Search input with button.

**File**: `components/molecules/search_bar.html`

**Props**:
- `name`: Input name (default: `search`)
- `placeholder`: Placeholder text (default: `Search...`)
- `value`: Current search value (optional)
- `button_text`: Search button text (default: `Search`)

**Example**:
```django
{% include 'components/molecules/search_bar.html' with placeholder='Search students...' %}
```

---

### Stat Card
Statistics display card.

**File**: `components/molecules/stat_card.html`

**Props**:
- `label` (required): Stat label
- `value` (required): Stat value
- `icon`: Icon HTML (optional)
- `change`: Percentage change (optional)
- `change_type`: `up|down` (optional)
- `color`: `primary|success|danger|warning` (default: `primary`)

**Example**:
```django
{% include 'components/molecules/stat_card.html' with label='Total Students' value='1,234' color='primary' change='+12%' change_type='up' %}
```

---

## Organisms

### Navbar
Navigation bar with branding and user info.

**File**: `components/organisms/navbar.html`

**Props**:
- `brand_text`: Brand text (default: `Richwell School Portal`)
- `user`: Current user object (optional)
- `logout_url`: Logout URL (optional)

**Example**:
```django
{% include 'components/organisms/navbar.html' with user=request.user %}
```

---

### Footer
Page footer with copyright and links.

**File**: `components/organisms/footer.html`

**Props**:
- `copyright_text`: Copyright text (default: auto-generated)
- `links`: List of footer links {text, href} (optional)

**Example**:
```django
{% include 'components/organisms/footer.html' %}
```

---

### Page Header
Page title with breadcrumbs and action button.

**File**: `components/organisms/page_header.html`

**Props**:
- `title` (required): Page title
- `subtitle`: Page subtitle (optional)
- `action_button`: Button config {text, href, type} (optional)
- `breadcrumbs`: List of {text, href} for breadcrumbs (optional)

**Example**:
```django
{% include 'components/organisms/page_header.html' with title='Dashboard' subtitle='Welcome back!' %}
```

---

### Data Table
Reusable data table component.

**File**: `components/organisms/data_table.html`

**Props**:
- `headers` (required): List of header names
- `rows` (required): List of row data - each row is a list of cell data
- `empty_message`: Message when no data (default: `No data available`)
- `striped`: boolean - alternating row colors (default: `False`)
- `hoverable`: boolean - highlight on hover (default: `True`)

**Example**:
```django
{% with headers=list_headers rows=table_rows %}
    {% include 'components/organisms/data_table.html' with headers=headers rows=rows hoverable=True %}
{% endwith %}
```

---

### Form
Complete form with fields and submit button.

**File**: `components/organisms/form.html`

**Props**:
- `action` (required): Form action URL
- `method`: `GET|POST` (default: `POST`)
- `fields` (required): List of field configs
- `submit_text`: Submit button text (default: `Submit`)
- `cancel_url`: Cancel button URL (optional)
- `form_id`: Form ID attribute (optional)

**Example**:
```django
{% with form_fields=fields_list %}
    {% include 'components/organisms/form.html' with action='/submit/' fields=form_fields submit_text='Save' %}
{% endwith %}
```

---

### Info Grid
Grid of information items.

**File**: `components/organisms/info_grid.html`

**Props**:
- `items` (required): List of info items - each with {label, value, icon, badge_type}
- `columns`: Number of columns (default: `2`)
- `title`: Grid title (optional)

**Example**:
```django
{% with info_items=student_info %}
    {% include 'components/organisms/info_grid.html' with items=info_items columns=2 title='Student Information' %}
{% endwith %}
```

---

### Stat Grid
Grid of statistics cards.

**File**: `components/organisms/stat_grid.html`

**Props**:
- `stats` (required): List of stat items
- `columns`: Number of columns (default: `4`)
- `title`: Grid title (optional)

**Example**:
```django
{% with statistics=stats_list %}
    {% include 'components/organisms/stat_grid.html' with stats=statistics columns=4 %}
{% endwith %}
```

---

## Usage Examples

### Example 1: Simple Form

```django
{% extends "portal/base.html" %}

{% block content %}
<div class="max-w-2xl mx-auto">
    {% include 'components/organisms/page_header.html' with title='Login' subtitle='Welcome back!' %}

    <div class="bg-white rounded-lg shadow p-6">
        <form action="{% url 'login' %}" method="POST">
            {% csrf_token %}

            {% include 'components/molecules/form_field.html' with label='Email' name='email' type='email' required=True %}
            {% include 'components/molecules/form_field.html' with label='Password' name='password' type='password' required=True %}

            <div class="flex gap-3 mt-6">
                {% include 'components/atoms/button.html' with text='Login' type='primary' %}
                {% include 'components/atoms/button.html' with text='Forgot Password?' type='outline' href='/forgot-password/' %}
            </div>
        </form>
    </div>
</div>
{% endblock %}
```

---

### Example 2: Dashboard with Stats

```django
{% extends "portal/base.html" %}

{% block content %}
{% include 'components/organisms/page_header.html' with title='Admin Dashboard' %}

{# Stats Grid #}
<div class="mb-6">
    {% include 'components/molecules/stat_card.html' with label='Total Students' value='1,234' color='primary' %}
</div>

{# Info Cards #}
<div class="bg-white rounded-lg shadow p-6">
    <h3 class="text-xl font-semibold mb-4">System Information</h3>
    <div class="grid grid-cols-2 gap-4">
        {% include 'components/molecules/info_item.html' with label='Version' value='1.0.0' %}
        {% include 'components/molecules/info_item.html' with label='Status' value='Active' badge_type='success' %}
    </div>
</div>
{% endblock %}
```

---

## Best Practices

### 1. **Component Composition**
Build complex UIs by composing smaller components:
```django
{# Good: Compose molecules from atoms #}
{% include 'components/molecules/form_field.html' with ... %}

{# Bad: Hardcoding HTML #}
<div><label>...</label><input>...</div>
```

### 2. **Consistent Styling**
Always use component props for styling rather than custom CSS:
```django
{# Good #}
{% include 'components/atoms/button.html' with type='primary' size='lg' %}

{# Bad #}
<button class="custom-blue-btn">...</button>
```

### 3. **Reusability**
Create new molecules/organisms when you find repeated patterns:
```django
{# If you're repeating this pattern, create a new molecule #}
{% include 'components/atoms/label.html' ... %}
{% include 'components/atoms/input.html' ... %}
{% include 'components/atoms/badge.html' ... %}
```

### 4. **Prop Validation**
Always provide required props and use defaults for optional ones:
```django
{# Good #}
{% include 'components/atoms/button.html' with text='Click Me' %}

{# Bad - missing required prop #}
{% include 'components/atoms/button.html' %}
```

### 5. **Template Comments**
Use Django template comments to document component usage:
```django
{# Using Button Atom Component #}
{% include 'components/atoms/button.html' with text='Submit' type='primary' %}
```

---

## Migration Guide

### Converting Existing Templates

**Before**:
```django
<button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
    Submit
</button>
```

**After**:
```django
{% include 'components/atoms/button.html' with text='Submit' type='primary' %}
```

---

## Contributing

When creating new components:

1. **Place them in the correct directory** (atoms/molecules/organisms)
2. **Document all props** in the component file header
3. **Provide usage examples** in this documentation
4. **Follow naming conventions**: descriptive, lowercase with underscores
5. **Keep components focused**: Each component should do one thing well

---

## Component Hierarchy

```
Organisms
    ├── Molecules
    │   ├── Atoms
    │   └── Atoms
    └── Molecules
        └── Atoms
```

**Remember**:
- Atoms are standalone
- Molecules combine atoms
- Organisms combine molecules and atoms
- Pages combine organisms, molecules, and atoms

---

## Support

For questions or issues with the component system, please:
1. Check this documentation first
2. Review component source files for inline documentation
3. Contact the development team

---

**Last Updated**: November 2025
**Version**: 1.0.0
