import pyvisa

TIMEOUT_MS = 50
NUMBER_OF_QUERY_ATTEMPT = 10

class VISAManager:
	def __init__ (self, supported_instruments, logger):
		self.supported_instruments = supported_instruments
		self.logger = logger
		self.generator = None
		self.oscilloscope = None

		self.rm = pyvisa.ResourceManager()
	
	def get_relevant_ports (self):
		return ("COM1", "COM2", "COM3")
	
	def _open_resource (self, port):
		return "MOCK"
	
	def _close_resource (self, instr_resource):
		instr_resource.close()

	def _is_instrument_a_generator (self, model):
		for generator_model in self.supported_instruments["generator"].keys():
			if model == generator_model:
				return True

		return False

	def _is_instrument_a_oscilloscope (self, model):
		for oscilloscope_model in self.supported_instruments["oscilloscope"].keys():
			if model == oscilloscope_model:
				return True

		return False

	def _is_model_supported (self, model):
		return (self._is_instrument_a_generator(model) or self._is_instrument_a_oscilloscope(model))
	
	def _get_generator_port (self):
		if self.generator != None:
			return self.generator.get_port()

		return None

	def _get_oscilloscope_port (self):
		if self.oscilloscope != None:
			return self.oscilloscope.get_port()

		return None

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

	def generator_is_responding (self):
		if self.generator == None:
			self.logger.debug("Cannot check if generator is responding because no generator is set")
			return False

		return self.generator.is_responding()

	def oscilloscope_is_responding (self):
		if self.oscilloscope == None:
			self.logger.debug("Cannot check if oscilloscope is responding because no oscilloscope is set")
			return False

		return self.oscilloscope.is_responding()
