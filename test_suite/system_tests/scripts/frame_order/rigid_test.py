###############################################################################
#                                                                             #
# Copyright (C) 2004-2013 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

"""Script for testing translation and rotation in the frame order analyses.

This script should be run from the directory where it is found with the commands:

$ ../../../../relax full_analysis.py
"""

# Python module imports.
from numpy import array, float64
from os import sep

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# The data path.
PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'displacements'


# Create the data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='rigid test', pipe_type='frame order')

# Read the structures.
self._execute_uf(uf_name='structure.read_pdb', file='displaced.pdb', dir=PATH, set_mol_name='fancy_mol')

# Set up the 15N and 1H spins.
self._execute_uf(uf_name='structure.load_spins')
self._execute_uf(uf_name='spin.isotope', isotope='15N', spin_id='@N')
self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@H')

# Define the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='dipole_pair.define', spin_id1='@N', spin_id2='@H', direct_bond=True)
self._execute_uf(uf_name='dipole_pair.set_dist', spin_id1='@N', spin_id2='@H', ave_dist=1.041 * 1e-10)
self._execute_uf(uf_name='dipole_pair.unit_vectors')

# The lanthanides and data files.
ln = ['dy', 'tb', 'tm', 'er', 'yb', 'ho']
pcs_files = [
    'pcs_dy.txt',
    'pcs_tb.txt',
    'pcs_tm.txt',
    'pcs_er.txt',
    'pcs_yb.txt',
    'pcs_ho.txt'
]
rdc_files = [
    'rdc_dy.txt',
    'rdc_tb.txt',
    'rdc_tm.txt',
    'rdc_er.txt',
    'rdc_yb.txt',
    'rdc_ho.txt'
]

# Loop over the alignments.
for i in range(len(ln)):
    # Load the RDCs.
    self._execute_uf(uf_name='rdc.read', align_id=ln[i], file=rdc_files[i], dir=PATH, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4)

    # The PCS (only a subset of ~5 spins for fast initial optimisations).
    self._execute_uf(uf_name='pcs.read', align_id=ln[i], file=pcs_files[i], dir=PATH, mol_name_col=1, res_num_col=2, spin_name_col=5, data_col=6, error_col=7)

    # The temperature and field strength.
    self._execute_uf(uf_name='temperature', id=ln[i], temp=303.0)
    self._execute_uf(uf_name='frq.set', id=ln[i], frq=800.0, units="MHz")

# Load the tensors (the full tensors).
self._execute_uf(uf_name='align_tensor.init', tensor='Dy fixed', align_id='dy', params=(-0.000283041921495, 0.00017331020651, 0.000348144461756, 0.00109678563394, -0.000261126459214), param_types=2)
self._execute_uf(uf_name='align_tensor.init', tensor='Dy fixed', align_id='dy', params=(1.32405973595e-05, 1.69451339335e-05, 1.11420056339e-05, 1.2902359091e-05, 1.06231229491e-05), param_types=2, errors=True)
self._execute_uf(uf_name='align_tensor.init', tensor='Tb fixed', align_id='tb', params=(0.000167738428636, -0.000311103377008, 0.000231043994111, 0.000927908442481, -0.00042448381621), param_types=2)
self._execute_uf(uf_name='align_tensor.init', tensor='Tb fixed', align_id='tb', params=(9.23106516114e-06, 1.23864406564e-05, 9.25138110416e-06, 1.0025121852e-05, 8.6027985631e-06), param_types=2, errors=True)
self._execute_uf(uf_name='align_tensor.init', tensor='Tm fixed', align_id='tm', params=(-0.000214531334757, 0.000250016686133, -0.000318452894707, -0.000566585709341, 0.000458689017372), param_types=2)
self._execute_uf(uf_name='align_tensor.init', tensor='Tm fixed', align_id='tm', params=(8.18656207912e-06, 1.09649975373e-05, 8.43998269558e-06, 8.63599444168e-06, 7.95937745247e-06), param_types=2, errors=True)
self._execute_uf(uf_name='align_tensor.init', tensor='Er fixed', align_id='er', params=(-9.34632913359e-05, 7.71986454118e-05, -0.000234020357448, -0.000363596427557, 0.000177874820425), param_types=2)
self._execute_uf(uf_name='align_tensor.init', tensor='Er fixed', align_id='er', params=(6.32851257036e-06, 9.3721066722e-06, 7.36682050165e-06, 7.52806731357e-06, 9.79003188793e-06), param_types=2, errors=True)
self._execute_uf(uf_name='align_tensor.init', tensor='Yb fixed', align_id='yb', params=(2.20524016343e-05, -6.04903356962e-05, -0.000114723702615, -0.000214855846027, 0.000143730520814), param_types=2)
self._execute_uf(uf_name='align_tensor.init', tensor='Yb fixed', align_id='yb', params=(4.2812326053e-06, 5.43186247053e-06, 4.83605375312e-06, 5.10468453851e-06, 4.31847329676e-06), param_types=2, errors=True)
self._execute_uf(uf_name='align_tensor.init', tensor='Ho fixed', align_id='ho', params=(-6.99147985047e-05, -8.00899711508e-06, 0.000102219102441, 0.000424559081645, -0.000255281322523), param_types=2)
self._execute_uf(uf_name='align_tensor.init', tensor='Ho fixed', align_id='ho', params=(7.74711876341e-06, 9.55677606858e-06, 9.13852550558e-06, 7.82230105216e-06, 7.33515152376e-06), param_types=2, errors=True)

