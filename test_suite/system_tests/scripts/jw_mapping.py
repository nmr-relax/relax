"""Script for jw_mapping testing."""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Create the data pipe.
name = 'jw_mapping'
self._execute_uf(uf_name='pipe.create', pipe_name=name, pipe_type='jw')

# Set up the 15N spins.
self._execute_uf(uf_name='sequence.read', file=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'noe.dat', res_num_col=1, res_name_col=2)
self._execute_uf(uf_name='spin.name', name='N')
self._execute_uf(uf_name='spin.element', element='N')
self._execute_uf(uf_name='spin.isotope', isotope='15N', spin_id='@N')

# Load the relaxation data.
self._execute_uf(uf_name='relax_data.read', ri_id='R1_600',  ri_type='R1',  frq=600.0*1e6, file=status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'R1.dat', res_num_col=1, res_name_col=2, data_col=3, error_col=4)
self._execute_uf(uf_name='relax_data.read', ri_id='R2_600',  ri_type='R2',  frq=600.0*1e6, file=status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'R2.dat', res_num_col=1, res_name_col=2, data_col=3, error_col=4)
self._execute_uf(uf_name='relax_data.read', ri_id='NOE_600', ri_type='NOE', frq=600.0*1e6, file=status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep+'noe.dat', res_num_col=1, res_name_col=2, data_col=3, error_col=4)

# Generate 1H spins for the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='sequence.attach_protons')

# Define the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='interatom.define', spin_id1='@N', spin_id2='@H', direct_bond=True)
self._execute_uf(uf_name='interatom.set_dist', spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)

# Define the chemical shift relaxation interaction.
self._execute_uf(uf_name='value.set', val=-172 * 1e-6, param='csa')

# Set the frequency.
self._execute_uf(uf_name='jw_mapping.set_frq', frq=600.0 * 1e6)

# Jw mapping.
self._execute_uf(uf_name='minimise.calculate')

# Monte Carlo simulations.
self._execute_uf(uf_name='monte_carlo.setup', number=5)
self._execute_uf(uf_name='monte_carlo.create_data')
self._execute_uf(uf_name='minimise.calculate')
self._execute_uf(uf_name='monte_carlo.error_analysis')

# Create grace files.
self._execute_uf(uf_name='grace.write', y_data_type='j0', file='devnull', force=True)
self._execute_uf(uf_name='grace.write', y_data_type='jwx', file='devnull', force=True)
self._execute_uf(uf_name='grace.write', y_data_type='jwh', file='devnull', force=True)

# Value writing.
self._execute_uf(uf_name='value.write', param='j0', file='devnull', force=True)
self._execute_uf(uf_name='value.write', param='jwx', file='devnull', force=True)
self._execute_uf(uf_name='value.write', param='jwh', file='devnull', force=True)

# Finish.
self._execute_uf(uf_name='results.write', file='devnull', force=True)
self._execute_uf(uf_name='state.save', state='devnull', force=True)
