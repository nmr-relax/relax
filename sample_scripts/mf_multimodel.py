# Script for model-free analysis.

# Set the run names (also the names of preset model-free models).
#runs = ['tm1', 'tm2', 'tm3', 'tm4', 'tm5', 'tm6', 'tm7', 'tm8', 'tm9']
runs = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']

# Nuclei type
nuclei('N')

for name in runs:
    # Create the run.
    run.create(name, 'mf')

    # Load the sequence.
    sequence.read(name, 'noe.500.out')

    # Load a PDB file.
    #pdb(name, 'example.pdb')

    # Load the relaxation data.
    relax_data.read(name, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
    relax_data.read(name, 'R2', '600', 600.0 * 1e6, 'r2.600.out')
    relax_data.read(name, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')
    relax_data.read(name, 'R1', '500', 500.0 * 1e6, 'r1.500.out')
    relax_data.read(name, 'R2', '500', 500.0 * 1e6, 'r2.500.out')
    relax_data.read(name, 'NOE', '500', 500.0 * 1e6, 'noe.500.out')

    # Setup other values.
    diffusion_tensor.set(name, 1e-8, fixed=1)
    #diffusion_tensor.set(name, (1e-8, 1.0, 60, 290), param_types=0, spheroid_type='oblate', fixed=0)
    value.set(name, 1.02 * 1e-10, 'bond_length')
    value.set(name, -160 * 1e-6, 'csa')
    #value.set(name, 0.970, 's2')
    #value.set(name, 1.0, 's2f')
    #value.set(name, 2048e-12, 'te')
    #value.set(name, 2048e-12, 'tf')
    #value.set(name, 2048e-12, 'ts')
    #value.set(name, 0.149/(2*pi*600e6)**2, 'rex')

    # Select the model-free model.
    model_free.select_model(run=name, model=name)
    #fix(name, 'all_res')

    # Minimise.
    grid_search(name, inc=11)
    minimise('newton', run=name)

    # Write the results.
    results.write(run=name, file='results', force=1)

# Save the program state.
state.save('save', force=1)
