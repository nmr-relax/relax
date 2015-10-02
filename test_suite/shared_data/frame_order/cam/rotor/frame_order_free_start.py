# Script for optimising the rotor frame order test model of CaM.


# The real parameter values.
AVE_POS_X, AVE_POS_Y, AVE_POS_Z = [ -21.269217407269576,   -3.122610661328414,   -2.400652421655998]
AVE_POS_ALPHA, AVE_POS_BETA, AVE_POS_GAMMA = [5.623469076122531, 0.435439405668396, 5.081265529106499]

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
    pcs.read(align_id=ln[i], file='pcs_%s_subset.txt'%ln[i], mol_name_col=1, res_num_col=2, spin_name_col=5, data_col=6, error_col=7)

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
frame_order.select_model('rotor')

# Set the reference domain.
frame_order.ref_domain('N')

# Set the paramagnetic centre.
paramag.centre(pos=[35.934, 12.194, -4.206])

# Set the average domain position parameters.
value.set(param='ave_pos_x', val=AVE_POS_X)
value.set(param='ave_pos_y', val=AVE_POS_Y)
value.set(param='ave_pos_z', val=AVE_POS_Z)
value.set(param='ave_pos_alpha', val=AVE_POS_ALPHA)
value.set(param='ave_pos_beta', val=AVE_POS_BETA)
value.set(param='ave_pos_gamma', val=AVE_POS_GAMMA)

# Free the pivot, and set it to the CoM of both domains which is far enough away from the real pivot.
frame_order.pivot([ 34.721619683345111,  -2.63891199102997 ,  12.941974078087899], fix=False)

# Grid search (low quality for speed).
frame_order.num_int_pts(num=500)
grid_search(inc=[21, 21, 21, None, None, None, None, None, None, 21, 21])

# Iterative optimisation with increasing precision.
num_int_pts = [500, 1000]
func_tol = [1e-2, 1e-3]
for i in range(len(num_int_pts)):
    frame_order.num_int_pts(num=num_int_pts[i])
    minimise('simplex', func_tol=func_tol[i])

# Load the full PCS data set.
for i in range(len(ln)):
    pcs.read(align_id=ln[i], file='pcs_%s.txt'%ln[i], mol_name_col=1, res_num_col=2, spin_name_col=5, data_col=6, error_col=7)

# Iterative optimisation with increasing precision.
num_int_pts = [500, 1000, 10000, 100000]
func_tol = [1e-2, 1e-3, 5e-3, 1e-4]
for i in range(len(num_int_pts)):
    frame_order.num_int_pts(num=num_int_pts[i])
    minimise('simplex', func_tol=func_tol[i])

# Test Monte Carlo simulations.
frame_order.num_int_pts(num=10000)
monte_carlo.setup(number=200)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise('simplex', func_tol=1e-4)
eliminate()
monte_carlo.error_analysis()

# Create the PDB representation.
frame_order.pdb_model(ave_pos='ave_pos_free_start', rep='frame_order_free_start', dist=None, compress_type=2, force=True)

# Compare to the true result in PyMOL.
pymol.frame_order(ave_pos='ave_pos_true', rep='frame_order_true', dist=None)
pymol.frame_order(ave_pos='ave_pos_free_start', rep='frame_order_free_start', dist=None)

# Save the state.
state.save('frame_order_free_start', force=True)
