import os
import scipy as sc
import scipy.io
import numpy as np

# Set path
cwd = os.getcwd()
outdir = cwd + os.sep + "Paul_Schanda_2015_Nov"

if not os.path.exists(outdir):
    os.makedirs(outdir)

fields = [600, 950]
file_names = ['rates', 'errorbars_rate', 'RFfields']

resi_sel = [12, 51]

# Loop over the experiments, collect all data
for field in fields:
    print "\n", field

    # Construct the path to the data
    path = cwd + os.sep + "Archive" + os.sep + "exp_%s"%field + os.sep + "matrices" + os.sep

    resi_file_name='residues'
    # Load the resis
    resi_file_name_path = path + "%s.mat"%resi_file_name
    # Load the data
    resi_file_name_path_data = sc.io.loadmat(resi_file_name_path)
    # Extract as numpy
    resi_file_name_path_data_np = resi_file_name_path_data[resi_file_name]

    resi_indexes = []
    for resi in resi_sel:
        index = np.where(resi_file_name_path_data_np[0]==resi)[0][0]
        resi_indexes.append(index)

    resi_trunc = resi_file_name_path_data_np[:, resi_indexes]
    resi_trunc_dict = resi_file_name_path_data
    resi_trunc_dict[resi_file_name] = resi_trunc
    resi_file_out = outdir + os.sep + "%s_residues.mat"%field
    scipy.io.savemat(resi_file_out, resi_trunc_dict)

    for file_name in file_names:
        # Create path name
        file_name_path = path + "%s.mat"%file_name

        # Load the data
        file_name_path_data = sc.io.loadmat(file_name_path)
        # Extract as numpy
        file_name_path_data_np = file_name_path_data[file_name]

        if file_name in file_names[:2]:
            data_trunc = file_name_path_data_np[resi_indexes, :]
        else:
            data_trunc = file_name_path_data_np

        data_trunc_dic = file_name_path_data
        data_trunc_dic[file_name] = data_trunc
        file_out = outdir + os.sep + "%s_%s.mat"%(field, file_name)
        scipy.io.savemat(file_out, data_trunc_dic)
