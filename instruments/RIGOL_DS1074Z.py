import logging
import pyvisa
import time

class RIGOL_DS1074Z:
	def __init__ (self, visa_resource, port, timeout_ms, number_of_query_attempt, logger):
		self.instr = visa_resource
		self.port = port
		self.instr.timeout = timeout_ms
		self.number_of_query_attempt = number_of_query_attempt
		self.logger = logger
	
	def get_port (self):
		return self.port
	
	def close (self):
		try:
			self.instr.close()
			self.logger.debug(f"({self.port})Successfuly closed resource")
		except Exception as e:
			self.logger.error(f"({self.port})Failed to close resource, error {e}")
	
	def _write (self, command):
		try:
			self.instr.write(command)
			self.logger.debug(f"({self.port})Successfully wrote: {command}")
			return True
		except Exception as e:
			self.logger.error(f"({self.port})Error while writting {command}, error : {e}")

		return False
	
	def _read (self):
		for read_attempt in range (self.number_of_query_attempt):
			try:
				response = self.instr.read()
				self.logger.debug(f"({self.port})Successfully read ({read_attempt + 1}/{self.number_of_query_attempt}): {response}")
				return response
			except Exception as e:
				self.logger.debug(f"({self.port})Error while reading ({read_attempt + 1}/{self.number_of_query_attempt}), error : {e}")

		self.logger.error(f"({self.port})Error while reading")
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
	
	def autoscale (self):
		self._write(f":AUT")
	
	##### CHANNEL #####
	def display_channel (self, channel_number):
		self._write(f":CHAN{channel_number}:DISP ON")
	
	def set_channel_offset (self, channel_number, offset_V):
		self._write(f":CHAN{channel_number}:OFFS {offset_V}")
	
	def set_channel_range (self, channel_number, range_V):
		self._write(f":CHAN{channel_number}:RANG {range_V}")
	
	def get_channel_range (self, channel_number):
		try:
			return float(self._query(f"CHAN{channel_number}:RANG?"))
		except Exception as e:
			raise Exception()
	
	def set_channel_probe_ratio (self, channel_number, ratio):
		self._write(f":CHAN{channel_number}:PROB {ratio}")
	
	def set_channel_unit (self, channel_number, unit):
		if unit == "V":
			cmd_unit = "VOLT"
		elif unit == "A":
			cmd_unit = "AMP"
		elif unit == "W":
			cmd_unit = "WATT"
		else:
			self.logger.error(f"({self.port})Channel unit {unit} unknown")
			return

		self._write(f":CHAN{channel_number}:UNIT {cmd_unit}")
	
	def set_average_mode (self, mode):
		mode_lower = mode.lower()
		if mode_lower == "average":
			cmd_mode = "AVER"
		elif mode_lower == "normal":
			cmd_mode = "NORM"
		else:
			self.logger.error(f"({self.port})Average mode {mode} unknown")
			return
			
		self._write(f"ACQ:TYPE {cmd_mode}")
	
	def set_average_number (self, number_of_points):
		self._write(f"ACQ:AVER {number_of_points}")
	
	##### Timebase #####
	def set_timebase_scale (self, scale):
		self._write(f":TIM:SCAL {scale}")
	
	def set_timebase_mode (self, mode):
		mode_lower = mode.lower()
		if mode_lower == "yt":
			cmd_mode = "MAIN"
		elif mode_lower == "xy":
			cmd_mode = "XY"
		else:
			self.logger.error(f"({self.port})Timebase mode {mode} unknown")
			return

		self._write(f":TIM:MODE {cmd_mode}")
	
	def measure_amplitude_pp (self, channel_number):
		try:
			return float(self._query(f":MEAS:ITEM? VPP,CHAN{channel_number}"))
		except Exception as e:
			raise Exception()
	#TMP
	
	def measure_phase (self, channel_1_number, channel_2_number):
		try:
			return float(self._query(f":MEAS:ITEM? RPH,CHAN{channel_1_number},CHAN{channel_2_number}"))
		except Exception as e:
			raise Exception
