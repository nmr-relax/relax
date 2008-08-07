# Script for creating a PDB representation of the Brownian rotational diffusion tensor.

# Create the data pipe.
name = 'sims'
pipe.create(name, 'mf')

# Read the results.
results.read(dir=None)

# Display the diffusion tensor.
diffusion_tensor.display()

# Create the tensor PDB file.
tensor_file = 'tensor.pdb'
structure.create_diff_tensor_pdb(file=tensor_file, force=True)

# PyMOL.
pymol.view()
pymol.cartoon()
pymol.tensor_pdb(file=tensor_file)
