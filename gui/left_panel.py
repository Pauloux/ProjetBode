import tkinter as tk
from tkinter import ttk

import numpy as np

class LeftPanel (ttk.Frame):
	##### Left Panel creation #####
	def __init__ (self, parent, supported_instruments, icon, logger):
		super().__init__(parent, borderwidth=5, relief="ridge")
		self.grid(column=0, row=0, sticky="nsew")
		self.columnconfigure(0, weight=1)

		self.supported_instruments = supported_instruments
		self.logger = logger
		self.icon = icon
		self._create_layout()
		self._create_callbacks()
	
	def _create_layout (self):
		self._create_title(0, "Instruments")
		self.refresh_instrument_status_button = self._create_refresh_instrument_button(self, 1)
		generator_list = list(self.supported_instruments["generator"].keys())
		oscilloscope_list = list(self.supported_instruments["oscilloscope"].keys())
		self.generator_frame = InstrumentConfigFrame(self, 2, "Générateur", generator_list, self._update_instruments, self.icon, self.logger)
		self.oscilloscope_frame = InstrumentConfigFrame(self, 3, "Oscilloscope", oscilloscope_list, self._update_instruments, self.icon, self.logger)

		self._create_title(4, "Signal")
		self.signal_shape_frame = ListSelector(self, 5, "Forme", ("Sinus", "Carré"), self.logger)
		self.voltage_range_selector_frame = VoltageRangeConfigFrame(self, 6, self.logger)

		self._create_title(7, "Fréquence")
		self.min_frequency_frame = ValueAndUnitSelector(self, 8, "Fréquence min.", 1, 10000,  1, 100, ("mHz", "Hz", "kHz", "MHz"), 1, 5, self.logger)
		self.max_frequency_frame = ValueAndUnitSelector(self, 9, "Fréquence max.", 1, 10000,  1, 10, ("mHz", "Hz", "kHz", "MHz"), 2, 0, self.logger)
		self.frequency_sweep_frame = FrequencySweepFrame(self, 10, ("mHz", "Hz", "kHz", "MHz"), 1, self.logger)

		self._create_title(11, "Acquisition")
		self.mean_samples = ListSelector(self, 12, "Moyenne", (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024), self.logger)
		
		self.rowconfigure(14, weight=1)	# To automatically adapt the height of the button bellow
		self.start_stop_button = StartStopButton(self, 15, self.get_acquisition_parameters, self.logger)

	def _create_title (self, row, title):
		title_frame = ttk.Frame(self)
		title_frame.grid(column=0, row=row, sticky="ew")

		ttk.Separator(title_frame, orient="horizontal").grid(column=0, row=0, sticky="ew", padx=5)
		ttk.Label(title_frame, text=title).grid(column=1, row=0)
		ttk.Separator(title_frame, orient="horizontal").grid(column=2, row=0, sticky="ew", padx=5)
		title_frame.columnconfigure(0, weight=1)
		title_frame.columnconfigure(1, weight=0)
		title_frame.columnconfigure(2, weight=1)	
	
	def _create_callbacks (self):
		self.start_stop_button.set_callback_on_button_press(self._on_callback_start_stop_button_press)

	##### Refresh instrument button #####
	def _create_refresh_instrument_button (self, parent, row):
		button = tk.Button(parent, image=self.icon["refresh"], command=self._update_instruments)
		button.grid(column=0, row=row, sticky="e", padx=5)

		return button
	
	def set_callback_update_instruments (self, callback_function):
		self.callback_update_instruments = callback_function
	
	def _update_instruments (self):
		self.callback_update_instruments()
	
	##### Start and stop acquisition button ####
	def set_start_stop_button_status (self, measure_is_started):
		self.start_stop_button.set_measure_is_started(measure_is_started)

	def _on_callback_start_stop_button_press (self):
		measure_is_started = self.start_stop_button.get_measure_is_started()

		# Stop the measure if it is running
		if measure_is_started:
			self.start_stop_button.set_measure_is_started(False)
			self.callback_stop_acquisition()
			return

		acquisition_parameters = self.get_acquisition_parameters()
		if acquisition_parameters == None:
			return

		self.start_stop_button.set_measure_is_started(True)
		self.callback_start_acquisition(acquisition_parameters)
	
	def set_callback_start_acquisition (self, callback_function):
		self.callback_start_acquisition = callback_function

	def set_callback_stop_acquisition (self, callback_function):
		self.callback_stop_acquisition = callback_function

	##### Get acquisition parameters #####
	def get_acquisition_parameters (self):
		try:
			return self._get_formatted_acquisition_parameters()
		except ValueError as e:
			tk.messagebox.showerror(message=e)
			return None

	def _get_formatted_acquisition_parameters (self):
		signal_shape = self._get_formated_signal_shape()

		amplitude_bias_dict = self.voltage_range_selector_frame.get_amplitude_bias_value()
		amplitude_Vpp = amplitude_bias_dict["amplitude_Vpp"]
		bias_V = amplitude_bias_dict["bias_V"]

		freq_points = self._get_freq_points()
		mean_samples = self._get_mean_samples_verified()
	
		return {
			"signal_shape" : signal_shape,
			"amplitude" : amplitude_Vpp,
			"bias" : bias_V,
			"freq_points" : freq_points,
			"mean_samples" : mean_samples,
		}

	### Signal shape ###
	def _get_formated_signal_shape (self):
		signal_shape = self.signal_shape_frame.get_value_str()
		signal_shape_lower = signal_shape.lower()

		if signal_shape_lower == "sinus":
			return "sine"
		if signal_shape_lower == "carré":
			return "square"

		self.logger.error("Signal shape {signal_shape} unknown")
		return 

	### Frequency points ###
	def _get_freq_points (self):
		freq_min = self._get_true_min_freq()
		freq_max = self._get_true_max_freq()

		if freq_min >= freq_max:
			raise ValueError("La fréquence minimale doit être strictement inférieure à la fréquence maximale")

		sweep_type = self.frequency_sweep_frame.get_sweep_type()
		if sweep_type == "Linéaire":
			number_of_points_spacing_is_selected = self.frequency_sweep_frame.is_number_of_points_spacing_selected()
			if number_of_points_spacing_is_selected:
				return self._get_freq_points_linear_number_of_points(freq_min, freq_max)

			else:
				return self._get_freq_points_linear_spacing(freq_min, freq_max)
		# Logarithmic if not linear
		else:
			return self._get_freq_points_logarithmic(freq_min, freq_max)	
	
	def _get_freq_points_linear_number_of_points (self, freq_min, freq_max):
		number_of_points = self.frequency_sweep_frame.get_number_of_points()

		if not number_is_in_range(number_of_points, 2, 100000):
			raise ValueError("Le nombre de points en fréquence doit être compris entre 2 et 100 000")

		freq_points = np.linspace(freq_min, freq_max, number_of_points)
		return freq_points.tolist()
		
	def _get_freq_points_linear_spacing (self, freq_min, freq_max):
		freq_step = self._get_true_freq_spacing()

		freq_points = []
		freq = freq_min
		while freq <= freq_max:
			freq_points.append(freq)
			freq += freq_step

		if len (freq_points) < 2:
			raise ValueError("Il doit y avoir au moins 2 points en fréquence au total")

		return freq_points
	
	def _get_freq_points_logarithmic (self, freq_min, freq_max):
		number_of_points_per_decade = self.frequency_sweep_frame.get_number_of_points()

		if not number_is_in_range(number_of_points_per_decade, 1, 10000):
			raise ValueError("Le nombre de points par décade doit être compris entre 1 et 10 000")

		number_of_decade = np.log10(freq_max) - np.log10(freq_min)
		number_of_points_total = int(number_of_points_per_decade * number_of_decade)
	
		if number_of_points_total < 2:
			raise ValueError("Il doit y avoir au moins 2 points en fréquence au total")
		
		freq_points = np.logspace(np.log10(freq_min), np.log10(freq_max), number_of_points_total)
		return freq_points.tolist()
	
	def _get_true_min_freq (self):
		try:
			value = self.min_frequency_frame.get_value()
		except ValueError as e:
			raise ValueError(f"Fréquence minimale : {str(e)}")

		if not number_is_in_range(value, 0.1, 10000):
			raise ValueError("La fréquence minimale doit être comprise entre 0.1 et 10000 (indépendamment de l'unité)")

		unit = self.min_frequency_frame.get_unit()
		true_freq = self._get_frequency_in_Hz(value, unit)

		return true_freq

	def _get_true_max_freq (self):
		try:
			value = self.max_frequency_frame.get_value()
		except ValueError as e:
			raise ValueError(f"Fréquence maximale : {str(e)}")

		if not number_is_in_range(value, 0.1, 10000):
			raise ValueError("La fréquence maximale doit être comprise entre 0.1 et 10000 (indépendamment de l'unité)")

		unit = self.max_frequency_frame.get_unit()
		true_freq = self._get_frequency_in_Hz(value, unit)

		return true_freq
	
	def _get_true_freq_spacing (self):
		try:
			value = self.frequency_sweep_frame.get_spacing_value()
		except ValueError as e:
			raise ValueError(f"Espacement des points en fréquence : {str(e)}")

		if not number_is_in_range(value, 0.1, 10000):
			raise ValueError("L'espacement des points en fréquence doit être compris entre 0.1 et 10000 (indépendamment de l'unité)")

		unit = self.frequency_sweep_frame.get_spacing_unit()
		true_freq = self._get_frequency_in_Hz(value, unit)

		return true_freq

	def _get_frequency_in_Hz (self, value, unit):
		if unit == "mHz":
			return value / 1000
		if unit == "Hz":
			return value
		if unit == "kHz":
			return value * 1000
		if unit == "MHz":
			return value * 1000000

		self.logger.warning(f"Unknown unit {unit} for frequency conversion")
		return 0
	
	### Number of samples for the mean ###
	def _get_mean_samples_verified (self):
		try:
			mean_samples = self.mean_samples.get_value_int()
		except ValueError as e:
			raise ValueError(f"Nombre de points de moyenne : {str(e)}")

		return mean_samples

