###############################################################################
#                                                                             #
# Copyright (C) 2013-2014 Troels E. Linnet                                    #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Python module imports.
from os import getcwd, sep
import re

# relax module imports.
from pipe_control.mol_res_spin import generate_spin_string, return_spin, spin_loop
from specific_analyses.relax_disp.data import generate_r20_key, loop_exp_frq
from specific_analyses.relax_disp.variables import MODEL_R2EFF, MODEL_NOREX_R1RHO_FIT_R1, MODEL_DPL94_FIT_R1, MODEL_TP02_FIT_R1, MODEL_TAP03_FIT_R1, MODEL_MP05_FIT_R1

#########################################
#### Setup
results_dir = getcwd() + sep + 'results_models'

# Load the previous state
state.load(state='final_state.bz2', dir=results_dir)

# Display all pipes
pipe.display()

# Define models which have been analysed.
#MODELS = [MODEL_NOREX_R1RHO_FIT_R1, MODEL_DPL94_FIT_R1, MODEL_TP02_FIT_R1, MODEL_TAP03_FIT_R1, MODEL_MP05_FIT_R1]
MODELS = [MODEL_NOREX_R1RHO_FIT_R1, MODEL_DPL94_FIT_R1]

# Print results for each model.
print("\n################")
print("Printing results")
print("################\n")

# Store all the pipe names.
pipes = []

for model in MODELS:
    # Skip R2eff model.
    if model == MODEL_R2EFF:
        continue

    # Switch to pipe.
    pipe_name = '%s - relax_disp' % (model)
    pipes.append(pipe_name)
    pipe.switch(pipe_name=pipe_name)
    print("\nModel: %s" % (model))

    # Loop over the spins.
    for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
        # Generate spin string.
        spin_string = generate_spin_string(spin=cur_spin, mol_name=mol_name, res_num=resi, res_name=resn)

        # Loop over the parameters.
        print("\nOptimised parameters for spin: %s" % (spin_string))
        for param in cur_spin.params + ['chi2']:
            # Get the value.
            if param in ['r1', 'r2']:
                for exp_type, frq, ei, mi in loop_exp_frq(return_indices=True):
                    # Generate the R20 key.
                    r20_key = generate_r20_key(exp_type=exp_type, frq=frq)

                    # Get the value.
                    value = getattr(cur_spin, param)[r20_key]

                    # Print value.
                    print("%-10s %-6s %-6s %3.8f" % ("Parameter:", param, "Value:", value))

            # For all other parameters.
            else:
                # Get the value.
                value = getattr(cur_spin, param)

                # Print value.
                print("%-10s %-6s %-6s %3.8f" % ("Parameter:", param, "Value:", value))


# Print the final pipe.
pipe.switch(pipe_name='%s - relax_disp' % ('final'))
print("\nFinal pipe")

# Loop over the spins.
for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
    # Generate spin string.
    spin_string = generate_spin_string(spin=cur_spin, mol_name=mol_name, res_num=resi, res_name=resn)

    # Loop over the parameters.
    print("\nOptimised model for spin: %s" % (spin_string))
    param = 'model'

    # Get the value.
    value = getattr(cur_spin, param)
    print("%-10s %-6s %-6s %6s" % ("Parameter:", param, "Value:", value))


# Print the model selection
print("Printing the model selection")
model_selection(method='AIC', modsel_pipe='test', pipes=pipes)
pipe.display()
