# Script for model-free analysis using the program Dasha.

# Set the run names (also the names of preset model-free models).
#runs = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']
runs = ['m1', 'm2', 'm3', 'm4', 'm5']

# Nuclei type
nuclei('N')

# Loop over the runs.
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
    diffusion_tensor.init(name, 10e-9, fixed=1)
    #diffusion_tensor.init(name, (10e-9, 0, 0, 40, 30, 80), fixed=1)
    value.set(name, 1.02 * 1e-10, 'bond_length')
    value.set(name, -172 * 1e-6, 'csa')

    # Select the model-free model.
    model_free.select_model(run=name, model=name)

    # Create the Dasha script.
    dasha.create(name, algor='NR', force=1)

    # Execute Dasha.
    dasha.execute(name)

    # Read the data.
    dasha.extract(name)

    # Write the results.
    results.write(name, file='results_dasha', force=1)
