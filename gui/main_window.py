import tkinter as tk
from tkinter import ttk
import pyvisa

from gui.graph_panel import GraphPanel
from gui.left_panel import LeftPanel
from gui.menu_bar import MenuBar

OSCILLOSCOPE_SECURITY_FACTOR = 7
OSCILLOSCOPE_PROCESSING_TIME_S = 0
OSCILLOSCOPE_STABILISATION_TIME_S = 0.2
OSCILLOSCOPE_MINIMUM_WAITING_TIME_S = 1

CHANNEL_IN = 1
CHANNEL_OUT = 2
MIN_SIGNAL_PERIOD = 3
NUMBER_OF_HORIZONTAL_DIV = 12

from instruments.visa_manager import VISAManager
from instruments.Argilent_33120A import Argilent_33120A
from instruments.RIGOL_DG1022 import RIGOL_DG1022
from instruments.RIGOL_DS1074Z import RIGOL_DS1074Z

supported_instruments = {
	"generator" : {
		"Argilent 33120A" : Argilent_33120A,
		"RIGOL DG1022" : RIGOL_DG1022
	},
	"oscilloscope" : {
		"RIGOL DS1074Z" : RIGOL_DS1074Z
	}
}

##### #####
# To use mock, uncomment the following lines (import and supported_instruments)
##### #####

#from instruments.mock.visa_manager import VISAManager
#from instruments.mock.instrument import InstrumentMock
#
#supported_instruments = {
#	"generator" : {
#		"Argilent 33120A" : InstrumentMock,
#		"RIGOL DG1022" : InstrumentMock
#	},
#	"oscilloscope" : {
#		"RIGOL DS1074Z" : InstrumentMock
#	}
#}

