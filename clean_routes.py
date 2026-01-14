
import os

path = r"c:\Users\amcgrean\python\pa-bid-request\project\blueprints\main\routes.py"
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "@main.route('/debug/fix_and_upgrade')" in line:
        break
    new_lines.append(line)

# Trim trailing whitespace/newlines safely
while new_lines and not new_lines[-1].strip():
    new_lines.pop()
    
# Add one newline at end
new_lines.append("\n")

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
    
print("Cleaned main/routes.py")
