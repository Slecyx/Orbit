import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Pango, GLib
from models import UpdateStatus, PackageSource

class DetailsView(Gtk.Box):
    def __init__(self, orbit_app, on_back_clicked, on_action_done):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        self.orbit_app = orbit_app
        self.on_back_clicked = on_back_clicked
        self.on_action_done = on_action_done
        self.set_margin_top(24)
        self.set_margin_bottom(24)
        self.set_margin_start(32)
        self.set_margin_end(32)

        # Back Button and Pack name
        top_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.append(top_box)

        back_btn = Gtk.Button.new_from_icon_name("go-previous-symbolic")
        back_btn.connect("clicked", lambda _: on_back_clicked())
        top_box.append(back_btn)

        self.title_label = Gtk.Label()
        self.title_label.set_attributes(Pango.AttrList.from_string("0 -1 size 24000 weight bold"))
        top_box.append(self.title_label)

        # Info Grid
        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(24)
        self.grid.set_row_spacing(12)
        self.append(self.grid)

        self.add_info_row(0, "Source", self.create_label(""))
        self.add_info_row(1, "Version", self.create_label(""))
        self.add_info_row(2, "Sandboxed", self.create_label(""))
        self.add_info_row(3, "Description", self.create_label(""))

        # Action Buttons
        self.actions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.append(self.actions_box)

        self.update_btn = Gtk.Button(label="Update")
        self.update_btn.add_css_class("suggested-action")
        self.update_btn.connect("clicked", self.on_update_clicked)
        self.actions_box.append(self.update_btn)

        self.remove_btn = Gtk.Button(label="Remove")
        self.remove_btn.add_css_class("destructive-action")
        self.remove_btn.connect("clicked", self.on_remove_clicked)
        self.actions_box.append(self.remove_btn)
        
        # Status label for feedback
        self.status_label = Gtk.Label(label="")
        self.status_label.add_css_class("dim-label")
        self.append(self.status_label)

    def create_label(self, text):
        label = Gtk.Label(label=text)
        label.set_halign(Gtk.Align.START)
        return label

    def add_info_row(self, row, title, value_widget):
        title_label = Gtk.Label(label=title)
        title_label.set_halign(Gtk.Align.START)
        title_label.add_css_class("dim-label")
        self.grid.attach(title_label, 0, row, 1, 1)
        self.grid.attach(value_widget, 1, row, 1, 1)

    def set_app(self, app):
        self.app = app
        self.title_label.set_label(app.name)
        
        # Update labels in grid
        self.grid.get_child_at(1, 0).set_label(app.source.value)
        self.grid.get_child_at(1, 1).set_label(app.version)
        self.grid.get_child_at(1, 2).set_label("Yes" if app.sandboxed else "No")
        self.grid.get_child_at(1, 3).set_label(app.summary or "No description")

        # Disable update/install logic
        if not app.is_installed:
            self.update_btn.set_label("Install")
            self.update_btn.set_sensitive(True)
            self.update_btn.set_tooltip_text(None)
            self.remove_btn.set_visible(False)
        else:
            self.remove_btn.set_visible(True)
            can_update = app.update_status == UpdateStatus.UPDATE_AVAILABLE
            self.update_btn.set_sensitive(can_update)
            
            if app.source == PackageSource.APPIMAGE:
                self.update_btn.set_label("Manual Update")
                self.update_btn.set_sensitive(False)
                self.update_btn.set_tooltip_text("This AppImage doesn't support AppImageUpdate. Please download new version manually.")
            else:
                self.update_btn.set_label("Update")
                self.update_btn.set_tooltip_text(None)

    def on_update_clicked(self, btn):
        self.actions_box.set_sensitive(False)
        if not self.app.is_installed:
            self.status_label.set_text("Installing...")
            GLib.idle_add(self.perform_action, "install")
        else:
            self.status_label.set_text("Updating...")
            GLib.idle_add(self.perform_action, "update")

    def on_remove_clicked(self, btn):
        self.actions_box.set_sensitive(False)
        self.status_label.set_text("Removing...")
        GLib.idle_add(self.perform_action, "remove")

    def perform_action(self, action_type):
        """Perform update or remove action with safety checks."""
        
        # Safety check for orbit_app before accessing manager
        if not self.orbit_app or not hasattr(self.orbit_app, 'manager'):
            print("Error: Application not fully initialized or manager not found.")
            self.actions_box.set_sensitive(True)
            self.status_label.set_text("❌ Error: Application manager not available")
            return False

        success = False
        try:
            if action_type == "update":
                success = self.orbit_app.manager.update_app(self.app)
            elif action_type == "remove":
                success = self.orbit_app.manager.remove_app(self.app)
            elif action_type == "install":
                success = self.orbit_app.manager.install_app(self.app)
        except Exception as e:
            print(f"Error during {action_type}: {e}")
            success = False
        
        self.actions_box.set_sensitive(True)
        
        if success:
            self.status_label.set_text(f"✅ {action_type.capitalize()} successful")
            if self.on_action_done:
                self.on_action_done()
        else:
            self.status_label.set_text(f"❌ {action_type.capitalize()} failed")
        
        return False
