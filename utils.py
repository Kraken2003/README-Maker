import pandas as pd
import os
import sys
import json
import subprocess 

def extract_code_cells_from_notebook(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            notebook_data = json.load(f)
        
        code_blocks = []
        for cell in notebook_data['cells']:
            if cell['cell_type'] == 'code':
                code_blocks.append(''.join(cell['source']))
        
        return '\n\n'.join(code_blocks)
    
    except Exception as e:
        print(f"Error processing Jupyter notebook {file_path}: {e}")
        return None


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

def clone_repository(repo_name, root_dir):
    url = f"{repo_name}"
    try:
        subprocess.run(["git", "clone", url], cwd=root_dir, check=True)
        print(f"Successfully cloned the repository: {repo_name}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone the repository. Error: {e}")
        raise

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

def check_and_clone_repository(repo_name, root_dir):
    repo_dir = repo_name.split('/')[-1]
    target_dir = os.path.join(root_dir, repo_dir)
    
    if os.path.exists(target_dir):
        print(f"Repository '{repo_name}' is already cloned. Proceeding with existing directory.")
        return target_dir
    
    print(f"Cloning repository '{repo_name}'...")
    try:
        clone_repository(repo_name, root_dir)
        return target_dir
    except Exception as e:
        print(f"Error cloning repository: {e}")
        retry = input("Do you want to retry? (y/n): ")
        if retry.lower() == 'y':
            return check_and_clone_repository(repo_name, root_dir)
        else:
            print("Exiting due to cloning failure.")
            sys.exit(1)

def get_repo_path(args):
    if args.git:
        if not args.root:
            print("Please provide a root directory for cloning Git repositories.")
            exit(1)
        return check_and_clone_repository(args.git, args.root)
    elif args.local:
        if os.path.isdir(args.local):
            return os.path.abspath(args.local)
        else:
            print("The provided path is not a valid directory.")
            exit(1)
    else:
        print("Please provide either a Git repository URL or a local directory path.")
        exit(1)