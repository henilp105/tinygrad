import os

def search_and_replace(root_dir, search_str, replace_str):
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            file_path = os.path.join(subdir, file)
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                if search_str in content:
                    print(f"String '{search_str}' found in file: {file_path}")
                    response = input("Do you want to replace it? (yes/no): ").strip().lower()
                    if response == 'yes':
                        new_content = content.replace(search_str, replace_str)
                        with open(file_path, 'w') as f:
                            f.write(new_content)
                        print(f"Replaced '{search_str}' with '{replace_str}' in file: {file_path}")
            except Exception as e:
                print(f"Could not read file {file_path}: {e}")

if __name__ == "__main__":
    repo_path = '.'  # Root directory of the repo
    search_str = input("Enter the string to search: ").strip()
    replace_str = input("Enter the string to replace with: ").strip()

    search_and_replace(repo_path, search_str, replace_str)
