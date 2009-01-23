# System test constructed from Tyler Reddy's bug report at https://gna.org/bugs/?12487.

# Python module imports.
import sys

# Path of the relaxation data.
DATA_PATH = sys.path[-1] + '/test_suite/shared_data/'

# A set of user functions executed by the full_analysis.py script.
pipe.create(pipe_name='ellipsoid', pipe_type='mf') 
results.read(file='tylers_peptide_trunc', dir=DATA_PATH+'results_files')
model_free.remove_tm(spin_id=None)
sequence.display()
structure.read_pdb(file='tylers_peptide_trunc.pdb', dir=DATA_PATH+'structures', parser='scientific')
structure.vectors(attached='H', spin_id=None, verbosity=1, ave=True, unit=True)
diffusion_tensor.init(params=(1e-08, 0, 0, 0, 0, 0), time_scale=1.0, d_scale=1.0, angle_units='deg', param_types=0, spheroid_type=None, fixed=False)
fix(element='all_spins', fixed=True)
grid_search(lower=None, upper=None, inc=6, constraints=True, verbosity=1)
