"""Statistics dashboard for Orbit."""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

class StatisticsView(Gtk.Box):
    """Display statistics about installed applications."""
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.set_margin_top(20)
        self.set_margin_bottom(20)
        self.set_margin_start(20)
        self.set_margin_end(20)
        
        # Title
        title = Gtk.Label(label="📊 Package Statistics")
        title.add_css_class("title-1")
        self.append(title)
        
        # Stats container
        self.stats_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.append(self.stats_box)
    
    def update_statistics(self, stats: dict):
        """Update the statistics display."""
        # Clear existing
        while child := self.stats_box.get_first_child():
            self.stats_box.remove(child)
        
        # Total apps card
        total_card = self._create_stat_card(
            "Total Applications",
            str(stats.get('total', 0)),
            "📦"
        )
        self.stats_box.append(total_card)
        
        # By source breakdown
        by_source = stats.get('by_source', {})
        if by_source:
            source_group = Adw.PreferencesGroup(title="By Package Source")
            for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
                row = Adw.ActionRow(title=source)
                badge = Gtk.Label(label=str(count))
                badge.add_css_class("badge")
                badge.add_css_class("numeric")
                row.add_suffix(badge)
                source_group.add(row)
            self.stats_box.append(source_group)
        
        # Other stats
        other_group = Adw.PreferencesGroup(title="Additional Info")
        
        # Updates available
        updates_row = Adw.ActionRow(
            title="Updates Available",
            subtitle="Packages with updates ready"
        )
        updates_badge = Gtk.Label(label=str(stats.get('updates_available', 0)))
        updates_badge.add_css_class("badge")
        if stats.get('updates_available', 0) > 0:
            updates_badge.add_css_class("warning")
        updates_row.add_suffix(updates_badge)
        other_group.add(updates_row)
        
        # Sandboxed apps
        sandboxed_row = Adw.ActionRow(
            title="Sandboxed Applications",
            subtitle="Apps running in isolation"
        )
        sandboxed_badge = Gtk.Label(label=str(stats.get('sandboxed', 0)))
        sandboxed_badge.add_css_class("badge")
        sandboxed_badge.add_css_class("success")
        sandboxed_row.add_suffix(sandboxed_badge)
        other_group.add(sandboxed_row)
        
        # Conflicts
        if stats.get('conflicts', 0) > 0:
            conflicts_row = Adw.ActionRow(
                title="Package Conflicts",
                subtitle="Apps with multiple sources"
            )
            conflicts_badge = Gtk.Label(label=str(stats.get('conflicts', 0)))
            conflicts_badge.add_css_class("badge")
            conflicts_badge.add_css_class("error")
            conflicts_row.add_suffix(conflicts_badge)
            other_group.add(conflicts_row)
        
        self.stats_box.append(other_group)
    
    def _create_stat_card(self, title: str, value: str, icon: str) -> Gtk.Box:
        """Create a statistics card."""
        card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        card.add_css_class("card")
        card.set_margin_top(6)
        card.set_margin_bottom(6)
        card.set_margin_start(12)
        card.set_margin_end(12)
        
        # Icon
        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class("title-1")
        card.append(icon_label)
        
        # Text container
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        text_box.set_hexpand(True)
        
        title_label = Gtk.Label(label=title)
        title_label.set_halign(Gtk.Align.START)
        title_label.add_css_class("caption")
        text_box.append(title_label)
        
        value_label = Gtk.Label(label=value)
        value_label.set_halign(Gtk.Align.START)
        value_label.add_css_class("title-2")
        text_box.append(value_label)
        
        card.append(text_box)
        
        return card
