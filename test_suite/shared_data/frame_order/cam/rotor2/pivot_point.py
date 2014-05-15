# Create a PDB representation for the real pivot point used to generate the data.

# relax module imports.
from lib.io import open_write_file
from lib.structure.internal.object import Internal


# Create the structural object.
structure = Internal()

# Add a molecule.
structure.add_molecule(name='piv')

# Alias the single molecule from the single model.
mol = structure.structural_data[0].mol[0]

# Add the original pivot.
mol.atom_add(atom_name='N', res_name='PIV', res_num=1, pos=[ 37.254, 0.5, 16.7465], element='N')

# Add the shifted pivot.
mol.atom_add(atom_name='N', res_name='SFT', res_num=2, pos=[ 38.968163825736738,   2.6192628972111,   13.499077238576398], element='N')

# Save as a PDB file.
file = open_write_file('pivot_point.pdb', force=True)
structure.write_pdb(file)
file.close()


