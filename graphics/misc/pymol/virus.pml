###############################################################################
#                                                                             #
# Copyright (C) 2011,2017 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Add a pseudoatom for the origin of the colour ramp.
pseudoatom orig, pos=(0,0,0), label=origin
 
# Download and create the capsid structure file from the PDB.
fetch 1rhi, async=0, type=pdb1
split_states 1rhi
delete 1rhi
 
# Hide everything.
hide all

# Show all as a surface.
as surface
#show spheres
 
# Create a colour ramp for the capsid.
ramp_new proximityRamp, orig, selection=(1rhi*), range=[140, 170], color=[[0, 0, 0.42], white]
 
# Set the colour.
set surface_color, proximityRamp, (1rhi*)
#set sphere_color, proximityRamp, (1rhi*)

# No clipping.
clip slab, 1000
 
# Set the zoom.
zoom center, 250

# White background
bg_color white

# Centre the molecule.
center
