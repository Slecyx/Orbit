import os
import glob
import hashlib
from typing import List
from models import App, PackageSource, UpdateStatus
from . import PackageAdapter

class AppImageAdapter(PackageAdapter):
    def __init__(self):
        self.search_paths = [
            os.path.expanduser("~/Applications"),
            "/opt",
            os.path.expanduser("~/.local/bin")
        ]
        self._id_map = {}

    def get_installed_apps(self) -> List[App]:
        apps = []
        self._id_map = {}
        for path in self.search_paths:
            if not os.path.exists(path):
                continue
            
            # Look for *.AppImage files
            for file_path in glob.glob(os.path.join(path, "*.AppImage")):
                filename = os.path.basename(file_path)
                name = filename.replace(".AppImage", "").replace("-", " ").capitalize()
                
                # Deterministic ID based on path
                app_id = hashlib.sha256(file_path.encode()).hexdigest()[:12]
                self._id_map[app_id] = file_path
                
                apps.append(App(
                    id=app_id,
                    name=name,
                    source=PackageSource.APPIMAGE,
                    version="Unknown",
                    sandboxed=False,
                    summary=f"Path: {file_path}",
                    update_status=UpdateStatus.UNKNOWN
                ))
        return apps

    def update_app(self, app_id: str) -> bool:
        return False

    def remove_app(self, app_id: str) -> bool:
        file_path = self._id_map.get(app_id)
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except OSError:
                return False
        return False

    def search_apps(self, query: str) -> List[App]:
        return []
