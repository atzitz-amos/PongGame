import enum
import random
from tkinter import Toplevel, Tk, Label


class Team:
    TEAM_LEFT = 0
    TEAM_RIGHT = 1


class CollisionStatus(enum.Enum):
    NO_COLLISION = 0
    LEFT = 1
    RIGHT = 2
    TOP = 3
    BOTTOM = 4

    LEFT_LOST = -1
    RIGHT_LOST = -2


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
        if status in (CollisionStatus.LEFT_LOST, CollisionStatus.RIGHT_LOST):
            return
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
        left, right, top, bottom = self.screen_dim

        win_startY, win_startX = self.window.get_position()

        win_end = win_startY + self.window.height

        if y < top:
            return CollisionStatus.TOP
        if y + h > bottom:
            return CollisionStatus.BOTTOM

        if x < left:
            MultiplayerManager.inst().scored(Team.TEAM_RIGHT)
            return CollisionStatus.LEFT_LOST
        if x + w > right:
            MultiplayerManager.inst().scored(Team.TEAM_LEFT)
            return CollisionStatus.RIGHT_LOST

        return CollisionStatus.NO_COLLISION


class MainWindow(Tk):
    speed = 6
    border = 10

    def __init__(self, screen_width, screen_height):
        Tk.__init__(self)

        self.wm_resizable(False, False)

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.collider = ColliderNormal((self.border, self.screen_width, self.border, self.screen_height), self)
        self.bouncing_window = BouncingWindow(self.collider)

        self.width = 100
        self.height = 350
        self.x = 660
        self.y = 680

        self.update_geometry()

        self.movement = 0

        self.bind("<Left>", lambda e: self.change_position(-1))
        self.bind("<Right>", lambda e: self.change_position(1))
        self.bind("<KeyRelease-Left>", lambda e: self.change_position(0))
        self.bind("<KeyRelease-Right>", lambda e: self.change_position(0))
        self.bind("<Up>", lambda e: self.change_position(-1))
        self.bind("<Down>", lambda e: self.change_position(1))
        self.bind("<KeyRelease-Up>", lambda e: self.change_position(0))
        self.bind("<KeyRelease-Down>", lambda e: self.change_position(0))

        self.dumm_widget = Label(self)
        self.dumm_widget.pack()

        self.wait_visibility(self)
        self.focus_force()

    def change_position(self, key):
        self.movement = key

    def update_ball(self):
        self.bouncing_window.update_movement()
        self.slide()
        self.lift()
        self.after(10, self.update_ball)

    def run(self):
        self.after(10, self.update_ball)
        self.mainloop()

    def update_geometry(self):
        self.wm_geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")

    def get_position(self):
        return self.x, self.y

    def slide(self):
        self.y += self.movement * self.speed
        self.assert_in_bounds()
        self.update_geometry()

    def assert_in_bounds(self):
        pass


class MultiplayerManager:
    _INSTANCE = None

    @classmethod
    def inst(cls):
        return cls._INSTANCE

    def bbox(self, team):
        pass

    def scored(self, team):
        pass


class Main:

    def __init__(self, host):
        self.isHost = host
        if self.isHost:
            self.init_host_mode()
        else:
            self.init_normal_mode()

    def init_host_mode(self):
        MultiplayerManager(True)
        self.window = MainWindow(Team.TEAM_LEFT)

    def init_normal_mode(self):
        MultiplayerManager(False)
        self.window = Team.TEAM_RIGHT


if __name__ == '__main__':
    MainWindow(1920, 1080).run()
