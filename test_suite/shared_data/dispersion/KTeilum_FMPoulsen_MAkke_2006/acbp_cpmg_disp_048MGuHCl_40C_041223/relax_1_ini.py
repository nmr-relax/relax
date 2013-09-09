# Taken from the relax disp manual, section 10.6.1 Dispersion script mode - the sample script
# Create the data pipe.
pipe_name = 'base pipe'
pipe_bundle = 'relax_disp'
pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type='relax_disp')

# Create the spins
script(file='relax_2_spins.py', dir=None)

# Name the isotope for field strength scaling.
spin.isotope(isotope='15N')

# Read the spectrum from NMRSeriesTab file. The "auto" will generate spectrum name of form: Z_A{i}
spectrum.read_intensities(file="peaks_list_max_standard.ser", dir=None, spectrum_id='auto', int_method='height')

# Set the spectra experimental properties/settings.
script(file='relax_3_spectra_settings.py', dir=None)

# Save the program state before run.
# This state file will also be used for loading, before a later cluster/global fit analysis.
state.save('ini_setup', force=True)
