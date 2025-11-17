import logging
import pyvisa
import time

def setup_logging ():
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.DEBUG)
	
	stream_handler = logging.StreamHandler()
	stream_handler.setFormatter(logging.Formatter("Argilent_33120A:%(levelname)s:%(message)s"))
	stream_handler.setLevel(logging.INFO)

	log_file_handler = logging.FileHandler("Argilent_33120A.log")
	log_file_handler.setLevel(logging.DEBUG)
	log_file_handler.setFormatter(logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s"))

	logger.addHandler(log_file_handler)
	logger.addHandler(stream_handler)

	return logger

##### Instrument class #####
class Argilent_33120A:
	
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
	
	def _send_query (self, command):
		if (self.instr == None):
			logger.error(f"[{self.port}] Cannot send query - instrument not initialized")
			return None

		try:
			self.instr.write(command)
			time.sleep(self.timeout_s)
			response = self.instr.read()
			logger.debug(f"[{self.port}] Query: {command}, response: {response}")
			return response
		except pyvisa.VisaIOError as e:
			logger.error(f"[{self.port}] Query: {command}, communication error : {e}")
			return None
		except Exception as e:
			logger.error(f"[{self.port}] Query: {command}, unknown error : {e}")
			return None


	def get_IDN (self):
		return self._send_query("*IDN?")

logger = setup_logging()

instr = Argilent_33120A("USB0::1024::2500::DG1D194204274\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00::0::INSTR", 1)