class FrequencySweepFrame (ttk.Frame):
	##### Frequency sweep frame creation #####
	def __init__ (self, parent, row, combobox_values, combobox_default_index, logger):
		self.logger = logger

		super().__init__(parent)
		self.grid(column=0, row=row, sticky="ew", padx=5, pady=5)
		self.columnconfigure(0, weight=1)

		self._create_type_selector()
		self._create_points_spacing_selector(combobox_values, combobox_default_index)
		self._update_selectors_display()
	
	def _create_type_selector (self):
		self.type_selector_frame = ttk.Frame(self)
		self.type_selector_frame.grid(column=0, row=0, sticky="ew")
		
		label = ttk.Label(self.type_selector_frame, text="Balayage")
		label.grid(column=0, row=0, sticky="w")

		self.type_selector_combobox = ttk.Combobox(self.type_selector_frame, values=("Logarithmique", "Linéaire"), width=13, justify=tk.RIGHT, state="readonly")
		self.type_selector_combobox.current(0)
		self.type_selector_combobox.bind("<<ComboboxSelected>>", self._on_type_selection_change)
		self.type_selector_combobox.grid(column=1, row=0, sticky="e")

		self.type_selector_frame.columnconfigure(0, weight=1)
		self.type_selector_frame.columnconfigure(1, weight=1)
	
	### Points or spacing selector creation (radiobutton, value and unit) ###
	def _create_points_spacing_selector (self, combobox_values, combobox_default_index):
		self.radiobutton_is_points_selected = tk.BooleanVar(value=True)
		self.radiobutton_is_points_selected.trace_add("write", lambda *args: self._update_selectors_state())

		self.points_spacing_selector_frame = ttk.Frame(self)
		self.points_spacing_selector_frame.grid(column=0, row=1, sticky="ew")
		self.points_spacing_selector_frame.columnconfigure(0, weight=1)
		
		self._create_points_frame(self.points_spacing_selector_frame)
		self._create_spacing_frame(self.points_spacing_selector_frame, combobox_values, combobox_default_index)
		self._update_selectors_state()
	
	# Number of points selector (radiobutton and value)
	def _create_points_frame (self, parent):
		self.points_frame = ttk.Frame(parent)
		self.points_frame.grid(column=0, row=0, sticky="ew", pady=5)
		self.points_frame.columnconfigure(0, weight=1)

		self._create_points_radiobutton(self.points_frame)
		self._create_points_spinbox(self.points_frame)
	
	def _create_points_radiobutton (self, parent):
		self.points_radiobutton_text = tk.StringVar(value="Points par décade")

		self.points_radiobutton = tk.Radiobutton(parent, textvariable=self.points_radiobutton_text, variable=self.radiobutton_is_points_selected, value=True)
		self.points_radiobutton.grid(column=0, row=0, sticky="w")
		self.points_radiobutton.columnconfigure(0, weight=1)
	
	def _create_points_spinbox (self, parent):
		self.points_spinbox = tk.Spinbox(parent, from_=1, to=10000, increment=1, wrap=False, justify=tk.RIGHT, width=8)

		set_spinbox_value(self.points_spinbox, 10)
		self.points_spinbox.grid(column=1, row=0, sticky="e")
		self.points_spinbox.columnconfigure(1, weight=1)
		
	# Frequency spacing between points selector (radiobutton, value and unit)
	def _create_spacing_frame (self, parent, combobox_values, combobox_default_index):
		self.spacing_frame = ttk.Frame(parent)
		self.spacing_frame.grid(column=0, row=2, sticky="ew")
		self.spacing_frame.columnconfigure(0, weight=1)

		self._create_spacing_radiobutton(self.spacing_frame)
		self._create_spacing_spinbox(self.spacing_frame)
		self._create_spacing_combobox(self.spacing_frame, combobox_values, combobox_default_index)
	
	def _create_spacing_radiobutton (self, parent):
		self.spacing_radiobutton = tk.Radiobutton(parent, text="Espacement", variable=self.radiobutton_is_points_selected, value=False)
		self.spacing_radiobutton.grid(column=0, row=0, sticky="w")
		self.spacing_radiobutton.columnconfigure(0, weight=1)
	
	def _create_spacing_spinbox (self, parent):
		self.spacing_spinbox = tk.Spinbox(parent, from_=1, to=10000, increment=1, wrap=False, justify=tk.RIGHT, width=8)

		set_spinbox_value(self.spacing_spinbox, 100)
		self.spacing_spinbox.grid(column=1, row=0, sticky="e")
	
	def _create_spacing_combobox (self, parent, values, default_index):
		self.spacing_combobox = ttk.Combobox(parent, values=values, width=6, justify=tk.LEFT, state="readonly")
		self.spacing_combobox.current(default_index)
		self.spacing_combobox.bind("<<ComboboxSelected>>", clear_selection)
		self.spacing_combobox.grid(column=2, row=0, sticky="e")

	##### Interaction with buttons and selectors #####
	def _update_selectors_state (self):
		self.logger.debug(f"radiobutton_is_points_selected set to {self.radiobutton_is_points_selected.get()}")
		if (self.radiobutton_is_points_selected.get() == True):
			self.spacing_spinbox.configure(state=tk.DISABLED)
			self.spacing_combobox.configure(state=tk.DISABLED)
			self.points_spinbox.configure(state=tk.NORMAL)
		else:
			self.points_spinbox.configure(state=tk.DISABLED)
			self.spacing_spinbox.configure(state=tk.NORMAL)
			self.spacing_combobox.configure(state="readonly")

	def _update_selectors_display (self):
		if (self.get_sweep_type() == "Linéaire"):
			self.points_radiobutton_text.set("Points totaux")
			self.spacing_frame.grid()
		else:
			self.points_radiobutton_text.set("Points par décade")
			self.spacing_frame.grid_remove()		# Hide spacing frame
			if not self.radiobutton_is_points_selected.get() == True:
				self.radiobutton_is_points_selected.set(True)	# Auto-select number of points

	def _on_type_selection_change (self, event):
		clear_selection(event)
		self.logger.debug(f"Sweep type set to {self.type_selector_combobox.get()}")
		self._update_selectors_display()
	
	##### Getter #####
	def get_sweep_type (self):
		return self.type_selector_combobox.get()
	
	def is_number_of_points_spacing_selected (self):
		return self.radiobutton_is_points_selected.get()
	
	def get_number_of_points (self):
		try:
			return int(self.points_spinbox.get())
		except ValueError:
			raise ValueError("Le nombre de points en fréquence doit être un entier")
	
	def get_spacing_value (self):
		try:
			return float(self.spacing_spinbox.get())
		except ValueError as e:
			raise ValueError(f"le nombre doit être un nombre à virgule")
	
	def get_spacing_unit (self):
		return self.spacing_combobox.get()

