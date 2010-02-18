"""Script for testing the fitting an alignment tensor to RDCs or PCSs."""

# Python module imports.
from os import sep
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes


# Path of the alignment data and structure.
DATA_PATH = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'CaM'
STRUCT_PATH = sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures'

# Create the data pipe.
pipe.create('rdc', 'N-state')

# Set the mode, if not specified by the system test.
if not hasattr(ds, 'mode'):
    ds.mode = 'all'

# The data to use.
if hasattr(ds, 'rand') and ds.rand:
    rdc_file = 'synth_rdc_rand'
    pcs_file = 'synth_pcs_rand'
else:
    rdc_file = 'synth_rdc'
    pcs_file = 'synth_pcs'

# Load the CaM structure.
structure.read_pdb(file='bax_C_1J7P_N_H_Ca', dir=STRUCT_PATH)

# Load the spins.
structure.load_spins()

# Load the NH vectors.
structure.vectors(spin_id='@N', attached='H', ave=False)

# Set the values needed to calculate the dipolar constant.
value.set(1.041 * 1e-10, 'bond_length', spin_id="@N")
value.set('15N', 'heteronucleus', spin_id="@N")
value.set('1H', 'proton', spin_id="@N")

# RDCs.
if ds.mode in ['rdc', 'all']:
    rdc.read(align_id='synth', file=rdc_file, dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6)

# PCSs.
if ds.mode in ['pcs', 'all']:
    pcs.read(align_id='synth', file=pcs_file, dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6)

    # Set the paramagnetic centre.
    pcs.centre(atom_id=':1000@CA')

    # The temperature.
    temperature(id='synth', temp=303)

    # The frequency.
    frq.set(id='synth', frq=600.0 * 1e6)

# Set up the model.
n_state_model.select_model(model='fixed')

# Set the tensor elements.
#cdp.align_tensors[0].Axx = -0.351261/2000
#cdp.align_tensors[0].Ayy = 0.556994/2000
#cdp.align_tensors[0].Axy = -0.506392/2000
#cdp.align_tensors[0].Axz = 0.560544/2000
#cdp.align_tensors[0].Ayz = -0.286367/2000

# Minimisation.
grid_search(inc=3)
minimise('simplex', constraints=False, max_iter=500)

# Write out a results file.
results.write('devnull', force=True)

# Show the tensors.
align_tensor.display()

# Print the contents of the current data pipe (for debugging Q-values).
print(cdp)
print((cdp.align_tensors[0]))
