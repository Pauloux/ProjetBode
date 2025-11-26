import tkinter as tk
from tkinter import ttk

from instruments.visa_manager import VISAManager

class LeftPanel (ttk.Frame):
	def __init__ (self, parent, icon, logger):
		super().__init__(parent, borderwidth=5, relief="ridge")
		self.grid(column=0, row=0, sticky="nsew")
		self.columnconfigure(0, weight=1)

		self.logger = logger
		self.icon = icon
		self._create_layout()
	
	def _create_layout (self):
		self._create_title(0, "Instruments")
		self.generator_frame = InstrumentConfigFrame(self, 1, "Générateur", ("Argilent 33120A", "RIGOL DG1022"), self.icon, self.logger)
		self.oscilloscope_frame = InstrumentConfigFrame(self, 2, "Oscilloscope", ("RIGOL DS1074Z", ), self.icon, self.logger)

		self._create_title(3, "Signal")
		self.signal_shape_frame = ListSelector(self, 4, "Forme", ("Sinus", "Carré"), self.logger)
		self.voltage_range_selector_frame = VoltageRangeConfigFrame(self, 5, self.logger)

		self._create_title(7, "Fréquence")
		self.min_frequency_frame = ValueAndUnitSelector(self, 8, "Fréquence min.", 1, 10000,  1, 100, ("mHz", "Hz", "kHz", "MHz"), 1, 5, self.logger)
		self.max_frequency_frame = ValueAndUnitSelector(self, 9, "Fréquence max.", 1, 10000,  1, 10, ("mHz", "Hz", "kHz", "MHz"), 2, 0, self.logger)
		self.frequency_sweep = FrequencySweepFrame(self, 10, ("mHz", "Hz", "kHz", "MHz"), 1, self.logger)

		self._create_title(11, "Acquisition")
		self.mean_samples = NumberSelector(self, 12, "Moyenne", 1, 1000, 1, 1, self.logger)
		self.interval_between_points = ValueAndUnitSelector(self, 13, "Intervalle points", 0.1, 10000,  0.1, 1, ("ms", "s"), 1, 5, self.logger)
		
		self.rowconfigure(14, weight=1)	# To automatically adapt the height of the button bellow
		self.start_stop_button = StartStopButton(self, 15, self.logger)

	def _create_title (self, row, title):
		title_frame = ttk.Frame(self)
		title_frame.grid(column=0, row=row, sticky="ew")

		ttk.Separator(title_frame, orient="horizontal").grid(column=0, row=0, sticky="ew", padx=5)
		ttk.Label(title_frame, text=title).grid(column=1, row=0)
		ttk.Separator(title_frame, orient="horizontal").grid(column=2, row=0, sticky="ew", padx=5)
		title_frame.columnconfigure(0, weight=1)
		title_frame.columnconfigure(1, weight=0)
		title_frame.columnconfigure(2, weight=1)	
		
