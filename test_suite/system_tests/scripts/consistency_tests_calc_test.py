"""Script for testing consistency testing."""

# Python module imports.
from os import sep

# relax module imports.
from physical_constants import N15_CSA, NH_BOND_LENGTH
from status import Status; status = Status()


# Data directory.
dir = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'jw_mapping'+sep

# The data.
ri_ids = ['NOE_600', 'R1_600', 'R2_600']
ri_type = ['NOE', 'R1', 'R2']
frq = [600e6]*3
data_paths = [dir + 'noe.dat', dir + 'R1.dat', dir + 'R2.dat']

# Read the sequence.
self._execute_uf(uf_name='sequence.read', file='test_seq', dir=status.install_path + sep+'test_suite'+sep+'shared_data', res_num_col=1, res_name_col=2)

# Read the data.
for i in xrange(len(ri_ids)):
    self._execute_uf(uf_name='relax_data.read', ri_id=ri_ids[i], ri_type=ri_type[i], frq=frq[i], file=data_paths[i], res_num_col=1, res_name_col=2, data_col=3, error_col=4)

# Set r, csa, heteronucleus type, and proton type.
self._execute_uf(uf_name='value.set', val=NH_BOND_LENGTH, param='r')
self._execute_uf(uf_name='value.set', val=N15_CSA, param='csa')
self._execute_uf(uf_name='value.set', val='15N', param='heteronuc_type')
self._execute_uf(uf_name='value.set', val='1H', param='proton_type')

# Set the angle between the 15N-1H vector and the principal axis of the 15N chemical shift tensor
self._execute_uf(uf_name='value.set', val=15.7, param='orientation')

# Set the approximate correlation time.
self._execute_uf(uf_name='value.set', val=13 * 1e-9, param='tc')

# Select the frequency.
self._execute_uf(uf_name='jw_mapping.set_frq', frq=600.0 * 1e6)

# Try the reduced spectral density mapping.
self._execute_uf(uf_name='calc')
