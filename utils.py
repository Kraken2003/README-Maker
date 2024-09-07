import pandas as pd
import os
import sys
import json
import subprocess 

def extract_code_cells_from_notebook(file_path):
    """
    Extracts code cells from a Jupyter notebook file.

    Args:
        file_path (str): The path to the Jupyter notebook file.

    Returns:
        str: A string containing the code from all code cells in the notebook, 
             separated by newline characters. If an error occurs, returns None.
    """
    
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
    """
    Reads a CSV file and returns its contents as a list.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        list: A list of values from the first column of the CSV file. 
              If an error occurs, returns an empty list.
    """

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
    """
    Clones a Git repository to a specified directory.

    Args:
        repo_name (str): The URL of the Git repository.
        root_dir (str): The directory where the repository will be cloned.

    Returns:
        None
    """

    url = f"{repo_name}"
    try:
        subprocess.run(["git", "clone", url], cwd=root_dir, check=True)
        print(f"Successfully cloned the repository: {repo_name}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone the repository. Error: {e}")
        raise

def read_existing_readme(repo_dir):
    """
    Reads the contents of an existing README.md file in a repository directory.

    Args:
        repo_dir (str): The directory of the repository.

    Returns:
        str: The contents of the README.md file. If the file does not exist, returns an empty string.
    """

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
    """
    Checks if a repository is already cloned, and clones it if not.

    Args:
        repo_name (str): The URL of the Git repository.
        root_dir (str): The directory where the repository will be cloned.

    Returns:
        str: The path to the cloned repository directory.

    """
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
    """
    Retrieves the path to a repository based on the provided arguments.

    Args:
        args (object): An object containing the command-line arguments.
            It should have the following attributes:
                - git (str): The URL of the Git repository.
                - root (str): The root directory for cloning Git repositories.
                - local (str): The path to a local directory.

    Returns:
        str: The path to the repository directory.
    """
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