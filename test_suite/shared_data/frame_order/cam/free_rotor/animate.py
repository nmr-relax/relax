# Script for creating an animation of the model and results.


# Load the frame order results.
state.load('frame_order')

# Launch PyMOL.
pymol.view()

# The cone representation.
pymol.cone_pdb('cone.pdb')

# View all.
pymol.command('zoom')

# Load the distribution of structures.
pymol.command('load distribution.pdb.gz')

# Structure display.
pymol.command('hide everything, 1J7O_1st_NH')
pymol.command('hide everything, 1J7P_1st_NH_rot')
pymol.command('hide everything, distribution')
pymol.command('show spheres, 1J7O_1st_NH')
pymol.command('show spheres, 1J7P_1st_NH_rot')
pymol.command('show sticks, distribution')
pymol.command('color firebrick, 1J7P_1st_NH_rot and n. N')
pymol.command('color salmon, 1J7P_1st_NH_rot and n. H')

# Animate.
pymol.command('cmd.mplay()')

# Load the original domain position.
pymol.command('load ../1J7P_1st_NH.pdb')
pymol.command('hide everything, 1J7P_1st_NH')
pymol.command('show spheres, 1J7P_1st_NH')
