# Script for determining populations for lactose conformations using RDCs and PCSs.

# Python module imports.
import __main__
from os import sep

# relax module imports.
from relax_errors import RelaxError
from specific_fns.setup import n_state_model_obj

# Path of the files.
str_path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'lactose'
data_path = __main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'+sep+'population_model'

# Create the data pipe.
pipe.create('populations', 'N-state')

# Load the structures.
NUM_STR = 3
i = 1
for model in [1, 3, 2]:
    structure.read_pdb(file='lactose_MCMM4_S1_%i.pdb' % i, dir=str_path, set_model_num=model, set_mol_name='LE')
    i += 1

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
paramag.centre([ -14.845,    0.969,    0.265])


# The solution.
###############

# Set up the model.
n_state_model.select_model(model='population')
print n_state_model_obj._assemble_param_vector()

# Set pc to the exact values.
value.set(0.3, 'p0')
value.set(0.1, 'p2')
value.set(0.6, 'p1')

# Set the tensors.
align_tensor.init(tensor=align_list[0], params=( 1.42219822168827662867e-04, -1.44543001566521341940e-04, -7.07796211648713973798e-04, -6.01619494082773244303e-04,  2.02008007072950861996e-04), param_types=2)
align_tensor.init(tensor=align_list[1], params=( 3.56720663040924505435e-04, -2.68385787902088840916e-04, -1.69361406642305853832e-04,  1.71873715515064501074e-04, -3.05790155096090983822e-04), param_types=2)
align_tensor.init(tensor=align_list[2], params=( 2.32088908680377300801e-07,  2.08076808579168379617e-06, -2.21735465435989729223e-06, -3.74311563209448033818e-06, -2.40784858070560310370e-06), param_types=2)
align_tensor.init(tensor=align_list[3], params=(-2.62495279588228071048e-04,  7.35617367964106275147e-04,  6.39754192258981332648e-05,  6.27880171180572523460e-05,  2.01197582457700226708e-04), param_types=2)
print n_state_model_obj._assemble_param_vector()

# Calculation.
print cdp
print cdp.mol[0].res[0].spin[0]
calc()
print("Chi2: %s" % cdp.chi2)
if abs(cdp.chi2) > 1e-15:
    raise RelaxError, "The chi2 at the solution is not zero!"


# The population model opt.
###########################

# Minimisation.
minimise('sd', func_tol=1e-2)
print cdp

# Write out a results file.
results.write('devnull', force=True)
