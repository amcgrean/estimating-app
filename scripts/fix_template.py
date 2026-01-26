
import os

path = r'C:\Users\amcgrean\python\pa-bid-request\project\templates\manage_fields.html'

try:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Check identifying line (Line 528 in 1-based index is 527 in 0-based)
    # Line 528 should be "    });\n"
    print(f"Checking line 528: {repr(lines[527] if len(lines) > 527 else 'EOF')}")
    
    # We want to keep up to line 528 (inclusive)
    # And replace the rest
    
    new_content = lines[:528]
    new_content.append("\n    </script>\n{% endblock %}\n")
    
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_content)
        
    print("File updated successfully.")
    
except Exception as e:
    print(f"Error: {e}")
