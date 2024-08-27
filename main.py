import argparse
import os
import subprocess
from sticher_model import get_final_response
from code_reader_model import get_code_response
from dir_sticher_model import get_dir_response
from jupyteread import extract_code_cells_from_notebook
from cloner import clone_repository
import time

def main():
    parser = argparse.ArgumentParser(description="Clone a GitHub repository and generate README.")
    parser.add_argument("repo_name", help="The name of the repository to clone (e.g., user/repo).")
    args = parser.parse_args()
    
    clone_repository(args.repo_name)
    repo_dir = args.repo_name.split('/')[-1]
    os.chdir(rf"D:\venv-test\{repo_dir}")

    ignored_dir = ['.git', '.streamlit', '.devcontainer']
    ignored_exts = ['.md', '.pth', '.avi', '.mp4', '.mp3', '.png','.jpg', '.jpeg', '.gif', '.cmd', '.svg', '.webp', '.class', '.lst', 
                    '.gitignore', '.gitattributes', '.csv']
    ignored_files = ['LICENSE', 'mnvw']
    dir_responses = {}

    for root, dirs, files in os.walk(os.getcwd()):
        dirs[:] = [d for d in dirs if d not in ignored_dir]
        filtered_files = [f for f in files if f not in ignored_files and not any(f.endswith(ext) for ext in ignored_exts)]

        print(f"Scanning directory: {root}")
        code_file_responses = {}

        for file_name in filtered_files:
            file_path = os.path.join(root, file_name)
            print(f"Reading file: {file_path}")

            try:

                if file_path.endswith('.ipynb'):
                    contents = extract_code_cells_from_notebook(file_path)
                else:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        contents = file.read()
                    
                if contents:    
                    print(f"reading {file_name}:")
                    print(". ")
                    model_response = get_code_response(file_name + contents)
                    print(". .")
                    code_file_responses[file_name] = model_response
                    print(". . .")
                    time.sleep(2)

                    
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        # Corrected iteration over code_file_responses
        if code_file_responses is not None:
            dir_prompt = "\n".join([f"{file_name}: {code_description}" for file_name, code_description in code_file_responses.items()])
        
        else:
            dir_prompt = ""

        if not dir_prompt:
            continue

        dir_responses[root] = get_dir_response(dir_prompt)
        time.sleep(2)
        print("- - -")

    readme_prompt = "\n".join([f"{dir_name}: {dir_description}" for dir_name, dir_description in dir_responses.items()])
    readme_content = get_final_response(readme_prompt)
    time.sleep(2)

    print("writing to file")
    with open('test.txt', 'w') as file:
        file.write(readme_content)
        print("done")
    
    print("the end!")

if __name__ == "__main__":
    main()