# Define the domains.
self._execute_uf(uf_name='domain', id='moving', spin_id=":0-100")
self._execute_uf(uf_name='domain', id='fixed', spin_id=":101-200")

# The tensor domains and reductions.
full = ['Dy fixed', 'Tb fixed', 'Tm fixed', 'Er fixed', 'Yb fixed', 'Ho fixed']
red =  ['Dy moving', 'Tb moving', 'Tm moving', 'Er moving', 'Yb moving', 'Ho moving']
for i in range(len(full)):
    # Initialise the reduced tensors (fitted during optimisation).
    self._execute_uf(uf_name='align_tensor.init', tensor=red[i], align_id=ln[i], params=(0, 0, 0, 0, 0))

    # Set the domain info.
    self._execute_uf(uf_name='align_tensor.set_domain', tensor=full[i], domain='fixed')
    self._execute_uf(uf_name='align_tensor.set_domain', tensor=red[i], domain='moving')

    # Specify which tensor is reduced.
    self._execute_uf(uf_name='align_tensor.reduction', full_tensor=full[i], red_tensor=red[i])

# Set the reference domain.
self._execute_uf(uf_name='frame_order.ref_domain', ref='fixed')

# Set up the mechanics of the displacement to the average domain position.
self._execute_uf(uf_name='frame_order.average_position', pivot='com', translation=True)

# Set the initial pivot point (should make no difference for the rigid model).
pivot = array([0, 0, 0], float64)
self._execute_uf(uf_name='frame_order.pivot', pivot=pivot, fix=True)

# Set the paramagnetic centre position.
self._execute_uf(uf_name='paramag.centre', pos=[-5, -7, -9])

# Set the number of integration points.
self._execute_uf(uf_name='frame_order.num_int_pts', num=10000)

# Set the real parameter values (the inverted displacement values).
cdp.ave_pos_x = -1
cdp.ave_pos_y = -2
cdp.ave_pos_z = -3
cdp.ave_pos_alpha = 0.14159265359
cdp.ave_pos_beta  = 2.0
cdp.ave_pos_gamma = 2.14159265359

# Set some parameters close to zero, but far enough away from zero to allow for the numerical integration.
cdp.cone_s1 = 0.99
cdp.cone_theta = 0.1
cdp.cone_theta_x = 0.1
cdp.cone_theta_y = 0.1
cdp.cone_sigma_max = 0.1

# Allow for stand-alone operation.
if not hasattr(ds, 'model'):
    ds.model = 'rigid'

# Select the Frame Order model.
self._execute_uf(uf_name='frame_order.select_model', model=ds.model)

# Calculate the chi2 value.
self._execute_uf(uf_name='calc')
