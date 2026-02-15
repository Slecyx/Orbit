import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Pango, GLib, Gdk
from models import UpdateStatus, PackageSource
from ui.icons import IconResolver
import threading
import subprocess

class DetailsView(Gtk.Box):
    def __init__(self, orbit_app, on_back_clicked, on_action_done):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.orbit_app = orbit_app
        self.on_back_clicked = on_back_clicked
        self.on_action_done = on_action_done
        
        # Main Scrollable Container
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_vexpand(True)
        self.scrolled.set_hexpand(True)
        self.append(self.scrolled)
        
        # Clamp to center content nicely
        self.clamp = Adw.Clamp()
        self.clamp.set_maximum_size(800)
        self.clamp.set_tightening_threshold(600)
        self.scrolled.set_child(self.clamp)
        
        # Main Content Box
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        self.content_box.set_margin_top(32)
        self.content_box.set_margin_bottom(32)
        self.content_box.set_margin_start(24)
        self.content_box.set_margin_end(24)
        self.clamp.set_child(self.content_box)

        # --- Header Section ---
        self.header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.header_box.set_halign(Gtk.Align.CENTER)
        self.content_box.append(self.header_box)
        
        # Back Button (Top Left - outside of centered header, actually better to have a top bar)
        # But we are in a stack, so maybe just a small back button at the top left of content?
        # Or depend on window navigation? The design usually has a back button in the headerbar.
        # For now, let's put a back button at the top of the content box.
        
        top_nav = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        back_btn = Gtk.Button.new_from_icon_name("go-previous-symbolic")
        back_btn.add_css_class("flat")
        back_btn.set_tooltip_text("Back")
        back_btn.connect("clicked", lambda _: on_back_clicked())
        top_nav.append(back_btn)
        self.content_box.prepend(top_nav)

        # Large Icon
        self.icon_image = Gtk.Image()
        self.icon_image.set_pixel_size(96) # Large icon
        self.icon_image.add_css_class("app-icon-large")
        self.header_box.append(self.icon_image)
        
        # Title & Developer
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        text_box.set_halign(Gtk.Align.CENTER)
        
        self.title_label = Gtk.Label()
        self.title_label.add_css_class("title-1")
        text_box.append(self.title_label)
        
        self.developer_label = Gtk.Label()
        self.developer_label.add_css_class("dim-label")
        text_box.append(self.developer_label)
        
        self.header_box.append(text_box)
        
        # Action Bar (Install, Open, Update, Remove)
        self.action_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.action_bar.set_halign(Gtk.Align.CENTER)
        self.content_box.append(self.action_bar)
        
        # Primary Action (Install/Open)
        self.primary_btn = Gtk.Button()
        self.primary_btn.add_css_class("pill")
        self.primary_btn.add_css_class("suggested-action")
        self.primary_btn.connect("clicked", self.on_primary_action)
        self.action_bar.append(self.primary_btn)
        
        # Update Button
        self.update_btn = Gtk.Button(label="Update")
        self.update_btn.add_css_class("pill")
        self.update_btn.add_css_class("accent") 
        self.update_btn.set_visible(False)
        self.update_btn.connect("clicked", self.on_update_clicked)
        self.action_bar.append(self.update_btn)
        
        # Remove Button
        self.remove_btn = Gtk.Button(label="Uninstall")
        self.remove_btn.add_css_class("pill")
        self.remove_btn.add_css_class("destructive-action") # Changed class name if needed
        self.remove_btn.connect("clicked", self.on_remove_clicked)
        self.action_bar.append(self.remove_btn)
        
        # Status Label
        self.status_label = Gtk.Label()
        self.status_label.add_css_class("dim-label")
        self.status_label.set_halign(Gtk.Align.CENTER)
        self.content_box.append(self.status_label)

        # --- Screenshots Section (Placeholder) ---
        self.screenshots_scroll = Gtk.ScrolledWindow()
        self.screenshots_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        self.screenshots_scroll.set_min_content_height(200)
        self.screenshots_scroll.add_css_class("screenshot-scroll")
        
        self.screenshots_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.screenshots_scroll.set_child(self.screenshots_box)
        self.content_box.append(self.screenshots_scroll)
        
        # --- Metadata Card ---
        self.metadata_group = Adw.PreferencesGroup()
        self.metadata_group.set_title("Details")
        self.content_box.append(self.metadata_group)
        
        self.version_row = Adw.ActionRow(title="Version")
        self.metadata_group.add(self.version_row)
        
        self.source_row = Adw.ActionRow(title="Source")
        self.metadata_group.add(self.source_row)
        
        self.license_row = Adw.ActionRow(title="License")
        self.metadata_group.add(self.license_row)
        
        self.size_row = Adw.ActionRow(title="Size")
        self.metadata_group.add(self.size_row)

        self.homepage_row = Adw.ActionRow(title="Homepage")
        self.homepage_row.set_activatable(True)
        self.homepage_row.add_suffix(Gtk.Image.new_from_icon_name("external-link-symbolic"))
        self.homepage_row.connect("activated", self.on_homepage_clicked)
        self.metadata_group.add(self.homepage_row)

        # --- Description Section ---
        self.desc_group = Adw.PreferencesGroup()
        self.desc_group.set_title("Description")
        self.content_box.append(self.desc_group)
        
        self.desc_label = Gtk.Label()
        self.desc_label.set_wrap(True)
        self.desc_label.set_xalign(0)
        self.desc_label.set_selectable(True)
        self.desc_label.add_css_class("description-text")
        
        # Wrap description in a box for padding if needed, but PrefGroup handles it well usually
        # Actually, AdwPreferencesGroup expects rows. Let's make a custom box for description.
        self.content_box.remove(self.desc_group)
        
        desc_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        desc_title = Gtk.Label(label="Description", xalign=0)
        desc_title.add_css_class("heading")
        desc_box.append(desc_title)
        desc_box.append(self.desc_label)
        self.content_box.append(desc_box)

    def set_app(self, app):
        self.app = app
        
        # Header
        self.title_label.set_label(app.name)
        self.developer_label.set_label(app.developer if app.developer else "Unknown Developer")
        
        # Icon
        icon_name = IconResolver.resolve(app.name, app.id)
        self.icon_image.set_from_icon_name(icon_name)
        
        # Metadata
        self.version_row.set_subtitle(app.version if app.version else "Unknown")
        
        # Source Badge visual logic
        source_name = app.source.value
        self.source_row.set_subtitle(source_name)
        # You could add a specialized icon/badge to the source row suffix here if you want
        
        self.license_row.set_subtitle(app.license if app.license else "Unknown")
        self.size_row.set_subtitle(app.size if app.size else "Unknown")
        
        if app.homepage:
            self.homepage_row.set_visible(True)
            self.homepage_row.set_subtitle(app.homepage)
        else:
            self.homepage_row.set_visible(False)

        # Description
        self.desc_label.set_label(app.description if app.description else (app.summary if app.summary else "No description available."))
        
        # Update Action Buttons
        self.update_buttons_state()
        
        # Mock Screenshots (Visual placeholder)
        # Clear old
        while child := self.screenshots_box.get_first_child():
            self.screenshots_box.remove(child)
            
        # Add a placeholder box
        placeholder = Gtk.Box()
        placeholder.set_size_request(300, 200)
        placeholder.add_css_class("screenshot-placeholder")
        label = Gtk.Label(label="No screenshots available")
        label.set_vexpand(True)
        label.set_hexpand(True)
        placeholder.append(label)
        self.screenshots_box.append(placeholder)

        # Trigger background fetch for details
        self.fetch_details_async()

    def fetch_details_async(self):
        def fetch():
            if self.orbit_app and hasattr(self.orbit_app, 'manager'):
                updated_app = self.orbit_app.manager.get_app_details(self.app)
                GLib.idle_add(self.update_details_ui, updated_app)

        threading.Thread(target=fetch, daemon=True).start()

    def update_details_ui(self, app):
        # Update UI with fetched details
        self.version_row.set_subtitle(app.version if app.version else "Unknown")
        self.license_row.set_subtitle(app.license if app.license else "Unknown")
        self.size_row.set_subtitle(app.size if app.size else "Unknown")
        self.developer_label.set_label(app.developer if app.developer else "Unknown Developer")
        
        if app.homepage:
            self.homepage_row.set_visible(True)
            self.homepage_row.set_subtitle(app.homepage)
        
        self.desc_label.set_label(app.description if app.description else (app.summary if app.summary else "No description available."))
        
        # Also re-evaluate launch command if it was populated during details fetch (unlikely for now but good practice)
        self.update_buttons_state()
        
    def update_buttons_state(self):
        # Reset
        self.primary_btn.set_visible(True)
        self.update_btn.set_visible(False)
        self.remove_btn.set_visible(False)
        self.status_label.set_label("")
        
        if self.app.is_installed:
            self.remove_btn.set_visible(True)
            
            # Check for updates
            if self.app.update_status == UpdateStatus.UPDATE_AVAILABLE:
                self.update_btn.set_visible(True)
            
            # Primary button becomes "Open"
            self.primary_btn.set_label("Open")
            self.primary_btn.set_icon_name("system-run-symbolic")
            self.primary_btn.remove_css_class("suggested-action") # Open is secondary usually? 
            # Actually, let's keep it suggested if it's the main thing to do.
            
            if not self.app.launch_command:
                 # If we don't know how to launch it, maybe disable or hide?
                 # Or just generic "Open" that tries best effort?
                 # Let's keep it but maybe dim it if we are unsure?
                 pass
        else:
            # Not installed
            self.primary_btn.set_label("Install")
            self.primary_btn.set_icon_name("system-software-install-symbolic")
            self.primary_btn.add_css_class("suggested-action")

    def on_primary_action(self, btn):
        if self.app.is_installed:
            # Launch
            self.launch_app()
        else:
            # Install
            self.perform_action("install")

    def launch_app(self):
        print(f"Launching {self.app.name}...")
        cmd = self.app.launch_command
        
        # Fallbacks if launch command is empty
        if not cmd:
            if self.app.source == PackageSource.FLATPAK:
                cmd = f"flatpak run {self.app.id}"
            elif self.app.source == PackageSource.SNAP:
                cmd = f"snap run {self.app.id}"
            else:
                # Try simple name or id
                cmd = self.app.id
        
        if cmd:
            try:
                subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"Failed to launch: {e}")
                self.status_label.set_text(f"❌ Failed to launch: {e}")
        else:
             self.status_label.set_text("❌ No launch command found")

    def on_update_clicked(self, btn):
        self.perform_action("update")

    def on_remove_clicked(self, btn):
        self.perform_action("remove")

    def on_homepage_clicked(self, row):
        if self.app.homepage:
            Gtk.show_uri(None, self.app.homepage, Gdk.CURRENT_TIME)

    def perform_action(self, action_type):
        """Perform action with UI feedback."""
        self.action_bar.set_sensitive(False)
        self.status_label.set_text(f"{action_type.capitalize()}ing...")
        
        def run_action():
            success = False
            try:
                if not self.orbit_app or not hasattr(self.orbit_app, 'manager'):
                    raise Exception("Manager not ready")

                if action_type == "install":
                    success = self.orbit_app.manager.install_app(self.app)
                elif action_type == "remove":
                    success = self.orbit_app.manager.remove_app(self.app)
                elif action_type == "update":
                    success = self.orbit_app.manager.update_app(self.app)
            except Exception as e:
                print(f"Action failed: {e}")
                GLib.idle_add(self.show_error, str(e))
                success = False
            
            GLib.idle_add(self.on_action_complete, action_type, success)

        threading.Thread(target=run_action, daemon=True).start()

    def on_action_complete(self, action_type, success):
        self.action_bar.set_sensitive(True)
        if success:
            self.status_label.set_text(f"✅ {action_type.capitalize()} successful")
             # Update model state locally to reflect change immediately?
             # For now, rely on refresh callback
            if self.on_action_done:
                self.on_action_done()
        else:
            self.status_label.set_text(f"❌ {action_type.capitalize()} failed")

    def show_error(self, message):
         self.status_label.set_text(f"❌ Error: {message}")
