# Script for model-free analysis using the program 'Modelfree4'.

# Load the sequence.
read.sequence('noe.500.out')

# Nuclei type
nuclei('N')


# Initial model-free minimisation stage.
########################################

# Set the run name (also the name of a preset model-free model).
runs = ['m3', 'm4', 'm5']
#runs = ['m1', 'm2', 'm3', 'm4', 'm5']

# Loop over the runs.
for run in runs:
    print "\n\n# " + run + " #"

    # Load the relaxation data.
    read.relax_data(run, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
    read.relax_data(run, 'R2', '600', 600.0 * 1e6, 'r2.600.out')
    read.relax_data(run, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')
    read.relax_data(run, 'R1', '500', 500.0 * 1e6, 'r1.500.out')
    read.relax_data(run, 'R2', '500', 500.0 * 1e6, 'r2.500.out')
    read.relax_data(run, 'NOE', '500', 500.0 * 1e6, 'noe.500.out')

    # Setup other values.
    diffusion_tensor(run, 1e-8)
    value.set(run, 'bond_length', 1.02 * 1e-10)
    value.set(run, 'csa', -160 * 1e-6)

    # Select the model-free model.
    model.select_mf(run=run, model=run)

    # Create the Modelfree4 files.
    palmer.create(run=run, force=1, sims=0)

    # Run Modelfree4.
    palmer.execute(run=run, force=1)

    # Extract the Modelfree4 data from the 'mfout' file.
    palmer.extract(run=run)


# Second model-free model selection stage.
##########################################

# Model selection.
model_selection('AIC', 'aic')


# Final model-free minimisation stage with diffusion tensor optimisation.
#########################################################################



# Finish.
#########

write(run='aic', file='results', force=1)
state.save('save', force=1)
