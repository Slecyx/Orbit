"""Batch operations dialog for Orbit."""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
import threading

class BatchOperationDialog(Adw.Window):
    """Dialog for batch operations with progress tracking."""
    
    def __init__(self, parent, operation_name: str):
        super().__init__()
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_title(operation_name)
        self.set_default_size(500, 300)
        
        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        self.set_content(main_box)
        
        # Status label
        self.status_label = Gtk.Label(label="Preparing...")
        self.status_label.add_css_class("title-3")
        main_box.append(self.status_label)
        
        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        main_box.append(self.progress_bar)
        
        # Current app label
        self.current_app_label = Gtk.Label(label="")
        self.current_app_label.add_css_class("dim-label")
        main_box.append(self.current_app_label)
        
        # Results area (initially hidden)
        self.results_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.append(self.results_box)
        
        # Close button (initially hidden)
        self.close_button = Gtk.Button(label="Close")
        self.close_button.add_css_class("suggested-action")
        self.close_button.connect('clicked', lambda _: self.close())
        self.close_button.set_visible(False)
        main_box.append(self.close_button)
        
        self.operation_complete = False
    
    def update_progress(self, current: int, total: int, app_name: str):
        """Update progress display."""
        fraction = current / total if total > 0 else 0
        self.progress_bar.set_fraction(fraction)
        self.progress_bar.set_text(f"{current} / {total}")
        self.status_label.set_text(f"Processing ({current}/{total})")
        self.current_app_label.set_text(f"Current: {app_name}")
    
    def show_results(self, results: dict):
        """Show operation results."""
        self.operation_complete = True
        self.status_label.set_text("Operation Complete")
        self.progress_bar.set_fraction(1.0)
        self.current_app_label.set_text("")
        
        # Success
        if results['success'] > 0:
            success_row = Adw.ActionRow(
                title=f"✅ Successful: {results['success']}",
                subtitle="Operations completed successfully"
            )
            success_row.add_css_class("success-row")
            self.results_box.append(success_row)
        
        # Failed
        if results['failed'] > 0:
            failed_row = Adw.ActionRow(
                title=f"❌ Failed: {results['failed']}",
                subtitle="Operations that encountered errors"
            )
            failed_row.add_css_class("error-row")
            self.results_box.append(failed_row)
        
        self.close_button.set_visible(True)


class BatchUpdateDialog(BatchOperationDialog):
    """Dialog for batch update operations."""
    
    def __init__(self, parent, manager):
        super().__init__(parent, "Update All Packages")
        self.manager = manager
        self.start_operation()
    
    def start_operation(self):
        """Start the batch update operation."""
        def progress_callback(current, total, app_name):
            GLib.idle_add(self.update_progress, current, total, app_name)
        
        def run_update():
            results = self.manager.update_all(progress_callback)
            GLib.idle_add(self.show_results, results)
        
        thread = threading.Thread(target=run_update, daemon=True)
        thread.start()


class BatchRemoveDialog(BatchOperationDialog):
    """Dialog for batch remove operations."""
    
    def __init__(self, parent, manager, apps):
        super().__init__(parent, f"Remove {len(apps)} Packages")
        self.manager = manager
        self.apps = apps
        self.start_operation()
    
    def start_operation(self):
        """Start the batch remove operation."""
        def progress_callback(current, total, app_name):
            GLib.idle_add(self.update_progress, current, total, app_name)
        
        def run_remove():
            results = self.manager.remove_multiple(self.apps, progress_callback)
            GLib.idle_add(self.show_results, results)
        
        thread = threading.Thread(target=run_remove, daemon=True)
        thread.start()
