###############################################################################
#                                                                             #
# Copyright (C) 2015 Troels E. Linnet                                         #
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
import os
from scipy.io import loadmat
import numpy as np

# relax module imports.
from status import Status; status = Status()

# Set path
cwd  = status.install_path+os.sep+'test_suite'+os.sep+'shared_data'+os.sep+'dispersion'+os.sep+'Paul_Schanda_2015_Nov'
outdir = status.outdir + os.sep

fields = [600, 950]
file_names = ['residues', 'rates', 'errorbars_rate', 'RFfields']

# Store data in dictionary
all_data = {}
all_data['fields'] = fields
all_data['file_names'] = file_names

# Make list of residues and make unique
all_res = []

# Loop over the experiments, collect all data
for field in fields:
    print("%s"%field,)

    # Make a dic inside
    all_data['%s'%field] = {}

    # Construct the path to the data
    path = cwd + os.sep

    # Collect all filename paths
    field_file_name_paths = []
    for file_name in file_names:
        # Create path name
        file_name_path = path + "%s_%s.mat"%(field, file_name)
        field_file_name_paths.append(file_name_path)

        # Load the data
        file_name_path_data = loadmat(file_name_path)
        # Extract as numpy
        file_name_path_data_np = file_name_path_data[file_name]
        # And store
        all_data['%s'%field]['%s'%file_name] = file_name_path_data
        all_data['%s'%field]['np_%s'%file_name] = file_name_path_data_np

        print(file_name, file_name_path_data_np.shape)

        # Collect residues
        if file_name == "residues":
            all_res += list(file_name_path_data_np.flatten())

    # Store
    all_data['%s'%field]['field_file_name_paths'] = field_file_name_paths


# Make list of residues and make unique
all_res_uniq = sorted(list(set(all_res)))
all_data['all_res_uniq'] = all_res_uniq

# Write a sequence file for relax
f = open(outdir + "residues.txt", "w")
f.write("# Residue_i\n")
for res in all_res_uniq:
    f.write("%s\n"%res)
f.close()

f_exp = open(outdir + "exp_settings.txt", "w")
f_exp.write("# sfrq_MHz RFfield_kHz file_name\n")

# Then write the files for the rates
k = 1
for field in all_data['fields']:
    resis = all_data['%s'%field]['np_residues'][0]
    rates = all_data['%s'%field]['np_rates']
    errorbars_rate = all_data['%s'%field]['np_errorbars_rate']
    RFfields = all_data['%s'%field]['np_RFfields'][0]

    print("\nfield: %3.3f"%field)
    for i, RF_field_strength_kHz in enumerate(RFfields):
        #print "RF_field_strength_kHz: %3.3f"%RF_field_strength_kHz
        # Generate file name
        f_name = outdir + "sfrq_%i_MHz_RFfield_%1.3f_kHz_%03d.in"%(field, RF_field_strength_kHz, k)
        cur_file = open(f_name, "w")
        cur_file.write("# resi rate        rate_err\n")

        exp_string = "%11.7f %11.7f %s\n"%(field, RF_field_strength_kHz, f_name)
        print("%s"%exp_string,)
        f_exp.write(exp_string)

        for j, resi in enumerate(resis):
            rate = rates[j, i]
            error = errorbars_rate[j, i]
            string = "%4d %11.7f %11.7f\n"%(resi, rate, error)
            cur_file.write(string)

        cur_file.close()
        k += 1

f_exp.close()