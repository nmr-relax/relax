"""Taken from the relax disp manual, section 10.6.1 Dispersion script mode - the sample script.

To run the script, simply type:

$ ../../../../../relax r1rho_1_ini.py --tee r1rho_1_ini.log
"""

# Create the data pipe.
pipe_name = 'base pipe'
pipe_bundle = 'relax_disp'
pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type='relax_disp')

# Create the spins
script(file='relax_2_spins.py', dir=None)

# Name the isotope for field strength scaling.
spin.isotope(isotope='15N')

# Set the spectra experimental properties/settings.
script(file='r1rho_3_spectra_settings.py', dir=None)

# Save the program state before run.
# This state file will also be used for loading, before a later cluster/global fit analysis.
#state.save('ini_setup_r1rho', force=True)
