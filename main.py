import enum
import random
from tkinter import Toplevel, Tk


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

    def collide(self, x, y, w, h, horizontal=True):
        left, right, top, bottom = self.screen_dim

        win_startY, win_startX = self.window.get_position()

        win_end = win_startY + self.window.height

        if y < top:
            return CollisionStatus.TOP
        if y + h > bottom:
            return CollisionStatus.BOTTOM

        if x < left and horizontal:
            Main.inst().scored(Team.TEAM_RIGHT)
            return CollisionStatus.LEFT_LOST
        if x + w > right and horizontal:
            Main.inst().scored(Team.TEAM_LEFT)
            return CollisionStatus.RIGHT_LOST

        return CollisionStatus.NO_COLLISION


class BaseWindow(Tk):
    speed = 4
    border = 10

    def __init__(self, team, screen_width, screen_height):
        Tk.__init__(self)

        self.wm_resizable(False, False)

        self.team = team
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.collider = ColliderNormal((self.border, self.screen_width, self.border, self.screen_height), self)

        self.width = 100
        self.height = 350
        self.x = screen_width - 340 if team == Team.TEAM_RIGHT else 240
        self.y = int(screen_height / 2 - self.height)

        self.update_geometry()

        self.movement = 0

    def change_position(self, key):
        self.movement = key

    def tick(self):
        self.slide()
        self.lift()
        self.after(10, self.tick)

    def run(self):
        self.after(10, self.tick)

    def update_geometry(self):
        if self.x == 240:
            print(f"{self.width}x{self.height}+{self.x}+{self.y}")
        self.wm_geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")

    def get_position(self):
        return self.x, self.y

    def slide(self):
        if not self.assert_in_bounds():
            print("Not in Bounds")
            self.y = 10 if self.y < 0 else self.screen_height - 10
            return
        self.y += self.movement * self.speed
        self.update_geometry()

    def assert_in_bounds(self):
        return self.collider.collide(self.x, self.y, self.width, self.height,
                                     horizontal=False) == CollisionStatus.NO_COLLISION


class PrimaryWindow(BaseWindow):

    def __init__(self, team, screen_width, screen_height):
        super().__init__(team, screen_width, screen_height)

        self.bind("<Left>", lambda e: self.change_position(-1))
        self.bind("<Right>", lambda e: self.change_position(1))
        self.bind("<KeyRelease-Left>", lambda e: self.change_position(0))
        self.bind("<KeyRelease-Right>", lambda e: self.change_position(0))
        self.bind("<Up>", lambda e: self.change_position(-1))
        self.bind("<Down>", lambda e: self.change_position(1))
        self.bind("<KeyRelease-Up>", lambda e: self.change_position(0))
        self.bind("<KeyRelease-Down>", lambda e: self.change_position(0))

    def tick(self):
        self.slide()
        self.lift()
        self.focus_force()
        self.after(10, self.tick)


class SecondaryWindow(BaseWindow):
    def __init__(self, team, screen_width, screen_height):
        super().__init__(team, screen_width, screen_height)

        self.update_geometry()

    def change_position(self, key):
        return


class MultiplayerManager:
    def __init__(self, host):
        self.host = host


class Main:
    _INSTANCE = None

    @classmethod
    def inst(cls):
        return cls._INSTANCE

    def __init__(self, host, screen):
        self.isHost = host
        self.screen = screen

        self.points = {Team.TEAM_RIGHT: 0, Team.TEAM_LEFT: 0}
        self.window = None
        self.swindow = None
        self.manager = None
        if self.isHost:
            self.init_host_mode()
        else:
            self.init_normal_mode()

        self._INSTANCE = self

    def init_host_mode(self):
        self.manager = MultiplayerManager(True)
        self.window = PrimaryWindow(Team.TEAM_LEFT, self.screen[0], self.screen[1])
        self.swindow = SecondaryWindow(Team.TEAM_RIGHT, self.screen[0], self.screen[1])

    def init_normal_mode(self):
        self.manager = MultiplayerManager(False)
        self.window = PrimaryWindow(Team.TEAM_RIGHT, self.screen[0], self.screen[1])
        self.swindow = SecondaryWindow(Team.TEAM_LEFT, self.screen[0], self.screen[1])

    def scored(self, team):
        self.points[team] += 1

    def get_winner(self):
        if self.points[Team.TEAM_RIGHT] > self.points[Team.TEAM_LEFT]:
            return Team.TEAM_RIGHT
        elif self.points[Team.TEAM_LEFT] > self.points[Team.TEAM_LEFT]:
            return Team.TEAM_LEFT
        return None

    def mainloop(self):
        self.window.run()
        self.swindow.run()
        self.window.mainloop()


if __name__ == '__main__':
    Main(True, (1536, 960)).mainloop()
