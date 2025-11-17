import logging

def init_logging ():
          logger = logging.getLogger(__name__)
          logger.setLevel(logging.DEBUG)
          
          stream_handler = logging.StreamHandler()
          stream_handler.setFormatter(logging.Formatter("App:%(levelname)s:%(message)s"))
          #stream_handler.setLevel(logging.INFO)
          stream_handler.setLevel(logging.DEBUG)
  
          log_file_handler = logging.FileHandler("App.log")
          log_file_handler.setLevel(logging.DEBUG)
          log_file_handler.setFormatter(logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s"))
  
          logger.addHandler(log_file_handler)
          logger.addHandler(stream_handler)
  
          return logger
