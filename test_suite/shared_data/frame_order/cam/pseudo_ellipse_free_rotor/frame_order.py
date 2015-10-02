# Script for optimising the free-rotor pseudo-ellipse frame order test model of CaM.

# Python module imports.
from numpy import array


# The real parameter values.
AVE_POS_X, AVE_POS_Y, AVE_POS_Z = [ -21.269217407269576,   -3.122610661328414,   -2.400652421655998]
AVE_POS_BETA = 0.19740471457956135
AVE_POS_GAMMA = 4.6622313104265416
EIGEN_ALPHA = 3.1415926535897931
EIGEN_BETA = 0.96007997859534311
EIGEN_GAMMA = 4.0322755062196229
CONE_THETA_X = 0.3
CONE_THETA_Y = 0.5

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
interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
interatom.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.041 * 1e-10)
interatom.unit_vectors()

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
domain(id='N', spin_id="#N-dom")
domain(id='C', spin_id="#C-dom")

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
frame_order.select_model('pseudo-ellipse, free rotor')

# Set the reference domain.
frame_order.ref_domain('N')

# Set the initial pivot point.
pivot = array([ 37.254, 0.5, 16.7465])
frame_order.pivot(pivot, fix=True)

# Set the paramagnetic centre.
paramag.centre(pos=[35.934, 12.194, -4.206])

# Check the minimum (at a very high quality to check that the chi-squared value is zero).
frame_order.num_int_pts(num=100000)
value.set(param='ave_pos_x', val=AVE_POS_X)
value.set(param='ave_pos_y', val=AVE_POS_Y)
value.set(param='ave_pos_z', val=AVE_POS_Z)
value.set(param='ave_pos_beta', val=AVE_POS_BETA)
value.set(param='ave_pos_gamma', val=AVE_POS_GAMMA)
value.set(param='eigen_alpha', val=EIGEN_ALPHA)
value.set(param='eigen_beta', val=EIGEN_BETA)
value.set(param='eigen_gamma', val=EIGEN_GAMMA)
value.set(param='cone_theta_x', val=CONE_THETA_X)
value.set(param='cone_theta_y', val=CONE_THETA_Y)
minimise.calculate()

# Create the PDB representation of the true state.
frame_order.pdb_model(ave_pos='ave_pos_true', rep='frame_order_true', dist=None, compress_type=2, force=True)

# Save the state.
state.save('frame_order_true', force=True)

# Grid search (low quality for speed).
frame_order.num_int_pts(num=200)
grid_search(inc=[None, None, None, None, None, 7, 7, 7, 7, 7])

# Iterative optimisation with increasing precision.
num_int_pts = [1000, 10000, 50000]
func_tol = [1e-2, 1e-3, 1e-4]
for i in range(len(num_int_pts)):
    frame_order.num_int_pts(num=num_int_pts[i])
    minimise('simplex', func_tol=func_tol[i])

# Store the result.
frame_order.pdb_model(ave_pos='ave_pos_fixed_piv', rep='frame_order_fixed_piv', dist=None, compress_type=2, force=True)

# Save the state.
state.save('frame_order_fixed_piv', force=True)

# Optimise the pivot and model, again iterating with increasing precision.
frame_order.pivot(pivot, fix=False)
num_int_pts = [1000, 10000, 50000]
func_tol = [1e-2, 1e-3, 1e-4]
for i in range(len(num_int_pts)):
    frame_order.num_int_pts(num=num_int_pts[i])
    minimise('simplex', func_tol=func_tol[i])

# Test Monte Carlo simulations.
frame_order.num_int_pts(num=10000)
monte_carlo.setup(number=5)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise('simplex', func_tol=1e-2)
eliminate()
monte_carlo.error_analysis()

# Create the PDB representation.
frame_order.pdb_model(ave_pos='ave_pos', rep='frame_order', dist=None, compress_type=2, force=True)

# PyMOL.
pymol.frame_order(ave_pos='ave_pos_true', rep='frame_order_true', dist=None)
pymol.frame_order(ave_pos='ave_pos_fixed_piv', rep='frame_order_fixed_piv', dist=None)
pymol.frame_order(ave_pos='ave_pos', rep='frame_order', dist=None)

# Save the state.
state.save('frame_order', force=True)
