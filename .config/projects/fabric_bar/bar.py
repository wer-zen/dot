import fabric
from fabric import Application
from fabric.widgets.datetime import DateTime
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils.helpers import get_relative_path, monitor_file

# Import your battery widget
from battery import Battery  # Assuming battery.py is in the same directory

class StatusBar(Window):
    def __init__(self, **kwargs):
        super().__init__(

            name="outer-bar",
            layer="top",
            anchor="top left right",
            margin="20px 10px 10px 20px",
            exclusivity="auto",
            visible=True,
            all_visible=True,


        )



        # Create the main container
        self.main = CenterBox(name="inner-bar", spacing=30)

        # Create widgets
        self.date_time = DateTime()
        self.battery = Battery()  # Create battery widget

        # Add widgets to different sections of the CenterBox
        self.main.center_children = self.date_time
        self.main.end_children = self.battery
        # Add the main container to the window
        self.add(self.main)

        # Force minimum height at GTK level
        self.set_size_request(-1, 40)

        self.show_all()

if __name__ == "__main__":
    bar = StatusBar()
    app = Application("bar", bar)

    def apply_stylesheet(*_):
        try:
            app.set_stylesheet_from_file(get_relative_path("bar_style.css"))

        except FileNotFoundError:
            print("style.css not found, continuing without styling")

    try:
        style_monitor = monitor_file(get_relative_path("bar_style.css"))
        style_monitor.connect("changed", apply_stylesheet)
        apply_stylesheet()
    except FileNotFoundError:
        print("style.css not found, continuing without file monitoring")

    app.run()
