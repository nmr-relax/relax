# Script for model-free analysis.

# Set the run names (also the names of preset model-free models).
runs = ['m1']
#runs = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']

# Nuclei type
nuclei('N')

# Minimise the model-free parameters.
print "\n\n\n\n\n"
print "#####################################"
print "# Minimising model-free parameters. #"
print "#####################################"
print "\n\n\n"

for run in runs:
    # Create the run.
    run.create(run, 'mf')

    # Load the sequence.
    sequence.read(run, 'noe.500.out')

    # Load a PDB file.
    pdb(run, 'example.pdb')

    # Load the relaxation data.
    relax_data.read(run, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
    relax_data.read(run, 'R2', '600', 600.0 * 1e6, 'r2.600.out')
    relax_data.read(run, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')
    relax_data.read(run, 'R1', '500', 500.0 * 1e6, 'r1.500.out')
    relax_data.read(run, 'R2', '500', 500.0 * 1e6, 'r2.500.out')
    relax_data.read(run, 'NOE', '500', 500.0 * 1e6, 'noe.500.out')

    # Setup other values.
    diffusion_tensor.set(run, (1e-8, 1.0, 60, 290), param_types=1, axial_type='oblate', fixed=1)
    value.set(run, 1.02 * 1e-10, 'bond_length')
    value.set(run, -160 * 1e-6, 'csa')

    # Select the model-free model.
    model_free.select_model(run=run, model=run)

    # Minimise.
    grid_search(run, inc=5)
    minimise('newton', run=run)

# Minimise the diffusion tensor parameters.
print "\n\n\n\n\n"
print "###########################################"
print "# Minimising diffusion tensor parameters. #"
print "###########################################"
print "\n\n\n"

for run in runs:
    # Unfix the diffusion tensor.
    fix(run, 'diff', fixed=0)

    # Fix all model-free paremeter values.
    fix(run, 'all_res')

    # Minimise.
    grid_search(run, inc=5)
    minimise('newton', run=run, max_iter=5000)

    # Write the results.
    results.write(run=run, file='results', force=1)

# Save the program state.
state.save('save', force=1)
