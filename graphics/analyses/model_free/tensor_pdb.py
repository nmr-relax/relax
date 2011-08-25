from time import sleep


# Create the data pipe.
pipe.create("ellipsoid", "mf")

# Load the PDB file.
structure.read_pdb("2I5O_trunc.pdb")

# Set up and then display the diffusion tensor.
diffusion_tensor.init((9e-9, 1e7, 0.5, 0, 90, 90))

# Create the tensor PDB file.
tensor_file = "ellipsoid.pdb"
structure.create_diff_tensor_pdb(file=tensor_file, scale=1e-6, force=True)

# PyMOL.
########

# Launch PyMOL.
pymol.view()

# Display the protein as a cartoon.
pymol.cartoon()

# Select the backbone H and N atoms, and display as sticks.
pymol.command("select bb, (name n,h)")
pymol.command("cmd.show('sticks', 'bb')")
pymol.command("util.cnc('bb',_self=cmd)")

# Select and display the zinc.
pymol.command("select name Zn")
pymol.command("cmd.show('spheres', 'sele')")
pymol.command("cmd.color(8, 'sele')")

# Set the view angle.
pymol.command("set_view (\
     0.757250905,    0.343928099,   -0.555234432,\
    -0.653088510,    0.389927387,   -0.649175942,\
    -0.006769199,    0.854205370,    0.519887865,\
    -0.000007369,    0.000006240, -107.869674683,\
    -1.294937849,   -4.170322418,   -0.788913548,\
    74.625320435,  141.113739014,  -20.000000000 )")

# Display the diffusion tensor.
pymol.tensor_pdb(file=tensor_file)

# Set the background to white.
pymol.command("bg_color bluewhite")

# Ray-trace.
pymol.command("ray 2000,2000")

# Wait a while.
sleep(10)

# Dump to a PNG.
pymol.command("png pymol_image.png")