class InstrumentConfigFrame (ttk.Frame):
	##### Instrument configuration frame creation #####
	def __init__ (self, parent, row, label_text, model_values, func_update_instruments_status, icon, logger):
		self.func_update_instruments_status = func_update_instruments_status
		self.logger = logger
		self.icon = icon
		self.label_text = label_text

		super().__init__(parent)
		self.grid(column=0, row=row, sticky="ew", padx=5, pady=5)

		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=0)
		self.columnconfigure(2, weight=0)

		self._create_label(label_text)
		self._create_status_icon()
		self.port_selector = self._create_list_selector(1, (), True, 5)
		self.model_selector = self._create_list_selector(2, model_values, False, 0)

	def _create_list_selector (self, row, values, update_port_on_click, pady):
		combobox = ttk.Combobox(self, values=values, width=15, justify=tk.LEFT, state="readonly")
		combobox.bind("<<ComboboxSelected>>", self._on_list_selector_selection)

		if (values != ()):
			combobox.current(0)

		if (update_port_on_click == True):
			combobox.configure(postcommand=self._on_port_selector_entry)

		combobox.grid(column=0, columnspan=3, row=row, sticky="e", pady=pady)

		return combobox
	
	def _create_status_icon (self):
		self.status_icon = ttk.Label(self, image=self.icon["OK"])
		self.status_icon.grid(column=2, row=0, sticky="e")
		self.set_status_icon(False)

	def _create_label(self, label_text):
		label = ttk.Label(self, text=label_text)
		label.grid(column=0, row=0, sticky="w")
	
	##### Interaction with buttons and selectors #####
	def _on_port_selector_entry (self):
		self._send_callback_get_port_list()
	
	def _on_list_selector_selection (self, event):
		clear_selection(event)
		self._send_callback_set_instrument()
		self.func_update_instruments_status()

	def _update_port_selector_width (self, values):
		max_length = self._get_max_string_length(values)
		if (max_length < 13):
			max_length = 13

		self.port_selector.configure(width = max_length + 2)

	def _get_max_string_length (self, values):
		max_length = 0
		for value in values:
			current_len = len(value)
			if (current_len > max_length):
				max_length = current_len

		return max_length
	
	def _get_selected_port (self):
		return self.port_selector.get()
	
	def _get_selected_model (self):
		return self.model_selector.get()

	##### Callback #####
	def set_callback_get_port_list (self, callback_function):
		self.callback_get_port_list = callback_function
	
	def set_callback_set_instrument (self, callback_function):
		self.callback_set_instrument = callback_function
	
	def _send_callback_set_instrument (self):
		model = self._get_selected_model()
		port = self._get_selected_port()

		self.callback_set_instrument(model, port)

	def _send_callback_get_port_list (self):
		self.callback_get_port_list()
	
	##### Setter #####
	def set_port_list_selector_values (self, values):
		self.port_selector.configure(values=values)
		if (self.port_selector.get() == ""):
			self.port_selector.current(0)

		self._update_port_selector_width(values)
	
	def set_status_icon (self, status_is_OK):
		if (status_is_OK == True):
			self.status_icon.configure(image=self.icon["OK"])
		else:
			self.status_icon.configure(image=self.icon["error"])

