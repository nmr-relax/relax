"""Script for setting up the data pipe for testing optimisation."""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Create a data pipe.
pipe.create('tm2_grid', 'mf')

# Path of the files.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'tm2_grid'

# Create the sequence.
molecule.create(mol_name='Polycarbonate')
for i in range(3*3*3):
    spin.create(spin_num=1, spin_name='C1', res_num=i+1, res_name='Bisphenol_A', mol_name='Polycarbonate')

# The proton frequencies in MHz.
frq = ['400', '500', '600', '700', '800', '900', '1000']

# Load the relaxation data.
for i in range(len(frq)):
    relax_data.read('NOE', frq[i], float(frq[i])*1e6, 'noe.%s.out' % frq[i], dir=path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
    relax_data.read('R1',  frq[i], float(frq[i])*1e6, 'r1.%s.out' % frq[i],  dir=path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
    relax_data.read('R2',  frq[i], float(frq[i])*1e6, 'r2.%s.out' % frq[i],  dir=path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

# Setup other values.
value.set(1.20 * 1e-10, 'bond_length')
value.set(200 * 1e-6, 'csa')
value.set('13C', 'heteronucleus')
value.set('1H', 'proton')

# Select the model-free model.
model_free.select_model(model='tm2')
