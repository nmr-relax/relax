name = 'spheroid'
run.create(name, 'mf')
pdb(name, "Ap4Aase_new_3.pdb")
diffusion_tensor.init(name, (1.698e7, 1.417e7, 67.174, -83.718), param_types=3)
angles(name)
