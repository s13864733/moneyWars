from tkinter import ttk

class App():
    def __init__(self, root):
        self.root = root
        self.root.title("Statistica")
        
        # UI
        main_frm = ttk.Frame(root, padding=10).grid()
        self.load_file_label = ttk.Label(main_frm, text="Load EXCEL file here").grid(column=0, row=0)