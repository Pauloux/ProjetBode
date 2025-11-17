#####
# À faire :
# Menu à gauche
#
# Simplifier/organiser le code
#####

import logging
import time

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

		self._init_shortcut()
		self._init_variables()

		self._create_window()
		self._create_menubar()
		self._create_main_paned()
		self._create_left_panel()
		self._finish_init_main_paned()
	
	def _init_variables (self):
		self.refresh_icon = tk.PhotoImage(file=r"Icons/Refresh_icon.png")
		self.icon_OK = tk.PhotoImage(file=r"Icons/OK_icon.png")
		self.icon_error = tk.PhotoImage(file=r"Icons/Error_icon.png")

		self.show_gain = tk.BooleanVar(value=True)
		self.show_phase = tk.BooleanVar(value=True)
		self.prev_show_gain = tk.BooleanVar(value=True)
		self.prev_show_phase = tk.BooleanVar(value=True)

		self.number_of_graph = tk.IntVar(value=2)
		self.show_one_graph = tk.BooleanVar(value=(self.number_of_graph.get() == 1))
		self.show_two_graph = tk.BooleanVar(value=(self.number_of_graph.get() == 2))
	
		self.amplitude_selection_use_min_max = tk.BooleanVar(value=False)

		self.frequency_sweep_points_radiobutton_text = tk.StringVar(value="Points totaux")
		self.frequency_sweep_points_radiobutton_is_points_selected = tk.BooleanVar(value=True)
		self.frequency_sweep_points_radiobutton_is_points_selected.trace_add("write", lambda *args: self._update_frequency_sweep_radiobuttons_state())

		self.show_debug = tk.BooleanVar(value=False)
	
	def _init_shortcut (self):
		self.bind("<Control-w>", lambda *args: self.destroy())
	
	def _create_window (self):
		self.title("Projet Bode - V1.0")
		self.geometry("1200x800")
		self.minsize(300, 150)

		# Allow resizing
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
	
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

	def _create_left_panel (self):
		self.left_panel = ttk.Frame(self.main_paned, borderwidth=5, relief="ridge")
		self.left_panel.grid(column=0, row=0, sticky="nsew")
		self.left_panel.columnconfigure(0, weight=1)
		self.left_panel.rowconfigure(0, weight=0)

		self._create_title_left_panel(0, "Instruments")
		self._create_generator_frame(1)
		self._create_oscilloscope_frame(2)

		self._create_title_left_panel(3, "Signal")
		self._create_signal_shape_frame(4)
		self._create_amplitude_selection_button(5)
		self._create_amplitude_bias_min_max_control(6)

		self._create_title_left_panel(7, "Fréquence")
		self._create_min_frequency_frame(8)
		self._create_max_frequency_frame(9)
		self._create_frequency_sweep_type_frame(10)
		self._create_frequency_sweep_points_spacing_frame(11)

	def _create_title_left_panel (self, row, title):
		title_frame = ttk.Frame(self.left_panel)
		title_frame.grid(column=0, row=row, sticky="ew")

		ttk.Separator(title_frame, orient="horizontal").grid(column=0, row=0, sticky="ew", padx=5)
		ttk.Label(title_frame, text=title).grid(column=1, row=0)
		ttk.Separator(title_frame, orient="horizontal").grid(column=2, row=0, sticky="ew", padx=5)
		title_frame.columnconfigure(0, weight=1)
		title_frame.columnconfigure(1, weight=0)
		title_frame.columnconfigure(2, weight=1)

	def _create_frequency_sweep_points_spacing_frame (self, row):
		self.frequency_sweep_points_spacing_frame = ttk.Frame(self.left_panel)
		self.frequency_sweep_points_spacing_frame.grid(column=0, row=row, sticky="ew", padx=5)
		self.frequency_sweep_points_spacing_frame.columnconfigure(0, weight=1)
	
		self._create_frequency_sweep_points_frame()
		self._create_frequency_sweep_spacing_frame()
		self._update_frequency_sweep_radiobutton_text()
		self._update_frequency_sweep_radiobuttons_state()
	
	def _create_frequency_sweep_spacing_frame (self):
		self.frequency_sweep_spacing_frame = ttk.Frame(self.frequency_sweep_points_spacing_frame)
		self.frequency_sweep_spacing_frame.grid(column=0, row=1, sticky="ew")

		self.frequency_sweep_spacing_radiobutton = tk.Radiobutton(self.frequency_sweep_spacing_frame, text="Espacement", variable=self.frequency_sweep_points_radiobutton_is_points_selected, value=False)
		self.frequency_sweep_spacing_radiobutton.grid(column=0, row=0, sticky="w")

		self.frequency_sweep_spacing_value_spinbox = tk.Spinbox(self.frequency_sweep_spacing_frame, from_=1, to=10000, increment=1, wrap=False, justify=tk.RIGHT, width=8)
		self.frequency_sweep_spacing_value_spinbox.delete(0, "end")
		self.frequency_sweep_spacing_value_spinbox.insert(0, 100)
		self.frequency_sweep_spacing_value_spinbox.grid(column=1, row=0, sticky="e")

		self.frequency_sweep_spacing_frame.columnconfigure(0, weight=1)
		self.frequency_sweep_spacing_frame.columnconfigure(1, weight=1)

	def _create_frequency_sweep_points_frame (self):
		self.frequency_sweep_points_frame = ttk.Frame(self.frequency_sweep_points_spacing_frame)
		self.frequency_sweep_points_frame.grid(column=0, row=0, sticky="ew")

		self.frequency_sweep_points_radiobutton = tk.Radiobutton(self.frequency_sweep_points_frame, textvariable=self.frequency_sweep_points_radiobutton_text, variable=self.frequency_sweep_points_radiobutton_is_points_selected, value=True)
		self.frequency_sweep_points_radiobutton.grid(column=0, row=0, sticky="w")

		self.frequency_sweep_points_value_spinbox = tk.Spinbox(self.frequency_sweep_points_frame, from_=0, to=10000, increment=1, wrap=False, justify=tk.RIGHT, width=8)
		self.frequency_sweep_points_value_spinbox.delete(0, "end")
		self.frequency_sweep_points_value_spinbox.insert(0, 10)
		self.frequency_sweep_points_value_spinbox.grid(column=1, row=0, sticky="e")

		self.frequency_sweep_points_frame.columnconfigure(0, weight=1)
		self.frequency_sweep_points_frame.columnconfigure(1, weight=1)

	def _update_frequency_sweep_radiobuttons_state (self):
		if (self.frequency_sweep_points_radiobutton_is_points_selected.get() == True):
			self.frequency_sweep_spacing_value_spinbox.configure(state=tk.DISABLED)
			self.frequency_sweep_points_value_spinbox.configure(state=tk.NORMAL)
		else:
			self.frequency_sweep_points_value_spinbox.configure(state=tk.DISABLED)
			self.frequency_sweep_spacing_value_spinbox.configure(state=tk.NORMAL)

	def _update_frequency_sweep_radiobutton_text (self):
		if (self.frequency_sweep_type_frame_combobox.get() == "Linéaire"):
			self.frequency_sweep_points_radiobutton_text.set("Points totaux")
			self.frequency_sweep_spacing_frame.grid()
		else:
			self.frequency_sweep_points_radiobutton_text.set("Points par décade")
			self.frequency_sweep_spacing_frame.grid_remove()
			self.frequency_sweep_points_radiobutton_is_points_selected.set(True)

	def _on_sweep_type_selection (self, event):
		self._clear_selection(event)
		self._update_frequency_sweep_radiobutton_text()
		self.logger.debug(f"Sweep type set to {self.frequency_sweep_type_frame_combobox.get()}")
	
	def _create_frequency_sweep_type_frame (self, row):
		self.frequency_sweep_type_frame = ttk.Frame(self.left_panel)
		self.frequency_sweep_type_frame.grid(column=0, row=row, sticky="ew", padx=5, pady=5)
		
		shape_text = ttk.Label(self.frequency_sweep_type_frame, text="Balayage")
		shape_text.grid(column=0, row=0, sticky="w")

		self.frequency_sweep_type_frame_combobox = ttk.Combobox(self.frequency_sweep_type_frame, values=("Linéaire", "Logarithmique"), width=13, justify=tk.RIGHT, state="readonly")
		self.frequency_sweep_type_frame_combobox.current(0)
		self.frequency_sweep_type_frame_combobox.bind("<<ComboboxSelected>>", self._on_sweep_type_selection)
		self.frequency_sweep_type_frame_combobox.grid(column=1, row=0, sticky="e")

		self.frequency_sweep_type_frame.columnconfigure(0, weight=1)
		self.frequency_sweep_type_frame.columnconfigure(1, weight=1)

	def _create_max_frequency_frame (self, row):
		self.max_frequency_frame = ttk.Frame(self.left_panel)
		self.max_frequency_frame.grid(column=0, row=row, sticky="ew", padx=5)
	
		max_frequency_text = ttk.Label(self.max_frequency_frame, text="Fréquence max.")
		max_frequency_text.grid(column=0, row=0, sticky="w")

		self.max_frequency_value_spinbox = tk.Spinbox(self.max_frequency_frame, from_=0, to=10000, increment=0.1, wrap=False, justify=tk.RIGHT, width=8)
		self.max_frequency_value_spinbox.delete(0, "end")
		self.max_frequency_value_spinbox.insert(0, 0)
		self.max_frequency_value_spinbox.grid(column=1, row=0, sticky="e")

		self.max_frequency_unit_combobox = ttk.Combobox(self.max_frequency_frame, values=("mHz", "Hz", "kHz", "MHz"), width=6, justify=tk.LEFT, state="readonly")
		self.max_frequency_unit_combobox.current(1)
		self.max_frequency_unit_combobox.bind("<<ComboboxSelected>>", self._clear_selection)
		self.max_frequency_unit_combobox.grid(column=2, row=0, sticky="e")

		self.max_frequency_frame.columnconfigure(0, weight=1)
		self.max_frequency_frame.columnconfigure(1, weight=0)
		self.max_frequency_frame.columnconfigure(2, weight=0)

	def _create_min_frequency_frame (self, row):
		self.min_frequency_frame = ttk.Frame(self.left_panel)
		self.min_frequency_frame.grid(column=0, row=row, sticky="ew", padx=5, pady=5)
	
		min_frequency_text = ttk.Label(self.min_frequency_frame, text="Fréquence min.")
		min_frequency_text.grid(column=0, row=0, sticky="w")

		self.min_frequency_value_spinbox = tk.Spinbox(self.min_frequency_frame, from_=0, to=10000, increment=0.1, wrap=False, justify=tk.RIGHT, width=8)
		self.min_frequency_value_spinbox.delete(0, "end")
		self.min_frequency_value_spinbox.insert(0, 0)
		self.min_frequency_value_spinbox.grid(column=1, row=0, sticky="e")

		self.min_frequency_unit_combobox = ttk.Combobox(self.min_frequency_frame, values=("mHz", "Hz", "kHz", "MHz"), width=6, justify=tk.LEFT, state="readonly")
		self.min_frequency_unit_combobox.current(1)
		self.min_frequency_unit_combobox.bind("<<ComboboxSelected>>", self._clear_selection)
		self.min_frequency_unit_combobox.grid(column=2, row=0, sticky="e")

		self.min_frequency_frame.columnconfigure(0, weight=1)
		self.min_frequency_frame.columnconfigure(1, weight=0)
		self.min_frequency_frame.columnconfigure(2, weight=0)
	
	def _create_amplitude_bias_min_max_control (self, row):
		self.amplitude_bias_min_max_control_frame = ttk.Frame(self.left_panel)
		self.amplitude_bias_min_max_control_frame.grid(column=0, row=row, sticky="ew", padx=5)
		self.amplitude_bias_min_max_control_frame.columnconfigure(0, weight=1)
	
		self._create_amplitude_frame()
		self._create_bias_frame()
		self._create_max_frame()
		self._create_min_frame()
		self._update_amplitude_selection()
	
	def _update_amplitude_selection (self):
		if (self.amplitude_selection_use_min_max.get() == True):
			self.amplitude_frame.grid_remove()
			self.bias_frame.grid_remove()
			self.max_frame.grid()
			self.min_frame.grid()
		else:
			self.amplitude_frame.grid()
			self.bias_frame.grid()
			self.max_frame.grid_remove()
			self.min_frame.grid_remove()
	
	def _create_max_frame (self):
		self.max_frame = ttk.Frame(self.amplitude_bias_min_max_control_frame)
		self.max_frame.grid(column=0, row=0, sticky="ew")
	
		max_text = ttk.Label(self.max_frame, text="Max.")
		max_text.grid(column=0, row=0, sticky="w")

		self.max_value_spinbox = tk.Spinbox(self.max_frame, from_=-10000, to=10000, increment=0.1, wrap=False, justify=tk.RIGHT, width=8)
		self.max_value_spinbox.delete(0, "end")
		self.max_value_spinbox.insert(0, 0)
		self.max_value_spinbox.grid(column=1, row=0, sticky="e")

		self.max_unit_combobox = ttk.Combobox(self.max_frame, values=("V", "mV"), width=6, justify=tk.LEFT, state="readonly")
		self.max_unit_combobox.current(0)
		self.max_unit_combobox.bind("<<ComboboxSelected>>", self._clear_selection)
		self.max_unit_combobox.grid(column=2, row=0, sticky="e")

		self.max_frame.columnconfigure(0, weight=1)
		self.max_frame.columnconfigure(1, weight=0)
		self.max_frame.columnconfigure(2, weight=0)

	def _create_min_frame (self):
		self.min_frame = ttk.Frame(self.amplitude_bias_min_max_control_frame)
		self.min_frame.grid(column=0, row=1, sticky="ew", pady=5)
	
		min_text = ttk.Label(self.min_frame, text="Min.")
		min_text.grid(column=0, row=0, sticky="w")

		self.min_value_spinbox = tk.Spinbox(self.min_frame, from_=-10000, to=10000, increment=0.1, wrap=False, justify=tk.RIGHT, width=8)
		self.min_value_spinbox.delete(0, "end")
		self.min_value_spinbox.insert(0, 0)
		self.min_value_spinbox.grid(column=1, row=0, sticky="e")

		self.min_unit_combobox = ttk.Combobox(self.min_frame, values=("V", "mV"), width=6, justify=tk.LEFT, state="readonly")
		self.min_unit_combobox.current(0)
		self.min_unit_combobox.bind("<<ComboboxSelected>>", self._clear_selection)
		self.min_unit_combobox.grid(column=2, row=0, sticky="e")

		self.min_frame.columnconfigure(0, weight=1)
		self.min_frame.columnconfigure(1, weight=0)
		self.min_frame.columnconfigure(2, weight=0)

	def _create_amplitude_frame (self):
		self.amplitude_frame = ttk.Frame(self.amplitude_bias_min_max_control_frame)
		self.amplitude_frame.grid(column=0, row=0, sticky="ew")
	
		amplitude_text = ttk.Label(self.amplitude_frame, text="Amplitude")
		amplitude_text.grid(column=0, row=0, sticky="w")

		self.amplitude_value_spinbox = tk.Spinbox(self.amplitude_frame, from_=0, to=10000, increment=0.1, wrap=False, justify=tk.RIGHT, width=8)
		self.amplitude_value_spinbox.delete(0, "end")
		self.amplitude_value_spinbox.insert(0, 0)
		self.amplitude_value_spinbox.grid(column=1, row=0, sticky="e")

		self.amplitude_unit_combobox = ttk.Combobox(self.amplitude_frame, values=("V", "Vpp", "mV", "mVpp"), width=6, justify=tk.LEFT, state="readonly")
		self.amplitude_unit_combobox.current(0)
		self.amplitude_unit_combobox.bind("<<ComboboxSelected>>", self._clear_selection)
		self.amplitude_unit_combobox.grid(column=2, row=0, sticky="e")

		self.amplitude_frame.columnconfigure(0, weight=1)
		self.amplitude_frame.columnconfigure(1, weight=0)
		self.amplitude_frame.columnconfigure(2, weight=0)

	def _create_bias_frame (self):
		self.bias_frame = ttk.Frame(self.amplitude_bias_min_max_control_frame)
		self.bias_frame.grid(column=0, row=1, sticky="ew", pady=5)
	
		bias_text = ttk.Label(self.bias_frame, text="Bias")
		bias_text.grid(column=0, row=0, sticky="w")

		self.bias_value_spinbox = tk.Spinbox(self.bias_frame, from_=-10000, to=10000, increment=0.1, wrap=False, justify=tk.RIGHT, width=8)
		self.bias_value_spinbox.delete(0, "end")
		self.bias_value_spinbox.insert(0, 0)
		self.bias_value_spinbox.grid(column=1, row=0, sticky="e")

		self.bias_unit_combobox = ttk.Combobox(self.bias_frame, values=("V", "mV"), width=6, justify=tk.LEFT, state="readonly")
		self.bias_unit_combobox.current(0)
		self.bias_unit_combobox.bind("<<ComboboxSelected>>", self._clear_selection)
		self.bias_unit_combobox.grid(column=2, row=0, sticky="e")

		self.bias_frame.columnconfigure(0, weight=1)
		self.bias_frame.columnconfigure(1, weight=0)
		self.bias_frame.columnconfigure(2, weight=0)

	def _create_signal_shape_frame (self, row):
		self.signal_shape_frame = ttk.Frame(self.left_panel)
		self.signal_shape_frame.grid(column=0, row=row, sticky="ew", padx=5)
		
		shape_text = ttk.Label(self.signal_shape_frame, text="Forme")
		shape_text.grid(column=0, row=0, sticky="w")

		self.signal_shape_combobox = ttk.Combobox(self.signal_shape_frame, values=("Sinus", "Carré"), width=6, justify=tk.RIGHT, state="readonly")
		self.signal_shape_combobox.current(0)
		self.signal_shape_combobox.bind("<<ComboboxSelected>>", self._clear_selection)
		self.signal_shape_combobox.grid(column=1, row=0, sticky="e")

		self.signal_shape_frame.columnconfigure(0, weight=1)
		self.signal_shape_frame.columnconfigure(1, weight=1)
	
	def _create_amplitude_selection_button (self, row):
		self.amplitude_selection_button = ttk.Button(self.left_panel, text="Utiliser min/max", command=self._on_amplitude_selection)
		self.amplitude_selection_button.grid(column=0, row=row, padx=5, pady=5)

	def _create_generator_frame (self, row):
		self.generator_frame = ttk.Frame(self.left_panel)
		self.generator_frame.grid(column=0, row=row, sticky="ew", padx=5)

		generator_text = ttk.Label(self.generator_frame, text="Générateur")
		generator_text.grid(column=0, row=0, sticky="w")

		self.tmp_generator_status_OK = True
	
		self.generator_refresh_button = ttk.Button(self.generator_frame, image=self.refresh_icon, command=self._on_generator_refresh)
		self.generator_refresh_button.grid(column=1, row=0, sticky="e", padx=5)

		self.generator_status = ttk.Label(self.generator_frame, image=self.icon_OK)
		self.generator_status.grid(column=2, row=0, sticky="e")

		self.generator_frame.columnconfigure(0, weight=1)
		self.generator_frame.columnconfigure(1, weight=0)
		self.generator_frame.columnconfigure(2, weight=0)

		self.generator_combobox_port = ttk.Combobox(self.generator_frame, values=("COM0", "COM1", "COM2"), width=15, justify=tk.RIGHT, state="readonly")
		self.generator_combobox_port.current(0)
		self.generator_combobox_port.grid(column=0, columnspan=3, row=1, sticky="e", pady=5)
		self.generator_combobox_port.bind("<<ComboboxSelected>>", self._clear_selection)

		self.generator_combobox_model = ttk.Combobox(self.generator_frame, values=("Argilent 33120A", "RIGOL DG1022"), width=15, justify=tk.RIGHT, state="readonly")
		self.generator_combobox_model.current(0)
		self.generator_combobox_model.grid(column=0, columnspan=3, row=2, sticky="e", pady=5)
		self.generator_combobox_model.bind("<<ComboboxSelected>>", self._clear_selection)

	def _create_oscilloscope_frame (self, row):
		self.oscilloscope_frame = ttk.Frame(self.left_panel)
		self.oscilloscope_frame.grid(column=0, row=row, sticky="ew", padx=5)

		oscilloscope_text = ttk.Label(self.oscilloscope_frame, text="Oscilloscope")
		oscilloscope_text.grid(column=0, row=0, sticky="w")

		self.tmp_oscilloscope_status_OK = True
	
		self.oscilloscope_refresh_button = ttk.Button(self.oscilloscope_frame, image=self.refresh_icon, command=self._on_oscilloscope_refresh)
		self.oscilloscope_refresh_button.grid(column=1, row=0, sticky="e", padx=5)

		self.oscilloscope_status = ttk.Label(self.oscilloscope_frame, image=self.icon_OK)
		self.oscilloscope_status.grid(column=2, row=0, sticky="e")

		self.oscilloscope_frame.columnconfigure(0, weight=1)
		self.oscilloscope_frame.columnconfigure(1, weight=0)
		self.oscilloscope_frame.columnconfigure(2, weight=0)

		self.oscilloscope_combobox_port = ttk.Combobox(self.oscilloscope_frame, values=("COM0", "COM1", "COM2"), width=15, justify=tk.RIGHT, state="readonly")
		self.oscilloscope_combobox_port.current(0)
		self.oscilloscope_combobox_port.grid(column=0, columnspan=3, row=1, sticky="e", pady=5)
		self.oscilloscope_combobox_port.bind("<<ComboboxSelected>>", self._clear_selection)

		self.oscilloscope_combobox_model = ttk.Combobox(self.oscilloscope_frame, values=("RIGOL DS1074Z", "Autres ?"), width=15, justify=tk.RIGHT, state="readonly")
		self.oscilloscope_combobox_model.current(0)
		self.oscilloscope_combobox_model.grid(column=0, columnspan=3, row=2, sticky="e", pady=5)
		self.oscilloscope_combobox_model.bind("<<ComboboxSelected>>", self._clear_selection)

	def _clear_selection (self, event):
		event.widget.selection_clear()

	def _on_oscilloscope_refresh (self):
		self.tmp_oscilloscope_status_OK = not self.tmp_oscilloscope_status_OK
		if (self.tmp_oscilloscope_status_OK == False):
			self.logger.error("Oscilloscope initialize FAIL")
		else:
			self.logger.info("Oscilloscope initialize SUCCESS")

		self._set_oscilloscope_status(self.tmp_oscilloscope_status_OK)

	def _on_generator_refresh (self):
		self.tmp_generator_status_OK = not self.tmp_generator_status_OK
		if (self.tmp_generator_status_OK == False):
			self.logger.error("Generator initialize FAIL")
		else:
			self.logger.info("Generator initialize SUCCESS")

		self._set_generator_status(self.tmp_generator_status_OK)
	
	def _on_amplitude_selection (self):
		self.amplitude_selection_use_min_max.set(not self.amplitude_selection_use_min_max.get())
		self.logger.debug(f"amplitude_selection_use_min_max set to {self.amplitude_selection_use_min_max.get()}")

		if (self.amplitude_selection_use_min_max.get() == True):
			self.amplitude_selection_button.configure(text="Utiliser amplitude/biais")
		else:
			self.amplitude_selection_button.configure(text="Utiliser min/max")

		self._update_amplitude_selection()
	
	def _set_oscilloscope_status (self, is_OK):
		if is_OK:
			self.oscilloscope_status.configure(image=self.icon_OK)
		else:
			self.oscilloscope_status.configure(image=self.icon_error)

	def _set_generator_status (self, is_OK):
		if is_OK:
			self.generator_status.configure(image=self.icon_OK)
		else:
			self.generator_status.configure(image=self.icon_error)

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
