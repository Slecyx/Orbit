"""Desktop notification support for Orbit."""

import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify, GLib

class NotificationManager:
    """Manages desktop notifications."""
    
    def __init__(self, app_name='Orbit'):
        self.app_name = app_name
        self.initialized = False
        try:
            Notify.init(app_name)
            self.initialized = True
        except Exception as e:
            print(f"Failed to initialize notifications: {e}")
    
    def send(self, title: str, message: str, icon: str = 'system-software-install'):
        """
        Send a desktop notification.
        
        Args:
            title: Notification title
            message: Notification message
            icon: Icon name
        """
        if not self.initialized:
            return
        
        try:
            notification = Notify.Notification.new(title, message, icon)
            notification.show()
        except Exception as e:
            print(f"Failed to send notification: {e}")
    
    def send_update_available(self, count: int):
        """Send notification about available updates."""
        self.send(
            'Updates Available',
            f'{count} package(s) can be updated',
            'system-software-update'
        )
    
    def send_operation_complete(self, operation: str, success: bool = True):
        """Send notification about completed operation."""
        if success:
            self.send(
                'Operation Complete',
                f'{operation} completed successfully',
                'emblem-ok-symbolic'
            )
        else:
            self.send(
                'Operation Failed',
                f'{operation} failed',
                'dialog-error-symbolic'
            )
    
    def __del__(self):
        if self.initialized:
            Notify.uninit()
