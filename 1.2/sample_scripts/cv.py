# Script for model-free analysis using cross-validation model selection.

# Initialise data structures.
ri_labels = ['R1', 'R2', 'NOE', 'R1', 'R2', 'NOE']
frq_labels = ['600', '600', '600', '500', '500', '500']
frqs = [600.0 * 1e6, 600.0 * 1e6, 600.0 * 1e6, 500.0 * 1e6, 500.0 * 1e6, 500.0 * 1e6]
file_names = ['r1.600.out', 'r2.600.out', 'noe.600.out', 'r1.500.out', 'r2.500.out', 'noe.500.out']
runs = ['m1', 'm2', 'm3', 'm4', 'm5']

# Construct the CV runs.
cv_runs = []
for i in xrange(len(runs)):
    cv_runs.append([])
    for j in xrange(len(ri_labels)):
        cv_runs[i].append(runs[i] + "_" + ri_labels[j] + "_" + frq_labels[j])

print "\n\n\n\n"
print "# Calibration set."
print "##################"
print "\n"

# Loop over the runs for single-item-out cross-validation.
for i in xrange(len(runs)):
    # Loop over the relaxation data.
    for j in xrange(len(ri_labels)):
        # Nuclei type
        nuclei('N')

        # Create the run.
        run.create(cv_runs[i][j], 'mf')

        # Load the sequence.
        sequence.read(cv_runs[i][j], 'noe.500.out')

        # Create the calibration set by loading all relaxation data except the index 'i'.
        for k in xrange(len(ri_labels)):
            if k == i:
                continue
            relax_data.read(cv_runs[i][j], ri_labels[k], frq_labels[k], frqs[k], file_names[k])

        # Set up the global rotational correlation time.
        diffusion_tensor.init(cv_runs[i][j], 1e-8)

        # Set the bond length and CSA values.
        value.set(cv_runs[i][j], 1.02 * 1e-10, 'bond_length')
        value.set(cv_runs[i][j], -172 * 1e-6, 'csa')

        # Select the preset model-free models.
        model_free.select_model(run=cv_runs[i][j], model=runs[i])

        # Minimisation of the calibration set.
        grid_search(cv_runs[i][j], inc=11)
        minimise('newton', 'chol', run=cv_runs[i][j])

        # Write the results.
        results.write(run=cv_runs[i][j], force=1)


print "\n\n\n\n"
print "# Validation set."
print "#################"
print "\n"

# Load all the runs.
for i in xrange(len(runs)):
    # Loop over the relaxation data.
    for j in xrange(len(ri_labels)):
        # Delete the relaxation data from the calibration set.
        delete(cv_runs[i][j], data_type='relax_data')

        # Create the validation set by loading the relaxation data excluded from the calibration set.
        relax_data.read(cv_runs[i][j], ri_labels[j], frq_labels[j], frqs[j], file_names[j])

        # Reload the model-free results.
        read.results(run=cv_runs[i][j], data_type='mf')

        # Calculate the chi-squared value for the validation set.
        calc(cv_runs[i][j])


print "\n\n\n\n"
print "# Model selection."
print "##################"
print "\n"

model_selection('CV', 'cv', cv_runs)


print "\n\n\n\n"
print "# Final minimisation using all relaxation data."
print "###############################################"
print "\n"

# Delete the relaxation data copied over to the run 'cv' and then load all the data.
delete('cv', data_type='relax_data')
for i in xrange(len(ri_labels)):
    relax_data.read('cv', ri_labels[i], frq_labels[i], frqs[i], file_names[i])

# Minimise the selected model using all relaxation data.
minimise('newton', run='cv')

# Finish.
results.write(run='cv', file='results', force=1)
state.save('save', force=1)
