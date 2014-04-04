# Script for optimising the rotor frame order test model applied to a 2-state system of CaM.

# Python module imports.
from numpy import array


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
pivot = array([ 37.254, 0.5, 16.7465])
frame_order.pivot(pivot, fix=True)

# Set the paramagnetic centre.
paramag.centre(pos=[35.934, 12.194, -4.206])

# The optimisation settings.
frame_order.num_int_pts(num=50)
frame_order.quad_int(flag=False)

# Check the minimum.
value.set(param='ave_pos_alpha', val=4.3434999280669997)
value.set(param='ave_pos_beta', val=0.43544332764249905)
value.set(param='ave_pos_gamma', val=3.8013235235956007)
value.set(param='axis_theta', val=0.52344988559983696152)
value.set(param='axis_phi', val=0.89068285262982982)
value.set(param='cone_sigma_max', val=10.0 / 360.0 * 2.0 * pi)
calc()
print("\nchi2: %s" % repr(cdp.chi2))

# Optimise.
grid_search(inc=3)
minimise('simplex', constraints=False)

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
