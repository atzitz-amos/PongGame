import enum
import random
from tkinter import Toplevel, Tk, Label, Button
from tkinter.font import Font


class CollisionStatus(enum.Enum):
    GAME_LOST = -1
    NO_COLLISION = 0
    LEFT = 1
    RIGHT = 2
    TOP = 3
    BOTTOM = 4

    LEFT_CHANGE_SCREEN = 5
    RIGHT_CHANGE_SCREEN = 6


class BouncingWindow(Toplevel):
    speed = 7

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
        left, right, top, bottom = self.screen_dim
        bottom_start = self.window.get_position()
        bottom_end = bottom_start[0] + self.window.width

        if x + w > right:
            return CollisionStatus.RIGHT
        if x < left:
            return CollisionStatus.LEFT
        if y < top:
            return CollisionStatus.TOP
        if y + h > bottom:
            self.window.end_game()
            return CollisionStatus.GAME_LOST
        if y + h > bottom_start[1] and bottom_start[0] < x < bottom_end:
            return CollisionStatus.BOTTOM

        return CollisionStatus.NO_COLLISION


class MainWindow(Tk):
    speed = 6
    acceleration = 0.8

    end_width = 550
    end_height = 500

    end_time = 0.5 * 100

    def __init__(self, screen_dim):
        Tk.__init__(self)

        self.distance_center = (0, 0)
        self.screen_dim = screen_dim

        self.wm_resizable(False, False)

        self.collider = ColliderNormal(screen_dim, self)
        self.bouncing_window = BouncingWindow(self.collider)

        self.width = 300
        self.height = 100
        self.x = 660
        self.y = 680

        self.movement = 0

        self.update_geometry()

        self.time = 0
        self.running_pid = None

        self.bind("<Left>", lambda e: self.change_position(-1))
        self.bind("<Right>", lambda e: self.change_position(1))
        self.bind("<KeyRelease-Left>", lambda e: self.change_position(0))
        self.bind("<KeyRelease-Right>", lambda e: self.change_position(0))

        self.wait_visibility(self)
        self.focus_force()

    def change_position(self, key):
        if self.movement >= 0 and key == -1 \
                or self.movement != 0 and key == 0 \
                or self.movement <= 0 and key == 1:
            self.time = 0
        self.time += 1
        self.movement = self.time * self.acceleration * key
        if -1 > self.movement or self.movement > 1:
            self.movement = key

    def update_ball(self):
        self.bouncing_window.update_movement()
        self.lift()
        self.focus_force()
        self.slide()
        self.running_pid = self.after(10, self.update_ball)

    def run(self):
        self.running_pid = self.after(10, self.update_ball)
        self.mainloop()

    def update_geometry(self):
        self.wm_geometry(f"{int(self.width)}x{int(self.height)}+{int(self.x)}+{int(self.y)}")

    def get_position(self):
        return self.x, self.y

    def slide(self):
        self.x += int(self.movement * self.speed)
        self.update_geometry()

    def end_game(self):
        self.bouncing_window.destroy()

        self.unbind("<Left>")
        self.unbind("<Right>")
        self.unbind("<KeyRelease-Left>")
        self.unbind("<KeyRelease-Right>")

        self.movement = 0

        self.distance_center = (-self.x + self.get_center()[0], -self.y + self.get_center()[1])

        speed_x, speed_y = self.distance_center[0] / (self.end_time), self.distance_center[1] / (
            self.end_time)
        speed_w, speed_h = (self.end_width - self.width) / (self.end_time), (self.end_height - self.height) / (
            self.end_time)

        self.after(10, lambda: self.slide_end_game(speed_x, speed_y, speed_w, speed_h))

    def slide_end_game(self, speed_x, speed_y, speed_w, speed_h):
        self.after_cancel(self.running_pid)
        self.movement = 0

        self.x = self.x + speed_x
        self.y = self.y + speed_y
        self.width = self.width + speed_w
        self.height = self.height + speed_h
        self.update_geometry()

        self.time += 1

        if self.time > self.end_time:
            return self.show_end_screen()

        self.after(10, lambda: self.slide_end_game(speed_x, speed_y, speed_w, speed_h))

    def get_center(self):
        return self.screen_dim[1] / 2 - self.end_width / 2, self.screen_dim[3] / 2 - self.end_height / 2

    def show_end_screen(self):
        print("end")
        font = Font(font=("Bahnschrift", 20, "normal"))
        lx, ly = self.end_width / 2 - font.measure("Vous avez perdu") / 2 - 20, self.end_height / 2 - 60
        Label(self, text="Vous avez perdu !", font=font).place(x=lx, y=ly)

        Button(self, text="Rejouer", command=self.new_game).place(x=self.end_width / 2 - 70, y=ly + 50)
        Button(self, text="Quitter", command=self.destroy).place(x=self.end_width / 2 + 10, y=ly + 50)

    def new_game(self):
        self.destroy()
        self.quit()
        new_game()


def new_game():
    MainWindow((10, 1516, 10, 940)).run()


if __name__ == '__main__':
    new_game()
