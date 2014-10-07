# Python imports
from os import getcwd, sep
from numpy import array, float64, zeros

# relax module imports.
from lib.io import open_write_file
from pipe_control.mol_res_spin import display_spin, generate_spin_string, return_spin

# Variables
prev_data_path = getcwd()
result_dir = None
result_filename = 'FT_-_TSMFK01_-_min_-_128_-_free_spins.bz2'

# Create pipe
pipe.create('relax_disp', 'relax_disp')

# Read data in
results.read(prev_data_path + sep + result_filename)

# Get residue of interest. L61 is 
cur_spin_id = ":%i@%s"%(61, 'N')
cur_spin_id_str = cur_spin_id .replace('#', '_').replace(':', '_').replace('@', '_')

# Get the spin container.
cur_spin = return_spin(cur_spin_id)

# Get the chi2 value
pre_chi2 = cur_spin.chi2

# Define dx.map settings.
dx_inc = 20
dx_params = ['dw', 'k_AB', 'r2a']

dx_point_clustered_min = [cur_spin.dw, cur_spin.k_AB, cur_spin.r2a['SQ CPMG - 499.86214000 MHz']]

print("Params for dx map is")
print(dx_params)
print("Point param for dx map is, with chi2=%3.3f"%pre_chi2)
print(dx_point_clustered_min)

# Define file_names.
cur_model = 'TSMFK01'
file_name_map = "%s_map%s" % (cur_model, cur_spin_id_str)
file_name_point = "%s_point%s" % (cur_model, cur_spin_id_str)

# Set bounds
lower = [0.0, 0.0, 5.0]
upper = [20.0, 6.0, 15.0]
dx.map(params=dx_params, map_type='Iso3D', spin_id=cur_spin_id, inc=dx_inc, lower=lower, upper=upper, axis_incs=10, file_prefix=file_name_map, dir=result_dir, point=dx_point_clustered_min, point_file=file_name_point)

print("Params for dx map is")
print(dx_params)
print("Point param for dx map is, with chi2=%3.3f"%pre_chi2)
print(dx_point_clustered_min)
