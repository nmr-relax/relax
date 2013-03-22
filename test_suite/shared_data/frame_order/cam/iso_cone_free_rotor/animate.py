# Script for creating an animation of the model and results.

from time import sleep


# Load the frame order results.
state.load('frame_order')

# Launch PyMOL.
pymol.view()
sleep(3)

# The cone representation.
pymol.cone_pdb('cone.pdb')

# Load the distribution of structures.
pymol.command('load distribution.pdb.gz')

# Structure display.
pymol.command('hide everything, 1J7O_1st_NH')
pymol.command('hide everything, 1J7P_1st_NH_rot')
pymol.command('show spheres, 1J7O_1st_NH')
pymol.command('show spheres, 1J7P_1st_NH_rot')
pymol.command('color firebrick, 1J7P_1st_NH_rot and n. N')
pymol.command('color salmon, 1J7P_1st_NH_rot and n. H')

# Animate.
pymol.command('cmd.mplay()')

# Load the original domain position.
pymol.command('load ../1J7P_1st_NH.pdb')
pymol.command('hide everything, 1J7P_1st_NH')
pymol.command('show spheres, 1J7P_1st_NH')

# Load the pivot-CoM axes.
pymol.command('load ../system.pdb')
pymol.command('show sticks, system')
pymol.command('label system, resn')
pymol.command('select sele, system and resi 1')
pymol.command('color blue, sele')
pymol.command('select sele, system and resi 2')
pymol.command('color blue, sele')
pymol.command('select sele, system and resi 3')
pymol.command('color yellow, sele')

# The original rotation axis.
pymol.command('load axis.pdb')
pymol.command('show sticks, axis')
pymol.command('color orange, axis')
pymol.command('select sele, axis and name N')
pymol.command('label sele, resn')

# View all.
pymol.command('zoom')
