import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Pango, Gdk
from ui.icons import IconResolver
from models import PackageSource, UpdateStatus

class AppRow(Adw.ActionRow):
    def __init__(self, app, advanced=False):
        super().__init__()
        self.app = app
        self.advanced = advanced
        
        # Main Layout
        self.set_title(app.name)
        self.add_css_class("premium-row")
        self.set_activatable(True)

        # Subtitle Construction
        subtitle_parts = []
        if app.version:
            subtitle_parts.append(f"v{app.version}")
        
        # Add summary if available and not too long
        if app.summary:
            summary = app.summary[:50] + "..." if len(app.summary) > 50 else app.summary
            subtitle_parts.append(summary)
            
        self.set_subtitle(" • ".join(subtitle_parts))

        # Icon
        icon_name = IconResolver.resolve(app.name, app.id)
        self.icon_image = Gtk.Image.new_from_icon_name(icon_name)
        self.icon_image.set_pixel_size(48)
        self.icon_image.add_css_class("app-icon")
        self.icon_image.set_margin_top(8)
        self.icon_image.set_margin_bottom(8)
        self.add_prefix(self.icon_image)

        # Source Badge (Suffix)
        source_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        source_box.set_valign(Gtk.Align.CENTER)
        
        # Source Label
        source_label = Gtk.Label(label=app.source.value)
        source_label.add_css_class("source-badge")
        source_label.add_css_class(f"source-{app.source.value.lower()}")
        source_box.append(source_label)
        
        self.add_suffix(source_box)

        # Status Badges
        if app.is_installed:
            installed_icon = Gtk.Image.new_from_icon_name("object-select-symbolic")
            installed_icon.set_pixel_size(16)
            installed_icon.add_css_class("dim-label")
            installed_icon.set_tooltip_text("Installed")
            # We don't necessarily need a big badge for installed if it's the default view, 
            # but for search results it's useful.
            source_box.append(installed_icon)
        
        if app.update_status == "UpdateStatus.UPDATE_AVAILABLE": # Enum check might need import
            update_badge = Gtk.Label(label="Update")
            update_badge.add_css_class("status-badge")
            update_badge.add_css_class("update")
            source_box.append(update_badge)

        if app.sandboxed:
            sandbox_icon = Gtk.Image.new_from_icon_name("security-high-symbolic")
            sandbox_icon.set_pixel_size(16)
            sandbox_icon.set_tooltip_text("Sandboxed")
            sandbox_icon.add_css_class("dim-label")
            source_box.append(sandbox_icon)

class AppListView(Gtk.Box):
    def __init__(self, on_app_selected):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.on_app_selected = on_app_selected
        
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list_box.add_css_class("boxed-list")
        self.list_box.connect("row-activated", self._on_row_activated)
        
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_vexpand(True)
        self.scrolled.set_child(self.list_box)
        self.append(self.scrolled)

    def set_compact(self, is_compact):
        """Toggle compact mode."""
        if is_compact:
            self.list_box.add_css_class("compact-list")
        else:
            self.list_box.remove_css_class("compact-list")

    def _on_row_activated(self, listbox, row):
        if row and hasattr(row, 'app'):
            self.on_app_selected(row.app)

    def update_list(self, apps, advanced=False):
        # Clear existing
        while child := self.list_box.get_first_child():
            self.list_box.remove(child)

        for app in apps:
            row = AppRow(app, advanced)
            self.list_box.append(row)
