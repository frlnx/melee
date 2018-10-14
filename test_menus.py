from pyglet import app

from gui.models.movable import MovableMixin
from gui.window import Window

if __name__ == "__main__":
    win = Window(width=1024, height=768)
    button = MovableMixin(10, 100, 10, 100)
    win.add_component(button)
    app.run()
