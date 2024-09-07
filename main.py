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
        print(f"Error decoding the file {file_path}: {e}")
    except pd.errors.EmptyDataError:
        print(f"The file {file_path} is empty.")
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred while reading {file_path}: {e}")
    return []

def read_existing_readme(repo_dir):
    readme_path = os.path.join(repo_dir, "README.md")
    try:
        with open(readme_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print("No existing README.md found.")
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
    try:
        clone_repository(repo_name)
        return target_dir
    except Exception as e:
        print(f"Error cloning repository: {e}")
        retry = input("Do you want to retry? (y/n): ")
        if retry.lower() == 'y':
            return check_and_clone_repository(repo_name)
        else:
            print("Exiting due to cloning failure.")
            sys.exit(1)

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
    ignored_files.append('LICENSE')

    repo_dir = get_repo_path(args)

    user_desc_bool = input("Do you wish to describe what your codebase in brief? (y/n): ")

    if user_desc_bool.lower() == 'y':
        print("Please provide a brief description of your codebase")
        print("Please mention the licence as well if possible")
        user_description = input("-> ") 
    else:
        user_description = ""

    try:
        os.chdir(repo_dir)
    except FileNotFoundError:
        print(f"The directory {repo_dir} does not exist.")
        sys.exit(1)
    except PermissionError:
        print(f"Permission denied to access {repo_dir}.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while changing to {repo_dir}: {e}")
        sys.exit(1)

    existing_readme = read_existing_readme(os.getcwd())
    
    dir_responses = {}

    try:
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
                            
                        elif file_path.endswith('.csv'):
                            df = pd.read_csv(file_path, nrows=2)
                            contents = df.to_string(index=False)

                        else:
                            with open(file_path, 'r', encoding='utf-8') as file:
                                contents = file.read()
                        
                        if contents:    
                            spinner = Spinner(f"Processing {file_name}")
                            spinner.start()
                            try:
                                model_response = get_code_response(file_name + contents)
                            except Exception as e:
                                print(f"Error getting code response for {file_name}: {e}")
                                time.sleep(2)  # Wait for 2 seconds before continuing
                                model_response = f"Error processing file: {str(e)}"
                            finally:
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
                try:
                    dir_prompt = "\n".join([f"{file_name}: {code_description}" for file_name, code_description in code_file_responses.items()])
                    dir_responses[root] = get_dir_response(dir_prompt)
                except Exception as e:
                    print(f"Error getting directory response for {root}: {e}")
                    time.sleep(2)  # Wait for 2 seconds before continuing
                    dir_responses[root] = f"Error processing directory: {str(e)}"
                finally:
                    spinner.stop()

    except Exception as e:
        print(f"An error occurred while walking through the directory: {e}")
        sys.exit(1)

    readme_prompt = "\n".join([f"{dir_name}: {dir_description}" for dir_name, dir_description in dir_responses.items()])
    
    # Initial README generation
    spinner = Spinner("Generating initial README")
    spinner.start()
    try:
        initial_prompt = f"Generate a README for a GitHub repository with the following description and structure:\n\nDescription: {user_description}\n\nExisting README: {existing_readme}\n\nStructure: {readme_prompt}"
        readme_content = get_final_response(initial_prompt)
    except Exception as e:
        print(f"Error generating initial README: {e}")
        time.sleep(2)  # Wait for 2 seconds before retrying
        try:
            readme_content = get_final_response(initial_prompt)
        except Exception as e:
            print(f"Failed to generate README after retry: {e}")
            sys.exit(1)
    finally:
        spinner.stop()

    # Interactive README generation loop
    iteration = 1
    while True:
        # Save the generated README to a file
        readme_filename = f"README_v{iteration}.md"
        try:
            with open(readme_filename, 'w', encoding='utf-8') as file:
                file.write(readme_content)
        except Exception as e:
            print(f"Error writing README to file: {e}")
            continue

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
        try:
            feedback_prompt = f"Based on the following feedback, please improve the README:\n{user_feedback}"
            readme_content = update_with_feedback(feedback_prompt)
        except Exception as e:
            print(f"Error updating README: {e}")
            time.sleep(2)  # Wait for 2 seconds before retrying
            try:
                readme_content = update_with_feedback(feedback_prompt)
            except Exception as e:
                print(f"Failed to update README after retry: {e}")
                break
        finally:
            spinner.stop()

        # Delete the previous version
        try:
            os.remove(readme_filename)
        except Exception as e:
            print(f"Error removing previous README version: {e}")

        iteration += 1

    # Rename or overwrite the final version as README.md
    final_readme = f"README_v{iteration}.md"
    try:
        if os.path.exists("README.md"):
            os.remove("README.md")
        os.rename(final_readme, "README.md")
        print(f"\nFinal README has been saved as README.md")
    except Exception as e:
        print(f"Error saving final README: {e}")

    print("README generation complete!")

    # Clean up any remaining version files
    for i in range(1, iteration):
        version_file = f"README_v{i}.md"
        if os.path.exists(version_file):
            try:
                os.remove(version_file)
            except Exception as e:
                print(f"Error removing {version_file}: {e}")

if __name__ == "__main__":
    main()