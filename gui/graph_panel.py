import tkinter as tk
from tkinter import ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import numpy as np

class GraphPanel (ttk.Frame):
	def __init__ (self, parent, logger):
		super().__init__(parent, borderwidth=5)

		self.logger = logger

		self.grid(column=1, row=0, sticky="nsew")
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)

		self.data = {
			"frequency"	: [],
			"amplitude"	: [],
			"phase"		: []
		}

		self.graph_both = DoubleGraph(self, 0, "Fréquence (Hz)", "Gain (dB)", "Phase (°)", self.logger)
		self.graph_gain = SimpleGraph(self, 0, "Fréquence (Hz)", "Gain (dB)", self.logger)
		self.graph_phase = SimpleGraph(self, 1, "Fréquence (Hz)", "Phase (°)", self.logger)

		self.update_all_graph()
	
	def update_all_graph (self):
		self._update_gain_graph_alone()
		self._update_phase_graph_alone()
		self._update_both_graph_alone()
	
	def _get_gain (self):
		return 20 * np.log10(self.data["amplitude"])
	
	def _update_gain_graph_alone (self):
		self.graph_gain.update(self.data["frequency"], self._get_gain())
	
	def _update_phase_graph_alone (self):
		self.graph_phase.update(self.data["frequency"], self.data["phase"])
	
	def _update_both_graph_alone (self):
		self.graph_both.update(self.data["frequency"], self._get_gain(), self.data["phase"])
	
	def show_gain_only (self):
		self.graph_gain.show()
		self.graph_phase.hide()
		self.graph_both.hide()
	
		self.rowconfigure(0, weight=1)
		self.rowconfigure(1, weight=0)
	
	def show_phase_only (self):
		self.graph_gain.hide()
		self.graph_phase.show()
		self.graph_both.hide()
	
		self.rowconfigure(0, weight=0)
		self.rowconfigure(1, weight=1)
	
	def show_both_separate_graph (self):
		self.graph_gain.show()
		self.graph_phase.show()
		self.graph_both.hide()
	
		self.rowconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		
	def show_both_same_graph (self):
		self.graph_gain.hide()
		self.graph_phase.hide()
		self.graph_both.show()
	
		self.rowconfigure(0, weight=1)
		self.rowconfigure(1, weight=0)
	
	def append_data_point (self, data):
		"""
		data : array or tuple.
		First element : frequency
		Second element : raw ampltiude
		Third element : phase
		"""
		self.data["frequency"].append(data[0])
		self.data["amplitude"].append(data[1])
		self.data["phase"].append(data[2])

class SimpleGraph (ttk.Frame):
	def __init__ (self, parent, row, x_axis_name, y_axis_name, logger):
		super().__init__(parent)
		self.grid(column=0, row=row, sticky="nsew")
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)

		self.logger = logger

		self.fig = Figure()
		self.ax = self.fig.add_subplot()
		self.fig.patch.set_facecolor("#D9D9D9")

		self.line, = self.ax.semilogx(1, 1)
		self.ax.set_xlabel(x_axis_name)
		self.ax.set_ylabel(y_axis_name)
		self.ax.grid(visible=True)
		self.fig.tight_layout()

		self.canva = FigureCanvasTkAgg(self.fig, self)
		self.canva.draw()

		self.canva.get_tk_widget().grid(column=0, row=0, sticky="nsew")
	
	def set_x_axis_range (self, minimum, maximum):
		self.ax.set_xlim(minimum, maximum)
	
	def _update_axis_range (self):
		self.ax.relim()
		self.ax.autoscale_view()

	def update (self, data_x, data_y):
		self.line.set_data(data_x, data_y)
		self._update_axis_range()
		self.canva.draw()
	
	def show (self):
		self.grid()

	def hide (self):
		self.grid_remove()

class DoubleGraph (ttk.Frame):
	def __init__ (self, parent, row, x_axis_name, y_axis_1_name, y_axis_2_name, logger):
		super().__init__(parent)
		self.grid(column=0, row=row, sticky="nsew")
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)

		self.logger = logger

		self.fig = Figure()
		self.ax_1 = self.fig.add_subplot()
		self.ax_2 = self.ax_1.twinx()

		self.ax_1.set_xlabel(x_axis_name)
		self.ax_1.set_ylabel(y_axis_1_name)
		self.ax_2.set_ylabel(y_axis_2_name)
		self.ax_1.grid(visible=True)

		self.line_1, = self.ax_1.semilogx(1, 1)
		self.line_2, = self.ax_2.semilogx(1, 1, linestyle="dotted")

		self.fig.patch.set_facecolor("#D9D9D9")
		self.fig.tight_layout()

		self.canva = FigureCanvasTkAgg(self.fig, self)
		self.canva.draw()

		self.canva.get_tk_widget().grid(column=0, row=0, sticky="nsew")

	def _update_axis_range (self):
		self.ax_1.relim()
		self.ax_1.autoscale_view()

		self.ax_2.relim()
		self.ax_2.autoscale_view()

	def update (self, data_x, data_y_1, data_y_2):
		self.line_1.set_data(data_x, data_y_1)
		self.line_2.set_data(data_x, data_y_2)

		self._update_axis_range()
		self.canva.draw()

	def show (self):
		self.grid()

	def hide (self):
		self.grid_remove()
