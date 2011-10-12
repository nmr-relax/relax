"""Script for testing the lanthanide position optimisation using RDCs and PCSs."""

# Python module imports.
from os import sep
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes
from relax_errors import RelaxError
from status import Status; status = Status()


# Set up.
NUM_STR = 3
SIMS = False

# Path of the alignment data and structure.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'metal_pos_opt'
STRUCT_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'

# Create the data pipe.
pipe.create('Ln3+ opt', 'N-state')

# Load the structures.
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
paramag.centre([ -14.845,    0.969,    0.265])

# File list.
align_list = ['Dy', 'Tb', 'Tm', 'Er']

# Set the tensors.
align_tensor.init(tensor=align_list[0], params=( 1.42219822168827662867e-04, -1.44543001566521341940e-04, -7.07796211648713973798e-04, -6.01619494082773244303e-04,  2.02008007072950861996e-04), param_types=2)
align_tensor.init(tensor=align_list[1], params=( 3.56720663040924505435e-04, -2.68385787902088840916e-04, -1.69361406642305853832e-04,  1.71873715515064501074e-04, -3.05790155096090983822e-04), param_types=2)
align_tensor.init(tensor=align_list[2], params=( 2.32088908680377300801e-07,  2.08076808579168379617e-06, -2.21735465435989729223e-06, -3.74311563209448033818e-06, -2.40784858070560310370e-06), param_types=2)
align_tensor.init(tensor=align_list[3], params=(-2.62495279588228071048e-04,  7.35617367964106275147e-04,  6.39754192258981332648e-05,  6.27880171180572523460e-05,  2.01197582457700226708e-04), param_types=2)

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

    # Calculate.
    calc()

    # Check that the chi2 is zero!
    if cdp.chi2 > 1e-15:
        print "Chi2: %s" % cdp.chi2
        raise RelaxError("The chi2 value must be zero here!")

    # Minimisation.
    minimise('newton', constraints=False, max_iter=500)

    # Fix the tensor.
    align_tensor.fix(id=align_list[i])

# Print out.
print "\n\n"
print "##############################"
print "# Ln3+ position optimisation #"
print "##############################\n\n\n"

# Exact position check.
paramag.centre(fix=False)
calc()
if cdp.chi2 > 1e-15:
    print "Chi2: %s" % cdp.chi2
    raise RelaxError("The chi2 value must be zero here!")

# Shift the metal.
print("\nShifting the Ln3+ position.")
print("Original position: [%.3f, %.3f, %.3f]" % (cdp.paramagnetic_centre[0], cdp.paramagnetic_centre[1], cdp.paramagnetic_centre[2]))
cdp.paramagnetic_centre[0] = cdp.paramagnetic_centre[0] + 0.02
print("Shifted position:  [%.3f, %.3f, %.3f]\n" % (cdp.paramagnetic_centre[0], cdp.paramagnetic_centre[1], cdp.paramagnetic_centre[2]))
calc()
if cdp.chi2 < 1e-15:
    print "Chi2: %s" % cdp.chi2
    raise RelaxError("The chi2 value cannot be zero here!")

# Optimise the Ln3+ position.
x, y, z = cdp.paramagnetic_centre
minimise('simplex', constraints=False, max_iter=500)

# Check that the metal moved.
print("\nOriginal position: [%.3f, %.3f, %.3f]" % (x, y, z))
print("New position:      [%.3f, %.3f, %.3f]\n" % (cdp.paramagnetic_centre[0], cdp.paramagnetic_centre[1], cdp.paramagnetic_centre[2]))
if "%.3f" % x == "%.3f" % cdp.paramagnetic_centre[0] and "%.3f" % y == "%.3f" % cdp.paramagnetic_centre[1] and "%.3f" % z == "%.3f" % cdp.paramagnetic_centre[2]:
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
    minimise('newton', constraints=False, max_iter=500)
    align_tensor.fix(id=align_list[i], fixed=True)

# Print out.
print "\n\n"
print "#######################"
print "# Global optimisation #"
print "#######################\n\n\n"

# Optimise everything.
align_tensor.fix(fixed=False)
paramag.centre(fix=False)
minimise('simplex', constraints=False, max_iter=50)

# Monte Carlo simulations.
if SIMS:
    monte_carlo.setup(3)
    monte_carlo.create_data()
    monte_carlo.initial_values()
    minimise('simplex', constraints=False, max_iter=500)
    monte_carlo.error_analysis()

# Write out a results file.
results.write('devnull', force=True)

# Print the contents of the current data pipe (for debugging Q-values).
print(cdp)
rdc.calc_q_factors()
pcs.calc_q_factors()
print(cdp)
