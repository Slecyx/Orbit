import subprocess
from typing import List
from models import App, PackageSource, UpdateStatus
from . import PackageAdapter

class SnapAdapter(PackageAdapter):
    def get_installed_apps(self) -> List[App]:
        apps = []
        try:
            # snap list
            result = subprocess.run(
                ["snap", "list"],
                capture_output=True, text=True, check=True
            )
            # Skip header line
            lines = result.stdout.strip().split('\n')[1:]
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    name, version, rev = parts[0], parts[1], parts[2]
                    apps.append(App(
                        id=name,
                        name=name.capitalize(),
                        source=PackageSource.SNAP,
                        version=version,
                        sandboxed=True # Snaps are sandboxed
                    ))
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return apps

    def update_app(self, app_id: str) -> bool:
        try:
            subprocess.run(["pkexec", "snap", "refresh", app_id], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def remove_app(self, app_id: str) -> bool:
        try:
            subprocess.run(["snap", "remove", app_id], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def search_apps(self, query: str) -> List[App]:
        apps = []
        try:
            # snap find "query"
            result = subprocess.run(
                ["snap", "find", query],
                capture_output=True, text=True, check=True
            )
            # Skip header
            lines = result.stdout.strip().split('\n')[1:]
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[0]
                    version = parts[1]
                    # summary is the rest
                    summary = " ".join(parts[3:]) if len(parts) > 3 else ""
                    
                    apps.append(App(
                        id=name,
                        name=name.capitalize(),
                        source=PackageSource.SNAP,
                        version=version,
                        summary=summary,
                        sandboxed=True,
                        is_installed=False
                    ))
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return apps

    def install_app(self, app_id: str) -> bool:
        try:
            subprocess.run(["pkexec", "snap", "install", app_id], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def get_details(self, app: App) -> App:
        try:
            # snap info <name>
            result = subprocess.run(
                ["snap", "info", app.id],
                capture_output=True, text=True, check=True
            )
            
            lines = result.stdout.split('\n')
            description_started = False
            description = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('license:'):
                    app.license = line.split(':', 1)[1].strip()
                elif line.startswith('publisher:'):
                    app.developer = line.split(':', 1)[1].strip().split()[0] # often 'Publisher Name (username)'
                elif line.startswith('description:'):
                    description_started = True
                    continue
                elif line.startswith('commands:') or line.startswith('snap-id:'):
                    description_started = False
                
                if description_started and line:
                    description.append(line)
                    
            if description:
                app.description = " ".join(description)
                
            # Size is hard to get from snap info without install? 
            # Actually 'installed:' line might have size if installed.
            # But simpler to maybe use 'du' on the snap folder if really needed, but let's skip for now to avoid complexity.
            
        except subprocess.CalledProcessError:
            pass
        return app
