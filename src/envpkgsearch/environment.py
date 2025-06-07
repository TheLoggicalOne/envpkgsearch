from dataclasses import dataclass, field
from typing import List, Dict, Any
import time

@dataclass
class Environment:
    id: str          # Unique ID, e.g., hash or cleaned path
    creator: str        # "system", "pyenv", "conda", "venv", "pipx", "unknown"
    path: str        # Prefix path of the environment
    executable: str  # Path to the python executable
    version: str     # Python version string
    site_packages_dirs: List[str] # List of directories where packages are installed
    user_site_dir: str | None # User site-packages directory, if applicable
    base_prefix: str # Base prefix (used to check for venv)
    detected_packages: Dict[str, Dict[str, str]] = field(default_factory=dict) # {package_name: {"version": "x.y.z", "location": "path/to/dist-info"}}
    last_scan_time: float = 0.0 # Timestamp of last package scan

    def __hash__(self):
        return hash(self.id) # Make it hashable for sets/dicts

    def __eq__(self, other):
        if not isinstance(other, Environment):
            return False
        return self.id == other.id

    def to_dict(self) -> Dict[str, Any]:
        """Convert Environment object to a dictionary for caching."""
        return {
            "id": self.id,
            "creator": self.creator,
            "path": self.path,
            "executable": self.executable,
            "version": self.version,
            "site_packages_dirs": self.site_packages_dirs,
            "user_site_dir": self.user_site_dir,
            "base_prefix": self.base_prefix,
            "detected_packages": self.detected_packages,
            "last_scan_time": self.last_scan_time
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Environment':
        """Create Environment object from a dictionary loaded from cache."""
        return Environment(
            id=data["id"],
            creator=data["creator"],
            path=data["path"],
            executable=data["executable"],
            version=data["version"],
            site_packages_dirs=data["site_packages_dirs"],
            user_site_dir=data.get("user_site_dir"), # Use .get for backward compatibility
            base_prefix=data.get("base_prefix", data["path"]), # Default to path if missing
            detected_packages=data.get("detected_packages", {}),
            last_scan_time=data.get("last_scan_time", 0.0)
        )
    
    @staticmethod
    def from_bin_path(bin_path: str) -> 'Environment':
        pass

     