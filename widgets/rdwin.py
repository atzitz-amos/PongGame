import math
from tkinter import Toplevel, Canvas, TclError
from tkinter.font import Font

from borders import RightBottomBorder, LightLeftTopBorder, LeftTopBorder, LightRightBottomBorder
from widgets.animations import FanButtonOpeningAnim


class TransformableObject:

    def __init__(self, position, size):
        self.position = position
        self.size = size

    def scale(self, master_scale):
        """ Scales the TransformableObject given the master scale which correspond to new_size / old_size"""
        self.size[0] *= master_scale[0]
        self.size[1] *= master_scale[1]

    def translate(self, master_translation):
        """ Translates the TransformableObject given the master translation which correspond to new_pos - old_pos"""
        self.position[0] += master_translation[0]
        self.position[1] += master_translation[1]


class Taskbar:

    def __init__(self, canvas: Canvas, w, h, **kwargs):
        self.canvas = canvas
        self.kwargs = kwargs

        self.x, self.y, self.width, self.height = 0, 0, w, h

    def draw(self):
        pass

    def mouse_event(self, event):
        pass

    def proceed_click(self, ev, released=False):
        pass


class _InternalWindow(TransformableObject):

    def __init__(self, canvas, x, y, width, height, **kwargs):
        super().__init__((x, y), (width, height))
        self.canvas = canvas

        self.window = self.canvas.create_oval(x, y, x + width, y + height, width=kwargs.pop("width", 2))

        kwargs.setdefault("fill", "white")
        for k, v in kwargs.items():
            try:
                self.canvas.itemconfig(self.window, **{k: v})
            except TclError:
                pass


class DNDManager:

    def __init__(self, window):
        self.window = window
        self.grabbing = False
        self.grab_origin = (None, None)

    def set_grabbing(self, x, y, grabbing):
        self.grabbing = grabbing
        self.grab_origin = (x, y)

    def mouse_event(self, event):
        rx, ry = event.x, event.y
        w, h = self.window.width, self.window.height
        border = 10
        north = 0 < ry < border
        south = h - border < ry < h
        west = 0 < rx < border
        east = w - border < rx < w
        if north and west:
            cursor = "size_nw_se"
        elif north and east:
            cursor = "size_ne_sw"
        elif south and west:
            cursor = "size_nw_se"
        elif south and west:
            cursor = "size_ne_sw"
        else:
            cursor = "arrow"
        self.window.canvas["cursor"] = cursor
        if self.grabbing:
            x, y = event.x, event.y
            translation = x - self.grab_origin[0], y - self.grab_origin[1]
            rx, ry = self.window.position
            self.window.position = rx + translation[0], ry + translation[1]


class CircularButton:

    def __init__(self, taskbar, **kwargs):
        self.taskbar = taskbar

        self.action = kwargs.get("action")
        self.color = kwargs.get("color", "grey")
        self.text = kwargs.get("text")

        self.toggled = False

    def draw(self, x, y, x2, y2):
        w = x2 - x
        h = y2 - y
        self.square = self.taskbar.canvas.create_rectangle(x, y, x + w, y + h, width=0,
                                                           fill=self.color)
        self.xborder = RightBottomBorder(self.taskbar.window, x2, y2, w, h)
        self.xlightborder = LightLeftTopBorder(self.taskbar.window, x, y, w, h)

        self.x, self.y, self.x2, self.y2, self.w, self.h = x, y, x2, y2, w, h

        if self.text:
            self.font = Font()
            self.text_comp = self.taskbar.canvas.create_text(x + w / 2, y + h / 2
                                                             , text=self.text)

    def event_pressed(self):
        if not self.toggled:
            self.xborder.change(LeftTopBorder(self.taskbar.window, self.x, self.y, self.w, self.h))
            self.xlightborder.change(
                LightRightBottomBorder(self.taskbar.window, self.x2, self.y2, self.w, self.h))
            self.toggled = True

    def event_released(self):
        if self.toggled:
            self.xborder.back()
            self.xlightborder.back()
            if callable(self.action):
                """self.action()"""
            self.toggled = False

    def isButton(self, item):
        return (hasattr(self, "square") and self.square in item) or (
                hasattr(self, "text_comp") and self.text_comp in item)


