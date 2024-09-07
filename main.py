import argparse
import os
from redme_model import get_final_response, update_with_feedback
from code_reader_model import get_code_response
from dir_sticher_model import get_dir_response
from jupyteread import extract_code_cells_from_notebook
from cloner import clone_repository
import time
import pandas as pd
from tqdm import tqdm
import sys
import threading

class Spinner:
    def __init__(self, message="Loading", delay=0.1):
        self.message = message
        self.delay = delay
        self.running = False
        self.spinner = threading.Thread(target=self._animate)

    def _animate(self):
        chars = "|/-\\"
        while self.running:
            for char in chars:
                sys.stdout.write(f'\r{self.message} {char}')
                sys.stdout.flush()
                time.sleep(self.delay)

    def start(self):
        self.running = True
        self.spinner.start()

    def stop(self):
        self.running = False
        self.spinner.join()
        sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
        sys.stdout.flush()

def read_csv_file(file_path):
    try:
        df = pd.read_csv(file_path, header=None)
        return df.iloc[:, 0].tolist()
    except UnicodeDecodeError as e:
        print(f"Error decoding the file: {e}")
        return []

def read_existing_readme(repo_dir):
    readme_path = os.path.join(repo_dir, "README.md")
    if os.path.exists(readme_path):
        try:
            with open(readme_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading existing README.md: {e}")
    return ""

def check_and_clone_repository(repo_name):
    repo_dir = repo_name.split('/')[-1]
    target_dir = os.path.join("D:\\venv-test", repo_dir)
    
    if os.path.exists(target_dir):
        print(f"Repository '{repo_name}' is already cloned. Proceeding with existing directory.")
        return target_dir
    
    print(f"Cloning repository '{repo_name}'...")
    clone_repository(repo_name)
    return target_dir

def get_repo_path(args):
    if args.git:
        return check_and_clone_repository(args.git)
    elif args.local:
        if os.path.isdir(args.local):
            return os.path.abspath(args.local)
        else:
            print("The provided path is not a valid directory.")
            exit(1)
    else:
        print("Please provide either a Git repository URL or a local directory path.")
        exit(1)

def main():
    parser = argparse.ArgumentParser(description="Generate README for a Git repository or local directory.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--git", help="Git repository URL")
    group.add_argument("--local", help="Path to local directory")
    args = parser.parse_args()

    ignored_dir = read_csv_file(r'ignored_dir.csv')
    ignored_exts = read_csv_file(r'ignored_exts.csv')
    ignored_files = read_csv_file(r'ignored_files.csv')

    repo_dir = get_repo_path(args)

    user_desc_bool = input("Do you wish to describe what your codebase in brief? (y/n): ")

    if user_desc_bool.lower() == 'y':
        print("Please provide a brief description of your codebase")
        print("Please mention the licence as well if possible")
        user_description = input("-> ") 
    else:
        user_description = ""

    os.chdir(repo_dir)

    existing_readme = read_existing_readme(os.getcwd())
    
    dir_responses = {}

    for root, dirs, files in os.walk(os.getcwd()):
        dirs[:] = [d for d in dirs if d not in ignored_dir]
        filtered_files = [f for f in files if f not in ignored_files and not any(f.endswith(ext) for ext in ignored_exts)]

        print(f"Scanning directory: {root}")
        code_file_responses = {}

        with tqdm(total=len(filtered_files), desc="Reading files", unit="file") as pbar:
            for file_name in filtered_files:
                file_path = os.path.join(root, file_name)

                try:
                    if file_path.endswith('.ipynb'):
                        contents = extract_code_cells_from_notebook(file_path)
                    else:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            contents = file.read()
                    
                    if contents:    
                        spinner = Spinner(f"Processing {file_name}")
                        spinner.start()
                        model_response = get_code_response(file_name + contents)
                        spinner.stop()
                        code_file_responses[file_name] = model_response
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    code_file_responses[file_name] = f"File could not be read: {str(e)}"
                
                pbar.update(1)
                time.sleep(0.1)  # Small delay to make progress visible

        if code_file_responses:
            spinner = Spinner("Processing directory")
            spinner.start()
            dir_prompt = "\n".join([f"{file_name}: {code_description}" for file_name, code_description in code_file_responses.items()])
            dir_responses[root] = get_dir_response(dir_prompt)
            spinner.stop()

    readme_prompt = "\n".join([f"{dir_name}: {dir_description}" for dir_name, dir_description in dir_responses.items()])
    
    # Initial README generation
    spinner = Spinner("Generating initial README")
    spinner.start()
    initial_prompt = f"Generate a README for a GitHub repository with the following description and structure:\n\nDescription: {user_description}\n\nExisting README: {existing_readme}\n\nStructure: {readme_prompt}"
    readme_content = get_final_response(initial_prompt)
    spinner.stop()

    # Interactive README generation loop
    iteration = 1
    while True:
        # Save the generated README to a file
        readme_filename = f"README_v{iteration}.md"
        with open(readme_filename, 'w') as file:
            file.write(readme_content)
        
        print(f"\nREADME version {iteration} has been saved as {readme_filename}")
        print("Please review the file and provide feedback.")
        
        user_feedback = input("\nAre you satisfied with this README? (yes/no): ").lower()
        if user_feedback == 'yes':
            break
        
        print("\nPlease provide feedback or suggestions for improvement:")
        user_feedback = input()
        
        # Update README based on feedback
        spinner = Spinner(f"Updating README (iteration {iteration + 1})")
        spinner.start()
        feedback_prompt = f"Based on the following feedback, please improve the README:\n{user_feedback}"
        readme_content = update_with_feedback(feedback_prompt)
        spinner.stop()

        # Delete the previous version
        os.remove(readme_filename)
        
        iteration += 1

    # Rename or overwrite the final version as README.md
    final_readme = f"README_v{iteration}.md"
    if os.path.exists("README.md"):
        os.remove("README.md")
    os.rename(final_readme, "README.md")
    print(f"\nFinal README has been saved as README.md")
    print("README generation complete!")

    # Clean up any remaining version files
    for i in range(1, iteration):
        version_file = f"README_v{i}.md"
        if os.path.exists(version_file):
            os.remove(version_file)

if __name__ == "__main__":
    main()