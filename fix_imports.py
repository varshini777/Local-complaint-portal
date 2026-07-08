import os
import re

base_dir = 'd:/Local_complaint/backend/templates'
new_import = '{% from "components/macros.html" import form_field, empty_state, table_header, status_badge, priority_badge, escalation_badge with context %}'

for root, _, files in os.walk(base_dir):
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Find the macro import line
            if 'import form_field' in content and 'components/macros.html' in content:
                # Replace the whole import line with all macros
                new_content = re.sub(r'{%\s*from\s*"components/macros.html"\s*import\s*.*?%}', new_import, content)
                
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as file:
                        file.write(new_content)
                    print(f'Updated imports in {path}')
