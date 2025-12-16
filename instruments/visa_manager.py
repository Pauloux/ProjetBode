import pyvisa

TIMEOUT_MS = 50
NUMBER_OF_QUERY_ATTEMPT = 100

class VISAManager:
	def __init__ (self, supported_instruments, logger):
		self.supported_instruments = supported_instruments
		self.logger = logger
		self.generator = None
		self.oscilloscope = None

		self.rm = pyvisa.ResourceManager()
	
	def get_relevant_ports (self):
		ports = self.rm.list_resources()

		relevant_ports = []

		for port in ports:
			if "USB" in port:
				relevant_ports.append(port)

		if len(relevant_ports) == 0:
			relevant_ports.append("Aucun port détecté")

		return relevant_ports
	
	def _open_resource (self, port):
		try:
			instr = self.rm.open_resource(port)
			self.logger.debug(f"Successfuly opened resource on port {port}")
			return instr
		except Exception as e:
			self.logger.debug(f"Failed to open resource on port {port}, error {e}")
			return None
	
	def _close_resource (self, instr_resource):
		instr_resource.close()

	##### Instruments common functions #####
	def _is_model_supported (self, model):
		return (self._is_instrument_a_generator(model) or self._is_instrument_a_oscilloscope(model))

	def _port_is_used_by (self, port):
		generator_port = self._get_generator_port()
		oscilloscope_port = self._get_oscilloscope_port()

		if port == generator_port:
			return "generator"
		elif port == oscilloscope_port:
			return "oscilloscope"
		else:
			return None

	def set_instrument (self, model, port):
		if not self._is_model_supported(model):
			self.logger.error(f"Unknown instrument model {model}")
			return

		port_used_by = self._port_is_used_by(port)
		if self._is_instrument_a_generator(model):
			if port_used_by == "generator":
				self.generator.close()
			elif port_used_by == "oscilloscope":
				self.oscilloscope.close()
				self.oscilloscope = None

			self.logger.debug(f"Setting {model} as the generator")

			instr_resource = self._open_resource(port)
			if instr_resource == None:
				return

			self.generator = self.supported_instruments["generator"][model](instr_resource, port, TIMEOUT_MS, NUMBER_OF_QUERY_ATTEMPT, self.logger)

		elif self._is_instrument_a_oscilloscope(model):
			if port_used_by == "oscilloscope":
				self.oscilloscope.close()
			elif port_used_by == "generator":
				self.generator.close()
				self.generator = None

			self.logger.debug(f"Setting {model} as the oscilloscope")

			instr_resource = self._open_resource(port)
			if instr_resource == None:
				return

			self.oscilloscope = self.supported_instruments["oscilloscope"][model](instr_resource, port, TIMEOUT_MS, NUMBER_OF_QUERY_ATTEMPT, self.logger)
		else:
			self.logger.debug("Instrument is supported but is not a generator nor an oscilloscope. SHOULD NEVER HAPPEN")

	##### Generator #####
	def generator_is_responding (self):
		if self.generator == None:
			self.logger.debug("Cannot check if generator is responding because no generator is set")
			return False

		return self.generator.is_responding()

	def _get_generator_port (self):
		if self.generator != None:
			return self.generator.get_port()

		return None

	def _is_instrument_a_generator (self, model):
		for generator_model in self.supported_instruments["generator"].keys():
			if model == generator_model:
				return True

		return False

	def set_generator_signal_shape (self, shape):
		self.generator.set_shape(shape)
	
	def set_generator_amplitude_pp (self, amplitude_pp):
		self.generator.set_amplitude(amplitude_pp)
	
	def set_generator_frequency (self, frequency_Hz):
		self.generator.set_frequency(frequency_Hz)

	def set_generator_offset (self, offset_V):
		self.generator.set_offset(offset_V)

	def set_generator_unit (self, unit):
		self.generator.set_unit(unit)

	##### Oscilloscope #####
	def oscilloscope_is_responding (self):
		if self.oscilloscope == None:
			self.logger.debug("Cannot check if oscilloscope is responding because no oscilloscope is set")
			return False

		return self.oscilloscope.is_responding()

	def _get_oscilloscope_port (self):
		if self.oscilloscope != None:
			return self.oscilloscope.get_port()

		return None

	def _is_instrument_a_oscilloscope (self, model):
		for oscilloscope_model in self.supported_instruments["oscilloscope"].keys():
			if model == oscilloscope_model:
				return True

		return False

	def oscilloscope_display_channel (self, channel_number):
		self.oscilloscope.display_channel(channel_number)
	
	def set_oscilloscope_channel_offset (self, channel_number, offset_V):
		self.oscilloscope.set_channel_offset(channel_number, offset_V)

	def set_oscilloscope_channel_range (self, channel_number, range_V):
		self.oscilloscope.set_channel_range(channel_number, range_V)

	def get_oscilloscope_channel_range (self, channel_number):
		return self.oscilloscope.get_channel_range(channel_number)

	def set_oscilloscope_channel_probe_ratio (self, channel_number, ratio):
		self.oscilloscope.set_channel_probe_ratio(channel_number, ratio)
	
	def set_oscilloscope_channel_unit (self, channel_number, unit):
		self.oscilloscope.set_channel_unit(channel_number, unit)

	def set_oscilloscope_timebase_scale (self, scale):
		self.oscilloscope.set_timebase_scale(scale)

	def set_oscilloscope_timebase_mode (self, mode):
		self.oscilloscope.set_timebase_mode(mode)

	def set_average (self, average_number):
		if average_number == 1:
			self._set_average_mode("normal")
		else:
			self._set_average_mode("average")
			self._set_average_number(average_number)

	def _set_average_mode (self, mode):
		self.oscilloscope.set_average_mode(mode)
	
	def _set_average_number (self, number_of_points):
		self.oscilloscope.set_average_number(number_of_points)

	def measure_amplitude_pp (self, channel_number):
		return self.oscilloscope.measure_amplitude_pp(channel_number)

	def measure_phase (self, channel_1_number, channel_2_number):
		return self.oscilloscope.measure_phase(channel_1_number, channel_2_number)
