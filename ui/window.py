import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
import threading

from ui.app_list import AppListView
from ui.details import DetailsView
from ui.statistics import StatisticsView
from ui.settings import SettingsDialog
from ui.batch_operations import BatchUpdateDialog, BatchRemoveDialog
from utils.backup import BackupManager
from models import UpdateStatus

class OrbitWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Store reference to the application
        self.orbit_app = self.get_application()
        
        # Create actions
        self.create_actions()
        
        self.set_title("Orbit - Universal Package Manager")
        self.set_default_size(900, 700)

        # Main Layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(self.main_box)

        # Header Bar
        self.header = Adw.HeaderBar()
        self.header.set_show_end_title_buttons(True)
        self.main_box.append(self.header)

        # Search Bar
        self.search_bar = Gtk.SearchEntry(placeholder_text="Search applications...")
        self.search_bar.set_hexpand(True)
        self.search_bar.set_halign(Gtk.Align.CENTER)
        self.search_bar.set_size_request(400, -1)
        self.header.set_title_widget(self.search_bar)

        # Menu button
        menu_button = Gtk.MenuButton(icon_name="open-menu-symbolic")
        menu_button.set_tooltip_text("Menu")
        menu_button.add_css_class("menu-button")
        self.header.pack_end(menu_button)
        
        # Create menu
        menu = Gio.Menu()
        menu.append("Statistics", "app.statistics")
        menu.append("Settings", "app.settings")
        menu.append("Backup Apps", "app.backup")
        menu.append("Restore Apps", "app.restore")
        menu.append("About", "app.about")
        menu_button.set_menu_model(menu)
        
        # Add actions
        self.create_actions()

        # Filter Button
        self.filter_btn = Gtk.MenuButton(icon_name="view-filter-symbolic")
        self.filter_btn.set_tooltip_text("Filter")
        self.header.pack_end(self.filter_btn)
        
        # Filter Popover content
        filter_popover = Gtk.Popover()
        filter_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        filter_box.set_margin_start(12)
        filter_box.set_margin_end(12)
        filter_box.set_margin_top(12)
        filter_box.set_margin_bottom(12)
        filter_popover.set_child(filter_box)
        self.filter_btn.set_popover(filter_popover)
        
        # Status Filters
        filter_box.append(self.create_filter_label("Status"))
        self.filter_installed = self.create_check("Installed", True)
        self.filter_updates = self.create_check("Updates Only", False)
        # self.filter_installed.connect("toggled", self.on_filter_changed) # Connect later
        # self.filter_updates.connect("toggled", self.on_filter_changed)
        filter_box.append(self.filter_installed)
        filter_box.append(self.filter_updates)
        
        filter_box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        
        # Source Filters
        filter_box.append(self.create_filter_label("Source"))
        self.source_filters = {}
        for source in ["Flatpak", "Snap", "APT", "Pacman", "DNF", "AppImage"]:
            check = self.create_check(source, True)
            self.source_filters[source] = check
            filter_box.append(check)
            
        # Advanced Toggle (Moved to menu or kept here? Kept here but styled)
        # self.advanced_toggle... (keeping existing)


        # Toolbar with batch operations
        self.toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.toolbar.set_margin_start(12)
        self.toolbar.set_margin_end(12)
        self.toolbar.set_margin_top(6)
        self.toolbar.set_margin_bottom(6)
        self.toolbar.add_css_class("toolbar")
        self.main_box.append(self.toolbar)
        
        # Update All button
        self.update_all_btn = Gtk.Button(label="Update All")
        self.update_all_btn.set_icon_name("system-software-update-symbolic")
        self.update_all_btn.add_css_class("suggested-action")
        self.update_all_btn.connect("clicked", self.on_update_all)
        self.toolbar.append(self.update_all_btn)
        
        # Refresh button
        refresh_btn = Gtk.Button(icon_name="view-refresh-symbolic")
        refresh_btn.set_tooltip_text("Refresh App List")
        refresh_btn.connect("clicked", self.on_refresh)
        self.toolbar.append(refresh_btn)


        # Views
        self.app_list_view = AppListView(self.on_app_selected)
        self.details_view = DetailsView(
            self.orbit_app,
            self.on_back_to_list,
            self.on_action_done
        )
        self.statistics_view = StatisticsView()
        
        # View Stack (for switching between list, details, and statistics)
        self.stack = Gtk.Stack()
        self.stack.set_vexpand(True)
        self.main_box.append(self.stack)
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.add_named(self.app_list_view, "list")
        self.stack.add_named(self.details_view, "details")
        self.stack.add_named(self.statistics_view, "statistics")
        
        # Loading page
        loading_page = Adw.StatusPage()
        loading_page.set_title("Loading Applications...")
        loading_spinner = Gtk.Spinner()
        loading_spinner.start()
        loading_page.set_child(loading_spinner)
        self.stack.add_named(loading_page, "loading")

        # Status bar
        self.status_bar = Gtk.Label(label="Ready")
        self.status_bar.add_css_class("dim-label")
        self.status_bar.set_margin_start(12)
        self.status_bar.set_margin_end(12)
        self.status_bar.set_margin_top(4)
        self.status_bar.set_margin_bottom(4)
        self.status_bar.set_halign(Gtk.Align.START)
        self.main_box.append(self.status_bar)

        # Connect search
        self.search_bar.connect("search-changed", self.on_search_changed)
        self.search_bar.connect("activate", self.on_search_activated)
        self.apps = []
        
        # Backup manager
        self.backup_manager = BackupManager()

        # Initialize Settings
        if self.orbit_app and hasattr(self.orbit_app, 'config'):
            # Apply initial theme
            theme = self.orbit_app.config.get('theme', 'System')
            manager = Adw.StyleManager.get_default()
            if theme == "Dark":
                manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
            elif theme == "Light":
                manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
            
            # Apply initial compact mode
            self.apply_compact_mode(self.orbit_app.config.get('compact_mode', False))

    def apply_compact_mode(self, is_compact):
        """Apply compact mode setting."""
        self.app_list_view.set_compact(is_compact)

    def create_filter_label(self, text):
        label = Gtk.Label(label=text, xalign=0)
        label.add_css_class("dim-label")
        label.add_css_class("caption-heading") # Custom class if needed
        return label

    def create_check(self, label, active=False):
        check = Gtk.CheckButton(label=label)
        check.set_active(active)
        check.connect("toggled", self.on_filter_changed)
        return check

    def create_actions(self):
        """Create application actions."""
        # Statistics action
        stats_action = Gio.SimpleAction.new("statistics", None)
        stats_action.connect("activate", self.on_show_statistics)
        self.get_application().add_action(stats_action)
        
        # Settings action
        settings_action = Gio.SimpleAction.new("settings", None)
        settings_action.connect("activate", self.on_show_settings)
        self.get_application().add_action(settings_action)
        
        # Backup action
        backup_action = Gio.SimpleAction.new("backup", None)
        backup_action.connect("activate", self.on_backup)
        self.get_application().add_action(backup_action)
        
        # Restore action
        restore_action = Gio.SimpleAction.new("restore", None)
        restore_action.connect("activate", self.on_restore)
        self.get_application().add_action(restore_action)
        
        # About action
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about)
        self.get_application().add_action(about_action)

    def on_app_selected(self, app):
        """Handle app selection from list."""
        self.details_view.set_app(app)
        self.stack.set_visible_child_name("details")
    
    def on_back_to_list(self):
        """Handle back button from details view."""
        self.stack.set_visible_child_name("list")
    
    def show_apps(self, apps):
        """Display the list of applications."""
        self.apps = apps
        self.app_list_view.update_list(apps)
        self.stack.set_visible_child_name("list")
        self.status_bar.set_text(f"{len(apps)} applications installed")
        
        # Update statistics - with safety check
        try:
            if self.orbit_app and hasattr(self.orbit_app, 'manager'):
                stats = self.orbit_app.manager.get_statistics()
                self.statistics_view.update_statistics(stats)
                
                # Update button state
                self.update_all_btn.set_sensitive(stats.get('updates_available', 0) > 0)
        except Exception as e:
            # If statistics update fails, just log it and continue
            print(f"Could not update statistics: {e}")

    def show_error(self, error_msg):
        """Show error message."""
        error_page = Adw.StatusPage(
            title="Error Loading Applications",
            description=error_msg,
            icon_name="dialog-error-symbolic"
        )
        self.stack.add_titled(error_page, "error", "Error")
        self.stack.set_visible_child_name("error")

    def on_filter_changed(self, btn):
        """Handle filter changes."""
        # Re-trigger search/filter logic
        self.on_search_changed(self.search_bar)

    def on_search_changed(self, entry):
        """Handle search input (local filter) and advanced filters."""
        query = entry.get_text().lower()
        
        # Gather active filters
        show_installed = self.filter_installed.get_active()
        show_updates_only = self.filter_updates.get_active()
        active_sources = [s for s, check in self.source_filters.items() if check.get_active()]
        
        filtered = []
        for app in self.apps:
            # 1. Search Query
            if query and (query not in app.name.lower() and query not in app.id.lower()):
                continue
            
            # 2. Installed Status
            # If "Installed" is unchecked, we assume we normally show everything? 
            # Actually, "Installed" check usually means "Show Installed".
            # If unchecked, maybe show only uninstalled? 
            # Let's define:
            # - Installed Checked: Show Installed
            # - Installed Unchecked: Hide Installed (Show uninstalled only?)
            # Wait, standard store behavior:
            # Usually you want to toggle "Show Installed" vs "Show All".
            # Let's make it simple:
            # If "Installed" passed -> include installed.
            # If "Updates Only" -> include only updates.
            
            if not show_installed and app.is_installed:
                continue
                
            if show_updates_only and app.update_status != UpdateStatus.UPDATE_AVAILABLE:
                continue
                
            # 3. Source
            if app.source.value not in active_sources:
                continue
                
            filtered.append(app)
            
        self.app_list_view.update_list(filtered, self.advanced_toggle.get_active())
        self.status_bar.set_text(f"{len(filtered)} applications found")

    def on_search_activated(self, entry):
        """Handle search activation (remote search)."""
        query = entry.get_text()
        if not query:
            return
            
        self.stack.set_visible_child_name("loading")
        self.status_bar.set_text(f"Searching for '{query}'...")
        
        def search():
            try:
                # Local results first
                local_results = [a for a in self.apps if query.lower() in a.name.lower() or query.lower() in a.id.lower()]
                
                # Remote results
                remote_results = self.orbit_app.manager.search_apps(query)
                
                # Merge: remote results not in local
                local_ids = {a.id for a in local_results}
                final_results = local_results + [r for r in remote_results if r.id not in local_ids]
                
                GLib.idle_add(self.show_search_results, final_results)
            except Exception as e:
                print(f"Search error: {e}")
                GLib.idle_add(self.show_error, str(e))
        
        threading.Thread(target=search, daemon=True).start()

    def show_search_results(self, results):
        self.app_list_view.update_list(results, self.advanced_toggle.get_active())
        self.stack.set_visible_child_name("list")
        self.status_bar.set_text(f"{len(results)} results found")

    def on_advanced_toggled(self, btn):
        """Toggle advanced view."""
        self.app_list_view.update_list(self.apps, btn.get_active())

    def on_row_activated(self, listbox, row):
        """Handle app row activation."""
        if row and hasattr(row, 'app'):
            self.details_view.set_app(row.app)
            self.stack.set_visible_child_name("details")

    def show_list(self):
        """Return to app list view."""
        self.stack.set_visible_child_name("list")

    def on_action_done(self):
        """Handle action completion (update/remove)."""
        self.stack.set_visible_child_name("loading")
        if self.orbit_app and hasattr(self.orbit_app, 'load_apps_async'):
            self.orbit_app.load_apps_async(self)

    def on_update_all(self, button):
        """Handle update all button."""
        if self.orbit_app and hasattr(self.orbit_app, 'manager'):
            dialog = BatchUpdateDialog(self, self.orbit_app.manager)
            dialog.present()
            # Refresh after dialog closes
            dialog.connect("close-request", lambda _: self.on_action_done())

    def on_refresh(self, button):
        """Handle refresh button."""
        self.stack.set_visible_child_name("loading")
        if self.orbit_app and hasattr(self.orbit_app, 'load_apps_async'):
            self.orbit_app.load_apps_async(self)

    def on_show_statistics(self, action, param):
        """Show statistics view."""
        self.stack.set_visible_child_name("statistics")

    def on_show_settings(self, action, param):
        """Show settings dialog."""
        if self.orbit_app and hasattr(self.orbit_app, 'config'):
            dialog = SettingsDialog(self, self.orbit_app.config)
            dialog.present()

    def on_backup(self, action, param):
        """Backup application list."""
        try:
            backup_mgr = BackupManager()
            apps = self.orbit_app.manager.get_all_apps()
            
            backup_path = backup_mgr.backup_to_file(apps)
            if backup_path:
                dialog = Adw.MessageDialog.new(self)
                dialog.set_heading("Backup Created")
                dialog.set_body(f"Application list backed up to:\n{backup_path}")
                dialog.add_response("ok", "OK")
                dialog.set_default_response("ok")
                dialog.present()
        except Exception as e:
            dialog = Adw.MessageDialog.new(self)
            dialog.set_heading("Backup Failed")
            dialog.set_body(f"Error creating backup: {e}")
            dialog.add_response("ok", "OK")
            dialog.set_default_response("ok")
            dialog.present()

    def on_restore(self, action, param):
        """Restore application list."""
        # File chooser dialog
        dialog = Gtk.FileChooserDialog(
            title="Select Backup File",
            action=Gtk.FileChooserAction.OPEN,
            transient_for=self
        )
        dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Open", Gtk.ResponseType.ACCEPT
        )
        
        # Add filter for JSON files
        filter_json = Gtk.FileFilter()
        filter_json.set_name("Orbit Backups")
        filter_json.add_pattern("*.json")
        dialog.add_filter(filter_json)
        
        dialog.connect("response", self.on_restore_response)
        dialog.show()

    def on_restore_response(self, dialog, response):
        """Handle restore file selection."""
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            if file:
                try:
                    apps_data = self.backup_manager.import_apps(file.get_path())
                    msg = Adw.MessageDialog.new(self)
                    msg.set_heading("Restore Information")
                    msg.set_body(f"Found {len(apps_data)} applications in backup.\n\nNote: This feature shows what was backed up. Automatic installation is not yet implemented.")
                    msg.add_response("ok", "OK")
                    msg.set_default_response("ok")
                    msg.present()
                except Exception as e:
                    msg = Adw.MessageDialog.new(self)
                    msg.set_heading("Restore Failed")
                    msg.set_body(f"Error reading backup: {e}")
                    msg.add_response("ok", "OK")
                    msg.set_default_response("ok")
                    msg.present()
        dialog.close()

    def on_about(self, action, param):
        """Show about dialog."""
        about = Adw.AboutWindow(
            transient_for=self,
            application_name="ORBIT",
            application_icon="system-software-install",
            developer_name="Slecyx",
            version="0.2.0",
            developers=["Slecyx"],
            copyright="© 2026 Slecyx",
            license_type=Gtk.License.GPL_3_0,
            website="https://github.com/slecyx/orbit",
            issue_url="https://github.com/slecyx/orbit/issues"
        )
        about.set_comments("Universal package manager for Linux")
        about.present()

