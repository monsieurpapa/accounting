import os

template_dir = r"c:\Users\Yves Zigashane\Documents\Projects\accounting_project\src\templates"

for root, _, files in os.walk(template_dir):
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if '|crispy' in content and 'crispy_forms_tags' not in content:
                lines = content.split('\n')
                inserted = False
                for i, line in enumerate(lines):
                    if '{% load' in line:
                        lines.insert(i + 1, '{% load crispy_forms_tags %}')
                        inserted = True
                        break
                    elif '{% extends' in line:
                        lines.insert(i + 1, '{% load crispy_forms_tags %}')
                        inserted = True
                        break
                
                if not inserted:
                    lines.insert(0, '{% load crispy_forms_tags %}')
                
                with open(path, 'w', encoding='utf-8') as file:
                    file.write('\n'.join(lines))
                print(f"Fixed missing crispy loading in {os.path.basename(path)}")
