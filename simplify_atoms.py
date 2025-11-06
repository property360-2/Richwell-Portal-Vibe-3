#!/usr/bin/env python3
"""Simplify atomic component templates by removing single {% with %} wrappers."""

import os
import re

def simplify_single_with(content):
    """
    Remove single {% with %} wrappers from atomic component templates.
    This reduces nesting depth and prevents recursion issues in tests.
    """
    # Pattern to match a template that consists mainly of a single {% with %} block
    # that wraps the entire content
    pattern = r'^(.*?)(\{% with[^%]+%\}\s*)(.*?)(\s*\{% endwith %\}\s*)$'

    match = re.match(pattern, content, re.DOTALL)
    if match:
        header, with_tag, body, endwith = match.groups()

        # Check if this is a simple atomic component (no nested includes in the body that need the with variables)
        # For atomic components, we can usually just use the variables directly
        # Skip this optimization if the body has complex logic
        if 'include' not in body:
            # Extract variable mappings from the with tag
            with_content = with_tag.strip()[7:-2].strip()  # Remove '{% with' and '%}'

            # Replace variable references in the body
            for assignment in with_content.split():
                if '=' in assignment:
                    new_var, old_expr = assignment.split('=', 1)
                    new_var = new_var.strip()
                    old_expr = old_expr.strip()

                    # Simple variable reference (no filters)
                    if '|' not in old_expr and '"' not in old_expr:
                        body = body.replace('{{ ' + new_var + ' }}', '{{ ' + old_expr + ' }}')
                        body = body.replace('{% if ' + new_var + ' %}', '{% if ' + old_expr + ' %}')

            return header + body

    return content

def process_atomic_files():
    """Process only atomic component files that don't include other components."""
    atoms_dir = '/home/user/Richwell-Portal-Vibe-3/richwell/portal/templates/components/atoms'

    # Files that are safe to simplify (don't include other templates)
    safe_files = [
        'badge_render.html',
        'button_render.html',
        'textarea.html',
        'select.html',
        'radio.html',
        'checkbox.html',
        'toggle.html',
    ]

    for filename in safe_files:
        filepath = os.path.join(atoms_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()

            new_content = simplify_single_with(content)

            if new_content != content:
                with open(filepath, 'w') as f:
                    f.write(new_content)
                print(f'Simplified: {filename}')

if __name__ == '__main__':
    process_atomic_files()