class ValueAndUnitSelector (ttk.Frame):
	##### Creation of the selector frame for a number with unit #####
	def __init__ (self, parent, row, label_text, spinbox_min, spinbox_max, spinbox_increment, spinbox_default_value, combobox_values, combobox_default_index, pady, logger):
		self.logger = logger

		super().__init__(parent)
		self.grid(column=0, row=row, sticky="ew", padx=5, pady=pady)

		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=0)
		self.columnconfigure(2, weight=0)
		
		self._create_label(label_text)
		self._create_value_selector(spinbox_min, spinbox_max, spinbox_increment, spinbox_default_value)
		self._create_unit_selector(combobox_values, combobox_default_index)
	
	def _create_label (self, label_text):
		label = ttk.Label(self, text=label_text)
		label.grid(column=0, row=0, sticky="w")

	def _create_value_selector (self, spinbox_min, spinbox_max, spinbox_increment, spinbox_default_value):
		self.spinbox = tk.Spinbox(self, from_=spinbox_min, to=spinbox_max, increment=spinbox_increment, wrap=False, justify=tk.RIGHT, width=8)
		set_spinbox_value(self.spinbox, spinbox_default_value)
		self.spinbox.grid(column=1, row=0, sticky="e")
	
	def _create_unit_selector (self, values, default_index):
		self.combobox = ttk.Combobox(self, values=values, width=6, justify=tk.LEFT, state="readonly")
		self.combobox.current(default_index)
		self.combobox.bind("<<ComboboxSelected>>", clear_selection)
		self.combobox.grid(column=2, row=0, sticky="e")
	
	##### Getter #####
	def get_value (self):
		try:
			return float(self.spinbox.get())
		except ValueError as e:
			raise ValueError(f"le nombre doit être un nombre à virgule")
	
	def get_unit (self):
		return self.combobox.get()

	##### Other public method #####
	def hide (self):
		self.grid_remove()
	
	def show (self):
		self.grid()

