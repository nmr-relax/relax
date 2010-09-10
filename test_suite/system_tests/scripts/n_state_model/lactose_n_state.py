# Script for determining populations for lactose conformations using RDCs and PCSs.

# Python module imports.
import __main__
from os import sep
import sys

# relax imports.
from data import Relax_data_store; ds = Relax_data_store()
from specific_fns.setup import n_state_model_obj


# Path of the files.
str_path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'
data_path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'

# Create the data pipe.
pipe.create('lactose', 'N-state')

# The population model for free operation of this script.
if not hasattr(ds, 'model'):
    ds.model = 'population'

# Load the structures.
NUM_STR = 4
for i in range(NUM_STR):
    structure.read_pdb(file='lactose_MCMM4_S1_'+repr(i+1), dir=str_path, parser='internal', set_model_num=i+1, set_mol_name='lactose_MCMM4_S1')

# Load the sequence information.
structure.load_spins(spin_id=':UNK@C*', combine_models=False, ave_pos=False)
structure.load_spins(spin_id=':UNK@H*', combine_models=False, ave_pos=False)

# Deselect the CH2 protons (the rotation of these doesn't work in the model, but the carbon doesn't move).
deselect.spin(spin_id=':UNK@H6')
deselect.spin(spin_id=':UNK@H7')
deselect.spin(spin_id=':UNK@H17')
deselect.spin(spin_id=':UNK@H18')

# Load the CH vectors for the C atoms.
structure.vectors(spin_id='@C*', attached='H*', ave=False)

# Set the values needed to calculate the dipolar constant.
value.set(1.10 * 1e-10, 'bond_length', spin_id="@C*")
value.set('13C', 'heteronucleus', spin_id="@C*")
value.set('1H', 'proton', spin_id="@C*")

# File list.
align_list = ['Dy', 'Tb', 'Tm', 'Er']

# Load the RDCs and PCSs.
for i in xrange(len(align_list)):
    # The RDC.
    rdc.read(align_id=align_list[i], file='rdc.txt', dir=data_path, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=1, data_col=i+3, error_col=None)
    rdc.read(align_id=align_list[i], file='rdc_err.txt', dir=data_path, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=1, data_col=None, error_col=i+3)
    rdc.display(align_id=align_list[i])

    # The PCS.
    pcs.read(align_id=align_list[i], file='pcs.txt', dir=data_path, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=1, data_col=i+2, error_col=None)
    pcs.read(align_id=align_list[i], file='pcs_err.txt', dir=data_path, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=1, data_col=None, error_col=i+2)
    pcs.display(align_id=align_list[i])

    # The temperature.
    temperature(id=align_list[i], temp=298)

    # The frequency.
    frq.set(id=align_list[i], frq=900.015 * 1e6)

# Create a data pipe for the aligned tag structures.
pipe.create('tag', 'N-state')

# Load all the tag structures.
NUM_TAG = 10
for i in range(NUM_TAG):
    structure.read_pdb(file='tag_MCMM4_'+repr(i+1), dir=str_path, parser='internal', set_model_num=i+1, set_mol_name='tag')

# Load the lanthanide atoms.
structure.load_spins(spin_id='@C1', combine_models=False, ave_pos=False)

# Switch back to the main analysis data pipe.
pipe.switch('lactose')

# Calculate the paramagnetic centre (from the structures in the 'tag' data pipe).
paramag.centre(atom_id=':4@C1', pipe='tag')

# Set up the model.
n_state_model.select_model(model=ds.model)

# Set to equal probabilities.
if ds.model == 'population':
    for j in xrange(NUM_STR):
        value.set(1.0/NUM_STR, 'p'+repr(j))

# Minimisation.
minimise('bfgs', constraints=True, max_iter=5)

# Calculate the AIC value.
k, n, chi2 = n_state_model_obj.model_statistics()
ds[ds.current_pipe].aic = chi2 + 2.0*k

# Write out a results file.
results.write('devnull', force=True)

# Show the tensors.
align_tensor.display()
