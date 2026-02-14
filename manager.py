from typing import List
from models import App, PackageSource, UpdateStatus
from adapters.apt import AptAdapter
from adapters.flatpak import FlatpakAdapter
from adapters.snap import SnapAdapter
from adapters.appimage import AppImageAdapter
from adapters.pacman import PacmanAdapter
from adapters.dnf import DnfAdapter
from utils.logger import setup_logger

logger = setup_logger('orbit.manager')

class OrbitException(Exception):
    """Base exception for Orbit operations."""
    pass

class ProviderRegistry:
    def __init__(self):
        self._adapters = {}

    def register(self, source, adapter):
        self._adapters[source] = adapter

    def get_adapter(self, source):
        return self._adapters.get(source)

    def all_adapters(self):
        return self._adapters.values()

class OrbitManager:
    def __init__(self):
        self.registry = ProviderRegistry()
        self.registry.register(PackageSource.APT, AptAdapter())
        self.registry.register(PackageSource.FLATPAK, FlatpakAdapter())
        self.registry.register(PackageSource.SNAP, SnapAdapter())
        self.registry.register(PackageSource.APPIMAGE, AppImageAdapter())
        self.registry.register(PackageSource.PACMAN, PacmanAdapter())
        self.registry.register(PackageSource.DNF, DnfAdapter())
        self.apps = []
        logger.info("OrbitManager initialized")

    def refresh_apps(self) -> List[App]:
        """Refresh the list of installed applications."""
        logger.info("Refreshing application list")
        self.apps = []
        for adapter in self.registry.all_adapters():
            try:
                apps = adapter.get_installed_apps()
                self.apps.extend(apps)
                logger.debug(f"Loaded {len(apps)} apps from {adapter.__class__.__name__}")
            except Exception as e:
                logger.error(f"Error loading apps from {adapter.__class__.__name__}: {e}")
        
        # Sort by name
        self.apps.sort(key=lambda x: x.name.lower())
        self.detect_conflicts()
        logger.info(f"Total apps loaded: {len(self.apps)}")
        return self.apps

    def detect_conflicts(self):
        """Identify apps with same name but different sources."""
        name_map = {}
        for app in self.apps:
            if app.name not in name_map:
                name_map[app.name] = []
            name_map[app.name].append(app)
        
        for name, apps in name_map.items():
            if len(apps) > 1:
                for app in apps:
                    app.summary = f"⚠️ Bu uygulamanın {len(apps)-1} farklı kaynağı daha mevcut. " + (app.summary or "")
                logger.warning(f"Conflict detected for {name}: {len(apps)} sources")

    def get_apps(self) -> List[App]:
        """Get the current list of applications."""
        if not self.apps:
            return self.refresh_apps()
        return self.apps

    def update_app(self, app: App) -> bool:
        """Update a single application."""
        logger.info(f"Updating app: {app.name} ({app.source.value})")
        adapter = self.registry.get_adapter(app.source)
        if adapter:
            try:
                result = adapter.update_app(app.id)
                if result:
                    logger.info(f"Successfully updated {app.name}")
                else:
                    logger.warning(f"Failed to update {app.name}")
                return result
            except Exception as e:
                logger.error(f"Error updating {app.name}: {e}")
                raise OrbitException(f"Failed to update {app.name}: {e}")
        return False

    def remove_app(self, app: App) -> bool:
        """Remove a single application."""
        logger.info(f"Removing app: {app.name} ({app.source.value})")
        adapter = self.registry.get_adapter(app.source)
        if adapter:
            try:
                result = adapter.remove_app(app.id)
                if result:
                    logger.info(f"Successfully removed {app.name}")
                else:
                    logger.warning(f"Failed to remove {app.name}")
                return result
            except Exception as e:
                logger.error(f"Error removing {app.name}: {e}")
                raise OrbitException(f"Failed to remove {app.name}: {e}")
        return False

    def update_all(self, progress_callback=None) -> dict:
        """
        Update all applications that have updates available.
        
        Args:
            progress_callback: Optional callback function(current, total, app_name)
            
        Returns:
            Dictionary with success and failure counts
        """
        logger.info("Starting batch update")
        updatable_apps = [app for app in self.apps if app.update_status == UpdateStatus.UPDATE_AVAILABLE]
        
        results = {'success': 0, 'failed': 0, 'total': len(updatable_apps)}
        
        for i, app in enumerate(updatable_apps):
            if progress_callback:
                progress_callback(i + 1, len(updatable_apps), app.name)
            
            try:
                if self.update_app(app):
                    results['success'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                logger.error(f"Error in batch update for {app.name}: {e}")
                results['failed'] += 1
        
        logger.info(f"Batch update complete: {results['success']} success, {results['failed']} failed")
        return results

    def remove_multiple(self, apps: List[App], progress_callback=None) -> dict:
        """
        Remove multiple applications.
        
        Args:
            apps: List of apps to remove
            progress_callback: Optional callback function(current, total, app_name)
            
        Returns:
            Dictionary with success and failure counts
        """
        logger.info(f"Starting batch removal of {len(apps)} apps")
        results = {'success': 0, 'failed': 0, 'total': len(apps)}
        
        for i, app in enumerate(apps):
            if progress_callback:
                progress_callback(i + 1, len(apps), app.name)
            
            try:
                if self.remove_app(app):
                    results['success'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                logger.error(f"Error in batch removal for {app.name}: {e}")
                results['failed'] += 1
        
        logger.info(f"Batch removal complete: {results['success']} success, {results['failed']} failed")
        return results

    def get_statistics(self) -> dict:
        """
        Get statistics about installed applications.
        
        Returns:
            Dictionary with various statistics
        """
        stats = {
            'total': len(self.apps),
            'by_source': {},
            'updates_available': 0,
            'sandboxed': 0,
            'conflicts': 0
        }
        
        for app in self.apps:
            # Count by source
            source_name = app.source.value
            stats['by_source'][source_name] = stats['by_source'].get(source_name, 0) + 1
            
            # Count updates
            if app.update_status == UpdateStatus.UPDATE_AVAILABLE:
                stats['updates_available'] += 1
            
            # Count sandboxed
            if app.sandboxed:
                stats['sandboxed'] += 1
            
            # Count conflicts
            if "⚠️" in (app.summary or ""):
                stats['conflicts'] += 1
        
        return stats

    def search_apps(self, query: str, source: PackageSource = None) -> List[App]:
        """
        Search for applications in repositories.
        
        Args:
            query: Search query
            source: Optional specific source to search
            
        Returns:
            List of matching apps
        """
        logger.info(f"Searching for: {query}")
        results = []
        
        adapters = [self.registry.get_adapter(source)] if source else self.registry.all_adapters()
        
        for adapter in adapters:
            if adapter:
                try:
                    results.extend(adapter.search_apps(query))
                except Exception as e:
                    logger.error(f"Error searching in {adapter.__class__.__name__}: {e}")
        
        return results

    def install_app(self, app: App) -> bool:
        """
        Install a new application.
        
        Args:
            app: App object to install
            
        Returns:
            True if successful
        """
        logger.info(f"Installing app: {app.name} from {app.source.value}")
        adapter = self.registry.get_adapter(app.source)
        if adapter and hasattr(adapter, 'install_app'):
            try:
                result = adapter.install_app(app.id)
                if result:
                    logger.info(f"Successfully installed {app.name}")
                else:
                    logger.warning(f"Failed to install {app.name}")
                return result
            except Exception as e:
                logger.error(f"Error installing {app.name}: {e}")
                raise OrbitException(f"Failed to install {app.name}: {e}")
        return False

