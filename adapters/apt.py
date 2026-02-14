import subprocess
from typing import List
from models import App, PackageSource, UpdateStatus
from . import PackageAdapter

class AptAdapter(PackageAdapter):
    def get_installed_apps(self) -> List[App]:
        apps = []
        try:
            # Using dpkg-query for faster listing of installed packages
            result = subprocess.run(
                ["dpkg-query", "-W", "-f=${Package}\t${Version}\t${Description}\n"],
                capture_output=True, text=True, check=True
            )
            for line in result.stdout.strip().split('\n'):
                parts = line.split('\t')
                if len(parts) >= 2:
                    pkg_name, version = parts[0], parts[1]
                    summary = parts[2] if len(parts) > 2 else ""
                    # Filter for GUI apps usually involves checking .desktop files, 
                    # but for MVP we list packages. 
                    # Note: Listing ALL apt packages might be too many. 
                    # We might want to filter for 'Section: utils/games/graphics' etc later.
                    apps.append(App(
                        id=pkg_name,
                        name=pkg_name,
                        source=PackageSource.APT,
                        version=version,
                        summary=summary,
                        sandboxed=False
                    ))
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return apps

    def update_app(self, app_id: str) -> bool:
        # Requires root. Using pkexec for PolicyKit integration.
        try:
            subprocess.run(["pkexec", "apt-get", "install", "--only-upgrade", "-y", app_id], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def remove_app(self, app_id: str) -> bool:
        try:
            subprocess.run(["pkexec", "apt-get", "remove", "-y", app_id], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def search_apps(self, query: str) -> List[App]:
        return []
