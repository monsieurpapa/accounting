import os

template_dir = r"c:\Users\Yves Zigashane\Documents\Projects\accounting_project\src\templates"

for root, _, files in os.walk(template_dir):
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if '{% trans' in content or '{% blocktrans' in content:
                if '{% load i18n' not in content:
                    lines = content.split('\n')
                    inserted = False
                    for i, line in enumerate(lines):
                        if line.startswith('{% extends'):
                            lines.insert(i + 1, '{% load i18n %}')
                            inserted = True
                            break
                    if not inserted:
                        lines.insert(0, '{% load i18n %}')
                    
                    with open(path, 'w', encoding='utf-8') as file:
                        file.write('\n'.join(lines))
                    print(f"Fixed missing i18n in {os.path.basename(path)}")
