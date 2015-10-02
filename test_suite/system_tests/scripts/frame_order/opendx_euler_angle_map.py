# Python module imports.
from os import sep

# relax module imports.
from lib.frame_order.variables import MODEL_RIGID
from status import Status; status = Status()


# Data paths.
BASE_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'+sep
DATA_PATH = BASE_PATH + 'rigid'

# Create a data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='mapping test', pipe_type='frame order')

# Read the structures.
self._execute_uf(uf_name='structure.read_pdb', file='1J7O_1st_NH.pdb', dir=BASE_PATH, set_mol_name='N-dom')
self._execute_uf(uf_name='structure.read_pdb', file='1J7P_1st_NH_rot.pdb', dir=BASE_PATH, set_mol_name='C-dom')

# Set up the 15N and 1H spins.
self._execute_uf(uf_name='structure.load_spins', spin_id='@N', ave_pos=False)
self._execute_uf(uf_name='structure.load_spins', spin_id='@H', ave_pos=False)
self._execute_uf(uf_name='spin.isotope', isotope='15N', spin_id='@N')
self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@H')

# Define the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='interatom.define', spin_id1='@N', spin_id2='@H', direct_bond=True)
self._execute_uf(uf_name='interatom.set_dist', spin_id1='@N', spin_id2='@H', ave_dist=1.041 * 1e-10)
self._execute_uf(uf_name='interatom.unit_vectors')

# Loop over the alignments.
ln = ['dy', 'tb', 'tm', 'er']
for i in range(len(ln)):
    # Load the RDCs.
    self._execute_uf(uf_name='rdc.read', align_id=ln[i], file='rdc_%s.txt'%ln[i], dir=DATA_PATH, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4)

    # The PCS.
    self._execute_uf(uf_name='pcs.read', align_id=ln[i], file='pcs_%s_subset.txt'%ln[i], dir=DATA_PATH, mol_name_col=1, res_num_col=2, spin_name_col=5, data_col=6, error_col=7)

    # The temperature and field strength.
    self._execute_uf(uf_name='spectrometer.temperature', id=ln[i], temp=303)
    self._execute_uf(uf_name='spectrometer.frequency', id=ln[i], frq=900e6)

# Load the N-domain tensors (the full tensors).
self._execute_uf(uf_name='script', file=BASE_PATH + 'tensors.py')

# Define the domains.
self._execute_uf(uf_name='domain', id='N', spin_id="#N-dom")
self._execute_uf(uf_name='domain', id='C', spin_id="#C-dom")

# The tensor domains and reductions.
full = ['Dy N-dom', 'Tb N-dom', 'Tm N-dom', 'Er N-dom']
red =  ['Dy C-dom', 'Tb C-dom', 'Tm C-dom', 'Er C-dom']
ids =  ['dy', 'tb', 'tm', 'er']
for i in range(len(full)):
    # Initialise the reduced tensor.
    self._execute_uf(uf_name='align_tensor.init', tensor=red[i], align_id=ids[i], params=(0, 0, 0, 0, 0))

    # Set the domain info.
    self._execute_uf(uf_name='align_tensor.set_domain', tensor=full[i], domain='N')
    self._execute_uf(uf_name='align_tensor.set_domain', tensor=red[i], domain='C')

    # Specify which tensor is reduced.
    self._execute_uf(uf_name='align_tensor.reduction', full_tensor=full[i], red_tensor=red[i])

# Select the model.
self._execute_uf(uf_name='frame_order.select_model', model=MODEL_RIGID)

# Set the reference domain.
self._execute_uf(uf_name='frame_order.ref_domain', ref='N')

# Set the initial pivot point - fixed when optimising, unfixed otherwise to check different code paths.
self._execute_uf(uf_name='frame_order.pivot', pivot=[ 37.254, 0.5, 16.7465], fix=False)

# Set the paramagnetic centre.
self._execute_uf(uf_name='paramag.centre', pos=[35.934, 12.194, -4.206])

# Set the initial parameter values.
self._execute_uf(uf_name='value.set', val=-21.269217407269576, param='ave_pos_x', force=True)
self._execute_uf(uf_name='value.set', val=-3.122610661328414, param='ave_pos_y', force=True)
self._execute_uf(uf_name='value.set', val=-2.400652421655998, param='ave_pos_z', force=True)
self._execute_uf(uf_name='value.set', val=5.623469076122531, param='ave_pos_alpha', force=True)
self._execute_uf(uf_name='value.set', val=0.435439405668396, param='ave_pos_beta', force=True)
self._execute_uf(uf_name='value.set', val=5.081265529106499, param='ave_pos_gamma', force=True)

# Map the Euler angle space.
self._execute_uf(uf_name='dx.map', params=['ave_pos_alpha', 'ave_pos_beta', 'ave_pos_gamma'], lower=[0, 0, 0], upper=[2*pi, 2*pi, 2*pi], inc=3, file_prefix='devnull', point_file='devnull')
