# Script for creating a PDB representation of the Brownian rotational diffusion tensor.

# Create the run.
name = 'sims'
run.create(name, 'mf')

# Read the results.
results.read(name, dir=None)

# Display the diffusion tensor.
diffusion_tensor.display(name)

# Create the tensor PDB file.
tensor_file = 'tensor.pdb'
structure.create_diff_tensor_pdb(name, file=tensor_file, force=1)

# PyMOL.
pymol.view(name)
pymol.cartoon(name)
pymol.tensor_pdb(name, file=tensor_file)
