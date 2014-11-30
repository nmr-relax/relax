"""Script for relaxation curve fitting.

Run with a debugging compiled version of Python, eg:

/data/python/pydebug/bin/python relax devel_scripts/memory_leak_test_relax_fit.py

and build the C module with:

gcc -o target_functions/c_chi2.os -c -I/data/python/pydebug/include/python2.7/ -fPIC target_functions/c_chi2.c
gcc -o target_functions/exponential.os -c -I/data/python/pydebug/include/python2.7/ -fPIC target_functions/exponential.c
gcc -o target_functions/exponential_inv.os -c -I/data/python/pydebug/include/python2.7/ -fPIC target_functions/exponential_inv.c
gcc -o target_functions/exponential_sat.os -c -I/data/python/pydebug/include/python2.7/ -fPIC target_functions/exponential_sat.c
gcc -o target_functions/relax_fit.os -c -I/data/python/pydebug/include/python2.7/ -fPIC target_functions/relax_fit.c
gcc -o target_functions/relax_fit.so -shared target_functions/c_chi2.os target_functions/exponential.os target_functions/exponential_inv.os target_functions/exponential_sat.os target_functions/relax_fit.os
"""


# Python module imports.
from os import sep
import sys

# Check.
if not hasattr(sys, 'gettotalrefcount'):
    print("This is not a debugging compiled version of Python, quitting!")
    sys.exit()

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Missing intensity type (allow this script to run outside of the system test framework).
if not hasattr(ds, 'int_type'):
    ds.int_type = 'height'

# Missing temporary directory.
if not hasattr(ds, 'tmpdir'):
    ds.tmpdir = 'temp'

# Create the data pipe.
pipe.create('rx', 'relax_fit')

# The path to the data files.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting'

# Load the sequence.
sequence.read('Ap4Aase.seq', dir=status.install_path + sep+'test_suite'+sep+'shared_data', res_num_col=1, res_name_col=2)

# Deselect unresolved spins.
deselect.read(file='unresolved', dir=data_path, res_num_col=1)

# Name the spins so they can be matched to the assignments.
spin.name(name='N')

# Spectrum names.
names = [
    'T2_ncyc1_ave',
    'T2_ncyc1b_ave',
    'T2_ncyc2_ave',
    'T2_ncyc4_ave',
    'T2_ncyc4b_ave',
    'T2_ncyc6_ave',
    'T2_ncyc9_ave',
    'T2_ncyc9b_ave',
    'T2_ncyc11_ave',
    'T2_ncyc11b_ave'
]

# Relaxation times (in seconds).
times = [
    0.0176,
    0.0176,
    0.0352,
    0.0704,
    0.0704,
    0.1056,
    0.1584,
    0.1584,
    0.1936,
    0.1936
]

# Load the data twice to test data deletion.
for iter in range(2):
    # Loop over the spectra.
    for i in range(len(names)):
        # Load the peak intensities.
        spectrum.read_intensities(file=names[i]+'.list', dir=data_path, spectrum_id=names[i], int_method=ds.int_type)

        # Set the relaxation times.
        relax_fit.relax_time(time=times[i], spectrum_id=names[i])

    # Specify the duplicated spectra.
    spectrum.replicated(spectrum_ids=['T2_ncyc1_ave', 'T2_ncyc1b_ave'])
    spectrum.replicated(spectrum_ids=['T2_ncyc4_ave', 'T2_ncyc4b_ave'])
    spectrum.replicated(spectrum_ids=['T2_ncyc9b_ave', 'T2_ncyc9_ave'])
    spectrum.replicated(spectrum_ids=['T2_ncyc11_ave', 'T2_ncyc11b_ave'])

    # Peak intensity error analysis.
    spectrum.error_analysis()

    # Delete the data.
    if iter == 0:
        for i in range(len(names)):
            spectrum.delete(names[i])

# Set the relaxation curve type.
relax_fit.select_model('exp')

# Grid search.
minimise.grid_search(inc=11)

# Minimise.
from guppy import hpy
file = open('guppy_log', 'w')
for i in range(10000):
    minimise.execute('simplex', constraints=False)
    if not i % 100:
        file.write("Iteration %i\n" % i)
        file.write("Reference counts:\n%s\n\n" % sys.gettotalrefcount())
        h = hpy()
        file.write("Guppy heap:\n%s\n\n\n" % h.heap())
        file.flush()


print("Finished :)")
