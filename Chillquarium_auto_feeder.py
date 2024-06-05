import tkinter as tk
from tkinter import Listbox, END, Scrollbar, Button, StringVar
import win32gui
import win32api
import win32con
import threading
import time
import random

def enum_callback(hwnd, results):
    title = win32gui.GetWindowText(hwnd)
    if title:
        results.append((title, hwnd))
    return True

def get_windows():
    windows = []
    win32gui.EnumWindows(enum_callback, windows)
    return windows

def send_right_click():
    global running
    close_new_fish_box_tick = time.time()
    while running:
        selected_window = window_list.get(tk.ACTIVE)
        hwnd = [win for title, win in all_windows if title == selected_window][0]

        # Get the dimensions of the selected window
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top

        # Get the current cursor position
        cursor_x, cursor_y = win32api.GetCursorPos()

        # Get window focus state
        is_focused = win32gui.GetForegroundWindow() == hwnd

        # Check if the cursor is within the bounds of the window
        # if left <= cursor_x <= right and top <= cursor_y <= bottom and is_focused:
        if left <= cursor_x <= right and top <= cursor_y <= bottom:
            print(f"Cursor is on the window [{cursor_x},{cursor_y}], stop Right clicking.")
            time.sleep(2.0)
            continue


        # Calculate the center coordinates of the window
        x_center = left + width // 2
        y_center = top + height // 2

        current_time = time.time()
        if current_time - close_new_fish_box_tick >= 20:
            close_new_fish_box_tick = current_time
            monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromPoint((x_center, y_center)))
            x_center = x_center - 500
            # Calculate the screen coordinates corresponding to the center of the window
            x_screen = x_center - monitor_info['Monitor'][0]  # Adjust for the monitor's left position
            y_screen = y_center - monitor_info['Monitor'][1]  # Adjust for the monitor's top position

            lParam = y_screen << 16 | x_screen

            # Send the right-click event at the center of the window (without moving the cursor)
            win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_RBUTTON, lParam)
            time.sleep(0.1)  # Introduce a small delay between mouse clicks
            win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, None, lParam)

            continue

        # set x_center and y_center to random position in window rect

        # x_center = random.randint(left+50, right-50)
        # y_center = random.randint(top+50, bottom-50)

        
        x_center = random.randint(x_center-150, x_center+150)
        y_center = random.randint(y_center, y_center+300)

        # Get the monitor information for the selected window
        monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromPoint((x_center, y_center)))

        # Calculate the screen coordinates corresponding to the center of the window
        x_screen = x_center - monitor_info['Monitor'][0]  # Adjust for the monitor's left position
        y_screen = y_center - monitor_info['Monitor'][1]  # Adjust for the monitor's top position

        lParam = y_screen << 16 | x_screen

        # Send the right-click event at the center of the window (without moving the cursor)
        win32api.PostMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lParam)
        time.sleep(0.1)  # Introduce a small delay between mouse clicks
        win32api.PostMessage(hwnd, win32con.WM_RBUTTONUP, None, lParam)
        #time.sleep(0.5)

def send_right_click1():
    global running
    while running:
        selected_window = window_list.get(tk.ACTIVE)
        hwnd = [win for title, win in all_windows if title == selected_window][0]

        # Get the dimensions of the selected window
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top

        # Calculate the center coordinates of the window
        x_center = left + width // 2
        y_center = top + height // 2

        # Convert these coordinates to screen coordinates
        screen_x, screen_y = win32api.GetCursorPos()
        lParam = y_center << 16 | x_center

        print("send")

        # Send the right-click event at the center of the window (without moving the cursor)
        win32api.PostMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lParam)
        time.sleep(0.1)  # Introduce a small delay between mouse clicks
        win32api.PostMessage(hwnd, win32con.WM_RBUTTONUP, None, lParam)
        time.sleep(1)

def start():
    global running
    running = True
    threading.Thread(target=send_right_click).start()

def stop():
    global running
    running = False

def filter_windows(*args):
    search_term = search_var.get().lower()
    window_list.delete(0, END)
    for title, _ in all_windows:
        if search_term in title.lower():
            window_list.insert(END, title)

            if search_term == title.lower():
                # set added item to active
                window_list.see(END)
                window_list.activate(END)
                window_list.select_clear(0, END)
                window_list.select_set(END, END)

running = False
root = tk.Tk()
all_windows = get_windows()
window_list = Listbox(root, width=50, height=15)
scrollbar = Scrollbar(root)
search_var = StringVar()
search_entry = tk.Entry(root, textvariable=search_var)
search_var.set("Chillquarium")

search_var.trace("w", filter_windows)
window_list.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=window_list.yview)

for title, _ in all_windows:
    window_list.insert(END, title)
window_list.pack(side=tk.LEFT, fill=tk.BOTH)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
search_entry.pack()

start_button = Button(root, text="Start", command=start)
stop_button = Button(root, text="Stop", command=stop)

start_button.pack()
stop_button.pack()

filter_windows(None)

root.mainloop()