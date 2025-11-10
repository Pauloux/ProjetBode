import logging
import pyvisa
import time

def setup_logging ():
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.DEBUG)
	
	stream_handler = logging.StreamHandler()
	stream_handler.setFormatter(logging.Formatter("RIGOL_DS1074Z:%(levelname)s:%(message)s"))
	stream_handler.setLevel(logging.INFO)

	log_file_handler = logging.FileHandler("RIGOL_DG1074Z.log")
	log_file_handler.setLevel(logging.DEBUG)
	log_file_handler.setFormatter(logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s"))

	logger.addHandler(log_file_handler)
	logger.addHandler(stream_handler)

	return logger

##### Instrument class #####
class RIGOL_DG1074Z:
	
	def __init__ (self, port, timeout_s):
		self.rm = None
		self.instr = None
		self.port = port
		self.is_connected = False
		self.timeout_s = timeout_s

		try:
			self.rm = pyvisa.ResourceManager()
			self.instr = self.rm.open_resource(self.port)

			logger.info(f"[{self.port}] Connected")

			if self._check_connection():
				self.is_connected = True

		except Exception as e:
			logger.critical(f"[{self.port}] Failed to init: {e}")
	
	def close (self):
		logger.debug(f"[{self.port}] Closing instrument...")
		if self.instr is not None:
			self.instr.close()
			logger.info(f"[{self.port}] Connection closed")
		if self.rm is not None:
			self.rm.close()
	
	def _check_connection (self):
		response = self.get_IDN()

		if (response == None):
			logger.warning(f"[{self.port}] Communication check FAIL")
			return False
		else:
			logger.info(f"[{self.port}] Communication check SUCCESS")
			return True
	
	def _write (self, command):
		if (self.instr == None):
			logger.error(f"[{self.port}] Cannot send command - instrument not initialized")
			return

		try:
			self.instr.write(command)
			logger.debug(f"[{self.port}] Command: {command}")
		except pyvisa.errors.VisaIOError as e:
			logger.error(f"[{self.port}] Command: {command}, communication error : {e}")
			return
		except Exception as e:
			logger.error(f"[{self.port}] Command: {command}, unknown error : {e}")
			return

	def _query (self, command):
		if (self.instr == None):
			logger.error(f"[{self.port}] Cannot send query - instrument not initialized")
			return None

		try:
			self.instr.write(command)
			time.sleep(self.timeout_s)
			response = self.instr.read()
			logger.debug(f"[{self.port}] Query: {command}, response: {response}")
			return response
		except pyvisa.errors.VisaIOError as e:
			logger.error(f"[{self.port}] Query: {command}, communication error : {e}")
			return None
		except Exception as e:
			logger.error(f"[{self.port}] Query: {command}, unknown error : {e}")
			return None

	def get_IDN (self):
		return self._query("*IDN?")
	
	def set_sinusoid (self, frequency, amplitude, offset):
		return self._write(f"APPL:SIN {frequency},{amplitude},{offset}")
	
	def sweep_sinusoid (self, f_min, f_max, step, delay_s, amplitude, offset):
		for frequency in range (f_min, f_max + step, step):
			self.set_sinusoid(frequency, amplitude, offset)
			time.sleep(delay_s)

logger = setup_logging()

instr = RIGOL_DG1074Z("USB0::6833::1230::DS1ZA163254087::0::INSTR", 1)

print(instr._query("MEAS:ITEM? FREQ,CHAN1"))
print(instr._query("MEAS:ITEM? VAMP,CHAN1"))
