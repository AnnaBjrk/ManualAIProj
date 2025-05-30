import os
import re
import sys

# python3 find_imports.py . om du står i directory
# python3 find_imports.py /path/to/your/project


def find_imports(directory='.'):
    imports = set()
    import_pattern = re.compile(r'^(?:import|from)\s+([a-zA-Z0-9_\.]+)')

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                try:
                    with open(os.path.join(root, file), 'r') as f:
                        for line in f:
                            match = import_pattern.match(line.strip())
                            if match:
                                imports.add(match.group(0))
                except (UnicodeDecodeError, IOError) as e:
                    print(f"Error reading {os.path.join(root, file)}: {e}")
                    continue

    return sorted(imports)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    for imp in find_imports(path):
        print(imp)
