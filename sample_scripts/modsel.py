# Script for model-free model selection.

# Nuclei type
nuclei('N')

# Set the run names.
runs = ['m0', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']

# Loop over the run names.
for name in runs:
    print "\n\n# " + name + " #"

    # Create the run.
    pipe.create(name, 'mf')

    # Reload precalculated results from the file 'm1/results', etc.
    results.read(run=name, file='results', dir=name)

# Model elimination.
eliminate()

# Model selection.
pipe.create('aic', 'mf')
model_selection('AIC', 'aic')

# Write the results.
state.save('save', force=1)
results.write(run='aic', file='results', force=1)

