# Script for model-free analysis.

# Load the sequence.
read.sequence('noe.500.out')

# Set the run names (also the names of preset model-free models).
runs = ['m1', 'm2', 'm3', 'm4', 'm5']

for i in range(len(runs)):
    # Load the relaxation data.
    read.relax_data(runs[i], 'R1', '600', 600.0 * 1e6, 'r1.600.out')
    read.relax_data(runs[i], 'R2', '600', 600.0 * 1e6, 'r2.600.out')
    read.relax_data(runs[i], 'NOE', '600', 600.0 * 1e6, 'noe.600.out')
    read.relax_data(runs[i], 'R1', '500', 500.0 * 1e6, 'r1.500.out')
    read.relax_data(runs[i], 'R2', '500', 500.0 * 1e6, 'r2.500.out')
    read.relax_data(runs[i], 'NOE', '500', 500.0 * 1e6, 'noe.500.out')

    # Setup other values.
    diffusion_tensor(runs[i], 'iso', 1e-8)
    value.set(runs[i], 'bond_length', 1.02 * 1e-10)
    value.set(runs[i], 'csa', -160 * 1e-6)

    # Select the model-free model.
    model.select_mf(runs[i], runs[i])

    # Minimise.
    grid_search(runs[i], inc=11)
    minimise('newton', 'eigen', run=runs[i])

    # Print results.
    write(run=runs[i], file='results', force=1)

# Save the program state.
state.save('save', force=1)
