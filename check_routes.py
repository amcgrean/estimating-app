import re

with open('project/blueprints/main/routes.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '@main.route' in line:
        # Check if next line has @login_required
        if i + 1 < len(lines):
            next_line = lines[i+1].strip()
            if not next_line.startswith('@login_required') and not next_line.startswith('@main.context_processor'):
                # Also check two lines down if multiple decorators might be used (rare here but safe)
                if i + 2 < len(lines) and next_line.startswith('@'):
                     next_next = lines[i+2].strip()
                     if not next_next.startswith('@login_required'):
                         print(f"Line {i+1}: {line.strip()} -> NEXT: {next_line}")
                else:
                    print(f"Line {i+1}: {line.strip()} -> NEXT: {next_line}")
