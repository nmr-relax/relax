"""Script for demonstrating bug #21562, the failure of the NOE analysis when replicated spectra are used."""

# Python module imports.
from os import sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Create the NOE data pipe.
pipe.create('NOE fail', 'noe')

# The path to the data files.
path_struct = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'
path_lists = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists'+sep+'bug_21562'

# Load the structure.
structure.read_pdb(file='2AT7_fmf.pdb', dir=path_struct)

# Load the sequence.
structure.load_spins(spin_id='@N', mol_name_target=None, ave_pos=True)

# Set up the reference spectra.
spectrum.read_intensities(file='n_np4_hs_ph65_02mm_noe1.list', dir=path_lists, spectrum_id='no1', dim=1, int_method='height', int_col=None, spin_id_col=None, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, sep=None, spin_id=None, ncproc=None)
noe.spectrum_type(spectrum_type='ref', spectrum_id='no1')
spectrum.read_intensities(file='n_np4_hs_ph65_02mm_noe2.list', dir=path_lists, spectrum_id='no2', dim=1, int_method='height', int_col=None, spin_id_col=None, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, sep=None, spin_id=None, ncproc=None)
spectrum.replicated(spectrum_ids=['no2', 'no1'])
noe.spectrum_type(spectrum_type='ref', spectrum_id='no2')

# Set up the saturated spectra.
spectrum.read_intensities(file='y_np4_hs_ph65_02mm_noe1.list', dir=path_lists, spectrum_id='yes1', dim=1, int_method='height', int_col=None, spin_id_col=None, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, sep=None, spin_id=None, ncproc=None)
noe.spectrum_type(spectrum_type='sat', spectrum_id='yes1')
spectrum.read_intensities(file='y_np4_hs_ph65_02mm_noe2.list', dir=path_lists, spectrum_id='yes2', dim=1, int_method='height', int_col=None, spin_id_col=None, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, sep=None, spin_id=None, ncproc=None)
spectrum.replicated(spectrum_ids=['yes2', 'yes1'])
noe.spectrum_type(spectrum_type='sat', spectrum_id='yes2')

# The error analysis.
spectrum.error_analysis(subset=None)

# Calculate the NOEs.
calc(verbosity=1)

# Save the NOEs.
value.write(param='noe', file=ds.tmpfile, dir=None, scaling=1.0, comment=None, bc=False, force=True)

# Write the results.
results.write(file='devnull', dir=None, compress_type=1, force=True)

# Create grace files.
grace.write(x_data_type='res_num', y_data_type='peak_intensity', spin_id=None, plot_data='value', file='devnull', dir=None, force=True, norm=False)
grace.write(x_data_type='res_num', y_data_type='noe', spin_id=None, plot_data='value', file='devnull', dir=None, force=True, norm=False)
