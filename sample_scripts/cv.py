# Script for model-free analysis using cross-validation model selection.

# Initialise data structures.
ri_labels = ['R1', 'R2', 'NOE', 'R1', 'R2', 'NOE']
frq_labels = ['600', '600', '600', '500', '500', '500']
frqs = [600.0 * 1e6, 600.0 * 1e6, 600.0 * 1e6, 500.0 * 1e6, 500.0 * 1e6, 500.0 * 1e6]
file_names = ['r1.600.out', 'r2.600.out', 'noe.600.out', 'r1.500.out', 'r2.500.out', 'noe.500.out']
runs = ['m1', 'm2', 'm3', 'm4', 'm5']
cv_runs = []
for i in range(len(ri_labels)):
    cv_runs.append([])
    for j in range(len(runs)):
        cv_runs[i].append(runs[j] + "_" + ri_labels[i] + "_" + frq_labels[i])

# Load the sequence.
read.sequence('noe.500.out')

# Precalculated flag.
precalc = 1


print "\n\n\n\n"
print "# Calibration set."
print "##################"
print "\n"

if not precalc:
    # Loop over the relaxation data for single-item-out cross-validation.
    for i in range(len(ri_labels)):
        # Loop over the preset model-free models 1 to 5.
        for j in range(len(cv_runs[i])):
            # Create the calibration set by loading all relaxation data except the index 'i'.
            for k in range(len(ri_labels)):
                if k == i:
                    continue
                read.rx_data(cv_runs[i][j], ri_labels[k], frq_labels[k], frqs[k], file_names[k])

            # Set up the global rotational correlation time.
            diffusion_tensor(cv_runs[i][j], 'iso', 1e-8)

            # Set the bond length and CSA values.
            value.set(cv_runs[i][j], 'bond_length', 1.02 * 1e-10)
            value.set(cv_runs[i][j], 'csa', -160 * 1e-6)

            # Select the preset model-free models.
            model.select_mf(run=cv_runs[i][j], model=runs[j])

            # Minimisation of the calibration set.
            grid_search(cv_runs[i][j], inc=11)
            minimise('newton', 'chol', run=cv_runs[i][j])

            # Write the results.
            write(run=cv_runs[i][j], force=1)


print "\n\n\n\n"
print "# Validation set."
print "#################"
print "\n"

# Load all the relaxation data.
for i in range(len(ri_labels)):
    # Loop over the model-free models.
    for j in range(len(cv_runs[i])):
        # Create the validation set by loading the relaxation data excluded from the calibration set.
        read.rx_data(cv_runs[i][j], ri_labels[j], frq_labels[j], frqs[j], file_names[j])

        # Set up the global rotational correlation time.
        diffusion_tensor(cv_runs[i][j], 'iso', 1e-8)

        # Reload the model-free results.
        read.read_data(run=cv_runs[i][j], data_type='mf')

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

# Load all the relaxation data.
for i in range(len(ri_labels)):
    read.rx_data('cv', ri_labels[i], frq_labels[i], frqs[i], file_names[i])

# Set up the global rotational correlation time.
diffusion_tensor('cv', 'iso', 1e-8)

# Minimise the selected model using all relaxation data.
minimise('newton', run='cv')

# Finish.
write(run='cv', file='results', force=1)
state.save('save', force=1)
