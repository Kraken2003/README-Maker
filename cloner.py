import subprocess

def clone_repository(repo_name):
    url = f"{repo_name}"
    try:
        subprocess.run(["git", "clone", url], cwd=r"D:\venv-test", check=True)
        print(f"Successfully cloned the repository: {repo_name}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone the repository. Error: {e}")