import tkinter as tk
from tkinter import ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import numpy as np

class GraphPanel (ttk.Frame):
	##### Creation of the graph panel #####
	def __init__ (self, parent, logger):
		super().__init__(parent, borderwidth=5)

		self.logger = logger

		self.grid(column=1, row=0, sticky="nsew")
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)

		self.data = {
			"frequency"	: [],
			"amplitude_in"	: [],
			"amplitude_out"	: [],
			"phase"		: []
		}

		self.graph_both = DoubleGraph(self, 0, "Fréquence (Hz)", "Gain (dB)", "Phase (°)", self.logger)
		self.graph_gain = SimpleGraph(self, 0, "Fréquence (Hz)", "Gain (dB)", self.logger)
		self.graph_phase = SimpleGraph(self, 1, "Fréquence (Hz)", "Phase (°)", self.logger)

		self.update_all_graph()
	
	### Public method ###
	# Graph update
	def update_all_graph (self):
		self._update_gain_graph_alone()
		self._update_phase_graph_alone()
		self._update_both_graph_alone()
	
	def _update_gain_graph_alone (self):
		self.graph_gain.update(self.data["frequency"], self._get_gain())
	
	def _update_phase_graph_alone (self):
		self.graph_phase.update(self.data["frequency"], self.data["phase"])
	
	def _update_both_graph_alone (self):
		self.graph_both.update(self.data["frequency"], self._get_gain(), self.data["phase"])
	
	def _get_gain (self):
		return 20 * np.log10(np.divide(self.data["amplitude_out"], self.data["amplitude_in"]))

	# Hide and show graphs
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
	
	# Save to csv
	def save_csv (self, filename):
		with open(filename, 'w') as file:
			file.write("frequency,amplitude_in,amplitude_out,gaindB,phase\n")

			frequency = self.data["frequency"]
			amplitude_in = self.data["amplitude_in"]
			amplitude_out = self.data["amplitude_out"]
			gain = self._get_gain()
			phase = self.data["phase"]
			for i in range (len(frequency)):
				file.write(f"{frequency[i]},{amplitude_in[i]},{amplitude_out[i]},{gain[i]},{phase[i]}\n")

	# Save graphs
	def save_gain (self, filename):
		self.graph_gain.save(filename)
	
	def save_phase (self, filename):
		self.graph_phase.save(filename)
	
	def save_both_on_same (self, filename):
		self.graph_both.save(filename)

	# Others
	def append_data_point (self, frequency, amplitude_in, amplitude_out, phase):
		self.data["frequency"].append(frequency)
		self.data["amplitude_in"].append(amplitude_in)
		self.data["amplitude_out"].append(amplitude_out)
		self.data["phase"].append(phase)
	
	def clear (self):
		self.data = {
			"frequency"	: [],
			"amplitude_in"	: [],
			"amplitude_out"	: [],
			"phase"		: []
		}
		
		self.update_all_graph()
	
class SimpleGraph (ttk.Frame):
	##### Creation of a graph with one data
	def __init__ (self, parent, row, x_axis_name, y_axis_name, logger):
		super().__init__(parent)
		self.grid(column=0, row=row, sticky="nsew")
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)

		self.logger = logger

		self.fig = Figure()
		self.ax = self.fig.add_subplot()
		self.fig.patch.set_facecolor("#D9D9D9")

		self.line, = self.ax.semilogx(1, 0)
		self.ax.set_xlabel(x_axis_name)
		self.ax.set_ylabel(y_axis_name)
		self.ax.grid(visible=True)
		self.fig.tight_layout()

		self.canva = FigureCanvasTkAgg(self.fig, self)
		self.canva.draw()

		self.canva.get_tk_widget().grid(column=0, row=0, sticky="nsew")

		toolbar = NavigationToolbar2Tk(self.canva, self, pack_toolbar=False)
		toolbar.grid(column=0, row=1, sticky="e")
	
	##### Methods #####
	def update (self, data_x, data_y):
		self.line.set_data(data_x, data_y)
		self._update_axis_range()
		self.canva.draw()
	
	def _update_axis_range (self):
		self.ax.relim()
		self.ax.autoscale_view()
	
	def show (self):
		self.grid()

	def hide (self):
		self.grid_remove()

	def set_x_axis_range (self, minimum, maximum):
		self.ax.set_xlim(minimum, maximum)
	
	def save (self, filename):
		self.fig.savefig(filename)
	
class DoubleGraph (ttk.Frame):
	##### Creation of a graph with two data (and y unit)
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

		self.line_1, = self.ax_1.semilogx(1, 0)
		self.line_2, = self.ax_2.semilogx(1, 0, linestyle="dotted")

		self.fig.patch.set_facecolor("#D9D9D9")
		self.fig.tight_layout()

		self.canva = FigureCanvasTkAgg(self.fig, self)
		self.canva.draw()

		self.canva.get_tk_widget().grid(column=0, row=0, sticky="nsew")

		toolbar = NavigationToolbar2Tk(self.canva, self, pack_toolbar=False)
		toolbar.grid(column=0, row=1, sticky="e")

	##### Methods #####
	def update (self, data_x, data_y_1, data_y_2):
		self.line_1.set_data(data_x, data_y_1)
		self.line_2.set_data(data_x, data_y_2)

		self._update_axis_range()
		self.canva.draw()

	def _update_axis_range (self):
		self.ax_1.relim()
		self.ax_1.autoscale_view()

		self.ax_2.relim()
		self.ax_2.autoscale_view()

	def show (self):
		self.grid()

	def hide (self):
		self.grid_remove()

	def set_x_axis_range (self, minimum, maximum):
		self.ax_1.set_xlim(minimum, maximum)
		self.ax_2.set_xlim(minimum, maximum)
	
	def save (self, filename):
		self.fig.savefig(filename)