class MainWindow(tk.Tk):
	##### Creation of the window #####
	def __init__ (self, logger):
		super().__init__()

		self.logger = logger

		self.icon = {
			"refresh" : tk.PhotoImage(file=r"icons/Refresh.png"),
			"OK" : tk.PhotoImage(file=r"icons/OK.png"),
			"error" : tk.PhotoImage(file=r"icons/Error.png")
		}

		self.after_identifier = None

		self.visa_manager = VISAManager(supported_instruments, self.logger)
		
		self._create_window()

		self._init_shortcut()
		self._create_menubar()
		self._create_main_interface()

		self.menu_bar.trigger_callback_graph_display()
	
	##### Graphical interface #####
	def _create_main_interface (self):
		self._create_main_paned()

		self.left_panel = LeftPanel(self, supported_instruments, self.icon, self.logger)
		self.graph_panel = GraphPanel(self, self.logger)

		self._finish_init_main_paned()
	
		self._init_instruments_callback()

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
		self.menu_bar.set_callback_save(self._on_callback_save)

	##### Instruments #####
	def _update_instruments_status (self):
		self.logger.debug("Updating instrument status")
	
		generator_status = self.visa_manager.generator_is_responding()
		oscilloscope_status = self.visa_manager.oscilloscope_is_responding()

		self.left_panel.generator_frame.set_status_icon(generator_status)
		self.left_panel.oscilloscope_frame.set_status_icon(oscilloscope_status)
		
		return {
			"generator_status" : generator_status,
			"oscilloscope_status" : oscilloscope_status
		}

	##### Callback #####
	### Instruments ###
	def _init_instruments_callback (self):
		self.left_panel.generator_frame.set_callback_get_port_list(self._on_callback_get_port_list)
		self.left_panel.oscilloscope_frame.set_callback_get_port_list(self._on_callback_get_port_list)
	
		self.left_panel.set_callback_update_instruments(self._on_callback_update_instruments_status)
		
		self.left_panel.generator_frame.set_callback_set_instrument(self._on_callback_set_instrument)
		self.left_panel.oscilloscope_frame.set_callback_set_instrument(self._on_callback_set_instrument)

		self.left_panel.set_callback_start_acquisition(self._on_callback_start_acquisition)
		self.left_panel.set_callback_stop_acquisition(self._on_callback_stop_acquisition)
	
	def _on_callback_get_port_list (self):
		self.logger.debug("Updating the available port list")
		self._update_generator_and_oscilloscope_port_list()
		
	def _on_callback_update_instruments_status (self):
		self._update_instruments_status()

	def _on_callback_set_instrument (self, model, port):
		self.visa_manager.set_instrument(model, port)

	def _update_generator_and_oscilloscope_port_list (self):
		ports = self.visa_manager.get_relevant_ports()

		self.left_panel.generator_frame.set_port_list_selector_values(ports)
		self.left_panel.oscilloscope_frame.set_port_list_selector_values(ports)
	
	def _on_callback_start_acquisition (self, acquisition_parameters):
		status_dict = self._update_instruments_status()
		if ((not status_dict["generator_status"] == True) or (not status_dict["oscilloscope_status"] == True)):
			self.left_panel.set_start_stop_button_status(False)
			tk.messagebox.showerror(message="Au moins un instrument n'est pas connecté ou ne répond pas")
			return

		self.graph_panel.clear()

		self._init_acquisition(acquisition_parameters)
		# Wait to give some time to the instrument to be initialized
		self.after_identifier = self.after(2000, self._acquire, acquisition_parameters)
	
	def _on_callback_stop_acquisition (self):
		self.after_cancel(self.after_identifier)

	### Graph ###
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

	def _on_callback_save (self, extension):
		filename = tk.filedialog.asksaveasfilename(parent=self, title=f"Save to {extension}", defaultextension=f".{extension}")

		if extension == "csv":
			self.graph_panel.save_csv(filename)
			return

		# Decide which graph to save
		show_gain = self.menu_bar.is_show_gain_selected()
		show_phase = self.menu_bar.is_show_phase_selected()
		show_on_same_graph = self.menu_bar.is_show_1_graph_selected()
		if ((show_gain == True) and (show_phase == True) and (show_on_same_graph == True)):
			self.graph_panel.save_both_on_same(filename)
			self.logger.debug(f"Saved {filename} (both on the same graph)")
		elif ((show_gain == True) and (show_phase == True) and (show_on_same_graph == False)):
			filename_gain, filename_phase = self._get_file_gain_and_phase_suffix(filename)
			self.graph_panel.save_gain(filename_gain)
			self.graph_panel.save_phase(filename_phase)
		elif ((show_gain == True) and (show_phase == False)):
			self.graph_panel.save_gain(filename)
			self.logger.debug(f"Saved {filename} (gain)")
		elif ((show_gain == False) and (show_phase == True)):
			self.graph_panel.save_phase(filename)
			self.logger.debug(f"Saved {filename} (phase)")
		else:
			self.logger.warning("Unknown combination of graph selection")

	def _get_file_gain_and_phase_suffix (self, filename):
		filename_name = filename[0:-4]
		filename_extension = filename[-4:]
		
		filename_gain = filename_name + "-gain" + filename_extension
		filename_phase = filename_name + "-phase" + filename_extension

		return (filename_gain, filename_phase)

	##### Data acquisition #####
	def _init_acquisition (self, acquisition_parameters):
		# REMOVE BEFORE FLIGHT
		print(acquisition_parameters)
		self._init_acquisition_generator(acquisition_parameters)
		self._init_acquisition_oscilloscope(acquisition_parameters)

	def _init_acquisition_generator (self, acquisition_parameters):
		self.visa_manager.set_generator_unit("VPP")
		self.visa_manager.set_generator_signal_shape(acquisition_parameters["signal_shape"])

		self.visa_manager.set_generator_amplitude_pp(acquisition_parameters["amplitude"])
		self.visa_manager.set_generator_offset(acquisition_parameters["bias"])

	def _init_acquisition_oscilloscope (self, acquisition_parameters):
		# Show both channel
		self.visa_manager.oscilloscope_display_channel(CHANNEL_IN)
		self.visa_manager.oscilloscope_display_channel(CHANNEL_OUT)
		# Set time mode in YT
		self.visa_manager.set_oscilloscope_timebase_mode("yt")
		# Set unit to volts
		self.visa_manager.set_oscilloscope_channel_unit(CHANNEL_IN, "V")
		self.visa_manager.set_oscilloscope_channel_unit(CHANNEL_OUT, "V")
		# Set probe ratio to 1
		self.visa_manager.set_oscilloscope_channel_probe_ratio(CHANNEL_IN, 1)
		self.visa_manager.set_oscilloscope_channel_probe_ratio(CHANNEL_OUT, 1)
		# Set number of average
		self.visa_manager.set_average(acquisition_parameters["mean_samples"])
		# Set offset
		self.visa_manager.set_oscilloscope_channel_offset(CHANNEL_IN, acquisition_parameters["bias"])
		self.visa_manager.set_oscilloscope_channel_offset(CHANNEL_OUT, acquisition_parameters["bias"])
		# Set both channel range to 1 V
		self.visa_manager.set_oscilloscope_channel_range(CHANNEL_IN, acquisition_parameters["amplitude"] / 0.8)
		self.visa_manager.set_oscilloscope_channel_range(CHANNEL_OUT, acquisition_parameters["amplitude"] / 0.8)

	def _acquire_set_frequency (self, frequency_list, frequency_index, mean_samples):
		print(f"set frequency to {frequency_list[frequency_index]}")
		self.visa_manager.set_generator_frequency(frequency_list[frequency_index])
		self._acquire_set_timebase(frequency_list, frequency_index, mean_samples)

	def _acquire_set_timebase (self, frequency_list, frequency_index, mean_samples):
		div_size = self._get_correct_timebase(frequency_list[frequency_index])
		self.visa_manager.set_oscilloscope_timebase_scale(div_size)

		time_to_wait_ms = self._get_waiting_time(div_size, mean_samples)

		self.logger.debug(f"Waiting {time_to_wait_ms} ms ({frequency_list[frequency_index]} Hz)...")

		self.after_identifier = self.after(time_to_wait_ms, self._acquire_measure, frequency_list, frequency_index, mean_samples, time_to_wait_ms)
	
	def _acquire_measure (self, frequency_list, frequency_index, mean_samples, time_to_wait_ms):
		# Get vertical range
		try:
			vertical_range = self.visa_manager.get_oscilloscope_channel_range(CHANNEL_OUT)
		except Exception as e:
			self._acquire_measure(frequency_list, frequency_index, mean_samples, time_to_wait_ms)
			return

		# Measure output signal amplitude
		try:
			amplitude_out = self.visa_manager.measure_amplitude_pp(CHANNEL_OUT)
		except Exception as e:
			self._acquire_measure(frequency_list, frequency_index, mean_samples, time_to_wait_ms)
			return

		self.logger.debug(f"vertical_range: {vertical_range}\t output amplitude measured: {amplitude_out}")

		if amplitude_out > 0.9 * vertical_range:
			self.visa_manager.set_oscilloscope_channel_range(CHANNEL_OUT, vertical_range * 2)
			# Redo the measure
			self.after_identifier = self.after(time_to_wait_ms, self._acquire_measure, frequency_list, frequency_index, mean_samples, time_to_wait_ms)
			return
		elif amplitude_out < 0.5 * vertical_range:
			self.visa_manager.set_oscilloscope_channel_range(CHANNEL_OUT, amplitude_out / 0.8)
			# Redo the measure
			self.after_identifier = self.after(time_to_wait_ms, self._acquire_measure, frequency_list, frequency_index, mean_samples, time_to_wait_ms)
			return
		else:
			# Do nothing, the measure is good
			pass

		# Measure input signal amplitude
		try:
			amplitude_in = self.visa_manager.measure_amplitude_pp(CHANNEL_IN)
		except Exception as e:
			self._acquire_measure(frequency_list, frequency_index, mean_samples, time_to_wait_ms)
			return

		self.logger.debug(f"input amplitude measured: {amplitude_in}")

		# Measure phase
		try:
			phase = self.visa_manager.measure_phase(CHANNEL_IN, CHANNEL_OUT)
		except Exception as e:
			self._acquire_measure(frequency_list, frequency_index, mean_samples, time_to_wait_ms)
			return

		self.logger.debug(f"phase measured: {phase}")

		self.graph_panel.append_data_point(frequency_list[frequency_index], amplitude_in, amplitude_out, phase)
		self.graph_panel.update_all_graph()

		# Do next measure
		if (frequency_index  + 1) < len(frequency_list):
			print(f"Go acquire next point : {frequency_list[frequency_index]}")
			self._acquire_set_frequency(frequency_list, frequency_index + 1, mean_samples)
		else:
			self._acquisition_end()

	def _acquire (self, acquisition_parameters):
		self._acquire_set_frequency(acquisition_parameters["freq_points"], 0, acquisition_parameters["mean_samples"])
	
	def _acquisition_end (self):
		self.logger.info("Acquisition finished !")
		self.left_panel.set_start_stop_button_status(False)
	
	def _get_correct_timebase (self, signal_frequency):
		period = 1 / signal_frequency
		div_size_min = (MIN_SIGNAL_PERIOD / NUMBER_OF_HORIZONTAL_DIV) * period

		possible_div_sizes = [
			"5e-9", "10e-9", "20e-9", "50e-9", "100e-9", "200e-9", "500e-9",
			"1e-6", "2e-6", "5e-6", "10e-6", "20e-6", "50e-6", "100e-6", "200e-6", "500e-6",
			"1e-3", "2e-3", "5e-3", "10e-3", "20e-3", "50e-3", "100e-3", "200e-3", "500e-3",
			"1", "2", "5", "10", "20", "50"
		]
		
		for current_div_size in possible_div_sizes:
			if float(current_div_size) > div_size_min:
				return float (current_div_size)

		return possible_div_sizes[-1]
	
	def _get_waiting_time (self, div_size, mean_samples):
		time_to_wait = NUMBER_OF_HORIZONTAL_DIV * div_size	# Time we see on screen
		time_to_wait *= OSCILLOSCOPE_SECURITY_FACTOR
		time_to_wait += OSCILLOSCOPE_PROCESSING_TIME_S
		time_to_wait *= mean_samples**1.2
		time_to_wait += OSCILLOSCOPE_STABILISATION_TIME_S
		time_to_wait = max(time_to_wait, OSCILLOSCOPE_MINIMUM_WAITING_TIME_S) # Security
		# REMOVE BEFORE FLIGHT
		print(time_to_wait)

		time_to_wait_ms = int(time_to_wait * 1000)

		return time_to_wait_ms
