"""Sample script demonstrating the use of the N-state model of domain motions.

Author:  Edward d'Auvergne
Last updated:  20/11/2007

The N-state model uses alignment tensors as determined by RDC data to determine N-states in rotational space, each associated with a given probability or weight.
"""

# Create the data pipe.
name = 'CaM'
pipe.create(name, 'N-state')
