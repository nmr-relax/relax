# Script for determining populations for lactose conformations using RDCs and PCSs.

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Path of the files.
str_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'dna'
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'missing_data'

# Create the data pipe.
pipe.create('missing_data_test', 'N-state')

# Load the structure.
structure.read_pdb(file='LE_trunc.pdb', dir=str_path, set_mol_name='LE')

# Load the sequence information.
structure.load_spins(spin_id='@C*', ave_pos=False)
structure.load_spins(spin_id='@H*', ave_pos=False)

# Load the CH vectors for the C atoms.
structure.vectors(spin_id='@C*', attached='H*', ave=False)

# Set the values needed to calculate the dipolar constant.
value.set(1.10 * 1e-10, 'r', spin_id="@C*")
value.set('13C', 'heteronuc_type', spin_id="@C*")
value.set('1H', 'proton_type', spin_id="@C*")

# File list.
align_list = ['Dy', 'Tb', 'Tm', 'Er']

# Load the RDCs and PCSs.
for i in xrange(len(align_list)):
    # The RDC.
    if i != 1:
        rdc.read(align_id=align_list[i], file='missing_rdc_%i' % i, dir=data_path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=None, spin_name_col=5, data_col=6, error_col=None)
        rdc.display(align_id=align_list[i])

    # The PCS.
    if i != 2:
        pcs.read(align_id=align_list[i], file='missing_pcs_%i' % i, dir=data_path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=None, spin_name_col=5, data_col=6, error_col=None)
        pcs.display(align_id=align_list[i])

    # The temperature.
    temperature(id=align_list[i], temp=298)

    # The frequency.
    frq.set(id=align_list[i], frq=799.75376122 * 1e6)

# Set the paramagnetic centre.
paramag.centre([1, 2, -30])

# Set up the model.
n_state_model.select_model(model='fixed')

# Minimisation.
minimise('bfgs', constraints=True)

# Write out a results file.
results.write('devnull', force=True)

# Show the tensors.
align_tensor.display()
