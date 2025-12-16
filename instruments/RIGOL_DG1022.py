import logging
import pyvisa
import time

class RIGOL_DG1022:
	def __init__ (self, visa_resource, port, timeout_ms, number_of_query_attempt, logger):
		self.instr = visa_resource
		self.port = port
		self.instr.timeout = timeout_ms
		self.number_of_query_attempt = number_of_query_attempt
		self.logger = logger

		# Default values
		self.set_shape("sine")
		self.set_amplitude(1)
		self.set_offset(0)
	
	def get_port (self):
		return self.port
	
	def close (self):
		try:
			self.instr.close()
			self.logger.debug("Successfuly closed resource")
		except Exception as e:
			self.logger.debug(f"Failed to close resource, error {e}")
	
	def _write (self, command):
		try:
			self.instr.write(command)
			self.logger.debug(f"Successfully wrote: {command}")
			return True
		except Exception as e:
			self.logger.error(f"Error while writting {command}, error : {e}")

		return False
	
	def _read (self):
		for read_attempt in range (self.number_of_query_attempt):
			try:
				response = self.instr.read()
				self.logger.debug(f"Successfully read ({read_attempt + 1}/{self.number_of_query_attempt}): {response}")
				return response
			except Exception as e:
				self.logger.error(f"Error while reading ({read_attempt + 1}/{self.number_of_query_attempt}), error : {e}")

		return None

	def _query (self, command):
		write_success = self._write(command)
		if not write_success:
			return None

		return self._read()

	def is_responding (self):
		response = self.get_IDN()
		if (response == None):
			return False
		else:
			return True

	def get_IDN (self):
		return self._query("*IDN?")
	
	def set_shape (self, signal_shape):
		signal_shape_lower = signal_shape.lower()
		if signal_shape_lower == "sine":
			self.signal_shape = "SIN"
		elif signal_shape_lower == "square":
			self.signal_shape = "SQU"
		else:
			self.signal_shape = None
			self.logger.error(f"Signal shape {signal_shape} unknown")
			return
	
	def set_frequency (self, frequency_Hz):
		self._write(f"APPL:{self.signal_shape} {frequency_Hz},{self.amplitude_pp},{self.offset_V}")
	
	def set_amplitude (self, amplitude_pp):
		self.amplitude_pp = amplitude_pp
	
	def set_offset (self, offset_V):
		self.offset_V = offset_V
	
	def set_unit (self, unit):
		pass
