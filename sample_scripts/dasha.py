# Script for model-free analysis using the program Dasha.

# Set the data pipe names (also the names of preset model-free models).
#pipes = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']
pipes = ['m1', 'm2', 'm3', 'm4', 'm5']

# Nuclei type
value.set('15N', 'heteronucleus')

# Loop over the pipes.
for name in pipes:
    # Create the data pipe.
    pipe.create(name, 'mf')

    # Load the sequence.
    sequence.read('noe.500.out', res_num_col=1)

    # Load a PDB file.
    #structure.read_pdb('example.pdb')

    # Load the relaxation data.
    relax_data.read('R1', '600', 600.0 * 1e6, 'r1.600.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read('R2', '600', 600.0 * 1e6, 'r2.600.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read('NOE', '600', 600.0 * 1e6, 'noe.600.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read('R1', '500', 500.0 * 1e6, 'r1.500.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read('R2', '500', 500.0 * 1e6, 'r2.500.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read('NOE', '500', 500.0 * 1e6, 'noe.500.out', res_num_col=1, data_col=3, error_col=4)

    # Setup other values.
    diffusion_tensor.init(10e-9, fixed=1)
    #diffusion_tensor.init((10e-9, 0, 0, 40, 30, 80), fixed=1)
    value.set(1.02 * 1e-10, 'bond_length')
    value.set(-172 * 1e-6, 'csa')

    # Select the model-free model.
    model_free.select_model(model=name)

    # Create the Dasha script.
    dasha.create(algor='NR', force=True)

    # Execute Dasha.
    dasha.execute()

    # Read the data.
    dasha.extract()

    # Write the results.
    results.write(file='results_dasha', force=True)
