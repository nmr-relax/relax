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

"""Script for black-box Frame Order analysis.

This script should be run from the directory where it is found with the commands:

$ ../../../../../relax full_analysis.py

The free rotor pseudo-elliptic cone model is not used in this script as the cone X and Y opening angles cannot be differentiated with simply RDC and PCS data, hence this model is perfectly approximated by the free rotor isotropic cone.
"""

# Python module imports.
from numpy import array
from time import asctime, localtime

# relax module imports.
from auto_analyses.frame_order import Frame_order_analysis


# Analysis variables.
#####################

# The grid search size (the number of increments per dimension).
GRID_INC = 11

# The more precise grid search size for the initial rigid model (the number of increments per dimension).
GRID_INC_RIGID = 31

# The number of Sobol' points for the PCS numerical integration in the grid searches.
NUM_INT_PTS_GRID = 50

# The list of the number of Sobol' points for the PCS numerical integration to use iteratively in the optimisations after the grid search (for the PCS data subset).
NUM_INT_PTS_SUBSET = [100]

# The minimisation function tolerance cutoff to terminate optimisation (for the PCS data subset, see the minimise user function).
FUNC_TOL_SUBSET = [1e-2]

# The list of the number of Sobol' points for the PCS numerical integration to use iteratively in the optimisations after the grid search (for all PCS and RDC data).
NUM_INT_PTS_FULL = [100, 1000, 10000]

# The minimisation function tolerance cutoff to terminate optimisation (for all PCS and RDC data, see the minimise user function).
FUNC_TOL_FULL = [1e-2, 1e-3, 1e-4]

# The optimisation technique.
MIN_ALGOR = 'simplex'

# The number of Monte Carlo simulations to be used for error analysis at the end of the protocol.
MC_NUM = 100

# The number of Sobol' points for the PCS numerical integration during Monte Carlo simulations.
MC_INT_PTS = 100

# The minimisation function tolerance cutoff to terminate optimisation during Monte Carlo simulations.
MC_FUNC_TOL = 1e-2

# The frame order models to use.
MODELS = [
    'rigid',
    'free rotor',
    'rotor',
    'iso cone, torsionless',
    'iso cone, free rotor',
    'iso cone',
    'pseudo-ellipse, torsionless',
    'pseudo-ellipse'
]

# Set up the base data pipes.
#############################

# The data pipe bundle to group all data pipes.
PIPE_BUNDLE = "Frame Order (%s)" % asctime(localtime())

# Create the base data pipe containing only a subset of the PCS data.
SUBSET = "Data subset - " + PIPE_BUNDLE
pipe.create(pipe_name=SUBSET, pipe_type='frame order', bundle=PIPE_BUNDLE)

# Read the structures.
structure.read_pdb('1J7O_1st_NH.pdb', dir='..', set_mol_name='N-dom')
structure.read_pdb('1J7P_1st_NH_rot.pdb', dir='..', set_mol_name='C-dom')

# Set up the 15N and 1H spins.
structure.load_spins(spin_id='@N', mol_name_target='CaM', ave_pos=False)
structure.load_spins(spin_id='@H', mol_name_target='CaM', ave_pos=False)
spin.isotope(isotope='15N', spin_id='@N')
spin.isotope(isotope='1H', spin_id='@H')

# Define the magnetic dipole-dipole relaxation interaction.
dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
dipole_pair.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.041 * 1e-10)
dipole_pair.unit_vectors()

# The lanthanides and data files.
ln = ['dy', 'tb', 'tm', 'er']
pcs_files = [
    'pcs_dy.txt',
    'pcs_tb.txt', 
    'pcs_tm.txt', 
    'pcs_er.txt'
]
pcs_files_subset = [
    'pcs_dy_subset.txt', 
    'pcs_tb_subset.txt', 
    'pcs_tm_subset.txt', 
    'pcs_er_subset.txt' 
]
rdc_files = [
    'rdc_dy.txt', 
    'rdc_tb.txt', 
    'rdc_tm.txt', 
    'rdc_er.txt' 
]

# The spectrometer frequencies.
pcs_frq = [
    700.0000000,    # Dy3+.
    700.0000000,    # Tb3+.
    700.0000000,    # Tm3+.
    700.0000000,    # Er3+.
]
rdc_frq = [
    900.00000000,   # Dy3+.
    900.00000000,   # Tb3+.
    900.00000000,   # Tm3+.
    900.00000000,   # Er3+.
]

# Loop over the alignments.
for i in range(len(ln)):
    # Load the RDCs.
    rdc.read(align_id=ln[i], file=rdc_files[i], dir='.', spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4)

    # The PCS (only a subset of ~5 spins for fast initial optimisations).
    pcs.read(align_id=ln[i], file=pcs_files_subset[i], dir='.', mol_name_col=1, res_num_col=2, spin_name_col=5, data_col=6, error_col=7)

    # The temperature and field strength.
    temperature(id=ln[i], temp=303.0)
    frq.set(id=ln[i], frq=rdc_frq[i], units="MHz")

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
    # Initialise the reduced tensors (fitted during optimisation).
    align_tensor.init(tensor=red[i], align_id=ids[i], params=(0, 0, 0, 0, 0))

    # Set the domain info.
    align_tensor.set_domain(tensor=full[i], domain='N')
    align_tensor.set_domain(tensor=red[i], domain='C')

    # Specify which tensor is reduced.
    align_tensor.reduction(full_tensor=full[i], red_tensor=red[i])

# Set the reference domain.
frame_order.ref_domain('N')

# Link the domains to the PDB files.
frame_order.domain_to_pdb(domain='N', pdb='1J7O_1st_NH.pdb')
frame_order.domain_to_pdb(domain='C', pdb='1J7P_1st_NH_rot.pdb')

# Allow the average domain to be translated during optimisation.
#frame_order.ave_pos_translate()

# Set the initial pivot point.
pivot = array([ 37.254, 0.5, 16.7465])
frame_order.pivot(pivot, fix=True)

# Set the paramagnetic centre position.
paramag.centre(pos=[35.934, 12.194, -4.206])

# Duplicate the PCS data subset data pipe to create a data pipe containing all the PCS data.
DATA = "Data - " + PIPE_BUNDLE
pipe.copy(pipe_from=SUBSET, pipe_to=DATA, bundle_to=PIPE_BUNDLE)
pipe.switch(DATA)

# Load the complete PCS data into the already filled data pipe.
for i in range(len(ln)):
    pcs.read(align_id=ln[i], file=pcs_files[i], mol_name_col=1, res_num_col=2, spin_name_col=5, data_col=6, error_col=7)



# Execution.
############

# Do not change!
Frame_order_analysis(data_pipe_full=DATA, data_pipe_subset=SUBSET, pipe_bundle=PIPE_BUNDLE, grid_inc=GRID_INC, grid_inc_rigid=GRID_INC_RIGID, min_algor=MIN_ALGOR, num_int_pts_grid=NUM_INT_PTS_GRID, num_int_pts_subset=NUM_INT_PTS_SUBSET, func_tol_subset=FUNC_TOL_SUBSET, num_int_pts_full=NUM_INT_PTS_FULL, func_tol_full=FUNC_TOL_FULL, mc_sim_num=MC_NUM, mc_int_pts=MC_INT_PTS, mc_func_tol=MC_FUNC_TOL, models=MODELS)
