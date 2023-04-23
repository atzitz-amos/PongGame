class AnimState:
    BW = -1
    DISABLED = 0
    FW = 1

    def __init__(self):
        self.direction = AnimState.DISABLED

        self.progress = 0

    def fw(self):
        self.direction = AnimState.FW

    def bw(self):
        self.direction = AnimState.BW

    def disable(self):
        self.direction = AnimState.DISABLED

    @property
    def enabled(self):
        return self.direction != AnimState.DISABLED

    def incr(self, amount):
        self.progress += amount
        if self.progress >= 100 or self.progress <= 0:
            self.disable()
            return True
        return False

    def reset(self):
        self.progress = 0

    def set(self, value):
        self.progress = value
        if self.progress >= 100 or self.progress <= 0:
            self.disable()
            return True
        return False


class FanButtonOpeningAnim:
    speed = 2
    time = 1000  # ms

    def __init__(self, taskbar):
        self.taskbar = taskbar
        self.state = AnimState()

        self.num = None

        self.arcs = []

    def fw(self):
        self.state.fw()

    def bw(self):
        self.state.bw()

    def tick(self):
        if self.state.enabled:
            self._anim()

    def _anim(self):
        total = self.taskbar.inner_angle * self.taskbar.getButtonsNum()
        current = total * self.state.progress / 100
        speed = total / self.time * 10
        ratio = (current + speed) / total * 100
        print(current, speed, total)
        match self.state.direction:
            case self.state.FW:
                self.state.set(ratio)
                pass
            case self.state.BW:
                pass
                # self.state.incr()
        self.update()

    def reset(self):
        self.num = self.taskbar.getButtonNum()
        self.state.reset()
        self.update()

    def update(self):
        pr = self.state.progress / 100
        num = 2  # self.taskbar.getButtonsNum()
        if num == 0:
            return
        if self.num and num != self.num:
            print("Warning, amount of buttons has changed during animation, resetting.")
            return self.reset()
        self.num = num

        angle = self.taskbar.inner_angle

        start = 90 - angle * num / 2
        if not len(self.arcs):
            self.init_arcs(start, num)

        bearing = 1 / len(self.arcs)
        new_ang = start + angle * num * pr

        for i, arc in enumerate(self.arcs):
            cstart, cextent = float(self.taskbar.canvas.itemcget(arc, "start")), float(
                self.taskbar.canvas.itemcget(arc, "extent"))
            if i * bearing < pr and cextent < self.taskbar.inner_angle:
                cextent = cextent + bearing * pr
            if i * bearing < pr:
                self.taskbar.canvas.itemconfigure(arc, start=new_ang - cextent, extent=cextent)

    def init_arcs(self, start, num):
        for _ in range(num):
            self.arcs.append(self.taskbar.canvas.create_arc(*self.taskbar.bbox, start=start, extent=0))
