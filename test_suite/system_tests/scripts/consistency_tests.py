"""Script for consistency testing."""

# Python module imports.
from os import devnull, sep
import sys

# relax module imports.
from status import Status; status = Status()

# Create the run.
name = 'consistency'
self._execute_uf(uf_name='pipe.create', pipe_name=name, pipe_type='ct')

# Load the sequence.
self._execute_uf(uf_name='sequence.read', file=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'noe.dat', res_num_col=1, res_name_col=2)

# Load the relaxation data.
self._execute_uf(uf_name='relax_data.read', ri_id='R1_600',  ri_type='R1',  frq=600.0*1e6, file=status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'R1.dat', res_num_col=1, res_name_col=2, data_col=3, error_col=4)
self._execute_uf(uf_name='relax_data.read', ri_id='R2_600',  ri_type='R2',  frq=600.0*1e6, file=status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'R2.dat', res_num_col=1, res_name_col=2, data_col=3, error_col=4)
self._execute_uf(uf_name='relax_data.read', ri_id='NOE_600', ri_type='NOE', frq=600.0*1e6, file=status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'noe.dat', res_num_col=1, res_name_col=2, data_col=3, error_col=4)

# Set the spin information.
spin.name('N')
spin.element('N')
sequence.attach_protons()
spin.isotope('15N', spin_id='@N')
spin.isotope('1H', spin_id='@H')

# Define the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='dipole_pair.define', spin_id1='@N', spin_id2='@H', direct_bond=True)
self._execute_uf(uf_name='dipole_pair.set_dist', spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)

# Define the chemical shift relaxation interaction.
self._execute_uf(uf_name='value.set', val=-172 * 1e-6, param='csa')

# Set the angle between the 15N-1H vector and the principal axis of the 15N chemical shift tensor
self._execute_uf(uf_name='value.set', val=15.7, param='orientation')

# Set the approximate correlation time.
self._execute_uf(uf_name='value.set', val=13 * 1e-9, param='tc')

# Set the frequency.
self._execute_uf(uf_name='consistency_tests.set_frq', frq=600.0 * 1e6)

# Consistency tests.
self._execute_uf(uf_name='calc')

# Monte Carlo simulations.
self._execute_uf(uf_name='monte_carlo.setup', number=500)
self._execute_uf(uf_name='monte_carlo.create_data')
self._execute_uf(uf_name='calc')
self._execute_uf(uf_name='monte_carlo.error_analysis')

# Create grace files.
self._execute_uf(uf_name='grace.write', y_data_type='j0', file='devnull', force=True)
self._execute_uf(uf_name='grace.write', y_data_type='f_eta', file='devnull', force=True)
self._execute_uf(uf_name='grace.write', y_data_type='f_r2', file='devnull', force=True)

# Value writing.
self._execute_uf(uf_name='value.write', param='j0', file='devnull', force=True)
self._execute_uf(uf_name='value.write', param='f_eta', file='devnull', force=True)
self._execute_uf(uf_name='value.write', param='f_r2', file='devnull', force=True)

# Finish.
self._execute_uf(uf_name='results.write', file='devnull', force=True)
self._execute_uf(uf_name='state.save', state='devnull', force=True)
