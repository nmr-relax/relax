# Script for model-free analysis.

# Load the sequence.
read.sequence('noe.500.out')

# Nuclei type
nuclei('N')

# Set the run names (also the names of preset model-free models).
runs = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9', 'm10', 'm11', 'm12', 'm13', 'm14', 'm15', 'm16', 'm17', 'm18', 'm19', 'm20', 'm21', 'm22', 'm23', 'm24', 'm25', 'm26', 'm27', 'm28', 'm29']

for run in runs:
    # Create the run.
    create_run(run, 'mf')

    # Load a PDB file.
    #pdb('example.pdb')
    #vectors()

    # Load the relaxation data.
    read.relax_data(run, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
    read.relax_data(run, 'R2', '600', 600.0 * 1e6, 'r2.600.out')
    read.relax_data(run, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')
    read.relax_data(run, 'R1', '500', 500.0 * 1e6, 'r1.500.out')
    read.relax_data(run, 'R2', '500', 500.0 * 1e6, 'r2.500.out')
    read.relax_data(run, 'NOE', '500', 500.0 * 1e6, 'noe.500.out')

    # Setup other values.
    diffusion_tensor(run, 1e-8)
    #diffusion_tensor(run, (1e-8, 1.0, 360, 90), param_types=1, axial_type='oblate', fixed=1)
    value.set(run, 'bond_length', 1.02 * 1e-10)
    value.set(run, 'csa', -160 * 1e-6)

    # Select the model-free model.
    model.select_mf(run=run, model=run)

    # Minimise.
    grid_search(run, inc=5)
    minimise('simplex', run=run, max_iter=2000)
    minimise('newton', run=run)

    # Print results.
    write(run=run, file='results', force=1)

# Save the program state.
state.save('save', force=1)
