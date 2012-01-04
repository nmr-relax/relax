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
pipe.create('test', 'N-state')


# Define the two domains.
domain('C')
domain('N')

# Load the C-terminal alignment tensors.
align_tensor.init(tensor='chi1 C-dom', params=(-1/2., -1/2.,  0.,   0.,     0.))
align_tensor.init(tensor='chi2 C-dom', params=(-1/8., -7/8.,  0.,   0.,     0.))
align_tensor.init(tensor='chi3 C-dom', params=(-1/8.,  1/16., 0.,   0.,    -15/16.))
align_tensor.init(tensor='chi4 C-dom', params=(7/16., -7/8.,  0.,   9/16.,  0.))
align_tensor.init(tensor='chi5 C-dom', params=(-1/2., -1/2.,  3/8., 0.,     0.))

# Set the domain the tensors correspond to.
align_tensor.set_domain(tensor='chi1 C-dom', domain='C')
align_tensor.set_domain(tensor='chi2 C-dom', domain='C')
align_tensor.set_domain(tensor='chi3 C-dom', domain='C')
align_tensor.set_domain(tensor='chi4 C-dom', domain='C')
align_tensor.set_domain(tensor='chi5 C-dom', domain='C')

# Calculate the singular values.
align_tensor.svd(basis_set=0, tensors=['chi1 C-dom', 'chi2 C-dom', 'chi3 C-dom', 'chi4 C-dom', 'chi5 C-dom'])
align_tensor.svd(basis_set=1, tensors=['chi1 C-dom', 'chi2 C-dom', 'chi3 C-dom', 'chi4 C-dom', 'chi5 C-dom'])

# Calculate the angles between the matrices.
align_tensor.matrix_angles(basis_set=0, tensors=['chi1 C-dom', 'chi2 C-dom', 'chi3 C-dom', 'chi4 C-dom', 'chi5 C-dom'])
align_tensor.matrix_angles(basis_set=1, tensors=['chi1 C-dom', 'chi2 C-dom', 'chi3 C-dom', 'chi4 C-dom', 'chi5 C-dom'])


# Load the N-terminal alignment tensors.
align_tensor.init(tensor='chi1 N-dom', params=(1/20.*(2-3*sqrt(2)),   -1/2.,   0.,              0.,   0.))
align_tensor.init(tensor='chi2 N-dom', params=(1/80.*(26-9*sqrt(2)),  -7/8.,   0.,              0.,  0.))
align_tensor.init(tensor='chi3 N-dom', params=(-1/160.*(8+3*sqrt(2)),  1/16.,  0.,    0., -3/16.*(1+sqrt(2)+2*cos(pi/8.))))
align_tensor.init(tensor='chi4 N-dom', params=(7/16.,                 -7/8.,   0.,    9/80.*(1+sqrt(2)),     0.))
align_tensor.init(tensor='chi5 N-dom', params=(1/20.*(2-3*sqrt(2)),   -1/2.,   3/40.*(1+sqrt(2)+2*cos(pi/8.)),   0., 0.))

# Set the domain the tensors correspond to.
align_tensor.set_domain(tensor='chi1 N-dom', domain='N')
align_tensor.set_domain(tensor='chi2 N-dom', domain='N')
align_tensor.set_domain(tensor='chi3 N-dom', domain='N')
align_tensor.set_domain(tensor='chi4 N-dom', domain='N')
align_tensor.set_domain(tensor='chi5 N-dom', domain='N')

# Specify the tensor reductions.
align_tensor.reduction(full_tensor='chi1 C-dom', red_tensor='chi1 N-dom')
align_tensor.reduction(full_tensor='chi2 C-dom', red_tensor='chi2 N-dom')
align_tensor.reduction(full_tensor='chi3 C-dom', red_tensor='chi3 N-dom')
align_tensor.reduction(full_tensor='chi4 C-dom', red_tensor='chi4 N-dom')
align_tensor.reduction(full_tensor='chi5 C-dom', red_tensor='chi5 N-dom')

# Calculate the singular values.
align_tensor.svd(basis_set=0, tensors=['chi1 N-dom', 'chi2 N-dom', 'chi3 N-dom', 'chi4 N-dom', 'chi5 N-dom'])
align_tensor.svd(basis_set=1, tensors=['chi1 N-dom', 'chi2 N-dom', 'chi3 N-dom', 'chi4 N-dom', 'chi5 N-dom'])

# Calculate the angles between the matrices.
align_tensor.matrix_angles(basis_set=0, tensors=['chi1 N-dom', 'chi2 N-dom', 'chi3 N-dom', 'chi4 N-dom', 'chi5 N-dom'])
align_tensor.matrix_angles(basis_set=1, tensors=['chi1 N-dom', 'chi2 N-dom', 'chi3 N-dom', 'chi4 N-dom', 'chi5 N-dom'])

# Set up the 5-state model.
n_state_model.select_model(model='2-domain')
n_state_model.number_of_states(N=5)
n_state_model.ref_domain(ref='C')

# Set the initial parameter values to the actual values (the grid search is too expensive).
for i in xrange(5):
    value.set(0.2, 'p'+repr(i))
    value.set(0.0, 'alpha'+repr(i))
    value.set(pi/4-pi/8*i, 'beta'+repr(i))
    value.set(0.0, 'gamma'+repr(i))
#value.set()

# Minimise.
minimise('simplex', constraints=False)

# Centre of mass analysis.
n_state_model.CoM(pivot_point=[0.0, 0.0, 0.0], centre=[0.0, 0.0, 1.0])

# Cone PDBs.
n_state_model.cone_pdb(cone_type='diff on cone', file='devnull', force=True)
n_state_model.cone_pdb(cone_type='diff in cone', file='devnull', force=True)

# Write the results.
results.write(file='devnull')
