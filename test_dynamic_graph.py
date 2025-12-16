import numpy as np

from utils import logging_config
from gui.main_window import MainWindow

def tracer_filtre_passe_bas_ordre_1 (app, f_range, i):
	if (i == 200):
		return

	f = f_range[i]
	amplitude, phase = get_filtre_passe_bas_ordre_1(f)
	
	app.graph_panel.append_data_point(f, 1, amplitude, phase)
	app.graph_panel.update_all_graph()

	print(f"i={i}; f={f}")

	app.after(10, tracer_filtre_passe_bas_ordre_1, app, f_range, i + 1)

def get_filtre_passe_bas_ordre_1 (f):
	cutoff_f = 100
	tf = 1 / (1 + 1j * (2 * np.pi * f) / (2 * np.pi * cutoff_f))

	amplitude = np.abs(tf)
	phase = np.angle(tf, deg=True)

	return (amplitude, phase)

if __name__ == "__main__":
	logger = logging_config.init_logging()

	app = MainWindow(logger)

	logger.info("App opened")

	f_range = np.logspace(-1, 4, 200)
	app.after(1000, tracer_filtre_passe_bas_ordre_1, app, f_range, 1)

	app.mainloop()

