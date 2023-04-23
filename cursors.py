import tkinter as tk
from tkinter import ttk

root = tk.Tk()

# config the root window
root.geometry('600x400')
root.resizable(False, False)
root.title('Tkinter Cursors')

frame = ttk.Frame(root)

# label
label = ttk.Label(frame, text="Cursor:")
label.pack(fill=tk.X, padx=5, pady=5)

# cursor list
selected_cursor = tk.StringVar()
cursor_list = ttk.Combobox(frame, textvariable=selected_cursor, cursor='arrow')
cursors = ["size_ne_sw", "size_ns", "size_nw_se", "size_we"]
cursor_list['values'] = cursors
cursor_list['state'] = 'readonly'

cursor_list.pack(fill=tk.X, padx=5, pady=5)

frame.pack(expand=True, fill=tk.BOTH)


# bind the selected value changes
def cursor_changed(event):
    frame.config(cursor=selected_cursor.get())


cursor_list.bind('<<ComboboxSelected>>', cursor_changed)

root.mainloop()
