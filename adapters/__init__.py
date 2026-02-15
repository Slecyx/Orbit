from abc import ABC, abstractmethod
from typing import List
from models import App

class PackageAdapter(ABC):
    @abstractmethod
    def get_installed_apps(self) -> List[App]:
        """Returns a list of installed applications for this source."""
        pass

    @abstractmethod
    def update_app(self, app_id: str) -> bool:
        """Updates the specified application. Returns True if successful."""
        pass

    @abstractmethod
    def remove_app(self, app_id: str) -> bool:
        """Removes the specified application. Returns True if successful."""
        pass

    @abstractmethod
    def search_apps(self, query: str) -> List[App]:
        """Searches for applications matching the query."""
        pass

    def get_details(self, app: App) -> App:
        """Retrieves detailed information for the application. Default implementation returns app as is."""
        return app
