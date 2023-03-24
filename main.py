import enum
import random
from tkinter import Toplevel, Tk, Label


class CollisionStatus(enum.Enum):
    NO_COLLISION = 0
    LEFT = 1
    RIGHT = 2
    TOP = 3
    BOTTOM = 4

    LEFT_CHANGE_SCREEN = 5
    RIGHT_CHANGE_SCREEN = 6


class BouncingWindow(Toplevel):
    speed = 6

    def __init__(self, collider):
        Toplevel.__init__(self)
        self.collider = collider

        self.wm_resizable(False, False)

        self.x = self.y = 10

        self.direction = [self.speed, self.speed]

        self.wm_geometry("100x100+10+10")

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.wm_geometry(f"+{x}+{y}")

    def update_movement(self):
        status = self.collider.collide(self.x, self.y, 100, 100)
        if status != CollisionStatus.NO_COLLISION:
            self.change_direction(status)
        self.move()

    def move(self):
        self.set_position(int(self.x + self.direction[0]), int(self.y + self.direction[1]))

    def change_direction(self, status):
        print(status)
        if status == CollisionStatus.LEFT:
            self.direction[0] = random.random() * self.speed
        elif status == CollisionStatus.RIGHT:
            self.direction[0] = -random.random() * self.speed
        if status == CollisionStatus.TOP:
            self.direction[1] = random.random() * self.speed
        elif status == CollisionStatus.BOTTOM:
            self.direction[1] = -random.random() * self.speed


class ColliderNormal:

    def __init__(self, screen_dim, window):
        self.screen_dim = screen_dim
        self.window = window

    def collide(self, x, y, w, h):
        left, right, top = self.screen_dim
        bottom_start = self.window.get_position()
        bottom_end = bottom_start[0] + self.window.width

        if x + w > right:
            return CollisionStatus.RIGHT
        if x < left:
            return CollisionStatus.LEFT
        if y < top:
            return CollisionStatus.TOP
        if y + h > bottom_start[1] and bottom_start[0] < x < bottom_end:
            return CollisionStatus.BOTTOM

        return CollisionStatus.NO_COLLISION


class MainWindow(Tk):

    def __init__(self):
        Tk.__init__(self)

        self.wm_resizable(False, False)

        self.collider = ColliderNormal((10, 1900, 10), self)
        self.bouncing_window = BouncingWindow(self.collider)

        self.width = 300
        self.height = 100
        self.x = 660
        self.y = 680

        self.update_geometry()

        self.bind("<Left>", lambda e: self.change_position(-1))
        self.bind("<Right>", lambda e: self.change_position(1))

        self.dumm_widget = Label(self)
        self.dumm_widget.pack()

        self.wait_visibility(self)
        self.focus_force()

    def change_position(self, key):
        self.x += key * 30

    def update_ball(self):
        self.bouncing_window.update_movement()
        self.update_geometry()
        self.lift()
        self.after(10, self.update_ball)

    def run(self):
        self.after(10, self.update_ball)
        self.mainloop()

    def update_geometry(self):
        self.wm_geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")

    def get_position(self):
        return self.x, self.y


if __name__ == '__main__':
    MainWindow().run()
