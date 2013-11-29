"""Script for removing data from the truncated CPMG data for testing purposes.""" 

# relax module imports.
from pipe_control.mol_res_spin import return_spin


# Create a data pipe.
pipe.create('missing', 'relax_disp')

# Read the base data pipe.
results.read('base_pipe')

# Delete all data with the following keys for spin :4.
spin_4 = return_spin(":4")
keys = ['500_733.33.in', '800_600.in', '800_400.in']
for key in keys:
    spin_4.intensities.pop(key)
    spin_4.intensity_err.pop(key)

# Delete all 800 MHz data for the spin :71.
spin_71 = return_spin(":71")
keys = ['800_reference.in', '800_66.667.in', '800_133.33.in', '800_133.33.in.bis', '800_200.in', '800_266.67.in', '800_333.33.in', '800_400.in', '800_466.67.in', '800_533.33.in', '800_533.33.in.bis', '800_600.in', '800_666.67.in', '800_733.33.in', '800_800.in', '800_866.67.in', '800_933.33.in', '800_933.33.in.bis', '800_1000.in']
for key in keys:
    spin_71.intensities.pop(key)
    spin_71.intensity_err.pop(key)

# Write out the missing data pipe.
results.write('missing_data_pipe', dir=None, force=True)
