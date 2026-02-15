import os
import subprocess
from typing import List
from models import App, PackageSource, UpdateStatus
from . import PackageAdapter

class FlatpakAdapter(PackageAdapter):
    def get_installed_apps(self) -> List[App]:
        apps = []
        try:
            # --columns=application,name,version,options
            result = subprocess.run(
                ["flatpak", "list", "--columns=application,name,version,options"],
                capture_output=True, text=True, check=True
            )
            for line in result.stdout.strip().split('\n'):
                if not line: continue
                parts = line.split('\t')
                if len(parts) >= 3:
                    app_id, name, version = parts[0], parts[1], parts[2]
                    options = parts[3] if len(parts) > 3 else ""
                    apps.append(App(
                        id=app_id,
                        name=name,
                        source=PackageSource.FLATPAK,
                        version=version,
                        sandboxed=True # Flatpaks are sandboxed by default
                    ))
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return apps

    def update_app(self, app_id: str) -> bool:
        try:
            subprocess.run(["flatpak", "update", "-y", app_id], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def remove_app(self, app_id: str) -> bool:
        try:
            subprocess.run(["flatpak", "uninstall", "-y", app_id], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def search_apps(self, query: str) -> List[App]:
        apps = []
        try:
            # flatpak search --columns=application,name,version,description
            result = subprocess.run(
                ["flatpak", "search", "--columns=application,name,version,description", query],
                capture_output=True, text=True, check=True
            )
            for line in result.stdout.strip().split('\n'):
                if not line: continue
                parts = line.split('\t')
                if len(parts) >= 2:
                    app_id = parts[0]
                    name = parts[1]
                    version = parts[2] if len(parts) > 2 else ""
                    desc = parts[3] if len(parts) > 3 else ""
                    
                    apps.append(App(
                        id=app_id,
                        name=name,
                        source=PackageSource.FLATPAK,
                        version=version,
                        summary=desc,
                        sandboxed=True,
                        is_installed=False
                    ))
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return apps

    def install_app(self, app_id: str) -> bool:
        try:
            # flatpak install -y flathub <app_id>
            # Assuming flathub is the remote, but better to let flatpak resolve it or use user interaction for remote selection if ambiguous.
            # Using --noninteractive -y
            subprocess.run(["flatpak", "install", "-y", "--noninteractive", app_id], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def get_details(self, app: App) -> App:
        try:
            # flatpak info <app_id>
            # We can use specific columns to make parsing easier
            # flatpak info --show-metadata <app_id> is XML, maybe too complex.
            # flatpak info <app_id> is human readable.
            
            # Let's try to just capture the output and parse commonly
            result = subprocess.run(
                ["flatpak", "info", app.id],
                capture_output=True, text=True, check=True
            )
            
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'License':
                        app.license = value
                    elif key == 'Origin':
                        app.developer = value # Close enough? Or 'maintaner' isn't usually there.
                    elif key == 'Installed':
                         # value is size usually? "1.2 GB"
                         app.size = value
            
            # Description is not easily available in 'flatpak info' simpler output.
            # We might need 'appstream-util' or similar if we want rich descriptions for flatpaks locally.
            # But flatpak list provided it during search.
            # If search populated it, we are good.
            
        except subprocess.CalledProcessError:
            pass
        return app