class FrequencySweepFrame (ttk.Frame):
	def __init__ (self, parent, row, combobox_values, combobox_default_index, logger):
		self.logger = logger

		super().__init__(parent)
		self.grid(column=0, row=row, sticky="ew", padx=5, pady=5)
		self.columnconfigure(0, weight=1)

		self._create_type_selector()
		self._create_points_spacing_selector(combobox_values, combobox_default_index)
	
	def _create_type_selector (self):
		self.type_selector_frame = ttk.Frame(self)
		self.type_selector_frame.grid(column=0, row=0, sticky="ew")
		
		label = ttk.Label(self.type_selector_frame, text="Balayage")
		label.grid(column=0, row=0, sticky="w")

		self.type_selector_combobox = ttk.Combobox(self.type_selector_frame, values=("Linéaire", "Logarithmique"), width=13, justify=tk.RIGHT, state="readonly")
		self.type_selector_combobox.current(0)
		self.type_selector_combobox.bind("<<ComboboxSelected>>", self._on_type_selection_change)
		self.type_selector_combobox.grid(column=1, row=0, sticky="e")

		self.type_selector_frame.columnconfigure(0, weight=1)
		self.type_selector_frame.columnconfigure(1, weight=1)
	
	def _create_points_spacing_selector (self, combobox_values, combobox_default_index):
		self.radiobutton_is_points_selected = tk.BooleanVar(value=True)
		self.radiobutton_is_points_selected.trace_add("write", lambda *args: self._update_selectors_state())

		self.points_spacing_selector_frame = ttk.Frame(self)
		self.points_spacing_selector_frame.grid(column=0, row=1, sticky="ew")
		self.points_spacing_selector_frame.columnconfigure(0, weight=1)
		
		self._create_points_frame(self.points_spacing_selector_frame)
		self._create_spacing_frame(self.points_spacing_selector_frame, combobox_values, combobox_default_index)
		self._update_selectors_state()
	
	def _create_points_frame (self, parent):
		self.points_frame = ttk.Frame(parent)
		self.points_frame.grid(column=0, row=0, sticky="ew", pady=5)
		self.points_frame.columnconfigure(0, weight=1)

		self._create_points_radiobutton(self.points_frame)
		self._create_points_spinbox(self.points_frame)
	
	def _create_points_radiobutton (self, parent):
		self.points_radiobutton_text = tk.StringVar(value="Points totaux")

		self.points_radiobutton = tk.Radiobutton(parent, textvariable=self.points_radiobutton_text, variable=self.radiobutton_is_points_selected, value=True)
		self.points_radiobutton.grid(column=0, row=0, sticky="w")
		self.points_radiobutton.columnconfigure(0, weight=1)
	
	def _create_points_spinbox (self, parent):
		self.points_spinbox = tk.Spinbox(parent, from_=1, to=10000, increment=1, wrap=False, justify=tk.RIGHT, width=8)

		set_spinbox_value(self.points_spinbox, 10)
		self.points_spinbox.grid(column=1, row=0, sticky="e")
		self.points_spinbox.columnconfigure(1, weight=1)
		
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
		if (self.type_selector_combobox.get() == "Linéaire"):
			self.points_radiobutton_text.set("Points totaux")
			self.spacing_frame.grid()
		else:
			self.points_radiobutton_text.set("Points par décade")
			self.spacing_frame.grid_remove()		# Hide spacing frame
			self.radiobutton_is_points_selected.set(True)	# Auto-select number of points

	def _on_type_selection_change (self, event):
		clear_selection(event)
		self.logger.debug(f"Sweep type set to {self.type_selector_combobox.get()}")
		self._update_selectors_display()

class InstrumentConfigFrame (ttk.Frame):
	def __init__ (self, parent, row, label_text, model_values, icon, logger):
		self.logger = logger
		self.icon = icon
		self.label_text = label_text

		super().__init__(parent)
		self.grid(column=0, row=row, sticky="ew", padx=5, pady=5)

		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=0)
		self.columnconfigure(2, weight=0)

		self._create_label(label_text)
		self._create_refresh_button()
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
	
	def set_port_list_selector_values (self, values):
		self.port_selector.configure(values=values)
		if (self.port_selector.get() == ""):
			self.port_selector.current(0)

		self._update_port_selector_width(values)
	
	def _get_max_string_length (self, values):
		max_length = 0
		for value in values:
			current_len = len(value)
			if (current_len > max_length):
				max_length = current_len

		return max_length
	
	def _update_port_selector_width (self, values):
		max_length = self._get_max_string_length(values)
		if (max_length < 15):
			max_length = 15

		self.port_selector.configure(width = max_length + 2)
	
	def _create_status_icon (self):
		self.status_icon = ttk.Label(self, image=self.icon["OK"])
		self.status_icon.grid(column=2, row=0, sticky="e")
		self.set_status_icon(False)

	def _create_label(self, label_text):
		label = ttk.Label(self, text=label_text)
		label.grid(column=0, row=0, sticky="w")
	
	def _create_refresh_button (self):
		self.status_is_OK = tk.BooleanVar(value = False)

		self.refresh_button = tk.Button(self, image=self.icon["refresh"], command=self._on_refresh_button_press)
		self.refresh_button.grid(column=1, row=0, sticky="e", padx=5)
	
	def _on_refresh_button_press (self):
		self._send_callback_update_instrument()

	def _on_port_selector_entry (self):
		self._send_callback_get_port_list()
	
	def _on_list_selector_selection (self, event):
		clear_selection(event)
		self._send_callback_update_instrument()
	
	def set_status_icon (self, status_is_OK):
		if (status_is_OK == True):
			self.status_icon.configure(image=self.icon["OK"])
		else:
			self.status_icon.configure(image=self.icon["error"])
	
	def trigger_callback_get_port_list (self):
		self._send_callback_get_port_list()

	def set_callback_get_port_list (self, callback_function):
		self.callback_get_port_list = callback_function
	
	def _send_callback_get_port_list (self):
		self.callback_get_port_list()

	def set_callback_update_instrument (self, callback_function):
		self.callback_update_instrument = callback_function
	
	def _send_callback_update_instrument (self):
		port = self._get_port()
		model = self._get_model()

		self.callback_update_instrument(
			port = port,
			model = model
		)

	def _get_port (self):
		return self.port_selector.get()
	
	def _get_model (self):
		return self.model_selector.get()

