# Script for model-free analysis.

# Create the run.
name = 'm1'
create_run(name, 'mf')

# Nuclei type
nuclei('N')

# Load the sequence.
sequence.read(name, 'noe.500.out')

# Load a PDB file.
#pdb(name, 'example.pdb')
#vectors(name)

# Load the relaxation data.
relax_data.read(name, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
relax_data.read(name, 'R2', '600', 600.0 * 1e6, 'r2.600.out')
relax_data.read(name, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')
relax_data.read(name, 'R1', '500', 500.0 * 1e6, 'r1.500.out')
relax_data.read(name, 'R2', '500', 500.0 * 1e6, 'r2.500.out')
relax_data.read(name, 'NOE', '500', 500.0 * 1e6, 'noe.500.out')

# Setup other values.
diffusion_tensor.set(name, 1e-8, fixed=1)
#diffusion_tensor.set(name, (1e-8, 1.0, 60, 290), param_types=1, axial_type='oblate', fixed=1)
#diffusion_tensor.set(name, (1.340e7, 1.516e7, 1.691e7, -82.027, -80.573, 65.568), fixed=0)
value.set(name, 1.02 * 1e-10, 'bond_length')
value.set(name, -160 * 1e-6, 'csa')

# Select the model-free model.
model_free.select_model(run=name, model=name)
#model_free.create_model(run=name, model=name, equation='mf_ext2', params=['S2f', 'S2s', 'ts'])

# Fixed value.
#fix(name, 'all_res')

# Grid search.
#grid_search(name, inc=5)
value.set(name)

# Minimise.
#minimise('newton', run=name, constraints=1, max_iter=500)
minimise('bfgs', run=name, constraints=0)

# Finish.
eliminate()
write(run=name, file='results', force=1)
state.save('save', force=1)