class ListSelector (ttk.Frame):
	##### Creation of the list selector frame #####
	def __init__ (self, parent, row, label_text, combobox_values, logger):
		self.logger = logger

		super().__init__(parent)
		self.grid(column=0, row=row, sticky="ew", padx=5)

		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=0)

		self._create_label(label_text)
		self._create_list_selector(combobox_values)
		
	def _create_label (self, label_text):
		label = ttk.Label(self, text=label_text)
		label.grid(column=0, row=0, sticky="w")

	def _create_list_selector (self, values):
		self.combobox = ttk.Combobox(self, values=values, width=6, justify=tk.LEFT, state="readonly")
		self.combobox.current(0)
		self.combobox.bind("<<ComboboxSelected>>", clear_selection)
		self.combobox.grid(column=1, row=0, sticky="e")
	
	##### Getter #####
	def get_value_str (self):
		return self.combobox.get()
	
	def get_value_int (self):
		try:
			return int(self.combobox.get())
		except ValueError as e:
			raise ValueError(f"doit être un nombre entier")

class NumberSelector (ttk.Frame):
	##### Creation of the number selector frame #####
	def __init__ (self, parent, row, label_text, min_value, max_value, increment, default_value, logger):
		self.logger = logger

		super().__init__(parent)
		self.grid(column=0, row=row, sticky="ew", padx=5)

		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=0)

		self._create_label(label_text)
		self._create_number_selector(min_value, max_value, increment, default_value)
		
	def _create_label (self, label_text):
		label = ttk.Label(self, text=label_text)
		label.grid(column=0, row=0, sticky="w")

	def _create_number_selector (self, min_value, max_value, increment, default_value):
		self.spinbox = tk.Spinbox(self, from_=min_value, to=max_value, increment=increment, wrap=False, justify=tk.RIGHT, width=8)
		set_spinbox_value(self.spinbox, default_value)
		self.spinbox.grid(column=1, row=0, sticky="e")

	##### Getter #####
	def get_value (self):
		try:
			return float(self.spinbox.get())
		except ValueError as e:
			raise ValueError(f"le nombre doit être un nombre à virgule")

