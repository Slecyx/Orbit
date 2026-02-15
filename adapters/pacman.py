import subprocess
from typing import List
from models import App, PackageSource, UpdateStatus
from . import PackageAdapter

class PacmanAdapter(PackageAdapter):
    def get_installed_apps(self) -> List[App]:
        apps = []
        try:
            # pacman -Qe (Query explicitly installed packages)
            # Format: name version
            result = subprocess.run(
                ["pacman", "-Qe"],
                capture_output=True, text=True, check=True
            )
            for line in result.stdout.strip().split('\n'):
                parts = line.split()
                if len(parts) >= 2:
                    pkg_name, version = parts[0], parts[1]
                    apps.append(App(
                        id=pkg_name,
                        name=pkg_name,
                        source=PackageSource.PACMAN,
                        version=version,
                        sandboxed=False
                    ))
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return apps

    def update_app(self, app_id: str) -> bool:
        try:
            subprocess.run(["pkexec", "pacman", "-S", "--noconfirm", app_id], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def remove_app(self, app_id: str) -> bool:
        try:
            # pacman -Rs removes package and its unneeded dependencies
            subprocess.run(["pkexec", "pacman", "-Rs", "--noconfirm", app_id], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def search_apps(self, query: str) -> List[App]:
        return []

    def get_details(self, app: App) -> App:
        try:
            # pacman -Qi <package_name>
            result = subprocess.run(
                ["pacman", "-Qi", app.id],
                capture_output=True, text=True, check=True
            )
            
            info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            
            app.description = info.get('Description', app.description)
            app.license = info.get('Licenses', app.license)
            app.size = info.get('Installed Size', app.size)
            app.homepage = info.get('URL', app.homepage)
            app.developer = info.get('Packager', app.developer)
            app.installed_date = info.get('Install Date', app.installed_date)
            
        except subprocess.CalledProcessError:
            pass
        return app
