# pyscan/detector.py
import os
import subprocess
import sys
from typing import List, Set
import glob # Useful for path matching

from .utils import run_subprocess # Use our helper for external commands
# from .environment import Environment # Don't import Environment here, detector only finds paths
# from .introspector import introspect_environment # Don't import introspector here

# Define common executable names
PYTHON_EXECUTABLES = ["python", "python3"]
if sys.platform == "win32":
    PYTHON_EXECUTABLES = [f"{name}.exe" for name in PYTHON_EXECUTABLES]
    # Windows might also have python.bat, python.cmd in some older setups, but .exe is standard

def _is_executable(path: str) -> bool:
    """Checks if a path is a file and is executable."""
    return os.path.isfile(path) and os.access(path, os.X_OK)

def _find_in_path() -> Set[str]:
    """Finds Python executables available in the system's PATH."""
    executables = set()
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)

    print("Searching PATH...")
    for path_dir in path_dirs:
        bin_dir = path_dir.strip()
        if not bin_dir or not os.path.isdir(bin_dir):
            continue

        for name in PYTHON_EXECUTABLES:
            exec_path = os.path.join(bin_dir, name)
            if _is_executable(exec_path):
                executables.add(os.path.normcase(exec_path)) # Normalize paths early for easier handling/comparison later

    print(f"Found {len(executables)} executables in PATH.")
    return executables

def _find_pyenv_executables() -> Set[str]:
    """Finds Python executables managed by pyenv."""
    executables = set()
    pyenv_root = os.path.join(os.path.expanduser("~"), ".pyenv")
    versions_dir = os.path.join(pyenv_root, "versions")

    if not os.path.isdir(versions_dir):
        # print(f"Pyenv versions directory not found: {versions_dir}") # Optional debug
        return executables # Pyenv not installed or not in standard location

    print(f"Searching pyenv versions in {versions_dir}...")

    # Find standard pyenv versions (e.g., ~/.pyenv/versions/3.9.18/bin/python)
    version_glob = os.path.join(versions_dir, "*", "bin")
    for bin_dir in glob.glob(version_glob):
        for name in PYTHON_EXECUTABLES:
            exec_path = os.path.join(bin_dir, name)
            if _is_executable(exec_path):
                 executables.add(os.path.normcase(exec_path))


    # Find pyenv virtualenvs (e.g., ~/.pyenv/versions/3.9.18/envs/myenv/bin/python)
    # Also covers ~/.pyenv/envs/myenv (standalone pyenv-virtualenv)
    virtualenv_glob1 = os.path.join(versions_dir, "*", "envs", "*", "bin")
    virtualenv_glob2 = os.path.join(pyenv_root, "envs", "*", "bin")

    for bin_dir_glob in [virtualenv_glob1, virtualenv_glob2]:
        for bin_dir in glob.glob(bin_dir_glob):
             for name in PYTHON_EXECUTABLES:
                 exec_path = os.path.join(bin_dir, name)
                 if _is_executable(exec_path):
                      executables.add(os.path.normcase(exec_path))

    # Alternative/Additional: Use `pyenv virtualenvs --bare` output
    # This might be more robust if pyenv structure changes or is non-standard
    try:
        # Use run_subprocess helper
        pyenv_output = run_subprocess(["pyenv", "virtualenvs", "--bare"], capture_output=True, text=True, check=True, timeout=10)
        # Each line is a path to a pyenv virtualenv's root directory
        venv_roots = pyenv_output.stdout.strip().splitlines()
        print(f"Found {len(venv_roots)} pyenv virtualenvs via `pyenv virtualenvs --bare`.")
        for venv_root in venv_roots:
            bin_dir = os.path.join(venv_root, "bin")
            for name in PYTHON_EXECUTABLES:
                exec_path = os.path.join(bin_dir, name)
                if _is_executable(exec_path):
                    executables.add(os.path.normcase(exec_path))

    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        # pyenv command not found or failed - just means we rely on the glob search
        print(f"Could not run `pyenv virtualenvs --bare`: {e}. Relying on filesystem scan for pyenv.")
    except Exception as e:
         print(f"An unexpected error occurred while running `pyenv virtualenvs --bare`: {e}.")


    print(f"Found {len(executables)} potential pyenv executables.")
    return executables


