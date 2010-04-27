# Script for determining populations for lactose conformations using RDCs and PCSs.

# Python module imports.
import __main__
from os import sep


# Path of the files.
str_path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'
data_path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'population_model'

# Create the data pipe.
pipe.create('populations', 'N-state')

# Load the structures.
for i in range(1, 4):
    structure.read_pdb(file='lactose_MCMM4_S1_%i.pdb' % i, dir=str_path, set_model_num=i, set_mol_name='LE')

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
    rdc.read(align_id=align_list[i], file='missing_rdc_%i' % i, dir=data_path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=None, spin_name_col=5, data_col=6, error_col=None)

    # The PCS.
    pcs.read(align_id=align_list[i], file='missing_pcs_%i' % i, dir=data_path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=None, spin_name_col=5, data_col=6, error_col=None)

    # The temperature.
    temperature(id=align_list[i], temp=298)

    # The frequency.
    frq.set(id=align_list[i], frq=799.75376122 * 1e6)

# Set the paramagnetic centre.
pcs.centre([ -14.845,    0.969,    0.265])

# Set up the model.
n_state_model.select_model(model='fixed')

# Minimisation.
minimise('newton', constraints=True)

# Write out a results file.
results.write('devnull', force=True)

# Switch to the population model.
n_state_model.select_model(model='population')

# Minimisation.
minimise('newton', constraints=True)

# Write out a results file.
results.write('devnull', force=True)
