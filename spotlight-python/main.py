import sys
import os
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Gio, GLib, Adw

class SpotlightApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='com.jaime.spotlight',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.all_apps = []
        self.filtered_apps = []
        self.is_grid_view = False

    def do_activate(self):
        self.load_apps()
        self.build_ui()

    def load_apps(self):
        # Load all system applications using Gio
        all_app_infos = Gio.AppInfo.get_all()
        for app in all_app_infos:
            if app.should_show():
                self.all_apps.append({
                    'name': app.get_name(),
                    'comment': app.get_description() or "",
                    'icon': app.get_icon(),
                    'app_info': app
                })
        self.all_apps.sort(key=lambda x: x['name'].lower())
        self.filtered_apps = self.all_apps[:]

    def build_ui(self):
        # Main Window
        self.win = Gtk.ApplicationWindow(application=self)
        self.win.set_default_size(680, 500)
        self.win.set_decorated(False) # Frameless
        self.win.set_title("Spotlight Python")
        
        # CSS Provider for Liquid Glass
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('style.css')
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Main Layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_box.add_css_class("spotlight-main")
        self.win.set_child(main_box)

        # Search Bar Area
        search_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        search_container.add_css_class("search-header")
        
        search_icon = Gtk.Image.new_from_icon_name("system-search-symbolic")
        search_icon.add_css_class("search-icon")
        
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Search applications...")
        self.search_entry.set_hexpand(True)
        self.search_entry.add_css_class("search-input")
        self.search_entry.connect("changed", self.on_search_changed)
        self.search_entry.connect("activate", self.on_enter_pressed)
        
        self.view_toggle_btn = Gtk.Button()
        self.view_toggle_btn.set_icon_name("view-grid-symbolic")
        self.view_toggle_btn.add_css_class("view-toggle")
        self.view_toggle_btn.connect("clicked", self.toggle_view)

        search_container.append(search_icon)
        search_container.append(self.search_entry)
        search_container.append(self.view_toggle_btn)
        
        main_box.append(search_container)

        # Scrollable area for results
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_vexpand(True)
        self.scroll.add_css_class("results-area")
        
        # Results container (Stack for Grid/List)
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list_box.connect("row-activated", self.on_row_activated)
        
        self.grid = Gtk.FlowBox()
        self.grid.set_valign(Gtk.Align.START)
        self.grid.set_max_children_per_line(6)
        self.grid.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.grid.connect("child-activated", self.on_child_activated)

        self.stack.add_named(self.list_box, "list")
        self.stack.add_named(self.grid, "grid")
        
        self.scroll.set_child(self.stack)
        main_box.append(self.scroll)

        # Focus lost -> close
        # In GTK4 we use EventControllerFocus
        focus_ctrl = Gtk.EventControllerFocus()
        focus_ctrl.connect("leave", lambda _: self.win.close())
        self.win.add_controller(focus_ctrl)

        # Keyboard shortcuts (Esc)
        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.connect("key-pressed", self.on_key_pressed)
        self.win.add_controller(key_ctrl)

        self.render_results()
        self.win.present()
        self.search_entry.grab_focus()

    def toggle_view(self, btn):
        self.is_grid_view = not self.is_grid_view
        self.stack.set_visible_child_name("grid" if self.is_grid_view else "list")
        btn.set_icon_name("view-list-symbolic" if self.is_grid_view else "view-grid-symbolic")
        self.render_results()

    def on_search_changed(self, entry):
        query = entry.get_text().lower()
        self.filtered_apps = [a for a in self.all_apps if query in a['name'].lower() or query in a['comment'].lower()]
        self.render_results()

    def render_results(self):
        # Clear current results
        while (child := self.list_box.get_first_child()): self.list_box.remove(child)
        while (child := self.grid.get_first_child()): self.grid.remove(child)

        for app in self.filtered_apps[:200]: # Increased limit
            if self.is_grid_view:
                self.grid.append(self.create_grid_item(app))
            else:
                self.list_box.append(self.create_list_item(app))

        
        # Select first item
        if not self.is_grid_view:
            first_row = self.list_box.get_row_at_index(0)
            if first_row: self.list_box.select_row(first_row)

    def create_list_item(self, app):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        box.add_css_class("app-item-list")
        
        icon = Gtk.Image.new_from_gicon(app['icon'])
        icon.set_pixel_size(32)
        icon.add_css_class("app-icon")
        
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        name_label = Gtk.Label(label=app['name'], xalign=0)
        name_label.add_css_class("app-name")
        
        desc_label = Gtk.Label(label=app['comment'], xalign=0)
        desc_label.add_css_class("app-desc")
        desc_label.set_ellipsize(True)
        desc_label.set_max_width_chars(60)

        info_box.append(name_label)
        info_box.append(desc_label)
        
        box.append(icon)
        box.append(info_box)
        return box

    def create_grid_item(self, app):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.add_css_class("app-item-grid")
        box.set_size_request(100, -1) # Let height be dynamic for wrapped text
        
        icon = Gtk.Image.new_from_gicon(app['icon'])
        icon.set_pixel_size(64)
        icon.add_css_class("app-icon-grid")
        
        name_label = Gtk.Label(label=app['name'])
        name_label.add_css_class("app-name-grid")
        name_label.set_wrap(True)
        name_label.set_justify(Gtk.Justification.CENTER)
        name_label.set_max_width_chars(15)
        name_label.set_halign(Gtk.Align.CENTER)

        box.append(icon)
        box.append(name_label)
        return box

    def on_enter_pressed(self, entry):
        if self.filtered_apps:
            self.launch_app(self.filtered_apps[0])

    def on_row_activated(self, listbox, row):
        index = row.get_index()
        self.launch_app(self.filtered_apps[index])

    def on_child_activated(self, flowbox, child):
        index = child.get_index()
        self.launch_app(self.filtered_apps[index])

    def launch_app(self, app):
        app['app_info'].launch(None, None)
        self.win.close()

    def on_key_pressed(self, ctrl, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            self.win.close()
            return True
        return False

if __name__ == "__main__":
    app = SpotlightApp()
    app.run(sys.argv)
       desc_label.add_css_class("app-desc")
        desc_label.set_ellipsize(True)
        desc_label.set_max_width_chars(60)

        info_box.append(name_label)
        info_box.append(desc_label)
        
        box.append(icon)
        box.append(info_box)
        return box

    def create_grid_item(self, app):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.add_css_class("app-item-grid")
        box.set_size_request(100, -1) # Let height be dynamic for wrapped text
        
        icon = Gtk.Image.new_from_gicon(app['icon'])
        icon.set_pixel_size(64)
        icon.add_css_class("app-icon-grid")
        
        name_label = Gtk.Label(label=app['name'])
        name_label.add_css_class("app-name-grid")
        name_label.set_wrap(True)
        name_label.set_justify(Gtk.Justification.CENTER)
        name_label.set_max_width_chars(15)
        name_label.set_halign(Gtk.Align.CENTER)

        box.append(icon)
        box.append(name_label)
        return box

    def on_enter_pressed(self, entry):
        if self.filtered_apps:
            self.launch_app(self.filtered_apps[0])

    def on_row_activated(self, listbox, row):
        index = row.get_index()
        self.launch_app(self.filtered_apps[index])

    def on_child_activated(self, flowbox, child):
        index = child.get_index()
        self.launch_app(self.filtered_apps[index])

    def launch_app(self, app):
        app['app_info'].launch(None, None)
        self.win.close()

    def on_key_pressed(self, ctrl, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            self.win.close()
            return True
        return False

if __name__ == "__main__":
    app = SpotlightApp()
    app.run(sys.argv)