def _find_conda_executables() -> Set[str]:
    """Finds Python executables managed by conda."""
    executables = set()

    # Use `conda info --envs` output
    try:
        # Use run_subprocess helper
        # Need to be careful about environments/shells where `conda` is not directly available in PATH
        # We might need to find the base conda executable first.
        # For simplicity initially, assume `conda` is in PATH.
        # A more robust version would try finding common conda install locations first.
        print("Searching for conda environments via `conda info --envs`...")
        conda_output = run_subprocess(["conda", "info", "--envs"], capture_output=True, text=True, check=True, timeout=10)

        # Parse output: lines are typically 'name   path' or '# name   path' for active env
        # Example:
        # # conda environments:
        # #
        # base                  * /home/user/miniconda3
        # myenv                    /home/user/miniconda3/envs/myenv
        # another_env              /opt/conda/envs/another_env
        env_lines = conda_output.stdout.strip().splitlines()

        # Find the line starting with 'base' or the path lines below the 'envs:' header
        parsing_envs = False
        for line in env_lines:
            line = line.strip()
            if not line or line.startswith('#'):
                 if "# conda environments:" in line:
                      parsing_envs = True
                 continue # Skip comments and empty lines

            if parsing_envs:
                # Split by whitespace, the last part is the path
                parts = line.split()
                if parts:
                    env_path = parts[-1]
                    bin_dir = os.path.join(env_path, "bin") # 'Scripts' on Windows
                    if sys.platform == "win32":
                         bin_dir = os.path.join(env_path, "Scripts") # Conda puts exes in Scripts on Windows

                    for name in PYTHON_EXECUTABLES:
                        exec_path = os.path.join(bin_dir, name)
                        if _is_executable(exec_path):
                            executables.add(os.path.normcase(exec_path))

        print(f"Found {len(executables)} potential conda executables.")
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
         print(f"Could not run `conda info --envs`: {e}. Skipping conda environment detection via command.")
    except Exception as e:
         print(f"An unexpected error occurred while running `conda info --envs`: {e}.")


    # Fallback/Additional: Scan common conda install locations directly if command failed
    # This is less reliable than `conda info` but better than nothing.
    # Common locations: ~/minicondaX, ~/anacondaX, /opt/conda, /usr/local/conda
    # And envs within those: <conda_root>/envs/*
    # Let's skip this manual scan for brevity unless `conda info` is proven unreliable.


    return executables

def _find_pipx_executables() -> Set[str]:
    """Finds Python executables managed by pipx."""
    executables = set()
    pipx_venvs_root = os.path.join(os.path.expanduser("~"), ".local", "pipx", "venvs")

    if not os.path.isdir(pipx_venvs_root):
        # print(f"Pipx venvs directory not found: {pipx_venvs_root}") # Optional debug
        return executables # Pipx not installed or no packages installed

    print(f"Searching pipx venvs in {pipx_venvs_root}...")

    # Pipx creates a venv for each installed application
    # The executable is usually inside the venv's bin/Scripts directory
    pipx_glob = os.path.join(pipx_venvs_root, "*")
    for venv_root in glob.glob(pipx_glob):
        bin_dir = os.path.join(venv_root, "bin")
        if sys.platform == "win32":
             bin_dir = os.path.join(venv_root, "Scripts") # Pipx uses Scripts on Windows

        for name in PYTHON_EXECUTABLES:
            exec_path = os.path.join(bin_dir, name)
            if _is_executable(exec_path):
                executables.add(os.path.normcase(exec_path))

    print(f"Found {len(executables)} potential pipx executables.")
    return executables


# --- Main Detection Function ---

def find_python_executables() -> List[str]:
    """
    Finds all potential Python executable paths across the system.

    Combines results from PATH, pyenv, conda, pipx, etc.
    Returns a list of unique, normalized executable paths.
    """
    all_executables: Set[str] = set()

    # Find executables from different sources
    all_executables.update(_find_in_path())
    all_executables.update(_find_pyenv_executables())
    all_executables.update(_find_conda_executables())
    all_executables.update(_find_pipx_executables())

    # Convert set to list and sort for consistent order (optional)
    sorted_executables = sorted(list(all_executables))

    print(f"\nTotal unique potential Python executables found: {len(sorted_executables)}")
    return sorted_executables


# Example usage (for testing/demonstration)
if __name__ == "__main__":
    print("--- Starting Python Executable Detection ---")
    found_execs = find_python_executables()
    print("\nFound Executable Paths:")
    if found_execs:
        for exec_path in found_execs:
            print(f"- {exec_path}")
    else:
        print("No Python executables found.")
    print("--- Detection Complete ---")