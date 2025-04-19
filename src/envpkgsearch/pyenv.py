# src/envpkgsearch/envs/pyenv.py
import os
from pathlib import Path
import pandas as pd

# This is the default path for pyenv installations.
# we are also making following assumings about the versions directory(which is the default behavior  
# for pyenv installations): 
# 1. The versions directory is inside the pyenv root directory. 
# 2. The versions directory contains a directory for each python version or env installed by pyenv.
PYENV_ROOT_DEFAULT = Path.home() / ".pyenv"
PYENV_ROOT: Path = Path(os.getenv("PYENV_ROOT", PYENV_ROOT_DEFAULT))
PYENV_VERSIONS_DIR_NAME: str =  "versions"
PYENV_VERSIONS_DIR = PYENV_ROOT / PYENV_VERSIONS_DIR_NAME


# prefixes are dirs inside the versions dir
# and each prefix is a python version or env installed by pyenv
# here we are assuming following structure for python inside each prefix:
# prefix/
#   ├── bin
#   │   ├── python -> python3.x or base_prefix/bin/python3.x(which is base_in_path)
#   │   └── python3
#   ├── lib
#   │   └── python3.x/site-packages
#   └── pyvenv.cfg
class PythonEnv():
    def __init__(self, prefix):
        self.prefix = prefix
        self.name: str = self.prefix.name
        self.bin_path = Path(self.prefix) / "bin" / "python"
        self.base_bin_path: Path = self.bin_path.resolve()
        # self.base_bin_name: str = self.base_bin_path.name
        self.base_prefix = self.base_bin_path.parent.parent
        self.creator: str = "pyenv"
        self.is_venv: bool = self.prefix.is_symlink()
        self.site_packages: Path = self.prefix / "lib" / self.base_bin_path.name / "site-packages"
    def __repr__(self):
        return f"PythonEnv(name={self.name}, bin_path={self.bin_path}, creator={self.creator}, is_venv={self.is_venv}"

    def get_bin_base_path(self):
        pass
        




# # This function returns a list of dictionaries representing the pyenv environments.
# # Each dictionary contains the name, type, and path of the environment.
# def get_pyenv_envs(versions_dir: Path = PYENV_VERSIONS_DIR) -> list:
#     envs = []
#     if versions_dir.exists():
#         for version in versions_dir.iterdir():
#             python_bin = version / "bin" / "python"
#             if python_bin.exists():
#                 envs.append({"name": version.name, "type": "pyenv", "path": python_bin})
#     return envs
 

class PyenvPathConfig():

    def __init__(self):
        self.pyenv_root = PYENV_ROOT
        self.versions_dir = PYENV_VERSIONS_DIR
        self.python_prefixes = [prefix for prefix in self.versions_dir.iterdir()]
        self.envs = [PythonEnv(version) for version in self.python_prefixes]


DEDAULT_PYENV_PATH_CONFIG = PyenvPathConfig()


if __name__ == "__main__":
    dppc = DEDAULT_PYENV_PATH_CONFIG
    envs = dppc.envs
    for env in envs:
        print(f"Name: {env.name}, Is venv: {env.is_venv}, Path: {env.bin_path}, Creator: {env.creator}")
    print(f"Pyenv root: {dppc.pyenv_root}")
    print(f"Versions dir: {dppc.versions_dir}")
    print(f"Python prefixes: {dppc.python_prefixes}")  
    python_envs_data = [env.__dict__ for env in envs]
    df = pd.DataFrame(python_envs_data)  
    print(df)