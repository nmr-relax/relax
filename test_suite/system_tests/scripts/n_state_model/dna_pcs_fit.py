# Script for performing a PCS analysis.

# Python module imports.
import __main__
from os import sep

# relax imports.
from data import Relax_data_store; ds = Relax_data_store()


# Path of the files.
str_path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'dna'
data_path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'pcs_data'

# Create the data pipe.
pipe.create('DNA', 'N-state')

# Load the structure.
structure.read_pdb(file='LE.pdb', dir=str_path)

# Load the sequence information.
structure.load_spins(spin_id='@H*')

# The PCS.
pcs.read(align_id='Dy', file='LE_dna', dir=data_path, res_num_col=2, res_name_col=3, spin_name_col=5, data_col=6, error_col=None)
pcs.display(align_id='Dy')

# The temperature.
temperature(id='Dy', temp=298)

# The frequency.
frq.set(id='Dy', frq=799.75376122 * 1e6)

# The paramagnetic centre location.
if ds.para_centre == 'true':
    pcs.centre(pos=[25.8279, -11.6382, -2.5931])
elif ds.para_centre == 'zero':
    pcs.centre(pos=[0, 0, 0])

# Set up the model.
n_state_model.select_model(model='fixed')

 # Minimisation.
minimise('simplex', scaling=False, constraints=False)

# Show the tensors.
align_tensor.display()
