# Script for model-free model selection of the models m1, m2, m3, m4, and m5.

# Load the sequence.
read.sequence('noe.500.out')

# Set the run names.
runs = ['m1', 'm2', 'm3', 'm4', 'm5']

# Loop over the run names.
for run in runs:
    print "\n\n# " + run + " #"

    # Load the relaxation data.
    read.relax_data(run, 'R1', '600', 600.0 * 1e6, 'r1.600.out')
    read.relax_data(run, 'R2', '600', 600.0 * 1e6, 'r2.600.out')
    read.relax_data(run, 'NOE', '600', 600.0 * 1e6, 'noe.600.out')
    read.relax_data(run, 'R1', '500', 500.0 * 1e6, 'r1.500.out')
    read.relax_data(run, 'R2', '500', 500.0 * 1e6, 'r2.500.out')
    read.relax_data(run, 'NOE', '500', 500.0 * 1e6, 'noe.500.out')

    # Reload precalculated results from the file 'm1/results', etc.
    read.read_data(run=run, data_type='mf', file='results', dir=run)

# Model selection.
model_selection('AIC', 'aic')

# Write the results.
write(run='aic', file='results', force=1)

