import tkinter as tk
from tkinter import ttk

from gui.left_panel import LeftPanel
from gui.menu_bar import MenuBar
class MainWindow(tk.Tk):
	def __init__ (self, logger):
		super().__init__()
		self.logger = logger

		self._create_window()

		self.icon = {
			"refresh" : tk.PhotoImage(file=r"icons/Refresh_icon.png"),
			"OK" : tk.PhotoImage(file=r"icons/OK_icon.png"),
			"error" : tk.PhotoImage(file=r"icons/Error_icon.png")

		}

		self._init_shortcut()
		self._create_menubar()
		self._create_main_interface()
	
	def _create_main_interface (self):
		self._create_main_paned()

		self.left_panel = LeftPanel(self, self.icon, self.logger)

		self._finish_init_main_paned()

	def _create_main_paned (self):
		self.main_paned = tk.PanedWindow(self, orient="horizontal")
		self.main_paned.grid(sticky="nsew")

	def _finish_init_main_paned (self):
		self.tmp_panel = ttk.Frame(self.main_paned)
		self.tmp_panel.grid(column=1, row = 0)
		ttk.Label(self.tmp_panel, text="Graphiques").grid()
		self.main_paned.add(self.left_panel, minsize=200)
		self.main_paned.add(self.tmp_panel)
		self.update_idletasks()
		self.main_paned.sash_place(0, 300, 0)

	def _init_shortcut (self):
		self.bind("<Control-w>", lambda *args: self.destroy())

	def _create_window (self):
		self.title("Projet Bode - V1.0")
		self.geometry("1200x800")
		self.minsize(300, 150)

		# Allow resizing
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)

	def _create_menubar (self):
		self.menu_bar = MenuBar(self, self.logger)
		self.config(menu=self.menu_bar)
