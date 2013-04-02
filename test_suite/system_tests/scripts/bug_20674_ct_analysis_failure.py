# Script for catching bug #20674 (https://gna.org/bugs/index.php?20674).

# Python module imports.
from os import sep
import sys

# relax module imports.
from status import Status; status = Status()


# Create the run.
name = 'consistency'
pipe.create(name, 'ct')

# The data directory.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'consistency_testing'+sep+'bug_20674_ct_analysis_failure'

# Load the PDB file.
structure.read_pdb(file='2QFK_MONOMERHabc5.pdb', dir=path, read_mol=None, set_mol_name=None, read_model=None, set_model_num=None)

# Set up the 15N and 1H spins (both backbone and Trp indole sidechains).
structure.load_spins('@N', ave_pos=True)
structure.load_spins('@H', ave_pos=True)
spin.isotope('15N', spin_id='@N')
spin.isotope('1H', spin_id='@H')

# Load the relaxation data.
bruker.read(ri_id='r1_700', file='T1 dhp 700.txt', dir=path)
bruker.read(ri_id='r2_700', file='T2 dhp 700.txt', dir=path)
bruker.read(ri_id='noe_700', file='NOE dhp 700.txt', dir=path)

# Define the magnetic dipole-dipole relaxation interaction.
dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
dipole_pair.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)

# Define the chemical shift relaxation interaction.
value.set(val=-172 * 1e-6, param='csa')

# Set the angle between the 15N-1H vector and the principal axis of the 15N chemical shift tensor
value.set(val=15.7, param='orientation')

# Set the approximate correlation time.
value.set(val=13 * 1e-9, param='tc')

# Set the frequency.
consistency_tests.set_frq(frq=700.17 * 1e6)

# Consistency tests.
calc()

# Monte Carlo simulations.
monte_carlo.setup(number=10)
monte_carlo.create_data()
calc()
monte_carlo.error_analysis()

# Create grace files.
grace.write(y_data_type='j0', file='devnull', force=True)
grace.write(y_data_type='f_eta', file='devnull', force=True)
grace.write(y_data_type='f_r2', file='devnull', force=True)

# Finish.
results.write(file='devnull', force=True)
state.save('devnull')