class StartStopButton (tk.Button):
	##### Creation of the start and stop acquisition button #####
	def __init__ (self, parent, row, func_start_acquisition, logger):
		self.func_start_acquisition = func_start_acquisition
		self.logger = logger

		self.measure_is_started = tk.BooleanVar(value=False)
		self.text = tk.StringVar(value="Commencer")

		super().__init__(parent, textvariable=self.text, command=self._on_press, background="#23C552", activebackground="#13B542")
		self.grid(column=0, row=row, sticky="nsew", padx=10, pady=10)

		parent.rowconfigure(row, weight=1)

	##### Interaction #####
	def _on_press (self):
		self.logger.debug("Start and stop acquisition button pressed")
		self.callback_on_button_press()

	def _update (self):
		if (self.measure_is_started.get() == False):
			self.text.set("Commencer")
			self.configure(background="#23C552", activebackground="#13B542")
		else:
			self.text.set("Arrêter")
			self.configure(background="#F84F31", activebackground="#E83F21")
	
	##### Getter #####
	def get_measure_is_started (self):
		return self.measure_is_started.get()
	
	##### Setter #####
	def set_measure_is_started (self, value):
		self.measure_is_started.set(value)
		self._update()

	##### Callback #####
	def set_callback_on_button_press (self, callback_function):
		self.callback_on_button_press = callback_function

