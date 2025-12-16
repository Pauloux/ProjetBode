import logging
import pyvisa

class InstrumentMock:
	def __init__ (self, visa_resource, port, timeout_ms, number_of_query_attempt, logger):
		self.instr = visa_resource
		self.port = port
		self.logger = logger
		self.logger.debug(f"MOCK({self.port}): set instrument")
	
	##### Common #####
	def get_port (self):
		return self.port
	
	def close (self):
		self.logger.debug(f"MOCK({self.port}): closed instrument on port")

	def _send_query (self, command):
		self.logger.debug(f"MOCK({self.port}): query {command}")
		return "MOCK"

	def is_responding (self):
		return True

	def get_IDN (self):
		return self._send_query("*IDN?")
		
	def set_unit (self, unit):
		pass
	
	##### Generator #####
	def set_shape (self, shape):
		pass
	
	def set_amplitude (self, amplitude_pp):
		pass
	
	def set_frequency (self, frequency_Hz):
		pass
	
	def set_offset (self, offset_V):
		pass
	
	##### Oscilloscope #####
	def display_channel (self, channel_number):
		pass
	
	def set_timebase_mode (self, mode):
		pass
	
	def set_timebase_scale (self, scale):
		pass
	
	def set_channel_range (self, channel_number, range_V):
		pass

	def get_channel_range (self, channel_number):
		return 1.2
		return 1

	def set_channel_unit (self, channel_number, unit):
		pass
	
	def set_channel_probe_ratio (self, channel_number, ratio):
		pass
	
	def set_average_mode (self, mode):
		pass
	
	def set_average_number (self, number_of_points):
		pass
	
	def set_channel_offset (self, channel_number, offset_V):
		pass
	
	def measure_amplitude_pp (self, channel_number):
		return 1.0
	
	def measure_phase (self, channel_1_number, channel_2_number):
		return 90.0
