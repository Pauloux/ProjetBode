import logging
import pyvisa
import time

class RIGOL_DG1022:
	def __init__ (self, visa_resource, timeout_ms, number_of_query_attempt, logger):
		self.instr = visa_resource
		self.instr.timeout = timeout_ms
		self.number_of_query_attempt = number_of_query_attempt
		self.logger = logger
	
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
				self.logger.debug(f"Successfully read: {response}")
				return response
			except Exception as e:
				self.logger.error(f"Error while reading ({read_attempt + 1}/{self.number_of_query_attempt}), error : {e}")

		return None
		

	def _send_query (self, command):
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
		return self._send_query("*IDN?")