class VoltageRangeConfigFrame (ttk.Frame):
	##### Creation of the voltage range selection frame (choose between amplitude/bias and min/max and get the values)
	def __init__ (self, parent, row, logger):
		self.logger = logger

		super().__init__(parent)
		self.grid(column=0, row=row, sticky="ew")
		self.columnconfigure(0, weight=1)
		
		self._create_range_mode_button(0)
		self.amplitude_selector_frame = ValueAndUnitSelector(self, 1, "Amplitude", 0.1, 10000, 0.1, 1, ("V", "Vpp", "mV", "mVpp"), 0, 5, self.logger)
		self.bias_selector_frame = ValueAndUnitSelector(self, 2, "Biais", -10000, 10000, 0.1, 0, ("V", "mV"), 0, 0, self.logger)
		self.minimum_selector_frame = ValueAndUnitSelector(self, 1, "Min.", -10000, 10000, 0.1, 0, ("V", "mV"), 0, 5, self.logger)
		self.maximum_selector_frame = ValueAndUnitSelector(self, 2, "Max.", -10000, 10000, 0.1, 1, ("V", "mV"), 0, 0, self.logger)
	
		self._update_frame_visibility()

	def _create_range_mode_button (self, row):
		self.range_mode_button_text = tk.StringVar()
		self.range_mode_is_min_max_selected = tk.BooleanVar(value=False)

		self.range_mode_button = tk.Button(self, textvariable=self.range_mode_button_text, command=self._on_range_mode_button_press)
		self.range_mode_button.grid(column=0, columnspan=3, row=row)
		self._update_range_mode_button()
	
	##### Interaction #####
	def _on_range_mode_button_press (self):
		self.range_mode_is_min_max_selected.set(not self.range_mode_is_min_max_selected.get())
		self.logger.debug(f"range_mode_is_min_max_selected set to {self.range_mode_is_min_max_selected.get()}")

		self._update_range_mode_button()
		self._update_frame_visibility()
	
	def _update_frame_visibility (self):
		if (self.range_mode_is_min_max_selected.get() == False):
			self.amplitude_selector_frame.show()
			self.bias_selector_frame.show()
			self.minimum_selector_frame.hide()
			self.maximum_selector_frame.hide()
		else:
			self.amplitude_selector_frame.hide()
			self.bias_selector_frame.hide()
			self.minimum_selector_frame.show()
			self.maximum_selector_frame.show()
	
	def _update_range_mode_button (self):
		if (self.range_mode_is_min_max_selected.get() == False):
			self.range_mode_button_text.set("Utiliser min/max")
		else:
			self.range_mode_button_text.set("Utiliser amplitude/biais")

	##### Getter #####
	def get_amplitude_bias_value (self):
		if self.range_mode_is_min_max_selected.get() == True:
			minimum_V = self._get_minimum_value_in_V()
			maximum_V = self._get_maximum_value_in_V()
			if minimum_V >= maximum_V:
				raise ValueError("La valeur minimale du signal doit être strictement inférieure à la valeur maximale du signal")
			return self._convert_min_max_to_amplitude_bias(minimum_V, maximum_V)
		else:
			amplitude_Vpp = self._get_amplitude_value_in_Vpp()
			bias_V = self._get_bias_value_in_V()
			return {
				"amplitude_Vpp" : amplitude_Vpp,
				"bias_V" : bias_V
			}

	def _get_voltage_in_Vpp (self, value, unit):
		tmp_value = value
		if "m" in unit:
			tmp_value = tmp_value / 1000

		if not ("pp" in unit):
			tmp_value = tmp_value * 2

		return tmp_value
	
	def _get_voltage_in_V (self, value, unit):
		tmp_value = value
		if "m" in unit:
			tmp_value = tmp_value / 1000

		return tmp_value

	def _convert_min_max_to_amplitude_bias (self, minimum_V, maximum_V):
		amplitude_Vpp = maximum_V - minimum_V
		bias_V = (minimum_V + maximum_V) / 2

		return {
			"amplitude_Vpp" : amplitude_Vpp,
			"bias_V" : bias_V
		}

	### Minimum value ###
	def _get_minimum_value (self):
		return self.minimum_selector_frame.get_value()
	
	def _get_minimum_value_unit (self):
		return self.minimum_selector_frame.get_unit()
	
	def _get_minimum_value_in_V (self):
		try:
			value = self._get_minimum_value()
		except ValueError as e:
			raise ValueError(f"Valeur minimale du signal : {str(e)}")

		if not number_is_in_range(value, -10000, 10000):
			raise ValueError("La valeur minimale du signal doit être comprise entre +/- 10 000 (indépendamment de l'unité)")

		unit = self._get_minimum_value_unit()

		return self._get_voltage_in_V(value, unit)
	
	### Maximum value ###
	def _get_maximum_value (self):
		return self.maximum_selector_frame.get_value()
	
	def _get_maximum_value_unit (self):
		return self.maximum_selector_frame.get_unit()
	
	def _get_maximum_value_in_V (self):
		try:
			value = self._get_maximum_value()
		except ValueError as e:
			raise ValueError(f"Valeur maximale du signal : {str(e)}")

		if not number_is_in_range(value, -10000, 10000):
			raise ValueError("La valeur maximale du signal doit être comprise entre +/- 10 000 (indépendamment de l'unité)")

		unit = self._get_maximum_value_unit()

		return self._get_voltage_in_V(value, unit)

	### Amplitude value ###
	def _get_amplitude_value (self):
		try:
			value = self.amplitude_selector_frame.get_value()
			return float(value)
		except ValueError as e:
			raise ValueError(f"le nombre doit être un nombre à virgule")
	
	def _get_amplitude_value_unit (self):
		return self.amplitude_selector_frame.get_unit()

	def _get_amplitude_value_in_Vpp (self):
		try:
			value = self._get_amplitude_value()
		except ValueError as e:
			raise ValueError(f"Amplitude du signal : {str(e)}")

		if not number_is_in_range(value, 0.1, 10000):
			raise ValueError("La valeur de l'amplitude du signal doit être comprise entre 0.1 et 10 000 (indépendamment de l'unité)")

		unit = self._get_amplitude_value_unit()

		return self._get_voltage_in_Vpp(value, unit)
	
	### Bias value ###
	def _get_bias_value (self):
		return self.bias_selector_frame.get_value()
	
	def _get_bias_value_unit (self):
		return self.bias_selector_frame.get_unit()
	
	def _get_bias_value_in_V (self):
		try:
			value = self._get_bias_value()
		except ValueError as e:
			raise ValueError(f"Biais du signal : {str(e)}")

		if not number_is_in_range(value, -10000, 10000):
			raise ValueError("La valeur du biais du signal doit être comprise entre +/- 10 000 (indépendamment de l'unité)")

		unit = self._get_bias_value_unit()

		return self._get_voltage_in_V(value, unit)

def set_spinbox_value (widget, value):
	widget.delete(0, "end")
	widget.insert(0, value)

def clear_selection (event):
	event.widget.selection_clear()
	event.widget.master.focus()	# for Windows

def number_is_in_range (number, range_min, range_max):
	return ((range_min <= number) and (number <= range_max))
