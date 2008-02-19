name = 'spheroid'
pipe.create(name, 'mf')
structure.read_pdb("Ap4Aase_new_3.pdb")
diffusion_tensor.init((1.698e7, 1.417e7, 67.174, -83.718), param_types=3)
angles()
