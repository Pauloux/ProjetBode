import logging

import tkinter as tk
import tkinter.scrolledtext
from tkinter import ttk

class DebugPanel (ttk.Frame):
	##### Creation of the debug panel #####
	def __init__ (self, parent, logger):
		super().__init__(parent, borderwidth=5)

		self.logger = logger

		self.scrolledtext = tk.scrolledtext.ScrolledText(self, height=10, bg="black", fg="white")
		self.scrolledtext.grid(column=0, row=0, sticky="nsew")

		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
	
		self._create_handler()
	
	def _create_handler (self):
		scrolledtext_handler = ScrolledTextHandler(self)
		scrolledtext_handler.setLevel(logging.INFO)
		scrolledtext_handler.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
		self.logger.addHandler(scrolledtext_handler)
	
	def append (self, message):
		self.scrolledtext.insert(tk.END, message)
	
class ScrolledTextHandler (logging.Handler):
	def __init__ (self, debug_panel):
		super().__init__()
		
		self.debug_panel = debug_panel

	def emit (self, record):
		message = self.format(record)
		self.debug_panel.append(f"{message}\n")

