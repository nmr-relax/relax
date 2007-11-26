"""Sample script demonstrating the use of the N-state model of domain motions.

Author:  Edward d'Auvergne
Last updated:  26/11/2007

The N-state model uses alignment tensors as determined by RDC data to determine N-states in rotational space, each associated with a given probability or weight.
"""

# Create the data pipe.
name = 'CaM'
pipe.create(name, 'N-state')

# Load the alignment tensor.
align_tensor.init(params=(-8.6322e-05, -5.5786e-04, -3.1732e-05, 2.2927e-05, 2.8599e-04), param_types=1)
align_tensor.init(params=(3.5e-06, 1.8e-05, 9.2e-06, 1.7e-06, 6.4e-05), param_types=1, errors=1)
