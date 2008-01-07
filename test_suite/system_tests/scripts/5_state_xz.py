"""A 5-state model in the xz-plane (no pivotting of alpha).

The 5 states correspond to the Euler angles (z-y-z notation):
    State 1:    {0, pi/4, 0}
    State 2:    {0, pi/8, 0}
    State 3:    {0, 0, 0}
    State 4:    {0, -pi/8, 0}
    State 5:    {0, -pi/4, 0}
"""

# Create the data pipe.
pipe.create('C domain', 'N-state')

# Load the C-terminal alignment tensors..
align_tensor.init(tensor='chi1', params=(-1/2., -1/2.,  0.,   0.,     0.))
align_tensor.init(tensor='chi2', params=(-1/8., -7/8.,  0.,   0.,     0.))
align_tensor.init(tensor='chi3', params=(-1/8.,  1/16., 0.,   0.,    -15/16.))
align_tensor.init(tensor='chi4', params=(7/16., -7/8.,  0.,   9/16.,  0.))
align_tensor.init(tensor='chi5', params=(-1/2., -1/2.,  3/8., 0.,     0.))

# Calculate the singular values.
align_tensor.svd(basis_set=0)
align_tensor.svd(basis_set=1)

# Calculate the angles between the matrices.
align_tensor.matrix_angles(basis_set=0)
align_tensor.matrix_angles(basis_set=1)


# Create the data pipe.
pipe.create('N domain', 'N-state')

# Load the N-terminal alignment tensors.
align_tensor.init(tensor='chi1', params=(1/4.,   -1/2.,   0.,              3/4.,   0.))
align_tensor.init(tensor='chi2', params=(7/16.,  -7/8.,   0.,              9/16.,  0.))
align_tensor.init(tensor='chi3', params=(-1/32.,  1/16., -15/(16*sqrt(2)), 3/32., -15/(16*sqrt(2))))
align_tensor.init(tensor='chi4', params=(1.,     -7/8.,   0.,              0.,     0.))
align_tensor.init(tensor='chi5', params=(1/4.,   -1/2.,   3/(8*sqrt(2)),   3/4.,  -3/(8*sqrt(2))))

# Calculate the singular values.
align_tensor.svd(basis_set=0)
align_tensor.svd(basis_set=1)

# Calculate the angles between the matrices.
align_tensor.matrix_angles(basis_set=0)
align_tensor.matrix_angles(basis_set=1)

# Grid search.
minimisation.grid_search(inc=11)

# Minimise.
minimisation.minimise('simplex')

# Finish.
#results.write(file='devnull', force=1)
