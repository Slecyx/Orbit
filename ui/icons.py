import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, Gdk

class IconResolver:
    @staticmethod
    def resolve(app_name, app_id):
        """Attempts to find a suitable icon for the app."""
        # 1. Try exact ID (works for many Flatpaks/Snaps)
        # 2. Try app name lowercase
        # 3. Try last part of RDNN (e.g. org.gnome.Calculator -> calculator)
        
        candidates = [app_id]
        if "." in app_id:
            candidates.append(app_id.split('.')[-1].lower())
        
        candidates.append(app_name.lower())
        candidates.append(app_name.replace(" ", "-").lower())
        
        # In GTK4, we can just return the icon name or a Gio.Icon
        # Let's return the most likely name
        return candidates[0]
