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

"""Script for black-box Frame Order analysis."""


# Python module imports.
from numpy import array
from os import sep
from time import asctime, localtime

# relax module imports.
from auto_analyses.frame_order import Frame_order_analysis, Optimisation_settings
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Analysis variables.
#####################

# The frame order models to use.
MODELS = [
    'rigid',
    'free rotor',
    'rotor',
    'iso cone, torsionless',
    'iso cone, free rotor',
    'iso cone',
    'pseudo-ellipse, torsionless',
    'pseudo-ellipse',
    'double rotor'
]

# The number of Monte Carlo simulations to be used for error analysis at the end of the protocol.
MC_NUM = 3

# Rigid model optimisation setup.
OPT_RIGID = Optimisation_settings()
OPT_RIGID.add_grid(inc=8, zoom=0)
OPT_RIGID.add_min(min_algor='simplex', func_tol=1e-2, max_iter=20)

# PCS subset optimisation setup.
OPT_SUBSET = Optimisation_settings()
OPT_SUBSET.add_grid(inc=2, sobol_max_points=1)
OPT_SUBSET.add_min(min_algor='simplex', func_tol=1e-2, max_iter=5, sobol_max_points=1)

# Full data set optimisation setup.
OPT_FULL = Optimisation_settings()
OPT_FULL.add_grid(inc=2, sobol_max_points=1)
OPT_FULL.add_min(min_algor='simplex', func_tol=1e-2, max_iter=5, sobol_max_points=1)

# Monte Carlo simulation optimisation setup.
OPT_MC = Optimisation_settings()
OPT_MC.add_min(min_algor='simplex', func_tol=1e-2, max_iter=5, sobol_max_points=1)

# Pseudo-Brownian simulation (for the frame_order.simulate user function).
STEP_SIZE = 2.0
SNAPSHOT = 2
TOTAL = 5


# Set up the base data pipes.
#############################

# The data paths.
BASE_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'+sep
DATA_PATH = BASE_PATH + sep+'rigid'

# The data pipe bundle to group all data pipes.
PIPE_BUNDLE = "Frame Order (%s)" % asctime(localtime())

# Create the base data pipe containing only a subset of the PCS data.
SUBSET = "Data subset - " + PIPE_BUNDLE
pipe.create(pipe_name=SUBSET, pipe_type='frame order', bundle=PIPE_BUNDLE)

# Read the structures.
structure.read_pdb('1J7O_1st_NH.pdb', dir=BASE_PATH, set_mol_name='N-dom')
structure.read_pdb('1J7P_1st_NH_rot.pdb', dir=BASE_PATH, set_mol_name='C-dom')

# Set up the 15N and 1H spins.
structure.load_spins(spin_id='@N', ave_pos=False)
structure.load_spins(spin_id='@H', ave_pos=False)
spin.isotope(isotope='15N', spin_id='@N')
spin.isotope(isotope='1H', spin_id='@H')

# Define the magnetic dipole-dipole relaxation interaction.
interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
interatom.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.041 * 1e-10)
interatom.unit_vectors()

# The lanthanides and data files.
ln = ['dy', 'tb', 'tm', 'er']
pcs_files = [
    'pcs_dy_subset.txt',
    'pcs_tb_subset.txt', 
    'pcs_tm_subset.txt', 
    'pcs_er_subset.txt'
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
    rdc.read(align_id=ln[i], file=rdc_files[i], dir=DATA_PATH, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4)

    # The PCS (only a subset of ~5 spins for fast initial optimisations).
    pcs.read(align_id=ln[i], file=pcs_files_subset[i], dir=DATA_PATH, mol_name_col=1, res_num_col=2, spin_name_col=5, data_col=6, error_col=7)

    # The temperature and field strength.
    spectrometer.temperature(id=ln[i], temp=303.0)
    spectrometer.frequency(id=ln[i], frq=rdc_frq[i], units="MHz")

# Load the N-domain tensors (the full tensors).
script(BASE_PATH + 'tensors.py')

# Define the domains.
domain(id='N', spin_id="#N-dom")
domain(id='C', spin_id="#C-dom")

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
    pcs.read(align_id=ln[i], file=pcs_files[i], dir=DATA_PATH, mol_name_col=1, res_num_col=2, spin_name_col=5, data_col=6, error_col=7)



# Execution.
############

# Do not change!
Frame_order_analysis(data_pipe_full=DATA, data_pipe_subset=SUBSET, pipe_bundle=PIPE_BUNDLE, results_dir=ds.tmpdir, opt_rigid=OPT_RIGID, opt_subset=OPT_SUBSET, opt_full=OPT_FULL, opt_mc=OPT_MC, mc_sim_num=MC_NUM, models=MODELS, brownian_step_size=STEP_SIZE, brownian_snapshot=SNAPSHOT, brownian_total=TOTAL)
