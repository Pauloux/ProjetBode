from utils import logging_config
from gui.main_window import MainWindow

if __name__ == "__main__":
	logger = logging_config.init_logging()

	app = MainWindow(logger)

	logger.info("App opened")

	app.mainloop()
