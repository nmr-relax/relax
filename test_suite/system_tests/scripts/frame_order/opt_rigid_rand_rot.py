# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Create the data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='rigid', pipe_type='frame order')

# Load the tensors.
self._execute_uf(uf_name='script', file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'frame_order'+sep+'tensors_rigid_rand_rot.py')

# The tensor reductions.
for i in range(10):
    self._execute_uf(uf_name='align_tensor.reduction', full_tensor='a '+repr(i), red_tensor='b '+repr(i))

# Select the model.
self._execute_uf(uf_name='frame_order.select_model', model='rigid')

# Set the reference domain.
self._execute_uf(uf_name='frame_order.ref_domain', ref='a')

# Optimise.
self._execute_uf(uf_name='grid_search', inc=6)
self._execute_uf(uf_name='minimise', min_algor='simplex', constraints=False)

# Write the results.
self._execute_uf(uf_name='results.write', file='devnull', dir=None, force=True)
