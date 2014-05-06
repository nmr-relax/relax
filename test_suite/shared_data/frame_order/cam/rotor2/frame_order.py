# Script for optimising the second rotor frame order test model of CaM.

# Python module imports.
from numpy import array, cross, float64, zeros
from numpy.linalg import norm

# relax module imports.
from lib.geometry.lines import closest_point_ax
from lib.geometry.coord_transform import spherical_to_cartesian
from lib.geometry.vectors import vector_angle
from pipe_control.structure.mass import pipe_centre_of_mass


def alpha_angle(pivot=None, com=None, theta=None, phi=None):
    """Calculate and return the rotor alpha angle."""

    # Create the rotor axis.
    axis = zeros(3, float64)
    spherical_to_cartesian([1, theta, phi], axis)

    # The CoM-pivot axis.
    com_piv = com - pivot
    com_piv /= norm(com_piv)

    # The mu_xy vector.
    z_axis = array([0, 0, 1], float64)
    mu_xy = cross(z_axis, com_piv)
    mu_xy /= norm(mu_xy)

    # The alpha angle.
    return vector_angle(mu_xy, axis, com_piv)


def shift_pivot(pivot_orig=None, com=None, theta=None, phi=None):
    """Shift the pivot to the closest point on the rotor axis to the CoM.)"""

    # Create the rotor axis.
    axis = zeros(3, float64)
    spherical_to_cartesian([1, theta, phi], axis)

    # The closest point.
    pivot_new = closest_point_ax(line_pt=pivot_orig, axis=axis, point=com)

    # Printout.
    print("\n%-20s%s" % ("Original pivot:", pivot_orig))
    print("%-20s%s" % ("New pivot:", pivot_new))

    # Return the shifted pivot.
    return pivot_new


# The real parameter values.
AVE_POS_ALPHA = 4.3434999280669997
AVE_POS_BETA = 0.43544332764249905
AVE_POS_GAMMA = 3.8013235235956007
AXIS_THETA = 0.69828059079619353433
AXIS_PHI = 4.03227550621962294031
CONE_SIGMA_MAX = 30.0 / 360.0 * 2.0 * pi

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
frame_order.select_model('rotor')

# Set up the mechanics of the displacement to the average domain position.
frame_order.average_position(pivot='motional', translation=False)

# Set the reference domain.
frame_order.ref_domain('N')

# Set the initial pivot point.
pivot = shift_pivot(pivot_orig=array([ 37.254, 0.5, 16.7465]), com=pipe_centre_of_mass(verbosity=0), theta=AXIS_THETA, phi=AXIS_PHI)
frame_order.pivot(pivot, fix=True)

# Set the paramagnetic centre.
paramag.centre(pos=[35.934, 12.194, -4.206])

# The optimisation settings.
frame_order.num_int_pts(num=50)
frame_order.quad_int(flag=False)

# Check the minimum.
value.set(param='ave_pos_alpha', val=AVE_POS_ALPHA)
value.set(param='ave_pos_beta', val=AVE_POS_BETA)
value.set(param='ave_pos_gamma', val=AVE_POS_GAMMA)
value.set(param='axis_alpha', val=alpha_angle(pivot=pivot, com=pipe_centre_of_mass(verbosity=0), theta=AXIS_THETA, phi=AXIS_PHI))
value.set(param='cone_sigma_max', val=CONE_SIGMA_MAX)
calc()
print("\nchi2: %s" % repr(cdp.chi2))

# Optimise.
grid_search(inc=5)
minimise('simplex', constraints=True)

# Optimise the pivot and model.
#frame_order.pivot(pivot, fix=False)
#minimise('simplex', constraints=False)

# Test Monte Carlo simulations.
monte_carlo.setup(number=5)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise('simplex', constraints=False)
eliminate()
monte_carlo.error_analysis()

# Create the PDB representation.
frame_order.pdb_model(force=True)

# PyMOL.
pymol.view()
pymol.command('show spheres')
pymol.cone_pdb('frame_order.pdb')

# Save the state.
state.save('frame_order', force=True)
