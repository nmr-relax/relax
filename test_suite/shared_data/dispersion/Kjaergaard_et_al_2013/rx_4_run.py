"""Taken from the relax disp manual, section 10.6.1 Dispersion script mode - the sample script.

To run the script, simply type:

$ ../../../../../relax rx_4_run.py --tee log_rx_4_run.log
"""

import os
from auto_analyses.relax_fit import Relax_fit

# Set settings for run.
GRID_INC = 11; MC_NUM = 3

# Load the initial state setup
state.load(state='ini_setup_rx.bz2')

# Load the pipe names.
fpipe = open('pipe_names_rx.txt', 'r')
pipenames = []
for line in fpipe:
    pipenames.append([line.split()[0], line.split()[1]])
fpipe.close()

for pipename, pipebundle in pipenames:
    pipe.switch(pipe_name=pipename)
    results_directory = os.path.join("rx", pipename)

    Relax_fit(pipe_name=pipename, pipe_bundle=pipebundle, file_root='rx', results_dir=results_directory, grid_inc=GRID_INC, mc_sim_num=MC_NUM, view_plots=False)
