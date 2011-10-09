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
