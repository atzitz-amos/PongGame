import tkinter

TK = tkinter.Tk()
TK.wm_attributes("-alpha", 0.0)

tk = tkinter.Toplevel()

tk.wm_attributes("-alpha", 1.0)
tk.wm_attributes("-transparentcolor", "red")
tk.wm_geometry("300x300+300+300")

tk["bg"] = "red"

canv = tkinter.Canvas(tk, bg="red", highlightthickness=0)
canv.pack(expand=True)
canv.update()
width, height = canv.winfo_width(), canv.winfo_height()
s = 100
win = canv.create_oval(width / 2 - s, height / 2 - s, width / 2 + s, height / 2 + s, fill="white")
taskbar = canv.create_rectangle(0, 0, width + 10, 23, fill="white")

grabbing = False
grab_origin = ()


def current_pos():
    geo = tk.wm_geometry()
    i = geo.find("+")
    rx, ry = geo[i + 1:].split("+")
    return int(rx), int(ry)


def current_geo():
    geo = tk.wm_geometry()
    i = geo.find("+")
    rx, ry = geo[:i].split("x")
    return int(rx), int(ry)


def set_grabbing(e, g):
    global grabbing, grab_origin
    grabbing = g
    grab_origin = e.x, e.y


def mouse(event):
    rx, ry = event.x, event.y
    w, h = current_geo()
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
    print(cursor)
    canv["cursor"] = cursor
    if grabbing:
        x, y = event.x, event.y
        translation = x - grab_origin[0], y - grab_origin[1]
        rx, ry = current_pos()
        tk.wm_geometry(f"+{rx + translation[0]}+{ry + translation[1]}")


canv.bind("<Button-1>", lambda e: set_grabbing(e, True))
canv.bind("<ButtonRelease-1>", lambda e: set_grabbing(e, False))
canv.bind("<Motion>", mouse)

tk.deiconify()
tk.lift()
tk.focus_force()
tk.wm_overrideredirect(True)

TK.mainloop()
