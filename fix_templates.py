#!/usr/bin/env python3
"""Fix multi-line {% with %} tags in Django templates."""

import re
import os

def fix_with_tag(content):
    """Convert multi-line {% with %} tags to single line."""
    # Pattern to match multi-line {% with %} tags
    pattern = r'{% with\n((?:\s+\w+=[^\n]+\n)+)%}'

    def replace_func(match):
        # Get the assignments part
        assignments = match.group(1)
        # Remove leading/trailing whitespace and newlines, keep only the assignments
        assignments = ' '.join(line.strip() for line in assignments.split('\n') if line.strip())
        # Return single-line version
        return f'{{% with {assignments} %}}'

    return re.sub(pattern, replace_func, content)

def process_file(filepath):
    """Process a single template file."""
    with open(filepath, 'r') as f:
        content = f.read()

    new_content = fix_with_tag(content)

    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f'Fixed: {filepath}')
        return True
    return False

def main():
    templates_dir = '/home/user/Richwell-Portal-Vibe-3/richwell/portal/templates'
    fixed_count = 0

    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                if process_file(filepath):
                    fixed_count += 1

    print(f'\nTotal files fixed: {fixed_count}')

if __name__ == '__main__':
    main()
