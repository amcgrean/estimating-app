import re

with open('project/blueprints/main/routes.py', 'r') as f:
    content = f.read()

# Find all @main.route calls
matches = re.finditer(r'@main\.route\((.*?)\)', content)

for match in matches:
    start = match.end()
    # Check if next line contains @login_required
    next_block = content[start:start+100]
    if '@login_required' not in next_block:
        # Get route info
        route_text = match.group(0)
        line_num = content.count('\n', 0, match.start()) + 1
        print(f"Line {line_num}: {route_text}")
