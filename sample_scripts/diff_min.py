# Script for model-free analysis.

# Set the data pipe names (also the names of preset model-free models).
#pipes = ['m1']
pipes = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']

# Nuclei type
value.set('15N', 'heteronucleus')

# Minimise the model-free parameters.
print("\n\n\n\n\n")
print("#####################################")
print("# Minimising model-free parameters. #")
print("#####################################")
print("\n\n\n")

for name in pipes:
    # Create the data pipe.
    pipe.create(name, 'mf')

    # Load the sequence.
    sequence.read('noe.500.out', res_num_col=1)

    # Load a PDB file.
    structure.read_pdb('example.pdb')

    # Load the relaxation data.
    relax_data.read('R1', '600', 600.0 * 1e6, 'r1.600.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read('R2', '600', 600.0 * 1e6, 'r2.600.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read('NOE', '600', 600.0 * 1e6, 'noe.600.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read('R1', '500', 500.0 * 1e6, 'r1.500.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read('R2', '500', 500.0 * 1e6, 'r2.500.out', res_num_col=1, data_col=3, error_col=4)
    relax_data.read('NOE', '500', 500.0 * 1e6, 'noe.500.out', res_num_col=1, data_col=3, error_col=4)

    # Setup other values.
    diffusion_tensor.init((1e-8, 1.0, 60, 290), param_types=1, spheroid_type='oblate', fixed=1)
    value.set(1.02 * 1e-10, 'bond_length')
    value.set(-172 * 1e-6, 'csa')

    # Select the model-free model.
    model_free.select_model(model=name)

    # Minimise.
    grid_search(inc=5)
    minimise('newton')

# Minimise the diffusion tensor parameters.
print("\n\n\n\n\n")
print("###########################################")
print("# Minimising diffusion tensor parameters. #")
print("###########################################")
print("\n\n\n")

# Loop over the data pipes.
for name in pipes:
    # Switch to the data pipe.
    pipe.switch(name)

    # Unfix the diffusion tensor.
    fix('diff', fixed=0)

    # Fix all model-free paremeter values.
    fix('all_res')

    # Minimise.
    grid_search(inc=5)
    minimise('newton', max_iter=5000)

    # Write the results.
    results.write(file='results', force=True)

# Save the program state.
state.save('save', force=True)
