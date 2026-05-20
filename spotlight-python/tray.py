import sys
import os
import gi
import signal
import subprocess

gi.require_version('Gtk', '3.0')
gi.require_version('AyatanaAppIndicator3', '0.1')
from gi.repository import Gtk, AyatanaAppIndicator3, GLib

MAIN_PID = int(sys.argv[1]) if len(sys.argv) > 1 else None

def show_app(item):
    # Try to launch via the installed command or directly
    try:
        subprocess.Popen(["spotlight-python"])
    except FileNotFoundError:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        main_script = os.path.join(script_dir, 'main.py')
        subprocess.Popen(["python3", main_script])

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
            # Main process is no longer running, so we should exit too
            Gtk.main_quit()
            return False
    return True

def main():
    indicator = AyatanaAppIndicator3.Indicator.new(
        "spotlight-python-tray",
        "system-search-symbolic",
        AyatanaAppIndicator3.IndicatorCategory.APPLICATION_STATUS
    )
    indicator.set_status(AyatanaAppIndicator3.IndicatorStatus.ACTIVE)
    
    menu = Gtk.Menu()
    
    item_show = Gtk.MenuItem(label="Show Spotlight")
    item_show.connect("activate", show_app)
    menu.append(item_show)
    
    item_quit = Gtk.MenuItem(label="Quit")
    item_quit.connect("activate", quit_app)
    menu.append(item_quit)
    
    menu.show_all()
    indicator.set_menu(menu)
    
    if MAIN_PID:
        # Check every 2 seconds if the main app is still alive
        GLib.timeout_add(2000, check_main_pid)
        
    # Handle graceful termination
    signal.signal(signal.SIGTERM, lambda *_: Gtk.main_quit())
    signal.signal(signal.SIGINT, lambda *_: Gtk.main_quit())
    
    Gtk.main()

if __name__ == "__main__":
    main()
