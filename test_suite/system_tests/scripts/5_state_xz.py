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


# Load the C-terminal alignment tensors.
align_tensor.init(tensor='chi1 C-dom', params=(-1/2., -1/2.,  0.,   0.,     0.))
align_tensor.init(tensor='chi2 C-dom', params=(-1/8., -7/8.,  0.,   0.,     0.))
align_tensor.init(tensor='chi3 C-dom', params=(-1/8.,  1/16., 0.,   0.,    -15/16.))
align_tensor.init(tensor='chi4 C-dom', params=(7/16., -7/8.,  0.,   9/16.,  0.))
align_tensor.init(tensor='chi5 C-dom', params=(-1/2., -1/2.,  3/8., 0.,     0.))

# Set the domain the tensors correspond to.
n_state_model.set_domain(tensor='chi1 C-dom', domain='C')
n_state_model.set_domain(tensor='chi2 C-dom', domain='C')
n_state_model.set_domain(tensor='chi3 C-dom', domain='C')
n_state_model.set_domain(tensor='chi4 C-dom', domain='C')
n_state_model.set_domain(tensor='chi5 C-dom', domain='C')

# Set that they are non-reduced tensors. 
n_state_model.set_type(tensor='chi1 C-dom', red=False)
n_state_model.set_type(tensor='chi2 C-dom', red=False)
n_state_model.set_type(tensor='chi3 C-dom', red=False)
n_state_model.set_type(tensor='chi4 C-dom', red=False)
n_state_model.set_type(tensor='chi5 C-dom', red=False)

# Calculate the singular values.
align_tensor.svd(basis_set=0, tensors=['chi1 C-dom', 'chi2 C-dom', 'chi3 C-dom', 'chi4 C-dom', 'chi5 C-dom'])
align_tensor.svd(basis_set=1, tensors=['chi1 C-dom', 'chi2 C-dom', 'chi3 C-dom', 'chi4 C-dom', 'chi5 C-dom'])

# Calculate the angles between the matrices.
align_tensor.matrix_angles(basis_set=0, tensors=['chi1 C-dom', 'chi2 C-dom', 'chi3 C-dom', 'chi4 C-dom', 'chi5 C-dom'])
align_tensor.matrix_angles(basis_set=1, tensors=['chi1 C-dom', 'chi2 C-dom', 'chi3 C-dom', 'chi4 C-dom', 'chi5 C-dom'])


# Load the N-terminal alignment tensors.
align_tensor.init(tensor='chi1 N-dom', params=(1/4.,   -1/2.,   0.,              3/4.,   0.))
align_tensor.init(tensor='chi2 N-dom', params=(7/16.,  -7/8.,   0.,              9/16.,  0.))
align_tensor.init(tensor='chi3 N-dom', params=(-1/32.,  1/16., -15/(16*sqrt(2)), 3/32., -15/(16*sqrt(2))))
align_tensor.init(tensor='chi4 N-dom', params=(1.,     -7/8.,   0.,              0.,     0.))
align_tensor.init(tensor='chi5 N-dom', params=(1/4.,   -1/2.,   3/(8*sqrt(2)),   3/4.,  -3/(8*sqrt(2))))

# Set the domain the tensors correspond to.
n_state_model.set_domain(tensor='chi1 N-dom', domain='N')
n_state_model.set_domain(tensor='chi2 N-dom', domain='N')
n_state_model.set_domain(tensor='chi3 N-dom', domain='N')
n_state_model.set_domain(tensor='chi4 N-dom', domain='N')
n_state_model.set_domain(tensor='chi5 N-dom', domain='N')

# Set that they are non-reduced tensors. 
n_state_model.set_type(tensor='chi1 N-dom', red=True)
n_state_model.set_type(tensor='chi2 N-dom', red=True)
n_state_model.set_type(tensor='chi3 N-dom', red=True)
n_state_model.set_type(tensor='chi4 N-dom', red=True)
n_state_model.set_type(tensor='chi5 N-dom', red=True)

# Calculate the singular values.
align_tensor.svd(basis_set=0, tensors=['chi1 N-dom', 'chi2 N-dom', 'chi3 N-dom', 'chi4 N-dom', 'chi5 N-dom'])
align_tensor.svd(basis_set=1, tensors=['chi1 N-dom', 'chi2 N-dom', 'chi3 N-dom', 'chi4 N-dom', 'chi5 N-dom'])

# Calculate the angles between the matrices.
align_tensor.matrix_angles(basis_set=0, tensors=['chi1 N-dom', 'chi2 N-dom', 'chi3 N-dom', 'chi4 N-dom', 'chi5 N-dom'])
align_tensor.matrix_angles(basis_set=1, tensors=['chi1 N-dom', 'chi2 N-dom', 'chi3 N-dom', 'chi4 N-dom', 'chi5 N-dom'])

# Set up the 5-state model.
n_state_model.model(N=3)

# Grid search.
grid_search(inc=2)

# Minimise.
minimise('simplex')

# Finish.
#results.write(file='devnull', force=1)
