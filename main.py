import sys
import gi
import threading
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib

from manager import OrbitManager
from ui.window import OrbitWindow
from utils.logger import setup_logger
from utils.config import Config
from utils.notifications import NotificationManager

# Setup logging
logger = setup_logger('orbit')

app = None # Global instance for UI callbacks

class OrbitApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id="io.github.slecyx.orbit",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.manager = OrbitManager()
        self.config = Config()
        self.notifications = NotificationManager()
        
        # Set global app reference IMMEDIATELY
        global app
        app = self
        
        logger.info("Orbit application initialized")

    def do_activate(self):
        self.load_css()
        window = self.get_active_window()
        if not window:
            window = OrbitWindow(application=self)
            self.load_apps_async(window)
        window.present()

    def load_css(self):
        """Load CSS with error handling."""
        try:
            style_provider = Gtk.CssProvider()
            style_provider.load_from_path('ui/style.css')
            Gtk.StyleContext.add_provider_for_display(
                Gtk.Widget.get_display(self.get_active_window() or Gtk.Window()),
                style_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            logger.info("CSS loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load CSS: {e}")

    def load_apps_async(self, window):
        """Load applications in a background thread."""
        def load():
            try:
                logger.info("Starting app refresh in background thread")
                apps = self.manager.refresh_apps()
                GLib.idle_add(window.show_apps, apps)
                
                # Check for updates and notify
                stats = self.manager.get_statistics()
                if stats['updates_available'] > 0 and self.config.get('show_notifications'):
                    GLib.idle_add(
                        self.notifications.send_update_available,
                        stats['updates_available']
                    )
            except Exception as e:
                logger.error(f"Error loading apps: {e}")
                GLib.idle_add(window.show_error, str(e))

        thread = threading.Thread(target=load, daemon=True)
        thread.start()

if __name__ == "__main__":
    orbit_app = OrbitApplication()
    sys.exit(orbit_app.run(sys.argv))


