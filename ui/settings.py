"""Settings/Preferences dialog for Orbit."""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

class SettingsDialog(Adw.PreferencesWindow):
    """Application settings dialog."""
    
    def __init__(self, parent, config):
        super().__init__()
        self.config = config
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_title("Settings")
        self.set_default_size(600, 500)
        
        # Appearance Page
        appearance_page = Adw.PreferencesPage(title="Appearance", icon_name="preferences-desktop-display-symbolic")
        self.add(appearance_page)

        # Visuals Group
        visuals_group = Adw.PreferencesGroup(title="Visuals")
        appearance_page.add(visuals_group)

        # Theme Selector
        theme_row = Adw.ComboRow(
            title="Theme",
            model=Gtk.StringList.new(["System", "Light", "Dark"])
        )
        # Map config value to index
        current_theme = config.get('theme', 'System').lower()
        if current_theme == 'light': theme_row.set_selected(1)
        elif current_theme == 'dark': theme_row.set_selected(2)
        else: theme_row.set_selected(0)
        
        theme_row.connect("notify::selected", self.on_theme_changed)
        visuals_group.add(theme_row)
        
        # Compact Mode
        self.compact_row = Adw.SwitchRow(
            title="Compact Mode",
            subtitle="Reduce spacing for list items"
        )
        self.compact_row.set_active(config.get('compact_mode', False))
        self.compact_row.connect("notify::active", self.on_compact_mode_changed)
        visuals_group.add(self.compact_row)

        # General settings page
        general_page = Adw.PreferencesPage(title="General", icon_name="preferences-system-symbolic")
        self.add(general_page)
        
        # Notifications group
        notifications_group = Adw.PreferencesGroup(
            title="Notifications",
            description="Configure desktop notifications"
        )
        general_page.add(notifications_group)
        
        # Show notifications toggle
        self.notifications_row = Adw.SwitchRow(
            title="Show Notifications",
            subtitle="Display desktop notifications for updates"
        )
        self.notifications_row.set_active(config.get('show_notifications', True))
        self.notifications_row.connect('notify::active', self.on_notifications_changed)
        notifications_group.add(self.notifications_row)
        
        # Updates group
        updates_group = Adw.PreferencesGroup(
            title="Updates",
            description="Configure update checking behavior"
        )
        general_page.add(updates_group)
        
        # Auto update check toggle
        self.auto_update_row = Adw.SwitchRow(
            title="Auto-Check for Updates",
            subtitle="Automatically check for package updates"
        )
        self.auto_update_row.set_active(config.get('auto_update_check', True))
        self.auto_update_row.connect('notify::active', self.on_auto_update_changed)
        updates_group.add(self.auto_update_row)
        
        # Package sources page
        sources_page = Adw.PreferencesPage(title="Sources", icon_name="folder-symbolic")
        self.add(sources_page)
        
        # Preferred source group
        preferred_group = Adw.PreferencesGroup(
            title="Preferred Package Source",
            description="Default source when multiple options are available"
        )
        sources_page.add(preferred_group)
        
        # Source selection
        sources = ["flatpak", "snap", "apt", "pacman", "dnf", "appimage"]
        current_source = config.get('preferred_source', 'flatpak')
        
        for source in sources:
            row = Adw.ActionRow(title=source.capitalize())
            check = Gtk.CheckButton()
            check.set_active(source == current_source)
            check.connect('toggled', self.on_source_changed, source)
            row.add_prefix(check)
            row.set_activatable_widget(check)
            preferred_group.add(row)
        
        # AppImage directories
        appimage_group = Adw.PreferencesGroup(
            title="AppImage Scan Directories",
            description="Directories to scan for AppImage files"
        )
        sources_page.add(appimage_group)
        
        dirs = config.get('appimage_scan_dirs', [])
        for directory in dirs:
            row = Adw.ActionRow(title=directory)
            appimage_group.add(row)
        
        # Backup page
        backup_page = Adw.PreferencesPage(title="Backup", icon_name="folder-download-symbolic")
        self.add(backup_page)
        
        backup_group = Adw.PreferencesGroup(
            title="Backup Location",
            description="Where to save application list backups"
        )
        backup_page.add(backup_group)
        
        backup_row = Adw.ActionRow(
            title="Backup Directory",
            subtitle=config.get('backup_location', '~/Documents/orbit_backups')
        )
        backup_group.add(backup_row)
    
    def on_notifications_changed(self, switch, *args):
        """Handle notifications toggle."""
        self.config.set('show_notifications', switch.get_active())
    
    def on_auto_update_changed(self, switch, *args):
        """Handle auto-update toggle."""
        self.config.set('auto_update_check', switch.get_active())
    
    def on_theme_changed(self, row, *args):
        """Handle theme change."""
        selected = row.get_selected_item().get_string()
        self.config.set('theme', selected)
        
        # Apply theme immediately
        manager = Adw.StyleManager.get_default()
        if selected == "Dark":
            manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        elif selected == "Light":
            manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        else:
            manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

    def on_compact_mode_changed(self, switch, *args):
        """Handle compact mode toggle."""
        is_compact = switch.get_active()
        self.config.set('compact_mode', is_compact)
        
        # Apply directly if parent is available
        parent = self.get_transient_for()
        if parent and hasattr(parent, 'apply_compact_mode'):
            parent.apply_compact_mode(is_compact)

    def on_source_changed(self, check, source):
        """Handle preferred source change."""
        if check.get_active():
            self.config.set('preferred_source', source)
