import pyvisa
from instruments.Argilent_33120A import Argilent_33120A
from instruments.RIGOL_DG1022 import RIGOL_DG1022
from instruments.RIGOL_DS1074Z import RIGOL_DS1074Z

TIMEOUT_MS = 50
NUMBER_OF_QUERY_ATTEMPT = 10

class VISAManager:
	def __init__ (self, logger):
		self.logger = logger
		self.generator = None
		self.oscilloscope = None

		self.rm = pyvisa.ResourceManager()
	
	def get_relevant_ports (self):
		ports = self.rm.list_resources()

		return ports
	
	def set_generator (self, model, port):
		if (model == "Argilent 33120A"):
			self.generator = Argilent_33120A(self.rm.open_resource(port), TIMEOUT_MS, NUMBER_OF_QUERY_ATTEMPT, self.logger)
		elif (model == "RIGOL DG1022"):
			self.generator = RIGOL_DG1022(self.rm.open_resource(port), TIMEOUT_MS, NUMBER_OF_QUERY_ATTEMPT, self.logger)
		else:
			self.logger.error(f"Unknown generator model {model}")
			return

		self.logger.info(f"Generator {model} on port {port} selected")
	
	def set_oscilloscope (self, model, port):
		if (model == "RIGOL DS1074Z"):
			self.oscilloscope = RIGOL_DS1074Z(self.rm.open_resource(port), TIMEOUT_MS, NUMBER_OF_QUERY_ATTEMPT, self.logger)
		else:
			self.logger.error(f"Unknown oscilloscope model {model}")
			return

		self.logger.info(f"Oscilloscope {model} on port {port} selected")

	def generator_is_responding (self):
		return self.generator.is_responding()

	def oscilloscope_is_responding (self):
		return self.oscilloscope.is_responding()
