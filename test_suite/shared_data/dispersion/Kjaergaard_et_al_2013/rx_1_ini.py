"""Taken from the relax disp manual, section 10.6.1 Dispersion script mode - the sample script.

To run the script, simply type:

$ ../../../../../relax rx_1_ini.py --tee log_rx_1_ini.log
"""

# Create the data pipe.
pipe_name = 'base pipe'
pipe_bundle = 'relax_fit'
pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type='relax_fit')

# Create the spins
script(file='relax_2_spins.py', dir=None)

# Set the spectra experimental properties/settings.
script(file='rx_3_spectra_settings.py', dir=None)

# Save the program state before run.
# This state file will also be used for loading, before a later cluster/global fit analysis.
state.save('ini_setup_rx', force=True)
