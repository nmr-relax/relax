"""Script for testing diffusion tensor optimisation."""

# Python module imports.
from numpy import array, float64
from os import sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Stand alone operation.
if not hasattr(ds, 'diff_type'):
    ds.diff_type = 'spheroid'
if not hasattr(ds, 'diff_dir'):
    ds.diff_dir = ds.diff_type

# A data pipe.
pipe.create('diff_opt', 'mf')

# Path of the files.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'diffusion_tensor'+sep+ds.diff_dir

# Load the sequence.
sequence.read('NOE.500.out', dir=path, res_num_col=1)

# Load a PDB file.
structure.read_pdb('uniform.pdb', dir=path)

# Set the spin names.
spin.name(name='N')

# Load the relaxation data.
frq = array([500, 600, 700, 800], float64)
for i in range(len(frq)):
    relax_data.read(ri_id='R1_%i'%frq[i],  ri_type='R1',  frq=frq[i]*1e6, file='R1.%i.out'%frq[i], dir=path, res_num_col=1, data_col=2, error_col=3)
    relax_data.read(ri_id='R2_%i'%frq[i],  ri_type='R2',  frq=frq[i]*1e6, file='R2.%i.out'%frq[i], dir=path, res_num_col=1, data_col=2, error_col=3)
    relax_data.read(ri_id='NOE_%i'%frq[i], ri_type='NOE', frq=frq[i]*1e6, file='NOE.%i.out'%frq[i], dir=path, res_num_col=1, data_col=2, error_col=3)

# Initialise the diffusion tensors.
if ds.diff_type == 'sphere':
    diffusion_tensor.init(1.0/(6.0*2e7), fixed=False)
elif ds.diff_type == 'spheroid':
    diffusion_tensor.init((1.0/(6.0*7e7/3.0), 1e7, 2.0, pi-0.5), angle_units='rad', fixed=False)
elif ds.diff_type == 'prolate':
    diffusion_tensor.init((1.0/(6.0*7e7/3.0), 1e7, 2.0, pi-0.5), angle_units='rad', fixed=False)
elif ds.diff_type == 'oblate':
    diffusion_tensor.init((1.0/(6.0*7e7/3.0), -1e7, 2.0, pi-0.5), angle_units='rad', fixed=False)
elif ds.diff_type == 'ellipsoid':
    diffusion_tensor.init((8.3333333333333335e-09, 15000000.0, 0.33333333333333331, 1.0, 2.0, 0.5), angle_units='rad', fixed=False)
else:
    raise RelaxError("The diffusion type '%s' is unknown." % ds.diff_type)

# Create the proton spins.
sequence.attach_protons()

# Define the magnetic dipole-dipole relaxation interaction.
spin.element('N', '@N')
structure.get_pos("@N")
structure.get_pos("@H")
interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
interatom.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)
interatom.unit_vectors()

# Define the chemical shift relaxation interaction.
value.set(-172 * 1e-6, 'csa', spin_id='@N')

# Set the nuclear isotope type.
spin.isotope('15N', spin_id='@N')

# Select the model-free model.
model_free.select_model(model='m0')

# Optimisation.
minimise.execute('newton')
