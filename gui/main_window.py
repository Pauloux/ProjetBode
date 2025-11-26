import tkinter as tk
from tkinter import ttk
import pyvisa

from gui.graph_panel import GraphPanel
from gui.left_panel import LeftPanel
from gui.menu_bar import MenuBar
from instruments.visa_manager import VISAManager

class MainWindow(tk.Tk):
	def __init__ (self, logger):
		super().__init__()

		self.logger = logger
		self.icon = {
			"refresh" : tk.PhotoImage(file=r"icons/Refresh_icon.png"),
			"OK" : tk.PhotoImage(file=r"icons/OK_icon.png"),
			"error" : tk.PhotoImage(file=r"icons/Error_icon.png")
		}
		self.visa_manager = VISAManager(self.logger)
		
		self._create_window()

		self._init_shortcut()
		self._create_menubar()
		self._create_main_interface()

		self.menu_bar.trigger_callback_graph_display()
		self.left_panel.generator_frame.trigger_callback_get_port_list()

	def _create_main_interface (self):
		self._create_main_paned()

		self.left_panel = LeftPanel(self, self.icon, self.logger)
		self.graph_panel = GraphPanel(self, self.logger)

		self._finish_init_main_paned()
	
		self._init_generator_and_oscilloscope_callback()

	def _init_generator_and_oscilloscope_callback (self):
		self.left_panel.generator_frame.set_callback_get_port_list(self._on_callback_get_port_list)
		self.left_panel.oscilloscope_frame.set_callback_get_port_list(self._on_callback_get_port_list)

		self.left_panel.generator_frame.set_callback_update_instrument(self._on_callback_update_generator)
		self.left_panel.oscilloscope_frame.set_callback_update_instrument(self._on_callback_update_oscilloscope)
	
	def _update_generator_and_oscilloscope_port_list (self):
		ports = self.visa_manager.get_relevant_ports()

		self.left_panel.generator_frame.set_port_list_selector_values(ports)
		self.left_panel.oscilloscope_frame.set_port_list_selector_values(ports)
	
	def _on_callback_get_port_list (self):
		self.logger.debug("Updating the available port list")
		self._update_generator_and_oscilloscope_port_list()

	def _on_callback_update_generator (self, model, port):
		self.logger.debug("Updating the generator status")

		self.visa_manager.set_generator(model, port)

		if (self.visa_manager.generator_is_responding() == True):
			self.left_panel.generator_frame.set_status_icon(True)
		else:
			self.left_panel.generator_frame.set_status_icon(False)

	def _on_callback_update_oscilloscope (self, model, port):
		self.logger.debug("Updating the oscilloscope status")

		self.visa_manager.set_oscilloscope(model, port)

		if (self.visa_manager.oscilloscope_is_responding() == True):
			self.left_panel.oscilloscope_frame.set_status_icon(True)
		else:
			self.left_panel.oscilloscope_frame.set_status_icon(False)

	def _create_main_paned (self):
		self.main_paned = tk.PanedWindow(self, orient="horizontal")
		self.main_paned.grid(sticky="nsew")

	def _finish_init_main_paned (self):
		self.main_paned.add(self.left_panel, minsize=200)
		self.main_paned.add(self.graph_panel)
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

		self.menu_bar.set_callback_graph_display(self._on_callback_graph_display)
	
	def _on_callback_graph_display (self, show_gain, show_phase, show_on_same_graph):
		if ((show_gain == True) and (show_phase == True) and (show_on_same_graph == True)):
			self.logger.debug("Activate display both gain and phase on the same graph")
			self.graph_panel.show_both_same_graph()
		elif ((show_gain == True) and (show_phase == True) and (show_on_same_graph == False)):
			self.logger.debug("Activate display both gain and phase on separate graphs")
			self.graph_panel.show_both_separate_graph()
		elif ((show_gain == True) and (show_phase == False)):
			self.logger.debug("Activate display only gain")
			self.graph_panel.show_gain_only()
		elif ((show_gain == False) and (show_phase == True)):
			self.logger.debug("Activate display only phase")
			self.graph_panel.show_phase_only()
		else:
			self.logger.warning("Unknown combination of graph selection")