class CircularTaskbar(Taskbar):

    @property
    def bbox(self):
        self.twidth = twidth = -self.kwargs.get("twidth", 30)
        x, y = self.width / 2 - self.win_sizex, self.height / 2
        return x + twidth, y - self.win_sizey + twidth, x + self.win_sizex * 2 - twidth, y + self.win_sizey - twidth

    @property
    def winbbox(self):
        self.twidth = twidth = -self.kwargs.get("twidth", 30)
        x, y = self.width / 2 - self.win_sizex, self.height / 2
        return x, y - self.win_sizey, x + self.win_sizex * 2, y + self.win_sizey

    def __init__(self, window, width, height, win_sizex, win_sizey, **kwargs):
        Taskbar.__init__(self, window.canvas, width, height, **kwargs)
        self.window = window
        self.win_sizex = win_sizex
        self.win_sizey = win_sizey
        self.buttons = []

        self.arc = self.arc2 = None

        self.animation = FanButtonOpeningAnim(self)

    def getButtonsNum(self):
        return len(self.buttons)

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, v):
        self._visible = v
        if self._visible:
            self.canvas.itemconfig(self.arc, state="normal")
            self.canvas.itemconfig(self.arc2, state="normal")
            self.animation.fw()
        else:
            self.canvas.itemconfig(self.arc, state="hidden")
            self.canvas.itemconfig(self.arc2, state="hidden")
            self.animation.bw()

    def draw(self):
        self.arc = self.canvas.create_arc(*self.bbox, start=0, extent=180, fill="lightgrey")
        self.arc2 = self.canvas.create_arc(*self.winbbox, start=0, extent=180, fill="white", outline="")

        self.visible = False

        self.draw_buttons()

    def draw_buttons(self):
        if self.kwargs.get("tshowquit", True):
            self.buttons.append(CircularButton(self,
                                               action=self.kwargs.get("tquit", lambda: self.window.quit()),
                                               color=self.kwargs.get("tquitcolor", "grey"),
                                               text=self.kwargs.get("tquittext", "Quit")))
        """for position in self.arrange_buttons(5):  # zip(self.arrange_buttons(), self.buttons):
            p1, p2 = position[:2], position[2:]
            self.canvas.create_line(p1, width=2.3, fill="#AAA")
            self.canvas.create_line(p1, width=2)
            self.canvas.create_line(p2, width=2.3, fill="#AAA")
            self.canvas.create_line(p2, width=2)"""

    @property
    def ccenter(self):
        return self.window.win.position[0] + self.window.win.size[0] / 2, self.window.win.position[1] + \
               self.window.win.size[1] / 2

    def tick(self):
        self.animation.tick()

        x = self.window.toplevel.winfo_pointerx() - self.window.toplevel.winfo_rootx()
        y = self.window.toplevel.winfo_pointery() - self.window.toplevel.winfo_rooty()
        if self.arc in self.canvas.find_closest(x, y, start=self.arc):
            self.visible = True
        else:
            mx, my = self.ccenter
            detection_radius = self.win_sizey - 20
            vx, vy = mx - x, my - y
            if y < self.y + self.win_sizey and detection_radius ** 2 < vx ** 2 + vy ** 2 < self.win_sizey ** 2:
                if not self.visible:
                    self.visible = True
            elif self.visible:
                self.visible = False
        self.window.toplevel.after(10, self.tick)

    def proceed_click(self, ev, released=False):
        item = self.canvas.find_closest(ev.x, ev.y)
        for button in self.buttons:
            if button.isButton(item):
                if released:
                    button.event_released()
                else:
                    button.event_pressed()
                return True

    @property
    def inner_angle(self):
        circ = self.kwargs.get("tcirc", 60)
        return circ * 360 / (math.pi * 2 * self.win_sizey)

    def arrange_buttons(self, length):
        cx, cy = self.ccenter
        sy = cy - self.win_sizey
        angle = self.inner_angle
        if length % 2 == 0:
            subangle = 270
        else:
            subangle = 270 + angle / 2

        def pos(rad, num, factor=1):
            return cx + rad * math.cos(math.radians(subangle - angle * num * factor)), cy + rad * math.sin(
                math.radians(subangle - angle * num * factor))

        """self.canvas.create_line(pos(self.win_sizey, 0), pos(self.win_sizey - self.twidth, 0))
        self.canvas.create_line(pos(self.win_sizey, 1), pos(self.win_sizey - self.twidth, 1))
        self.canvas.create_line(pos(self.win_sizey, 2), pos(self.win_sizey - self.twidth, 2))"""
        if length % 2 != 0:
            t0 = pos(self.win_sizey, length // 2 + 1), pos(
                self.win_sizey - self.twidth, length // 2 + 1)
        else:
            t0 = pos(self.win_sizey, length // 2, factor=-1), pos(self.win_sizey - self.twidth, length // 2, factor=-1),
        prev = None
        for n in range(1, length + 1):
            if n < (length + 1) / 2:
                factor = 1
                i = n
            else:
                factor = -1
                i = n - length // 2 - 1
            current = pos(self.win_sizey, i, factor=factor), pos(self.win_sizey - self.twidth, i, factor=factor)
            if not prev:
                yield *t0, *current
            else:
                yield *prev, *current
            prev = current
            self.canvas.create_line(pos(self.win_sizey, i, factor=factor),
                                    pos(self.win_sizey - self.twidth, i, factor=factor))


class RDWin:

    def mouse_event(self, event):
        self.dnd.mouse_event(event)

    def mouse_pressed(self, ev):
        if self.taskbar and self.taskbar.proceed_click(ev):
            return
        self.dnd.set_grabbing(ev.x, ev.y, True)

    def mouse_released(self, ev):
        if self.taskbar and self.taskbar.proceed_click(ev, released=True):
            return
        self.dnd.set_grabbing(ev.x, ev.y, False)

    def __init__(self, master, width=300, height=300, position=(500, 500), **kwargs):
        self.master = master
        self.toplevel = Toplevel(master)

        self.transparency = "#f46a32"
        self.toplevel.wm_attributes("-transparentcolor", self.transparency)
        self.toplevel.wm_overrideredirect(True)
        self.toplevel["bg"] = self.transparency

        self.canvas = Canvas(self.toplevel, background=self.transparency, highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")

        win_sizex, win_sizey = width / 2 - 50, height / 2 - 50
        self.win = _InternalWindow(
            self.canvas,
            width / 2 - win_sizex, height / 2 - win_sizey,
            2 * win_sizex, 2 * win_sizey,
            **kwargs
        )
        ttype = kwargs.get("taskbar")
        match ttype:
            case "none":
                self.taskbar = None
            case "circular":
                self.taskbar = CircularTaskbar(self, width, height, win_sizex, win_sizey)
                self.toplevel.after(10, self.taskbar.tick)
            case _:
                self.taskbar = Taskbar(self.canvas, width, 23)
        if self.taskbar:
            self.taskbar.draw()
        self._width = width
        self._height = height
        self._position = position
        self.update_geometry()

        self.dnd = DNDManager(self)

        self.canvas.bind("<Button-1>", self.mouse_pressed)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_released)
        self.canvas.bind("<Motion>", self.mouse_event)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, newpos):
        self._position = newpos
        self.update_geometry()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, newwidth):
        self._width = newwidth
        self.update_geometry()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, newheight):
        self._height = newheight
        self.update_geometry()

    def update_geometry(self):
        self.toplevel.wm_geometry(f"{self.width}x{self.height}+{self.position[0]}+{self.position[1]}")

    def quit(self):
        self.toplevel.destroy()


if __name__ == '__main__':
    import tkinter

    tk = tkinter.Tk()
    tk.wm_attributes("-alpha", 0.0)
    app = RDWin(tk, width=300, taskbar="circular")
    tkinter.Button(app.toplevel, text="salut").place(x=130, y=135)
    tk.mainloop()
