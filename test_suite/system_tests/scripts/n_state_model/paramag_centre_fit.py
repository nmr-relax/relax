"""Script for testing the fitting of the paramagnetic centre of the PCSs."""

# Python module imports.
import __main__
from os import sep
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes


# Path of the alignment data and structure.
DATA_PATH = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'CaM'
STRUCT_PATH = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

# Create the data pipe.
pipe.create('para_centre', 'N-state')

# Set the mode, if not specified by the system test.
if not hasattr(ds, 'mode'):
    ds.mode = 'all'

# The data to use.
rdc_file = 'synth_rdc'
pcs_file = 'synth_pcs'

# Load the CaM structure.
structure.read_pdb(file='bax_C_1J7P_N_H_Ca', dir=STRUCT_PATH)

# Load the spins.
structure.load_spins()

# Deselect most spins (to speed things up).
deselect.spin()
select.spin(":83")
select.spin(":84")
select.spin(":85")
select.spin(":111")
select.spin(":130")
select.spin(":131")
select.spin(":132")
select.spin(":148")

# Load the NH vectors.
structure.vectors(spin_id='@N', attached='H', ave=False)

# Set the values needed to calculate the dipolar constant.
value.set(1.041 * 1e-10, 'bond_length', spin_id="@N")
value.set('15N', 'heteronucleus', spin_id="@N")
value.set('1H', 'proton', spin_id="@N")

# RDCs.
if ds.mode == 'all':
    rdc.read(align_id='synth', file=rdc_file, dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6)

# PCSs.
pcs.read(align_id='synth', file=pcs_file, dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6)

# The temperature.
temperature(id='synth', temp=303)

# The frequency.
frq.set(id='synth', frq=600.0 * 1e6)

# Set up the model.
n_state_model.select_model(model='fixed')

# Paramagnetic centre optimisation
real_pos = [32.555, -19.130, 27.775]

#paramag.centre([  32.555,  -19.130,   27.775], fix=False)
paramag.centre([ 32, -19, 28], fix=False)

# Set the tensor elements.
cdp.align_tensors[0].Axx = -0.351261/2000
cdp.align_tensors[0].Ayy = 0.556994/2000
cdp.align_tensors[0].Axy = -0.506392/2000
cdp.align_tensors[0].Axz = 0.560544/2000
cdp.align_tensors[0].Ayz = -0.286367/2000
print cdp.align_tensors[0].A

#cdp.align_tensors[0].Axx = 0.0
#cdp.align_tensors[0].Ayy = 0.0
#cdp.align_tensors[0].Axy = 0.0
#cdp.align_tensors[0].Axz = 0.0
#cdp.align_tensors[0].Ayz = 0.0

# Minimisation.
#grid_search(inc=6)
minimise('simplex', constraints=False, max_iter=500)
#calc()

print cdp.align_tensors[0].A

# Write out a results file.
results.write('devnull', force=True)

## Show the tensors.
#align_tensor.display()
#
# Print out
print("A:\n" % cdp.align_tensors[0])
print("centre: %s" % cdp.paramagnetic_centre)
print("centre diff: %s" % (cdp.paramagnetic_centre - real_pos))
print("chi2: %s" % cdp.chi2)

# Map.
#dx.map(params=['paramag_x', 'paramag_y', 'paramag_z'], inc=10, lower=[30, -20, 26], upper=[33, -18, 30])
print cdp
