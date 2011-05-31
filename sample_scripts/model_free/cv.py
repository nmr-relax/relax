###############################################################################
#                                                                             #
# Copyright (C) 2003-2011 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

"""Script for model-free analysis using cross-validation model selection."""


# Initialise data structures.
ri_ids = ['R1_600', 'R2_600', 'NOE_600', 'R1_500', 'R2_500', 'NOE_500']
ri_types = ['R1', 'R2', 'NOE', 'R1', 'R2', 'NOE']
frqs = [600.0 * 1e6, 600.0 * 1e6, 600.0 * 1e6, 500.0 * 1e6, 500.0 * 1e6, 500.0 * 1e6]
file_names = ['r1.600.out', 'r2.600.out', 'noe.600.out', 'r1.500.out', 'r2.500.out', 'noe.500.out']
pipes = ['m1', 'm2', 'm3', 'm4', 'm5']

# Construct the CV pipes.
cv_pipes = []
for i in xrange(len(pipes)):
    cv_pipes.append([])
    for j in xrange(len(ri_ids)):
        cv_pipes[i].append(pipes[i] + "_" + ri_ids[j])

print("\n\n\n\n")
print("# Calibration set.")
print("##################")
print("\n")

# Loop over the pipes for single-item-out cross-validation.
for i in xrange(len(pipes)):
    # Loop over the relaxation data.
    for j in xrange(len(ri_ids)):
        # Nuclei type
        nuclei('N')

        # Create the data pipe.
        pipe.create(cv_pipes[i][j], 'mf')

        # Load the sequence.
        sequence.read('noe.500.out', res_num_col=1)

        # Create the calibration set by loading all relaxation data except the index 'i'.
        for k in xrange(len(ri_ids)):
            if k == i:
                continue
            relax_data.read(ri_ids[k], ri_types[k], frqs[k], file_names[k])

        # Set up the global rotational correlation time.
        diffusion_tensor.init(1e-8)

        # Set the bond length and CSA values.
        value.set(1.02 * 1e-10, 'bond_length')
        value.set(-172 * 1e-6, 'csa')

        # Select the preset model-free models.
        model_free.select_model(model=pipes[i])

        # Minimisation of the calibration set.
        grid_search(inc=11)
        minimise('newton', 'chol')

        # Write the results.
        results.write(force=True)


print("\n\n\n\n")
print("# Validation set.")
print("#################")
print("\n")

# Load all the pipes.
for i in xrange(len(pipes)):
    # Loop over the relaxation data.
    for j in xrange(len(ri_ids)):
        # Switch to the relevent data pipe.
        pipe.switch(cv_pipes[i][j])

        # Delete the relaxation data from the calibration set.
        delete(data_type='relax_data')

        # Create the validation set by loading the relaxation data excluded from the calibration set.
        relax_data.read(ri_ids[j], ri_types[j], frqs[j], file_names[j])

        # Reload the model-free results.
        read.results(data_type='mf')

        # Calculate the chi-squared value for the validation set.
        calc()


print("\n\n\n\n")
print("# Model selection.")
print("##################")
print("\n")

model_selection('CV', 'cv', cv_pipes)


print("\n\n\n\n")
print("# Final minimisation using all relaxation data.")
print("###############################################")
print("\n")

# Switch to the 'cv' data pipe.
pipe.switch('cv')

# Delete the relaxation data copied over to the 'cv' data pipe and then load all the data.
delete(data_type='relax_data')
for i in xrange(len(ri_ids)):
    relax_data.read(ri_ids[i], ri_types[i], frqs[i], file_names[i])

# Minimise the selected model using all relaxation data.
minimise('newton')

# Finish.
results.write(file='results', force=True)
state.save('save', force=True)
