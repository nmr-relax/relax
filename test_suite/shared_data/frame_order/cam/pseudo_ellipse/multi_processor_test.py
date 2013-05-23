"""Script for testing out the multi-processor optimisation efficiency.

This script should be run from the directory where it is found with the commands:

$ ../../../../../relax multi_processor_test.py

$ mpirun -n 3 ../../../../../relax --multi mpi4py multi_processor_test.py
"""

# Python module imports.
from numpy import array, float64, transpose, zeros
from os import sep

# relax module imports.
from lib.geometry.rotations import euler_to_R_zyz


# Create the data pipe.
pipe.create(pipe_name='frame order', pipe_type='frame order')

# Read the structures.
structure.read_pdb('1J7O_1st_NH.pdb', dir='..', set_mol_name='N-dom')
structure.read_pdb('1J7P_1st_NH_rot.pdb', dir='..', set_mol_name='C-dom')

# Set up the 15N and 1H spins.
structure.load_spins(spin_id='@N', ave_pos=False)
structure.load_spins(spin_id='@H', ave_pos=False)
spin.isotope(isotope='15N', spin_id='@N')
spin.isotope(isotope='1H', spin_id='@H')

# Define the magnetic dipole-dipole relaxation interaction.
dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
dipole_pair.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.041 * 1e-10)
dipole_pair.unit_vectors()

# Loop over the alignments.
ln = ['dy', 'tb', 'tm', 'er']
for i in range(len(ln)):
    # Load the RDCs.
    rdc.read(align_id=ln[i], file='rdc_%s.txt'%ln[i], spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4)

    # The PCS.
    pcs.read(align_id=ln[i], file='pcs_%s.txt'%ln[i], mol_name_col=1, res_num_col=2, spin_name_col=5, data_col=6, error_col=7)

    # The temperature and field strength.
    spectrometer.temperature(id=ln[i], temp=303)
    spectrometer.frequency(id=ln[i], frq=900e6)

# Load the N-domain tensors (the full tensors).
script('../tensors.py')

# Define the domains.
domain(id='N', spin_id=":1-78")
domain(id='C', spin_id=":80-148")

# The tensor domains and reductions.
full = ['Dy N-dom', 'Tb N-dom', 'Tm N-dom', 'Er N-dom']
red =  ['Dy C-dom', 'Tb C-dom', 'Tm C-dom', 'Er C-dom']
ids = ['dy', 'tb', 'tm', 'er']
for i in range(len(full)):
    # Initialise the reduced tensor.
    align_tensor.init(tensor=red[i], align_id=ids[i], params=(0, 0, 0, 0, 0))

    # Set the domain info.
    align_tensor.set_domain(tensor=full[i], domain='N')
    align_tensor.set_domain(tensor=red[i], domain='C')

    # Specify which tensor is reduced.
    align_tensor.reduction(full_tensor=full[i], red_tensor=red[i])

# Select the model.
frame_order.select_model('pseudo-ellipse')

# Set the reference domain.
frame_order.ref_domain('N')

# Set the initial pivot point.
pivot = array([ 37.254, 0.5, 16.7465])
frame_order.pivot(pivot, fix=True)

# Set the paramagnetic centre.
paramag.centre(pos=[35.934, 12.194, -4.206])

# The optimisation settings.
frame_order.num_int_pts(num=1000)
frame_order.quad_int(flag=False)

# Check the minimum.
value.set(param='ave_pos_alpha', val=4.3434999280669997+0.1)
value.set(param='ave_pos_beta', val=0.43544332764249905+0.1)
value.set(param='ave_pos_gamma', val=3.8013235235956007+0.1)
value.set(param='eigen_alpha', val=3.14159265358979311600+0.1)
value.set(param='eigen_beta', val=0.96007997859534310869+0.1)
value.set(param='eigen_gamma', val=4.03227550621962294031+0.1)
value.set(param='cone_theta_x', val=0.5235987755982988+0.1)    # 30 deg.
value.set(param='cone_theta_y', val=0.8726646259971648+0.1)    # 50 deg.
value.set(param='cone_sigma_max', val=1.0471975511965976+0.1)    # 60 deg.
calc()
print("\nchi2: %s" % repr(cdp.chi2))

# Optimise.
minimise('simplex', constraints=False, max_iter=300)
