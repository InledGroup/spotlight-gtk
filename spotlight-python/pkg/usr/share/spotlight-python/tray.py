import sys
import os
import gi
import signal
import subprocess

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

MAIN_PID = int(sys.argv[1]) if len(sys.argv) > 1 else None

def show_app(icon=None):
    # This is called on left click
    try:
        # Try to call the installed binary first
        subprocess.Popen(["spotlight-python"])
    except FileNotFoundError:
        # Fallback to local script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        main_script = os.path.join(script_dir, 'main.py')
        subprocess.Popen(["python3", main_script])

def on_popup_menu(icon, button, time):
    # This is called on right click
    menu = Gtk.Menu()
    
    item_show = Gtk.MenuItem(label="Show Spotlight")
    item_show.connect("activate", lambda _: show_app())
    menu.append(item_show)
    
    item_quit = Gtk.MenuItem(label="Quit")
    item_quit.connect("activate", quit_app)
    menu.append(item_quit)
    
    menu.show_all()
    menu.popup(None, None, Gtk.StatusIcon.position_menu, icon, button, time)

def quit_app(item):
    if MAIN_PID:
        try:
            os.kill(MAIN_PID, signal.SIGTERM)
        except OSError:
            pass
    Gtk.main_quit()

def check_main_pid():
    if MAIN_PID:
        try:
            os.kill(MAIN_PID, 0)
        except OSError:
            # Main process died
            Gtk.main_quit()
            return False
    return True

def main():
    # Gtk.StatusIcon supports 'activate' (left click)
    icon = Gtk.StatusIcon.new_from_icon_name("system-search-symbolic")
    icon.set_title("Spotlight")
    icon.set_tooltip_text("Spotlight Launcher")
    
    icon.connect("activate", show_app)
    icon.connect("popup-menu", on_popup_menu)
    
    if MAIN_PID:
        GLib.timeout_add(2000, check_main_pid)
        
    signal.signal(signal.SIGTERM, lambda *_: Gtk.main_quit())
    signal.signal(signal.SIGINT, lambda *_: Gtk.main_quit())
    
    Gtk.main()

if __name__ == "__main__":
    main()
