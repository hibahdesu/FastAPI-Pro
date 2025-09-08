import os

EXCLUDE_DIRS = {'__pycache__', '.git', '.venv', 'env', '.idea'}

def print_tree(start_path, file, prefix=''):
    entries = [e for e in os.listdir(start_path) if e not in EXCLUDE_DIRS]
    entries.sort()
    for i, entry in enumerate(entries):
        path = os.path.join(start_path, entry)
        connector = "├── " if i < len(entries) - 1 else "└── "
        file.write(prefix + connector + entry + '\n')
        if os.path.isdir(path):
            extension = "│   " if i < len(entries) - 1 else "    "
            print_tree(path, file, prefix + extension)

# ✅ Use UTF-8 encoding
with open("project_structure.txt", "w", encoding="utf-8") as f:
    print_tree('.', f)

print("✅ Project structure saved to project_structure.txt")
