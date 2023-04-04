import enum
import random
import tkinter
from tkinter import Toplevel, Tk, Label, Button, Canvas
from tkinter.font import Font


class CollisionStatus(enum.Enum):
    NO_COLLISION_DONT_UPDATE = -2
    GAME_LOST = -1
    NO_COLLISION = 0
    LEFT = 1
    RIGHT = 2
    TOP = 3
    BOTTOM = 4

    LEFT_CHANGE_SCREEN = 5
    RIGHT_CHANGE_SCREEN = 6


class Bullet(Toplevel):
    speed = 7
    max_height = 60

    def __init__(self, x, y, collider, manager):
        Toplevel.__init__(self)
        self.collider = collider
        self.manager = manager

        self.wm_resizable(False, False)
        self.wm_attributes("-toolwindow", 1)
        self.wm_attributes("-alpha", 0.9)
        self["bg"] = "red"

        self.width = 1
        self.height = 1

        self.set_position(x, y)

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.update_geometry()

    def update_geometry(self):
        self.wm_geometry(f"{self.width}x{int(self.height)}+{self.x}+{self.y}")

    def update_movement(self):
        self.move()
        self.check_collisions()

    def move(self):
        if self.height < self.max_height:
            self.height += 10
        self.y -= 10
        self.update_geometry()

    def cancel(self):
        self.manager.cancel_bullet()

    def check_collisions(self):
        if self.collider.collide_main_window(self.x, self.y + self.height, -1, -1) != CollisionStatus.NO_COLLISION:
            return self.cancel()
        bw = self.manager.bouncing_window
        status, res = bw.check_if_collided(self.x, self.y, self.x + self.width, self.y + self.height - 10, 20)
        if status == CollisionStatus.NO_COLLISION_DONT_UPDATE:
            return
        elif status == CollisionStatus.BOTTOM:
            return self.manager.bullet_hit(*res)
        if self.collider.collide_bullet((bw.x - 10, bw.y + 10, bw.x + bw.width + 10, bw.y + bw.height + 10),
                                        (self.x, self.y)) == CollisionStatus.BOTTOM:
            return self.manager.bullet_hit(self.x, self.y + 1, self.x + 20, self.y - 15)


class LaserBeamBullet(Bullet):
    def __init__(self, x, y, collider, manager, laserbeam):
        Bullet.__init__(self, x, y, collider, manager)
        self.laserbeam = laserbeam
        self.width = 10
        self.height = 10
        self["bg"] = "white"

    def cancel(self):
        print("cancelling")
        self.laserbeam.cancel(self)

    def update_movement(self):
        super().update_movement()


class LaserBeam(Bullet):

    def __init__(self, x, y, collider, manager):
        Bullet.__init__(self, x, y, collider, manager)
        print(self.y)
        self["bg"] = "blue"
        # self.overrideredirect(1)
        self.width = 10
        self.update_geometry()

        self.bullets = []

    def update_movement(self):
        super().update_movement()
        for bullet in self.bullets:
            bullet.update_movement()

    def move(self):
        self.height += 20
        if self.height > self.manager.screen_dim[3]:
            self.height = self.manager.screen_dim[3]
        else:
            self.y -= 20

    def check_collisions(self):
        pass

    def fire(self):
        print("fired")
        self.bullets.append(LaserBeamBullet(self.x, self.y + self.height, self.collider, self.manager, self))

    def cancel(self, b):
        # b.destroy()
        # self.bullets.remove(b)
        pass


class BouncingWindow(Toplevel):
    speed = 3

    def __init__(self, collider):
        Toplevel.__init__(self)
        self.collider = collider
        self.alpha_color = "#add123"

        self.wm_resizable(False, False)
        self.wm_attributes("-transparentcolor", self.alpha_color)
        self.overrideredirect(1)

        self.x = self.y = 10
        self.width = self.height = 100

        self.direction = [self.speed, self.speed]

        self.update_geometry()

        self.canvas = Canvas(self, background=self["bg"])
        self.canvas.place(x=0, y=0, width=self.width + 50, height=self.height + 50)

        self.sub_pos_x = self.sub_pos_y = 0
        self.sub_rad = 0
        self.drawing = None

        self.collided_territory = []

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.update_geometry()

    def update_geometry(self):
        self.wm_geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")

    def update_movement(self):
        status = self.collider.collide_main_window(self.x, self.y, 100, 100)
        if status != CollisionStatus.NO_COLLISION:
            self.change_direction(status)
        self.move()

    def move(self):
        self.set_position(int(self.x + self.direction[0]), int(self.y + self.direction[1]))

    def change_direction(self, status):
        if status == CollisionStatus.LEFT:
            self.direction[0] = random.random() * self.speed
        elif status == CollisionStatus.RIGHT:
            self.direction[0] = -random.random() * self.speed
        if status == CollisionStatus.TOP:
            self.direction[1] = random.random() * self.speed
        elif status == CollisionStatus.BOTTOM:
            self.direction[1] = -random.random() * self.speed

    def hit(self, hit_x, hit_y, hit_x2, hit_y2):
        # self.sub_pos_x = self.width / 2 - random.randint(-20, 20)
        # self.sub_pos_y = self.height / 2 - random.randint(-20, 20)
        # self.drawing = self.canvas.create_oval(self.sub_pos_x - self.sub_rad, self.sub_pos_y - self.sub_rad,
        # self.sub_pos_x + self.sub_rad, self.sub_pos_y + self.sub_rad,outline = "red", width = 2) self.after(10,
        # self.draw_update)
        self.canvas.create_rectangle(hit_x - self.x, hit_y - self.y, hit_x2 - self.x, hit_y2 - self.y,
                                     fill=self.alpha_color, outline="")
        self.collided_territory.append((hit_x - self.x, hit_y - self.y, hit_x2 - self.x, hit_y2 - self.y))

    def check_if_collided(self, X, Y, X2, Y2, radius):
        x = X - self.x
        y = Y - self.y
        x2 = X2 - self.x
        y2 = Y2 - self.y
        for tx, ty, tx2, ty2 in self.collided_territory.copy():
            if x >= tx and x2 <= tx2:
                print(X, Y, X2, Y2)
                if y2 <= ty:
                    print("------------------------------------------------------------")
                    self.collided_territory.remove((tx, ty, tx2, ty2))
                    return CollisionStatus.BOTTOM, (X, ty2 + self.y, X + radius, ty + self.y - radius)
                return CollisionStatus.NO_COLLISION_DONT_UPDATE, None

        return CollisionStatus.NO_COLLISION, None


