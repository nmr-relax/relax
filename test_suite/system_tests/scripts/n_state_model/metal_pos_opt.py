"""Script for testing the lanthanide position optimisation using RDCs and PCSs."""

# Python module imports.
from os import sep
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes
from relax_errors import RelaxError
from status import Status; status = Status()


# Path of the alignment data and structure.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'metal_pos_opt'
STRUCT_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

# Create the data pipe.
pipe.create('Ln3+ opt', 'N-state')

# Load the structures.
NUM_STR = 3
for i in range(1, NUM_STR+1):
    structure.read_pdb(file='lactose_MCMM4_S1_%i.pdb' % i, dir=STRUCT_PATH, set_model_num=i, set_mol_name='LE')

# Load the spins.
structure.load_spins(spin_id=':UNK@C*', ave_pos=False)
structure.load_spins(spin_id=':UNK@H*', ave_pos=False)

# Deselect the CH2 protons (the rotation of these doesn't work in the model, but the carbon doesn't move).
deselect.spin(spin_id=':UNK@H6')
deselect.spin(spin_id=':UNK@H7')
deselect.spin(spin_id=':UNK@H17')
deselect.spin(spin_id=':UNK@H18')

# Load the CH vectors.
structure.vectors(spin_id='@C*', attached='H*', ave=False)

# Set the values needed to calculate the dipolar constant.
value.set(1.10 * 1e-10, 'bond_length', spin_id="@C*")
value.set('13C', 'heteronucleus', spin_id="@C*")
value.set('1H', 'proton', spin_id="@C*")

# Set the paramagnetic centre.
paramag.centre([ -14.8,    0.9,    0.2])

# File list.
align_list = ['Dy', 'Tb', 'Tm', 'Er']

# Load the RDCs and PCSs.
for i in xrange(len(align_list)):
    # The RDC.
    rdc.read(align_id=align_list[i], file='missing_rdc_%i' % i, dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=None, spin_name_col=5, data_col=6, error_col=None)

    # The PCS.
    pcs.read(align_id=align_list[i], file='missing_pcs_%i' % i, dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=None, spin_name_col=5, data_col=6, error_col=None)

    # The temperature.
    temperature(id=align_list[i], temp=298)

    # The frequency.
    frq.set(id=align_list[i], frq=799.75376122 * 1e6)

    # Set up the model.
    n_state_model.select_model('fixed')

    # Minimisation.
    grid_search(inc=3)
    minimise('newton', constraints=False)

    # Fix the tensor.
    align_tensor.fix(id=align_list[i])

# Print out.
print "\n\n"
print "##############################"
print "# Ln3+ position optimisation #"
print "##############################\n\n\n"

# Optimise the Ln3+ position.
x, y, z = cdp.paramagnetic_centre
paramag.centre(fix=False)
minimise('simplex', constraints=False)

# Check that the metal moved.
print("\nOriginal position: [%.3f, %.3f, %.3f]" % (x, y, z))
print("New position:      [%.3f, %.3f, %.3f]\n" % (cdp.paramagnetic_centre[0], cdp.paramagnetic_centre[1], cdp.paramagnetic_centre[2]))
if "%.3f" % x == "%.3f" % cdp.paramagnetic_centre[0] or "%.3f" % y == "%.3f" % cdp.paramagnetic_centre[1] or "%.3f" % z == "%.3f" % cdp.paramagnetic_centre[2]:
    raise RelaxError("The metal position has not been optimised!")

# Print out.
print "\n\n"
print "#######################"
print "# Tensor optimisation #"
print "#######################\n\n\n"

# Optimise each tensor again, one by one.
paramag.centre(fix=True)
for i in xrange(len(align_list)):
    align_tensor.fix(id=align_list[i], fixed=False)
    minimise('newton', constraints=False)
    align_tensor.fix(id=align_list[i], fixed=True)

# Print out.
print "\n\n"
print "#######################"
print "# Global optimisation #"
print "#######################\n\n\n"

# Optimise everything.
align_tensor.fix(fixed=False)
paramag.centre(fix=False)
minimise('simplex', constraints=False)

# Monte Carlo simulations.
monte_carlo.setup(3)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise('simplex', constraints=False, max_iter=500)
monte_carlo.error_analysis()

# Write out a results file.
results.write('devnull', force=True)

# Show the tensors.
align_tensor.display()

# Print the contents of the current data pipe (for debugging Q-values).
print(cdp)
print((cdp.align_tensors[0]))
