import re

def audit_routes(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Auditing {filepath}...\n")
    
    route_pattern = re.compile(r'@\w+\.route\(')
    login_required_pattern = re.compile(r'@login_required')
    
    routes_found = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if route_pattern.search(line):
            route_def = line
            line_num = i + 1
            has_login = False
            
            # Look ahead for decorators until def
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line.startswith('@'):
                    if login_required_pattern.search(next_line):
                        has_login = True
                elif next_line.startswith('def '):
                    func_name = next_line
                    break
                j += 1
            
            if not has_login:
                print(f"[UNSECURED?] Line {line_num}: {route_def} -> {func_name}")
            else:
                pass 
                # print(f"[SECURED] Line {line_num}: {route_def}")
                
        i += 1

if __name__ == "__main__":
    audit_routes('project/blueprints/main/routes.py')
