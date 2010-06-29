# Script for catching a number of bugs as submitted by Michael Funk (mifu att nmr dot mpibpc dot mpg dot de).  These include:
# Bug #12670 (https://gna.org/bugs/index.php?12670).
# Bug #12679 (https://gna.org/bugs/index.php?12679).

# Python module imports.
import __main__
from os import sep
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()


# Missing temp directory (allow this script to run outside of the system test framework).
if not hasattr(ds, 'tmpdir'):
    ds.tmpdir = 'temp_script'

# Create the 'rx' data pipe.
pipe.create('rx', 'relax_fit')

# The paths to the data files.
seq_path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'sequence'
list_path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists'

# Load the sequence.
sequence.read('1UBQ.seq', dir=seq_path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5)

# Spectrum names.
names = [
    '700mhz-263k-1m-02',
    '700mhz-263k-1m-04',
    '700mhz-263k-1m-06',
    '700mhz-263k-1m-08',
    '700mhz-263k-1m-10',
    '700mhz-263k-1m-12',
    '700mhz-263k-1m-14',
    '700mhz-263k-1m-16'
    ]

# Relaxation times (in seconds).
times = [
    0.004,
    0.008,
    0.012,
    0.016,
    0.020,
    0.024,
    0.028,
    0.032
]

#maf# Definte data path
data_path = '.'

# Loop over the spectra.
for i in xrange(len(names)):
    # Load the peak intensities.
    spectrum.read_intensities(file=names[i]+'.listb', dir=list_path, spectrum_id=names[i], int_method='height', proton='H')

    # Set the relaxation times.
    relax_fit.relax_time(time=times[i], spectrum_id=names[i])

# Specify the duplicated spectra.

#maf# Spectrum baseplane noise for non-duplicated spectra
spectrum.baseplane_rmsd(error=20570, spectrum_id='700mhz-263k-1m-02', spin_id=None)
spectrum.baseplane_rmsd(error=20570, spectrum_id='700mhz-263k-1m-04', spin_id=None)
spectrum.baseplane_rmsd(error=18125, spectrum_id='700mhz-263k-1m-06', spin_id=None)
spectrum.baseplane_rmsd(error=15560, spectrum_id='700mhz-263k-1m-08', spin_id=None)
spectrum.baseplane_rmsd(error=15652, spectrum_id='700mhz-263k-1m-10', spin_id=None)
spectrum.baseplane_rmsd(error=16500, spectrum_id='700mhz-263k-1m-12', spin_id=None)
spectrum.baseplane_rmsd(error=16000, spectrum_id='700mhz-263k-1m-14', spin_id=None)
spectrum.baseplane_rmsd(error=16700, spectrum_id='700mhz-263k-1m-16', spin_id=None)

# Peak intensity error analysis.
spectrum.error_analysis()

# Set the relaxation curve type.
relax_fit.select_model('exp')

# Grid search.
grid_search(inc=11)

# Minimise.
minimise('simplex', scaling=False, constraints=False)

# Monte Carlo simulations.
monte_carlo.setup(number=5)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise('simplex', scaling=False, constraints=False)
monte_carlo.error_analysis()

# Save the relaxation rates.
value.write(param='rx', file='rx.out', dir=ds.tmpdir, force=True)

# Save the results.
results.write(file='devnull', force=True)

# Create Grace plots of the data.
grace.write(y_data_type='chi2', file='chi2.agr', dir=ds.tmpdir, force=True)    # Minimised chi-squared value.
grace.write(y_data_type='i0', file='i0.agr', dir=ds.tmpdir, force=True)    # Initial peak intensity.
grace.write(y_data_type='rx', file='rx.agr', dir=ds.tmpdir, force=True)    # Relaxation rate.
grace.write(x_data_type='relax_times', y_data_type='int', file='intensities.agr', dir=ds.tmpdir, force=True)    # Average peak intensities.
grace.write(x_data_type='relax_times', y_data_type='int', norm=True, file='intensities_norm.agr', dir=ds.tmpdir, force=True)    # Average peak intensities (normalised).

# Save the program state.
state.save('rx.save', dir=ds.tmpdir, force=True)
