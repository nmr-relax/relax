"""A 5-state model in the xz-plane (no pivotting of alpha).

The 5 states correspond to the Euler angles (z-y-z notation):
    State 1:    {0, pi/4, 0}
    State 2:    {0, pi/8, 0}
    State 3:    {0, 0, 0}
    State 4:    {0, -pi/8, 0}
    State 5:    {0, -pi/4, 0}
"""

# Python module imports.
from math import sqrt


# Create the data pipe.
pipe.create('test', 'N-state')


# Load the C-terminal alignment tensors..
n_state_model.init(label='chi1', domain='C', red=False, params=(-1/2., -1/2.,  0.,   0.,     0.))
n_state_model.init(label='chi2', domain='C', red=False, params=(-1/8., -7/8.,  0.,   0.,     0.))
n_state_model.init(label='chi3', domain='C', red=False, params=(-1/8.,  1/16., 0.,   0.,    -15/16.))
n_state_model.init(label='chi4', domain='C', red=False, params=(7/16., -7/8.,  0.,   9/16.,  0.))
n_state_model.init(label='chi5', domain='C', red=False, params=(-1/2., -1/2.,  3/8., 0.,     0.))

# Calculate the singular values.
n_state_model.svd(basis_set=0, domain='C')
n_state_model.svd(basis_set=1, domain='C')

# Calculate the angles between the matrices.
n_state_model.matrix_angles(basis_set=0, domain='C')
n_state_model.matrix_angles(basis_set=1, domain='C')


# Load the N-terminal alignment tensors.
n_state_model.init(label='chi1', domain='N', red=True, params=(1/4.,   -1/2.,   0.,              3/4.,   0.))
n_state_model.init(label='chi2', domain='N', red=True, params=(7/16.,  -7/8.,   0.,              9/16.,  0.))
n_state_model.init(label='chi3', domain='N', red=True, params=(-1/32.,  1/16., -15/(16*sqrt(2)), 3/32., -15/(16*sqrt(2))))
n_state_model.init(label='chi4', domain='N', red=True, params=(1.,     -7/8.,   0.,              0.,     0.))
n_state_model.init(label='chi5', domain='N', red=True, params=(1/4.,   -1/2.,   3/(8*sqrt(2)),   3/4.,  -3/(8*sqrt(2))))

# Calculate the singular values.
n_state_model.svd(basis_set=0, domain='N')
n_state_model.svd(basis_set=1, domain='N')

# Calculate the angles between the matrices.
n_state_model.matrix_angles(basis_set=0, domain='N')
n_state_model.matrix_angles(basis_set=1, domain='N')


# Grid search.
grid_search(inc=11)

# Minimise.
minimise('simplex')

# Finish.
#results.write(file='devnull', force=1)
