"""A 5-state model in the xz-plane (no pivotting of alpha).

The 5 states correspond to the Euler angles (z-y-z notation):
    State 1:    {0, pi/4, 0}
    State 2:    {0, pi/8, 0}
    State 3:    {0, 0, 0}
    State 4:    {0, -pi/8, 0}
    State 5:    {0, -pi/4, 0}
"""

# Python module imports.
from math import cos, pi, sqrt


# Create the data pipe.
self._execute_uf('test', 'N-state', uf_name='pipe.create')


# Define the two domains.
self._execute_uf(uf_name='domain', id='C')
self._execute_uf(uf_name='domain', id='N')

# Load the C-terminal alignment tensors.
self._execute_uf(uf_name='align_tensor.init', tensor='chi1 C-dom', align_id='1', domain='C', params=(-1/2., -1/2.,  0.,   0.,     0.))
self._execute_uf(uf_name='align_tensor.init', tensor='chi2 C-dom', align_id='2', domain='C', params=(-1/8., -7/8.,  0.,   0.,     0.))
self._execute_uf(uf_name='align_tensor.init', tensor='chi3 C-dom', align_id='3', domain='C', params=(-1/8.,  1/16., 0.,   0.,    -15/16.))
self._execute_uf(uf_name='align_tensor.init', tensor='chi4 C-dom', align_id='4', domain='C', params=(7/16., -7/8.,  0.,   9/16.,  0.))
self._execute_uf(uf_name='align_tensor.init', tensor='chi5 C-dom', align_id='5', domain='C', params=(-1/2., -1/2.,  3/8., 0.,     0.))

# Calculate the singular values.
self._execute_uf(uf_name='align_tensor.svd', basis_set=0, tensors=['chi1 C-dom', 'chi2 C-dom', 'chi3 C-dom', 'chi4 C-dom', 'chi5 C-dom'])
self._execute_uf(uf_name='align_tensor.svd', basis_set=1, tensors=['chi1 C-dom', 'chi2 C-dom', 'chi3 C-dom', 'chi4 C-dom', 'chi5 C-dom'])

# Calculate the angles between the matrices.
self._execute_uf(uf_name='align_tensor.matrix_angles', basis_set='unitary 5D', tensors=['chi1 C-dom', 'chi2 C-dom', 'chi3 C-dom', 'chi4 C-dom', 'chi5 C-dom'])
self._execute_uf(uf_name='align_tensor.matrix_angles', basis_set='geometric 5D', tensors=['chi1 C-dom', 'chi2 C-dom', 'chi3 C-dom', 'chi4 C-dom', 'chi5 C-dom'])


# Load the N-terminal alignment tensors.
self._execute_uf(uf_name='align_tensor.init', tensor='chi1 N-dom', align_id='1', domain='N', params=(1/20.*(2-3*sqrt(2)),   -1/2.,   0.,              0.,   0.))
self._execute_uf(uf_name='align_tensor.init', tensor='chi2 N-dom', align_id='2', domain='N', params=(1/80.*(26-9*sqrt(2)),  -7/8.,   0.,              0.,  0.))
self._execute_uf(uf_name='align_tensor.init', tensor='chi3 N-dom', align_id='3', domain='N', params=(-1/160.*(8+3*sqrt(2)),  1/16.,  0.,    0., -3/16.*(1+sqrt(2)+2*cos(pi/8.))))
self._execute_uf(uf_name='align_tensor.init', tensor='chi4 N-dom', align_id='4', domain='N', params=(7/16.,                 -7/8.,   0.,    9/80.*(1+sqrt(2)),     0.))
self._execute_uf(uf_name='align_tensor.init', tensor='chi5 N-dom', align_id='5', domain='N', params=(1/20.*(2-3*sqrt(2)),   -1/2.,   3/40.*(1+sqrt(2)+2*cos(pi/8.)),   0., 0.))

# Specify the tensor reductions.
self._execute_uf(uf_name='align_tensor.reduction', full_tensor='chi1 C-dom', red_tensor='chi1 N-dom')
self._execute_uf(uf_name='align_tensor.reduction', full_tensor='chi2 C-dom', red_tensor='chi2 N-dom')
self._execute_uf(uf_name='align_tensor.reduction', full_tensor='chi3 C-dom', red_tensor='chi3 N-dom')
self._execute_uf(uf_name='align_tensor.reduction', full_tensor='chi4 C-dom', red_tensor='chi4 N-dom')
self._execute_uf(uf_name='align_tensor.reduction', full_tensor='chi5 C-dom', red_tensor='chi5 N-dom')

# Calculate the singular values.
self._execute_uf(uf_name='align_tensor.svd', basis_set=0, tensors=['chi1 N-dom', 'chi2 N-dom', 'chi3 N-dom', 'chi4 N-dom', 'chi5 N-dom'])
self._execute_uf(uf_name='align_tensor.svd', basis_set=1, tensors=['chi1 N-dom', 'chi2 N-dom', 'chi3 N-dom', 'chi4 N-dom', 'chi5 N-dom'])

# Calculate the angles between the matrices.
self._execute_uf(uf_name='align_tensor.matrix_angles', basis_set='unitary 5D', tensors=['chi1 N-dom', 'chi2 N-dom', 'chi3 N-dom', 'chi4 N-dom', 'chi5 N-dom'])
self._execute_uf(uf_name='align_tensor.matrix_angles', basis_set='geometric 5D', tensors=['chi1 N-dom', 'chi2 N-dom', 'chi3 N-dom', 'chi4 N-dom', 'chi5 N-dom'])

# Set up the 5-state model.
self._execute_uf(uf_name='n_state_model.select_model', model='2-domain')
self._execute_uf(uf_name='n_state_model.number_of_states', N=5)
self._execute_uf(uf_name='n_state_model.ref_domain', ref='C')

# Set the initial parameter values to the actual values (the grid search is too expensive).
for i in range(5):
    self._execute_uf(uf_name='value.set', val=0.2, param='probs', index=i)
    self._execute_uf(uf_name='value.set', val=0.0, param='alpha', index=i)
    self._execute_uf(uf_name='value.set', val=pi/4-pi/8*i, param='beta', index=i)
    self._execute_uf(uf_name='value.set', val=0.0, param='gamma', index=i)
#self._execute_uf(uf_name='value.set')

# Minimise.
self._execute_uf('simplex', constraints=False, uf_name='minimise.execute', max_iter=1000)

# Centre of mass analysis.
self._execute_uf(uf_name='n_state_model.CoM', pivot_point=[0.0, 0.0, 0.0], centre=[0.0, 0.0, 1.0])

# Cone PDBs.
self._execute_uf(uf_name='n_state_model.cone_pdb', cone_type='diff on cone', file='devnull', force=True)
self._execute_uf(uf_name='n_state_model.cone_pdb', cone_type='diff in cone', file='devnull', force=True)

# Write the results.
self._execute_uf(uf_name='results.write', file='devnull')
