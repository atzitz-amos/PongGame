class Border:

    def __init__(self, master):
        self.master = master.toplevel
        self.screen = master.canvas
        self._border = None

    def delete(self):
        if self._border:
            self.screen.delete(self._border)

    def change(self, border):
        print("Changed")
        self.screen.itemconfigure(self._border, state='hidden')
        self._xdchangedborder = border
        return self._xdchangedborder

    def back(self):
        if hasattr(self, '_xdchangedborder'):
            self._xdchangedborder.delete()
            self.screen.itemconfig(self._border, state='normal')

    def __getitem__(self, k):
        return self.screen.itemcget(self._border, k)

    def __setitem__(self, k, v):
        self.screen.itemconfig(self._border, {k: v})


class LeftBottomBorder(Border):

    def __init__(self, master, x, y, s1, s2):
        Border.__init__(self, master)

        self.s1 = s1
        self.s2 = s2
        self.x = x
        self.y = y

        self._border = self.screen.create_line(x, y - self.s1, x, y, x + self.s2, y, fill='gray25', width=0.1)


class RightBottomBorder(Border):

    def __init__(self, master, x, y, s1, s2):
        Border.__init__(self, master)

        self.s1 = s1
        self.s2 = s2
        self.x = x
        self.y = y

        self._border = self.screen.create_line(x, y - self.s2, x, y, x - self.s1, y, fill='gray25', width=0.1)


class LeftTopBorder(Border):

    def __init__(self, master, x, y, s1, s2):
        Border.__init__(self, master)

        self.x = x
        self.y = y
        self.s1 = s1
        self.s2 = s2

        self._border = self.screen.create_line(x + self.s1, y, x, y, x, y + self.s2, fill='gray25')


class RightTopBorder(Border):

    def __init__(self, master, x, y, s1, s2):
        Border.__init__(self, master)

        self.x = x
        self.y = y
        self.s1 = s1
        self.s2 = s2

        self._border = self.screen.create_line(x - self.s1, y, x, y, x, y - self.s2, fill='gray25')


class LightRightTopBorder(RightTopBorder):

    def __init__(self, master, x, y, s1, s2):
        RightTopBorder.__init__(self, master, x, y, s1, s2)

        self.screen.itemconfigure(self._border, fill='white', width=0.1)


class LightLeftTopBorder(LeftTopBorder):

    def __init__(self, master, x, y, s1, s2):
        LeftTopBorder.__init__(self, master, x, y, s1, s2)

        self.screen.itemconfigure(self._border, fill='white', width=0.1)


class LightRightBottomBorder(RightBottomBorder):

    def __init__(self, master, x, y, s1, s2):
        RightBottomBorder.__init__(self, master, x, y, s1, s2)

        self.screen.itemconfigure(self._border, fill='white', width=0.1)


class LightLeftBottomBorder(LeftBottomBorder):

    def __init__(self, master, x, y, s1, s2):
        LeftBottomBorder.__init__(self, master, x, y, s1, s2)

        self.screen.itemconfigure(self._border, fill='white', width=0.1)
