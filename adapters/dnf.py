import subprocess
from typing import List
from models import App, PackageSource, UpdateStatus
from . import PackageAdapter

class DnfAdapter(PackageAdapter):
    def get_installed_apps(self) -> List[App]:
        apps = []
        try:
            # dnf list installed
            result = subprocess.run(
                ["dnf", "list", "installed", "--quiet"],
                capture_output=True, text=True, check=True
            )
            # Skip first line (header)
            lines = result.stdout.strip().split('\n')[1:]
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    pkg_name = parts[0].split('.')[0] # Remove architecture e.g. .x86_64
                    version = parts[1]
                    apps.append(App(
                        id=pkg_name,
                        name=pkg_name,
                        source=PackageSource.DNF,
                        version=version,
                        sandboxed=False
                    ))
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return apps

    def update_app(self, app_id: str) -> bool:
        try:
            subprocess.run(["pkexec", "dnf", "upgrade", "-y", app_id], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def remove_app(self, app_id: str) -> bool:
        try:
            subprocess.run(["pkexec", "dnf", "remove", "-y", app_id], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def search_apps(self, query: str) -> List[App]:
        return []
