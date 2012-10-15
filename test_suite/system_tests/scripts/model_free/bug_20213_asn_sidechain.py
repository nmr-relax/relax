# Python module imports.
from os import sep
from time import asctime, localtime

# relax module imports.
from auto_analyses.dauvergne_protocol import dAuvergne_protocol
from data import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Analysis variables.
#####################

# The diffusion model.
DIFF_MODEL = 'local_tm'

# The model-free models.  Do not change these unless absolutely necessary, the protocol is likely to fail if these are changed.
MF_MODELS = ['m0', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']
LOCAL_TM_MODELS = ['tm0']

# The grid search size (the number of increments per dimension).
GRID_INC = 2

# The optimisation technique.
MIN_ALGOR = 'simplex'

# The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
MC_NUM = 3

# Automatic looping over all rounds until convergence (must be a boolean value of True or False).
CONV_LOOP = True



# Set up the data pipe.
#######################

# Create the data pipe.
pipe_bundle = "mf (%s)" % asctime(localtime())
name = "origin - " + pipe_bundle
pipe.create(name, 'mf', bundle=pipe_bundle)

# The data path.
data_path = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'model_free' + sep + 'bug_20213_asn_sidechain' + sep

# Load PDB file
structure.read_pdb(file='./1U06-H_trunc.pdb', dir=data_path, read_mol=1, set_mol_name=None, read_model=None, set_model_num=None, parser='internal')

# Set up spins and isotopes
structure.load_spins(spin_id=':47@N*', ave_pos=True)
structure.load_spins(spin_id=':47@H*', ave_pos=True)
spin.isotope(isotope='15N', spin_id='@N*', force=True)
spin.isotope(isotope='1H', spin_id='@H*', force=True)
spin.element(element='N', spin_id=':*@N*', force=True)
spin.element(element='H', spin_id=':*@H*', force=True)

# Load relaxation files
relax_data.read(ri_id='R1_600',  ri_type='R1',  frq=600.17991*1e6, file='./600/rx_t1.out', dir=data_path, spin_id_col=None, mol_name_col=None, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7, sep=None, spin_id=None)
relax_data.read(ri_id='R2_600',  ri_type='R2',  frq=600.17991*1e6, file='./600/rx_t2.out', dir=data_path, spin_id_col=None, mol_name_col=None, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7, sep=None, spin_id=None)
relax_data.read(ri_id='NOE_600', ri_type='NOE', frq=600.17991*1e6, file='./600/600_noe.out', dir=data_path, spin_id_col=None, mol_name_col=None, res_num_col=1, res_name_col=2, spin_num_col=None, spin_name_col=5, data_col=3, error_col=4, sep=None, spin_id=None)

relax_data.read(ri_id='R1_750',  ri_type='R1',  frq=750.04990*1e6, file='./750/rx_t1.out', dir=data_path, spin_id_col=None, mol_name_col=None, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7, sep=None, spin_id=None)
relax_data.read(ri_id='R2_750',  ri_type='R2',  frq=750.04990*1e6, file='./750/rx_t2.out', dir=data_path, spin_id_col=None, mol_name_col=None, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7, sep=None, spin_id=None)
relax_data.read(ri_id='NOE_750', ri_type='NOE', frq=750.04990*1e6, file='./750/750_noe.out', dir=data_path, spin_id_col=None, mol_name_col=None, res_num_col=1, res_name_col=2, spin_num_col=None, spin_name_col=5, data_col=3, error_col=4, sep=None, spin_id=None)

# Define the magnetic dipole-dipole relaxation interaction.
dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
dipole_pair.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02e-10)
dipole_pair.unit_vectors(ave=True)

# Define the chemical shift relaxation interaction.
value.set(val=-0.000172, param='csa', spin_id=None)



# Execution.
############

# The results dir.
if not hasattr(ds, 'tmpdir'):
    results_dir = status.install_path + sep + 'dauvergne_protocol'
else:
    results_dir = ds.tmpdir

# Change some opt params.
dAuvergne_protocol.opt_func_tol = 1e-5
dAuvergne_protocol.opt_max_iterations = 1000

# Do not change!
dAuvergne_protocol(pipe_name=name, pipe_bundle=pipe_bundle, results_dir=results_dir, diff_model=DIFF_MODEL, mf_models=MF_MODELS, local_tm_models=LOCAL_TM_MODELS, grid_inc=GRID_INC, min_algor=MIN_ALGOR, mc_sim_num=MC_NUM, conv_loop=CONV_LOOP)
