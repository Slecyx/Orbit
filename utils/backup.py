"""Backup and restore functionality for Orbit."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from models import App, PackageSource, UpdateStatus

class BackupManager:
    """Manages backup and restore of application lists."""
    
    def __init__(self, backup_dir: str = None):
        if backup_dir:
            self.backup_dir = Path(backup_dir)
        else:
            self.backup_dir = Path.home() / 'Documents' / 'orbit_backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def export_apps(self, apps: List[App], filename: str = None) -> str:
        """
        Export application list to JSON file.
        
        Args:
            apps: List of App objects to export
            filename: Optional custom filename
            
        Returns:
            Path to the created backup file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'orbit_backup_{timestamp}.json'
        
        backup_path = self.backup_dir / filename
        
        # Convert apps to serializable format
        apps_data = []
        for app in apps:
            apps_data.append({
                'id': app.id,
                'name': app.name,
                'source': app.source.value,
                'version': app.version,
                'summary': app.summary,
                'icon': app.icon,
                'sandboxed': app.sandboxed,
                'size': app.size
            })
        
        backup_data = {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'total_apps': len(apps),
            'apps': apps_data
        }
        
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        return str(backup_path)
    
    def import_apps(self, backup_file: str) -> List[Dict[str, Any]]:
        """
        Import application list from backup file.
        
        Args:
            backup_file: Path to backup JSON file
            
        Returns:
            List of app dictionaries
        """
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        return backup_data.get('apps', [])
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups.
        
        Returns:
            List of backup metadata
        """
        backups = []
        for backup_file in self.backup_dir.glob('orbit_backup_*.json'):
            try:
                with open(backup_file, 'r') as f:
                    data = json.load(f)
                backups.append({
                    'filename': backup_file.name,
                    'path': str(backup_file),
                    'created_at': data.get('created_at', 'Unknown'),
                    'total_apps': data.get('total_apps', 0)
                })
            except Exception:
                continue
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        return backups
    
    def delete_backup(self, backup_file: str) -> bool:
        """
        Delete a backup file.
        
        Args:
            backup_file: Path to backup file
            
        Returns:
            True if successful
        """
        try:
            Path(backup_file).unlink()
            return True
        except Exception:
            return False
