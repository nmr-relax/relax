# Script for model-free analysis using the program 'Modelfree4'.

# Load the sequence.
read.sequence('noe.500.out')

# Nuclei type
nuclei('N')

# Set the run name (also the name of a preset model-free model).
runs = ['m1', 'm2', 'm3', 'm4', 'm5']

for i in xrange(len(runs)):
    # Load the relaxation data.
    read.relax_data(runs[i], 'R1', '600', 600.0 * 1e6, 'r1.600.out')
    read.relax_data(runs[i], 'R2', '600', 600.0 * 1e6, 'r2.600.out')
    read.relax_data(runs[i], 'NOE', '600', 600.0 * 1e6, 'noe.600.out')
    read.relax_data(runs[i], 'R1', '500', 500.0 * 1e6, 'r1.500.out')
    read.relax_data(runs[i], 'R2', '500', 500.0 * 1e6, 'r2.500.out')
    read.relax_data(runs[i], 'NOE', '500', 500.0 * 1e6, 'noe.500.out')

    # Setup other values.
    diffusion_tensor(runs[i], 1e-8)
    value.set(runs[i], 'bond_length', 1.02 * 1e-10)
    value.set(runs[i], 'csa', -160 * 1e-6)

    # Select the model-free model.
    model.select_mf(run=runs[i], model=runs[i])

    # Create the Modelfree4 files.
    palmer.create(run=runs[i], force=1, sims=500)

    # Run Modelfree4.
    palmer.execute(run=runs[i], force=1)

state.save('save', force=1)