class ValueAndUnitSelector (ttk.Frame):
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
	
	def hide (self):
		self.grid_remove()
	
	def show (self):
		self.grid()

class ListSelector (ttk.Frame):
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

class NumberSelector (ttk.Frame):
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

class StartStopButton (tk.Button):
	def __init__ (self, parent, row, logger):
		self.logger = logger

		self.measure_is_started = tk.BooleanVar(value=False)
		self.text = tk.StringVar(value="Commencer")

		super().__init__(parent, textvariable=self.text, command=self._on_press, background="#23C552", activebackground="#13B542")
		self.grid(column=0, row=row, sticky="nsew", padx=10, pady=10)

		parent.rowconfigure(row, weight=1)

	def _on_press (self):
		self.measure_is_started.set(not self.measure_is_started.get())
		self.logger.debug(f"measure_is_started set to {self.measure_is_started.get()}")

		self._update()

	def _update (self):
		if (self.measure_is_started.get() == False):
			self.text.set("Commencer")
			self.configure(background="#23C552", activebackground="#13B542")
		else:
			self.text.set("Arrêter")
			self.configure(background="#F84F31", activebackground="#E83F21")

class VoltageRangeConfigFrame (ttk.Frame):
	def __init__ (self, parent, row, logger):
		self.logger = logger

		super().__init__(parent)
		self.grid(column=0, row=row, sticky="ew")
		self.columnconfigure(0, weight=1)
		
		self._create_range_mode_button(0)
		self.amplitude_selector_frame = ValueAndUnitSelector(self, 1, "Amplitude", 0, 10000, 0.1, 0, ("V", "Vpp", "mV", "mVpp"), 0, 5, self.logger)
		self.bias_selector_frame = ValueAndUnitSelector(self, 2, "Biais", -10000, 10000, 0.1, 0, ("V", "mV"), 0, 0, self.logger)
		self.minimum_selector_frame = ValueAndUnitSelector(self, 1, "Min.", -10000, 10000, 0.1, 0, ("V", "mV"), 0, 5, self.logger)
		self.maximum_selector_frame = ValueAndUnitSelector(self, 2, "Max.", -10000, 10000, 0.1, 0, ("V", "mV"), 0, 0, self.logger)
	
		self._update_frame_visibility()

	def _create_range_mode_button (self, row):
		self.range_mode_button_text = tk.StringVar()
		self.range_mode_is_min_max_selected = tk.BooleanVar(value=False)

		self.range_mode_button = tk.Button(self, textvariable=self.range_mode_button_text, command=self._on_range_mode_button_press)
		self.range_mode_button.grid(column=0, columnspan=3, row=row)
		self._update_range_mode_button()
	
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
	
	def _on_range_mode_button_press (self):
		self.range_mode_is_min_max_selected.set(not self.range_mode_is_min_max_selected.get())
		self.logger.debug(f"range_mode_is_min_max_selected set to {self.range_mode_is_min_max_selected.get()}")

		self._update_range_mode_button()
		self._update_frame_visibility()

def set_spinbox_value (widget, value):
	widget.delete(0, "end")
	widget.insert(0, value)

def clear_selection (event):
	event.widget.selection_clear()
	event.widget.master.focus()	# for Windows
