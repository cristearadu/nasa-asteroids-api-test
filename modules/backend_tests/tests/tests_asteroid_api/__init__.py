import os
import re


def find_test_functions(file_path):
    test_names = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'\s*def\s+(test_[a-zA-Z0-9_]+)', line)
            if match:
                test_names.append(match.group(1))
    return test_names


def main():
    for root, _, files in os.walk('.'):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                full_path = os.path.join(root, file)
                test_functions = find_test_functions(full_path)
                if test_functions:
                    filename_without_ext = os.path.splitext(file)[0]
                    print(f"{filename_without_ext}: {', '.join(test_functions)}")


if __name__ == "__main__":
    main()
