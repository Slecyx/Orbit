from dataclasses import dataclass
from enum import Enum, auto

class PackageSource(Enum):
    APT = "APT"
    FLATPAK = "Flatpak"
    SNAP = "Snap"
    APPIMAGE = "AppImage"
    PACMAN = "Pacman"
    DNF = "DNF"

class UpdateStatus(Enum):
    UP_TO_DATE = auto()
    UPDATE_AVAILABLE = auto()
    MANUAL = auto()
    UNKNOWN = auto()

@dataclass
class App:
    id: str
    name: str
    source: PackageSource
    version: str
    update_status: UpdateStatus = UpdateStatus.UNKNOWN
    is_installed: bool = True
    summary: str = ""
    icon: str = "system-run" # Default icon
    sandboxed: bool = False
    size: str = "" # Disk usage
    description: str = ""  # Full description
    launch_command: str = ""  # Command to launch the app
    installed_date: str = ""  # Installation date
    dependencies: list = None  # List of dependencies
    developer: str = "" # Developer name
    license: str = "" # License type
    homepage: str = "" # Homepage URL
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

