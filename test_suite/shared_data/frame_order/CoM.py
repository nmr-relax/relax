# Script for determining the centre of mass of the reference structures.
# The CoM is not the real one as only the N, H, and Ca2+ atoms are used.

# relax module imports.
from generic_fns.structure.mass import centre_of_mass


# The PDB files.
files = [
    '1J7O_1st_NH.pdb',
    '1J7P_1st_NH.pdb',
    '1J7P_1st_NH_rot.pdb'
]

# Loop over each PDB file.
for name in files:
    # Create a separate data pipe for each.
    pipe.create(name, 'N-state')

    # Load the file.
    structure.read_pdb(name)

    # Calculate the CoM.
    centre_of_mass()
