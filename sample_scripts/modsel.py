# Script for model-free model selection of the models m1, m2, m3, m4, and m5.

# Nuclei type
nuclei('N')

# Set the run names.
runs = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']

# Loop over the run names.
for run in runs:
    print "\n\n# " + run + " #"

    # Create the run.
    run.create(run, 'mf')

    # Reload precalculated results from the file 'm1/results', etc.
    results.read(run=run, file='results', dir=run)

# Model selection.
eliminate()
run.create('aic', 'mf')
model_selection('AIC', 'aic')

# Write the results.
state.save('save', force=1)
results.write(run='aic', file='results', force=1)

