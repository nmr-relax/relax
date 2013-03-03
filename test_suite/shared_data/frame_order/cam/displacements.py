"""Script to determine the displacements of 1J7P_1st_NH_rot_trans to the original structure."""

# Create a data pipe.
pipe.create('displacements', 'N-state')

# Load the structures as models.
structure.read_pdb('1J7P_1st_NH_rot_trans.pdb', set_mol_name='N-dom', set_model_num=1)
structure.read_pdb('1J7P_1st_NH.pdb', set_mol_name='N-dom', set_model_num=2)

# Calculate the displacements.
structure.superimpose(method='fit to first')
