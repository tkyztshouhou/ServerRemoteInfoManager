import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def on_add_group():
    print("Add group clicked")

def on_add_host():
    print("Add host clicked")

def on_edit_host():
    print("Edit host clicked")

def on_delete_host():
    print("Delete host clicked")

def on_connect():
    print("Connect to host clicked")

root = tk.Tk()
root.title("Remote Desktop Manager")

# Menu Bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New Group")
file_menu.add_command(label="New Host")
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# Tool Bar
tool_bar_frame = tk.Frame(root)
tool_bar_frame.pack(side=tk.TOP, fill=tk.X)

add_group_button = tk.Button(tool_bar_frame, text="Add Group", command=on_add_group)
add_group_button.pack(side=tk.LEFT)

add_host_button = tk.Button(tool_bar_frame, text="Add Host", command=on_add_host)
add_host_button.pack(side=tk.LEFT)

edit_host_button = tk.Button(tool_bar_frame, text="Edit Host", command=on_edit_host)
edit_host_button.pack(side=tk.LEFT)

delete_host_button = tk.Button(tool_bar_frame, text="Delete Host", command=on_delete_host)
delete_host_button.pack(side=tk.LEFT)

connect_button = tk.Button(tool_bar_frame, text="Connect", command=on_connect)
connect_button.pack(side=tk.RIGHT)

# Host List
host_list_frame = tk.Frame(root)
host_list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

host_list_tree = ttk.Treeview(host_list_frame)
host_list_tree["columns"] = ("name", "type", "status")

host_list_tree.column("#0", width=50, minwidth=50, anchor=tk.CENTER)
host_list_tree.column("name", width=200, minwidth=200, anchor=tk.W)
host_list_tree.column("type", width=150, minwidth=150, anchor=tk.W)
host_list_tree.column("status", width=100, minwidth=100, anchor=tk.W)

host_list_tree.heading("#0", text="ID")
host_list_tree.heading("name", text="Name")
host_list_tree.heading("type", text="Type")
host_list_tree.heading("status", text="Status")

host_list_tree.pack(fill=tk.BOTH, expand=True)

# Main loop
root.mainloop()