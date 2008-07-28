# Script for creating a grace plot of 'S2' vs 'te'.

# Create the run.
name = 'm4'
pipe.create(name, 'mf')

# Load the data.
results.read(name)

# Grace plot.
grace.write(name, x_data_type='s2', y_data_type='te', plot_data='sim', file='s2_te.agr', force=True)

# View the plot.
grace.view(file='s2_te.agr')