def draw_update(self):
    self.canvas.coords(self.drawing, self.sub_pos_x - self.sub_rad, self.sub_pos_y - self.sub_rad,
                       self.sub_pos_x + self.sub_rad, self.sub_pos_y + self.sub_rad)
    self.sub_rad += 1

    if self.sub_rad > max(self.width, self.height):
        self.canvas.delete(self.drawing)
        self.sub_rad = 0
        self.drawing = None
        return
    self.after(10, self.draw_update)


class ColliderNormal:

    def __init__(self, screen_dim, window):
        self.screen_dim = screen_dim
        self.window = window

    def collide_screen(self, x, y, w, h):
        return self.collide(*self.screen_dim, (x, y, x + w, y + h))

    def collide_main_window(self, x, y, w, h):
        left, right, top, bottom = self.screen_dim
        bottom_start_x, bottom_start_y = self.window.get_position()
        bottom_end = bottom_start_x + self.window.width

        if y + h > bottom:
            self.window.end_game()
            return CollisionStatus.GAME_LOST
        if y + h > bottom_start_y and bottom_start_x < x < bottom_end:
            return CollisionStatus.BOTTOM

        return self.collide((left, top, right, bottom), (x, y, x + w, y + h))

    def collide(self, bbox_collider, bbox_collided):
        left, top, right, bottom = bbox_collider
        x1, y1, x2, y2 = bbox_collided

        if x2 > right:
            return CollisionStatus.RIGHT
        if x1 < left:
            return CollisionStatus.LEFT
        if y1 < top:
            return CollisionStatus.TOP
        if y2 > bottom:
            return CollisionStatus.BOTTOM
        return CollisionStatus.NO_COLLISION

    def collide_bullet(self, bbox1, bbox2):
        left, top, right, bottom = bbox1
        x1, y1 = bbox2

        if left < x1 < right and top < y1 < bottom:
            return CollisionStatus.BOTTOM
        return CollisionStatus.NO_COLLISION


class MainWindow(Tk):
    speed = 6
    acceleration = 0.8

    end_width = 550
    end_height = 500

    end_time = 0.5 * 100

    laserbeam_duration = 300

    def __init__(self, screen_dim):
        Tk.__init__(self)

        self.distance_center = (0, 0)
        self.screen_dim = screen_dim

        self.wm_resizable(False, False)

        self.collider = ColliderNormal(screen_dim, self)
        self.bouncing_window = BouncingWindow(self.collider)
        self.bullet = None

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
        self.bind("<space>", lambda e: self.fire())

        self.wait_visibility(self)
        self.focus_force()

        self.laserbeam = None
        self.laserbeam_time = 0

    def change_position(self, key):
        if self.movement >= 0 and key == -1 or self.movement != 0 and key == 0 or self.movement <= 0 and key == 1:
            self.time = 0
        self.time += 1
        self.movement = self.time * self.acceleration * key
        if -1 > self.movement or self.movement > 1:
            self.movement = key

    def update_ball(self):
        self.bouncing_window.update_movement()
        if self.bullet:
            self.bullet.update_movement()
        if self.laserbeam:
            self.laserbeam.update_movement()
            self.laserbeam.set_position(int(self.x + self.width / 2 - 5), self.laserbeam.y)
            self.laserbeam_time += 1
            if self.laserbeam_time > self.laserbeam_duration:
                self.cancel_laserbeam()
            elif self.laserbeam_time % 50 == 0:
                self.laserbeam.fire()
        self.lift()
        self.focus_force()
        self.slide()
        self.running_pid = self.after(10, self.update_ball)

    def run(self):
        self.running_pid = self.after(10, self.update_ball)
        self.mainloop()

    def fire(self):
        if not self.laserbeam:
            if not self.bullet:
                if random.random() < 0:
                    print("laserbeam")
                    self.laserbeam = LaserBeam(int(self.x + self.width / 2 - 5), self.y, self.collider, self)
                else:
                    print("bullet")
                    self.bullet = Bullet(int(self.x + self.width / 2 - 5), self.y, self.collider, self)

    def cancel_bullet(self):
        self.bullet.destroy()
        self.bullet = None

    def cancel_laserbeam(self):
        self.laserbeam.destroy()
        self.laserbeam = None

    def bullet_hit(self, hit_x, hit_y, hit_x2, hit_y2):
        self.cancel_bullet()
        self.bouncing_window.hit(hit_x, hit_y, hit_x2, hit_y2)

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

        speed_x, speed_y = self.distance_center[0] / (self.end_time), self.distance_center[1] / (self.end_time)
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
