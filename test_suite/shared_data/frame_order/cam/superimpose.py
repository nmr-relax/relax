# Script for superimposing the C-domain structures to convert the pivoted rotation to a translation + CoM rotation.

# Create a data pipe.
pipe.create('superimpose', 'N-state')

# Load the two structures.
structure.read_pdb('1J7P_1st_NH.pdb', set_mol_name='C-dom', set_model_num=1)
structure.read_pdb('1J7P_1st_NH_rot.pdb', set_mol_name='C-dom', set_model_num=2)

# Delete the calciums to match the data pipe CoM (from only 15N and 1H spins).
structure.delete(atom_id='@CA')

# Superimpose.
structure.superimpose(method='fit to first', centre_type='CoM')

# Save the result.
structure.write_pdb('superimpose.pdb', force=True)
