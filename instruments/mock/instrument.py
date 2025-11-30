import logging
import pyvisa
import time

class InstrumentMock:
	def __init__ (self, visa_resource, port, timeout_ms, number_of_query_attempt, logger):
		self.instr = visa_resource
		self.port = port
		self.logger = logger
		self.logger.debug(f"MOCK({self.port}): set instrument")
	
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
