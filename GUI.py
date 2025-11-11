#####
# À faire :
# Menu à gauche
#####

import logging

import tkinter as tk
from tkinter import ttk

def setup_logging ():
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.DEBUG)
	
	stream_handler = logging.StreamHandler()
	stream_handler.setFormatter(logging.Formatter("App:%(levelname)s:%(message)s"))
	#stream_handler.setLevel(logging.INFO)
	stream_handler.setLevel(logging.DEBUG)

	log_file_handler = logging.FileHandler("App.log")
	log_file_handler.setLevel(logging.DEBUG)
	log_file_handler.setFormatter(logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s"))

	logger.addHandler(log_file_handler)
	logger.addHandler(stream_handler)

	logger.info("App opened")

	return logger

class App (tk.Tk):
	def __init__ (self, logger):
		super().__init__()

		self.logger = logger

		##### Variables #####
		self.show_gain = tk.BooleanVar(value=True)
		self.show_phase = tk.BooleanVar(value=True)
		self.prev_show_gain = tk.BooleanVar(value=True)
		self.prev_show_phase = tk.BooleanVar(value=True)

		self.number_of_graph = tk.IntVar(value=2)
		self.show_one_graph = tk.BooleanVar(value=(self.number_of_graph.get() == 1))
		self.show_two_graph = tk.BooleanVar(value=(self.number_of_graph.get() == 2))

		self.show_debug = tk.BooleanVar(value=False)

		self._create_window()
		self._create_menubar()
	
	def _create_window (self):
		self.title("Projet Bode - V1.0")
		self.geometry("1200x800")
		self.minsize(300, 150)
		

	def _create_save_menubar (self, menubar):
		self.save_menu = tk.Menu(menubar, tearoff=0)
		
		self.menubar.add_cascade(menu=self.save_menu, label="Enregistrer")

		self.save_menu.add_command(label="Enregistrer au format csv", command=lambda *args: self.logger.debug("Save to csv"))
		self.save_menu.add_command(label="Enregistrer au format png", command=lambda *args: self.logger.debug("Save to png"))
		self.save_menu.add_command(label="Enregistrer au format jpg", command=lambda *args: self.logger.debug("Save to jpg"))
	
	def _create_display_menubar (self, menubar):
		self.display_menu = tk.Menu(menubar, tearoff=0)

		self.menubar.add_cascade(menu=self.display_menu, label="Affichage")

		self.display_menu.add_checkbutton(label="Gain", variable=self.show_gain, command=self._on_gain_phase_change)
		self.display_menu.add_checkbutton(label="Phase", variable=self.show_phase, command=self._on_gain_phase_change)
		self.display_menu.add_checkbutton(label="1 graphique", variable=self.show_one_graph, command=self._on_graph_selection)
		self.display_menu.add_checkbutton(label="2 graphiques", variable=self.show_two_graph, command=self._on_graph_selection)
		self.display_menu.add_checkbutton(label="Debug", variable=self.show_debug)

		self.show_gain.trace_add("write", lambda *args: self.logger.debug(f"show_gain set to {self.show_gain.get()}"))
		self.show_phase.trace_add("write", lambda *args: self.logger.debug(f"show_phase set to {self.show_phase.get()}"))
		self.number_of_graph.trace_add("write", lambda *args: self.logger.debug(f"number_of_graph set to {self.number_of_graph.get()}"))
		self.show_debug.trace_add("write", lambda *args: self.logger.debug(f"show_debug set to {self.show_debug.get()}"))

	def _create_menubar (self):
		self.menubar = tk.Menu(self)

		self._create_save_menubar(self.menubar)
		self._create_display_menubar(self.menubar)

		self.config(menu=self.menubar)
	
	def _update_state_number_of_graph (self):
		if (self.show_gain.get() == True and self.show_phase.get() == True):
			self.display_menu.entryconfigure("1 graphique", state=tk.NORMAL)
			self.display_menu.entryconfigure("2 graphiques", state=tk.NORMAL)
		else:
			self.display_menu.entryconfigure("1 graphique", state=tk.DISABLED)
			self.display_menu.entryconfigure("2 graphiques", state=tk.DISABLED)

	def _on_gain_phase_change (self, *args):
		"""
		Allows to select gain and/or phase to display, but prevents both of them being off.
		If the user unselect both, the previously off selection is switched on automatically.
		"""
		if (self.show_gain.get() == False and self.show_phase.get() == False):
			self.logger.debug("show_gain and show_phase both set to False")
			self.show_gain.set(not self.prev_show_gain.get())	
			self.show_phase.set(not self.prev_show_phase.get())
		
		self.prev_show_gain.set(self.show_gain.get())
		self.prev_show_phase.set(self.show_phase.get())

		self._update_state_number_of_graph()

	def _on_graph_selection (self, *args):
		"""
		Allows to select 1 or 2 graph to display, but never both or none of them.
		If we click on the button already selected, nothing changes.
		If we click on the other button, the selection is switched.
		"""
		if (self.show_one_graph.get() == True and self.show_two_graph.get() == True):
			if (self.number_of_graph.get() == 1):
				self.number_of_graph.set(2)
			else:
				self.number_of_graph.set(1)

		self.show_one_graph.set(self.number_of_graph.get() == 1)
		self.show_two_graph.set(self.number_of_graph.get() == 2)

if __name__ == "__main__":
	logger = setup_logging()

	app = App(logger)
	app.mainloop()
