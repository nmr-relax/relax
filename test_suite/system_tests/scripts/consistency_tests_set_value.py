"""Script for testing the value.set() user function for consistency testing."""

# Python module imports.
from os import sep

# relax module imports.
from physical_constants import N15_CSA, NH_BOND_LENGTH
from status import Status; status = Status()


# Read the sequence.
self._execute_uf(uf_name='sequence.read', file='test_seq', dir=status.install_path + sep+'test_suite'+sep+'shared_data', res_num_col=1, res_name_col=2)

# Try to set the values.
self._execute_uf(uf_name='value.set', val=NH_BOND_LENGTH, param='r')
self._execute_uf(uf_name='value.set', val=N15_CSA, param='csa')
