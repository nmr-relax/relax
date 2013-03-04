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


# Create the data pipe.
pipe.create(pipe_name='rigid test', pipe_type='frame order')

# Read the structures.
structure.read_pdb('displaced.pdb', set_mol_name='fancy_mol')

# Set up the 15N and 1H spins.
structure.load_spins()
spin.isotope(isotope='15N', spin_id='@N')
spin.isotope(isotope='1H', spin_id='@H')

# Define the magnetic dipole-dipole relaxation interaction.
dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
dipole_pair.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.041 * 1e-10)
dipole_pair.unit_vectors()

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
    rdc.read(align_id=ln[i], file=rdc_files[i], dir='.', spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4)

    # The PCS (only a subset of ~5 spins for fast initial optimisations).
    pcs.read(align_id=ln[i], file=pcs_files[i], dir='.', mol_name_col=1, res_num_col=2, spin_name_col=5, data_col=6, error_col=7)

    # The temperature and field strength.
    temperature(id=ln[i], temp=303.0)
    frq.set(id=ln[i], frq=800.0, units="MHz")

# Load the tensors (the full tensors).
align_tensor.init(tensor='Dy fixed', align_id='dy', params=(-0.000283041921495, 0.00017331020651, 0.000348144461756, 0.00109678563394, -0.000261126459214), param_types=2)
align_tensor.init(tensor='Dy fixed', align_id='dy', params=(1.32405973595e-05, 1.69451339335e-05, 1.11420056339e-05, 1.2902359091e-05, 1.06231229491e-05), param_types=2, errors=True)
align_tensor.init(tensor='Tb fixed', align_id='tb', params=(0.000167738428636, -0.000311103377008, 0.000231043994111, 0.000927908442481, -0.00042448381621), param_types=2)
align_tensor.init(tensor='Tb fixed', align_id='tb', params=(9.23106516114e-06, 1.23864406564e-05, 9.25138110416e-06, 1.0025121852e-05, 8.6027985631e-06), param_types=2, errors=True)
align_tensor.init(tensor='Tm fixed', align_id='tm', params=(-0.000214531334757, 0.000250016686133, -0.000318452894707, -0.000566585709341, 0.000458689017372), param_types=2)
align_tensor.init(tensor='Tm fixed', align_id='tm', params=(8.18656207912e-06, 1.09649975373e-05, 8.43998269558e-06, 8.63599444168e-06, 7.95937745247e-06), param_types=2, errors=True)
align_tensor.init(tensor='Er fixed', align_id='er', params=(-9.34632913359e-05, 7.71986454118e-05, -0.000234020357448, -0.000363596427557, 0.000177874820425), param_types=2)
align_tensor.init(tensor='Er fixed', align_id='er', params=(6.32851257036e-06, 9.3721066722e-06, 7.36682050165e-06, 7.52806731357e-06, 9.79003188793e-06), param_types=2, errors=True)
align_tensor.init(tensor='Yb fixed', align_id='yb', params=(2.20524016343e-05, -6.04903356962e-05, -0.000114723702615, -0.000214855846027, 0.000143730520814), param_types=2)
align_tensor.init(tensor='Yb fixed', align_id='yb', params=(4.2812326053e-06, 5.43186247053e-06, 4.83605375312e-06, 5.10468453851e-06, 4.31847329676e-06), param_types=2, errors=True)
align_tensor.init(tensor='Ho fixed', align_id='ho', params=(-6.99147985047e-05, -8.00899711508e-06, 0.000102219102441, 0.000424559081645, -0.000255281322523), param_types=2)
align_tensor.init(tensor='Ho fixed', align_id='ho', params=(7.74711876341e-06, 9.55677606858e-06, 9.13852550558e-06, 7.82230105216e-06, 7.33515152376e-06), param_types=2, errors=True)

# Define the domains.
domain(id='moving', spin_id=":0-100")
domain(id='fixed', spin_id=":101-200")

# The tensor domains and reductions.
full = ['Dy fixed', 'Tb fixed', 'Tm fixed', 'Er fixed', 'Yb fixed', 'Ho fixed']
red =  ['Dy moving', 'Tb moving', 'Tm moving', 'Er moving', 'Yb moving', 'Ho moving']
for i in range(len(full)):
    # Initialise the reduced tensors (fitted during optimisation).
    align_tensor.init(tensor=red[i], align_id=ln[i], params=(0, 0, 0, 0, 0))

    # Set the domain info.
    align_tensor.set_domain(tensor=full[i], domain='fixed')
    align_tensor.set_domain(tensor=red[i], domain='moving')

    # Specify which tensor is reduced.
    align_tensor.reduction(full_tensor=full[i], red_tensor=red[i])

# Set the reference domain.
frame_order.ref_domain('fixed')

# Link the domains to the PDB files.
frame_order.domain_to_pdb(domain='fixed', pdb='displaced.pdb')

# Allow the average domain to be translated during optimisation.
frame_order.ave_pos_translate()

# Set the initial pivot point (should make no difference for the rigid model).
pivot = array([0, 0, 0], float64)
frame_order.pivot(pivot, fix=True)

# Set the paramagnetic centre position.
paramag.centre(pos=[-5, -7, -9])

# Select the Frame Order model.
frame_order.select_model(model='rigid')

# Set the real parameter values.
cdp.ave_pos_x = -1
cdp.ave_pos_y = -2
cdp.ave_pos_z = -3
cdp.ave_pos_alpha = 0.14159265359
cdp.ave_pos_beta  = 2.0
cdp.ave_pos_gamma = 2.14159265359

# Calculate the chi2 value.
calc()

# Attempt to mimimise.
minimise('simplex', constraints=False)
